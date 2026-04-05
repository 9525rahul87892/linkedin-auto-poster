"""
LinkedIn Posts API integration.
Creates posts with text, images, and article links.
"""

import requests
from config import (
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_REFRESH_TOKEN,
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    LINKEDIN_API_BASE,
    LINKEDIN_API_VERSION,
    DEFAULT_HASHTAGS,
    KEYWORD_HASHTAGS,
)


def get_headers(access_token=None):
    """Build LinkedIn API headers."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LINKEDIN_API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }


def get_user_id(access_token=None):
    """Get the authenticated user's LinkedIn person URN."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(
            "https://api.linkedin.com/v2/userinfo", headers=headers, timeout=15
        )
        resp.raise_for_status()
        user_info = resp.json()
        user_id = user_info.get("sub")
        if user_id:
            print(f"[+] Authenticated as user: {user_id}")
            return f"urn:li:person:{user_id}"
    except Exception as e:
        print(f"[!] Failed to get user info: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"    Response: {e.response.text}")

    return None


def refresh_access_token():
    """Refresh the LinkedIn access token using the refresh token."""
    if not LINKEDIN_REFRESH_TOKEN or not LINKEDIN_CLIENT_ID:
        print("[!] No refresh token or client credentials available")
        return None, None

    try:
        resp = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "refresh_token",
                "refresh_token": LINKEDIN_REFRESH_TOKEN,
                "client_id": LINKEDIN_CLIENT_ID,
                "client_secret": LINKEDIN_CLIENT_SECRET,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        new_access = data.get("access_token")
        new_refresh = data.get("refresh_token", LINKEDIN_REFRESH_TOKEN)
        print("[+] Access token refreshed successfully!")
        return new_access, new_refresh

    except Exception as e:
        print(f"[!] Failed to refresh token: {e}")
        return None, None


def generate_hashtags(title, description):
    """Generate relevant hashtags based on article content."""
    text = f"{title} {description}".lower()
    tags = set()

    for keyword, hashtag in KEYWORD_HASHTAGS.items():
        if keyword in text:
            tags.add(hashtag)

    # Add default tags, total max 6
    for tag in DEFAULT_HASHTAGS:
        if len(tags) >= 6:
            break
        tags.add(tag)

    return list(tags)[:6]


def format_post_text(article):
    """Format the article into a LinkedIn post."""
    title = article["title"]
    description = article.get("description", "")
    source = article["source"]
    url = article["url"]
    source_tag = article.get("source_tag", "")

    hashtags = generate_hashtags(title, description)
    hashtag_str = " ".join(hashtags)

    # Build post text
    lines = []
    lines.append(f"\xf0\x9f\x9a\x80 {title}")
    lines.append("")

    if description:
        lines.append(description)
        lines.append("")

    lines.append(f"\xf0\x9f\x93\xb0 Source: {source}")
    lines.append(f"\xf0\x9f\x94\x97 Read more: {url}")
    lines.append("")
    lines.append(hashtag_str)
    if source_tag:
        lines.append(f"#{source_tag}")

    return "\n".join(lines)


def create_post_with_article(article, person_urn, access_token=None):
    """
    Create a LinkedIn post with an article link (shows a rich preview card).
    """
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)

    body = {
        "author": person_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "article": {
                "source": article["url"],
                "title": article["title"],
                "description": article.get("description", "")[:200],
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    # Add thumbnail if available
    if article.get("image_url"):
        body["content"]["article"]["thumbnail"] = article["image_url"]

    try:
        resp = requests.post(
            f"{LINKEDIN_API_BASE}/posts",
            json=body,
            headers=get_headers(token),
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.headers.get("x-restli-id", "unknown")
        print(f"[+] Article post created successfully! Post ID: {post_id}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"[!] Failed to create article post: {e}")
        print(f"    Status: {e.response.status_code}")
        print(f"    Response: {e.response.text}")
        return False


def create_post_with_image(article, image_urn, person_urn, access_token=None):
    """
    Create a LinkedIn post with an uploaded image.
    """
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)

    body = {
        "author": person_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": article["title"],
                "id": image_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    try:
        resp = requests.post(
            f"{LINKEDIN_API_BASE}/posts",
            json=body,
            headers=get_headers(token),
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.headers.get("x-restli-id", "unknown")
        print(f"[+] Image post created successfully! Post ID: {post_id}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"[!] Failed to create image post: {e}")
        print(f"    Status: {e.response.status_code}")
        print(f"    Response: {e.response.text}")
        return False


def create_text_post(article, person_urn, access_token=None):
    """
    Create a text-only LinkedIn post (fallback if image/article fails).
    """
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)

    body = {
        "author": person_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    try:
        resp = requests.post(
            f"{LINKEDIN_API_BASE}/posts",
            json=body,
            headers=get_headers(token),
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.headers.get("x-restli-id", "unknown")
        print(f"[+] Text post created successfully! Post ID: {post_id}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"[!] Failed to create text post: {e}")
        print(f"    Status: {e.response.status_code}")
        print(f"    Response: {e.response.text}")
        return False