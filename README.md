# arXiv Paper Scraper

A Python script to scrape arXiv papers and extract metadata into a CSV file.

## Features

The scraper extracts the following information from arXiv papers:
- **Paper ID**: Extracted from the URL
- **URL**: The original arXiv paper URL
- **og:title**: OpenGraph title meta tag content
- **category**: Main subject category (e.g., "Mathematics", "Computer Science")
- **subcategory**: Specific subcategory (e.g., "Numerical Analysis", "Machine Learning")
- **submitted_on**: Submission date (e.g., "14 Sep 2025")
- **abstract**: Full abstract text
- **scraped_at**: Timestamp when the data was scraped

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Automatic continuation scraping (current configuration)

The script automatically detects the maximum paper_id from the existing CSV file and continues scraping the next 100 papers:

```bash
python arxiv_scraper.py
```

**How it works:**
- Reads existing `arxiv_papers.csv` to find the highest paper number
- Automatically starts from the next sequential paper ID  
- Scrapes the next 100 papers in sequence
- Handles year/month transitions automatically (e.g., 2511 → 2512)

### Modify the batch size

To scrape a different number of papers, edit the `main()` function in `arxiv_scraper.py`:

```python
def main():
    max_paper_num, year_month_prefix = get_max_paper_id()
    start_id = max_paper_num + 1
    end_id = start_id + 49  # Change this number (default is 99 for 100 papers)
    # ... rest of the function
```

## Output

The script creates/appends to `arxiv_papers.csv` with the following columns:
- `paper_id`
- `url` 
- `og_title`
- `category`
- `subcategory`
- `submitted_on`
- `abstract`
- `scraped_at`

**Note**: All CSV fields are properly quoted to handle commas and special characters in text content.

## Example Output

```
Paper ID: 2511.00001
Title: Incarnations of the Fourier Transform in Algebraic Geometry
Category: Mathematics > Algebraic Geometry
Submitted: 14 Sep 2025
Abstract: An exploration into the uses of the Fourier transform in the areas of algebraic and arithmetic geometry...
Data saved to arxiv_papers.csv
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- pandas
- lxml

## Error Handling

The script includes error handling for:
- Network request failures
- HTML parsing errors
- Missing metadata elements

If scraping fails, check your internet connection and verify the arXiv URL is correct.