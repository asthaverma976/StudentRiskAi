"""
preprocessing.py
-----------------
Text Preprocessing Module for the AI Student Feedback & Complaint Analysis System.

Responsible for cleaning raw feedback text before it is passed to the
sentiment / category ML models:
    - lowercasing
    - removing URLs, punctuation, numbers and extra whitespace
    - tokenization
    - stopword removal
    - (optional) lemmatization if NLTK wordnet data is available
"""

import re
import string

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    # Attempt to use NLTK data; download quietly on first run if missing.
    def _ensure_nltk_data():
        for pkg in ["punkt", "punkt_tab", "stopwords"]:
            try:
                nltk.data.find(
                    f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}"
                )
            except LookupError:
                try:
                    nltk.download(pkg, quiet=True)
                except Exception:
                    pass

    _ensure_nltk_data()
    _STOPWORDS = set(stopwords.words("english"))
    _NLTK_OK = True
except Exception:
    # Fallback stopword list if NLTK / its data isn't available in the environment.
    _STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "in", "on", "at", "to", "for", "of", "and", "or", "but", "with",
        "this", "that", "these", "those", "it", "its", "as", "by", "from",
        "we", "our", "us", "i", "my", "me", "you", "your", "they", "their",
        "he", "she", "him", "her", "his", "not", "no", "do", "does", "did",
        "have", "has", "had", "will", "would", "can", "could", "should",
        "so", "very", "just", "there", "here", "than", "then",
    }
    _NLTK_OK = False


def clean_text(text: str) -> str:
    """Lowercase + strip URLs/punctuation/numbers/extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)          # URLs
    text = re.sub(r"[^a-z\s]", " ", text)                    # keep only letters
    text = re.sub(r"\s+", " ", text).strip()                 # collapse whitespace
    return text


def tokenize(text: str):
    """Tokenize cleaned text into words."""
    if _NLTK_OK:
        try:
            return word_tokenize(text)
        except Exception:
            pass
    return text.split()


def remove_stopwords(tokens):
    """Remove common stopwords and very short tokens."""
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def preprocess(text: str) -> str:
    """
    Full pipeline: clean -> tokenize -> remove stopwords -> rejoin.
    Returns a cleaned string ready for vectorization (e.g. TF-IDF).
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    return " ".join(tokens)


if __name__ == "__main__":
    sample = "The Computer Lab has SEVERAL non-working computers!!! Our practical exam is next week :("
    print("Original :", sample)
    print("Cleaned  :", preprocess(sample))
