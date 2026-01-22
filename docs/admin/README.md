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

### Step 2: Configure GitHub OAuth (Optional but Recommended)

To enable authentication, create a GitHub OAuth App:

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Auto Blog Admin Panel
   - **Homepage URL**: `https://YOUR_USERNAME.github.io/YOUR_REPO/`
   - **Authorization callback URL**: `https://YOUR_USERNAME.github.io/YOUR_REPO/admin/`
4. Click "Register application"
5. Copy the **Client ID**
6. Edit `docs/admin/index.html` and replace:
   ```javascript
   const GITHUB_CLIENT_ID = 'YOUR_GITHUB_CLIENT_ID';
   ```
   with your actual Client ID

**Note**: For full OAuth to work on a static site, you typically need a backend service to handle the token exchange. For a simpler setup, the admin panel includes a "skip authentication" option for testing.

### Step 3: Enable GitHub Pages

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

### Step 4: Automate Database Export

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

### For Production Use:

1. **Enable GitHub OAuth**: Don't skip authentication in production
2. **Backend Token Exchange**: Implement a backend service to handle OAuth token exchange securely (GitHub OAuth requires a client secret that shouldn't be exposed)
3. **Access Control**: Consider using GitHub Organizations and team-based access control
4. **Data Sensitivity**: The exported JSON files are publicly accessible on GitHub Pages. If your data is sensitive, consider:
   - Using a private repository with GitHub Pages (requires GitHub Pro)
   - Implementing additional authentication layers
   - Hosting on a private server instead of GitHub Pages

### Recommended Production Architecture:

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│   Browser   │ ───> │  GitHub OAuth    │ ───> │   Backend   │
│             │      │  (GitHub.com)    │      │   Service   │
└─────────────┘      └──────────────────┘      └─────────────┘
       │                                                │
       │  (Authenticated)                             │
       ▼                                                ▼
┌─────────────┐                              ┌─────────────┐
│   Admin     │ <────────────────────────────│  Database   │
│   Panel     │        (Secure API)          │   (SQLite)  │
└─────────────┘                              └─────────────┘
```

For the GitHub Pages static version (current implementation):
- Authentication is simplified/optional
- Data is pre-exported to JSON
- Querying happens client-side in browser

## Troubleshooting

### Admin panel shows "Loading data..."
- Make sure you've run `python export_db_json.py`
- Check that `docs/admin/database.json` exists
- Check browser console for errors

### GitHub OAuth not working
- Verify your Client ID is correct in `index.html`
- Check that the callback URL matches your GitHub Pages URL
- For testing, you can use the "skip authentication" option

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
