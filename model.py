import base64
import io
import json
import logging
from collections.abc import Generator

import requests
from PIL import Image

from config import (
    HF_MODEL_ID,
    HF_TOKEN,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    USE_OLLAMA,
)
from prompts import build_system_prompt
from utils import resize_image

logger = logging.getLogger(__name__)


def _image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def stream_ollama(
    image: Image.Image, symptom_text: str = "", language: str = "Marathi"
) -> Generator[str, None, None]:
    """
    Stream tokens from Ollama one chunk at a time.
    Yields the *accumulated* text so the Gradio textbox updates in place.
    """
    image = resize_image(image)
    b64 = _image_to_base64(image)
    system_prompt = build_system_prompt(language)

    user_content = "Please examine the patient's condition shown in this image."
    if symptom_text.strip():
        user_content += f"\n\nSymptom description: {symptom_text.strip()}"

    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": user_content,
        "images": [b64],
        "stream": True,
        "options": {
            "num_ctx": 4096,      # was 131 072 — massive speedup
            "num_predict": 450,   # cap output at ~450 tokens
            "num_gpu": 99,        # use every GPU layer that fits in VRAM
            "temperature": 0.3,   # more deterministic / structured output
        },
    }

    url = f"{OLLAMA_BASE_URL}/api/generate"
    accumulated = ""
    try:
        with requests.post(url, json=payload, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                chunk = json.loads(raw_line)
                token = chunk.get("response", "")
                accumulated += token
                yield accumulated          # Gradio replaces the textbox each yield
                if chunk.get("done"):
                    break
    except requests.exceptions.ConnectionError:
        yield f"⚠ Ollama not reachable at {OLLAMA_BASE_URL}. Run: ollama serve"
    except requests.exceptions.Timeout:
        yield accumulated + "\n\n⚠ Request timed out."
    except Exception as exc:
        logger.error("Ollama stream error: %s", exc)
        yield accumulated + f"\n\n⚠ Error: {exc}"


_HF_UNAVAILABLE_MSG = (
    "ℹ️  Gemma 4 E4B is not yet available on the HF Inference API serverless tier.\n\n"
    "To use ASHA Sahayak with real Gemma 4 inference:\n\n"
    "1. 🖥️  Run locally with Ollama:\n"
    "   ollama pull gemma4:e4b\n"
    "   python app.py\n\n"
    "2. 📓  View the full interactive Kaggle notebook:\n"
    "   https://kaggle.com/code  (search: ASHA Sahayak)\n\n"
    "The HF Space demonstrates the UI and architecture. "
    "Full offline inference runs on-device via Ollama — "
    "keeping patient data private and requiring no internet connection."
)


def query_hf_inference(
    image: Image.Image, symptom_text: str = "", language: str = "Marathi"
) -> str:
    """HF Inference API fallback (cloud, non-streaming).

    Gemma 4 E4B does not currently have an HF Inference API provider.
    Returns a clear informational message instead of crashing.
    """
    if not HF_TOKEN:
        return _HF_UNAVAILABLE_MSG

    image = resize_image(image)
    b64 = _image_to_base64(image)
    system_prompt = build_system_prompt(language)

    user_text = "Please examine the patient's condition shown in this image."
    if symptom_text.strip():
        user_text += f"\n\nSymptom description: {symptom_text.strip()}"

    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "model": HF_MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    {"type": "text", "text": user_text},
                ],
            },
        ],
        "max_tokens": 450,
    }

    url = f"https://router.huggingface.co/hf-inference/v1/chat/completions"
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in (404, 400, 403):
            logger.warning("HF Inference API unavailable for %s: %s", HF_MODEL_ID, exc)
            return _HF_UNAVAILABLE_MSG
        logger.error("HF query failed: %s", exc)
        raise
    except Exception as exc:
        logger.error("HF query failed: %s", exc)
        raise


def run_inference(
    image: Image.Image, symptom_text: str = "", language: str = "Marathi"
) -> Generator[str, None, None] | str:
    """
    Primary entry point.
    Returns a generator (Ollama streaming) or a string (HF fallback).
    """
    if USE_OLLAMA:
        return stream_ollama(image, symptom_text, language)
    return query_hf_inference(image, symptom_text, language)
