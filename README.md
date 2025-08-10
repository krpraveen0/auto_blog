# Auto Blog

Command-line tools to plan, generate and publish Medium articles driven by the Perplexity API.

## Features
- Plan single articles or entire series and store them in a SQL database
- List scheduled articles
- Generate Markdown articles with Indian mini-projects and optional code snippets
- Publish drafts or public posts directly to Medium

## Project layout
```
app/
  cli.py                 # CLI entry points
  db.py                  # SQLAlchemy models and helpers
  medium_publisher.py    # Medium API wrapper
  perplexity_generator.py# Perplexity API wrapper
db/
  migrations/            # yoyo SQL migrations
requirements.txt         # Python dependencies
```

## Installation
1. Install Python 3.11+
2. Clone the repository and install dependencies  
   `pip install -r requirements.txt`

## Configuration
Create a `.env` file (or set environment variables):

| Variable             | Purpose                                             |
|----------------------|-----------------------------------------------------|
| `PERPLEXITY_API_KEY` | Key for the Perplexity `/chat/completions` API      |
| `MEDIUM_TOKEN`       | Medium integration token used for publishing        |
| `DATABASE_URL`       | SQLAlchemy-compatible database URL (e.g. `sqlite:///blog.db` or PostgreSQL URL) |

## Database migrations
Apply the migrations before using the CLI:

```bash
yoyo apply --database "$DATABASE_URL" db/migrations
```

## CLI usage
```bash
python -m app.cli plan         --db-url sqlite:///blog.db --topic "FastAPI with UPI"
python -m app.cli plan-series  --db-url sqlite:///blog.db --topic "Data Viz in Python" --posts 3
python -m app.cli list         --db-url sqlite:///blog.db
python -m app.cli generate 1   --db-url sqlite:///blog.db --publish --tags python medium
```

Key options for `generate`:

- `--audience {beginner|intermediate|advanced}`
- `--tone {friendly|professional|practical|conversational}`
- `--minutes N` and `--outline-depth N`
- `--no-code` to minimize code examples
- `--publish` to upload to Medium; `--status {draft|public|unlisted}`, `--tags`, `--canonical-url`
- `--save-md path` to persist generated Markdown locally
- `--pplx-key` and `--medium-token` override `.env` values

## GitHub Actions
Automate article generation with a workflow (save as `.github/workflows/generate.yml`):

```yaml
name: Generate article
on:
  workflow_dispatch:
  schedule:
    - cron: "0 9 * * *"
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - env:
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          MEDIUM_TOKEN:        ${{ secrets.MEDIUM_TOKEN }}
          DATABASE_URL:        ${{ secrets.DATABASE_URL }}
        run: |
          yoyo apply --database "$DATABASE_URL" db/migrations
          python -m app.cli generate 1 --db-url "$DATABASE_URL" --publish
```

Store the API keys and database URL as repository secrets.
