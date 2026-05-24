## E2B
Update your mental model:
Failure mode (revised)          E2B behavior
#1 Audio overridden             ✓ Confirmed (generic boilerplate)
#3 OCR on Indian handwriting    ✓ Confirmed (missed PENTANERVE)
#4 Confabulation                ✗ Disconfirmed — UNIMED is real#5 Repetition✓ Confirmed (duplicated rows)
So E2B's actual failures are: weak audio modality + weak handwriting OCR + repetition under multi-image. NOT confabulation. That's a cleaner, more credible writeup observation.


## UI improvements to note for later
Since you said "some improvement to make", jot in LOG.md:

Anything that felt rough (font sizes, spacing, table rendering)
Anything missing (download summary button, model switching feedback, etc.)
Anything confusing

## CC Trail
Side task before we continue with UC3:

Generate a comprehensive log of every permission decision and tool 
action you've taken in this session so far. I want this as raw material 
for a future blog post about permission decisions in Claude Code.

Save it to: blog_notes/cc_permission_trail.md

Structure each entry like:
- Time (relative to session start, e.g. "00:15")
- Action category (file_read, file_write, bash_command, network_request, 
  system_modification, package_install, chmod, etc.)
- Actual command or operation
- Brief context (what task was I doing when this happened)
- Risk classification (low/moderate/high) from an enterprise perspective
- One-line note: would this be auto-approved, need review, or be 
  denied in a typical enterprise platform team's managed settings

Group by time. Be honest about what was risky vs routine. Don't 
sanitize — I want the real trail.

Also create the folder blog_notes/ since it doesn't exist yet.

Once saved, just confirm the file path and number of entries. Then 
return to the UC3 work.

## 2026-05-24 — Redacted set + full test matrix

Audio framing (corrected): audio support varies by Gemma 4 variant per Google's
docs — E2B/E4B have native audio; 26B (and 31B) are vision+text only. Earlier 26B
"not provided" on audio is this architectural limit, not a bug.

- Redaction integrated. `config.UC1_IMAGE_SET` now points at `data/prescriptions_redacted/`
  (originals kept in a comment). 1A + medical bill actually redacted (PII removed/
  substituted, name unified to "J Shanthi Devi"); 1B + tablets carry no PII, named
  `_redacted` for continuity. OCR-verified no real identifiers leak.
- `.gitignore`: originals stay ignored; `data/prescriptions_redacted/` whitelisted
  (committable). Verified via `git check-ignore`.
- App loads all 4 redacted paths; voice presets resolve.
- Matrix run 1/12 — **UC1A_noaudio_26b**: extraction quality preserved on redacted
  images (reads PENTANERV→GABAPIN, catches substitution; identifiers read as the fakes).
  Metrics: 898 tok, 65.4 tok/s, 13.7s, peak 17.49 GB. Full-card screenshot verified
  (1500×4729, privacy footer captured). Awaiting approval before the remaining 11.

- Approved. Full 12-run matrix complete (UC1A/UC1B/UC3A/UC3B × e2b/e4b/26b).
  Each cell: full JSON (record + _raw + _metrics + _inputs), full-card screenshot
  (heights 4517–4759 px, footer captured), scraped raw JSON. All screenshots verified full.
  Tooling note: running 2 inferences in one long-lived Streamlit server hung the 2nd
  (E4B UC1B). Fix = one fresh server per screenshot (cheap reload). Standalone JSON runs
  were unaffected.
  Findings (see model_comparison.md):
    * Audio support is architectural — E2B/E4B use the memo in all 3 languages incl. Telugu;
      26B is vision+text only and ignores audio in every run (audio still enters its prompt).
    * Honesty inversion: with no audio, 26B says "not provided"; E2B/E4B fabricate a concern.
    * Substitution (PENTANERVE→GABAPIN) caught by all models in all conditions; 26B most
      precise on drug names; E4B sometimes leaks an audio-named drug into the prescribed list.
  model_comparison.md rewritten as the clean public-facing 4-section comparison.