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

Create a `.env` file in the project root with your API keys:

```dotenv
PERPLEXITY_API_KEY=pk-xxxxxxxxxxxxxxxx
MEDIUM_TOKEN=xxxxxxxxxxxxxxxx
```

Alternatively, you can pass keys using `--pplx-key` and `--medium-token` when
running the CLI.

### Generate an article (local only)

```bash
python -m medium_auto_article.cli \
  --topic "Real‑time bus tracking with Python and WebSockets" \
  --audience beginner \
  --tone practical \
  --model sonar \
  --minutes 12 \
  --outline-depth 3 \
  --save-md my_article.md
```

This command produces `my_article.md`, containing a fully formed Medium article
ready for publication.

### Generate and publish to Medium

```bash
python -m medium_auto_article.cli \
  --topic "Building a UPI‑like payment flow demo with Java + Spring" \
  --publish \
  --status draft \
  --tags payments upi spring java india
```

When `--publish` is specified, the tool will save the article to `article.md`
and then publish it on Medium. The response from the Medium API will be
printed to the console.

## Repository structure

```text
medium_auto_article/
├── medium_auto_article/
│   ├── __init__.py         # top‑level exports for easy import
│   ├── perplexity_generator.py  # wrapper around Perplexity API
│   ├── medium_publisher.py      # wrapper around Medium API
│   └── cli.py                # command line interface
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

See `python -m medium_auto_article.cli --help` for all available options.
