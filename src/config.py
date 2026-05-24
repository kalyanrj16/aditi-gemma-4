# src/config.py
# Model registry, paths, scenarios, and generation defaults for the Aditi demo.

from pathlib import Path

# --- Model registry (sidebar dropdown picks from this) ---
# "audio" = native audio input. Per Google's Gemma 4 docs, audio is featured on
# E2B and E4B only; the 26B MoE and 31B dense models are vision + text only.
MODELS = {
    "Gemma 4 E2B (fast, edge variant — may hallucinate)": {
        "id": "mlx-community/gemma-4-e2b-it-4bit",
        "tier": "edge",
        "audio": True,
        "context": "fast capture, lowest memory, native audio, expect uncertainty",
    },
    "Gemma 4 E4B (balanced)": {
        "id": "mlx-community/gemma-4-e4b-it-4bit",
        "tier": "edge+",
        "audio": True,
        "context": "balanced speed vs accuracy, native audio",
    },
    "Gemma 4 26B MoE (best — for deep extraction)": {
        "id": "mlx-community/gemma-4-26b-a4b-it-4bit",
        "tier": "synthesis",
        "audio": False,
        "context": "best quality, slower; vision + text only (no audio)",
    },
}

DEFAULT_MODEL = "Gemma 4 26B MoE (best — for deep extraction)"

# --- Paths (absolute, derived from this file's location) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PRESCRIPTIONS_DIR = DATA_DIR / "prescriptions"
PRESCRIPTIONS_REDACTED_DIR = DATA_DIR / "prescriptions_redacted"
VOICE_MEMOS_DIR = DATA_DIR / "voice_memos"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# --- Generation defaults ---
MAX_TOKENS = 1500          # UC1 substitution extraction
SUMMARY_MAX_TOKENS = 3000  # UC2 multi-document health summary (longer output)

# --- UC1 image set: the medicine-substitution case (redacted) ---
# Image 1+2: the doctor's prescription. Image 3: pharmacy bill. Image 4: dispensed tablets.
UC1_IMAGE_SET = [
    PRESCRIPTIONS_REDACTED_DIR / "UC1_prescription1A_medicalClarity_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC1_prescription1B_medicalClarity_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC1_medicalBill_medicalClarity_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC1_tablets_medicalClarity_redacted.jpeg",
]
# Original (unredacted) paths — gitignored, kept for local reference only:
# UC1_ORIGINAL_IMAGE_SET = [
#     PRESCRIPTIONS_DIR / "UC1_prescription1A_medicalClarity.jpeg",
#     PRESCRIPTIONS_DIR / "UC1_prescription1B_medicalClarity.jpeg",
#     PRESCRIPTIONS_DIR / "UC1_medicalBill_medicalClarity.jpeg",
#     PRESCRIPTIONS_DIR / "UC1_tablets_medicalClarity.jpeg",
# ]

# --- UC2 image set: the multi-specialist "health story" case (redacted) ---
# Multiple past prescriptions across specialists; no pharmacy bill / tablets.
UC2_IMAGE_SET = [
    PRESCRIPTIONS_REDACTED_DIR / "UC2_prescription_cardiologist_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_prescription_gastro_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_prescription1A_ortho_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_prescription1B_ortho_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_prescription1A_pulmonologist_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_prescription1B_pulmonologist_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_CPAP-1A_redacted.jpeg",
    PRESCRIPTIONS_REDACTED_DIR / "UC2_CPAP-1B_redacted.jpeg",
]

# --- Voice memo presets (label -> path) ---
VOICE_PRESETS = {
    "US English (synthetic baseline)": VOICE_MEMOS_DIR / "UC1_voicememo_us_english.wav",
    "Indian English (UC3a)": VOICE_MEMOS_DIR / "UC3a_voicememo_indianenglish.wav",
    "Telugu (UC3b)": VOICE_MEMOS_DIR / "UC3b_voicememo_telugu.wav",
}

# Friendly Voice radio labels (one line in the UI) -> preset key (or None).
VOICE_CHOICES = {
    "English": "US English (synthetic baseline)",
    "Indian English": "Indian English (UC3a)",
    "Telugu": "Telugu (UC3b)",
    "No audio": None,
}

# --- Pre-loaded query text per scenario ---
# CONTEXT ONLY: no drug names, doses, or specific symptoms — the model still
# extracts every medical fact from the images (and audio).
USER_CONTEXT_DEFAULT = (
    "My mother is 72. She visited the doctor for leg pain and the doctor wrote "
    "some tablets. But the pharmacy gave different tablets. Can you help her?"
)
HEALTH_STORY_QUERY_DEFAULT = (
    "I'm seeing a new doctor and need to share my health history. Please read "
    "these prescriptions and put together a clear summary the doctor can review quickly."
)

# --- Scenarios: the radio routes which task Aditi runs ---
SCENARIOS = {
    "Did I get the right medicine?": {
        "task": "substitution",
        "images": UC1_IMAGE_SET,
        "default_query": USER_CONTEXT_DEFAULT,
        "audio": True,
    },
    "My health story": {
        "task": "summary",
        "images": UC2_IMAGE_SET,
        "default_query": HEALTH_STORY_QUERY_DEFAULT,
        "audio": False,  # text + images only for now; audio is a later addition
    },
}

# --- Privacy footer shown on the result card ---
PRIVACY_FOOTER = (
    "Runs entirely on this device. No prescription, voice memo, or medical "
    "detail left your Mac. No cloud, no account, no network call."
)
