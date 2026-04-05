"""
LinkedIn Auto Poster - Main Entry Point.
Fetches tech news from RSS feeds and posts to LinkedIn.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_fetcher import get_fresh_article
from media_handler import download_image, upload_image_to_linkedin
from linkedin_poster import (
    get_user_id,
    refresh_access_token,
    create_post_with_article,
    create_post_with_image,
    create_text_post,
)
from config import LINKEDIN_ACCESS_TOKEN


def update_github_secret(name, value):
    """
    Update a GitHub Actions secret using the gh CLI.
    Only works when running inside GitHub Actions with proper permissions.
    """
    try:
        import subprocess
        repo = os.getenv("GITHUB_REPOSITORY", "")
        if repo:
            subprocess.run(
                ["gh", "secret", "set", name, "--body", value, "--repo", repo],
                check=True,
                capture_output=True,
            )
            print(f"[+] Updated GitHub secret: {name}")
    except Exception as e:
        print(f"[!] Could not update GitHub secret {name}: {e}")


def main():
    print("=" * 60)
    print("  LinkedIn Auto Poster - Tech News")
    print("=" * 60)

    # Step 1: Check access token
    access_token = LINKEDIN_ACCESS_TOKEN
    if not access_token:
        print("[!] No LINKEDIN_ACCESS_TOKEN found. Please set it.")
        print("    Run: python auth/get_token.py")
        sys.exit(1)

    # Step 2: Get user ID
    print("\n[1/4] Authenticating with LinkedIn...")
    person_urn = get_user_id(access_token)

    if not person_urn:
        print("[*] Token may be expired, attempting refresh...")
        new_access, new_refresh = refresh_access_token()
        if new_access:
            access_token = new_access
            person_urn = get_user_id(access_token)

            # Update secrets if running in GitHub Actions
            if os.getenv("GITHUB_ACTIONS"):
                update_github_secret("LINKEDIN_ACCESS_TOKEN", new_access)
                if new_refresh:
                    update_github_secret("LINKEDIN_REFRESH_TOKEN", new_refresh)

    if not person_urn:
        print("[!] Could not authenticate with LinkedIn. Exiting.")
        sys.exit(1)

    # Step 3: Fetch fresh article
    print("\n[2/4] Fetching fresh tech news...")
    article = get_fresh_article()

    if not article:
        print("[!] No fresh articles to post. Exiting.")
        sys.exit(0)

    print(f"\n  Title: {article['title']}")
    print(f"  Source: {article['source']}")
    print(f"  URL: {article['url']}")
    print(f"  Image: {article.get('image_url', 'None')}")

    # Step 4: Post to LinkedIn
    print("\n[3/4] Posting to LinkedIn...")
    posted = False

    # Strategy 1: Try article post (rich preview card)
    print("  -> Trying article post with preview card...")
    posted = create_post_with_article(article, person_urn, access_token)

    # Strategy 2: If article post fails, try image post
    if not posted and article.get("image_url"):
        print("  -> Article post failed. Trying image post...")
        image_path = download_image(article["image_url"])
        if image_path:
            image_urn = upload_image_to_linkedin(image_path, person_urn, access_token)
            if image_urn:
                posted = create_post_with_image(
                    article, image_urn, person_urn, access_token
                )

    # Strategy 3: Fallback to text-only post
    if not posted:
        print("  -> Falling back to text-only post...")
        posted = create_text_post(article, person_urn, access_token)

    # Final status
    print("\n[4/4] Result:")
    if posted:
        print("  [SUCCESS] Tech news posted to LinkedIn!")
        print(f"  Article: {article['title']}")
    else:
        print("  [FAILED] Could not post to LinkedIn.")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()