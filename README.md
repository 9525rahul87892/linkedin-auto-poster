# LinkedIn Auto Poster

Automatically posts tech news to your LinkedIn profile every hour using GitHub Actions. Works even when your laptop is off.

## How It Works

1. **GitHub Actions** triggers every hour (cron schedule)
2. **RSS scraping** fetches latest tech news from 8 major sources
3. **Formats** the article with title, description, hashtags
4. **Posts** to LinkedIn via official Posts API (text + article preview card + image)
5. **Tracks** posted articles to avoid duplicates

## News Sources (RSS - No API Keys Needed)

- TechCrunch
- The Verge
- Ars Technica
- Wired
- MIT Technology Review
- Hacker News
- TechRadar
- Engadget

## Setup

### Step 1: LinkedIn Developer App

1. Go to [developer.linkedin.com](https://developer.linkedin.com/)
2. Create an app (associate with your Company Page)
3. Go to **Products** tab -> Add **"Share on LinkedIn"**
4. Go to **Products** tab -> Add **"Sign In with LinkedIn using OpenID Connect"**
5. Go to **Auth** tab -> Add `http://localhost:8585/callback` to **Redirect URLs**
6. Note your **Client ID** and **Client Secret**

### Step 2: Get OAuth Tokens

```bash
pip install requests
python auth/get_token.py
```

This will:
- Open your browser for LinkedIn authorization
- Capture the OAuth token via local redirect
- Print your Access Token and Refresh Token

### Step 3: Create GitHub Repo and Add Secrets

1. Create a new GitHub repository
2. Push this code to it
3. Go to **Settings > Secrets and variables > Actions**
4. Add these secrets:

| Secret Name | Value |
|---|---|
| `LINKEDIN_ACCESS_TOKEN` | From Step 2 |
| `LINKEDIN_REFRESH_TOKEN` | From Step 2 |
| `LINKEDIN_CLIENT_ID` | From Step 1 |
| `LINKEDIN_CLIENT_SECRET` | From Step 1 |
| `GH_PAT` | GitHub Personal Access Token (for updating secrets) |

### Step 4: Enable GitHub Actions

1. Go to the **Actions** tab in your repo
2. Enable workflows
3. Manually trigger "LinkedIn Auto Poster" to test
4. Once working, it will auto-run every hour

## Local Testing

```bash
pip install -r requirements.txt

# Test news fetching only
python src/news_fetcher.py

# Full run (needs LinkedIn tokens)
export LINKEDIN_ACCESS_TOKEN=your_token
python src/main.py
```

## Post Format

Each post looks like:

```
 Apple Unveils New M4 MacBook Pro with Enhanced AI Features

Apple today announced the latest MacBook Pro lineup featuring the M4 chip...

 Source: TechCrunch
 Read more: https://techcrunch.com/...

#TechNews #Technology #Apple
#TechCrunch
```

## Configuration

Edit `src/config.py` to:
- Add/remove RSS feeds
- Customize hashtags
- Change API version