# arXiv Research Intelligence Platform

> Data pipeline for Computer Science research papers from arXiv.org

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Papers: 110K+](https://img.shields.io/badge/papers-110K+-green.svg)]()

## Overview

Automated pipeline that:
1. **Scrapes** papers from arXiv (110K+ collected)
2. **Summarizes** abstracts with AI (Codex CLI)  
3. **Filters** by research subcategory (48 areas)
4. **Visualizes** trends over time

## Structure

```
arXiv/
├── ingestion/      # arxiv_scraper.py - Data collection
├── enrichment/     # AI summarization pipeline
├── analysis/       # Category filtering tools
├── visualization/  # Interactive dashboard
├── data/          # Monthly CSV files (111K+ papers)
└── config/        # Prompt templates
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Scrape papers (auto-continues from last ID)
cd ingestion && python arxiv_scraper.py

# Add AI summaries
cd enrichment && python batch_summarizer.py

# Generate dashboard
cd visualization && python leaderboard_viz.py
```

## Data Schema

CSV files in `data/` folder:
```csv
paper_id,url,og_title,category,subcategory,submitted_on,abstract,summary,scraped_at
"2511.00010","https://arxiv.org/abs/2511.00010","Title...","Computer Science","Machine Learning","15-Oct-25","Abstract...","Summary...","2025-11-08"
```

## Key Features

- **Smart Continuation**: Automatically resumes from last scraped paper
- **AI Summaries**: 20-25 word summaries via Codex CLI
- **Rate Limiting**: 1 second delay between requests  
- **Interactive Charts**: Monthly trends with Chart.js
- **Category Filtering**: Extract papers by research area

## License

MIT
