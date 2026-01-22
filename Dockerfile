FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY oauth_requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r oauth_requirements.txt

# Copy application
COPY oauth_handler.py .

# Expose port
EXPOSE 5000

# Set environment variables (override these in deployment)
ENV GITHUB_CLIENT_ID=""
ENV GITHUB_CLIENT_SECRET=""
ENV ALLOWED_USERS=""
ENV PORT=5000

# Run the application
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 oauth_handler:app
