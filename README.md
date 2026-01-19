# AI Research Publisher

**A personal AI research editor that scans trusted sources, filters signal from noise, and converts updates into blog-ready articles and LinkedIn posts.**

## 🎯 What This Does

- **Scans** trusted AI/ML/LLM sources (arXiv, company blogs, Hacker News, GitHub)
- **Filters** using relevance heuristics and deduplication
- **Analyzes** using Perplexity AI (sonar-pro model) for credible insights
- **Generates** blog articles (800-1000 words) and LinkedIn posts (120 words)
- **Publishes** to GitHub Pages and LinkedIn (with approval flow)
- **Automates** via GitHub Actions (daily/weekly)

## 🏗️ Architecture

```
[ Sources ]
   ↓
[ Fetchers ]
   ↓
[ Dedup + Relevance Filter ]
   ↓
[ Summarizer / Insight Generator (Perplexity LLM) ]
   ↓
[ Content Formatter ]
   ↓
[ Blog + LinkedIn Publisher ]
```

## 📁 Project Structure

```
ai-research-publisher/
│
├── sources/              # Source-specific fetchers
│   ├── __init__.py
│   ├── arxiv.py         # arXiv RSS feeds
│   ├── blogs.py         # Company blogs (OpenAI, DeepMind, etc.)
│   ├── hackernews.py    # HN AI stories
│   └── github.py        # GitHub trending ML/AI
│
├── filters/              # Filtering and ranking logic
│   ├── __init__.py
│   ├── relevance.py     # Keyword/heuristic filtering
│   ├── dedup.py         # Deduplication engine
│   └── ranker.py        # Score and rank items
│
├── llm/                  # Perplexity AI integration
│   ├── __init__.py
│   ├── client.py        # Perplexity API wrapper
│   ├── prompts.py       # Credibility-focused prompts
│   └── analyzer.py      # Content analysis pipeline
│
├── formatters/           # Output formatters
│   ├── __init__.py
│   ├── blog.py          # Long-form blog articles
│   └── linkedin.py      # Short-form LinkedIn posts
│
├── publishers/           # Publishing modules
│   ├── __init__.py
│   ├── github_pages.py  # Markdown to GitHub Pages
│   └── linkedin_api.py  # LinkedIn UGC API
│
├── workflows/            # GitHub Actions
│   └── daily_scan.yml   # Automated daily workflow
│
├── utils/                # Utilities
│   ├── __init__.py
│   ├── cache.py         # Simple caching
│   └── logger.py        # Logging setup
│
├── data/                 # Runtime data
│   ├── cache/           # Cached fetches
│   ├── drafts/          # Generated drafts
│   └── published/       # Published content
│
├── tests/                # Unit tests
│
├── config.yaml           # Configuration
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── main.py               # CLI entry point
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Setup

```bash
# Clone repository
git clone <repo-url>
cd auto_blog

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configuration

Edit `config.yaml`:

```yaml
sources:
  arxiv:
    enabled: true
    categories: ["cs.AI", "cs.LG", "cs.CL"]
  
filters:
  max_age_days: 7
  keywords: ["LLM", "transformer", "diffusion", "RAG", "agent"]
  
llm:
  provider: "perplexity"
  model: "sonar-pro"
  
publishing:
  blog:
    enabled: true
    auto_publish: false
  linkedin:
    enabled: true
    auto_publish: false
```

### 3. Run

```bash
# Fetch and analyze
python main.py fetch

# Generate content
python main.py generate

# Review drafts
python main.py review

# Publish (with approval)
python main.py publish
```

## 🧪 Development Phases

### Week 1: Foundation
- [x] Project structure
- [ ] RSS/API fetchers
- [ ] Deduplication logic
- [ ] Markdown output

### Week 2: Intelligence
- [ ] Perplexity integration
- [ ] Multi-stage prompting
- [ ] Blog formatting
- [ ] GitHub Pages publishing

### Week 3: Distribution
- [ ] LinkedIn post generation
- [ ] LinkedIn API publishing
- [ ] Metrics & logging
- [ ] GitHub Actions automation

## 🔑 Environment Variables

```env
# Perplexity AI
PERPLEXITY_API_KEY=your_api_key_here

# LinkedIn (optional)
LINKEDIN_ACCESS_TOKEN=your_token_here

# GitHub (for publishing)
# Note: Use GH_PAGES_TOKEN instead of GITHUB_TOKEN (reserved by GitHub Actions)
GH_PAGES_TOKEN=your_github_token_here

# Medium (optional - for Medium publishing)
MEDIUM_INTEGRATION_TOKEN=your_medium_token_here
```

## 📊 Credibility Approach

This system uses **7-stage prompt engineering** to ensure factual, non-hype content:

1. **Fact extraction** - Ground truth only
2. **Engineer summary** - Technical, no fluff
3. **Impact analysis** - Evidence-based
4. **Application mapping** - Realistic use cases
5. **Blog synthesis** - Authoritative long-form
6. **LinkedIn formatting** - Credible short-form
7. **Self-audit** - Credibility check

## 🎯 Competitive Advantage

**Most people:** Repost + hype + zero insight

**This system:** Curate + explain + connect research to real systems

→ Positions you as a **thinking engineer**, not a content farmer

## 📝 License

MIT

## 🤝 Contributing

This is a personal project, but suggestions welcome via issues.
