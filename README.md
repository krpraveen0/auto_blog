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

## Quick start

### Installation

Clone this repository and install its dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys and database connection string:

```dotenv
PERPLEXITY_API_KEY=pk-xxxxxxxxxxxxxxxx
MEDIUM_TOKEN=xxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://user:password@neonhost/neondb
```

`DATABASE_URL` should be the full connection string from your [Neon](https://neon.tech) Postgres dashboard.
Never commit this file to version control; it is already ignored via `.gitignore`.

Alternatively, you can pass keys using `--pplx-key` and `--medium-token` when
running the CLI.

### Plan an article

Use the `plan` subcommand to insert a topic into the database. Optionally
associate it with a series and a scheduled publication date.

```bash
python -m app.cli plan \
  --db-url sqlite:///blog.db \
  --topic "Real‑time bus tracking with Python and WebSockets" \
  --series "Transport" \
  --schedule-date 2024-06-01
```

### List planned articles

```bash
python -m app.cli list --db-url sqlite:///blog.db
```

### Generate (and optionally publish) a planned article

```bash
python -m app.cli generate 1 \
  --db-url sqlite:///blog.db \
  --minutes 12 \
  --outline-depth 3 \
  --publish \
  --status draft \
  --tags payments upi spring java india
```

By default the generated Markdown is stored in the database. Pass `--save-md`
with a path if you also want a local copy.

## Repository structure

```text
auto_blog/
├── app/
│   ├── __init__.py         # top‑level exports for easy import
│   ├── perplexity_generator.py  # wrapper around Perplexity API
│   ├── medium_publisher.py      # wrapper around Medium API
│   ├── db.py                    # simple SQLAlchemy helpers
│   └── cli.py                   # command line interface
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
