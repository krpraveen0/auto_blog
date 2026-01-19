# GitHub Trending Repository Features - ELI5 Blog Generation

## Overview

This update enhances the auto_blog system to fetch comprehensive statistics from trending GitHub repositories and generate "Explain Like I'm 5" (ELI5) style blog articles that make complex technical projects accessible to everyone.

## New Features

### 1. Enhanced GitHub Repository Statistics

The GitHub fetcher now collects comprehensive statistics for each repository:

- **Basic Stats**: Stars, Forks, Watchers, Open Issues
- **Contributors**: Number of contributors
- **Languages**: Distribution of programming languages used
- **License**: Repository license information
- **Topics**: Associated topics and tags
- **Trending Metrics**: 
  - Stars per day (velocity)
  - Forks per day
  - Activity score
  - Days since creation/update
  - Recently active status

### 2. ELI5 (Explain Like I'm 5) Blog Generation

For GitHub repositories, the system now uses a special ELI5 analysis pipeline that generates accessible, beginner-friendly content:

#### ELI5 Analysis Stages:
1. **What Does It Do?** - Simple explanation with analogies
2. **How Does It Work?** - Breaking down the main components
3. **Why Does It Matter?** - Real-world impact and applications
4. **Getting Started** - Beginner-friendly guide

#### Blog Structure:
- Catchy introduction with relatable problem
- Simple explanation with analogies
- Key components breakdown
- Real-world applications
- Cool features highlight
- Getting started guide
- Community and adoption stats
- Repository statistics display

### 3. Database Enhancements

Added 19 new columns to the `papers` table for GitHub statistics:

```sql
- stars, forks, watchers, open_issues
- language, topics, license, languages
- contributors_count, owner_type
- stars_per_day, forks_per_day, activity_score
- days_since_creation, days_since_update
- is_recently_active, has_wiki, has_pages, has_discussions
```

New database methods:
- `export_blogs_for_pages()` - Export blogs with metadata for GitHub Pages
- `get_blog_statistics()` - Get comprehensive database statistics

### 4. GitHub Pages Integration

Automatically generate a beautiful, searchable index page for published blogs:

- **index.html** - Responsive web interface with search
- **blogs.json** - JSON API for blogs data
- **stats.json** - Database statistics

Features:
- Real-time search by title, language, or topic
- Repository statistics display (stars, forks, etc.)
- Responsive grid layout
- Filtering by source and language
- Beautiful gradient header
- Statistics dashboard

## Usage

### Fetching GitHub Repositories

```bash
# Fetch trending repositories (all sources including GitHub)
python main.py fetch --source github

# Fetch from all sources
python main.py fetch --source all
```

### Generating ELI5 Blogs

```bash
# Generate blog articles (automatically uses ELI5 for GitHub repos)
python main.py generate --format blog --count 5

# Generate all formats
python main.py generate --format all --count 3
```

The system automatically detects GitHub repositories and uses the ELI5 analysis pipeline.

### Viewing Database Statistics

```bash
# Show comprehensive database statistics
python main.py db-stats
```

Output includes:
- Total papers and GitHub repos
- Content by type (blog, linkedin, medium)
- Content by status (drafted, published)
- Top programming languages

### Generating GitHub Pages Index

```bash
# Generate GitHub Pages index from published blogs
python main.py generate-index
```

This creates:
- `docs/index.html` - Main page
- `docs/blogs.json` - JSON data
- `docs/stats.json` - Statistics

### Enabling GitHub Pages

1. Commit the `docs/` folder to your repository
2. Go to **Settings > Pages** in your GitHub repository
3. Set **Source** to "Deploy from a branch"
4. Select your branch and `/docs` folder
5. Your site will be available at `https://USERNAME.github.io/REPO-NAME/`

## Configuration

The GitHub fetcher configuration in `config.yaml`:

```yaml
sources:
  github:
    enabled: true
    topics: ["machine-learning", "artificial-intelligence", "llm", "transformers"]
    min_stars: 100  # Minimum stars for trending repos
    max_results: 10  # Number of repos per topic
```

## Example Output

### Blog Article Structure for GitHub Repos

```markdown
---
layout: post
title: "username/awesome-ml-project"
date: 2026-01-19
categories: [AI, Research]
tags:
  - machine-learning
  - Open Source
  - Python
source: github
source_url: https://github.com/username/awesome-ml-project
---

# Introduction
Imagine you want to teach your computer to recognize your voice...

# What Is It?
This project is like a super-smart translator...

# How Does It Work?
Think of it like a kitchen where...

# Why Should You Care?
This matters because...

# Cool Features
- Feature 1: Easy to use...
- Feature 2: Works fast...

# Getting Started
To start using this project...

---

## Source

**Original Publication:** [github](https://github.com/username/awesome-ml-project)

### Repository Statistics
- ⭐ Stars: 5,432
- 🔱 Forks: 876
- 👀 Watchers: 234
- 👥 Contributors: 42
- 📋 Open Issues: 45
- 💻 Primary Language: Python
- 📜 License: MIT
- 📈 Growth: 110.2 stars/day
- 🔥 Recently Active
- 🏷️ Topics: `machine-learning`, `deep-learning`, `neural-networks`
```

## LLM Prompts

The system uses specialized prompts for GitHub repositories:

- `GITHUB_ELI5_SYSTEM_PROMPT` - Sets friendly, educational tone
- `GITHUB_ELI5_WHAT_PROMPT` - Explains what the project does
- `GITHUB_ELI5_HOW_PROMPT` - Explains how it works
- `GITHUB_ELI5_WHY_PROMPT` - Explains why it matters
- `GITHUB_ELI5_GETTING_STARTED_PROMPT` - Getting started guide
- `GITHUB_ELI5_BLOG_PROMPT` - Full blog article synthesis

## Architecture Changes

### Files Modified

1. **sources/github.py**
   - Added `fetch_repo_details()` for detailed statistics
   - Added `calculate_trending_metrics()` for velocity calculations
   - Enhanced `fetch()` to collect comprehensive data

2. **utils/database.py**
   - Added 19 new columns for GitHub statistics
   - Auto-migration support
   - Added `export_blogs_for_pages()`
   - Added `get_blog_statistics()`

3. **llm/prompts.py**
   - Added 6 new ELI5 prompts
   - Added `get_github_eli5_system_prompt()`

4. **llm/analyzer.py**
   - Added `analyze_github_eli5()` method
   - Added `generate_github_eli5_blog()` method

5. **formatters/blog.py**
   - Updated `format()` to detect GitHub repos and use ELI5
   - Enhanced `_generate_source_section()` with repository statistics

6. **main.py**
   - Updated `generate` command to use ELI5 for GitHub
   - Added `db-stats` command
   - Added `generate-index` command

### New Files

1. **generate_pages_index.py**
   - Generates GitHub Pages index.html
   - Creates JSON API endpoints
   - Beautiful, responsive design

## Benefits

1. **Accessibility**: Complex technical projects explained in simple terms
2. **Comprehensive Statistics**: Full repository metrics tracked and displayed
3. **Beautiful Presentation**: Professional GitHub Pages site
4. **Searchable**: Easy to find blogs by topic, language, or keyword
5. **Community Focused**: Shows stars, forks, contributors to highlight community
6. **Beginner Friendly**: ELI5 approach makes technology accessible to everyone

## Future Enhancements

- Add more sources (GitLab, Bitbucket)
- Add trending graphs and charts
- Add comparison between repositories
- Add automated scheduling for fetching trending repos
- Add RSS feed generation
- Add tags cloud visualization

## Testing

All features have been tested:

- ✅ Database migration with 19 new columns
- ✅ Mock repository data storage and retrieval
- ✅ ELI5 prompt generation
- ✅ GitHub Pages index generation
- ✅ CLI commands (db-stats, generate-index)
- ✅ Statistics export

## License

MIT - Same as the main project
