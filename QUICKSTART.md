# AI Research Publisher - Quick Start

## 🎯 What This Does

Automatically finds, analyzes, and converts AI/ML research into **credible blog posts and LinkedIn content**.

**Key Features:**
- Scans arXiv, blogs, HN, GitHub
- Uses Perplexity AI (sonar-pro)
- 7-stage credibility-focused prompts
- No hype, only factual content
- Human approval before publishing

## ⚡ Quick Setup

### 1. Install

```bash
# Clone repository
git clone <your-repo-url>
cd auto_blog

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure

```bash
# Edit .env file
nano .env

# Add your Perplexity API key:
PERPLEXITY_API_KEY=pplx-your-key-here
```

Get API key: https://www.perplexity.ai/settings/api

### 3. Test

```bash
# Activate virtual environment
source venv/bin/activate

# Fetch AI/ML content
python main.py fetch

# Generate 2 articles
python main.py generate --count 2

# Review drafts
ls data/drafts/blog/
cat data/drafts/blog/*.md
```

## 📋 Main Commands

```bash
# Fetch from all sources
python main.py fetch

# Fetch from specific source
python main.py fetch --source arxiv

# Generate content
python main.py generate --count 5

# Review drafts
python main.py review

# Publish (with approval)
python main.py publish
```

## 🔧 Configuration

Edit `config.yaml`:

```yaml
# Which sources to scan
sources:
  arxiv:
    enabled: true
    categories: ["cs.AI", "cs.LG"]

# Filter keywords
filters:
  keywords:
    high_priority:
      - "LLM"
      - "transformer"
      - "RAG"

# LLM settings
llm:
  model: "sonar-pro"
  temperature: 0.3  # Low = more factual
```

## 🤖 Automation

GitHub Actions runs daily automatically:
- Fetches new content
- Generates drafts
- Saves as artifacts
- Deploys to GitHub Pages (when docs/ folder is updated)

To enable:
1. Add repository secret: `PERPLEXITY_API_KEY`
2. Enable GitHub Pages: Settings > Pages > Source: GitHub Actions
3. Workflows run automatically

Your site will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/` (e.g., `https://krpraveen0.github.io/auto_blog/`)

## 📖 Documentation

- **README.md** - Project overview
- **DEVELOPMENT.md** - Detailed guide
- **config.yaml** - Configuration options

## 🎓 Learning Path

1. ✅ Run setup
2. ✅ Test fetch command
3. ✅ Generate 1-2 pieces
4. ✅ Review output quality
5. ✅ Adjust prompts/config
6. ✅ Enable automation
7. ✅ Start publishing weekly

## 🔑 The Secret Sauce

**7-Stage Prompt Pipeline:**
1. Fact extraction (ground truth only)
2. Engineer summary (technical, no fluff)
3. Impact analysis (evidence-based)
4. Application mapping (realistic use cases)
5. Blog synthesis (authoritative long-form)
6. LinkedIn formatting (credible short-form)
7. Credibility check (self-audit)

This prevents hype and ensures quality.

## 🚨 Important

- **Start with manual approval** - Don't auto-publish initially
- **Review 10-20 pieces** before trusting the system
- **Quality > Quantity** - Aim for 3-5 pieces/week, not daily spam
- **Add your voice** - Edit generated content to add personal insights

## ❓ Troubleshooting

**"No items found"**
- Check `config.yaml` sources are enabled
- Check internet connection

**"API key error"**
- Verify `PERPLEXITY_API_KEY` in `.env`
- Check API quota/credits

**"Generated content is too generic"**
- Lower temperature in config
- Adjust prompts in `llm/prompts.py`
- Add more specific keywords

## 🎯 Goal

Position yourself as a **thinking engineer** who understands AI deeply, not a content farmer who reposts hype.

**Most people:** Repost + hype + zero insight

**You:** Curate + explain + connect research to real systems

---

For detailed documentation, see [DEVELOPMENT.md](DEVELOPMENT.md)

For architecture details, see [README.md](README.md)
