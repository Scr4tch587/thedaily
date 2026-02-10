Got it — you want something you can **paste directly into Claude Code (or another coding agent)** so it can plan the entire project end-to-end with full context, constraints, architecture, and intent.
I’ll write this as a **clear project spec + planning brief** (not implementation code), so the agent can:

* design architecture
* propose folder structure
* suggest tasks
* identify edge cases
* plan build order

This will assume:

* EC2-hosted single-instance system
* daily batch processing
* Reddit scraping focus
* Streamlit chatbot frontend
* LangGraph orchestration
* light distributed computing (Ray)
* practical daily-use project (not resume polish).

---

# 📌 PROJECT PLANNING DOCUMENT — TECH NEWS REDDIT CHATBOT

## Project Title

**Tech Breakthrough Radar Chatbot**

---

# 1. Project Overview

This project is a personal-use chatbot that provides daily summaries of important technology news and breakthroughs extracted from Reddit.

The system:

* scrapes Reddit once per day (scheduled batch job)
* processes and summarizes posts using distributed computing
* stores processed insights locally on an AWS EC2 instance
* serves a Streamlit chatbot interface that responds instantly using preprocessed data.

The goal is:

* reduce daily tech news information overload
* practice data pipelines, scraping, distributed processing, and LLM orchestration
* build something genuinely useful day-to-day.

This is **NOT a production SaaS system**. Simplicity, reliability, and learning value are prioritized over scalability.

---

# 2. Core Constraints (Important)

## Infrastructure

* Everything runs on ONE AWS EC2 instance.
* No S3, no Lambda, no external DB initially.
* Use local disk storage only (EBS-backed EC2 volume).

---

## Data Processing Model

Batch pipeline:

* runs daily at 12:00 PM via cron
* scraping + processing takes < 1 hour
* chatbot always uses precomputed data.

No live scraping during user chat.

---

## Frontend Requirement

Must use:

* Streamlit.

No React/Next/etc.

---

## Agent Framework Requirement

Must use:

* LangGraph.

But keep agent complexity minimal.

---

## Distributed Computing Requirement

Use:

* Ray (local multi-core parallelism).

Not Kubernetes/Spark clusters.

---

## Data Source

Primary:

* Reddit only.

Specifically tech/news communities.

---

# 3. Target User Experience

User opens Streamlit app anytime during day.

Typical interaction:

* “What happened in AI recently?”
* “Explain major tech breakthroughs this week.”
* “Any new tools trending?”
* “Give me a 5-minute tech rundown.”

Response should be:

* immediate (no waiting for scraping)
* based on latest daily snapshot.

---

# 4. Reddit Scraping Details

## Use PRAW (Python Reddit API Wrapper)

Reasons:

* official API wrapper
* avoids HTML scraping fragility
* respects Reddit rate limits.

---

## Subreddits to scrape initially

Start with:

* r/MachineLearning
* r/programming
* r/datascience
* r/artificial
* r/technology.

Agent should allow easy expansion later.

---

## Data to collect per post

Minimum:

* title
* post body/selftext
* top comments (limit ~5–10)
* score/upvotes
* timestamp
* permalink
* subreddit.

Avoid scraping entire comment trees initially.

---

# 5. Data Storage Strategy (Local EC2 Disk)

## Directory structure suggestion

```
project_root/

data/
  raw/
    YYYY-MM-DD_reddit.json

  processed/
    summaries.json
    embeddings.parquet

logs/
models/
```

---

## Storage principles

* raw data immutable snapshots
* processed data overwritten daily
* logs retained for debugging.

---

# 6. Processing Pipeline (Daily Batch Job)

## Step-by-step pipeline

### Step 1 — Scraping

Fetch posts/comments from target subreddits.

Save raw JSON snapshot.

---

### Step 2 — Cleaning

Remove:

* deleted posts
* low-score noise
* duplicates.

Normalize text fields.

---

### Step 3 — Distributed NLP Processing (Ray)

Parallelize:

* summarization
* embedding generation
* topic classification.

Ray runs locally across CPU cores.

No cluster required.

---

### Step 4 — Insight Extraction

Generate:

* daily summaries
* trending topics
* “breakthrough candidates.”

Save processed outputs.

---

# 7. LangGraph Agent Design

Keep minimal:

## Agent 1 — Retrieval Agent

Responsibilities:

* load processed data
* select relevant posts based on query.

---

## Agent 2 — Synthesis Agent

Responsibilities:

* summarize multiple posts
* extract coherent insights.

---

## Agent 3 — Chat Response Agent

Responsibilities:

* generate final conversational response.

---

Avoid:

* autonomous loops
* recursive agents
* planner agents.

Keep simple.

---

# 8. Streamlit Frontend Design

## Core Features

### Chat Interface

Main feature:

* user question input
* conversational response.

---

### Optional Sidebar

Daily digest:

* top breakthroughs
* quick summary bullets.

---

### Performance Goals

* instant responses
* minimal loading delays.

---

# 9. Deployment on AWS EC2

## EC2 Recommendations

Minimum:

* 2–4 vCPU
* 8–16 GB RAM
* Ubuntu Linux.

---

## Services Running on EC2

Two main processes:

### 1. Pipeline job

Scheduled via cron:

```
0 12 * * * python run_pipeline.py
```

---

### 2. Streamlit server

Runs continuously:

```
streamlit run app.py
```

---

# 10. Monitoring & Reliability

## Logging

Log:

* scraping success/failure
* processing duration
* API errors.

---

## Failure handling

If pipeline fails:

* chatbot uses previous day’s data
* log failure clearly.

---

## Optional backup

Enable EBS snapshots periodically.

---

# 11. Security Considerations

* Store Reddit API keys in environment variables
* Never hardcode credentials
* Restrict EC2 security group access.

---

# 12. Visualization

- Tech trends should be explained with lots of graphs and dashboards and stats, not just words

---

# 13. Explicit Non-Goals

To prevent overengineering:

* no real-time scraping
* no distributed cloud clusters
* no microservices
* no production-grade scaling
* no advanced agent autonomy.

---

# 14. Expected Deliverables (From Planning Agent)

Claude Code should produce:

1. Full architecture plan
2. Suggested folder structure
3. Implementation task breakdown
4. Pipeline pseudocode
5. Agent graph design
6. Deployment steps

---
