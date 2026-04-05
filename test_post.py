import requests, os, sys
sys.path.insert(0, "src")

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
sys.stdout.write("User: " + data.get("name", "?") + " (" + person_urn + ")\n")
sys.stdout.flush()

# Try a simple text post
post_headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "LinkedIn-Version": "202406",
    "X-Restli-Protocol-Version": "2.0.0",
}

body = {
    "author": person_urn,
    "commentary": "\xf0\x9f\x9a\x80 Test post from LinkedIn Auto Poster!\n\nThis is an automated test.\n\n#TechNews #Test",
    "visibility": "PUBLIC",
    "distribution": {
        "feedDistribution": "MAIN_FEED",
        "targetEntities": [],
        "thirdPartyDistributionChannels": [],
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": False,
}

r2 = requests.post("https://api.linkedin.com/rest/posts", json=body, headers=post_headers)
sys.stdout.write("Post status: " + str(r2.status_code) + "\n")
sys.stdout.write("Response: " + r2.text[:500] + "\n")
if r2.status_code in (200, 201):
    sys.stdout.write("Post ID: " + r2.headers.get("x-restli-id", "unknown") + "\n")
    sys.stdout.write("SUCCESS!\n")
sys.stdout.flush()