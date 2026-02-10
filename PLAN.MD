Tech Breakthrough Radar Chatbot — Implementation Plan                                                                                                   │
│                                                                                                                                                         │
│ Context                                                                                                                                                 │
│                                                                                                                                                         │
│ Build a personal-use chatbot that scrapes Reddit daily for tech news, processes it with Ray, stores insights locally, and serves a Streamlit chat       │
│ interface powered by LangGraph agents. Hybrid LLM approach: local sentence-transformers for embeddings + OpenAI API for summarization/chat. Single EC2  │
│ instance, no external services.                                                                                                                         │
│                                                                                                                                                         │
│ ---                                                                                                                                                     │
│ 1. Project Structure                                                                                                                                    │
│                                                                                                                                                         │
│ thedaily/                                                                                                                                               │
│ ├── .env.example              # Template for env vars                                                                                                   │
│ ├── .gitignore                                                                                                                                          │
│ ├── pyproject.toml             # Dependencies (uv/pip)                                                                                                  │
│ ├── README.md                                                                                                                                           │
│ ├── run_pipeline.py            # Entry point for daily batch job                                                                                        │
│ ├── app.py                     # Streamlit entry point                                                                                                  │
│ │                                                                                                                                                       │
│ ├── config/                                                                                                                                             │
│ │   └── settings.py            # Central config (subreddits, paths, thresholds)                                                                         │
│ │                                                                                                                                                       │
│ ├── scraper/                                                                                                                                            │
│ │   ├── __init__.py                                                                                                                                     │
│ │   └── reddit_scraper.py      # PRAW-based Reddit scraping                                                                                             │
│ │                                                                                                                                                       │
│ ├── pipeline/                                                                                                                                           │
│ │   ├── __init__.py                                                                                                                                     │
│ │   ├── cleaner.py             # Data cleaning & dedup                                                                                                  │
│ │   ├── processor.py           # Ray-parallel NLP (summarize, embed, classify)                                                                          │
│ │   ├── insights.py            # Daily summaries, trending topics, breakthroughs                                                                        │
│ │   └── index_builder.py       # FAISS index creation                                                                                                   │
│ │                                                                                                                                                       │
│ ├── agents/                                                                                                                                             │
│ │   ├── __init__.py                                                                                                                                     │
│ │   ├── graph.py               # LangGraph agent graph definition                                                                                       │
│ │   ├── retrieval.py           # Retrieval node (FAISS query)                                                                                           │
│ │   ├── synthesis.py           # Synthesis node (summarize results)                                                                                     │
│ │   └── responder.py           # Chat response node                                                                                                     │
│ │                                                                                                                                                       │
│ ├── ui/                                                                                                                                                 │
│ │   ├── __init__.py                                                                                                                                     │
│ │   ├── chat.py                # Streamlit chat component                                                                                               │
│ │   ├── sidebar.py             # Daily digest sidebar                                                                                                   │
│ │   └── charts.py              # Precomputed visualization rendering                                                                                    │
│ │                                                                                                                                                       │
│ ├── data/                      # .gitignored                                                                                                            │
│ │   ├── raw/                   # YYYY-MM-DD_reddit.json                                                                                                 │
│ │   └── processed/             # summaries.json, embeddings.npy, faiss.index, charts_data.json                                                          │
│ │                                                                                                                                                       │
│ └── logs/                      # .gitignored                                                                                                            │
│                                                                                                                                                         │
│ 2. Key Dependencies                                                                                                                                     │
│                                                                                                                                                         │
│ praw                  # Reddit API                                                                                                                      │
│ ray                   # Local parallel processing                                                                                                       │
│ langchain-openai      # OpenAI LLM integration                                                                                                          │
│ langgraph             # Agent orchestration                                                                                                             │
│ faiss-cpu             # Vector similarity search                                                                                                        │
│ sentence-transformers # Local embeddings                                                                                                                │
│ streamlit             # Frontend                                                                                                                        │
│ plotly                # Charts/visualizations                                                                                                           │
│ pandas                # Data manipulation                                                                                                               │
│ python-dotenv         # Env var loading                                                                                                                 │
│ numpy                 # Array ops                                                                                                                       │
│                                                                                                                                                         │
│ 3. Build Order (Implementation Tasks)                                                                                                                   │
│                                                                                                                                                         │
│ Phase 1: Foundation                                                                                                                                     │
│                                                                                                                                                         │
│ 1. Project setup — pyproject.toml, .env.example, config/settings.py, directory scaffolding                                                              │
│ 2. Reddit scraper — PRAW client, fetch posts+comments from 5 subreddits, save raw JSON                                                                  │
│                                                                                                                                                         │
│ Phase 2: Pipeline                                                                                                                                       │
│                                                                                                                                                         │
│ 3. Data cleaner — Remove deleted/low-score posts, dedup by permalink, normalize text                                                                    │
│ 4. Ray processor — Parallel summarization (OpenAI), embedding generation (sentence-transformers), topic classification (keyword/LLM-based)              │
│ 5. Insight extraction — Daily summary, trending topics (by frequency + score), breakthrough detection                                                   │
│ 6. FAISS index builder — Build index from embeddings, save to disk                                                                                      │
│ 7. Pipeline orchestrator — run_pipeline.py wiring all steps together                                                                                    │
│                                                                                                                                                         │
│ Phase 3: Agent                                                                                                                                          │
│                                                                                                                                                         │
│ 8. Retrieval node — Load FAISS index, embed query, return top-K relevant posts                                                                          │
│ 9. Synthesis node — Take retrieved posts, produce coherent summary via OpenAI                                                                           │
│ 10. Response node — Format final conversational answer                                                                                                  │
│ 11. LangGraph graph — Wire nodes: retrieve → synthesize → respond                                                                                       │
│                                                                                                                                                         │
│ Phase 4: Frontend                                                                                                                                       │
│                                                                                                                                                         │
│ 12. Streamlit chat interface — Chat input, message history, agent integration                                                                           │
│ 13. Sidebar daily digest — Top breakthroughs, summary bullets from precomputed data                                                                     │
│ 14. Charts/visualizations — Trending topics bar chart, subreddit activity, score distribution, topic trends over time (Plotly)                          │
│                                                                                                                                                         │
│ Phase 5: Integration & Deployment                                                                                                                       │
│                                                                                                                                                         │
│ 15. End-to-end integration test — Run pipeline, then chat queries                                                                                       │
│ 16. Deployment config — Cron setup, systemd for Streamlit, EC2 instructions                                                                             │
│                                                                                                                                                         │
│ 4. Pipeline Flow (run_pipeline.py)                                                                                                                      │
│                                                                                                                                                         │
│ 1. Initialize Ray (local, num_cpus=auto)                                                                                                                │
│ 2. Scrape Reddit → data/raw/YYYY-MM-DD_reddit.json                                                                                                      │
│ 3. Clean raw data → filtered posts list                                                                                                                 │
│ 4. Ray parallel processing:                                                                                                                             │
│    - @ray.remote summarize_batch(posts) → summaries (OpenAI)                                                                                            │
│    - @ray.remote embed_batch(posts) → embeddings (sentence-transformers)                                                                                │
│    - @ray.remote classify_batch(posts) → topic labels                                                                                                   │
│ 5. Merge results → data/processed/summaries.json                                                                                                        │
│ 6. Build FAISS index → data/processed/faiss.index                                                                                                       │
│ 7. Generate chart data → data/processed/charts_data.json                                                                                                │
│ 8. Generate daily digest → data/processed/daily_digest.json                                                                                             │
│ 9. Shutdown Ray                                                                                                                                         │
│ 10. Log completion                                                                                                                                      │
│                                                                                                                                                         │
│ 5. LangGraph Agent Design                                                                                                                               │
│                                                                                                                                                         │
│ [User Query]                                                                                                                                            │
│      │                                                                                                                                                  │
│      ▼                                                                                                                                                  │
│ ┌─────────┐    top-K posts    ┌───────────┐    summary    ┌───────────┐                                                                                 │
│ │ Retrieve │ ───────────────► │ Synthesize │ ────────────► │  Respond  │                                                                                │
│ │  (FAISS) │                  │  (OpenAI)  │              │  (OpenAI) │                                                                                 │
│ └─────────┘                  └───────────┘              └───────────┘                                                                                   │
│                                                               │                                                                                         │
│                                                               ▼                                                                                         │
│                                                       [Chat Response]                                                                                   │
│                                                                                                                                                         │
│ - State: { query, retrieved_posts, synthesis, response }                                                                                                │
│ - Linear graph: no loops, no conditional branching                                                                                                      │
│ - Each node reads from state and writes its output key                                                                                                  │
│                                                                                                                                                         │
│ 6. Visualization (Precomputed)                                                                                                                          │
│                                                                                                                                                         │
│ Pipeline generates charts_data.json containing:                                                                                                         │
│ - trending_topics: topic → post count + avg score                                                                                                       │
│ - subreddit_activity: subreddit → post count per day                                                                                                    │
│ - score_distribution: histogram buckets                                                                                                                 │
│ - topic_trend: topic → count over last 7 days                                                                                                           │
│                                                                                                                                                         │
│ Streamlit renders these with Plotly (bar charts, line charts, histograms).                                                                              │
│                                                                                                                                                         │
│ 7. Environment Variables                                                                                                                                │
│                                                                                                                                                         │
│ REDDIT_CLIENT_ID=                                                                                                                                       │
│ REDDIT_CLIENT_SECRET=                                                                                                                                   │
│ REDDIT_USER_AGENT=                                                                                                                                      │
│ OPENAI_API_KEY=                                                                                                                                         │
│                                                                                                                                                         │
│ 8. EC2 Deployment                                                                                                                                       │
│                                                                                                                                                         │
│ 1. Ubuntu EC2 (t3.medium or larger, 4GB+ RAM)                                                                                                           │
│ 2. Install Python 3.11+, pip, uv                                                                                                                        │
│ 3. Clone repo, install deps                                                                                                                             │
│ 4. Set env vars in /etc/environment or .env                                                                                                             │
│ 5. Cron: 0 12 * * * cd /home/ubuntu/thedaily && python run_pipeline.py >> logs/pipeline.log 2>&1                                                        │
│ 6. Streamlit: systemd service running streamlit run app.py --server.port 8501                                                                           │
│ 7. Security group: allow inbound 8501 (or 80 with nginx proxy)                                                                                          │
│                                                                                                                                                         │
│ 9. Verification                                                                                                                                         │
│                                                                                                                                                         │
│ - Scraper: Run scraper, verify raw JSON contains expected fields                                                                                        │
│ - Pipeline: Run full pipeline, check all output files exist and are valid                                                                               │
│ - FAISS: Query with sample text, verify relevant results returned                                                                                       │
│ - Agent: Send test queries through LangGraph, verify coherent responses                                                                                 │
│ - Streamlit: Launch app, test chat + sidebar + charts render correctly                                                                                  │
│ - Failure mode: Delete processed data, verify chatbot falls back to previous day's data 