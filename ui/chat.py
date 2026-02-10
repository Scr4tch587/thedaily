"""Streamlit chat component — dual input: new conversation + follow-up with memory."""

import streamlit as st

from agents.graph import query_agent


def _handle_query(prompt: str, with_history: bool = False):
    """Send a query to the agent and update session state."""
    history = st.session_state.messages if with_history else []

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Consulting today's briefing..."):
        try:
            response = query_agent(prompt, chat_history=history)
        except Exception as e:
            response = (
                f"**Unable to retrieve briefing.** {e}\n\n"
                "Ensure the pipeline has run at least once and API keys are configured."
            )

    st.session_state.messages.append({"role": "assistant", "content": response})


def render_chat():
    """Render the chat interface with new-conversation and follow-up inputs."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    has_history = len(st.session_state.messages) > 0

    # ── New conversation input (always visible at top) ──
    if has_history:
        new_topic = st.chat_input("Start a new topic...", key="new_conversation")
        if new_topic:
            st.session_state.messages = []  # clear history
            _handle_query(new_topic, with_history=False)
            st.rerun()
    else:
        st.markdown("""
        <div class="headline-lg">What's happening in tech?</div>
        <p class="summary-text">
            Ask about today's trends, AI developments,
            or anything from the latest discussions on Hacker News.
        </p>
        """, unsafe_allow_html=True)

        first_query = st.chat_input("Ask about today's tech news...", key="first_message")
        if first_query:
            _handle_query(first_query, with_history=False)
            st.rerun()

    # ── Display message history ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Follow-up input (only when there's history) ──
    if has_history:
        followup = st.chat_input("Follow up on this conversation...", key="followup")
        if followup:
            _handle_query(followup, with_history=True)
            st.rerun()
