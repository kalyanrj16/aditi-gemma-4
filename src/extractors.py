# src/extractors.py
# Thin wrapper around mlx-vlm for Gemma 4 multimodal extraction.
# Follows the pattern from references/post4_GemmaChallenge/multimodal_test.py:
#   load -> apply_chat_template(num_images) -> generate(image=[...], audio=[...]).

import json
import re
from pathlib import Path

from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template

from config import MAX_TOKENS
from prompts import build_extraction_prompt


def load_model(model_id: str):
    """Load a Gemma 4 model + processor. Returns (model, processor).

    Cache this in the app layer (st.cache_resource); loading is the slow part.
    """
    return load(model_id)


def run_extraction(
    model,
    processor,
    prompt: str,
    image_paths: list,
    audio_paths: list | None = None,
    max_tokens: int = MAX_TOKENS,
):
    """Format the prompt for N images and run a single multimodal generate call.

    image_paths and audio_paths are passed to generate() as lists (the bugfix
    noted in the reference: audio must be a list, not a bare string). Returns the
    mlx-vlm GenerationResult (use .text for the output, plus timing/token fields).
    """
    images = [str(p) for p in image_paths]
    audios = [str(p) for p in (audio_paths or [])]

    formatted = apply_chat_template(
        processor,
        model.config,
        prompt,
        num_images=len(images),
        num_audios=len(audios),
    )

    # Sanity check: one placeholder token per input, or the model silently drops it.
    img_token_count = formatted.count("<|image|>")
    if img_token_count != len(images):
        raise ValueError(
            f"Prompt has {img_token_count} image tokens but {len(images)} images "
            f"were provided. apply_chat_template did not insert one per image."
        )
    audio_token_count = formatted.count("<|audio|>")
    if audio_token_count != len(audios):
        raise ValueError(
            f"Prompt has {audio_token_count} audio tokens but {len(audios)} audio "
            f"files were provided. apply_chat_template did not insert one per audio."
        )

    return generate(
        model,
        processor,
        formatted,
        image=images,
        audio=audios if audios else None,
        max_tokens=max_tokens,
        verbose=False,
    )


def parse_json(raw: str) -> dict:
    """Pull a JSON object out of the model's raw output.

    Strips ``` fences, then slices from the first { to the last }. Returns the
    parsed dict, or {"_parse_error": ..., "_raw": raw} so the UI can still show
    what the model produced instead of crashing.
    """
    text = raw.strip()
    # Drop a leading ```json / ``` fence and trailing ``` if present.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {"_parse_error": "no JSON object found in output", "_raw": raw}

    candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        return {"_parse_error": str(e), "_raw": raw}


def extract_prescription(
    model,
    processor,
    image_paths: list,
    audio_path: Path | str | None = None,
    max_tokens: int = MAX_TOKENS,
) -> dict:
    """High-level UC1 entry point: build the prompt, run extraction, parse JSON.

    Returns the parsed record dict. On parse failure the dict carries
    _parse_error and _raw so the caller can surface the raw output.
    """
    audio_paths = [audio_path] if audio_path else None
    prompt = build_extraction_prompt(
        num_images=len(image_paths),
        has_audio=audio_path is not None,
    )
    result = run_extraction(
        model, processor, prompt, image_paths, audio_paths, max_tokens=max_tokens
    )
    text = result.text
    record = parse_json(text)
    # Keep the raw text and generation metrics for the demo / debugging.
    record.setdefault("_raw", text)
    record["_metrics"] = {
        "generation_tokens": result.generation_tokens,
        "generation_tps": round(result.generation_tps, 1) if result.generation_tps else None,
        "prompt_tokens": result.prompt_tokens,
        "generation_seconds": (
            round(result.generation_tokens / result.generation_tps, 1)
            if result.generation_tps
            else None
        ),
        "peak_memory_gb": round(result.peak_memory, 2) if result.peak_memory else None,
    }
    return record
