"""Parallel NLP processing — summarization, embeddings, topic classification."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from openai import OpenAI

from config.settings import EMBEDDING_MODEL, OPENAI_API_KEY, OPENAI_MODEL, TOPIC_KEYWORDS

logger = logging.getLogger(__name__)


def _post_text(post: dict) -> str:
    """Combine title + story_text + top comment bodies into one string."""
    parts = [post["title"]]
    if post.get("story_text"):
        parts.append(post["story_text"][:500])
    for c in post.get("top_comments", [])[:3]:
        parts.append(c.get("body", "")[:200])
    return "\n".join(parts)


def classify_topic(text: str) -> list[str]:
    """Keyword-based topic classification."""
    text_lower = text.lower()
    topics = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            topics.append(topic)
    return topics if topics else ["General"]


def _summarize_batch(posts: list[dict]) -> list[str]:
    """Summarize a batch of posts using OpenAI."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    summaries = []

    for post in posts:
        text = _post_text(post)
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise tech news summarizer. Summarize the following Hacker News story in 2-3 sentences, focusing on the key technical insight or news.",
                    },
                    {"role": "user", "content": text[:2000]},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            summaries.append(resp.choices[0].message.content.strip())
        except Exception as e:
            logger.error("Summarization failed for story %s: %s", post.get("id"), e)
            summaries.append(post["title"])

    return summaries


def _embed_all(posts: list[dict]) -> np.ndarray:
    """Generate embeddings for all posts using OpenAI embeddings API."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    texts = [_post_text(post)[:8000] for post in posts]

    # OpenAI supports batching up to 2048 inputs
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        batch_embs = [item.embedding for item in resp.data]
        all_embeddings.extend(batch_embs)
        logger.info("Embedded %d/%d texts", min(i + batch_size, len(texts)), len(texts))

    return np.array(all_embeddings, dtype=np.float32)


def _classify_all(posts: list[dict]) -> list[list[str]]:
    """Classify topics for all posts."""
    return [classify_topic(_post_text(post)) for post in posts]


def process_posts(posts: list[dict]) -> tuple[list[str], np.ndarray, list[list[str]]]:
    """Run all processing and return (summaries, embeddings, topics).

    - Summarization: batched across threads (IO-bound OpenAI calls)
    - Embeddings: batched OpenAI API calls
    - Classification: single pass (fast keyword matching)
    """
    # Split summaries into batches for thread-parallel OpenAI calls
    num_workers = min(4, os.cpu_count() or 2)
    batch_size = max(1, len(posts) // num_workers)
    batches = [posts[i : i + batch_size] for i in range(0, len(posts), batch_size)]

    # Summarize in parallel threads (IO-bound)
    logger.info("Summarizing %d stories across %d threads...", len(posts), len(batches))
    summaries: list[str] = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_summarize_batch, batch): i for i, batch in enumerate(batches)}
        results: dict[int, list[str]] = {}
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()
        for i in range(len(batches)):
            summaries.extend(results[i])

    # Embeddings via OpenAI API
    logger.info("Generating embeddings via OpenAI...")
    embeddings = _embed_all(posts)

    # Classification (fast, no parallelism needed)
    logger.info("Classifying topics...")
    topics = _classify_all(posts)

    logger.info("Processed %d stories: %d summaries, %s embeddings, %d topic lists",
                len(posts), len(summaries), embeddings.shape, len(topics))
    return summaries, embeddings, topics
