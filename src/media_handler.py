"""
Handles downloading images from article URLs and uploading them to LinkedIn.
"""

import os
import tempfile
import requests
from config import LINKEDIN_ACCESS_TOKEN, LINKEDIN_API_BASE, LINKEDIN_API_VERSION


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
            print(f"  [!] Not an image: {content_type}")
            return None

        # Determine extension
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
        if file_size < 1000:  # Less than 1KB is probably not a real image
            os.unlink(tmp.name)
            print(f"  [!] Image too small ({file_size} bytes), skipping")
            return None

        print(f"  [+] Downloaded image: {tmp.name} ({file_size} bytes)")
        return tmp.name

    except Exception as e:
        print(f"  [!] Failed to download image: {e}")
        return None


def upload_image_to_linkedin(image_path, person_urn, access_token=None):
    """
    Upload an image to LinkedIn and return the image URN.
    Uses the Images API (initializeUpload + PUT binary).
    """
    token = access_token or LINKEDIN_ACCESS_TOKEN
    if not token:
        print("  [!] No access token for image upload")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LINKEDIN_API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Step 1: Initialize upload
    init_url = f"{LINKEDIN_API_BASE}/images?action=initializeUpload"
    init_body = {
        "initializeUploadRequest": {
            "owner": person_urn,
        }
    }

    try:
        resp = requests.post(init_url, json=init_body, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        upload_url = data["value"]["uploadUrl"]
        image_urn = data["value"]["image"]

        print(f"  [+] Got upload URL, image URN: {image_urn}")

    except Exception as e:
        print(f"  [!] Failed to initialize image upload: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"      Response: {e.response.text}")
        return None

    # Step 2: Upload the binary image
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()

        upload_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        }

        resp = requests.put(
            upload_url, data=image_data, headers=upload_headers, timeout=60
        )
        resp.raise_for_status()
        print(f"  [+] Image uploaded successfully!")
        return image_urn

    except Exception as e:
        print(f"  [!] Failed to upload image binary: {e}")
        return None

    finally:
        # Clean up temp file
        try:
            os.unlink(image_path)
        except OSError:
            pass