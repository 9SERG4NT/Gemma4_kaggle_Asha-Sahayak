import logging
import os

from config import WHISPER_MODEL_SIZE

logger = logging.getLogger(__name__)

_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        logger.info("Loading faster-whisper model: %s", WHISPER_MODEL_SIZE)
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device="cpu",
            compute_type="int8",
        )
        logger.info("faster-whisper model loaded.")
    return _whisper_model


def transcribe(audio_path: str, language_code: str | None = None) -> str:
    """
    Transcribe audio to text in the specified language.

    Args:
        audio_path: Path to audio file (wav, mp3, m4a, ogg).
        language_code: ISO 639-1 code (e.g. "hi", "sw", "ar").
                       None = auto-detect from audio.
    Returns:
        Transcribed text. Empty string on failure.
    """
    if not audio_path or not os.path.exists(audio_path):
        logger.warning("Audio path not found: %s", audio_path)
        return ""

    try:
        model = _get_model()
        kwargs = dict(beam_size=5, vad_filter=True)
        if language_code:
            kwargs["language"] = language_code

        segments, info = model.transcribe(audio_path, **kwargs)
        text = " ".join(seg.text for seg in segments).strip()
        logger.info(
            "Transcribed %.1fs audio → %d chars (detected lang: %s, prob: %.2f)",
            info.duration, len(text), info.language, info.language_probability,
        )
        return text
    except Exception as exc:
        logger.error("Transcription failed: %s", exc)
        return ""
