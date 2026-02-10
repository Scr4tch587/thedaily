"""Hacker News scraper via Algolia API — no auth required."""

import json
import logging
import time
from datetime import datetime, timezone

import requests

from config.settings import (
    HN_ALGOLIA_BASE,
    HN_FRONT_PAGE_HITS,
    HN_ITEM_URL,
    HN_SEARCH_HITS_PER_QUERY,
    HN_TOP_COMMENTS,
    HN_TOPIC_QUERIES,
    RAW_DIR,
)

logger = logging.getLogger(__name__)

SESSION = requests.Session()


def _fetch_front_page() -> list[dict]:
    """Fetch current front-page stories via Algolia search."""
    url = f"{HN_ALGOLIA_BASE}/search"
    params = {
        "tags": "front_page",
        "hitsPerPage": HN_FRONT_PAGE_HITS,
    }
    resp = SESSION.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("hits", [])


def _search_recent(query: str) -> list[dict]:
    """Search recent HN stories by keyword."""
    url = f"{HN_ALGOLIA_BASE}/search_by_date"
    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": HN_SEARCH_HITS_PER_QUERY,
    }
    resp = SESSION.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("hits", [])


def _fetch_item_comments(object_id: str) -> list[dict]:
    """Fetch top-level comments for a story."""
    url = f"{HN_ALGOLIA_BASE}/items/{object_id}"
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
        item = resp.json()
        children = item.get("children", [])
        comments = []
        for child in children[:HN_TOP_COMMENTS]:
            text = child.get("text") or ""
            if text and child.get("author"):
                comments.append({
                    "body": text,
                    "author": child["author"],
                })
        return comments
    except Exception:
        return []


def _normalize_hit(hit: dict, comments: list[dict] | None = None) -> dict:
    """Convert an Algolia hit into our standard post format."""
    object_id = hit.get("objectID", "")
    return {
        "id": object_id,
        "title": hit.get("title") or "",
        "url": hit.get("url") or "",
        "story_text": hit.get("story_text") or "",
        "score": hit.get("points") or 0,
        "num_comments": hit.get("num_comments") or 0,
        "created_utc": hit.get("created_at_i") or 0,
        "author": hit.get("author") or "",
        "hn_url": HN_ITEM_URL.format(object_id),
        "source_tag": hit.get("_tags", ["story"])[0] if hit.get("_tags") else "story",
        "top_comments": comments or [],
    }


def scrape_all(fetch_comments: bool = True) -> list[dict]:
    """Scrape HN front page + topic searches. Save raw JSON snapshot."""
    seen_ids: set[str] = set()
    all_posts: list[dict] = []

    # 1. Front page
    logger.info("Fetching HN front page...")
    for hit in _fetch_front_page():
        oid = hit.get("objectID", "")
        if oid and oid not in seen_ids:
            seen_ids.add(oid)
            comments = _fetch_item_comments(oid) if fetch_comments else []
            all_posts.append(_normalize_hit(hit, comments))
            if fetch_comments:
                time.sleep(0.1)  # be polite to the API

    logger.info("Front page: %d stories", len(all_posts))

    # 2. Topic searches
    for query in HN_TOPIC_QUERIES:
        logger.info("Searching HN for '%s'...", query)
        try:
            hits = _search_recent(query)
            added = 0
            for hit in hits:
                oid = hit.get("objectID", "")
                if oid and oid not in seen_ids:
                    seen_ids.add(oid)
                    comments = _fetch_item_comments(oid) if fetch_comments else []
                    all_posts.append(_normalize_hit(hit, comments))
                    added += 1
                    if fetch_comments:
                        time.sleep(0.1)
            logger.info("  → %d new stories from '%s'", added, query)
        except Exception:
            logger.exception("Failed to search for '%s'", query)

    # Save raw snapshot
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = RAW_DIR / f"{today}_hn.json"
    with open(output_path, "w") as f:
        json.dump(all_posts, f, indent=2)

    logger.info("Saved %d total stories to %s", len(all_posts), output_path)
    return all_posts
