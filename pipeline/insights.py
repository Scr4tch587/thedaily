"""Insight extraction — daily summaries, trending topics, breakthrough detection."""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone

from config.settings import (
    BREAKTHROUGH_SCORE_THRESHOLD,
    CHARTS_DATA_PATH,
    DAILY_DIGEST_PATH,
)

logger = logging.getLogger(__name__)


def extract_trending_topics(posts: list[dict], topics: list[list[str]]) -> dict:
    """Compute topic → {count, avg_score}."""
    topic_scores: dict[str, list[int]] = defaultdict(list)

    for post, post_topics in zip(posts, topics):
        for t in post_topics:
            topic_scores[t].append(post["score"])

    return {
        topic: {"count": len(scores), "avg_score": round(sum(scores) / len(scores), 1)}
        for topic, scores in sorted(topic_scores.items(), key=lambda x: -len(x[1]))
    }


def detect_breakthroughs(posts: list[dict], summaries: list[str], topics: list[list[str]]) -> list[dict]:
    """Flag high-score stories as potential breakthroughs."""
    breakthroughs = []
    for post, summary, post_topics in zip(posts, summaries, topics):
        if post["score"] >= BREAKTHROUGH_SCORE_THRESHOLD:
            breakthroughs.append({
                "title": post["title"],
                "summary": summary,
                "score": post["score"],
                "num_comments": post.get("num_comments", 0),
                "hn_url": post["hn_url"],
                "topics": post_topics,
            })

    breakthroughs.sort(key=lambda x: -x["score"])
    logger.info("Detected %d breakthroughs", len(breakthroughs))
    return breakthroughs


def build_comment_engagement(posts: list[dict]) -> dict:
    """Comment count buckets for engagement analysis."""
    buckets = {"0-10": 0, "11-50": 0, "51-100": 0, "101-250": 0, "250+": 0}
    for p in posts:
        n = p.get("num_comments", 0)
        if n <= 10:
            buckets["0-10"] += 1
        elif n <= 50:
            buckets["11-50"] += 1
        elif n <= 100:
            buckets["51-100"] += 1
        elif n <= 250:
            buckets["101-250"] += 1
        else:
            buckets["250+"] += 1
    return buckets


def build_score_distribution(posts: list[dict]) -> list[int]:
    """Return list of scores for histogram."""
    return [p["score"] for p in posts]


def generate_charts_data(posts: list[dict], topics: list[list[str]]) -> dict:
    """Produce the charts_data.json content."""
    charts = {
        "trending_topics": extract_trending_topics(posts, topics),
        "comment_engagement": build_comment_engagement(posts),
        "score_distribution": build_score_distribution(posts),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(CHARTS_DATA_PATH, "w") as f:
        json.dump(charts, f, indent=2)

    logger.info("Charts data saved to %s", CHARTS_DATA_PATH)
    return charts


def generate_daily_digest(
    posts: list[dict],
    summaries: list[str],
    topics: list[list[str]],
    breakthroughs: list[dict],
    trending: dict,
) -> dict:
    """Produce the daily_digest.json content."""
    # Top 10 stories by score
    indexed = sorted(enumerate(posts), key=lambda x: -x[1]["score"])[:10]
    top_posts = []
    for i, post in indexed:
        top_posts.append({
            "title": post["title"],
            "summary": summaries[i] if i < len(summaries) else "",
            "score": post["score"],
            "num_comments": post.get("num_comments", 0),
            "hn_url": post["hn_url"],
            "url": post.get("url", ""),
            "topics": topics[i] if i < len(topics) else [],
        })

    digest = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_posts": len(posts),
        "breakthroughs": breakthroughs[:5],
        "top_posts": top_posts,
        "trending_topics": trending,
    }

    with open(DAILY_DIGEST_PATH, "w") as f:
        json.dump(digest, f, indent=2)

    logger.info("Daily digest saved to %s", DAILY_DIGEST_PATH)
    return digest
