# Admin Panel OAuth Setup - Quick Start Guide

This guide will help you set up secure GitHub OAuth authentication for your admin panel in under 15 minutes.

## Overview

The admin panel now requires authentication via GitHub OAuth. This ensures only authorized users can access your admin interface.

## Prerequisites

- GitHub account
- Repository with admin panel deployed to GitHub Pages
- 10-15 minutes for setup

## Step-by-Step Setup

### 1. Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"OAuth Apps"** → **"New OAuth App"**
3. Fill in the form:
   - **Application name**: `Auto Blog Admin Panel` (or your preferred name)
   - **Homepage URL**: `https://YOUR_USERNAME.github.io/auto_blog/`
   - **Authorization callback URL**: We'll update this in step 3
   - **Application description**: (optional) `OAuth handler for admin panel authentication`
4. Click **"Register application"**
5. **Copy the Client ID** (you'll need this)
6. Click **"Generate a new client secret"**
7. **Copy the Client Secret immediately** (you won't be able to see it again)

### 2. Deploy OAuth Handler

The OAuth handler is a lightweight Python service that securely manages OAuth token exchange.

#### Option A: Railway (Recommended - Free Tier)

1. Go to [Railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `auto_blog` repository
4. Railway will detect the `Procfile` and configure automatically
5. Go to **"Variables"** tab and add:
   ```
   GITHUB_CLIENT_ID=<paste your Client ID from step 1>
   GITHUB_CLIENT_SECRET=<paste your Client Secret from step 1>
   ALLOWED_USERS=<your_github_username>
   ```
6. Click **"Deploy"**
7. Once deployed, go to **"Settings"** → **"Networking"**
8. Click **"Generate Domain"**
9. **Copy the generated URL** (e.g., `https://auto-blog-production-xxxx.up.railway.app`)

#### Option B: Render (Alternative - Free Tier)

1. Go to [Render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `auto-blog-oauth`
   - **Build Command**: `pip install -r oauth_requirements.txt`
   - **Start Command**: `gunicorn oauth_handler:app`
5. Add Environment Variables:
   ```
   GITHUB_CLIENT_ID=<your Client ID>
   GITHUB_CLIENT_SECRET=<your Client Secret>
   ALLOWED_USERS=<your_github_username>
   ```
6. Click **"Create Web Service"**
7. **Copy the service URL** (e.g., `https://auto-blog-oauth.onrender.com`)

#### Option C: Heroku

```bash
# Install Heroku CLI first: https://devcenter.heroku.com/articles/heroku-cli
cd /path/to/auto_blog
heroku login
heroku create auto-blog-oauth

# Set environment variables
heroku config:set GITHUB_CLIENT_ID=your_client_id
heroku config:set GITHUB_CLIENT_SECRET=your_client_secret
heroku config:set ALLOWED_USERS=your_username

# Deploy
git push heroku main

# Get the URL
heroku info -s | grep web_url
```

See [OAUTH_DEPLOYMENT.md](./OAUTH_DEPLOYMENT.md) for more deployment options.

### 3. Update GitHub OAuth App Callback URL

1. Go back to your [GitHub OAuth App settings](https://github.com/settings/developers)
2. Click on your OAuth App
3. Update **"Authorization callback URL"** to:
   ```
   https://YOUR-OAUTH-HANDLER-URL/auth/callback
   ```
   Replace `YOUR-OAUTH-HANDLER-URL` with the URL from step 2 (e.g., `https://auto-blog-production-xxxx.up.railway.app`)
4. Click **"Update application"**

### 4. Configure Admin Panel

Edit `docs/admin/index.html` in your repository:

1. Find line ~730 (search for `OAUTH_HANDLER_URL`):
   ```javascript
   const OAUTH_HANDLER_URL = 'https://your-oauth-handler.railway.app';
   ```

2. Replace with your OAuth handler URL:
   ```javascript
   const OAUTH_HANDLER_URL = 'https://auto-blog-production-xxxx.up.railway.app';
   ```

3. Verify the `GITHUB_CLIENT_ID` matches (line ~727):
   ```javascript
   const GITHUB_CLIENT_ID = 'Iv23liJ9FRJcuICjBURM';
   ```

4. Save and commit:
   ```bash
   git add docs/admin/index.html
   git commit -m "Configure OAuth handler for admin panel"
   git push
   ```

### 5. Test Authentication

1. Wait 1-2 minutes for GitHub Pages to redeploy
2. Visit your admin panel: `https://YOUR_USERNAME.github.io/auto_blog/admin/`
3. Click **"Login with GitHub"**
4. Authorize the application on GitHub
5. You should be redirected back and logged in!

## Verification Checklist

- [ ] GitHub OAuth App created with correct callback URL
- [ ] OAuth handler deployed with environment variables set
- [ ] OAuth handler URL updated in `docs/admin/index.html`
- [ ] Changes committed and pushed to GitHub
- [ ] Admin panel accessible and authentication working

## Restricting Access

By default, only users listed in `ALLOWED_USERS` can access the admin panel.

To add more users:
1. Go to your OAuth handler deployment settings
2. Update `ALLOWED_USERS` environment variable:
   ```
   ALLOWED_USERS=user1,user2,user3
   ```
3. Restart the service (automatic on most platforms)

To allow any GitHub user:
- Remove or leave empty the `ALLOWED_USERS` variable

## Troubleshooting

### "OAuth Handler Not Configured" error
- Make sure you updated `OAUTH_HANDLER_URL` in `docs/admin/index.html`
- Verify the changes are committed and pushed
- Wait for GitHub Pages to redeploy (~1-2 minutes)

### "Authentication failed" error
- Check OAuth handler logs in your deployment platform
- Verify `GITHUB_CLIENT_SECRET` is set correctly
- Ensure callback URL matches exactly in GitHub OAuth App settings

### "User not authorized" error
- Add your GitHub username to `ALLOWED_USERS` in OAuth handler
- Username is case-sensitive

### OAuth handler not responding
- Check if the service is running in your deployment dashboard
- Verify the URL is accessible: visit `https://YOUR-HANDLER-URL/health`
- Check deployment logs for errors

## Security Notes

✅ **What's Secure:**
- Client secret is never exposed to the browser
- Token exchange happens server-side
- User authentication via GitHub
- Optional access control with `ALLOWED_USERS`

⚠️ **Be Aware:**
- Exported JSON data is publicly accessible on GitHub Pages
- Access tokens are stored in browser localStorage
- For highly sensitive data, consider hosting admin panel on a private server

## Cost

All recommended platforms offer free tiers suitable for personal use:
- **Railway**: Free tier with 500 hours/month
- **Render**: Free tier with 750 hours/month
- **Heroku**: ~$7/month (no free tier as of Nov 2022)

## Need Help?

- **OAuth Deployment Issues**: See [OAUTH_DEPLOYMENT.md](./OAUTH_DEPLOYMENT.md)
- **Admin Panel Issues**: See [docs/admin/README.md](./docs/admin/README.md)
- **GitHub OAuth Documentation**: https://docs.github.com/en/apps/oauth-apps

## Next Steps

Once authentication is working:
1. Explore the admin panel features
2. Set up automated database exports (see admin README)
3. Customize the OAuth handler (add logging, monitoring, etc.)
4. Consider adding more authentication providers if needed

---

**Estimated Setup Time**: 10-15 minutes  
**Difficulty**: Beginner-friendly  
**Cost**: Free (with free tier deployments)
