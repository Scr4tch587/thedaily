"""Ray-parallel NLP processing — summarization, embeddings, topic classification."""

import logging

import numpy as np
import ray
from openai import OpenAI
from sentence_transformers import SentenceTransformer

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


@ray.remote
def summarize_batch(posts: list[dict]) -> list[str]:
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


@ray.remote
def embed_batch(posts: list[dict]) -> np.ndarray:
    """Generate embeddings for a batch of posts using sentence-transformers."""
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [_post_text(post) for post in posts]
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embeddings, dtype=np.float32)


@ray.remote
def classify_batch(posts: list[dict]) -> list[list[str]]:
    """Classify topics for a batch of posts."""
    return [classify_topic(_post_text(post)) for post in posts]


def process_posts(posts: list[dict]) -> tuple[list[str], np.ndarray, list[list[str]]]:
    """Run all processing in parallel with Ray and return (summaries, embeddings, topics)."""
    # Split into batches for parallelism
    batch_size = max(1, len(posts) // 4)
    batches = [posts[i : i + batch_size] for i in range(0, len(posts), batch_size)]

    # Launch all tasks in parallel
    summary_futures = [summarize_batch.remote(batch) for batch in batches]
    embed_futures = [embed_batch.remote(batch) for batch in batches]
    classify_futures = [classify_batch.remote(batch) for batch in batches]

    # Gather results
    summary_results = ray.get(summary_futures)
    embed_results = ray.get(embed_futures)
    classify_results = ray.get(classify_futures)

    # Flatten
    summaries = [s for batch in summary_results for s in batch]
    embeddings = np.vstack(embed_results)
    topics = [t for batch in classify_results for t in batch]

    logger.info("Processed %d stories: %d summaries, %s embeddings, %d topic lists",
                len(posts), len(summaries), embeddings.shape, len(topics))
    return summaries, embeddings, topics
