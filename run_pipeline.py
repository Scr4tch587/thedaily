"""Daily batch pipeline entry point — scrape HN, clean, process, index, digest."""

import logging
import sys
from datetime import datetime, timezone

import ray

from config.settings import LOG_DIR

# ── Logging setup ──────────────────────────────────────────────────────
log_file = LOG_DIR / f"pipeline_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("pipeline")


def main() -> None:
    logger.info("═══ Pipeline starting ═══")

    # 1. Initialize Ray
    ray.init(ignore_reinit_error=True)
    logger.info("Ray initialized with %d CPUs", int(ray.cluster_resources().get("CPU", 0)))

    try:
        # 2. Scrape Hacker News
        from scraper.hn_scraper import scrape_all

        logger.info("Step 1/6: Scraping Hacker News...")
        raw_posts = scrape_all()
        if not raw_posts:
            logger.warning("No stories scraped — aborting pipeline")
            return

        # 3. Clean raw data
        from pipeline.cleaner import clean_posts

        logger.info("Step 2/6: Cleaning data...")
        posts = clean_posts(raw_posts)
        if not posts:
            logger.warning("No stories survived cleaning — aborting pipeline")
            return

        # 4. Ray parallel processing
        from pipeline.processor import process_posts

        logger.info("Step 3/6: Processing stories with Ray (%d stories)...", len(posts))
        summaries, embeddings, topics = process_posts(posts)

        # 5. Build FAISS index
        from pipeline.index_builder import build_faiss_index

        logger.info("Step 4/6: Building FAISS index...")
        build_faiss_index(posts, summaries, embeddings, topics)

        # 6. Generate insights & charts
        from pipeline.insights import (
            detect_breakthroughs,
            extract_trending_topics,
            generate_charts_data,
            generate_daily_digest,
        )

        logger.info("Step 5/6: Generating charts data...")
        generate_charts_data(posts, topics)

        logger.info("Step 6/6: Generating daily digest...")
        trending = extract_trending_topics(posts, topics)
        breakthroughs = detect_breakthroughs(posts, summaries, topics)
        generate_daily_digest(posts, summaries, topics, breakthroughs, trending)

        logger.info("═══ Pipeline completed successfully ═══")

    except Exception:
        logger.exception("Pipeline failed")
        sys.exit(1)
    finally:
        ray.shutdown()


if __name__ == "__main__":
    main()
