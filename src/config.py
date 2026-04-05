"""
Configuration for LinkedIn Auto Poster.
All settings are read from environment variables.
"""

import os
import pathlib

# --- LinkedIn API ---
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN", "")

# LinkedIn API base URL
LINKEDIN_API_BASE = "https://api.linkedin.com"

# --- RSS Feeds (Tech News Sources) ---
RSS_FEEDS = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "tag": "TechCrunch"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "tag": "TheVerge"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "tag": "ArsTechnica"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss", "tag": "Wired"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "tag": "MITTechReview"},
    {"name": "Hacker News (Best)", "url": "https://hnrss.org/best", "tag": "HackerNews"},
    {"name": "TechRadar", "url": "https://www.techradar.com/rss", "tag": "TechRadar"},
    {"name": "Engadget", "url": "https://www.engadget.com/rss.xml", "tag": "Engadget"},
]

# --- Paths ---
DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
POSTED_ARTICLES_FILE = DATA_DIR / "posted_articles.json"

# Max articles to remember
MAX_POSTED_HISTORY = 500