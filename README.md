# Aditi: a private medical paralegal that runs on your Mac

Aditi reads handwritten prescriptions, pharmacy bills, and spoken voice memos, and helps a patient
understand what their doctor wrote, **entirely on-device**. No cloud, no account, no network call.
Built for the Gemma 4 Challenge.

> Aditi is a paralegal, **not a doctor**. It organizes and summarizes what is already in your
> documents so you can have a better conversation with your doctor. It does not diagnose.

## What it does

Two scenarios, from one screen:

- **"Did I get the right medicine?"**: reads the prescription, the pharmacy bill, and a photo of the
  dispensed tablets (and an optional voice memo), and flags when the pharmacy dispensed something
  different from what the doctor wrote, with plain-language questions to ask the doctor.
- **"My health story"**: reads several past prescriptions and reports across specialists (including
  CPAP therapy reports) and produces a clean Markdown health summary to hand a new doctor.

Everything runs locally with Google's **Gemma 4** models via [MLX](https://github.com/ml-explore/mlx)
on Apple Silicon.

## Requirements

- macOS on Apple Silicon (M1, M2, M3, or M4)
- ~24 GB unified memory for the 26B model; the E2B and E4B edge models run in ~5 to 7 GB
- Python 3.11
- ~20 GB free disk for model weights (downloaded once from Hugging Face on first run)

## Setup & run

Using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv venv --python 3.11
uv pip install -r requirements.txt
uv run streamlit run src/aditi_app.py
```

Or with pip:

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run src/aditi_app.py
```

On first run the selected model downloads from Hugging Face (a few GB). After that, Aditi runs fully
offline. You can confirm by turning Wi-Fi off.

## Models (switch in the sidebar)

| Model | Role | Audio | Peak memory |
|---|---|---|---|
| Gemma 4 26B MoE (default) | best handwriting OCR plus multi-document synthesis | no (vision and text) | ~17.5 GB |
| Gemma 4 E4B | balanced; native voice including Telugu; cleanest prose | yes | ~7 GB |
| Gemma 4 E2B | fastest edge variant (~114 tok/s) | yes | ~5 GB |

Per Google's Gemma 4 docs, audio is native to **E2B and E4B only**; the 26B (and 31B) are vision and
text. Aditi only feeds the voice memo to models that can actually use it.

## Repo layout

- `src/`: the Streamlit app plus extraction, bill cross-check, and prompt modules
- `data/prescriptions_redacted/`: the demo image set (PII removed or substituted)
- `data/voice_memos/`: the three demo voice memos (US English, Indian English, Telugu)
- `outputs/`: empirical run artifacts (JSON plus full result-card screenshots) across all models
- `.streamlit/config.toml`: disables Streamlit telemetry (keeps the demo offline)

## Data & consent

The prescription images are from one real case, used with the patient's consent. All identifying
details (patient, doctor, and hospital names, IDs, address, phone, signatures) are substituted with
fictional values or redacted; drug names, doses, and clinical content are preserved exactly so the
model's extraction can be demonstrated honestly.

## The full writeup

The story behind Aditi, the model comparison, and what the experiments showed are in
**[build-submission.md](build-submission.md)**.
