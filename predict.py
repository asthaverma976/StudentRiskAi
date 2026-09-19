"""
predict.py
----------
AI-based student feedback and complaint analysis.

Returns:
    - sentiment
    - category
    - priority
    - confidence
    - original text
"""


# ============================================================
# SENTIMENT KEYWORDS
# ============================================================

POSITIVE_WORDS = [
    "good",
    "great",
    "excellent",
    "happy",
    "satisfied",
    "helpful",
    "amazing",
    "best",
    "thank",
    "thanks",
    "nice",
    "clean",
    "improved",
    "improvement",
    "better",
    "अच्छा",
    "बहुत अच्छा",
    "धन्यवाद",
]


NEGATIVE_WORDS = [
    "bad",
    "poor",
    "worst",
    "angry",
    "unhappy",
    "problem",
    "issue",
    "complaint",
    "hate",
    "terrible",
    "worried",
    "disappointed",
    "broken",
    "dirty",
    "unsafe",
    "delay",
    "not working",
    "unavailable",
    "खराब",
    "समस्या",
    "शिकायत",
    "परेशान",
]


# ============================================================
# CATEGORY KEYWORDS
# These match the Admin Dashboard filters.
# ============================================================

CATEGORY_KEYWORDS = {

    "Faculty": [
        "teacher",
        "faculty",
        "professor",
        "lecturer",
        "class",
        "lecture",
        "teaching",
        "teacher behavior",
        "faculty behavior",
        "staff",
    ],

    "Hostel": [
        "hostel",
        "room",
        "warden",
        "hostel room",
        "water",
        "hostel food",
        "hostel mess",
        "cleaning",
        "electricity",
        "fan",
        "accommodation",
    ],

    "Library": [
        "library",
        "book",
        "books",
        "reading room",
        "library timing",
        "library seat",
        "journal",
        "study room",
    ],

    "Canteen": [
        "canteen",
        "food",
        "mess",
        "restaurant",
        "meal",
        "lunch",
        "breakfast",
        "dinner",
        "canteen food",
        "food quality",
    ],

    "Examination": [
        "exam",
        "examination",
        "marks",
        "result",
        "result issue",
        "question paper",
        "paper",
        "internal marks",
        "semester exam",
        "back paper",
        "revaluation",
    ],

    "Infrastructure": [
        "lab",
        "laboratory",
        "classroom",
        "building",
        "computer",
        "wifi",
        "internet",
        "electricity",
        "projector",
        "fan",
        "ac",
        "chair",
        "bench",
        "infrastructure",
        "washroom",
        "road",
        "parking",
        "campus",
    ],
}


# ============================================================
# PRIORITY KEYWORDS
# ============================================================

HIGH_PRIORITY_WORDS = [
    "urgent",
    "emergency",
    "immediately",
    "danger",
    "dangerous",
    "unsafe",
    "harassment",
    "ragging",
    "threat",
    "violence",
    "critical",
    "accident",
    "fire",
    "security",
    "sexual harassment",
]


MEDIUM_PRIORITY_WORDS = [
    "problem",
    "issue",
    "complaint",
    "delay",
    "broken",
    "not working",
    "poor",
    "unavailable",
    "dirty",
    "bad",
]


# ============================================================
# ANALYZE FEEDBACK
# ============================================================

def analyze_feedback(text):
    """
    Analyze a student feedback / complaint.

    Returns a dictionary compatible with:
        pages/student_feedback.py
        database.insert_complaint()
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not text or not str(text).strip():

        return {
            "text": "",
            "sentiment": "Neutral",
            "category": "General",
            "priority": "Low",
            "confidence": 0.0,
        }


    original_text = str(text).strip()

    normalized_text = original_text.lower()


    # ========================================================
    # SENTIMENT
    # ========================================================

    positive_count = sum(
        1
        for word in POSITIVE_WORDS
        if word.lower() in normalized_text
    )


    negative_count = sum(
        1
        for word in NEGATIVE_WORDS
        if word.lower() in normalized_text
    )


    if negative_count > positive_count:

        sentiment = "Negative"

    elif positive_count > negative_count:

        sentiment = "Positive"

    else:

        sentiment = "Neutral"


    # --------------------------------------------------------
    # Sentiment confidence
    # --------------------------------------------------------

    total_sentiment_matches = (
        positive_count + negative_count
    )


    if total_sentiment_matches == 0:

        sentiment_confidence = 0.60

    else:

        sentiment_confidence = (
            max(
                positive_count,
                negative_count
            )
            / total_sentiment_matches
        )


    # ========================================================
    # CATEGORY
    # ========================================================

    category_scores = {}


    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in normalized_text:

                score += 1


        category_scores[category] = score


    best_category = max(
        category_scores,
        key=category_scores.get
    )


    best_category_score = (
        category_scores[best_category]
    )


    if best_category_score == 0:

        category = "General"
        category_confidence = 0.60

    else:

        category = best_category

        total_category_matches = sum(
            category_scores.values()
        )

        category_confidence = (
            best_category_score
            / total_category_matches
        )


    # ========================================================
    # PRIORITY
    # ========================================================

    high_count = sum(
        1
        for word in HIGH_PRIORITY_WORDS
        if word.lower() in normalized_text
    )


    medium_count = sum(
        1
        for word in MEDIUM_PRIORITY_WORDS
        if word.lower() in normalized_text
    )


    if high_count > 0:

        priority = "High"

    elif (
        medium_count > 0
        or sentiment == "Negative"
    ):

        priority = "Medium"

    else:

        priority = "Low"


    # ========================================================
    # OVERALL CONFIDENCE
    # ========================================================

    confidence = round(
        (
            sentiment_confidence
            + category_confidence
        ) / 2,
        2
    )


    # Keep confidence between 0 and 1

    confidence = max(
        0.0,
        min(1.0, confidence)
    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "text": original_text,

        "sentiment": sentiment,

        "category": category,

        "priority": priority,

        "confidence": confidence,
    }