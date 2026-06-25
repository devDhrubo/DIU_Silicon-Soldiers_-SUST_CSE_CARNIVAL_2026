KEYWORDS = {
    "wrong_transfer": [
        "wrong number", "wrong transfer", "sent to wrong", "wrong recipient",
        "wrong account", "sent by mistake", "wrong person", "mistakenly sent",
        "wrong bkash", "wrong mobile", "ভুল নম্বর", "taka to wrong", "send to wrong"
    ],
    "payment_failed": [
        "balance deducted", "failed but", "not received", "payment failed",
        "transaction failed", "deducted but", "money gone", "did not go through",
        "failed transaction", "payment not", "double charge", "double deducted",
        "charged twice", "unsuccessful", "payment unsuccessful"
    ],
    "refund_request": [
        "refund", "money back", "cancel", "i changed my mind", "return my money",
        "get my money back", "give back", "revert", "reverse",
        "want a refund", "please refund", "request refund"
    ],
    "phishing_or_social_engineering": [
        "otp", "pin", "password", "someone called", "suspicious call",
        "asking for otp", "asking for pin", "asking for password",
        "is that bkash", "is that real", "scam", "fraud call", "fake call",
        "they asked", "told me to share", "verify my account",
        "send otp", "give otp", "share pin"
    ],
    "other": [
        "app crashed", "app not working", "login issue", "can't login",
        "cannot login", "slow", "bug", "error", "not loading",
        "app problem", "technical issue", "ui issue"
    ]
}

STRONG_KEYWORDS = {
    "wrong_transfer": ["wrong number", "wrong transfer", "sent to wrong"],
    "payment_failed": ["balance deducted", "failed but", "not received"],
    "phishing_or_social_engineering": ["otp", "pin", "password", "someone called"],
    "refund_request": [],
    "other": []
}

REFUND_ESCALATION_KEYWORDS = [
    "contest", "wrong", "unauthorized", "dispute",
    "didn't send", "i never made", "i did not send", "not authorised",
    "not authorized", "didn't make", "did not make"
]

AGENT_SUMMARIES = {
    "wrong_transfer": "User sent money to the wrong person, needs recovery.",
    "payment_failed": "Payment failed but user thinks money was deducted.",
    "refund_request": "User wants a refund for a recent transaction.",
    "phishing_or_social_engineering": "Possible phishing attempt! Someone asked for sensitive details.",
    "other": "General issue, needs manual review."
}

def _score(msg: str, category: str) -> float:
    kw_list = KEYWORDS[category]
    if not kw_list:
        return 0.0
    hits = sum(1 for kw in kw_list if kw in msg)
    return hits / len(kw_list)

def _has_strong_keyword(msg: str, category: str) -> bool:
    return any(kw in msg for kw in STRONG_KEYWORDS[category])

def classify(message: str) -> dict:
    msg = message.lower()
    scores = {cat: _score(msg, cat) for cat in KEYWORDS}
    
    floored = {}
    for cat, raw in scores.items():
        if _has_strong_keyword(msg, cat):
            floored[cat] = max(raw, 0.70)
        else:
            floored[cat] = raw

    case_type = max(floored, key=floored.get)
    if floored[case_type] == 0.0:
        case_type = "other"

    confidence = min(round(floored[case_type], 2), 0.95)

    severity_map = {
        "wrong_transfer": "high",
        "payment_failed": "high",
        "phishing_or_social_engineering": "critical",
        "refund_request": "low",
        "other": "low"
    }
    severity = severity_map[case_type]

    if case_type == "refund_request":
        if any(kw in msg for kw in REFUND_ESCALATION_KEYWORDS):
            department = "dispute_resolution"
            severity = "medium"
        else:
            department = "customer_support"
    else:
        department_map = {
            "wrong_transfer": "dispute_resolution",
            "payment_failed": "payments_ops",
            "phishing_or_social_engineering": "fraud_risk",
            "other": "customer_support"
        }
        department = department_map[case_type]

    human_review_required = (severity == "critical" or case_type == "phishing_or_social_engineering")
    agent_summary = AGENT_SUMMARIES[case_type]

    return {
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": agent_summary,
        "human_review_required": human_review_required,
        "confidence": confidence
    }
