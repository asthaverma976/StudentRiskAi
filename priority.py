"""
priority.py
------------
Priority Module: assigns Low / Medium / High priority to a complaint using a
rule-assisted approach that combines:
    - predicted sentiment
    - predicted category
    - presence of urgency keywords in the raw text

This keeps the logic simple, transparent and explainable (per PRD - "simple,
explainable models"), while still using the ML predictions as signals.
"""

# Keywords that strongly suggest an urgent / safety-related issue
HIGH_URGENCY_KEYWORDS = [
    "exam", "examination", "urgent", "immediately", "not working", "broken",
    "fire", "safety", "unsafe", "danger", "accident", "injury", "harassment",
    "leak", "leakage", "electric", "shock", "emergency", "next week",
    "tomorrow", "no water", "no electricity", "not functioning", "crash",
    "server crash", "security",
]

MEDIUM_URGENCY_KEYWORDS = [
    "delay", "delayed", "slow", "queue", "long wait", "shortage", "dirty",
    "unhygienic", "outdated", "overcrowded", "issue", "problem", "complaint",
]

# Categories that tend to carry higher operational urgency when negative
HIGH_PRIORITY_CATEGORIES = {"Examination", "Infrastructure"}


def detect_priority(raw_text: str, sentiment: str, category: str) -> str:
    """
    Determine priority (Low / Medium / High) from the raw feedback text plus
    the predicted sentiment and category.
    """
    text_lower = (raw_text or "").lower()

    has_high_keyword = any(kw in text_lower for kw in HIGH_URGENCY_KEYWORDS)
    has_medium_keyword = any(kw in text_lower for kw in MEDIUM_URGENCY_KEYWORDS)

    # Rule 1: Negative sentiment + urgency keyword => High
    if sentiment == "Negative" and has_high_keyword:
        return "High"

    # Rule 2: Negative sentiment + sensitive category => High
    if sentiment == "Negative" and category in HIGH_PRIORITY_CATEGORIES:
        return "High"

    # Rule 3: Negative sentiment generally => Medium (unless already High above)
    if sentiment == "Negative":
        return "Medium"

    # Rule 4: Neutral sentiment with a medium-urgency keyword => Medium
    if sentiment == "Neutral" and (has_medium_keyword or has_high_keyword):
        return "Medium"

    # Rule 5: Everything else (Positive, or Neutral with no urgency signal) => Low
    return "Low"


if __name__ == "__main__":
    examples = [
        ("The computer lab has several non-working computers and our practical exam is next week.", "Negative", "Infrastructure"),
        ("The canteen food is tasty and reasonably priced.", "Positive", "Canteen"),
        ("Library timings could be extended a little.", "Neutral", "Library"),
    ]
    for text, s, c in examples:
        print(text, "->", detect_priority(text, s, c))
