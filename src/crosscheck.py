# src/crosscheck.py
# Cross-check the (handwritten) prescribed medication names against the (printed)
# pharmacy bill. The bill is clean OCR; the prescription is hard handwriting, so a
# close match on the bill is a confidence signal. We FLAG, we never correct — the
# model's reading is left intact and the human confirms with the pharmacist.

import re
from difflib import SequenceMatcher

# dosage-form / unit noise to strip before comparing names
_NOISE = re.compile(r"\b(tab|tablet|tablets|cap|capsule|caps|ip|usp|bp|mg|mcg|ml|sr|xr|er|gm|g)\b", re.I)


def _norm(name: str) -> str:
    s = (name or "").upper()
    s = re.sub(r"[^A-Z0-9 ]", " ", s)   # punctuation/hyphens -> space
    s = _NOISE.sub(" ", s)              # drop dosage-form / unit words
    s = re.sub(r"\d+", " ", s)          # drop numbers (strengths/doses)
    return re.sub(r"\s+", " ", s).strip()


def _similarity(a: str, b: str) -> float:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return 0.0
    if na in nb or nb in na:
        return 1.0
    return SequenceMatcher(None, na.replace(" ", ""), nb.replace(" ", "")).ratio()


def _name(item) -> str:
    if isinstance(item, dict):
        return item.get("medication") or ""
    return str(item or "")


def crosscheck_prescribed_against_bill(record: dict, threshold: float = 0.6) -> list[dict]:
    """For each prescribed medication, find the closest name on the pharmacy bill.

    Returns [{prescribed, status, bill_name, note}]. status is one of:
      'confirmed'      — present on the bill, spelling matches
      'likely_misread' — present on the bill but spelling differs (surface bill's text)
      'unverified'     — no close match on the bill (can't cross-check here)
    Flag only; never rewrites the model's reading.
    """
    prescribed = record.get("medications_prescribed") or []
    bill_names = [n for n in (_name(d) for d in (record.get("medications_dispensed") or [])) if n]
    if not bill_names:
        return []  # no bill to check against

    results = []
    for p in prescribed:
        pname = _name(p)
        if not pname:
            continue
        best_name, best_sim = None, 0.0
        for bn in bill_names:
            sim = _similarity(pname, bn)
            if sim > best_sim:
                best_name, best_sim = bn, sim

        if best_sim >= threshold and _norm(pname) == _norm(best_name):
            status, note = "confirmed", "Confirmed on the pharmacy bill."
        elif best_sim >= threshold:
            status = "likely_misread"
            note = (
                f"The bill prints “{best_name}” — the handwriting was likely read imperfectly "
                f"here. Confirm the exact name with your pharmacist."
            )
        else:
            status, best_name = "unverified", None
            note = "Not on this pharmacy bill, so Aditi couldn't cross-check this name here."
        results.append({"prescribed": pname, "status": status, "bill_name": best_name, "note": note})
    return results
