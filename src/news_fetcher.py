"""
Fetches tech news from RSS feeds.
No API keys required - pure RSS scraping.
"""

import json
import random
import re
import time
import feedparser
import requests
from config import RSS_FEEDS, POSTED_ARTICLES_FILE, MAX_POSTED_HISTORY


def load_posted_articles():
    """Load the list of already-posted article URLs."""
    try:
        with open(POSTED_ARTICLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_posted_articles(posted):
    """Save the posted articles list, trimming to max history."""
    posted = posted[-MAX_POSTED_HISTORY:]
    with open(POSTED_ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(posted, f, indent=2, ensure_ascii=False)


def extract_image_from_entry(entry):
    """Try to extract an image URL from an RSS entry."""
    # Check media_content
    if hasattr(entry, "media_content") and entry.media_content:
        for media in entry.media_content:
            if "url" in media and ("image" in media.get("type", "image")):
                return media["url"]

    # Check media_thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if "url" in thumb:
                return thumb["url"]

    # Check enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if "image" in enc.get("type", ""):
                return enc.get("href", enc.get("url", ""))

    # Try to find image in summary/content HTML
    content_html = ""
    if hasattr(entry, "summary"):
        content_html = entry.summary
    if hasattr(entry, "content") and entry.content:
        content_html = entry.content[0].get("value", content_html)

    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html)
    if img_match:
        url = img_match.group(1)
        # Filter out tiny tracking pixels
        if "1x1" not in url and "pixel" not in url.lower():
            return url

    return None


def clean_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    # Decode HTML entities
    import html
    clean = html.unescape(clean)
    return clean


def fetch_articles_from_feed(feed_info):
    """Fetch articles from a single RSS feed."""
    articles = []
    try:
        feed = feedparser.parse(
            feed_info["url"],
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        if feed.bozo and not feed.entries:
            print(f"  [!] Error parsing {feed_info['name']}: {feed.bozo_exception}")
            return []

        for entry in feed.entries[:15]:  # Take top 15 from each feed
            title = clean_html(getattr(entry, "title", ""))
            description = clean_html(
                getattr(entry, "summary", getattr(entry, "description", ""))
            )
            link = getattr(entry, "link", "")
            image_url = extract_image_from_entry(entry)

            if not title or not link:
                continue

            # Trim description to 250 chars
            if len(description) > 250:
                description = description[:247] + "..."

            articles.append({
                "title": title,
                "description": description,
                "url": link,
                "image_url": image_url,
                "source": feed_info["name"],
                "source_tag": feed_info["tag"],
            })

    except Exception as e:
        print(f"  [!] Failed to fetch {feed_info['name']}: {e}")

    return articles


def get_fresh_article():
    """
    Fetch articles from all RSS feeds, filter out already-posted ones,
    and return one fresh article to post.
    """
    posted = load_posted_articles()
    posted_urls = set(posted)

    all_articles = []
    random.shuffle(RSS_FEEDS)  # Randomize source order for variety

    print("[*] Fetching tech news from RSS feeds...")
    for feed_info in RSS_FEEDS:
        print(f"  -> {feed_info['name']}...")
        articles = fetch_articles_from_feed(feed_info)
        all_articles.extend(articles)
        time.sleep(0.5)  # Be nice to servers

    print(f"[*] Total articles fetched: {len(all_articles)}")

    # Filter already posted
    fresh = [a for a in all_articles if a["url"] not in posted_urls]
    print(f"[*] Fresh (unposted) articles: {len(fresh)}")

    if not fresh:
        print("[!] No fresh articles found. All have been posted already.")
        return None

    # Prefer articles with images
    with_images = [a for a in fresh if a.get("image_url")]
    if with_images:
        article = random.choice(with_images[:10])  # Pick from top 10 with images
    else:
        article = random.choice(fresh[:10])

    # Mark as posted
    posted.append(article["url"])
    save_posted_articles(posted)

    print(f"[*] Selected: {article['title']} ({article['source']})")
    return article


if __name__ == "__main__":
    article = get_fresh_article()
    if article:
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print(f"Image: {article.get('image_url', 'None')}")
        print(f"Description: {article['description'][:100]}...")