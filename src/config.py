# src/config.py (conceptual — Claude Code CLI in VS Code will implement)

from turtle import st


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


# Have this in aditi_app.py and then later delete it from there once we have the config.py file working
# selected_model = st.sidebar.selectbox(
#     "Model",
#     list(MODELS.keys()),
#     index=list(MODELS.keys()).index(DEFAULT_MODEL),
#     help="Switch to E2B to see how smaller models behave on the same input"
# )