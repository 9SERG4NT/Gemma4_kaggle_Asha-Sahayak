# ASHA Sahayak — Kaggle Competition Writeup
## Deploying Gemma 4 E4B Offline for Rural Indian Healthcare

---

### The Problem Worth Solving

India has 1.07 million ASHA (Accredited Social Health Activists) workers — government-trained women who are the primary healthcare touchpoint for 600,000+ villages. Each ASHA worker serves roughly 1,000 people. They walk 5–10 km daily, carrying a basic kit, a mobile phone, and a health register.

When a child has a wound that won't stop bleeding, or a rash spreads overnight, or a snakebite happens at 2 AM — the ASHA worker is there. The nearest doctor may not be.

She faces a compounding set of obstacles:
- **No reliable 4G** in many villages. Cloud AI isn't an option.
- **No medical training** beyond a short course. She cannot diagnose.
- **No English.** She speaks Marathi or Hindi — not the language of most medical AI tools.
- **Patient privacy.** India's Digital Personal Data Protection (DPDP) Act means she legally cannot upload a patient's photo to a cloud service.

Existing AI solutions fail on at least two of these four dimensions. **Gemma 4 E4B fails on none.**

---

### Why Gemma 4 E4B is the Only Viable Architecture

The combination of properties required for this use case is unusual:

| Property | Required | Gemma 4 E4B |
|---|---|---|
| Runs offline (no internet) | Yes | Yes — via Ollama, 4B params, CPU-only |
| Understands photographs | Yes | Yes — native multimodal, no extra model |
| Marathi / Hindi output | Yes | Yes — 140+ languages, Devanagari native |
| Fits on basic hardware | Yes | Yes — ~4 GB RAM, quantized |
| Open weights, free to deploy | Yes | Yes — Apache 2.0 |

No other model in the current open-weight landscape satisfies all five simultaneously. GPT-4o and Claude require internet. Llama 3 is not multimodal. LLaVA is not multilingual at this quality level. Gemma 4 E4B was built specifically for the intersection of edge deployment and multilingual multimodal understanding.

---

### What We Built

**ASHA Sahayak** (आशा सहायक) is a complete, offline-capable triage assistant with three input modalities:

1. **Photo** — ASHA worker photographs the patient's condition using their phone camera.
2. **Voice** — She describes symptoms in Marathi or Hindi; `faster-whisper` (running locally) transcribes to Devanagari text.
3. **Text** — Optional typed symptom description, or auto-filled by the voice transcription.

Gemma 4 E4B (via Ollama) receives the image and symptom text and responds with a structured Marathi triage report, always in three sections:

```
काय दिसते आहे:
[What the model observes — 1–2 sentences, hedged]

तातडीची मदत:
[Numbered first-aid steps — max 4, no medications named]

डॉक्टरकडे जाणे आवश्यक आहे का?:
[Yes/No referral decision + one sentence of reasoning]
```

The entire pipeline — camera, STT, LLM — runs **without a network connection**. An airplane-mode test passes.

---

### Technical Architecture

```
ASHA Worker
    ├── Photo → Gradio UI
    ├── Voice → faster-whisper (local STT) → Devanagari text → Gradio UI
    └── Typed text → Gradio UI
                          │
                    model.py
                          │
              ┌───────────┴───────────┐
              │ USE_OLLAMA=true        │ USE_OLLAMA=false
              │ (local device)         │ (HF Spaces demo)
              ▼                       ▼
      Ollama /api/generate     HF Inference API
      gemma4:e4b (local)       gemma4:e4b (cloud)
              └───────────┬───────────┘
                          │
                  Marathi response
                  (three sections)
```

The `USE_OLLAMA` environment variable (default `true`) selects the runtime. Locally, everything is on-device. On Hugging Face Spaces, the HF Inference API fallback is used for the public demo — with a banner explaining the difference.

**Stack (locked per spec):** Python 3.11, Gradio 4.x, Ollama, faster-whisper (small model), Pillow, python-dotenv, huggingface-hub.

---

### Prompt Engineering: Getting Consistent Marathi Output

The core challenge was not the model — it was the prompt. Getting a multilingual model to produce consistently structured, safe, Marathi-only output across diverse medical images required several iterations.

**What failed:**
- `"Respond in Marathi"` alone caused English medical terms to bleed through ("wound", "infection").
- Open-ended formatting instructions produced inconsistent structure — sometimes bullets, sometimes prose.
- No safety framing caused specific medication names to appear (e.g., "apply Dettol").

**What worked:**

1. **Script-level constraint**: `"Respond ONLY in simple Marathi using Devanagari script. Never use English words or Roman letters."` — eliminates code-switching entirely.

2. **Exact headers in the prompt**: Including the literal Marathi section headers (`काय दिसते आहे:`, etc.) in the system prompt causes the model to reliably reproduce them. Describing the structure in English does not.

3. **Concrete hedge phrase**: `"Use phrases like 'हे ... असू शकते'"` — giving the model the exact Marathi uncertainty phrase eliminates definitive diagnoses.

4. **Binary referral options**: Providing both `"होय, लवकर PHC मध्ये घेऊन जा"` and `"नाही, घरी काळजी घेता येईल"` as the two literal options makes the triage decision crisp and machine-readable.

5. **Education level anchor**: `"Write as if speaking to someone with a 10th-grade education"` reduced jargon dramatically without needing to enumerate every medical term to avoid.

**Key insight:** For low-resource-language, safety-critical output, **show the model exactly what you want in the target language in the prompt** — don't describe it in English and hope for translation.

---

### Safety Design

This is a healthcare tool. Safety is non-negotiable:

- **Never diagnoses with certainty.** Every observation uses hedged language enforced at the prompt level.
- **Mandatory PHC referral triggers** are listed explicitly: heavy bleeding, deep wounds, signs of infection, difficulty breathing, unconsciousness, snakebite, burns larger than a palm, eye injuries.
- **No medication names** — the prompt bans specific drugs; only general hygiene advice is permitted.
- **No telemetry, no analytics, no PII logging** — patient photos are processed in memory only and never written to disk.
- **Honest about uncertainty** — if the image is unclear, the model says so in Marathi rather than guessing.

---

### Results

| Test | Result |
|---|---|
| Static prompt guardrail tests (6 checks) | 6/6 pass |
| Devanagari output (synthetic image) | Confirmed |
| Three-section structure (model test) | Confirmed |
| Offline (airplane mode) | Pass |
| Voice transcription (faster-whisper, Hindi/Marathi) | Functional |

---

### Real-World Impact Potential

With Gemma 4 E4B running offline on a ₹15,000 (~$180) Android tablet or refurbished laptop:
- A single ASHA worker's diagnostic support capability increases dramatically.
- No recurring cost — the model runs free after the one-time download.
- No privacy risk — zero patient data leaves the device.
- No connectivity dependency — works in the most remote villages.

Scaled to India's 1.07 million ASHA workers, this is a public health infrastructure upgrade that costs nothing per query and requires no internet backbone investment.

---

### What's Next

- **Android port** via Ollama's mobile runtime — the real target device.
- **Marathi-specific Whisper fine-tune** — the `small` model handles Marathi but a fine-tuned version would improve accuracy for dialectal speech.
- **Offline map integration** — auto-suggest the nearest PHC when referral is recommended.
- **NHM partnership** — deploy through India's National Health Mission ASHA training program.

---

*Word count: ~1,050*

*GitHub: https://github.com/YOUR_USERNAME/asha-sahayak*  
*HF Space: https://huggingface.co/spaces/YOUR_USERNAME/asha-sahayak*  
*Hackathon: Gemma 4 Good Hackathon, Kaggle, May 2026*
