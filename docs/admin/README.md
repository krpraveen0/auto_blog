# Admin Panel Setup Guide

This admin panel allows you to query and explore the SQLite database through a web interface hosted on GitHub Pages, protected by GitHub OAuth.

## Features

- 📊 **Dashboard Overview**: Statistics and visualizations of your data
- 🔍 **Papers Browser**: Filter and search through collected papers
- 📝 **Content Manager**: View and filter generated content
- 🛠️ **Query Builder**: Build custom queries with natural language
- 📤 **Export**: Export filtered data to CSV
- 🔐 **GitHub OAuth**: Secure authentication with GitHub SSO

## Architecture

Since GitHub Pages only supports static hosting, the admin panel uses a client-side architecture:

1. **Data Export**: Python script exports SQLite database to JSON files
2. **Static Frontend**: HTML/CSS/JavaScript admin interface
3. **Client-Side Queries**: JavaScript filters and queries the exported JSON data
4. **GitHub OAuth**: Authentication via GitHub OAuth App

## Setup Instructions

### Step 1: Export Database to JSON

The database needs to be exported to JSON format for the admin panel to read:

```bash
# Export database
python export_db_json.py

# Or specify custom paths
python export_db_json.py data/research.db docs/admin
```

This creates the following files in `docs/admin/`:
- `papers.json` - All papers data
- `content.json` - All generated content
- `stats.json` - Database statistics
- `database.json` - Combined export with metadata

### Step 2: Deploy OAuth Handler (Required for Authentication)

**Important**: The admin panel requires a backend OAuth handler service to securely handle GitHub authentication. This is necessary because the client secret cannot be exposed in the browser.

#### Quick Start: Deploy OAuth Handler

1. **Choose a deployment platform** (see `OAUTH_DEPLOYMENT.md` for detailed instructions):
   - Railway (recommended - free tier available)
   - Heroku
   - Render
   - PythonAnywhere
   - DigitalOcean

2. **Deploy the OAuth handler**:
   ```bash
   # The oauth_handler.py file is included in the repository
   # Follow OAUTH_DEPLOYMENT.md for platform-specific instructions
   ```

3. **Configure environment variables** in your deployment:
   ```
   GITHUB_CLIENT_ID=your_github_oauth_client_id
   GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
   ALLOWED_USERS=your_github_username (optional - restricts access)
   ```

4. **Note your OAuth handler URL** (e.g., `https://your-app.railway.app`)

See the complete guide: [OAUTH_DEPLOYMENT.md](../../OAUTH_DEPLOYMENT.md)

### Step 3: Configure GitHub OAuth App

To enable authentication, create a GitHub OAuth App:

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Auto Blog Admin Panel
   - **Homepage URL**: `https://YOUR_USERNAME.github.io/YOUR_REPO/`
   - **Authorization callback URL**: `https://YOUR-OAUTH-HANDLER.railway.app/auth/callback` (use your OAuth handler URL)
4. Click "Register application"
5. Copy the **Client ID** and generate a **Client Secret**
6. Configure these in your OAuth handler deployment (see Step 2)

### Step 4: Update Admin Panel Configuration

Edit `docs/admin/index.html` to configure your OAuth settings:

1. **Update the OAuth handler URL** (around line 730):
   ```javascript
   const OAUTH_HANDLER_URL = 'https://your-oauth-handler.railway.app';
   ```
   Replace with your actual OAuth handler deployment URL.

2. **Verify the GitHub Client ID** (around line 727):
   ```javascript
   const GITHUB_CLIENT_ID = 'Iv23liJ9FRJcuICjBURM';
   ```
   This should match the Client ID from your GitHub OAuth App.

**Important**: Without a properly configured OAuth handler, users will not be able to access the admin panel. The authentication bypass has been removed for security.

### Step 5: Enable GitHub Pages

1. Push your changes to GitHub:
   ```bash
   git add docs/admin/
   git commit -m "Add admin panel"
   git push
   ```

2. Go to your GitHub repository settings
3. Navigate to **Pages** section
4. Under **Source**, select:
   - Branch: `main` (or your default branch)
   - Folder: `/docs`
5. Click **Save**
6. Wait a few minutes for deployment

Your admin panel will be available at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO/admin/
```

### Step 6: Automate Database Export

To keep the admin panel data up-to-date, add the export step to your GitHub Actions workflows:

```yaml
# Add to your workflow files (e.g., .github/workflows/daily_scan.yml)
- name: Export database to JSON
  run: |
    python export_db_json.py
    
- name: Commit updated data
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"
    git add docs/admin/*.json
    git diff --quiet && git diff --staged --quiet || git commit -m "Update admin panel data"
    git push
```

## Using the Admin Panel

### Overview Tab
- View key statistics
- See charts for papers by source, languages, content types, etc.

### Papers Tab
- Filter by source, language, minimum stars
- Search by keywords
- View all collected papers
- Export results to CSV

### Generated Content Tab
- Filter by content type (blog, LinkedIn, Medium)
- Filter by status (drafted, published)
- Search through generated content
- Export results to CSV

### Query Builder Tab
- Use natural language to describe your query
- Pre-built query presets:
  - Recent papers (last 7 days)
  - Top starred GitHub repos
  - Drafted content
  - Published blogs
- Export custom query results

## Security Considerations

### Authentication is Now Required

As of this update, the admin panel **requires proper GitHub OAuth authentication**. The previous "skip authentication" bypass has been removed for security reasons.

### For Production Use:

1. **✅ OAuth Handler Deployed**: The OAuth handler service must be deployed and configured
2. **✅ GitHub OAuth App**: Properly configured with correct callback URL
3. **✅ Client Secret Secure**: Never exposed in client-side code - only in OAuth handler environment variables
4. **✅ Access Control**: Use `ALLOWED_USERS` environment variable to restrict access to specific GitHub users
5. **⚠️ Data Sensitivity**: The exported JSON files are publicly accessible on GitHub Pages. If your data is sensitive, consider:
   - Using a private repository with GitHub Pages (requires GitHub Pro)
   - Implementing additional authentication layers
   - Hosting on a private server instead of GitHub Pages

### Authentication Flow:

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Browser   │ ───> │  GitHub OAuth    │ ───> │  OAuth Handler  │
│  (Admin UI) │      │  (GitHub.com)    │      │   (Backend)     │
└─────────────┘      └──────────────────┘      └─────────────────┘
       │                                                │
       │  ← Returns access_token ←────────────────────┘
       │
       ▼
┌─────────────┐                              ┌─────────────┐
│   GitHub    │                              │  Database   │
│   API       │                              │   (JSON)    │
│  (Verify)   │                              └─────────────┘
└─────────────┘
```

The OAuth handler securely manages:
- Token exchange with GitHub (using client secret)
- Token verification
- User authorization (optional whitelist)

The admin panel (static site):
- Initiates OAuth flow
- Receives and stores access token
- Queries exported JSON data
- Makes authenticated requests to GitHub API for verification

## Troubleshooting

### Admin panel shows "Loading data..."
- Make sure you've run `python export_db_json.py`
- Check that `docs/admin/database.json` exists
- Check browser console for errors

### "OAuth Handler Not Configured" error
- Deploy the OAuth handler service (see OAUTH_DEPLOYMENT.md)
- Update `OAUTH_HANDLER_URL` in `docs/admin/index.html`
- Verify the URL is accessible from your browser

### GitHub OAuth not working
- Verify your Client ID is correct in `index.html`
- Check that the OAuth callback URL in GitHub OAuth App settings points to your OAuth handler (e.g., `https://your-handler.railway.app/auth/callback`)
- Verify `GITHUB_CLIENT_SECRET` is set in your OAuth handler deployment
- Check OAuth handler logs for errors

### "User not authorized" error
- Check the `ALLOWED_USERS` environment variable in your OAuth handler
- Ensure your GitHub username is in the allowed list
- If you want to allow all users, remove or leave empty the `ALLOWED_USERS` variable

### Charts not displaying
- The current implementation uses simple canvas-based charts
- For production, consider integrating Chart.js or similar library

### Data not updating
- Run the export script after database changes
- Commit and push the updated JSON files
- Add automation to your GitHub Actions workflows

## Development

To modify the admin panel:

1. Edit `docs/admin/index.html` for UI changes
2. Test locally by opening the file in a browser
3. For local testing with live data:
   ```bash
   # Run export
   python export_db_json.py
   
   # Serve locally
   cd docs/admin
   python -m http.server 8000
   # Open http://localhost:8000
   ```

## Future Enhancements

Potential improvements for the admin panel:

- [ ] Real-time database queries (requires backend API)
- [ ] Advanced SQL query builder UI
- [ ] Data visualization library integration (Chart.js, D3.js)
- [ ] Bulk operations (delete, update status)
- [ ] Export to multiple formats (JSON, Excel, PDF)
- [ ] Scheduled report generation
- [ ] Email notifications for key metrics
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Database backup/restore interface

## License

Same as the main project (MIT)
