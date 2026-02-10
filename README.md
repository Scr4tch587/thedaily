# The Daily Tech Radar

A daily AI-powered tech news assistant that curates Hacker News, builds a searchable knowledge base, and serves a conversational Streamlit chat interface.

## What This Project Does

`The Daily` runs a daily pipeline that:

1. Scrapes fresh stories from Hacker News (front page + topic queries).
2. Cleans and deduplicates story data.
3. Generates concise summaries and vector embeddings.
4. Builds a FAISS index for semantic retrieval.
5. Produces digest + chart artifacts for the UI.

At runtime, users ask questions in chat, and the app retrieves relevant stories from the FAISS index, injects them into context, and generates a grounded response with source links.

This is an **offline-indexed RAG system**: data is refreshed daily, and chat answers are based on precomputed artifacts.

## How To View It / Run It

## Live

- **EC2 app**: your Streamlit runtime URL (or domain)
- **GitHub Pages**: static landing page that links/redirects to the live app

## Local Development

Requirements:

- Python `3.11+`
- OpenAI API key in `.env`

Setup:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Configure `.env`:

```bash
OPENAI_API_KEY=your_key_here
```

Run the daily pipeline once:

```bash
python run_pipeline.py
```

Start the app:

```bash
streamlit run app.py
```

## EC2 Deployment

- Bootstrap script: `/deploy/ec2/bootstrap_ec2.sh`
- Streamlit service: `/deploy/ec2/thedaily-streamlit.service`
- Daily pipeline timer: `/deploy/ec2/thedaily-pipeline.timer`
- Full steps: `/DEPLOYMENT.md`

## How It Works (Architecture)

## 1) Daily Data Pipeline

Entry point: `/run_pipeline.py`

Pipeline stages:

1. **Scrape** (`/scraper/hn_scraper.py`)
2. **Clean** (`/pipeline/cleaner.py`)
3. **Process** (`/pipeline/processor.py`)
4. **Index** (`/pipeline/index_builder.py`)
5. **Insights** (`/pipeline/insights.py`)

Outputs (in `/data/processed`):

- `faiss.index`
- `summaries.json`
- `embeddings.npy`
- `charts_data.json`
- `daily_digest.json`

## 2) Chat Agent Flow (LangGraph)

Entry point: `/agents/graph.py`

Graph:

1. `retrieve` (`/agents/retrieval.py`)
2. `respond` via `synthesize_and_respond` (`/agents/synthesis.py`)

State keys:

- `query`
- `chat_history`
- `retrieved_posts`
- `response`

The graph is linear (`retrieve -> respond -> END`) and keeps orchestration explicit and extensible.

## 3) Frontend

Entry point: `/app.py`

- Chat UI: `/ui/chat.py`
- Charts UI: `/ui/charts.py`

The UI reads precomputed artifacts for fast rendering and invokes the LangGraph agent for conversational responses.

## Operational Notes

- Daily refresh is managed by `systemd` timer on EC2.
- CI/CD workflow deploys EC2 updates and GitHub Pages:
  - `/.github/workflows/deploy-pages.yml`
- If pipeline artifacts are missing, chat will fail gracefully and prompt you to run the pipeline.
