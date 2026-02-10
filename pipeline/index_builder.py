"""FAISS index builder — create and save a flat IP index from embeddings."""

import json
import logging

import faiss
import numpy as np

from config.settings import EMBEDDING_DIM, FAISS_INDEX_PATH, EMBEDDINGS_PATH, SUMMARIES_PATH

logger = logging.getLogger(__name__)


def build_faiss_index(
    posts: list[dict],
    summaries: list[str],
    embeddings: np.ndarray,
    topics: list[list[str]],
) -> None:
    """Build FAISS index and save embeddings + metadata to disk."""
    assert embeddings.shape[0] == len(posts), "Embedding count must match post count"
    assert embeddings.shape[1] == EMBEDDING_DIM, f"Expected dim {EMBEDDING_DIM}, got {embeddings.shape[1]}"

    # Build index (Inner Product for cosine similarity on normalized vectors)
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    # Save embeddings
    np.save(str(EMBEDDINGS_PATH), embeddings)

    # Save metadata alongside summaries
    metadata = []
    for i, post in enumerate(posts):
        metadata.append({
            "id": post["id"],
            "title": post["title"],
            "summary": summaries[i] if i < len(summaries) else "",
            "score": post["score"],
            "num_comments": post.get("num_comments", 0),
            "hn_url": post["hn_url"],
            "url": post.get("url", ""),
            "topics": topics[i] if i < len(topics) else [],
            "story_text": post.get("story_text", "")[:300],
        })

    with open(SUMMARIES_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("FAISS index (%d vectors) saved to %s", index.ntotal, FAISS_INDEX_PATH)
