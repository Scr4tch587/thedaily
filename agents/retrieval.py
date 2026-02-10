"""Retrieval node — embed query and search FAISS index for relevant posts."""

import json
import logging

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL, FAISS_INDEX_PATH, FAISS_TOP_K, SUMMARIES_PATH

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None
_index: faiss.Index | None = None
_metadata: list[dict] | None = None


def _load_resources():
    global _model, _index, _metadata
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    if _index is None:
        _index = faiss.read_index(str(FAISS_INDEX_PATH))
    if _metadata is None:
        with open(SUMMARIES_PATH) as f:
            _metadata = json.load(f)


def retrieve(state: dict) -> dict:
    """Retrieve top-K relevant posts for the user query."""
    _load_resources()

    query = state["query"]
    query_embedding = _model.encode([query], normalize_embeddings=True).astype(np.float32)

    scores, indices = _index.search(query_embedding, FAISS_TOP_K)

    retrieved = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        entry = _metadata[idx].copy()
        entry["relevance_score"] = float(score)
        retrieved.append(entry)

    logger.info("Retrieved %d posts for query: %s", len(retrieved), query[:80])
    return {**state, "retrieved_posts": retrieved}
