# GitHub Copilot Instructions

1. Never use em dashes
2. In titles & headers: Never use Title Case in headings, only sentence case

## What This Repository Does

Data pipeline for Computer Science research papers from arXiv.org:
1. Scrapes papers from arXiv
2. Summarizes abstracts with AI (Codex CLI)
3. Filters papers by subcategory
4. Creates visualization dashboard

**Current data:** 110,000+ papers across 11 months (Jan-Nov 2025)

## Folder Structure

```
arXiv/
├── ingestion/         # arxiv_scraper.py - Scrapes arXiv, filters CS papers
├── enrichment/        # codex_abstract_summarizer.py, batch_summarizer.py - AI summaries
├── analysis/          # filter_by_subcategory.py - Category filtering
├── visualization/     # leaderboard_viz.py - HTML dashboard generator
├── data/              # Monthly CSV files (YYMM_arxiv_papers.csv)
└── config/            # Prompt templates
```

## CSV Schema

Located in `data/` folder as `YYMM_arxiv_papers.csv`:
```
paper_id,url,og_title,category,subcategory,submitted_on,abstract,summary,scraped_at
```

- `paper_id`: arXiv ID (YYMM.NNNNN format)
- `abstract`: Full paper abstract
- `summary`: AI-generated 20-25 word summary (may be empty)
- `subcategory`: One of 48 CS research areas

## How Scripts Work

### arxiv_scraper.py
- Reads last paper_id from CSV, continues from next ID
- Filters only Computer Science papers
- 1 second delay between requests
- Saves to `data/YYMM_arxiv_papers.csv`

### codex_abstract_summarizer.py
- Uses `subprocess.run()` to call Codex CLI
- Command: `codex exec [prompt] < /dev/null`
- Returns 20-25 word summaries
- Prompt: "Describe what they built/discovered in 20-25 words. Be specific and clear, but cut unnecessary words."

### batch_summarizer.py
- Processes DataFrames with multiple abstracts
- Calls codex_abstract_summarizer for each row
- Continues on individual failures

### filter_by_subcategory.py
- Reads all CSV files from `data/`
- Filters by subcategory
- Exports to `sample_outputs/`

### leaderboard_viz.py
- Aggregates data from all CSVs in `data/`
- Generates `arxiv_leaderboard.html` with Chart.js
- Shows trends over time

## Import Paths

All scripts use relative imports:
```python
# From enrichment/
df = pd.read_csv('../data/2511_arxiv_papers.csv')

# From visualization/
csv_files = glob.glob('../data/*arxiv_papers.csv')
```

## Key Notes

- Summary column is empty until enrichment runs
- Paper IDs are sequential - scraper auto-continues
- CSV files are UTF-8 encoded
- All paths are relative to script location
