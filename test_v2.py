import requests, os, sys

with open(".env") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")

# Get user ID
headers = {"Authorization": "Bearer " + token}
r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
data = r.json()
person_urn = "urn:li:person:" + data["sub"]
sys.stdout.write("User: " + data.get("name", "?") + "\n")
sys.stdout.flush()

# Use ugcPosts v2 API (no version header needed)
post_headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}

body = {
    "author": person_urn,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Test post from LinkedIn Auto Poster!\n\nThis is an automated test.\n\n#TechNews #Test"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

r2 = requests.post("https://api.linkedin.com/v2/ugcPosts", json=body, headers=post_headers)
sys.stdout.write("Post status: " + str(r2.status_code) + "\n")
sys.stdout.write("Response: " + r2.text[:500] + "\n")
if r2.status_code in (200, 201):
    sys.stdout.write("SUCCESS! Post ID: " + r2.headers.get("x-restli-id", r2.json().get("id", "?")) + "\n")
sys.stdout.flush()