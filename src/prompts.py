# src/prompts.py
# System prompts, kept separate so we can iterate on wording without touching code.

# The paralegal framing carried over from the Days 1-3 reference scripts.
# This is the guardrail: organize and summarize, never diagnose.
PARALEGAL_GUARDRAIL = """I am the patient. Act as my paralegal medical assistant. You are NOT a doctor.
You will NOT diagnose, prescribe, suggest medication changes, or make clinical judgments.
Your job is to ORGANIZE and SUMMARIZE what is already in these inputs so I can have an
informed conversation with my doctor and pharmacist."""

# Exact input labels for the UC1 set, in the order images are passed to the model.
# (config.UC1_IMAGE_SET uses this same order.)
UC1_INPUT_LABELS = [
    "Image 1: prescription page 1 (what the doctor wrote)",
    "Image 2: prescription page 2 (what the doctor wrote)",
    "Image 3: pharmacy bill (what the pharmacy actually dispensed)",
    "Image 4: photo of the dispensed tablets",
]
AUDIO_LABEL = "Audio: patient's voice memo describing the situation"

# The JSON shape we ask the model to return. medications_prescribed vs
# medications_dispensed is the core of UC1 — we want the model to surface any
# mismatch on its own, with no external drug database backing it up.
EXTRACTION_SCHEMA = """Return a single JSON object with these exact fields:

- patient_name: from the prescription, or "not specified"
- date: visit/prescription date, or "not specified"
- doctor_name: from the prescription, or "not specified"
- hospital_or_clinic: from the letterhead, or "not specified"
- suspected_condition: what the doctor appears to suspect or is treating (e.g. nerve pain), or "not specified"
- complaints: list combining the audio and the handwritten notes
- medications_prescribed: list of what the DOCTOR wrote. Each item: {medication, dose, frequency, duration}
- medications_dispensed: list of what the PHARMACY actually gave (from the bill and the tablet photo). Each item: {medication, dose, quantity}
- substitution_observations: list. For any prescribed medication that does NOT match what was dispensed, note it here as a plain observation: {prescribed, dispensed, what_you_notice}. If everything matches, use an empty list.
- patient_concern_from_audio: in one or two sentences, what the patient says they are worried about
- illegible_or_uncertain: list of anything you saw but could not read or confidently extract. Be honest.
- questions_for_doctor: list of questions the patient might raise, framed as organizational prompts, NOT medical advice"""

EXTRACTION_RULES = """RULES:
- Be exhaustively honest about uncertainty. If you cannot read handwriting, say so in illegible_or_uncertain rather than guessing.
- If a medication name is unclear, write "unclear" rather than inventing one.
- Do NOT fabricate content. Empty arrays and "not specified" are acceptable answers.
- Do NOT diagnose, do NOT suggest treatments, do NOT recommend medication changes.
- Cross-reference the inputs: the prescription, the bill, the tablets, and the audio describe the SAME situation and complement each other.
- Output ONLY the JSON object. No prose before or after it."""


def build_extraction_prompt(num_images: int, has_audio: bool) -> str:
    """Assemble the full extraction prompt for the given inputs.

    Uses the UC1 input labels for up to 4 images (the canonical demo set),
    falling back to generic labels for anything beyond that.
    """
    labels = []
    for i in range(num_images):
        if i < len(UC1_INPUT_LABELS):
            labels.append(UC1_INPUT_LABELS[i])
        else:
            labels.append(f"Image {i + 1}: additional document")
    if has_audio:
        labels.append(AUDIO_LABEL)

    manifest = "\n".join(labels)

    return f"""{PARALEGAL_GUARDRAIL}

You have been given these inputs:
{manifest}

{EXTRACTION_SCHEMA}

{EXTRACTION_RULES}"""
