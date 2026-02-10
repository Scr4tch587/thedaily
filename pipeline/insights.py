"""Insight extraction — daily summaries, trending topics, breakthrough detection."""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.parse import urlparse

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


def build_top_stories(posts: list[dict], summaries: list[str]) -> list[dict]:
    """Top 5 stories by score."""
    indexed = sorted(enumerate(posts), key=lambda x: -x[1]["score"])[:5]
    return [
        {
            "title": posts[i]["title"],
            "score": posts[i]["score"],
            "num_comments": posts[i].get("num_comments", 0),
            "hn_url": posts[i]["hn_url"],
            "summary": summaries[i] if i < len(summaries) else "",
        }
        for i, _ in indexed
    ]


def build_hot_discussions(posts: list[dict]) -> list[dict]:
    """Stories with highest comment-to-score ratio (min 20 comments to filter noise)."""
    candidates = [p for p in posts if p.get("num_comments", 0) >= 20 and p.get("score", 0) > 0]
    candidates.sort(key=lambda p: p["num_comments"] / max(p["score"], 1), reverse=True)
    return [
        {
            "title": p["title"],
            "score": p["score"],
            "num_comments": p["num_comments"],
            "ratio": round(p["num_comments"] / max(p["score"], 1), 1),
            "hn_url": p["hn_url"],
        }
        for p in candidates[:5]
    ]


def build_domain_leaderboard(posts: list[dict]) -> list[dict]:
    """Top domains by link count."""
    domains: Counter = Counter()
    for p in posts:
        url = p.get("url", "")
        if url:
            try:
                host = urlparse(url).netloc
                # Clean up www. prefix
                if host.startswith("www."):
                    host = host[4:]
                if host:
                    domains[host] += 1
            except Exception:
                pass

    return [{"domain": domain, "count": count} for domain, count in domains.most_common(10)]


def build_story_type_breakdown(posts: list[dict]) -> dict:
    """Count of Show HN / Ask HN / regular stories."""
    types: dict[str, int] = {"Show HN": 0, "Ask HN": 0, "Launch HN": 0, "Stories": 0}
    for p in posts:
        title = p.get("title", "")
        if title.startswith("Show HN"):
            types["Show HN"] += 1
        elif title.startswith("Ask HN"):
            types["Ask HN"] += 1
        elif title.startswith("Launch HN"):
            types["Launch HN"] += 1
        else:
            types["Stories"] += 1

    # Remove zero entries
    return {k: v for k, v in types.items() if v > 0}


def generate_charts_data(posts: list[dict], topics: list[list[str]], summaries: list[str] | None = None) -> dict:
    """Produce the charts_data.json content."""
    charts = {
        "trending_topics": extract_trending_topics(posts, topics),
        "top_stories": build_top_stories(posts, summaries or []),
        "hot_discussions": build_hot_discussions(posts),
        "domain_leaderboard": build_domain_leaderboard(posts),
        "story_type_breakdown": build_story_type_breakdown(posts),
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
