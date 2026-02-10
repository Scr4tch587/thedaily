"""Data cleaning — dedup, filter low-score stories, normalize text."""

import logging
import re

from config.settings import MIN_SCORE

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Collapse whitespace, strip HTML remnants, and strip."""
    text = re.sub(r"<[^>]+>", " ", text)  # strip HTML tags from HN story_text / comments
    text = re.sub(r"&\w+;", " ", text)    # strip HTML entities
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_posts(raw_posts: list[dict]) -> list[dict]:
    """Filter and deduplicate HN stories."""
    seen_ids: set[str] = set()
    cleaned: list[dict] = []

    for post in raw_posts:
        # Skip posts with no title
        if not post.get("title"):
            continue

        # Skip low-score posts
        if post.get("score", 0) < MIN_SCORE:
            continue

        # Dedup by HN object ID
        post_id = post.get("id", "")
        if post_id in seen_ids:
            continue
        seen_ids.add(post_id)

        # Normalize text fields
        post["title"] = normalize_text(post.get("title", ""))
        post["story_text"] = normalize_text(post.get("story_text", ""))
        for comment in post.get("top_comments", []):
            comment["body"] = normalize_text(comment.get("body", ""))

        cleaned.append(post)

    logger.info("Cleaned %d → %d stories", len(raw_posts), len(cleaned))
    return cleaned
