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