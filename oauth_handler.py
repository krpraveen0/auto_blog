#!/usr/bin/env python3
"""
OAuth Handler for GitHub Pages Admin Panel

This lightweight Flask server handles OAuth token exchange for the admin panel.
It can be deployed on any platform (Heroku, Railway, PythonAnywhere, etc.)

Environment variables required:
- GITHUB_CLIENT_ID: Your GitHub OAuth App Client ID
- GITHUB_CLIENT_SECRET: Your GitHub OAuth App Client Secret
- ALLOWED_USERS: Comma-separated list of GitHub usernames allowed to access (optional)
"""

import os
import requests
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for GitHub Pages domain
CORS(app, resources={
    r"/auth/*": {
        "origins": ["https://*.github.io", "http://localhost:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
ALLOWED_USERS = os.environ.get('ALLOWED_USERS', '').split(',') if os.environ.get('ALLOWED_USERS') else None


@app.route('/auth/callback', methods=['GET'])
def oauth_callback():
    """
    Handle OAuth callback from GitHub and exchange code for token.
    """
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        return jsonify({'error': 'OAuth not configured on server'}), 500
    
    # Exchange code for access token
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
        }
    )
    
    if token_response.status_code != 200:
        return jsonify({'error': 'Failed to exchange code for token'}), 500
    
    token_data = token_response.json()
    
    if 'error' in token_data:
        return jsonify({'error': token_data.get('error_description', 'Token exchange failed')}), 400
    
    access_token = token_data.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'No access token received'}), 500
    
    # Verify token by getting user info
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if user_response.status_code != 200:
        return jsonify({'error': 'Failed to verify token'}), 500
    
    user_data = user_response.json()
    username = user_data.get('login')
    
    # Check if user is allowed (if ALLOWED_USERS is set)
    if ALLOWED_USERS and username not in ALLOWED_USERS:
        return jsonify({'error': f'User {username} is not authorized to access this admin panel'}), 403
    
    # Return token to frontend
    # In production, consider using a more secure method like httpOnly cookies
    return jsonify({
        'access_token': access_token,
        'user': {
            'login': username,
            'name': user_data.get('name'),
            'avatar_url': user_data.get('avatar_url'),
            'email': user_data.get('email')
        }
    })


@app.route('/auth/verify', methods=['POST'])
def verify_token():
    """
    Verify a GitHub access token and return user information.
    """
    data = request.get_json()
    access_token = data.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400
    
    # Verify token with GitHub API
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if user_response.status_code != 200:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    user_data = user_response.json()
    username = user_data.get('login')
    
    # Check if user is allowed
    if ALLOWED_USERS and username not in ALLOWED_USERS:
        return jsonify({'error': f'User {username} is not authorized'}), 403
    
    return jsonify({
        'valid': True,
        'user': {
            'login': username,
            'name': user_data.get('name'),
            'avatar_url': user_data.get('avatar_url'),
            'email': user_data.get('email')
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'oauth-handler'})


if __name__ == '__main__':
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        print("WARNING: GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set")
        print("Please set these environment variables before running.")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
