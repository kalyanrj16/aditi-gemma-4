# UC1 model comparison — same inputs, three Gemma 4 variants

Inputs (identical for all three runs):
- Images: `UC1_prescription1A`, `UC1_prescription1B`, `UC1_medicalBill`, `UC1_tablets`
- Audio: `UC1_voicememo_us_english.wav`
- Single multimodal call, greedy decoding (runs are reproducible — browser run matched standalone byte-for-byte)

Ground truth for the headline check: the doctor prescribed **PENTANERVE**; the pharmacy dispensed **GABAPIN/Gabapentin**. Catching that substitution is the point of UC1.

## Timing & memory (from GenerationResult)

| Model | Peak mem | Prompt tokens | Gen tokens | Throughput | Gen time | Wall (extract) |
|---|---|---|---|---|---|---|
| E2B 4-bit | 5.17 GB | 1,645 | 536 | 113.7 tok/s | 4.7 s | 9.4 s |
| E4B 4-bit | 6.88 GB | 1,645 | 752 | 64.6 tok/s | 11.6 s | 16.3 s |
| 26B MoE 4-bit | 17.51 GB | 1,649 | 837 | 65.9 tok/s | 12.7 s | 38.0 s |

(Load time excluded — it's dominated by first-run weight download. After caching, load is 2–7 s.)

## What each model did on the substitution (headline)

| | E2B | E4B | 26B MoE |
|---|---|---|---|
| Read the prescribed drug? | No — reported "Gabapentin" for both prescribed and dispensed | Partly — "TENTANERV-NT" (OCR slip on PENTANERV), plus Vertyn/Glucomet/Myoor | Yes — "Pentanerv-NT", "Pentanerv", plus Vertim/Glucomet SR/Myo-D |
| Caught the substitution? | **No** — `"No substitution observations found."` | **Yes, coarse** — "dispensed Gabapentin does not match prescribed list" | **Yes, per-item** — Pentanerv→Gabapentin NT, Pentanerv→Gabapentin |
| Hospital | Correct — "UNIMED Healthcare Pvt. Ltd" (registered company name, top-right, matches the CIN on the letterhead) | Correct — "STAR HOSPITALS" (brand name, top-left) | Correct — "Star Hospitals" (brand name, top-left) |
| Complaints | Generic ("pain, headache, nerve pain") | Mixed vitals into complaints (BP/pulse/temp + headache/nausea) | Real handwriting ("bilateral gluteal pain radiating to legs", "intense burning") |
| Audio used? | Generic boilerplate | Generic ("discussing visit details") | `"not provided"` |

> Letterhead note: the page 1 letterhead carries **two** valid hospital identifiers — "STAR HOSPITALS" (brand) top-left and "UNIMED Healthcare Pvt. Ltd" (registered company, with CIN `U85110TG2006PTC051751`) top-right. All three models read a correct one; they just picked different halves of the same header. This is *not* a hallucination by E2B — an earlier draft of this file wrongly called it one.

## Read this as a tier ladder

- **E2B** collapses the two drugs into one and declares no substitution — it misses the entire UC1 case. (Its hospital field is correct, just the registered-company half of the letterhead.) Missing the substitution is the edge-tier failure the tiered architecture is meant to avoid.
- **E4B** recovers the prescribed drug names (with OCR errors) and flags the mismatch at a coarse level. Useful as a fast triage, not as the synthesis tier.
- **26B MoE** reads the actual prescription, separates the drugs, and pairs each prescribed item to its dispensed substitute. This is the v1 demo tier.

## Audio caveat (not yet investigated)

None of the three made meaningful use of the voice memo. 26B was the most honest about it (`"not provided"`); the smaller two emitted vague filler. This points at an audio-path issue to investigate separately, not a model-quality difference.

## Files

Per model: `UC1_<tag>_baseline.json` (parsed record + `_raw` + `_metrics`), `UC1_<tag>_screenshot.png` (full result card), `UC1_<tag>_card_scraped.txt` (raw JSON pulled from the card).
