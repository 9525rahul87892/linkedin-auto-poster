import requests, os, sys
sys.path.insert(0, "src")

with open(".env") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
print(f"Token length: {len(token)}")

headers = {"Authorization": f"Bearer {token}"}
r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
print(f"UserInfo status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"User sub: {data.get('sub', '?')}")
    print(f"Name: {data.get('name', '?')}")
    person_urn = f"urn:li:person:{data['sub']}"
    
    # Try a test post
    post_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202501",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    body = {
        "author": person_urn,
        "commentary": "Testing automated post setup...",
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
    print(f"Post status: {r2.status_code}")
    print(f"Post response: {r2.text[:500]}")
    if r2.status_code in (200, 201):
        print(f"Post ID: {r2.headers.get('x-restli-id', 'unknown')}")
else:
    print(f"Error: {r.text[:300]}")
