"""Response node — format the final conversational answer."""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


def respond(state: dict) -> dict:
    """Format synthesis into a conversational chat response."""
    synthesis = state.get("synthesis", "")
    query = state["query"]
    retrieved = state.get("retrieved_posts", [])

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.6)

    # Build source links
    sources = []
    for post in retrieved[:5]:
        title_short = post["title"][:60]
        hn_url = post.get("hn_url", "")
        score = post.get("score", 0)
        comments = post.get("num_comments", 0)
        sources.append(f"- [{title_short}]({hn_url}) ({score} pts, {comments} comments)")
    sources_text = "\n".join(sources) if sources else "No sources available."

    messages = [
        SystemMessage(content=(
            "You are a friendly, knowledgeable tech news assistant called 'The Daily'. "
            "Based on the synthesis provided, give a natural conversational response. "
            "Keep it informative but accessible. Use markdown formatting. "
            "End with a brief 'Sources' section listing the most relevant Hacker News stories."
        )),
        HumanMessage(content=(
            f"User asked: {query}\n\n"
            f"Synthesis:\n{synthesis}\n\n"
            f"Available sources:\n{sources_text}"
        )),
    ]

    response = llm.invoke(messages)
    logger.info("Generated response (%d chars)", len(response.content))
    return {**state, "response": response.content}
