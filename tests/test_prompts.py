"""
Phase 3 — Static tests for prompts.py.
Verifies all required guardrails are present in the dynamic prompt.
No model or Ollama required.

Run with: python -m pytest tests/test_prompts.py -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts import SYSTEM_PROMPT, build_system_prompt


def test_language_placeholder_injected():
    """build_system_prompt injects the target language into the prompt."""
    for lang in ["Marathi", "French", "Swahili", "Hindi"]:
        prompt = build_system_prompt(lang)
        assert lang in prompt, f"Language '{lang}' not found in generated prompt"


def test_three_section_descriptions_present():
    """Prompt must describe all three required output sections."""
    required = [
        "What I observe",
        "Immediate first aid",
        "Is an urgent doctor visit needed",
    ]
    for phrase in required:
        assert phrase in SYSTEM_PROMPT, f"Section description missing: {phrase!r}"


def test_safety_triggers_present():
    """All critical urgent-referral triggers must be listed in the prompt."""
    triggers = [
        "Heavy or uncontrolled bleeding",
        "Snake bite or animal bite",
        "Burns larger than",
        "Signs of infection",
        "Difficulty breathing",
    ]
    for trigger in triggers:
        assert trigger in SYSTEM_PROMPT, f"Safety trigger missing: {trigger!r}"


def test_no_medication_names_in_prompt():
    """Prompt must not suggest specific drug names."""
    banned = ["paracetamol", "ibuprofen", "amoxicillin", "dettol", "betadine"]
    for drug in banned:
        assert drug.lower() not in SYSTEM_PROMPT.lower(), (
            f"Banned medication name in prompt: {drug!r}"
        )


def test_uncertainty_language_required():
    """Prompt must instruct the model never to diagnose with certainty."""
    assert "NEVER diagnose with certainty" in SYSTEM_PROMPT


def test_triage_aid_framing():
    """Prompt must frame the assistant as a triage aid, not a doctor."""
    assert "triage aid" in SYSTEM_PROMPT
    assert "not a doctor" in SYSTEM_PROMPT


def test_output_language_rule_present():
    """Prompt must explicitly require output in the target language only."""
    assert "Respond ONLY in" in SYSTEM_PROMPT


def test_no_other_script_rule():
    """Prompt must forbid Roman transliteration of native scripts."""
    assert "Roman transliteration" in SYSTEM_PROMPT
