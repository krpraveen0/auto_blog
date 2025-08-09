# Medium Auto‑Article Generator

This repository provides a modular Python library and command line tool for
generating complete Medium articles from a single topic. Articles are generated
using the [Perplexity](https://www.perplexity.ai) chat completions API and
include:

* **Contextual Indian examples** – such as UPI, IRCTC, cricket statistics and
  other everyday references to make the content relatable for Indian readers.
* **Mini projects** – each with a clear goal, prerequisites, step‑by‑step
  instructions, runnable code (where relevant) and example input/output.
* **Personal branding** – helpful tips and anecdotes attributed to Praveen are
  interwoven throughout the article.

The tool supports publishing articles directly to your Medium account via
Medium's official API. Both Perplexity and Medium credentials are read from
environment variables or can be supplied on the command line.

## Run locally

Follow these steps to generate an article on your machine:

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Provide credentials** – create a `.env` file in the project root:

   ```dotenv
   PERPLEXITY_API_KEY=pk-xxxxxxxxxxxxxxxx
   MEDIUM_TOKEN=xxxxxxxxxxxxxxxx
   DATABASE_URL=postgresql://user:password@neonhost/neondb
   ```

   `DATABASE_URL` should be the full connection string from your [Neon](https://neon.tech) Postgres dashboard. Never commit this file to version control; it is already ignored via `.gitignore`. Alternatively, you can pass keys using `--pplx-key` and `--medium-token` when running the CLI.

3. **Run database migrations**

   ```bash
   yoyo apply --database "$DATABASE_URL" db/migrations
   ```

   With the tables in place you can start planning articles.

4. **Plan an article** (optionally associate it with a series and a scheduled publication date):

   ```bash
   python -m app.cli plan \
     --db-url sqlite:///blog.db \
     --topic "Real‑time bus tracking with Python and WebSockets" \
     --series "Transport" \
     --schedule-date 2024-06-01
   ```

5. **List planned articles**

   ```bash
   python -m app.cli list --db-url sqlite:///blog.db
   ```

6. **Generate (and optionally publish) a planned article**

   ```bash
   python -m app.cli generate 1 \
     --db-url sqlite:///blog.db \
     --minutes 12 \
     --outline-depth 3 \
     --publish \
     --status draft \
     --tags payments upi spring java india
   ```

   By default the generated Markdown is stored in the database. Pass `--save-md` with a path if you also want a local copy.

## GitHub Actions

Automate article generation with a scheduled or manually triggered workflow:

```yaml
# .github/workflows/generate.yml
name: Generate article
on:
  workflow_dispatch:
  schedule:
    - cron: "0 9 * * *"  # run daily at 09:00 UTC
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Run generator
        env:
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          MEDIUM_TOKEN: ${{ secrets.MEDIUM_TOKEN }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          yoyo apply --database "$DATABASE_URL" db/migrations
          python -m app.cli generate 1 --db-url "$DATABASE_URL" --publish
```

Store credentials as repository secrets under *Settings → Secrets and variables → Actions*.

## Cloudflare Workflows

Deploy the generator as a container job using [Cloudflare Workflows](https://developers.cloudflare.com/workflows/):

```yaml
# workflows.yml
name: generate-article
triggers:
  - type: schedule
    cron: "0 9 * * *"  # run daily at 09:00 UTC
jobs:
  run-cli:
    container:
      image: ghcr.io/your-org/auto_blog:latest
      cmd: ["python", "-m", "app.cli", "generate", "1", "--db-url", "${DATABASE_URL}", "--publish"]
      env:
        PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}
        MEDIUM_TOKEN: ${MEDIUM_TOKEN}
        DATABASE_URL: ${DATABASE_URL}
```

Use `wrangler workflows deploy` to deploy and `wrangler workflows secrets put` to supply the required environment variables.

## Repository structure

```text
auto_blog/
├── app/
│   ├── __init__.py         # top‑level exports for easy import
│   ├── perplexity_generator.py  # wrapper around Perplexity API
│   ├── medium_publisher.py      # wrapper around Medium API
│   ├── db.py                    # simple SQLAlchemy helpers
│   └── cli.py                   # command line interface
├── db/
│   └── migrations/          # SQL schema migrations
├── README.md                # this file
└── requirements.txt         # pip dependencies
```

## Customisation

* **Audience and tone** – adjust using `--audience` and `--tone`.
* **Model selection** – choose from `sonar`, `sonar-reasoning`, `sonar-pro`,
  and `sonar-deep-research` with `--model`.
* **Outline depth and reading time** – control the structure and length of
  articles using `--outline-depth` and `--minutes`.
* **Code inclusion** – pass `--no-code` to minimise code examples and focus on
  step‑by‑step guidance.

See `python -m app.cli --help` for all available options.
