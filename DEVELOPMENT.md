# AI Research Publisher - Development Guide

## 🎯 Project Overview

This is a **personal AI research aggregator** that automatically:
1. Scans trusted AI/ML/LLM sources (arXiv, blogs, HN, GitHub)
2. Filters content using relevance heuristics
3. Analyzes using **Perplexity AI (sonar-pro model)**
4. Generates credible blog articles and LinkedIn posts
5. Publishes with human approval

## 🏗️ Architecture

### Clean Modular Design
```
Sources → Fetchers → Filters → LLM Analyzer → Formatters → Publishers
```

Each module is independent and testable.

### 7-Stage Credibility Pipeline

The LLM analysis uses **7 sequential prompts** to ensure factual, non-hype content:

1. **Fact Extraction** - Extract ground truth only
2. **Engineer Summary** - Technical summary (150 words, no fluff)
3. **Impact Analysis** - Evidence-based implications + constraints
4. **Application Mapping** - Realistic use cases with assumptions
5. **Blog Synthesis** - 800-1000 word authoritative article
6. **LinkedIn Formatting** - 120 word credible short-form
7. **Credibility Check** - Self-audit for quality

This pipeline is the **secret sauce** that separates this from generic content farms.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate
cd /workspaces/auto_blog

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your PERPLEXITY_API_KEY
```

### 2. Get Perplexity API Key

1. Go to: https://www.perplexity.ai/settings/api
2. Create an API key
3. Add to `.env`: `PERPLEXITY_API_KEY=pplx-your-key-here`

### 3. Initialize Project

```bash
python main.py init
```

This creates all necessary directories.

### 4. Test the Pipeline

```bash
# Fetch content from all sources
python main.py fetch

# Generate content for top 3 items
python main.py generate --count 3 --format both

# Review generated drafts
ls data/drafts/blog/
ls data/drafts/linkedin/

# View a blog draft
cat data/drafts/blog/<filename>.md

# View a LinkedIn draft
cat data/drafts/linkedin/<filename>.txt
```

## 📋 CLI Commands

### Fetch
```bash
# Fetch from all sources
python main.py fetch

# Fetch from specific source
python main.py fetch --source arxiv
python main.py fetch --source blogs
python main.py fetch --source hackernews
python main.py fetch --source github

# Disable caching
python main.py fetch --no-cache
```

### Generate
```bash
# Generate top 5 (default)
python main.py generate

# Generate specific count
python main.py generate --count 3

# Generate only blogs
python main.py generate --format blog

# Generate only LinkedIn
python main.py generate --format linkedin
```

### Review
```bash
# List all drafts
python main.py review
```

### Publish
```bash
# Publish with approval prompts
python main.py publish

# Publish only to blog
python main.py publish --platform blog

# Publish only to LinkedIn
python main.py publish --platform linkedin

# Auto-approve (use in automation)
python main.py publish --approve
```

### Metrics
```bash
# Show last 7 days
python main.py metrics

# Show last 30 days
python main.py metrics --days 30
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

### Sources
```yaml
sources:
  arxiv:
    enabled: true
    categories: ["cs.AI", "cs.LG", "cs.CL"]
    max_results: 20
```

### Filters
```yaml
filters:
  max_age_days: 7
  keywords:
    high_priority:
      - "LLM"
      - "transformer"
      - "RAG"
```

### LLM (Perplexity)
```yaml
llm:
  provider: "perplexity"
  model: "sonar-pro"
  generation_params:
    temperature: 0.3  # Low for factual content
    max_tokens: 2000
```

### Publishing
```yaml
publishing:
  blog:
    auto_publish: false  # Require manual approval
  linkedin:
    auto_publish: false
```

## 🤖 GitHub Actions Automation

### Daily Scan

The workflow in `.github/workflows/daily_scan.yml` runs automatically:

- **Schedule**: Daily at 9 AM UTC
- **Actions**:
  1. Fetch content from all sources
  2. Generate drafts for top 5 items
  3. Upload drafts as artifacts
  4. Save metrics

### Manual Trigger

You can also trigger manually:
1. Go to GitHub Actions tab
2. Select "Daily AI Research Scan"
3. Click "Run workflow"
4. Choose source and count

### Setup GitHub Secrets

Add these to your repository secrets:

```
PERPLEXITY_API_KEY=pplx-...
LINKEDIN_ACCESS_TOKEN=... (optional)
LINKEDIN_USER_ID=... (optional)
```

## 📝 Publishing Setup

### GitHub Pages (Blog)

1. Create a `gh-pages` branch
2. Add `GITHUB_TOKEN` secret (auto-created)
3. Set `GITHUB_REPO` in `.env` or as secret

Posts will be committed to `_posts/` folder in Jekyll format.

### LinkedIn

1. Create LinkedIn app: https://www.linkedin.com/developers/apps
2. Get access token with `w_member_social` scope
3. Add to `.env`:
   ```
   LINKEDIN_ACCESS_TOKEN=...
   LINKEDIN_USER_ID=...
   ```

## 🧪 Testing Individual Components

### Test Source Fetchers

```python
from sources.arxiv import ArxivFetcher
import yaml

config = yaml.safe_load(open('config.yaml'))
fetcher = ArxivFetcher(config['sources']['arxiv'])
papers = fetcher.fetch()
print(f"Fetched {len(papers)} papers")
print(papers[0])
```

### Test Perplexity Client

```python
from llm.client import PerplexityClient
import yaml

config = yaml.safe_load(open('config.yaml'))
client = PerplexityClient(config['llm'])

response = client.generate(
    system_prompt="You are a helpful AI assistant.",
    user_prompt="Explain transformers in one sentence."
)
print(response)
```

### Test Full Analysis

```python
from llm.analyzer import ContentAnalyzer
import yaml

config = yaml.safe_load(open('config.yaml'))
analyzer = ContentAnalyzer(config['llm'])

item = {
    'id': 'test_1',
    'title': 'New LLM Architecture',
    'url': 'https://example.com',
    'summary': 'A novel transformer architecture...',
    'source': 'arxiv'
}

analysis = analyzer.analyze(item)
print(analysis)
```

## 🎯 Phased Development

### ✅ Phase 1: Foundation (Complete)
- [x] Project structure
- [x] Source fetchers (arXiv, blogs, HN, GitHub)
- [x] Filtering and deduplication
- [x] Ranking system

### ✅ Phase 2: Intelligence (Complete)
- [x] Perplexity integration
- [x] 7-stage prompt pipeline
- [x] Content analyzer
- [x] Blog formatter
- [x] LinkedIn formatter

### ✅ Phase 3: Publishing (Complete)
- [x] GitHub Pages publisher
- [x] LinkedIn API publisher
- [x] Approval workflow
- [x] Metrics tracking

### ✅ Phase 4: Automation (Complete)
- [x] GitHub Actions workflows
- [x] Daily scan automation
- [x] Weekly digest

## 🔍 Prompt Engineering Strategy

The prompts are designed with **credibility guardrails**:

### Global Rules (System Prompt)
- Be factual and precise
- No exaggeration
- No marketing language
- Prefer technical clarity
- State uncertainties explicitly

### Stage-Specific Constraints

Each stage has specific output formats that force structured thinking:

**Fact Extraction:**
```
- Core contribution:
- Technical details:
- Explicit claims:
- Open questions / limitations:
```

**Impact Analysis:**
```
- Immediate implications:
- Long-term implications:
- Practical constraints:
```

This structure **prevents hallucination** and **enforces honesty**.

## 🚀 Extending the System

### Add New Source

1. Create `sources/newsource.py`:
```python
class NewSourceFetcher:
    def __init__(self, config):
        self.config = config
    
    def fetch(self):
        # Return list of dicts with keys:
        # id, title, url, summary, published, source
        return []
```

2. Add to `config.yaml`:
```yaml
sources:
  newsource:
    enabled: true
    api_key: "..."
```

3. Import in `main.py`

### Add New Prompt Stage

1. Add prompt to `llm/prompts.py`:
```python
NEW_STAGE_PROMPT = """..."""
```

2. Add to `config.yaml`:
```yaml
llm:
  prompt_stages:
    - "fact_extraction"
    - "new_stage"
    - "..."
```

### Add New Publisher

1. Create `publishers/newplatform.py`:
```python
class NewPlatformPublisher:
    def __init__(self, config):
        pass
    
    def publish(self, draft_path):
        # Publish and return True/False
        return True
```

2. Add to `main.py` publish command

## 📊 Metrics and Monitoring

Metrics are stored in `data/metrics.json`:

```json
[
  {
    "timestamp": "2026-01-13T10:00:00",
    "fetched": 45,
    "generated": 5,
    "published": 3
  }
]
```

View with:
```bash
python main.py metrics --days 7
```

## 🔐 Security Best Practices

1. **Never commit `.env`** - It's in `.gitignore`
2. **Use GitHub Secrets** for automation
3. **Rotate API keys** periodically
4. **Review generated content** before publishing
5. **Monitor API usage** (Perplexity has rate limits)

## 🐛 Troubleshooting

### "PERPLEXITY_API_KEY not set"
- Create `.env` file: `cp .env.example .env`
- Add your API key

### "No items found" after fetch
- Check if sources are enabled in `config.yaml`
- Check internet connection
- Check for API rate limits

### "Failed to generate content"
- Check Perplexity API key is valid
- Check API quota/credits
- Check logs in `logs/app.log`

### GitHub Actions failing
- Check repository secrets are set
- Check workflow permissions
- Check logs in Actions tab

## 📚 Resources

- **Perplexity API**: https://docs.perplexity.ai/
- **arXiv API**: https://arxiv.org/help/api
- **LinkedIn API**: https://learn.microsoft.com/en-us/linkedin/
- **GitHub API**: https://docs.github.com/en/rest
- **Hacker News API**: https://hn.algolia.com/api

## 🎓 Learning Path

1. **Start small**: Run fetch and generate for 1-2 items
2. **Inspect outputs**: Read generated drafts carefully
3. **Tune prompts**: Adjust prompts in `llm/prompts.py`
4. **Tune filters**: Adjust keywords in `config.yaml`
5. **Automate**: Enable GitHub Actions
6. **Monitor**: Track metrics and quality
7. **Iterate**: Refine based on published content performance

## 💡 Pro Tips

1. **Start with manual approval** - Don't auto-publish initially
2. **Review 10-20 pieces** before trusting automation
3. **Adjust temperature** - Lower = more factual, Higher = more creative
4. **Use source priority** - arXiv papers are usually higher quality
5. **Monitor engagement** - Track which content performs best
6. **Weekly batches** - Better than daily spam
7. **Add personal commentary** - Edit generated content to add your voice

## 🏆 Success Metrics

**Quality over quantity:**
- Aim for 3-5 pieces per week
- Each piece should add genuine insight
- Focus on emerging trends, not hype

**Positioning:**
- Technical depth (for engineers, not marketers)
- Balanced perspective (benefits + limitations)
- Real-world relevance (use cases + constraints)

## 🤝 Contributing

This is a personal project, but suggestions welcome via GitHub issues.

## 📄 License

MIT License - Use freely, build your own system!

---

**Remember:** The goal is to position yourself as a **thinking engineer** who understands AI deeply, not a content farmer who reposts headlines with hype.

The 7-stage prompt pipeline is your competitive advantage. Guard it, tune it, make it yours. 🚀
