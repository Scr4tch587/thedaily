import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LOG_DIR = PROJECT_ROOT / "logs"

for d in (RAW_DIR, PROCESSED_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Hacker News (Algolia API) ─────────────────────────────────────────
HN_ALGOLIA_BASE = "https://hn.algolia.com/api/v1"
HN_ITEM_URL = "https://news.ycombinator.com/item?id={}"
HN_FRONT_PAGE_HITS = 200       # number of front-page stories to fetch
HN_SEARCH_HITS_PER_QUERY = 50  # hits per topic search
HN_TOP_COMMENTS = 5            # top comments to keep per story
MIN_SCORE = 10                 # filter threshold for cleaning

# Topic queries — fetched via Algolia search to broaden beyond front page
HN_TOPIC_QUERIES = [
    "machine learning",
    "artificial intelligence",
    "programming language",
    "open source",
    "startup",
]

# ── OpenAI ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

# ── Embeddings ─────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# ── FAISS ──────────────────────────────────────────────────────────────
FAISS_INDEX_PATH = PROCESSED_DIR / "faiss.index"
FAISS_TOP_K = 8

# ── Pipeline outputs ──────────────────────────────────────────────────
SUMMARIES_PATH = PROCESSED_DIR / "summaries.json"
CHARTS_DATA_PATH = PROCESSED_DIR / "charts_data.json"
DAILY_DIGEST_PATH = PROCESSED_DIR / "daily_digest.json"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"

# ── Topic classification keywords ─────────────────────────────────────
TOPIC_KEYWORDS = {
    "AI/ML": ["ai", "machine learning", "deep learning", "neural", "llm", "gpt", "transformer", "diffusion", "generative"],
    "Web Development": ["javascript", "react", "vue", "angular", "frontend", "backend", "web", "css", "html", "node"],
    "Cloud/Infra": ["aws", "cloud", "docker", "kubernetes", "devops", "terraform", "ci/cd", "infrastructure"],
    "Security": ["security", "vulnerability", "exploit", "encryption", "privacy", "hack", "breach", "zero-day"],
    "Programming Languages": ["rust", "python", "golang", "java", "typescript", "compiler", "language"],
    "Data/Analytics": ["data", "analytics", "database", "sql", "spark", "pipeline", "etl", "warehouse"],
    "Open Source": ["open source", "oss", "github", "repository", "fork", "release", "license"],
    "Hardware/Chips": ["chip", "gpu", "cpu", "hardware", "semiconductor", "nvidia", "amd", "intel", "quantum"],
    "Startups": ["startup", "funding", "yc", "seed", "series a", "acquisition", "ipo", "valuation"],
}

BREAKTHROUGH_SCORE_THRESHOLD = 300  # HN stories above this score flagged as breakthroughs
