"""
Handles downloading images from article URLs.
Upload is now handled in linkedin_poster.py via v2 assets API.
"""

import os
import tempfile
import requests


def download_image(image_url):
    """Download an image from a URL and return the local file path."""
    if not image_url:
        return None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type and not image_url.lower().endswith(
            (".jpg", ".jpeg", ".png", ".gif", ".webp")
        ):
            print("  [!] Not an image: " + content_type)
            return None

        if "png" in content_type or image_url.lower().endswith(".png"):
            ext = ".png"
        elif "gif" in content_type or image_url.lower().endswith(".gif"):
            ext = ".gif"
        elif "webp" in content_type or image_url.lower().endswith(".webp"):
            ext = ".webp"
        else:
            ext = ".jpg"

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        for chunk in response.iter_content(8192):
            tmp.write(chunk)
        tmp.close()

        file_size = os.path.getsize(tmp.name)
        if file_size < 1000:
            os.unlink(tmp.name)
            print("  [!] Image too small (" + str(file_size) + " bytes), skipping")
            return None

        print("  [+] Downloaded image: " + str(file_size) + " bytes")
        return tmp.name

    except Exception as e:
        print("  [!] Failed to download image: " + str(e))
        return None