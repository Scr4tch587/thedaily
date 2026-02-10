"""Synthesis node — summarize retrieved stories into a coherent briefing."""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


def synthesize(state: dict) -> dict:
    """Take retrieved stories and produce a coherent synthesis via OpenAI."""
    retrieved = state.get("retrieved_posts", [])
    query = state["query"]

    if not retrieved:
        return {**state, "synthesis": "No relevant stories found for your query."}

    # Build context from retrieved stories
    context_parts = []
    for i, post in enumerate(retrieved, 1):
        topics_str = ", ".join(post.get("topics", []))
        comments = post.get("num_comments", 0)
        context_parts.append(
            f"[{i}] HN (score: {post['score']}, comments: {comments}, topics: {topics_str})\n"
            f"Title: {post['title']}\n"
            f"Summary: {post['summary']}\n"
        )

    context = "\n".join(context_parts)

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.4)

    messages = [
        SystemMessage(content=(
            "You are a tech news analyst. Given a set of Hacker News stories and their summaries, "
            "synthesize them into a clear, informative briefing that answers the user's query. "
            "Highlight key trends, breakthroughs, and notable discussions. "
            "Reference specific stories by number [1], [2], etc. Be concise but thorough."
        )),
        HumanMessage(content=f"User query: {query}\n\nRelevant stories:\n{context}"),
    ]

    response = llm.invoke(messages)
    synthesis = response.content

    logger.info("Synthesized %d stories into briefing (%d chars)", len(retrieved), len(synthesis))
    return {**state, "synthesis": synthesis}
