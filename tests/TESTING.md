# Testing Guide

## Running Tests

### Install test dependencies
```bash
pip install pytest pytest-cov pytest-mock
```

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_basic.py -v
```

### Run specific test
```bash
pytest tests/test_basic.py::test_config_exists -v
```

## Test Categories

### Unit Tests (`test_basic.py`)
- No API keys required
- Tests module initialization
- Tests data structures
- Tests filtering logic

### Integration Tests (`test_integration.py`)
- Requires API keys
- Tests Perplexity client
- Tests full analysis pipeline
- Tests publishers (if credentials available)

## Before Running Integration Tests

Set environment variables:
```bash
export PERPLEXITY_API_KEY=pplx-your-key
export GITHUB_TOKEN=ghp-your-token
export LINKEDIN_ACCESS_TOKEN=your-token
```

Or create `.env` file.

## Manual Testing

### Test Source Fetchers

```bash
# Test arXiv
python -c "
from sources.arxiv import ArxivFetcher
import yaml

config = yaml.safe_load(open('config.yaml'))
fetcher = ArxivFetcher(config['sources']['arxiv'])
papers = fetcher.fetch()
print(f'Fetched {len(papers)} papers')
for p in papers[:3]:
    print(f'- {p[\"title\"][:60]}...')
"

# Test blogs
python -c "
from sources.blogs import BlogFetcher
import yaml

config = yaml.safe_load(open('config.yaml'))
fetcher = BlogFetcher(config['sources']['blogs'])
posts = fetcher.fetch()
print(f'Fetched {len(posts)} blog posts')
for p in posts[:3]:
    print(f'- {p[\"title\"][:60]}...')
"
```

### Test Filtering

```bash
python -c "
from filters.relevance import RelevanceFilter
from filters.dedup import Deduplicator
from filters.ranker import ContentRanker
import yaml
import json

config = yaml.safe_load(open('config.yaml'))

# Mock items
items = [
    {
        'id': '1',
        'title': 'New LLM Architecture for Transformers',
        'url': 'https://example.com/1',
        'summary': 'A novel transformer-based LLM architecture',
        'published': '2026-01-10',
        'source': 'arxiv',
        'source_priority': 'high'
    },
    {
        'id': '2',
        'title': 'Blockchain and AI',
        'url': 'https://example.com/2',
        'summary': 'Combining blockchain with AI',
        'published': '2026-01-10',
        'source': 'blog',
        'source_priority': 'medium'
    }
]

# Filter
rf = RelevanceFilter(config['filters'])
filtered = rf.filter(items)
print(f'Filtered: {len(items)} -> {len(filtered)} items')

# Rank
ranker = ContentRanker(config['filters']['ranking'])
ranked = ranker.rank(filtered)
print('Top item:', ranked[0]['title'] if ranked else 'None')
"
```

### Test Perplexity Client

```bash
python -c "
from llm.client import PerplexityClient
import yaml
import os

if not os.getenv('PERPLEXITY_API_KEY'):
    print('ERROR: PERPLEXITY_API_KEY not set')
    exit(1)

config = yaml.safe_load(open('config.yaml'))
client = PerplexityClient(config['llm'])

response = client.generate(
    system_prompt='You are a helpful AI assistant.',
    user_prompt='Explain transformers in one sentence.'
)

print('Response:', response)
"
```

### Test Full Pipeline

```bash
# Fetch
python main.py fetch --source arxiv

# Check output
ls -lh data/fetched/
cat data/fetched/latest.json | head -20

# Generate (requires API key)
python main.py generate --count 1

# Check drafts
ls -lh data/drafts/blog/
ls -lh data/drafts/linkedin/
```

## Troubleshooting Tests

### ImportError
```bash
# Make sure you're in project root
cd /workspaces/auto_blog

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### API Errors
```bash
# Check API key is set
echo $PERPLEXITY_API_KEY

# Or check .env file
cat .env | grep PERPLEXITY
```

### Directory Errors
```bash
# Initialize project
python main.py init
```

## Expected Test Results

### test_basic.py (should all pass)
```
✓ test_config_exists
✓ test_required_modules
✓ test_data_directories
✓ test_prompts_available
✓ test_arxiv_fetcher_init
✓ test_relevance_filter_init
✓ test_deduplicator
✓ test_ranker
✓ test_cache
✓ test_logger
```

### test_integration.py (skipped if no API keys)
```
✓ test_perplexity_client (or SKIPPED)
✓ test_content_analyzer (or SKIPPED)
✓ test_github_publisher_init (or SKIPPED)
```

## Performance Testing

### Measure fetch time
```bash
time python main.py fetch
```

### Measure generation time
```bash
time python main.py generate --count 5
```

### Check API usage
Monitor Perplexity dashboard for token consumption.

## Quality Testing

### Generate sample content
```bash
python main.py fetch
python main.py generate --count 3
```

### Review manually
```bash
# Read blog drafts
for file in data/drafts/blog/*.md; do
    echo "=== $file ==="
    head -50 "$file"
    echo ""
done

# Read LinkedIn drafts
for file in data/drafts/linkedin/*.txt; do
    echo "=== $file ==="
    cat "$file"
    echo ""
done
```

### Check for quality indicators
- ✓ No exaggerated claims
- ✓ Includes limitations
- ✓ Technical terminology correct
- ✓ Source attribution present
- ✓ Proper markdown formatting

## Continuous Testing

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/test_basic.py -v
      
      - name: Run integration tests
        env:
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
        run: pytest tests/test_integration.py -v
```

## Test Checklist

Before deployment:
- [ ] All unit tests pass
- [ ] Integration tests pass (with API keys)
- [ ] Manual fetch works
- [ ] Manual generate works (quality check)
- [ ] Config file validates
- [ ] .env.example is up to date
- [ ] Documentation is accurate
- [ ] GitHub Actions workflow tested
