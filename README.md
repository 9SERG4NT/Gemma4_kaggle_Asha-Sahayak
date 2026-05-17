---
title: ASHA Sahayak
emoji: 🏥
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: true
license: apache-2.0
short_description: AI triage assistant for rural Indian ASHA workers
---

<div align="center">

# 🏥 ASHA Sahayak — आशा सहायक

**Offline-first AI triage assistant for India's frontline community health workers**

[![HuggingFace Space](https://img.shields.io/badge/🤗%20HuggingFace-Space-FFD21E?style=for-the-badge)](https://huggingface.co/spaces/SERG4NT/asha-sahayak)
[![GitHub](https://img.shields.io/badge/GitHub-9SERG4NT%2FGemma4__kaggle__Asha--Sahayak-181717?style=for-the-badge&logo=github)](https://github.com/9SERG4NT/Gemma4_kaggle_Asha-Sahayak)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.44-FF7C00?style=for-the-badge&logo=gradio)](https://gradio.app)
[![Model](https://img.shields.io/badge/Gemma%204-E4B%20(4B)-4285F4?style=for-the-badge&logo=google)](https://huggingface.co/google/gemma-4-e4b-it)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)

*Built for the **Gemma 4 Good Hackathon** (Kaggle, May 2026)*

</div>

---

## The Problem

India has **~1 million ASHA** (Accredited Social Health Activists) workers — one per 1,000 villagers. They walk 5–10 km daily through villages where:

- 4G connectivity is absent or unreliable
- The nearest doctor is often 20–50 km away
- Workers are typically Class 10 educated, speak only their regional language
- Patients cannot always travel to Primary Health Centres (PHC)

**Uploading patient photos to cloud AI is not viable:**  
connectivity fails, and India's DPDP Act + health data norms make cloud processing legally and ethically risky.

---

## The Solution

**ASHA Sahayak** gives every ASHA worker a pocket doctor that runs entirely on their phone or a shared village tablet — no internet required.

A worker can:
1. 📸 **Photograph** a wound, rash, burn, or skin condition
2. 🎙️ **Describe symptoms by voice** in any of 117 languages (auto-transcribed to text)
3. 📋 **Receive structured triage guidance** in their own language:
   - What the condition likely is
   - Basic first aid they can provide right now
   - Whether urgent PHC referral is needed

---

## Live Demo

> **Try it on HuggingFace Spaces** (uses HF Inference API, no Ollama needed):  
> 👉 https://huggingface.co/spaces/SERG4NT/asha-sahayak

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ASHA Sahayak App                           │
│                       (Gradio 4.44)                             │
└─────────────┬────────────────────────────┬──────────────────────┘
              │                            │
   ┌──────────▼──────────┐     ┌──────────▼──────────┐
   │  Voice Input (mic)   │     │  Image Upload       │
   │  faster-whisper STT  │     │  (PIL → JPEG B64)   │
   │  99+ language codes  │     │  resize ≤ 1024 px   │
   └──────────┬──────────┘     └──────────┬──────────┘
              │                            │
              └─────────────┬──────────────┘
                            │
              ┌─────────────▼──────────────┐
              │     Language-aware         │
              │     System Prompt          │
              │  (build_system_prompt())   │
              └─────────────┬──────────────┘
                            │
                   USE_OLLAMA env var
                    /              \
      ┌────────────▼───┐    ┌──────▼─────────────────┐
      │  LOCAL (true)  │    │   HF SPACES (false)     │
      │  Ollama Server │    │   HF Inference API      │
      │  gemma4:e4b    │    │   google/gemma-4-e4b-it │
      │  HTTP stream   │    │   REST / chat/completions│
      └────────────┬───┘    └──────┬─────────────────┘
                   └────────┬──────┘
                            │
              ┌─────────────▼──────────────┐
              │    Structured Response      │
              │  • What I observe          │
              │  • Immediate first aid     │
              │  • Urgent referral needed? │
              └────────────────────────────┘
```

### Why this architecture?

| Design Choice | Reason |
|---|---|
| `USE_OLLAMA` toggle | One codebase, two environments: offline village deployment (Ollama) and the public HF Spaces demo (API) |
| Ollama via raw HTTP | Enables token streaming — the UI updates word-by-word rather than waiting for the full response |
| Base64 image in API payload | HF Inference API `/v1/chat/completions` accepts `data:image/jpeg;base64,...` URLs — no separate vision endpoint needed |
| System prompt per request | Language is injected at runtime so one model serves 117 languages without fine-tuning |
| `faster-whisper` local STT | Voice audio never leaves the device — full offline transcription |

---

## Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **UI** | Gradio 4.44 | Web interface, image upload, audio recording, streaming output |
| **Vision-Language Model** | Google Gemma 4 E4B (4B params) | Core multimodal triage analysis — photo + text in one pass |
| **Local Inference** | Ollama | Serves Gemma 4 locally; token-streaming via HTTP NDJSON |
| **Cloud Inference** | HF Inference API | Serverless fallback for HF Spaces (`/v1/chat/completions`) |
| **Speech-to-Text** | faster-whisper (small) | Offline multilingual voice transcription, 99+ language codes |
| **Image Processing** | Pillow (PIL) | Resize to ≤1024 px, encode as JPEG base64 |
| **Configuration** | python-dotenv | Environment-variable driven — no hardcoded credentials |
| **Testing** | pytest | Static guardrail tests + live model smoke tests |
| **Hosting** | HuggingFace Spaces (demo) / Ollama (production) | Dual deployment targets |

---

## How It Was Built

### Phase 1 — Core Inference Pipeline
Started with the simplest working path: image → Gemma 4 via Ollama → response. Verified the model could describe wounds in Marathi before building any UI. Key discovery: Gemma 4 E4B is genuinely multilingual — same model weights, different system prompt language, and the output language changes cleanly.

### Phase 2 — Safety Guardrails
The system prompt is the most critical component. Iterated on `prompts.py` to enforce:
- Structured 3-section output (observation → first aid → referral decision)
- Hedged language — never diagnoses with certainty
- Hard trigger list: heavy bleeding, snake/animal bite, burns >palm-size, signs of infection, difficulty breathing → always refer urgently
- No specific drug names ever
- Output ONLY in the chosen language — no transliteration, no English fallback

All guardrails are covered by automated static tests in `test_prompts.py` that run in under 1 second without any model.

### Phase 3 — Language Expansion
Expanded from 3 languages to **117 languages** across 9 regional groups. Cross-referenced all voice codes against the faster-whisper supported language list and caught 4 invalid codes (`ln`, `ff`, `qu`, `ay`) that would crash transcription at runtime. Fixed the `parse_choice()` parser to correctly handle parenthetical language names like "Chinese (Simplified)" using `rfind(" (")` instead of `split(" (")[0]`.

### Phase 4 — UI Design
Replaced the default Gradio theme with a fully custom animated CSS design featuring an animated gradient header, floating bubble decorations, glassmorphism-inspired cards, and a pulsing status indicator. Critical fix: removed `backdrop-filter: blur()` from all card elements because it creates a new CSS stacking context in Chromium that traps z-index and prevents the dropdown popup from rendering above sibling elements. The dropdown popup is anchored with `position: relative` on `.wrap` + `position: absolute; top: calc(100% + 4px)` on the popup list.

### Phase 5 — Dual Deployment
Built a single `run_inference()` entry point that returns a streaming generator (Ollama) or a string (HF API) based on the `USE_OLLAMA` environment variable — no code changes between local and cloud deployment.

---

## Project Structure

```
asha-sahayak/
├── app.py              # Gradio UI — animated CSS, streaming output, 117 languages
├── model.py            # Gemma 4 client: Ollama streaming + HF Inference API fallback
├── prompts.py          # System prompt builder (language-injected, safety-enforced)
├── audio.py            # faster-whisper STT, mic recording, language code lookup
├── config.py           # All settings via environment variables
├── languages.py        # 117-language registry: name, native script, Whisper code, region
├── utils.py            # Image resize, Devanagari script detection
├── requirements.txt    # Pinned Python dependencies
├── packages.txt        # System packages for HF Spaces (ffmpeg for audio)
├── demo/
│   └── sample_images/  # Test images for the demo
├── notebook/
│   └── asha_sahayak.ipynb  # Kaggle walkthrough notebook
└── tests/
    ├── test_prompts.py # Static guardrail tests — no model needed, fast CI
    └── test_model.py   # Smoke tests — require Ollama running with gemma4:e4b
```

---

## Setup — Local Offline Mode

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/download) installed

### 1. Pull the model

```bash
ollama pull gemma4:e4b    # ~4 GB download, one-time
ollama serve              # keep this running
```

### 2. Install dependencies

```bash
git clone https://github.com/9SERG4NT/Gemma4_kaggle_Asha-Sahayak.git
cd Gemma4_kaggle_Asha-Sahayak
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
# Open http://localhost:7860
```

---

## Running Tests

```bash
# Static guardrail tests — no model needed, completes in ~1 second
python -m pytest tests/test_prompts.py -v

# Full smoke tests — requires Ollama running with gemma4:e4b
python -m pytest tests/ -v
```

---

## Deploying to Hugging Face Spaces

```bash
git remote add space https://huggingface.co/spaces/SERG4NT/asha-sahayak
git push space main
```

In the Space **Settings → Variables**, add:

| Variable | Value |
|---|---|
| `USE_OLLAMA` | `false` |
| `HF_TOKEN` | your HF token with Inference API access |

> The HF Space uses `google/gemma-4-e4b-it` via the HF Inference API.  
> The production village deployment uses Ollama fully offline — zero cloud dependency.

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `USE_OLLAMA` | `true` | `true` = local Ollama; `false` = HF Inference API |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma4:e4b` | Model tag in Ollama |
| `HF_TOKEN` | — | Required when `USE_OLLAMA=false` |
| `HF_MODEL_ID` | `google/gemma-4-e4b-it` | HF model ID for cloud inference |
| `WHISPER_MODEL_SIZE` | `small` | faster-whisper model size (`tiny`/`small`/`medium`) |
| `GRADIO_SERVER_PORT` | `7860` | Local server port |
| `GRADIO_SHARE` | `false` | `true` to generate a public Gradio share link |

---

## Why Gemma 4 E4B?

| Requirement | How Gemma 4 E4B delivers |
|---|---|
| **No internet** | Runs fully offline via Ollama on any consumer CPU |
| **Multilingual** | 140+ languages natively including all Indian scripts |
| **Multimodal** | Understands photographs + text in a single forward pass |
| **Edge-ready** | 4B parameters — runs on CPU, no GPU required |
| **Privacy** | All inference local — patient photos never leave the device |
| **Open weights** | Apache 2.0 — deployable without per-query API costs |

---

## Language Coverage

117 languages across 9 regional groups:

| Region | Count | Examples |
|---|---|---|
| South Asian | 19 | Marathi, Hindi, Bengali, Tamil, Telugu, Kannada, Gujarati, Malayalam, Punjabi, Urdu... |
| European Major | 35 | English, French, Spanish, German, Russian, Turkish, Georgian, Armenian... |
| Southeast Asian | 11 | Thai, Vietnamese, Indonesian, Filipino, Malay, Burmese, Khmer... |
| East Asian | 6 | Chinese (Simplified), Chinese (Traditional), Japanese, Korean, Mongolian, Tibetan |
| Middle East & Central Asia | 12 | Arabic, Hebrew, Persian (Farsi), Pashto, Uzbek, Kazakh, Azerbaijani... |
| African | 17 | Swahili, Amharic, Hausa, Yoruba, Zulu, Xhosa, Somali, Wolof... |
| European Regional | 9 | Welsh, Catalan, Basque, Irish, Galician, Occitan, Breton... |
| Indigenous Americas | 5 | Quechua, Guaraní, Nahuatl, Haitian Creole, Aymara |
| Pacific | 3 | Māori, Hawaiian, Malagasy |

Voice transcription: 95 languages have explicit Whisper codes; 22 fall back to auto-detection.

---

## Safety & Ethics

- **Never diagnoses with certainty** — always uses hedged language ("this may be...", "this appears to be...")
- **Urgent referral triggers** enforced in every response: heavy bleeding, snake/animal bite, burns larger than palm-size, signs of infection, difficulty breathing, unconsciousness
- **No medication names** — never suggests specific drugs or dosages by name
- **No telemetry or analytics** — zero PII logging
- **Images processed in-memory only** — never written to disk or transmitted (in local mode)
- **Framed as a triage aid, not a doctor** — explicit disclaimer built into the system prompt

---

## Hackathon

Built for the **Gemma 4 Good Hackathon** (Kaggle, May 2026).  
Tracks targeted:
- Main Track
- Health & Sciences ($10,000)
- Digital Equity ($10,000)
- Ollama Special Tech ($10,000)

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.  
Gemma 4 model weights are subject to [Google's Gemma Terms of Use](https://ai.google.dev/gemma/terms).
