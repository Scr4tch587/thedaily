"""Streamlit sidebar — NYT-styled daily digest display."""

import json
import logging

import streamlit as st

from config.settings import DAILY_DIGEST_PATH

logger = logging.getLogger(__name__)


def render_sidebar():
    """Render the daily digest in a newspaper sidebar style."""

    # Sidebar masthead
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 0.5rem 0; border-bottom: 2px solid #000; margin-bottom: 0.8rem;">
        <div style="font-family: 'Libre Franklin', sans-serif; font-size: 0.6rem; font-weight: 600;
                     text-transform: uppercase; letter-spacing: 2px; color: #666;">Today's Edition</div>
        <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.3rem; font-weight: 900;
                     color: #000; margin: 0.15rem 0;">The Daily Digest</div>
    </div>
    """, unsafe_allow_html=True)

    if not DAILY_DIGEST_PATH.exists():
        st.sidebar.markdown("""
        <p class="summary-text" style="text-align: center; color: #999; font-style: italic;">
            No edition available yet.<br>Run the pipeline to generate today's digest.
        </p>
        """, unsafe_allow_html=True)
        return

    try:
        with open(DAILY_DIGEST_PATH) as f:
            digest = json.load(f)
    except (json.JSONDecodeError, OSError):
        st.sidebar.error("Failed to load daily digest.")
        return

    # Date & stats bar
    date_str = digest.get("date", "N/A")
    total = digest.get("total_posts", 0)
    st.sidebar.markdown(f"""
    <div style="display: flex; justify-content: space-between; padding: 0.2rem 0;
                border-bottom: 1px solid #E0E0E0; margin-bottom: 0.6rem;">
        <span class="meta-text">{date_str}</span>
        <span class="meta-text">{total} stories analyzed</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Breakthroughs ──
    breakthroughs = digest.get("breakthroughs", [])
    if breakthroughs:
        st.sidebar.markdown("""
        <div class="section-label" style="border-bottom: 1px solid #000; padding-bottom: 0.15rem;">
            Breaking Through
        </div>
        """, unsafe_allow_html=True)

        for bt in breakthroughs[:5]:
            score = bt.get("score", 0)
            comments = bt.get("num_comments", 0)
            hn_url = bt.get("hn_url", "")
            title = bt["title"][:90]
            summary = bt.get("summary", "")[:160]

            st.sidebar.markdown(f"""
            <div style="padding: 0.4rem 0; border-bottom: 1px solid #F0F0F0;">
                <div class="headline-sm">
                    <a href="{hn_url}" target="_blank"
                       style="color: #121212 !important;">{title}</a>
                </div>
                <p class="summary-text" style="font-size: 0.8rem; margin: 0.1rem 0;">{summary}</p>
                <span class="meta-text">{score} pts&ensp;&middot;&ensp;{comments} comments</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Trending Topics ──
    trending = digest.get("trending_topics", {})
    if trending:
        st.sidebar.markdown("""
        <div class="section-label" style="border-bottom: 1px solid #000; padding-bottom: 0.15rem; margin-top: 0.8rem;">
            Trending Topics
        </div>
        """, unsafe_allow_html=True)

        for topic, data in list(trending.items())[:8]:
            count = data.get("count", 0)
            avg = data.get("avg_score", 0)
            bar_width = min(count * 12, 100)
            st.sidebar.markdown(f"""
            <div style="padding: 0.25rem 0; border-bottom: 1px solid #F5F5F5;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-family: 'Libre Franklin', sans-serif; font-size: 0.78rem;
                                 font-weight: 500; color: #121212;">{topic}</span>
                    <span class="meta-text">{count} stories</span>
                </div>
                <div style="background: #F0F0F0; height: 3px; margin-top: 3px; border-radius: 1px;">
                    <div style="background: #121212; height: 3px; width: {bar_width}%; border-radius: 1px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Top Stories ──
    top_posts = digest.get("top_posts", [])
    if top_posts:
        st.sidebar.markdown("""
        <div class="section-label" style="border-bottom: 1px solid #000; padding-bottom: 0.15rem; margin-top: 0.8rem;">
            Most Upvoted
        </div>
        """, unsafe_allow_html=True)

        for i, post in enumerate(top_posts[:5], 1):
            title = post["title"][:75]
            hn_url = post.get("hn_url", "")
            score = post.get("score", 0)
            comments = post.get("num_comments", 0)

            st.sidebar.markdown(f"""
            <div style="padding: 0.3rem 0; border-bottom: 1px solid #F0F0F0; display: flex; gap: 0.5rem;">
                <span style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem;
                             font-weight: 300; color: #CCC; line-height: 1;">{i}</span>
                <div>
                    <a href="{hn_url}" target="_blank"
                       style="font-family: 'Libre Franklin', sans-serif; font-size: 0.78rem;
                              font-weight: 500; color: #121212 !important; line-height: 1.3;
                              text-decoration: none !important;">{title}</a>
                    <div class="meta-text" style="margin-top: 2px;">{score} pts&ensp;&middot;&ensp;{comments} comments</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
