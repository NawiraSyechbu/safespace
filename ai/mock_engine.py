"""
Mesin moderasi PALSU, hanya untuk menguji alur web (AI_MODE=mock).
Bukan model AI. Gunakan kata pemicu berikut di dalam teks:
  [uji-blokir]  -> status blocked
  [uji-review]  -> status pending_review
  selain itu    -> approved
"""


def mock_analyze(text: str) -> dict:
    lowered = text.lower()

    if "[uji-blokir]" in lowered:
        status, decision = "blocked", "block"
        reason = "[MODE UJI] Konten ditolak karena memuat pemicu [uji-blokir]."
    elif "[uji-review]" in lowered:
        status, decision = "pending_review", "review"
        reason = "[MODE UJI] Konten ditahan karena memuat pemicu [uji-review]."
    else:
        status, decision = "approved", "allow"
        reason = "[MODE UJI] Tidak ada pemicu uji; konten disetujui."

    return {
        "text": text,
        "status": status,
        "decision": decision,
        "reason": reason,
        "predictions": None,
    }
