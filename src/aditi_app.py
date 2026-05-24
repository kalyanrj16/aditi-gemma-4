# src/aditi_app.py
# Aditi — UC1 demo. Single flow: pick a model, give it the prescription set +
# a voice memo, run one multimodal Gemma 4 call, show what the model produced.
#
# Run with:  streamlit run src/aditi_app.py

import tempfile
from pathlib import Path

import streamlit as st

import config
import extractors

st.set_page_config(page_title="Aditi", page_icon="🩺", layout="wide")


# --- Model loading (cached so we only pay the load cost once per model) ---
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


def render_sidebar() -> str:
    """Model picker + privacy badge. Returns the selected model id."""
    st.sidebar.title("Aditi")
    st.sidebar.caption("A private medical paralegal that runs on your device.")

    label = st.sidebar.selectbox(
        "Model",
        list(config.MODELS.keys()),
        index=list(config.MODELS.keys()).index(config.DEFAULT_MODEL),
        help="Switch to E2B to see how a smaller edge model behaves on the same input.",
    )
    entry = config.MODELS[label]
    st.sidebar.caption(f"`{entry['id']}` — {entry['context']}")
    st.sidebar.success("🔒 On-device. No network call once the model is loaded.")
    return entry["id"]


def gather_inputs():
    """Collect image paths and an optional audio path. Returns (image_paths, audio_path)."""
    st.subheader("1. Prescription & pharmacy inputs")

    img_mode = st.radio(
        "Images",
        ["Use the UC1 demo set", "Upload my own"],
        horizontal=True,
    )
    if img_mode == "Use the UC1 demo set":
        image_paths = [p for p in config.UC1_IMAGE_SET if p.exists()]
        st.caption(f"{len(image_paths)} images: prescription (2 pages), pharmacy bill, dispensed tablets.")
    else:
        uploads = st.file_uploader(
            "Prescription pages, pharmacy bill, tablet photo",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
        )
        image_paths = _materialize(uploads, ".jpg") if uploads else []

    st.subheader("2. Voice memo")
    voice_mode = st.radio(
        "Audio",
        list(config.VOICE_PRESETS.keys()) + ["Upload my own", "No audio"],
        index=0,
    )
    if voice_mode == "No audio":
        audio_path = None
    elif voice_mode == "Upload my own":
        up = st.file_uploader("Voice memo (16kHz mono WAV works best)", type=["wav"])
        audio_path = _materialize([up], ".wav")[0] if up else None
    else:
        candidate = config.VOICE_PRESETS[voice_mode]
        audio_path = candidate if candidate.exists() else None

    return image_paths, audio_path


def _render_meds(title: str, meds, columns):
    st.markdown(f"**{title}**")
    if not meds:
        st.caption("— none listed —")
        return
    rows = [{c: m.get(c, "") for c in columns} if isinstance(m, dict) else {columns[0]: m} for m in meds]
    st.table(rows)


def render_result_card(record: dict, image_paths: list[Path], audio_path: Path | None):
    st.divider()
    st.subheader("Result")

    m = record.get("_metrics")
    if m:
        st.caption(
            f"⏱ {m.get('generation_tokens', '?')} tokens in "
            f"{m.get('generation_seconds', '?')}s "
            f"({m.get('generation_tps', '?')} tok/s) · "
            f"peak {m.get('peak_memory_gb', '?')} GB"
        )

    if record.get("_parse_error"):
        st.error(f"Could not parse JSON from the model: {record['_parse_error']}")
        with st.expander("Show raw model output"):
            st.code(record.get("_raw", ""), language="json")
        return

    left, right = st.columns([1, 1])

    # Left: the original inputs the model actually saw.
    with left:
        st.markdown("**What Aditi looked at**")
        for p in image_paths:
            st.image(str(p), use_container_width=True)
        if audio_path:
            st.audio(str(audio_path))

    # Right: the model's structured extraction, shown as-is.
    with right:
        st.markdown("**What the model read**")
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

    # Full width below: the model's own observations and questions.
    subs = record.get("substitution_observations") or []
    if subs:
        st.markdown("**What the model noticed about substitutions**")
        for s in subs:
            if isinstance(s, dict):
                st.warning(
                    f"Prescribed: **{s.get('prescribed', '?')}** → Dispensed: "
                    f"**{s.get('dispensed', '?')}**\n\n{s.get('what_you_notice', '')}"
                )
            else:
                st.warning(str(s))

    concern = record.get("patient_concern_from_audio")
    if concern:
        st.info(f"**From the voice memo:** {concern}")

    questions = record.get("questions_for_doctor") or []
    if questions:
        st.markdown("**Questions you might ask your doctor**")
        for q in questions:
            st.markdown(f"- {q}")

    uncertain = record.get("illegible_or_uncertain") or []
    if uncertain:
        with st.expander("What the model could not read confidently"):
            for u in uncertain:
                st.markdown(f"- {u}")

    with st.expander("Raw model output (JSON)"):
        st.code(record.get("_raw", ""), language="json")

    st.divider()
    st.caption(f"🔒 {config.PRIVACY_FOOTER}")


def main():
    model_id = render_sidebar()
    st.title("🩺 Aditi")
    st.caption("Read what the doctor wrote. Hear what the patient said. Understand the connection.")

    image_paths, audio_path = gather_inputs()

    if st.button("Run Aditi", type="primary", disabled=not image_paths):
        if not image_paths:
            st.warning("Add at least one image first.")
            return
        with st.spinner("Loading model… (first run downloads weights)"):
            model, processor = get_cached_model(model_id)
        with st.spinner("Reading prescription, bill, tablets, and voice memo…"):
            record = extractors.extract_prescription(model, processor, image_paths, audio_path)
        render_result_card(record, image_paths, audio_path)


if __name__ == "__main__":
    main()
