"""Synthesis + response node — single LLM call to produce the final answer."""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config.settings import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


def synthesize_and_respond(state: dict) -> dict:
    """Synthesize retrieved posts and produce the final response in one LLM call."""
    retrieved = state.get("retrieved_posts", [])
    query = state["query"]
    chat_history = state.get("chat_history", [])

    if not retrieved:
        return {**state, "response": "I couldn't find any relevant stories for that query. Try rephrasing or asking about a different topic."}

    # Build context from retrieved stories
    context_parts = []
    source_links = []
    for i, post in enumerate(retrieved, 1):
        topics_str = ", ".join(post.get("topics", []))
        comments = post.get("num_comments", 0)
        context_parts.append(
            f"[{i}] (score: {post['score']}, comments: {comments}, topics: {topics_str})\n"
            f"Title: {post['title']}\n"
            f"Summary: {post['summary']}"
        )
        if i <= 5:
            title_short = post["title"][:60]
            hn_url = post.get("hn_url", "")
            source_links.append(f"- [{title_short}]({hn_url}) ({post['score']} pts, {comments} comments)")

    context = "\n\n".join(context_parts)
    sources_text = "\n".join(source_links)

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.5)

    messages = [
        SystemMessage(content=(
            "You are 'The Daily', a friendly and knowledgeable tech news assistant. "
            "Given Hacker News stories and their summaries, provide a clear, conversational answer "
            "to the user's question. Highlight key trends and insights. Use markdown formatting. "
            "End with a brief 'Sources' section listing the relevant HN stories. "
            "Use the conversation history to understand follow-up questions."
        )),
    ]

    # Inject conversation history
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=(
        f"{query}\n\n"
        f"--- Relevant stories from today ---\n{context}\n\n"
        f"--- Sources ---\n{sources_text}"
    )))

    response = llm.invoke(messages)
    logger.info("Generated response (%d chars)", len(response.content))
    return {**state, "response": response.content}
