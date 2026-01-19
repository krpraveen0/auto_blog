# AI Research Publisher - Project Architecture

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│   arXiv      │  AI Blogs    │  Hacker News │    GitHub        │
│  (RSS API)   │  (RSS feeds) │ (Algolia API)│  (Search API)   │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬─────────┘
       │              │              │                 │
       ▼              ▼              ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SOURCE FETCHERS                             │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│ arxiv.py     │  blogs.py    │hackernews.py │   github.py      │
│              │              │              │                  │
│ • Fetch      │ • Fetch      │ • Fetch      │  • Fetch         │
│   papers     │   posts      │   stories    │    repos         │
│ • Parse      │ • Parse      │ • Filter     │  • Filter        │
│   metadata   │   RSS        │   by tags    │    by topics     │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬─────────┘
       │              │              │                 │
       └──────────────┴──────────────┴─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ All Items    │
                    │ (Combined)   │
                    └──────┬───────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FILTERING LAYER                              │
├──────────────────┬──────────────────┬──────────────────────────┤
│ relevance.py     │   dedup.py       │      ranker.py           │
│                  │                  │                          │
│ • Age filter     │ • URL hash       │  • Recency score         │
│ • Keywords       │ • Title sim.     │  • Source priority       │
│ • Exclusions     │ • Remove dupes   │  • Keyword match         │
│                  │                  │  • Engagement score      │
└──────┬───────────┴──────┬───────────┴──────┬───────────────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Top N Items    │
                  │ (Ranked)       │
                  └────────┬───────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PERPLEXITY LLM LAYER                           │
│                      (sonar-pro)                                 │
├─────────────────────────────────────────────────────────────────┤
│  client.py          │  prompts.py        │  analyzer.py         │
│                     │                    │                      │
│  • API wrapper      │  • System prompt   │  • 7-stage pipeline  │
│  • Rate limiting    │  • 7 stage prompts │  • Content analysis  │
│  • Retry logic      │  • Credibility     │  • Blog generation   │
│  • Error handling   │    guardrails      │  • LinkedIn gen.     │
└─────────────────────┴────────────────────┴──────────────────────┘
                           │
                           ▼
         ┌──────────────────────────────────┐
         │   7-STAGE CREDIBILITY PIPELINE    │
         ├──────────────────────────────────┤
         │ 1. Fact Extraction               │
         │ 2. Engineer Summary              │
         │ 3. Impact Analysis               │
         │ 4. Application Mapping           │
         │ 5. Blog Synthesis                │
         │ 6. LinkedIn Formatting           │
         │ 7. Credibility Check             │
         └─────────────┬────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   Analysis     │
              │   Results      │
              └────────┬───────┘
                       │
         ┏━━━━━━━━━━━━━┻━━━━━━━━━━━━━┓
         ▼                            ▼
┌────────────────────┐      ┌────────────────────┐
│  BLOG FORMATTER    │      │ LINKEDIN FORMATTER │
│  (blog.py)         │      │  (linkedin.py)     │
├────────────────────┤      ├────────────────────┤
│ • Markdown format  │      │ • 120 words max    │
│ • YAML frontmatter │      │ • Bullet points    │
│ • 900 words        │      │ • Hashtags         │
│ • References       │      │ • Hook + takeaway  │
└─────────┬──────────┘      └──────────┬─────────┘
          │                            │
          ▼                            ▼
   ┌────────────┐              ┌────────────────┐
   │ Blog Draft │              │ LinkedIn Draft │
   │  (.md)     │              │    (.txt)      │
   └──────┬─────┘              └────────┬───────┘
          │                             │
          │   ┌─────────────────────┐   │
          └──►│ Human Approval?     │◄──┘
              │ (Review & Approve)  │
              └─────────┬───────────┘
                        │ ✓ Approved
         ┏━━━━━━━━━━━━━━┻━━━━━━━━━━━━━┓
         ▼                             ▼
┌────────────────────┐       ┌────────────────────┐
│ GITHUB PUBLISHER   │       │ LINKEDIN PUBLISHER │
│ (github_pages.py)  │       │ (linkedin_api.py)  │
├────────────────────┤       ├────────────────────┤
│ • Commit to repo   │       │ • Post via UGC API │
│ • gh-pages branch  │       │ • Member network   │
│ • Jekyll format    │       │ • Public visibility│
└─────────┬──────────┘       └──────────┬─────────┘
          │                             │
          ▼                             ▼
   ┌────────────┐              ┌────────────────┐
   │ Blog Post  │              │ LinkedIn Post  │
   │ Published  │              │   Published    │
   └────────────┘              └────────────────┘
```

## 🔄 Data Flow

### 1. Ingestion Phase
```
Sources → Fetchers → Raw Items (JSON)
```
- Multiple sources fetched in parallel
- Each returns standardized item format
- Combined into single list

### 2. Filtering Phase
```
Raw Items → Relevance Filter → Deduplicator → Ranker → Top N
```
- Filter by age, keywords, exclusions
- Remove duplicates by URL and title similarity
- Score and rank by multiple factors
- Select top N for processing

### 3. Analysis Phase (7 Stages)
```
Item → [Stage 1..7] → Comprehensive Analysis
```
- Each stage builds on previous
- Sequential processing (no skipping)
- Results stored in analysis dict

### 4. Formatting Phase
```
Analysis → Blog Formatter → Markdown (.md)
Analysis → LinkedIn Formatter → Text (.txt)
```
- Parallel generation for both formats
- Different constraints per format
- Saved as drafts

### 5. Publishing Phase
```
Drafts → Human Review → Publishers → Live Content
```
- Manual approval required (by default)
- Can enable auto-publish in config
- GitHub commits or API posts

## 🗂️ Directory Structure

```
auto_blog/
│
├── sources/              # Data ingestion
│   ├── arxiv.py
│   ├── blogs.py
│   ├── hackernews.py
│   └── github.py
│
├── filters/              # Data filtering
│   ├── relevance.py
│   ├── dedup.py
│   └── ranker.py
│
├── llm/                  # LLM integration
│   ├── client.py         # Perplexity API
│   ├── prompts.py        # 7-stage prompts
│   └── analyzer.py       # Pipeline orchestrator
│
├── formatters/           # Output formatting
│   ├── blog.py
│   └── linkedin.py
│
├── publishers/           # Publishing
│   ├── github_pages.py
│   └── linkedin_api.py
│
├── utils/                # Utilities
│   ├── logger.py
│   └── cache.py
│
├── data/                 # Runtime data
│   ├── cache/           # HTTP cache
│   ├── fetched/         # Fetched items
│   ├── drafts/          # Generated drafts
│   │   ├── blog/
│   │   └── linkedin/
│   └── published/       # Published content
│
├── .github/workflows/    # Automation
│   ├── daily_scan.yml
│   └── weekly_digest.yml
│
├── config.yaml           # Configuration
├── main.py               # CLI entry point
└── requirements.txt      # Dependencies
```

## 🔑 Key Design Principles

### 1. Modularity
- Each component is independent
- Clear interfaces between modules
- Easy to test and extend

### 2. Configurability
- Single `config.yaml` for all settings
- Environment variables for secrets
- No hardcoded values

### 3. Credibility First
- 7-stage prompt pipeline
- Low temperature (0.3) for facts
- Explicit constraint prompts
- Self-audit stage

### 4. Human-in-the-Loop
- Approval required by default
- Review before publish
- Metrics tracking
- Quality over quantity

### 5. Extensibility
- Add new sources easily
- Add new prompt stages
- Add new publishers
- Plugin-style architecture

## 🧩 Component Dependencies

```
main.py
  ├─ sources.*
  ├─ filters.*
  ├─ llm.analyzer
  │   ├─ llm.client
  │   └─ llm.prompts
  ├─ formatters.*
  └─ publishers.*

llm.analyzer
  └─ Depends on: llm.client, llm.prompts

formatters.*
  └─ Depends on: llm.analyzer (for content generation)

publishers.*
  └─ Independent (only needs draft files)
```

## 🎯 Critical Paths

### Happy Path (Automated)
```
Sources → Fetch → Filter → Analyze → Format → Review → Publish
```

### Error Handling
- API failures → Retry with backoff
- Invalid content → Skip and log
- Rate limits → Sleep and continue
- Missing keys → Fail fast with clear error

## 🔒 Security Model

### API Keys (via .env)
```
PERPLEXITY_API_KEY  → llm/client.py
LINKEDIN_TOKEN      → publishers/linkedin_api.py
GH_PAGES_TOKEN        → publishers/github_pages.py
MEDIUM_INTEGRATION_TOKEN → publishers/medium_api.py
```

### GitHub Actions (Secrets)
```
Repository Secrets → Workflow → Environment variables
```

### No Credentials in Code
- All secrets from environment
- .env in .gitignore
- Example template provided

## 📊 Metrics & Monitoring

```
Metrics Collection:
  ├─ Items fetched (per source)
  ├─ Items filtered (pass rate)
  ├─ Content generated
  ├─ Content published
  └─ API usage (token consumption)

Storage: data/metrics.json
Format: Time-series JSON
Access: python main.py metrics
```

## 🚀 Deployment Options

### 1. Local (Development)
```bash
python main.py fetch
python main.py generate
python main.py publish
```

### 2. GitHub Actions (Production)
```
Schedule: Daily at 9 AM UTC
Trigger: Manual or automatic
Output: Artifacts + commits
```

### 3. Self-Hosted (Advanced)
```
Cron job on VPS
Docker container
K8s deployment
```

## 🎓 Prompt Engineering Architecture

### System Prompt (Global)
```
Role: AI researcher & engineer
Rules: Factual, precise, no hype
Applies to: ALL stages
```

### Stage Prompts (Sequential)
```
Stage 1: Extract facts → Ground truth
Stage 2: Summarize → Technical (150w)
Stage 3: Analyze impact → Evidence-based
Stage 4: Map applications → Realistic
Stage 5: Write blog → Long-form (900w)
Stage 6: Write LinkedIn → Short-form (120w)
Stage 7: Audit → Quality check
```

### Temperature Strategy
```
Analysis stages (1-4): 0.3 (factual)
Writing stages (5-6): 0.3 (still factual)
Audit stage (7): 0.3 (critical)
```

Low temperature throughout = High credibility

## 🔧 Configuration Schema

```yaml
sources:           # What to fetch
filters:           # What to keep
llm:               # How to analyze
formatting:        # How to format
publishing:        # Where to publish
scheduling:        # When to run
logging:           # How to log
```

Each section independent and optional.

## 📈 Scalability Considerations

### Current Design (Single Machine)
- Sequential processing
- Local file storage
- GitHub API limits
- Perplexity rate limits

### Future Enhancements
- Parallel LLM calls
- Database storage (SQLite/Postgres)
- Queue system (Redis/Celery)
- Multi-account rotation

## 🎯 The Competitive Edge

**What makes this system unique:**

1. **7-Stage Prompt Pipeline**
   - Most systems: 1 prompt
   - This system: 7 sequential prompts
   - Result: Higher credibility

2. **Constraint-Based Generation**
   - Forces structured output
   - Prevents hallucination
   - Explicit limitations

3. **Human-in-the-Loop**
   - Quality gate before publish
   - Maintains reputation
   - Learns from feedback

4. **Multi-Source Aggregation**
   - Broader coverage
   - Better signal detection
   - Trend identification

---

**Remember:** The architecture is designed for **credibility at scale**, not content farming. Quality is the moat. 🏰
