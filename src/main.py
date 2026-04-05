"""
LinkedIn Auto Poster - Main Entry Point.
Fetches tech news from RSS feeds and posts to LinkedIn.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_fetcher import get_fresh_article
from media_handler import download_image
from linkedin_poster import (
    get_user_id,
    refresh_access_token,
    create_post_with_article,
    create_post_with_image,
    create_text_post,
    upload_image_v2,
)
from config import LINKEDIN_ACCESS_TOKEN


def update_github_secret(name, value):
    """Update a GitHub Actions secret using the gh CLI."""
    try:
        import subprocess
        repo = os.getenv("GITHUB_REPOSITORY", "")
        if repo:
            subprocess.run(
                ["gh", "secret", "set", name, "--body", value, "--repo", repo],
                check=True,
                capture_output=True,
            )
            print("[+] Updated GitHub secret: " + name)
    except Exception as e:
        print("[!] Could not update GitHub secret " + name + ": " + str(e))


def main():
    print("=" * 60)
    print("  LinkedIn Auto Poster - Tech News")
    print("=" * 60)

    access_token = LINKEDIN_ACCESS_TOKEN
    if not access_token:
        print("[!] No LINKEDIN_ACCESS_TOKEN found.")
        print("    Run: python auth/get_token.py")
        sys.exit(1)

    # Step 1: Authenticate
    print("\n[1/4] Authenticating with LinkedIn...")
    person_urn = get_user_id(access_token)

    if not person_urn:
        print("[*] Token may be expired, attempting refresh...")
        new_access, new_refresh = refresh_access_token()
        if new_access:
            access_token = new_access
            person_urn = get_user_id(access_token)
            if os.getenv("GITHUB_ACTIONS"):
                update_github_secret("LINKEDIN_ACCESS_TOKEN", new_access)
                if new_refresh:
                    update_github_secret("LINKEDIN_REFRESH_TOKEN", new_refresh)

    if not person_urn:
        print("[!] Could not authenticate with LinkedIn. Exiting.")
        sys.exit(1)

    # Step 2: Fetch article
    print("\n[2/4] Fetching fresh tech news...")
    article = get_fresh_article()

    if not article:
        print("[!] No fresh articles to post. Exiting.")
        sys.exit(0)

    print("\n  Title: " + article["title"])
    print("  Source: " + article["source"])
    print("  URL: " + article["url"])
    print("  Image: " + str(article.get("image_url", "None")))

    # Step 3: Post to LinkedIn
    print("\n[3/4] Posting to LinkedIn...")
    posted = False

    # Strategy 1: Article post with rich preview
    print("  -> Trying article post with preview card...")
    posted = create_post_with_article(article, person_urn, access_token)

    # Strategy 2: Image post
    if not posted and article.get("image_url"):
        print("  -> Trying image post...")
        image_path = download_image(article["image_url"])
        if image_path:
            asset_urn = upload_image_v2(image_path, person_urn, access_token)
            if asset_urn:
                posted = create_post_with_image(article, asset_urn, person_urn, access_token)
            try:
                os.unlink(image_path)
            except OSError:
                pass

    # Strategy 3: Text-only fallback
    if not posted:
        print("  -> Falling back to text-only post...")
        posted = create_text_post(article, person_urn, access_token)

    # Result
    print("\n[4/4] Result:")
    if posted:
        print("  [SUCCESS] Tech news posted to LinkedIn!")
        print("  Article: " + article["title"])
    else:
        print("  [FAILED] Could not post to LinkedIn.")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()