import logging

# gradio-client 1.3.x (ships with Gradio 4.44) has a bug on Python 3.13:
# get_type() does `"const" in schema` without checking if schema is a dict,
# which raises TypeError when schema is a bool (e.g. "additionalProperties": false).
# Patch the function before importing Gradio so the fix is in place when the
# API schema is built at server startup.
try:
    import gradio_client.utils as _gc_utils
    _orig_get_type = _gc_utils.get_type
    def _safe_get_type(schema):
        if not isinstance(schema, dict):
            return "any"
        return _orig_get_type(schema)
    _gc_utils.get_type = _safe_get_type
except Exception:
    pass

import gradio as gr
import requests

from audio import transcribe
from config import GRADIO_SERVER_PORT, GRADIO_SHARE, OLLAMA_BASE_URL, OLLAMA_MODEL, USE_OLLAMA
from languages import get_dropdown_choices, get_whisper_code, get_native_name, parse_choice
from model import run_inference

logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _ollama_status() -> tuple[bool, str]:
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        models = [m["name"] for m in r.json().get("models", [])]
        model_ready = any(OLLAMA_MODEL in m for m in models)
        return True, ("ready" if model_ready else "connected — model not pulled")
    except Exception:
        return False, "not reachable"


# ── Animated CSS ───────────────────────────────────────────────────────────────

CUSTOM_CSS = """
/* ─── Keyframe Animations ────────────────────────────────────────────────── */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes statusPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.55);
  }
  50% {
    transform: scale(1.25);
    box-shadow: 0 0 0 7px rgba(74, 222, 128, 0);
  }
}
@keyframes shimmer {
  0%   { transform: translateX(-100%) rotate(25deg); }
  100% { transform: translateX(350%) rotate(25deg); }
}
@keyframes floatA {
  0%, 100% { transform: translate(0, 0) rotate(0deg);   opacity: 0.07; }
  33%       { transform: translate(-12px, -20px) rotate(4deg);  opacity: 0.12; }
  66%       { transform: translate(8px, -10px) rotate(-3deg); opacity: 0.08; }
}
@keyframes floatB {
  0%, 100% { transform: translate(0, 0) rotate(0deg);   opacity: 0.05; }
  40%       { transform: translate(14px, -16px) rotate(-5deg); opacity: 0.09; }
  70%       { transform: translate(-6px, -8px) rotate(3deg);  opacity: 0.06; }
}
@keyframes cardEntrance {
  from { opacity: 0; transform: translateY(18px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}
@keyframes borderGlow {
  0%, 100% { border-color: rgba(19, 165, 152, 0.22); }
  50%       { border-color: rgba(19, 165, 152, 0.60); }
}
@keyframes outputAppear {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* ─── Variables ──────────────────────────────────────────────────────────── */
:root {
    --primary:       #0B7A6E;
    --primary-light: #13A598;
    --primary-dark:  #064E45;
    --accent-bg:     #F0FAF9;
    --glass-bg:      rgba(255, 255, 255, 0.88);
    --glass-border:  rgba(19, 165, 152, 0.25);
    --text:          #111827;
    --text-muted:    #6B7280;
    --radius:        14px;
    --shadow-sm:     0 2px 8px rgba(11, 122, 110, 0.08);
    --shadow-md:     0 4px 24px rgba(11, 122, 110, 0.13);
    --shadow-lg:     0 10px 44px rgba(11, 122, 110, 0.22);
}

/* ─── Base ───────────────────────────────────────────────────────────────── */
body, .gradio-container {
    background: linear-gradient(135deg, #E9F7F5 0%, #F4FAFA 55%, #EEF9F4 100%) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    animation: fadeInUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

/* ─── Animated Header ────────────────────────────────────────────────────── */
#app-header {
    background: linear-gradient(135deg, #064E45, #0B7A6E, #13A598, #1BBFAC, #0B7A6E, #064E45);
    background-size: 400% 400%;
    animation: gradientShift 10s ease infinite;
    border-radius: var(--radius);
    padding: 28px 32px 22px;
    margin-bottom: 18px;
    box-shadow: 0 8px 40px rgba(6, 78, 69, 0.40), inset 0 1px 0 rgba(255,255,255,0.12);
    position: relative;
    overflow: hidden;
}
#app-header .bubble-a {
    position: absolute; top: -55px; right: -55px;
    width: 240px; height: 240px;
    background: rgba(255,255,255,0.09);
    border-radius: 50%;
    animation: floatA 7s ease-in-out infinite;
}
#app-header .bubble-b {
    position: absolute; bottom: -80px; left: 22%;
    width: 320px; height: 320px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
    animation: floatB 11s ease-in-out infinite;
}
#app-header .bubble-c {
    position: absolute; top: 10px; left: -40px;
    width: 140px; height: 140px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
    animation: floatA 9s ease-in-out infinite reverse;
}

/* ─── Status bar ─────────────────────────────────────────────────────────── */
#status-bar {
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.24);
    border-radius: 10px;
    padding: 9px 18px;
    margin-top: 14px;
    display: flex; gap: 20px; align-items: center;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    position: relative; z-index: 1;
}
.dot-online {
    display: inline-block;
    width: 9px; height: 9px; border-radius: 50%;
    background: #4ADE80;
    animation: statusPulse 2.2s ease-in-out infinite;
    vertical-align: middle; margin-right: 4px;
}
.dot-offline {
    display: inline-block;
    width: 9px; height: 9px; border-radius: 50%;
    background: #F87171;
    vertical-align: middle; margin-right: 4px;
}

/* ─── Language panel ─────────────────────────────────────────────────────── */
/* z-index: 200 > z-index: 1 on the cards below → lang-panel stacking context
   always paints on top, so the popup inside it appears above the cards. */
#lang-panel {
    position: relative;
    z-index: 200;
    overflow: visible !important;
    background: #FFFFFF;
    border: 1.5px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 18px 22px 20px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-md);
}

/* All ancestors of the popup inside the panel must not clip it */
#lang-panel,
#lang-panel > *,
.lang-dropdown,
.lang-dropdown > *,
.lang-dropdown .wrap {
    overflow: visible !important;
}

/* Anchor the popup to .wrap (the immediate parent that contains the input).
   position: absolute, not fixed — fixed loses width and breaks on scroll. */
.lang-dropdown .wrap {
    position: relative !important;
}
.lang-dropdown .options,
.lang-dropdown ul[role="listbox"],
.lang-dropdown ul {
    position: absolute !important;
    top: calc(100% + 4px) !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    min-width: 0 !important;
    z-index: 9999 !important;
    max-height: 320px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    background: #FFFFFF !important;
    border: 1.5px solid rgba(19, 165, 152, 0.4) !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 36px rgba(11, 122, 110, 0.22) !important;
    padding: 4px 0 !important;
    margin: 0 !important;
}
.lang-dropdown .options li,
.lang-dropdown ul[role="listbox"] li,
.lang-dropdown ul li {
    padding: 9px 16px !important;
    cursor: pointer !important;
    font-size: 0.93rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: background 0.12s ease !important;
}
.lang-dropdown .options li:hover,
.lang-dropdown ul[role="listbox"] li:hover,
.lang-dropdown ul li:hover {
    background: var(--accent-bg) !important;
    color: var(--primary-dark) !important;
}
.lang-dropdown .options li.selected,
.lang-dropdown ul li[aria-selected="true"] {
    color: var(--primary) !important;
    font-weight: 600 !important;
}

/* ─── Input / Output cards ───────────────────────────────────────────────── */
/* NOTE: NO backdrop-filter here — it creates a stacking context that traps
   z-index and prevents the dropdown popup from rendering on top.  Use a
   solid opaque background instead for the same frosted-glass look. */
.input-card, .output-card {
    background: rgba(255, 255, 255, 0.96) !important;
    border: 1.5px solid var(--glass-border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 18px !important;
    position: relative;
    z-index: 1;
    transition: box-shadow 0.3s ease, transform 0.3s ease, border-color 0.3s ease !important;
    animation: cardEntrance 0.65s cubic-bezier(0.22,1,0.36,1) both;
}
.input-card { margin-bottom: 12px; }
.input-card:hover, .output-card:hover {
    box-shadow: var(--shadow-lg) !important;
    transform: translateY(-3px) !important;
    border-color: rgba(19, 165, 152, 0.52) !important;
}

/* staggered card entrance */
.input-card:nth-child(1) { animation-delay: 0.15s; }
.input-card:nth-child(2) { animation-delay: 0.26s; }
.input-card:nth-child(3) { animation-delay: 0.37s; }
.output-card             { animation-delay: 0.20s; }

/* ─── Analyze button ─────────────────────────────────────────────────────── */
#analyze-btn {
    background: linear-gradient(135deg, #085F55, #0B7A6E 50%, #13A598) !important;
    background-size: 200% 200% !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 1.07rem !important;
    font-weight: 700 !important;
    padding: 15px 28px !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.22,1,0.36,1) !important;
    box-shadow: 0 4px 18px rgba(11, 122, 110, 0.40) !important;
    width: 100% !important;
    letter-spacing: 0.4px !important;
    position: relative !important;
    overflow: hidden !important;
}
#analyze-btn::after {
    content: "";
    position: absolute;
    top: -60%; left: -80%;
    width: 55%; height: 220%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.28), transparent);
    transform: rotate(25deg);
}
#analyze-btn:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 32px rgba(11, 122, 110, 0.55) !important;
    background-position: right center !important;
}
#analyze-btn:hover::after {
    animation: shimmer 0.75s ease forwards;
}
#analyze-btn:active {
    transform: translateY(0) scale(0.97) !important;
    box-shadow: 0 3px 10px rgba(11, 122, 110, 0.30) !important;
}

/* ─── Transcribe button ──────────────────────────────────────────────────── */
#transcribe-btn {
    background: rgba(255, 255, 255, 0.92) !important;
    color: var(--primary) !important;
    border: 1.5px solid rgba(11, 122, 110, 0.32) !important;
    border-radius: 9px !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 9px 16px !important;
    cursor: pointer !important;
    transition: all 0.22s ease !important;
}
#transcribe-btn:hover {
    background: var(--accent-bg) !important;
    border-color: var(--primary) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(11,122,110,0.18) !important;
}

/* ─── Output textbox ─────────────────────────────────────────────────────── */
#output-box textarea {
    font-family: 'Noto Sans', 'Segoe UI', sans-serif !important;
    font-size: 1rem !important;
    line-height: 1.85 !important;
    color: var(--text) !important;
    background: linear-gradient(160deg, #F0FAF9 0%, #F8FFFE 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 18px !important;
    transition: background 0.4s ease !important;
    animation: outputAppear 0.4s ease;
}

/* ─── Dropdown ───────────────────────────────────────────────────────────── */
.lang-dropdown label span {
    font-weight: 700 !important;
    color: var(--primary-dark) !important;
    font-size: 0.95rem !important;
}

/* ─── Section labels ─────────────────────────────────────────────────────── */
.section-label {
    font-size: 0.77rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    color: var(--primary-dark);
    margin-bottom: 8px;
    opacity: 0.9;
}

/* ─── Examples ───────────────────────────────────────────────────────────── */
.gr-examples {
    background: var(--glass-bg) !important;
    border: 1.5px solid var(--glass-border) !important;
    border-radius: var(--radius) !important;
    padding: 16px !important;
    margin-top: 12px !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}

/* ─── Disclaimer ─────────────────────────────────────────────────────────── */
#disclaimer {
    background: linear-gradient(135deg, #FFFCEB, #FFF9EC);
    border: 1px solid #FDE68A;
    border-radius: 10px;
    padding: 12px 18px;
    margin-top: 16px;
    font-size: 0.82rem;
    color: #92400E;
    box-shadow: 0 2px 10px rgba(217, 119, 6, 0.12);
}

/* ─── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    #app-header { padding: 20px 16px 16px; }
    #status-bar { flex-wrap: wrap; gap: 10px; }
}
"""


# ── Header HTML ────────────────────────────────────────────────────────────────

def _make_header(ollama_ok: bool, ollama_msg: str) -> str:
    dot_class = "dot-online" if ollama_ok else "dot-offline"
    mode_label = "Offline · Ollama" if USE_OLLAMA else "Cloud · HF Inference API"
    return f"""
<div id="app-header">
  <div class="bubble-a"></div>
  <div class="bubble-b"></div>
  <div class="bubble-c"></div>
  <div style="display:flex;align-items:center;gap:16px;position:relative;z-index:1;">
    <div style="font-size:2.8rem;line-height:1;filter:drop-shadow(0 3px 10px rgba(0,0,0,0.35));">🏥</div>
    <div>
      <div style="color:#fff;font-size:1.7rem;font-weight:800;letter-spacing:-0.5px;text-shadow:0 2px 14px rgba(0,0,0,0.25);">
        ASHA Sahayak
        <span style="font-size:1rem;font-weight:400;opacity:0.75;margin-left:8px;">· आशा सहायक</span>
      </div>
      <div style="color:rgba(255,255,255,0.85);font-size:0.93rem;margin-top:4px;text-shadow:0 1px 5px rgba(0,0,0,0.18);">
        AI Health Triage Assistant &nbsp;·&nbsp; 55 Languages &nbsp;·&nbsp; Offline-First
      </div>
    </div>
  </div>
  <div id="status-bar">
    <span style="color:rgba(255,255,255,0.92);font-size:0.82rem;font-weight:600;">
      <span class="{dot_class}"></span>Ollama: <strong>{ollama_msg}</strong>
    </span>
    <span style="color:rgba(255,255,255,0.35);">|</span>
    <span style="color:rgba(255,255,255,0.92);font-size:0.82rem;">
      🤖&nbsp;Model: <strong>{OLLAMA_MODEL if USE_OLLAMA else "HF Inference API"}</strong>
    </span>
    <span style="color:rgba(255,255,255,0.35);">|</span>
    <span style="color:rgba(255,255,255,0.92);font-size:0.82rem;">
      {'📶' if not USE_OLLAMA else '✈️'}&nbsp;Mode: <strong>{mode_label}</strong>
    </span>
  </div>
</div>
"""


# ── Callbacks ──────────────────────────────────────────────────────────────────

def transcribe_audio(audio_path, lang_choice):
    if not audio_path:
        return ""
    lang_name = parse_choice(lang_choice) if lang_choice else "English"
    whisper_code = get_whisper_code(lang_name)
    text = transcribe(audio_path, language_code=whisper_code)
    if not text:
        return "⚠ Audio not understood — please try again or type symptoms below."
    return text


def analyze(image, symptom_text, lang_choice):
    """Generator — yields accumulated text so Gradio streams it live."""
    if image is None:
        yield "⚠ Please upload a patient photo first."
        return

    lang_name = parse_choice(lang_choice) if lang_choice else "English"

    try:
        result = run_inference(image, symptom_text or "", lang_name)
        if isinstance(result, str):
            yield result or "⚠ Empty response. Please try again."
        else:
            yield from result
    except RuntimeError as exc:
        logger.error("Inference error: %s", exc)
        yield f"⚠ Error: {exc}"
    except Exception as exc:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        yield "⚠ Unexpected error. Please try again."


def update_placeholder(lang_choice):
    lang_name = parse_choice(lang_choice) if lang_choice else "English"
    native = get_native_name(lang_name)
    return gr.update(
        placeholder=f"Describe symptoms in {lang_name} ({native}) or any language…"
    )


# ── Build UI ───────────────────────────────────────────────────────────────────

DROPDOWN_CHOICES = get_dropdown_choices()
# Pick the Marathi entry from the actual list so the string matches exactly
DEFAULT_LANG = next((c for c in DROPDOWN_CHOICES if c.startswith("English")), DROPDOWN_CHOICES[0])

ollama_ok, ollama_msg = _ollama_status()

with gr.Blocks(
    title="ASHA Sahayak — AI Health Triage",
    theme=gr.themes.Soft(
        primary_hue="teal",
        secondary_hue="cyan",
        neutral_hue="slate",
        font=["Inter", "ui-sans-serif", "system-ui"],
    ),
    css=CUSTOM_CSS,
) as demo:

    # ── Header ──
    gr.HTML(_make_header(ollama_ok, ollama_msg))

    # ── Language selector ──
    with gr.Column(elem_id="lang-panel"):
        gr.HTML(f'<div class="section-label">🌍 Output Language — Select any of {len(DROPDOWN_CHOICES)} languages</div>')
        lang_dropdown = gr.Dropdown(
            choices=DROPDOWN_CHOICES,
            value=DEFAULT_LANG,
            label="",
            show_label=False,
            filterable=True,
            elem_classes=["lang-dropdown"],
        )

    # ── Main columns ──
    with gr.Row(equal_height=False):

        # LEFT: Inputs
        with gr.Column(scale=5, min_width=320):
            with gr.Group(elem_classes=["input-card"]):
                gr.HTML('<div class="section-label">📷 Patient Photo</div>')
                image_input = gr.Image(
                    label="",
                    show_label=False,
                    type="pil",
                    sources=["upload", "webcam"],
                    height=260,
                )

            with gr.Group(elem_classes=["input-card"]):
                gr.HTML('<div class="section-label">🎙 Voice Symptoms (optional)</div>')
                audio_input = gr.Audio(
                    label="",
                    show_label=False,
                    sources=["microphone"],
                    type="filepath",
                )
                transcribe_btn = gr.Button(
                    "🎤 Transcribe Voice → Text",
                    elem_id="transcribe-btn",
                    size="sm",
                )

            with gr.Group(elem_classes=["input-card"]):
                gr.HTML('<div class="section-label">✍ Symptom Description (optional)</div>')
                symptom_input = gr.Textbox(
                    label="",
                    show_label=False,
                    placeholder="Describe symptoms in the selected language or any language…",
                    lines=3,
                )

            analyze_btn = gr.Button(
                "🔍  Analyze Patient Condition",
                elem_id="analyze-btn",
                variant="primary",
            )

        # RIGHT: Output
        with gr.Column(scale=6, min_width=360):
            with gr.Group(elem_classes=["output-card"]):
                gr.HTML('<div class="section-label">📋 Triage Report</div>')
                output_box = gr.Textbox(
                    label="",
                    show_label=False,
                    lines=22,
                    max_lines=30,
                    interactive=False,
                    elem_id="output-box",
                    placeholder=(
                        "Upload a photo and click Analyze.\n\n"
                        "The report will appear here in the selected language —\n"
                        "three sections:\n"
                        "  • What I observe\n"
                        "  • Immediate first aid\n"
                        "  • Is urgent referral needed?"
                    ),
                )

    # ── Examples ──
    gr.Examples(
        examples=[
            ["demo/sample_images/laceration_wound.jpg",
             "Patient has a deep cut on the arm, bleeding continues.",
             "Marathi (मराठी)"],
            ["demo/sample_images/skin_rash.jpg",
             "Rash on skin for 3 days, itching and redness.",
             "Hindi (हिन्दी)"],
            ["demo/sample_images/burn.jpg",
             "Hot water burn on hand, blisters forming.",
             "Swahili (Kiswahili)"],
            ["demo/sample_images/cellulitis_infection.jpg",
             "Leg is swollen, red, warm and painful since yesterday.",
             "Arabic (العربية)"],
            ["demo/sample_images/skin_rash.jpg",
             "Eruption cutanée depuis 2 jours.",
             "Tamil (தமிழ்)"],
            ["demo/sample_images/laceration_wound.jpg",
             "손에 깊은 상처가 났습니다.",
             "Bengali (বাংলা)"],
        ],
        inputs=[image_input, symptom_input, lang_dropdown],
        label="📸 Real Examples — click any row to load (images: Wikimedia Commons, CC BY-SA)",
    )

    # ── Disclaimer ──
    gr.HTML("""
    <div id="disclaimer">
      ⚕️ <strong>Medical disclaimer:</strong> ASHA Sahayak is a <em>triage aid only</em>, not a substitute
      for professional medical diagnosis. Always refer serious or uncertain cases to a trained healthcare
      provider or nearby health centre. No patient data leaves the device when running locally via Ollama.
    </div>
    """)

    # ── Wire events ──
    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[audio_input, lang_dropdown],
        outputs=[symptom_input],
    )

    analyze_btn.click(
        fn=analyze,
        inputs=[image_input, symptom_input, lang_dropdown],
        outputs=[output_box],
    )

    lang_dropdown.change(
        fn=update_placeholder,
        inputs=[lang_dropdown],
        outputs=[symptom_input],
    )


# ── Launch ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=GRADIO_SERVER_PORT,
        share=GRADIO_SHARE,
        show_error=True,
        show_api=False,
    )
