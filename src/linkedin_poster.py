"""
LinkedIn posting via v2 ugcPosts API.
Optimized using data from 329,504 LinkedIn posts analysis.

Key optimizations:
- NO hashtags (they scream AI)
- Strategic emoji usage to highlight key points
- 1,250-3,000 character posts (31% better performance)
- Hook with proof/authority in first line
- White space for visual breaks (>14 paragraphs = 57% better)
- Simple language (short words perform 38% better)
- Include article link (posts with links get more saves)
- Day-of-week aware content styling
"""

import random
import datetime
import requests
from config import (
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_REFRESH_TOKEN,
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
)


def get_headers(access_token=None):
    token = access_token or LINKEDIN_ACCESS_TOKEN
    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def get_user_id(access_token=None):
    token = access_token or LINKEDIN_ACCESS_TOKEN
    headers = {"Authorization": "Bearer " + token}
    try:
        resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=15)
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
        return data.get("access_token"), data.get("refresh_token", LINKEDIN_REFRESH_TOKEN)
    except Exception as e:
        print("[!] Failed to refresh token: " + str(e))
        return None, None


# ===================================================================
# POST TEMPLATES - Optimized for LinkedIn algorithm
# ===================================================================

HOOK_TEMPLATES = [
    "This just dropped and it changes everything.\n\n",
    "Most people missed this.\n\nBut it matters more than you think.\n\n",
    "Stop scrolling.\n\nThis is worth your time.\n\n",
    "I read 50+ tech articles today.\n\nThis one stood out.\n\nHere's why:\n\n",
    "The future of tech just shifted.\n\nAnd most people have no idea.\n\n",
    "This caught my eye today.\n\nAnd it should catch yours too.\n\n",
    "Breaking this down because it matters.\n\n",
    "This is the kind of news that shapes careers.\n\nPay attention.\n\n",
    "Read this before everyone else does.\n\n",
    "Something big just happened in tech.\n\nLet me break it down:\n\n",
    "This story is flying under the radar.\n\nBut it shouldn't be.\n\n",
    "The tech world is buzzing about this.\n\nHere's what you need to know:\n\n",
]

ENGAGEMENT_CTAS = [
    "\n\nWhat do you think about this?\n\nDrop your take below.",
    "\n\nAgree or disagree?\n\nI want to hear your thoughts.",
    "\n\nThis affects all of us.\n\nWhat's your take?",
    "\n\nSave this for later.\n\nYou'll want to come back to it.",
    "\n\nShare this with someone who needs to see it.",
    "\n\nFollow me for daily tech updates that matter.",
    "\n\nWhat would you do differently?\n\nLet me know below.",
    "\n\nHot take or cold take?\n\nTell me in the comments.",
    "\n\nBookmark this.\n\nCome back when it hits your industry.",
    "\n\nRepost if you found it useful.\n\nHelp others stay informed.",
]

WEEKEND_HOOKS = [
    "Weekend reading that's worth your time.\n\n",
    "Catching up on tech news this weekend.\n\nThis one hit different:\n\n",
    "Saturday deep dive into something cool.\n\n",
    "Sunday reads for the curious mind.\n\n",
    "Before you log off for the weekend...\n\nRead this.\n\n",
]

PADDING_BLOCKS = [
    "I share tech news like this every day.\n\nBecause staying informed isn't optional anymore.\n\nThe people who read and adapt are always one step ahead.\n\nThe ones who scroll past?\n\nThey wonder how they missed it.",
    "Tech moves fast.\n\nSo fast that what matters today might change everything tomorrow.\n\nThat's why I break down the big stories.\n\nSo you stay sharp without the noise.",
    "Every day I go through dozens of tech stories.\n\nMost are noise.\n\nBut some are signal.\n\nThis one is signal.\n\nThe kind you want to save and revisit.",
    "The best career advice I ever got?\n\nStay curious.\n\nRead widely.\n\nConnect the dots others miss.\n\nThat's what stories like this help you do.",
    "I post tech news daily because knowledge compounds.\n\nOne article today.\n\nAnother tomorrow.\n\nWithin a month you see patterns others can't.\n\nThat's how you stay ahead.",
]

WHY_MATTERS = [
    "Here's why this matters:",
    "Why you should care:",
    "The key takeaway:",
    "What this means for you:",
    "Why this is a big deal:",
    "The bottom line:",
]

TITLE_EMOJIS = [
    "\xe2\x9c\x85 ", "\xf0\x9f\x92\xa1 ", "\xf0\x9f\x94\xa5 ",
    "\xe2\x9a\xa1 ", "\xf0\x9f\x9a\x80 ", "\xf0\x9f\x92\xb8 ",
    "\xf0\x9f\x8e\xaf ", "\xf0\x9f\x94\x91 ",
]


def _get_day_type():
    day = datetime.datetime.utcnow().weekday()
    return "weekend" if day in (4, 5) else "weekday"


def _get_key_points(title, description, source):
    points = []
    text = (title + " " + description).lower()

    points.append("\xe2\x9c\x85 Reported by " + source + " \xe2\x80\x94 a trusted source")

    if any(w in text for w in ["ai", "artificial", "machine learning", "llm", "gpt"]):
        points.append("\xf0\x9f\xa4\x96 AI is moving faster than most realize")
        points.append("\xf0\x9f\x92\xa1 The companies adapting now will win big")
    elif any(w in text for w in ["apple", "iphone", "mac", "ios"]):
        points.append("\xf0\x9f\x8d\x8e Apple keeps pushing the envelope")
        points.append("\xf0\x9f\x92\xa1 This could change how millions use devices")
    elif any(w in text for w in ["google", "search", "android"]):
        points.append("\xf0\x9f\x94\x8d Google's moves affect the entire internet")
        points.append("\xf0\x9f\x92\xa1 Watch this space closely")
    elif any(w in text for w in ["security", "hack", "breach", "cyber"]):
        points.append("\xf0\x9f\x94\x92 Cybersecurity isn't optional anymore")
        points.append("\xf0\x9f\x92\xa1 Every business needs to pay attention")
    elif any(w in text for w in ["startup", "funding", "venture", "raised"]):
        points.append("\xf0\x9f\x92\xb0 The startup world never sleeps")
        points.append("\xf0\x9f\x92\xa1 There's a lesson here for every founder")
    elif any(w in text for w in ["crypto", "bitcoin", "blockchain"]):
        points.append("\xe2\x9b\x93 Blockchain tech keeps evolving")
        points.append("\xf0\x9f\x92\xa1 The smart money is watching this")
    else:
        points.append("\xf0\x9f\x93\x88 The tech industry moves fast")
        points.append("\xf0\x9f\x92\xa1 This could impact your work soon")

    points.append("\xe2\x9a\xa1 Read the full story for all the details")
    return points


def format_post_text(article):
    """
    Format article into an optimized LinkedIn post.
    No hashtags. Strategic emojis. 1,250-3,000 chars.
    Hook + white space + short paragraphs + CTA.
    """
    title = article["title"]
    description = article.get("description", "")
    source = article["source"]
    url = article["url"]

    hook = random.choice(WEEKEND_HOOKS if _get_day_type() == "weekend" else HOOK_TEMPLATES)
    cta = random.choice(ENGAGEMENT_CTAS)

    lines = []

    # 1. HOOK
    lines.append(hook)

    # 2. TITLE with emoji
    lines.append(random.choice(TITLE_EMOJIS) + title)
    lines.append("")

    # 3. DESCRIPTION broken into short paragraphs
    if description:
        sentences = description.replace(". ", ".\n\n").split("\n\n")
        for sent in sentences[:3]:
            sent = sent.strip()
            if sent:
                lines.append(sent)
                lines.append("")

    # 4. WHY IT MATTERS
    lines.append(random.choice(WHY_MATTERS))
    lines.append("")

    # 5. Key points with emojis
    for point in _get_key_points(title, description, source):
        lines.append(point)
        lines.append("")

    # 6. PADDING to hit 1,250+ chars
    lines.append(random.choice(PADDING_BLOCKS))
    lines.append("")

    # 7. SOURCE + link
    lines.append("\xf0\x9f\x93\x96 Full story: " + url)
    lines.append("")
    lines.append("(via " + source + ")")

    # 8. CTA
    lines.append(cta)

    post = "\n".join(lines)

    # Trim if over 3000
    if len(post) > 3000:
        post = post[:2950] + "\n\n..."

    return post


def upload_image_v2(image_path, person_urn, access_token=None):
    token = access_token or LINKEDIN_ACCESS_TOKEN
    headers = get_headers(token)
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    }
    try:
        resp = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", json=register_body, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = data["value"]["asset"]
        print("  [+] Got upload URL, asset: " + asset_urn)
    except Exception as e:
        print("  [!] Failed to register image upload: " + str(e))
        return None
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        upload_headers = {"Authorization": "Bearer " + token, "Content-Type": "application/octet-stream"}
        resp = requests.put(upload_url, data=image_data, headers=upload_headers, timeout=60)
        resp.raise_for_status()
        print("  [+] Image uploaded successfully!")
        return asset_urn
    except Exception as e:
        print("  [!] Failed to upload image: " + str(e))
        return None


def create_post_with_article(article, person_urn, access_token=None):
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)
    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "ARTICLE",
                "media": [{"status": "READY", "originalUrl": article["url"], "title": {"text": article["title"]}, "description": {"text": article.get("description", "")[:200]}}],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    if article.get("image_url"):
        body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"][0]["thumbnails"] = [{"url": article["image_url"]}]
    try:
        resp = requests.post("https://api.linkedin.com/v2/ugcPosts", json=body, headers=get_headers(token), timeout=30)
        resp.raise_for_status()
        post_id = resp.json().get("id", resp.headers.get("x-restli-id", "unknown"))
        print("[+] Article post created! ID: " + str(post_id))
        print("[*] Post length: " + str(len(text)) + " chars")
        return True
    except requests.exceptions.HTTPError as e:
        print("[!] Article post failed: " + str(e.response.status_code))
        print("    " + e.response.text[:300])
        return False


def create_post_with_image(article, asset_urn, person_urn, access_token=None):
    token = access_token or LINKEDIN_ACCESS_TOKEN
    text = format_post_text(article)
    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE",
                "media": [{"status": "READY", "media": asset_urn, "title": {"text": article["title"]}}],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    try:
        resp = requests.post("https://api.linkedin.com/v2/ugcPosts", json=body, headers=get_headers(token), timeout=30)
        resp.raise_for_status()
        post_id = resp.json().get("id", resp.headers.get("x-restli-id", "unknown"))
        print("[+] Image post created! ID: " + str(post_id))
        print("[*] Post length: " + str(len(text)) + " chars")
        return True
    except requests.exceptions.HTTPError as e:
        print("[!] Image post failed: " + str(e.response.status_code))
        print("    " + e.response.text[:300])
        return False


def create_text_post(article, person_urn, access_token=None):
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
        resp = requests.post("https://api.linkedin.com/v2/ugcPosts", json=body, headers=get_headers(token), timeout=30)
        resp.raise_for_status()
        post_id = resp.json().get("id", resp.headers.get("x-restli-id", "unknown"))
        print("[+] Text post created! ID: " + str(post_id))
        print("[*] Post length: " + str(len(text)) + " chars")
        return True
    except requests.exceptions.HTTPError as e:
        print("[!] Text post failed: " + str(e.response.status_code))
        print("    " + e.response.text[:300])
        return False