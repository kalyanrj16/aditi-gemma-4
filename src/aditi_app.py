# src/aditi_app.py
# Aditi demo. One "Your query" block: a pre-loaded prompt box, a scenario radio,
# a prescription loader, a voice radio, and a collapsible input preview -> Ask Aditi.
# Two scenarios:
#   "Did I get the right medicine?"  -> substitution check  -> findings card
#   "My health story"                -> multi-doc synthesis -> Markdown summary
#
# Run with:  streamlit run src/aditi_app.py

import tempfile
from pathlib import Path

import streamlit as st

import config
import crosscheck
import extractors

st.set_page_config(page_title="Aditi", page_icon="🩺", layout="wide")

_EMPTY_PREFIXES = ("not provided", "no audio", "not specified", "n/a", "none")


@st.cache_resource(show_spinner=False)
def get_cached_model(model_id: str):
    return extractors.load_model(model_id)


def _materialize(uploaded_files, default_suffix: str) -> list[Path]:
    """Write Streamlit UploadedFile objects to temp paths (mlx-vlm needs paths)."""
    paths = []
    for uf in uploaded_files:
        suffix = Path(uf.name).suffix or default_suffix
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(uf.getbuffer())
        tmp.flush()
        tmp.close()
        paths.append(Path(tmp.name))
    return paths


def _is_meaningful(text: str) -> bool:
    """True if the model actually said something (not a 'not provided' placeholder)."""
    if not text:
        return False
    t = text.strip().lower()
    return not any(t.startswith(p) for p in _EMPTY_PREFIXES if p)


def _render_images(image_paths: list[Path]):
    cols = st.columns(2)
    for i, p in enumerate(image_paths):
        with cols[i % 2]:
            st.image(str(p), use_container_width=True)


def render_sidebar() -> str:
    st.sidebar.title("Aditi")
    st.sidebar.caption("A private medical paralegal that runs on your device.")
    label = st.sidebar.selectbox(
        "Model",
        list(config.MODELS.keys()),
        index=list(config.MODELS.keys()).index(config.DEFAULT_MODEL),
        help="Switch to E2B/E4B to see how smaller edge models behave on the same input.",
    )
    entry = config.MODELS[label]
    st.sidebar.caption(f"`{entry['id']}` — {entry['context']}")
    st.sidebar.success("🔒 On-device. No network call once the model is loaded.")
    return entry["id"], entry.get("audio", False)


def gather_inputs():
    """One unified query block. Returns (task, query, image_paths, audio_path)."""
    st.subheader("Your query")

    scenarios = list(config.SCENARIOS.keys())
    if "scenario" not in st.session_state:
        st.session_state["scenario"] = scenarios[0]
    if "query_text" not in st.session_state:
        st.session_state["query_text"] = config.SCENARIOS[scenarios[0]]["default_query"]

    def _sync_query():
        st.session_state["query_text"] = config.SCENARIOS[st.session_state["scenario"]]["default_query"]

    st.text_area(
        "Describe what you need in your own words. Aditi reads the documents (and voice) "
        "for the actual medical details.",
        key="query_text",
        height=90,
    )
    scenario = st.radio("Scenario", scenarios, key="scenario", horizontal=True, on_change=_sync_query)
    cfg = config.SCENARIOS[scenario]
    query = st.session_state["query_text"]

    img_mode = st.radio("Prescriptions", ["Use demo set", "Upload my own"], horizontal=True)
    if img_mode == "Use demo set":
        image_paths = [p for p in cfg["images"] if p.exists()]
        st.caption(f"{len(image_paths)} demo image(s) for “{scenario}”.")
    else:
        uploads = st.file_uploader(
            "Prescription / report images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
        )
        image_paths = _materialize(uploads, ".jpg") if uploads else []

    if cfg["audio"]:
        voice = st.radio("Voice", list(config.VOICE_CHOICES.keys()), horizontal=True, index=0)
        preset = config.VOICE_CHOICES[voice]
        audio_path = config.VOICE_PRESETS[preset] if preset else None
        if audio_path and not audio_path.exists():
            audio_path = None
    else:
        st.caption("Voice: this scenario uses text + images only for now (audio coming later).")
        audio_path = None

    # Show the inputs up front (handy for the demo) — collapsible.
    with st.expander("👁 Preview inputs", expanded=False):
        if image_paths:
            _render_images(image_paths)
        else:
            st.caption("No images loaded yet.")
        if audio_path:
            st.markdown("**Voice memo**")
            st.audio(str(audio_path))

    return cfg["task"], query, image_paths, audio_path


def _render_meds(title: str, meds, columns):
    st.markdown(f"**{title}**")
    if not meds:
        st.caption("— none listed —")
        return
    rows = [{c: m.get(c, "") for c in columns} if isinstance(m, dict) else {columns[0]: m} for m in meds]
    st.table(rows)


# ============================ UC1: substitution findings card ============================
def _esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_answer(record: dict):
    """The headline output — large, bordered, obvious."""
    st.markdown("## 🔍 Aditi's findings")
    finding = (record.get("plain_language_finding") or "").strip()
    subs = record.get("substitution_observations") or []
    if finding:
        icon, html = "⚠️", _esc(finding)
    elif subs:
        pairs = []
        for s in subs:
            if isinstance(s, dict):
                pairs.append(
                    f"the doctor wrote <b>{_esc(s.get('prescribed', '?'))}</b> but the bill shows "
                    f"<b>{_esc(s.get('dispensed', '?'))}</b>"
                )
        if pairs:
            icon = "⚠️"
            html = (
                "The pharmacy dispensed something different from the prescription — "
                + "; ".join(pairs)
                + ". Aditi can't judge whether that's appropriate; please ask your doctor to "
                "confirm the substitute and its dose are right."
            )
        else:
            icon, html = "⚠️", (
                "The pharmacy appears to have dispensed something different from what the doctor "
                "wrote. Please ask your doctor to confirm whether the substitute and its dose are right."
            )
    else:
        icon, html = "✅", (
            "No substitution detected between the prescription and the pharmacy bill. "
            "If anything still seems off, check with your doctor."
        )
    with st.container(border=True):
        st.markdown(
            f"<p style='font-size:1.2rem; line-height:1.55; margin:0'>{icon} {html}</p>",
            unsafe_allow_html=True,
        )


def _render_questions(record: dict):
    questions = record.get("questions_for_doctor") or []
    if not questions:
        return
    st.markdown("### ❓ Suggested questions for the doctor")
    with st.container(border=True):
        for q in questions:
            st.markdown(f"- {q}")


def _render_voice_check(record: dict, audio_path: Path | None, model_audio: bool):
    """Voice-interpretation sanity check — collapsible, lives under Detailed extraction."""
    if not audio_path:
        return  # no voice memo selected
    if not model_audio:
        with st.expander("🎤 Voice check — audio not used by this model"):
            st.caption(
                "This model is vision + text only (per Google's Gemma 4 docs: audio is supported "
                "on E2B and E4B only), so the voice memo was not used. Switch to E2B or E4B to "
                "include the voice."
            )
        return
    concern = record.get("patient_concern_from_audio") or ""
    if not _is_meaningful(concern):
        return
    with st.expander("🎤 Voice check — what Aditi heard"):
        st.markdown(f"> {concern}")
        st.caption("A quick check that the voice memo was interpreted correctly.")


def _render_extraction(record: dict):
    st.subheader("Detailed extraction")
    for field in ["patient_name", "date", "doctor_name", "hospital_or_clinic", "suspected_condition"]:
        val = record.get(field)
        if val:
            st.markdown(f"- **{field.replace('_', ' ').title()}:** {val}")

    complaints = record.get("complaints") or []
    if complaints:
        st.markdown("**Complaints**")
        for c in complaints:
            st.markdown(f"- {c}")

    _render_meds("Prescribed (what the doctor wrote)",
                 record.get("medications_prescribed"),
                 ["medication", "dose", "frequency", "duration"])
    _render_meds("Dispensed (what the pharmacy gave)",
                 record.get("medications_dispensed"),
                 ["medication", "dose", "quantity"])

    checks = record.get("_bill_crosscheck") or []
    if checks:
        st.markdown("**🔎 Cross-check against the pharmacy bill**")
        st.caption(
            "Aditi compared each handwritten medicine name to the printed bill. It flags, it does "
            "not correct — confirm anything flagged with your pharmacist."
        )
        icons = {"confirmed": "✅", "likely_misread": "📝", "unverified": "◻️"}
        for c in checks:
            st.markdown(f"- {icons.get(c['status'], '◻️')} **{c['prescribed']}** — {c['note']}")

    subs = record.get("substitution_observations") or []
    if subs:
        st.markdown("**Substitution observations (raw, from the model)**")
        for s in subs:
            if isinstance(s, dict):
                st.markdown(
                    f"- Prescribed **{s.get('prescribed', '?')}** → Dispensed "
                    f"**{s.get('dispensed', '?')}**: {s.get('what_you_notice', '')}"
                )
            else:
                st.markdown(f"- {s}")

    uncertain = record.get("illegible_or_uncertain") or []
    if uncertain:
        with st.expander("What the model could not read confidently"):
            for u in uncertain:
                st.markdown(f"- {u}")


def _render_technical(record: dict, include_raw_json: bool):
    st.subheader("Technical details")
    with st.expander("Prompt sent to the model"):
        st.code(record.get("_prompt", "(not captured)"), language="text")
    if include_raw_json:
        with st.expander("Raw model output (JSON)"):
            st.code(record.get("_raw", ""), language="json")
    with st.expander("Generation metrics"):
        st.json(record.get("_metrics") or {})


def render_result_card(record: dict, image_paths: list[Path], audio_path: Path | None,
                       user_context: str, model_audio: bool = True):
    st.divider()
    if record.get("_parse_error"):
        st.error(f"Could not parse JSON from the model: {record['_parse_error']}")
        with st.expander("Show raw model output"):
            st.code(record.get("_raw", ""), language="json")
        return

    _render_answer(record)
    _render_questions(record)
    st.caption(
        "⚠️ Aditi is a paralegal medical assistant, not a doctor. Please discuss with your "
        "doctor before any medication changes."
    )
    st.divider()
    _render_extraction(record)
    _render_voice_check(record, audio_path, model_audio)
    st.divider()
    _render_technical(record, include_raw_json=True)
    st.divider()
    st.caption(f"🔒 {config.PRIVACY_FOOTER}")


# ============================ UC2: health summary ============================
def render_summary(record: dict, image_paths: list[Path], user_context: str):
    st.divider()
    st.markdown("## 🩺 Aditi's health summary")
    md = (record.get("_markdown") or "").strip()
    if not md:
        st.error("The model returned an empty summary.")
        _render_technical(record, include_raw_json=False)
        return

    with st.container(border=True):
        st.markdown(md)
    st.download_button(
        "⬇️ Download summary (.md)",
        data=md,
        file_name="aditi_health_summary.md",
        mime="text/markdown",
    )
    st.caption(
        "⚠️ Aditi is a paralegal medical assistant, not a doctor. This organizes what is written "
        "in your documents for discussion with your doctor — it is not medical advice."
    )
    st.divider()
    _render_technical(record, include_raw_json=False)
    st.divider()
    st.caption(f"🔒 {config.PRIVACY_FOOTER}")


def main():
    model_id, model_audio = render_sidebar()
    st.title("🩺 Aditi")
    st.caption("Read what the doctor wrote. Hear what the patient said. Understand the connection.")

    task, query, image_paths, audio_path = gather_inputs()

    if st.button("Ask Aditi", type="primary", disabled=not image_paths):
        if not image_paths:
            st.warning("Load at least one prescription image first.")
            return
        with st.spinner("Loading model… (first run downloads weights)"):
            model, processor = get_cached_model(model_id)

        if task == "summary":
            with st.spinner("Reading your prescriptions and writing a summary…"):
                record = extractors.summarize_documents(model, processor, image_paths, user_context=query)
            render_summary(record, image_paths, query)
        else:
            # 26B (and 31B) are vision + text only — don't feed audio to a model that can't use it.
            effective_audio = audio_path if model_audio else None
            with st.spinner("Reading prescription, bill, tablets, and voice memo…"):
                record = extractors.extract_prescription(
                    model, processor, image_paths, effective_audio, user_context=query
                )
            record["_bill_crosscheck"] = crosscheck.crosscheck_prescribed_against_bill(record)
            render_result_card(record, image_paths, audio_path, query, model_audio)


if __name__ == "__main__":
    main()
