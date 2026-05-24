# UC1 model comparison — Gemma 4 variants × audio conditions

A 12-run matrix: 4 input conditions × 3 Gemma 4 variants, all on the **redacted** UC1
image set, single multimodal call, greedy decoding (runs reproduce; browser cards match
the standalone JSON).

## Test design

| Condition | Inputs | Audio modality |
|---|---|---|
| **UC1A** | 4 images + structured prompt | none |
| **UC1B** | 4 images + prompt + `UC1_voicememo_us_english.wav` | US English |
| **UC3A** | 4 images + prompt + `UC3a_voicememo_indianenglish.wav` | Indian English |
| **UC3B** | 4 images + prompt + `UC3b_voicememo_telugu.wav` | Telugu |

A note on "text": the model **always** receives the structured prompt from
`prompts.py` (input labels + output schema). UC1A is "no audio modality," not "no
text" — the user never types free-form text in v1.

## Architectural note (why audio behaves differently)

Per Google's Gemma 4 docs, audio support varies by variant: **E2B and E4B accept audio
natively; 26B (and 31B) are vision + text only.** In every audio run the audio is placed
in the prompt (prompt grows ~460–580 tokens), but only E2B/E4B act on it. 26B encodes the
audio and ignores it — so this is a capability boundary, not a bug.

## Timing & memory (stable per model)

| Model | Peak mem | Throughput | Gen time (no-audio → +audio) | Prompt tokens (no-audio / +audio) |
|---|---|---|---|---|
| E2B 4-bit | ~4.6–5.2 GB | ~114 tok/s | ~7 s → ~5 s | 1,634 / 2,095–2,210 |
| E4B 4-bit | ~6.2–6.9 GB | ~66 tok/s | ~12 s → ~7 s | 1,634 / 2,095–2,210 |
| 26B MoE 4-bit | ~16.9–17.5 GB | ~64 tok/s | ~14 s → ~12 s | 1,638 / 2,099–2,214 |

(Telugu memo is the longest audio → highest prompt-token counts.)

---

## UC1A — no audio (text + image only)

| | prescribed read | dispensed read | substitution | concern-from-audio |
|---|---|---|---|---|
| **E2B** | Pentanerv set, but **leaks GABAPENTIN into prescribed** (×2) | GABAPENTIN ×2 | ✓ caught (coarse) | **fabricated** — "pain and headache… some discomfort" |
| **E4B** | T.PENTANERV-NT, VERTIN, GLUCOMET SR, MYOTO (OCR drift) | GABAPENTIN 100MG | ✓ caught (coarse) | **fabricated** — "discussing symptoms like headache and pain" |
| **26B** | PENTANERV-NT, PENTANERV, VERTIM, GLUCOMET SR, MYOOP | GABAPIN ×2 + ZUVENTUS | ✓ caught (2 obs, per-item) | **"not provided"** (honest) |

The tell: with no audio, **26B honestly leaves the audio field empty; E2B and E4B invent a
patient concern.** 26B also reads the bill's actual brand (GABAPIN) and the fullest drug list.

## UC1B — + US English audio

| | prescribed read | dispensed | substitution | concern-from-audio |
|---|---|---|---|---|
| **E2B** | PENTENERV, VENTIN, GLUCOMET, MYOOP | GABAPIN | ✓ | ✓ **"pain in legs/feet has not decreased after two days"** |
| **E4B** | Pentaner, **"Vitamin B"** (hallucinated), Glucomet SR | Gabapin | ✓ | ✓ **"pain not reduced after two days… wants to know if the substitution is correct"** |
| **26B** | PENTANERV-NT, PENTANERV, VERTIM, GLUCOMET SR, MYOOP | GABAPIN ×2 | ✓ | **"not provided in text input"** (audio ignored) |

E2B/E4B now extract the spoken concern verbatim; 26B still blank. Note E4B's audio gain comes
with contamination — it slipped "Vitamin B" into the prescribed list.

## UC3A — + Indian English audio

| | prescribed read | dispensed | substitution | concern-from-audio |
|---|---|---|---|---|
| **E2B** | PENTENERUV-NT, VENTIN, GLUCOMET SR, MYOOP | GABAPENTIN | ✓ | ✓ "pain not decreased after two days… is the substitution correct" |
| **E4B** | Pantenerv, **Ghabapin** (audio drug leaked into prescribed) | Gabapin | ✓ | ✓ "substitution of Pantenerv with Gabapin might be incorrect…" |
| **26B** | PENTANERV-NT, PENTANERV, VERTIM, GLUCOMET SR, MYOOP | GABAPIN ×2 | ✓ | **"not provided"** |

Indian-accented English handled as well as US English by E2B/E4B. E4B again leaks an
audio-mentioned drug ("Ghabapin") into the prescribed list.

## UC3B — + Telugu audio

| | prescribed read | dispensed | substitution | concern-from-audio |
|---|---|---|---|---|
| **E2B** | PENTANER ×2, GLUCOMET, MYOOP | GABAPENTIN | ✓ | ✓ "PENTANER replaced by GABAPENTIN… having trouble taking it" (slight drift) |
| **E4B** | Pantenerv, Gabapin | Gabapin | ✓ | ✓ "substitution of Pantenerv with Gabapin… taking Gabapin two days, pain not subsided" |
| **26B** | PENTANERV-NT, PENTANERV, VERTIM, GLUCOMET SR, MYOOP | GABAPIN ×2 | ✓ | **"not provided in text input"** |

**Telugu audio works** on E2B/E4B — both recover the substitution concern from Telugu speech
(E4B notably clean). E2B drifts slightly ("having trouble taking it"). 26B blank as expected.

---

## Cross-cutting findings

1. **Audio support is architectural, not tunable.** E2B/E4B use the voice memo across all three
   languages (US English, Indian English, **Telugu**); 26B never does, in any language — it's
   vision+text only. The audio reaches 26B's prompt and is simply unused.
2. **Epistemic honesty inverts with size on the empty field.** With no audio (UC1A), 26B reports
   `"not provided"`; E2B and E4B **confabulate** a plausible concern. So the small models' audio
   wins come bundled with a tendency to fill the field even when the modality is absent.
3. **The UC1 substitution is caught by every model in every condition** (PENTANERVE → GABAPIN).
   26B is the most precise on names — it reads the bill's real brand (GABAPIN) and the full
   prescribed list. E2B/E4B have OCR drift on drug names, and E4B sometimes leaks an
   audio-mentioned drug into the *prescribed* list ("Vitamin B", "Ghabapin").

**Reading for the demo:** 26B is the reliable vision/text synthesis tier (no audio). For the
voice-memo use cases (UC1B/UC3A/UC3B), E4B is the sweet spot — native audio, ~6 GB, clean
concern extraction — with E2B as the fast edge fallback.

## Files / naming

Clean public-facing set: `UC1A_noaudio_*`, `UC1B_withaudio_us_*`, `UC3A_indianenglish_*`,
`UC3B_telugu_*` for each of `{e2b, e4b, 26b}` — `.json` (record + `_raw` + `_metrics` +
`_inputs`), `.png` (full result card), `_scraped.txt` (raw JSON from the card). Older
`UC1_*_baseline*.json` kept as private reference only.
