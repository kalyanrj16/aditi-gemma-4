# src/config.py
# Model registry, paths, and generation defaults for the Aditi demo.

from pathlib import Path

# --- Model registry (sidebar dropdown picks from this) ---
MODELS = {
    "Gemma 4 E2B (fast, edge variant — may hallucinate)": {
        "id": "mlx-community/gemma-4-e2b-it-4bit",
        "tier": "edge",
        "context": "fast capture, lowest memory, expect uncertainty",
    },
    "Gemma 4 E4B (balanced)": {
        "id": "mlx-community/gemma-4-e4b-it-4bit",
        "tier": "edge+",
        "context": "balanced speed vs accuracy",
    },
    "Gemma 4 26B MoE (best — for deep extraction)": {
        "id": "mlx-community/gemma-4-26b-a4b-it-4bit",
        "tier": "synthesis",
        "context": "best quality, slower, used for multi-doc synthesis",
    },
}

DEFAULT_MODEL = "Gemma 4 26B MoE (best — for deep extraction)"

# --- Paths (absolute, derived from this file's location) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PRESCRIPTIONS_DIR = DATA_DIR / "prescriptions"
VOICE_MEMOS_DIR = DATA_DIR / "voice_memos"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# --- Generation defaults ---
MAX_TOKENS = 1500

# --- Demo presets: the UC1 image set, in the order the prompt labels them ---
# Image 1+2: the doctor's prescription. Image 3: pharmacy bill. Image 4: dispensed tablets.
UC1_IMAGE_SET = [
    PRESCRIPTIONS_DIR / "UC1_prescription1A_medicalClarity.jpeg",
    PRESCRIPTIONS_DIR / "UC1_prescription1B_medicalClarity.jpeg",
    PRESCRIPTIONS_DIR / "UC1_medicalBill_medicalClarity.jpeg",
    PRESCRIPTIONS_DIR / "UC1_tablets_medicalClarity.jpeg",
]

# --- Voice memo presets (label -> path) for one-click demo switching ---
VOICE_PRESETS = {
    "US English (synthetic baseline)": VOICE_MEMOS_DIR / "UC1_voicememo_us_english.wav",
    "Indian English (UC3a)": VOICE_MEMOS_DIR / "UC3a_voicememo_indianenglish.wav",
    "Telugu (UC3b)": VOICE_MEMOS_DIR / "UC3b_voicememo_telugu.wav",
}

# --- Privacy footer shown on the result card ---
PRIVACY_FOOTER = (
    "Runs entirely on this device. No prescription, voice memo, or medical "
    "detail left your Mac. No cloud, no account, no network call."
)
