# Aditi — Gemma 4 Challenge Submission

## What this project is

Aditi is a private medical paralegal for Indian patients, built for the Dev.to Gemma 4 Challenge.
It reads handwritten prescriptions, listens to symptom voice memos, and helps patients understand 
what their doctor wrote, without sending data to any cloud.

## The submission

Submitting to BOTH tracks of the Gemma 4 Challenge:
- **Build track:** a working macOS Streamlit demo + writeup + 90-120 second video
- **Write track:** an empirical writeup on what I learned building it

Deadline: Monday May 25, 2026, 12:30 PM IST (= Sunday May 24, 11:59 PM PDT).

## The thesis

Indian healthcare has information asymmetry that costs lives. Doctors don't have time to explain. 
Pharmacies substitute prescribed medicines for cheaper alternatives. Specialists are concentrated 
in tier-1 cities. Family medical history isn't stored anywhere useful. Stigmatized conditions don't 
get asked about.

Aditi is a private paralegal for the patient. It reads what the doctor wrote, hears what the 
patient described, and helps the patient understand the connections, so they can ask their doctor 
the right questions, take medications correctly, and notice when something doesn't fit.

The architectural constraint: this AI must stay on the patient's device. Family medical history is 
the most sensitive data a person owns. Stigmatized conditions cannot risk cloud trails. Privacy 
must be by architecture, not by promise.

## The hook story (for the writeup)

Last week, my mother was prescribed PENTANERVE for nerve pain in her legs. Her doctor suspected 
diabetic neuropathy. The pharmacy didn't have PENTANERVE and gave her GABAPIN instead. Two days 
later, her pain hasn't reduced. She suspects she's on the wrong medicine.

Both medications are real first-line treatments for diabetic neuropathy. They're in the same drug 
class (gabapentinoids). But the dose conversion is not one-to-one, and pharmacy substitutions 
without explicit doctor approval are common in India. Was the substitution legitimate? Was the 
dose equivalent? Is 2 days enough time to judge?

To answer this without Aditi, I would have spent hours with cloud AI, sending my mother's name, 
medications, and symptoms to servers in another country. Aditi is what I would have wanted 
instead: an honest paralegal on my own device.

## Architecture (Apple Silicon, tiered)

- **Tier 1 (capture):** iPhone E2B 4-bit via MLX. Fast preview, capture role.
- **Tier 2 (synthesis):** Mac with Gemma 4 26B MoE via mlx-vlm. Deep extraction. v1 demo target.
- **Tier 3 (optional boost):** Cloud 26B MoE via user's own Google AI Studio API key. Opt-in.

The iOS work from Saturday May 23 demonstrated 5 failure modes that justify the tiered design 
(see WRITE PIECE section below). iOS is EVIDENCE platform for v1, not the demo platform.

## What runs where in v1

| Capability | iPhone (E2B 4-bit) | Mac (26B MoE) |
|---|---|---|
| Text generation | Works (19-27 tok/s) | Works |
| Image extraction (single) | Partial, hallucinates on Indian handwriting | Works |
| Image + audio multimodal | Fails (5 documented failure modes) | Works (cross-modal grounding) |
| Multi-document synthesis | Fails at 2 docs (repetition loops) | Works to 10 docs |
| Indic language audio | Too weak to test | Honestly limited, v2 roadmap |

This is the empirical case for Mac-primary v1.

## Build piece use cases (for v1 demo)

### UC1 — Medication Clarity (headline)

The mother's PENTANERVE/GABAPIN substitution case.
- Prescription image + voice memo (in any of 3 languages, see below)
- Aditi extracts the prescription
- Cross-references substitution: same drug class, dose conversion not 1:1
- Generates a clear question to ask the doctor

This is the headline of the Build piece and the video.

### UC2 — Longitudinal Care (DEFERRED)

Multi-specialist synthesis across visits (gastro, ENT, pulmonologist + CPAP report).
Currently parked. Old prescriptions are in `data/prescriptions/old/` and 
`data/voice_memos/old/`. Will be revisited if time permits Sunday afternoon.

### UC3 — Indic Voice (multilingual reality)

Tests how Aditi handles the languages real Indian patients actually use.
- **UC3a:** Same UC1 script in Indian-accented English (Kalyan's voice)
- **UC3b:** Same UC1 script in Telugu (Kalyan's voice)
- Demonstrates: model behavior across language/accent on the same prescription input

UC3 is for the Build piece (showing multilingual range). The deeper analysis 
of what works vs what doesn't goes in the Write piece.

## Write piece content (not for Build demo)

These topics live in the Write piece exclusively, not the Build demo:

1. **5 iOS failure modes** with root cause analysis (model vs app vs prompting)
2. **Epistemic honesty across model sizes** (E2B fabricates, 26B MoE hedges) 
   - Use `data/prescriptions/old/prescription_uc1_gastro_foldedpaper.jpg` for this analysis
3. **Multi-document synthesis ceiling** (iPhone fails at 2, Mac at 10)
4. **Voice modality's role and limits** (compares UC1, UC3a, UC3b empirically)
5. **Indic content gap** (independent verification of Avinash Seethalam's Telugu vision finding)
6. **Design principles for honest medical AI**

The Write piece grounds every claim in actual experiments and outputs from this project.

## Today's specific goal (Sunday May 24)

Build a working Streamlit demo on macOS that demonstrates UC1 end-to-end. Then UC3a and UC3b 
on the same prescription. Then record a 90-120 second screen capture video.

Definition of done for today:
- Streamlit app starts with `streamlit run src/aditi_app.py`
- UC1 demo works: upload prescription images + voice memo → result card appears
- UC3a and UC3b voice memos produce visibly different model behavior on the same prescription
- Demo screen capture recorded (60-120 seconds)
- LOG.md updated with day's progress

## Test data assets (canonical location)

### data/prescriptions/

Current Build set (UC1 active):
- `UC1_prescription1A_medicalClarity.jpeg` — mother's PENTANERVE prescription page 1
- `UC1_prescription1B_medicalClarity.jpeg` — mother's PENTANERVE prescription page 2
- `UC1_medicalBill_medicalClarity.jpeg` — pharmacy bill showing the substitution to GABAPIN
- `UC1_tablets_medicalClarity.jpeg` — photo of the actual GABAPIN tablets dispensed

Deferred (UC2, moved to `data/prescriptions/old/`):
- All multi-specialist prescriptions (gastro doctor + assistant, ENT, pulmonologist, CPAP report)

Write piece reference (still in `data/prescriptions/old/`):
- `prescription_uc1_gastro_foldedpaper.jpg` — the folded paper hard-OCR case

### data/voice_memos/

Current Build set:
- `UC1_voicememo_us_english.wav` — synthetic baseline via macOS `say` with Ava (Premium). 
  Clean US English, ~18 seconds. The UC1 script.
- `UC3a_voicememo_indianenglish.wav` — Kalyan's real voice, Indian English. Same UC1 script. 
  ~19 seconds. Tests accent handling.
- `UC3b_voicememo_telugu.wav` — Kalyan's Telugu version. ~22 seconds. Tests regional language.

All three are 16kHz mono PCM s16le (verified). This matches Gemma 4's audio processor format.

## Model selection (provision in src/)

The Streamlit app should expose a sidebar dropdown to switch between Gemma 4 model variants 
at runtime. This is important for the demo (live comparison between E2B and 26B MoE behaviors).

`src/config.py` should define:

```python
MODELS = {
    "Gemma 4 E2B (fast edge variant, may hallucinate)": {
        "id": "mlx-community/gemma-4-e2b-it-4bit",
        "tier": "edge",
    },
    "Gemma 4 E4B (balanced)": {
        "id": "mlx-community/gemma-4-e4b-it-4bit",
        "tier": "edge+",
    },
    "Gemma 4 26B MoE (best, default for synthesis)": {
        "id": "mlx-community/gemma-4-26b-a4b-it-4bit",
        "tier": "synthesis",
    },
}
DEFAULT_MODEL = "Gemma 4 26B MoE (best, default for synthesis)"
```

The Streamlit sidebar uses `st.selectbox(...)` to pick from MODELS.

## references/ folder — READ-ONLY

This folder contains prior work that informs Aditi v1. CC may READ these files to understand 
patterns and prior findings. CC must NOT modify, delete, rename, or run code from these folders.

### references/post4_GemmaChallenge/

The Days 1-3 mlx-vlm Python experiments.

Key files to reference for patterns:
- `multimodal_test.py` — image + audio multimodal extraction (THE PATTERN TO REUSE)
- `multi_doc_summary.py` — multi-document synthesis with 26B MoE
- `generate_health_report.py` — structured health report generation
- `fromGemma.md` — outputs and findings
- `01_compass_artifact.md`, `02_compass_artifact.md` — planning context
- `notes.md` — daily notes Days 1-3

### references/post4_Aditi/

The iOS Swift work and Flutter experiments (NOT for porting to Python).

- `AditiIOS/` — native iOS app (Swift + MLX) tested heavily Saturday
- `swift-experiments/gemma-4-swift-mlx/` — Swift MLX package source
- `flutter_gemma/` — brief Flutter exploration
- `hello_aditi/` — early experiment
- `notes.md` — iOS testing notes Saturday May 23

This is used as EVIDENCE in the Write piece. CC should NOT need to read most of this folder.

## Editorial preferences

The `blog-publishing-workflow` skill handles em-dashes and AI-cadence patterns automatically 
during writeup drafting (read it when working on writeup/ files). For all other writing 
(code comments, LOG entries, prompts to the model), follow these:

- Informal practitioner voice, not academic.
- Direct sentences, not hedged ones.
- No marketing flourish, no salesy adjectives ("groundbreaking", "revolutionary", "seamless").
- Specific over abstract: "Mac 26B MoE refused to fabricate the doctor name" beats 
  "the larger model showed epistemic humility".

## Tech stack

- Python 3.11+ (probably already installed; verify via `python --version`)
- mlx-vlm for Gemma 4 multimodal on Apple Silicon (already installed from Days 1-3)
- Streamlit for the UI (`pip install streamlit` if not present)
- Standard libs for JSON, file handling, audio loading
- ffmpeg for any audio conversion needs (already installed)

## What CC writes today goes in:

- `src/` — application code (aditi_app.py, extractors.py, correlator.py, drug_db.py, prompts.py, config.py)
- `writeup/` — Build piece and Write piece drafts
- `LOG.md` — daily progress notes (CC and Kalyan both write here)
- `outputs/` — demo screenshots, JSON results, video frames

Nothing outside these directories should be modified by CC. Specifically:
- `data/` — read-only, do not modify file contents
- `references/` — read-only at OS level (chmod -R a-w applied)
- `CLAUDE.md` — only modified by Kalyan, not by CC
- `README.md` — only modified by Kalyan

## Constraints for today

- Focus on UC1 first. UC3a and UC3b are additions, not blockers.
- One Streamlit app, one flow. No tabs or multi-page features.
- The result card should clearly show: extracted data + original photo side-by-side + warnings + 
  privacy footer.
- Demo must run entirely offline (verify by turning off WiFi during testing).
- No iOS or Swift work today. iOS findings live in the Write piece only.

## Reference paths (external, do not modify)

External original paths exist for these references but CC should never read them — 
the canonical copies are inside `references/`.
