"""
LinkedIn posting via v2 ugcPosts API.
Creates posts with text, images, and article links.
"""

import requests
from config import (
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_REFRESH_TOKEN,
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    DEFAULT_HASHTAGS,
    KEYWORD_HASHTAGS,
)


def get_headers(access_token=None):
    """Build LinkedIn API headers."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def get_user_id(access_token=None):
    """Get the authenticated user person URN."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    headers = {"Authorization": "Bearer " + token}

    try:
        resp = requests.get(
            "https://api.linkedin.com/v2/userinfo", headers=headers, timeout=15
        )
        resp.raise_for_status()
        user_info = resp.json()
        user_id = user_info.get("sub")
        if user_id:
            print("[+] Authenticated as: " + user_info.get("name", user_id))
            return "urn:li:person:" + user_id
    except Exception as e:
        print("[!] Failed to get user info: " + str(e))

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
        print("[!] Failed to refresh token: " + str(e))
        return None, None


def generate_hashtags(title, description):
    """Generate relevant hashtags based on article content."""
    text = (title + " " + description).lower()
    tags = set()

    for keyword, hashtag in KEYWORD_HASHTAGS.items():
        if keyword in text:
            tags.add(hashtag)

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

    lines = []
    lines.append("\xf0\x9f\x9a\x80 " + title)
    lines.append("")

    if description:
        lines.append(description)
        lines.append("")

    lines.append("\xf0\x9f\x93\xb0 Source: " + source)
    lines.append("\xf0\x9f\x94\x97 Read more: " + url)
    lines.append("")
    lines.append(hashtag_str)
    if source_tag:
        lines.append("#" + source_tag)

    return "\n".join(lines)


def upload_image_v2(image_path, person_urn, access_token=None):
    """Upload image via v2 assets API and return the asset URN."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    headers = get_headers(token)

    # Step 1: Register upload
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    try:
        resp = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            json=register_body,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = data["value"]["asset"]

        print("  [+] Got upload URL, asset: " + asset_urn)

    except Exception as e:
        print("  [!] Failed to register image upload: " + str(e))
        return None

    # Step 2: Upload binary
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()

        upload_headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/octet-stream",
        }

        resp = requests.put(upload_url, data=image_data, headers=upload_headers, timeout=60)
        resp.raise_for_status()
        print("  [+] Image uploaded successfully!")
        return asset_urn

    except Exception as e:
        print("  [!] Failed to upload image: " + str(e))
        return None


def create_post_with_article(article, person_urn, access_token=None):
    """Create a post with article link (rich preview card)."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)

    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": article["url"],
                        "title": {"text": article["title"]},
                        "description": {"text": article.get("description", "")[:200]},
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    # Add thumbnail
    if article.get("image_url"):
        body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"][0]["thumbnails"] = [
            {"url": article["image_url"]}
        ]

    try:
        resp = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=body,
            headers=get_headers(token),
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.json().get("id", resp.headers.get("x-restli-id", "unknown"))
        print("[+] Article post created! ID: " + str(post_id))
        return True

    except requests.exceptions.HTTPError as e:
        print("[!] Article post failed: " + str(e.response.status_code))
        print("    " + e.response.text[:300])
        return False


def create_post_with_image(article, asset_urn, person_urn, access_token=None):
    """Create a post with an uploaded image."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)

    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset_urn,
                        "title": {"text": article["title"]},
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        resp = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=body,
            headers=get_headers(token),
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.json().get("id", resp.headers.get("x-restli-id", "unknown"))
        print("[+] Image post created! ID: " + str(post_id))
        return True

    except requests.exceptions.HTTPError as e:
        print("[!] Image post failed: " + str(e.response.status_code))
        print("    " + e.response.text[:300])
        return False


def create_text_post(article, person_urn, access_token=None):
    """Create a text-only post (fallback)."""
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)

    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        resp = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=body,
            headers=get_headers(token),
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.json().get("id", resp.headers.get("x-restli-id", "unknown"))
        print("[+] Text post created! ID: " + str(post_id))
        return True

    except requests.exceptions.HTTPError as e:
        print("[!] Text post failed: " + str(e.response.status_code))
        print("    " + e.response.text[:300])
        return False