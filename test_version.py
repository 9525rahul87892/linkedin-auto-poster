import requests, os, sys

with open(".env") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")

versions = ["202301", "202306", "202310", "202401", "202406", "202410", "202501", "202502", "202503"]
results = []
for ver in versions:
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "LinkedIn-Version": ver,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    r = requests.get("https://api.linkedin.com/rest/me", headers=headers)
    results.append(ver + " -> " + str(r.status_code))

for x in results:
    sys.stdout.write(x + "\n")
    sys.stdout.flush()