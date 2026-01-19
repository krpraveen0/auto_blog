# AI Research Publisher

**A personal AI research editor that scans trusted sources, filters signal from noise, and converts updates into blog-ready articles and LinkedIn posts.**

## 🆕 New: GitHub Trending + ELI5 Features

This system now includes **enhanced GitHub repository tracking** with comprehensive statistics and **ELI5 (Explain Like I'm 5) blog generation**:

- 📊 **Comprehensive GitHub Stats**: Stars, forks, watchers, contributors, trending metrics
- 🎓 **ELI5 Blog Generation**: Makes complex technical projects accessible with simple language and analogies
- 🌐 **GitHub Pages Integration**: Automatically generated searchable index of published blogs
- 💾 **Enhanced Database**: SQLite storage with 19+ fields for repository statistics
- 🔍 **Search & Filter**: Beautiful web interface to browse and search blogs

[📖 Read the full documentation](./GITHUB_ELI5_FEATURES.md)

## 🎯 What This Does

- **Scans** trusted AI/ML/LLM sources (arXiv, company blogs, Hacker News, **GitHub trending repos**)
- **Filters** using relevance heuristics and deduplication
- **Analyzes** using Perplexity AI (sonar-pro model) for credible insights
- **Generates** blog articles (800-1000 words with **ELI5 style for GitHub**), LinkedIn posts (120 words), and comprehensive Medium articles (2000+ words with Mermaid diagrams)
- **Stores** all content in SQLite database with comprehensive metadata
- **Publishes** to GitHub Pages (with searchable index), LinkedIn, and Medium (with approval flow)
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
[ Blog + LinkedIn + Medium Publisher ]
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
│   ├── linkedin.py      # Short-form LinkedIn posts
│   └── medium.py        # Comprehensive Medium articles with diagrams
│
├── publishers/           # Publishing modules
│   ├── __init__.py
│   ├── github_pages.py  # Markdown to GitHub Pages
│   ├── linkedin_api.py  # LinkedIn UGC API
│   └── medium_api.py    # Medium Integration Token API
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
python main.py fetch --source github  # Fetch GitHub trending repos only

# Generate content (choose format: blog, linkedin, medium, or all)
# GitHub repos automatically get ELI5 (Explain Like I'm 5) style blogs!
python main.py generate --format blog --count 3      # Blog articles with ELI5 for GitHub
python main.py generate --format medium --count 1    # Comprehensive Medium article with diagrams
python main.py generate --format all --count 2       # Generate all formats

# Review drafts
python main.py review

# View database statistics
python main.py db-stats

# Generate GitHub Pages index (searchable website)
python main.py generate-index

# Publish (with approval)
python main.py publish --platform medium --medium-status draft
```

### 4. Enable GitHub Pages (NEW!)

After generating some blogs, create a beautiful searchable website:

```bash
# Generate the GitHub Pages site
python main.py generate-index

# Commit and push the docs/ folder
git add docs/
git commit -m "Add GitHub Pages site"
git push

# Then in your GitHub repository:
# Settings > Pages > Source: Deploy from branch > Select branch and /docs folder
# Your site will be at: https://USERNAME.github.io/REPO-NAME/
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

This system uses **comprehensive multi-stage prompt engineering** to ensure factual, non-hype content:

### Standard Analysis (7 stages for blog & LinkedIn):
1. **Fact extraction** - Ground truth only
2. **Engineer summary** - Technical, no fluff
3. **Impact analysis** - Evidence-based
4. **Application mapping** - Realistic use cases
5. **Blog synthesis** - Authoritative long-form
6. **LinkedIn formatting** - Credible short-form
7. **Self-audit** - Credibility check

### Comprehensive Analysis (13 stages for Medium):
All 7 standard stages PLUS:
8. **Medium synthesis** - Deep-dive article (2000+ words)
9. **Methodology extraction** - Detailed research approach
10. **Results analysis** - In-depth findings breakdown
11. **Architecture diagram** - Visual system structure (Mermaid)
12. **Flow diagram** - Process visualization (Mermaid)
13. **Comparison diagram** - vs baseline/prior work (Mermaid)

## 🎯 Competitive Advantage

**Most people:** Repost + hype + zero insight

**This system:** Curate + explain + connect research to real systems

→ Positions you as a **thinking engineer**, not a content farmer

## 🚀 Medium Integration (NEW!)

### What's Special About Medium Articles

This system generates **comprehensive research analysis** specifically designed for Medium:

**Content Features:**
- 2000+ words of detailed analysis
- Complete paper breakdown from introduction to conclusion
- **Mermaid diagrams** embedded directly in articles:
  - System architecture visualization
  - Process flow diagrams
  - Comparison with baseline methods
- Methodology deep-dive
- Results analysis with specific metrics
- Real-world applications
- Future implications

**Medium-Specific Formatting:**
- Clean Markdown that Medium renders beautifully
- Proper heading hierarchy
- Code blocks for diagrams
- Rich metadata (tags, canonical URLs)

### Setup Medium Publishing

1. **Get Integration Token:**
   ```bash
   # Visit: https://medium.com/me/settings
   # Scroll to "Integration tokens" section
   # Enter description: "Auto Blog Publisher"
   # Click "Get integration token"
   # Copy the token (shown only once!)
   ```

2. **Add to Environment:**
   ```bash
   # Add to .env file
   MEDIUM_INTEGRATION_TOKEN=your_token_here
   
   # Or export directly
   export MEDIUM_INTEGRATION_TOKEN=your_token_here
   ```

3. **Generate and Publish:**
   ```bash
   # Generate comprehensive Medium article with diagrams
   python main.py generate --format medium --count 1
   
   # Review the generated content
   cat data/drafts/medium/*.md
   
   # Publish as draft (review on Medium before making public)
   python main.py publish --platform medium --medium-status draft
   
   # Or publish directly as public
   python main.py publish --platform medium --medium-status public
   ```

### Automated Medium Publishing

Use GitHub Actions for scheduled publishing:

1. **Add Secrets:**
   - Go to Settings > Secrets and variables > Actions
   - Add `MEDIUM_INTEGRATION_TOKEN`
   - Add `PERPLEXITY_API_KEY` (if not already added)

2. **Workflows Available:**
   - `publish_medium_manual.yml` - On-demand publishing with topic
   - `publish_medium_scheduled.yml` - Weekly automatic publishing

3. **Manual Trigger:**
   - Go to Actions tab
   - Select "Publish Medium - Manual"
   - Click "Run workflow"
   - Choose options:
     - Generate new content or use existing drafts
     - Set publish status (draft/public/unlisted)
     - Number of articles to publish

### Why Use Medium?

**Advantages:**
- Built-in audience and discovery
- Professional reading experience
- SEO benefits
- Easy sharing and curation
- No hosting required
- Monetization options

**Best Practices:**
- Publish as `draft` first to review on Medium's interface
- Use meaningful tags (max 5)
- Add a compelling title and subtitle
- Review diagrams render correctly
- Check formatting before making public

## 📝 License

MIT

## 🤝 Contributing

This is a personal project, but suggestions welcome via issues.
