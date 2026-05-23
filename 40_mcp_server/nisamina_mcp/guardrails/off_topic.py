"""Off-topic redirect — keyword filter STUB.

The chatbot is scoped to Garifuna learning + cultural context + heritage
practice. This stub uses a simple on-topic keyword filter to flag clear
off-topic drift. A real classifier requires a labeled off-topic vs
on-topic corpus, which doesn't exist yet — that's deferred.
"""

from __future__ import annotations


ON_TOPIC_KEYWORDS: tuple[str, ...] = (
    "garifuna",
    "garínagu",
    "garinagu",
    "kareru",
    "yurumein",
    "cayetano",
    "belize",
    "honduras",
    "guatemala",
    "nicaragua",
    "walagallo",  # at anthropological level — sacred_knowledge module handles ritual specifics
    "abeimahani",
    "arumahani",
    "wanaragua",
    "buyei",
    "moecst",
    "commission",
    "dictionary",
    "lesson",
    "vocabulary",
    "word",
    "phrase",
    "grammar",
    "pronunciation",
    "translate",
    "learn",
    "culture",
    "tradition",
    "song",
    "drum",
    "elder",
    "ancestor",
    "language",
    "diaspora",
    "nyc",
    "new york",
    "st. vincent",
    "st vincent",
    "yurumein",
    # Common Garifuna lexicon hooks
    "buguya",
    "nuani",
    "katei",
    "ababagüda",
    "ababaü",
)


def is_likely_off_topic(
    text: str,
    allowed_topics: list[str] | None = None,
) -> bool:
    """Return True if `text` shows no on-topic keyword match.

    Conservative: short messages (<= 3 words) default to ON-topic to
    avoid false-positive redirects on greetings or short clarifications.
    Long messages with zero on-topic keyword present are flagged.

    TODO M-P3.A: replace with a proper classifier once on/off-topic
    labeled corpus exists.
    """
    if not text:
        return False
    norm = text.lower()
    word_count = len(norm.split())
    if word_count <= 3:
        return False

    keywords = tuple(allowed_topics) if allowed_topics else ON_TOPIC_KEYWORDS
    return not any(k in norm for k in keywords)
