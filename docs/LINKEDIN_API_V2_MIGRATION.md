# LinkedIn API v2 Migration Guide

## Overview

The LinkedIn posting functionality has been migrated from the newer REST API (`/rest/posts`) to the proven v2 UGC Posts API (`/v2/ugcPosts`) which has better reliability and wider support.

## What Changed

### API Endpoint
- **Old**: `https://api.linkedin.com/rest/posts`
- **New**: `https://api.linkedin.com/v2/ugcPosts`

### Payload Structure

#### Old Structure (REST API)
```json
{
  "author": "urn:li:person:USER_ID",
  "commentary": "Post content here",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

#### New Structure (v2 UGC API)
```json
{
  "author": "urn:li:person:USER_ID",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Post content here"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

### Headers

#### Old Headers
```python
{
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'LinkedIn-Version': '202401',
    'X-Restli-Protocol-Version': '2.0.0'
}
```

#### New Headers (Simplified)
```python
{
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'X-Restli-Protocol-Version': '2.0.0'
}
```

Note: The `LinkedIn-Version` header is removed as it's specific to the REST API.

## Why This Change?

1. **Proven Reliability**: The v2 UGC API has been battle-tested and widely used
2. **Better Documentation**: More examples and community support
3. **Wider Compatibility**: Works with standard LinkedIn API access tokens
4. **Simpler Structure**: Clearer separation of content and visibility

## Configuration Requirements

No changes needed to your environment variables:

```bash
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_USER_ID=your_person_id  # Can be just the ID or full URN format
```

The system automatically formats the user ID as a proper URN if needed.

## Testing

To test the new implementation:

```bash
cd /home/runner/work/auto_blog/auto_blog
python tests/test_linkedin_api_fix.py
```

Expected output:
```
✅ Test passed: 201 status code is treated as success
✅ Test passed: Correct v2 API endpoint and structure used
✅ Test passed: 200 status code is treated as failure
...
```

## Response Handling

The v2 API returns:
- **201 Created**: Post successfully created
- **Any other status**: Treated as an error

The post ID is extracted from:
1. Response body `id` field
2. Or `x-restli-id` header

## Content Enhancements

Along with the API migration, content generation has been significantly improved:

### Enhanced Prompts
- Based on how top companies (Google AI, Meta, Microsoft) share content
- Emphasis on authentic, human-sounding writing
- Strong guardrails against AI-generated content detection

### Improved Content Cleaning
- Removes meta-commentary ("Here's what...", "Let me share...")
- Strips AI-specific phrases
- Eliminates marketing buzzwords
- Preserves technical accuracy while improving readability

### Safety Validation
- Comprehensive 7-category validation system
- AI-detection risk assessment
- Authenticity scoring
- Professional reputation protection

## Troubleshooting

### Common Issues

**Issue**: 401 Unauthorized
- **Solution**: Verify your `LINKEDIN_ACCESS_TOKEN` is valid and not expired

**Issue**: 403 Forbidden
- **Solution**: Check that your LinkedIn app has the required permissions:
  - `w_member_social` - Post, comment and like posts

**Issue**: Post not appearing
- **Solution**: 
  - Verify you received a 201 response
  - Check the post ID in the response
  - LinkedIn may take a few moments to process the post

### Debug Mode

Enable debug logging to see full API requests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show the full payload (with token redacted) being sent to LinkedIn.

## References

- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/)
- [UGC Post API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)
- [Getting Started with LinkedIn API](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access)

## Support

For issues or questions:
1. Check the test suite passes: `python tests/test_linkedin_api_fix.py`
2. Review logs for error messages
3. Verify API credentials are correctly set
4. Check LinkedIn API status page for service issues
