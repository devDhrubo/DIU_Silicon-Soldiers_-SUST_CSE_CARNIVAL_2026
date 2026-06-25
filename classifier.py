"""
classifier.py
-------------
Rule-based ticket classifier for QueueStorm Warmup API.

Design decisions (Rev 3, locked before coding):
  - Confidence scored per winning category (matches / category_list_size)
  - Floor at 0.70 when any STRONG_KEYWORD from that category matched
  - Cap at 0.95
  - Refund routing: default → customer_support (low);
    escalate → dispute_resolution (medium) if escalation keywords present
  - Agent summaries are static templates — no PIN/OTP/password words ever appear
"""

from __future__ import annotations

# ── Keyword tables ──────────────────────────────────────────────────────────────

KEYWORDS: dict[str, list[str]] = {
    "wrong_transfer": [
        "wrong number", "wrong transfer", "sent to wrong", "wrong recipient",
        "wrong account", "sent by mistake", "wrong person", "mistakenly sent",
        "wrong bkash", "wrong mobile", "ভুল নম্বর",  # romanised Bengali handled below
        "taka to wrong", "send to wrong",
    ],
    "payment_failed": [
        "balance deducted", "failed but", "not received", "payment failed",
        "transaction failed", "deducted but", "money gone", "did not go through",
        "failed transaction", "payment not", "double charge", "double deducted",
        "charged twice", "unsuccessful", "payment unsuccessful",
    ],
    "refund_request": [
        "refund", "money back", "cancel", "i changed my mind", "return my money",
        "get my money back", "give back", "revert", "reverse",
        "want a refund", "please refund", "request refund",
    ],
    "phishing_or_social_engineering": [
        "otp", "pin", "password", "someone called", "suspicious call",
        "asking for otp", "asking for pin", "asking for password",
        "is that bkash", "is that real", "scam", "fraud call", "fake call",
        "they asked", "told me to share", "verify my account",
        "send otp", "give otp", "share pin",
    ],
    "other": [
        "app crashed", "app not working", "login issue", "can't login",
        "cannot login", "slow", "bug", "error", "not loading",
        "app problem", "technical issue", "ui issue",
    ],
}

# ── Strong keywords (deterministic 0.70 confidence floor) ──────────────────────
# Any match here → confidence = max(raw_score, 0.70)

STRONG_KEYWORDS: dict[str, list[str]] = {
    "wrong_transfer":                ["wrong number", "wrong transfer", "sent to wrong"],
    "payment_failed":                ["balance deducted", "failed but", "not received"],
    "phishing_or_social_engineering":["otp", "pin", "password", "someone called"],
    "refund_request":                [],   # no single-keyword trigger strong enough
    "other":                         [],
}

# ── Refund escalation triggers ─────────────────────────────────────────────────
# If refund + any of these → dispute_resolution (medium) instead of customer_support (low)

REFUND_ESCALATION_KEYWORDS: list[str] = [
    "contest", "wrong", "unauthorized", "dispute",
    "didn't send", "i never made", "i did not send", "not authorised",
    "not authorized", "didn't make", "did not make",
]

# ── Static agent summary templates (safety-clean by construction) ──────────────

AGENT_SUMMARIES: dict[str, str] = {
    "wrong_transfer": (
        "Customer reports sending money to an unintended recipient and requests recovery."
    ),
    "payment_failed": (
        "Customer reports a failed transaction with possible balance deduction."
    ),
    "refund_request": (
        "Customer is requesting a refund for a recent transaction."
    ),
    "phishing_or_social_engineering": (
        "Customer reports a suspicious contact attempting to obtain account credentials. "
        "Immediate human review required."
    ),
    "other": (
        "Customer has reported a general issue requiring support team review."
    ),
}

# ── Core classifier ────────────────────────────────────────────────────────────

def _score(message_lower: str, category: str) -> float:
    """Return raw match ratio for a category."""
    kw_list = KEYWORDS[category]
    if not kw_list:
        return 0.0
    hits = sum(1 for kw in kw_list if kw in message_lower)
    return hits / len(kw_list)


def _has_strong_keyword(message_lower: str, category: str) -> bool:
    return any(kw in message_lower for kw in STRONG_KEYWORDS[category])


def _confidence(message_lower: str, category: str) -> float:
    raw = _score(message_lower, category)
    if _has_strong_keyword(message_lower, category):
        raw = max(raw, 0.70)
    return min(round(raw, 2), 0.95)


def classify(message: str) -> dict:
    """
    Returns a dict with keys:
      case_type, severity, department, agent_summary,
      human_review_required, confidence
    """
    msg = message.lower()

    # Score all categories
    scores = {cat: _score(msg, cat) for cat in KEYWORDS}

    # Apply strong-keyword floor per category before picking winner
    floored = {}
    for cat, raw in scores.items():
        if _has_strong_keyword(msg, cat):
            floored[cat] = max(raw, 0.70)
        else:
            floored[cat] = raw

    # Winning category is the highest floored score
    case_type = max(floored, key=floored.get)

    # If everything scored 0 (no keywords matched at all) → other
    if floored[case_type] == 0.0:
        case_type = "other"

    confidence = min(round(floored[case_type], 2), 0.95)

    # ── Severity ───────────────────────────────────────────────────────────────
    severity_map: dict[str, str] = {
        "wrong_transfer":                "high",
        "payment_failed":                "high",
        "phishing_or_social_engineering":"critical",
        "refund_request":                "low",
        "other":                         "low",
    }
    severity = severity_map[case_type]

    # ── Department + refund escalation ────────────────────────────────────────
    if case_type == "refund_request":
        if any(kw in msg for kw in REFUND_ESCALATION_KEYWORDS):
            department = "dispute_resolution"
            severity = "medium"
        else:
            department = "customer_support"
    else:
        department_map: dict[str, str] = {
            "wrong_transfer":                "dispute_resolution",
            "payment_failed":                "payments_ops",
            "phishing_or_social_engineering":"fraud_risk",
            "other":                         "customer_support",
        }
        department = department_map[case_type]

    # ── Human review flag ─────────────────────────────────────────────────────
    human_review_required = (
        severity == "critical"
        or case_type == "phishing_or_social_engineering"
    )

    # ── Agent summary (static template, safety-clean) ─────────────────────────
    agent_summary = AGENT_SUMMARIES[case_type]

    return {
        "case_type":             case_type,
        "severity":              severity,
        "department":            department,
        "agent_summary":         agent_summary,
        "human_review_required": human_review_required,
        "confidence":            confidence,
    }
