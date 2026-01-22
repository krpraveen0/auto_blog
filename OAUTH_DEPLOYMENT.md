# OAuth Handler Deployment Guide

This document explains how to deploy the OAuth handler service that enables secure GitHub authentication for the admin panel.

## Why is this needed?

The admin panel is hosted on GitHub Pages (a static site), which cannot securely handle OAuth token exchange because it would require exposing the `GITHUB_CLIENT_SECRET`. This lightweight backend service handles the OAuth flow securely.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Browser   │────>│   GitHub     │────>│  OAuth Handler  │
│  (Admin UI) │     │  OAuth       │     │  (This Service) │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                                           │
       │  ← Returns access_token ←────────────────┘
       │
       ▼
┌─────────────┐
│   GitHub    │
│   API       │
│  (Verify)   │
└─────────────┘
```

## Deployment Options

### Option 1: Railway (Recommended - Free tier available)

1. Sign up at [Railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Set environment variables:
   ```
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ALLOWED_USERS=your_github_username,other_username (optional)
   ```
5. Railway will auto-detect the Procfile and deploy
6. Note the deployment URL (e.g., `https://your-app.railway.app`)

### Option 2: Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Run the following commands:
   ```bash
   heroku login
   heroku create your-app-name
   
   heroku config:set GITHUB_CLIENT_ID=your_client_id
   heroku config:set GITHUB_CLIENT_SECRET=your_client_secret
   heroku config:set ALLOWED_USERS=your_github_username (optional)
   
   git push heroku main
   ```
3. Note the deployment URL (e.g., `https://your-app-name.herokuapp.com`)

### Option 3: Render

1. Sign up at [Render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set:
   - Build Command: `pip install -r oauth_requirements.txt`
   - Start Command: `gunicorn oauth_handler:app`
5. Add environment variables:
   ```
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ALLOWED_USERS=your_github_username (optional)
   ```
6. Deploy and note the URL

### Option 4: PythonAnywhere

1. Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Upload `oauth_handler.py` and `oauth_requirements.txt`
3. Create a new web app with Flask
4. Install requirements: `pip install -r oauth_requirements.txt`
5. Configure WSGI file to point to your app
6. Set environment variables in WSGI file
7. Note the deployment URL

### Option 5: DigitalOcean App Platform

1. Sign up at [DigitalOcean](https://www.digitalocean.com)
2. Create a new App from GitHub repository
3. Configure environment variables
4. Deploy and note the URL

### Option 6: Docker (Self-hosted)

For self-hosting on any platform with Docker support:

1. **Build the Docker image**:
   ```bash
   docker build -t oauth-handler .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 5000:5000 \
     -e GITHUB_CLIENT_ID=your_client_id \
     -e GITHUB_CLIENT_SECRET=your_client_secret \
     -e ALLOWED_USERS=your_github_username \
     --name oauth-handler \
     oauth-handler
   ```

3. **Or use Docker Compose**:
   ```yaml
   version: '3.8'
   services:
     oauth-handler:
       build: .
       ports:
         - "5000:5000"
       environment:
         - GITHUB_CLIENT_ID=your_client_id
         - GITHUB_CLIENT_SECRET=your_client_secret
         - ALLOWED_USERS=your_github_username
       restart: unless-stopped
   ```
   
   Run with: `docker-compose up -d`

4. Access at `http://your-server:5000`

**Deploy to cloud with Docker:**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Fly.io (recommended for Docker deployments)

## Configuration

### GitHub OAuth App Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: Your Auto Blog Admin OAuth
   - **Homepage URL**: `https://your-username.github.io/auto_blog/`
   - **Authorization callback URL**: `https://your-oauth-handler.com/auth/callback`
4. Register and note the Client ID and generate a Client Secret

### Update Admin Panel

After deploying the OAuth handler, update `docs/admin/index.html`:

1. Update the OAuth handler URL (line ~730):
   ```javascript
   const OAUTH_HANDLER_URL = 'https://your-oauth-handler.com';
   ```

2. The GITHUB_CLIENT_ID should already be set to your OAuth app's client ID

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_CLIENT_ID` | Yes | Your GitHub OAuth App Client ID |
| `GITHUB_CLIENT_SECRET` | Yes | Your GitHub OAuth App Client Secret (keep secure!) |
| `ALLOWED_USERS` | No | Comma-separated list of GitHub usernames allowed to access. If not set, any GitHub user can authenticate. |
| `PORT` | No | Port to run on (default: 5000). Most platforms set this automatically. |

## Testing Locally

```bash
# Install dependencies
pip install -r oauth_requirements.txt

# Set environment variables
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret
export ALLOWED_USERS=your_username

# Run the server
python oauth_handler.py

# Server will run on http://localhost:5000
```

## API Endpoints

### GET /auth/callback
Handles OAuth callback from GitHub. Exchanges authorization code for access token.

**Query Parameters:**
- `code`: Authorization code from GitHub
- `state`: (optional) State parameter for CSRF protection

**Response:**
```json
{
  "access_token": "gho_xxxxxxxxxxxxx",
  "user": {
    "login": "username",
    "name": "Full Name",
    "avatar_url": "https://...",
    "email": "user@example.com"
  }
}
```

### POST /auth/verify
Verifies an access token is valid.

**Request Body:**
```json
{
  "access_token": "gho_xxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "valid": true,
  "user": {
    "login": "username",
    "name": "Full Name",
    "avatar_url": "https://...",
    "email": "user@example.com"
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "oauth-handler"
}
```

## Security Considerations

1. **HTTPS Only**: Always use HTTPS in production. Never use HTTP for OAuth.
2. **Environment Variables**: Never commit `GITHUB_CLIENT_SECRET` to your repository.
3. **CORS**: The service is configured to only accept requests from `*.github.io` domains.
4. **User Whitelist**: Use `ALLOWED_USERS` to restrict access to specific GitHub users.
5. **Token Storage**: The admin panel stores tokens in localStorage. For higher security, consider using httpOnly cookies.

## Troubleshooting

### "OAuth not configured on server"
- Make sure `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` environment variables are set.

### "Failed to exchange code for token"
- Verify your GitHub OAuth App settings.
- Make sure the callback URL matches your OAuth handler URL.

### "User not authorized"
- Check the `ALLOWED_USERS` environment variable.
- Ensure your GitHub username is in the allowed list.

### CORS errors in browser
- Verify the OAuth handler is deployed and accessible.
- Check that your admin panel URL matches the CORS configuration.

## Cost Estimates

- **Railway**: Free tier available, ~$5/month for paid tier
- **Heroku**: ~$7/month for basic dyno
- **Render**: Free tier available, ~$7/month for paid tier
- **PythonAnywhere**: Free tier available with limitations
- **DigitalOcean**: ~$5/month for basic app

All of these platforms offer free tiers that should be sufficient for personal use.

## Alternative: Serverless Functions

For a serverless approach, you could also deploy this as:
- **Vercel Edge Functions** (TypeScript/JavaScript version)
- **Netlify Functions**
- **AWS Lambda** (requires more setup)
- **Cloudflare Workers**

These would require adapting the code to their specific formats but follow the same logic.
