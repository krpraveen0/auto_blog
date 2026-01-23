# Admin Panel - LinkedIn Posting Feature

## Overview

The admin panel now includes a **"Post to LinkedIn"** button that allows you to publish drafted LinkedIn posts with a single click.

**Recent Update**: Manual LinkedIn posting now works **without database operations**. When you click "Post to LinkedIn" in the admin panel, the content is posted directly to LinkedIn without updating the database status. This provides a cleaner separation between content generation/storage and manual publishing.

## Prerequisites

1. **LinkedIn API Credentials**: You need to have the following environment variables set in your `.env` file:
   - `LINKEDIN_ACCESS_TOKEN`: Your LinkedIn OAuth access token
   - `LINKEDIN_USER_ID`: Your LinkedIn user ID (or URN)

2. **API Server**: The admin panel communicates with a Flask API server that handles the actual posting to LinkedIn.

## Setup Instructions

### 1. Install Dependencies

Make sure Flask and Flask-CORS are installed:

```bash
pip install -r requirements.txt
```

### 2. Configure LinkedIn Credentials

Edit your `.env` file and add/verify your LinkedIn credentials:

```bash
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_USER_ID=your_user_id_here
```

You can obtain these credentials by following the [LinkedIn API OAuth documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication).

### 3. Start the API Server

Run the API server in a separate terminal:

```bash
python api_server.py
```

By default, the server runs on `http://localhost:5000`. You can configure the port by setting the `API_PORT` environment variable:

```bash
API_PORT=8080 python api_server.py
```

### 4. Access the Admin Panel

Open the admin panel in your browser:

- **Local Development**: `file:///path/to/docs/admin/index.html` or serve it with a local web server
- **GitHub Pages**: `https://your-username.github.io/your-repo/admin/`

**Note**: When using GitHub Pages, you'll need to deploy the API server to a publicly accessible URL and update the `API_BASE_URL` in the admin panel's JavaScript.

## Usage

1. **Navigate to the Content Tab**: In the admin panel, click on the "Generated Content" tab.

2. **Filter for LinkedIn Posts**: Optionally, use the filters to show only LinkedIn content with "drafted" status.

3. **Post to LinkedIn**: 
   - Find the drafted LinkedIn post you want to publish
   - Click the blue **"Post to LinkedIn"** button in the Actions column
   - Confirm the action when prompted
   - Wait for the success message

4. **View Published Post**: After successful posting, the content status will be updated to "published" and you'll see a "View" link to the LinkedIn post.

## API Endpoints

The API server provides the following endpoints:

### Health Check
- **URL**: `/api/health`
- **Method**: `GET`
- **Description**: Check if the API server is running

### Publish to LinkedIn (Direct - No DB)
- **URL**: `/api/publish/linkedin/direct`
- **Method**: `POST`
- **Description**: Publish content directly to LinkedIn without database operations
- **Request Body**:
  ```json
  {
    "content": "Your LinkedIn post content here..."
  }
  ```
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Successfully published to LinkedIn",
    "post_url": "https://www.linkedin.com/feed/update/...",
    "post_id": "..."
  }
  ```
- **Note**: This endpoint does NOT save or update any database records. It posts directly to LinkedIn.

### Publish to LinkedIn (Legacy - With DB)
- **URL**: `/api/publish/linkedin/<content_id>`
- **Method**: `POST`
- **Description**: Publish a drafted LinkedIn post (reads from DB and updates status)
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Successfully published to LinkedIn",
    "post_url": "https://www.linkedin.com/feed/update/...",
    "post_id": "..."
  }
  ```
- **Note**: This endpoint reads content from database and updates its status after posting.

### Get Content
- **URL**: `/api/content/<content_id>`
- **Method**: `GET`
- **Description**: Get details of a specific content item

### List Content
- **URL**: `/api/content?type=linkedin&status=drafted`
- **Method**: `GET`
- **Description**: List all content with optional filtering

## Troubleshooting

### "Failed to post to LinkedIn: LinkedIn credentials not configured"
- Make sure you have set `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_USER_ID` in your `.env` file
- Restart the API server after updating the `.env` file

### "Error posting to LinkedIn: Failed to fetch"
- Make sure the API server is running on the expected port (default: 5000)
- Check the browser console for CORS errors
- Verify the `API_BASE_URL` in the admin panel matches your API server URL

### "LinkedIn API error: 401"
- Your LinkedIn access token may have expired
- Generate a new access token and update your `.env` file

### "Content already published"
- The content has already been posted to LinkedIn
- Check the "View" link to see the published post

## Production Deployment

For production deployment:

1. **Deploy the API Server**: Deploy the Flask API to a cloud service (e.g., Heroku, AWS, Google Cloud, Railway)

2. **Update API_BASE_URL**: In `docs/admin/index.html`, update the `API_BASE_URL` to point to your deployed API server

3. **Secure the API**: Consider adding authentication to the API endpoints to prevent unauthorized access

4. **Use HTTPS**: Ensure your API server uses HTTPS to protect credentials in transit

5. **Environment Variables**: Make sure your deployed API server has access to the LinkedIn credentials via environment variables

## Security Considerations

- **Never commit** your `.env` file or expose LinkedIn credentials in client-side code
- The API server should validate all inputs and handle errors gracefully
- Consider implementing rate limiting to prevent abuse
- Use HTTPS for all API communications in production
- Implement proper authentication and authorization for the API endpoints

## Alternative: GitHub Actions

If you prefer not to run an API server, you can also post to LinkedIn using the CLI:

```bash
# List drafted LinkedIn content
python main.py export-admin

# Post a specific content file
python main.py publish-linkedin --file path/to/linkedin_post.txt
```

Then check the database to see the published status and URL.
