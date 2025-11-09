#!/usr/bin/env python3
"""
arXiv Paper Scraper

This script scrapes arXiv papers and extracts metadata including:
- og:title (OpenGraph title)
- Category and subcategory information
- Submission date (cleaned format)
- Abstract content

The data is saved to a CSV file for further analysis.

Usage:
    python arxiv_scraper.py [YYMM]
    
    YYMM (optional): Year-month prefix (e.g., 2511 for November 2025)
                     If not provided, uses current year-month
"""

import requests
import csv
import re
import time
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from datetime import datetime

def scrape_arxiv_paper(url):
    """
    Scrape an arXiv paper page and extract metadata.
    
    Args:
        url (str): The arXiv paper URL
        
    Returns:
        dict: Dictionary containing extracted metadata
    """
    try:
        # Send GET request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract og:title
        og_title_tag = soup.find('meta', property='og:title')
        og_title = og_title_tag.get('content', '') if og_title_tag else ''
        
        # Extract submission date from citation_online_date meta tag
        submitted_on = ''
        citation_date_tag = soup.find('meta', attrs={'name': 'citation_online_date'})
        if citation_date_tag:
            submitted_on = citation_date_tag.get('content', '').replace('/', '-')
        
        # Extract abstract content
        abstract_content = ''
        content_inner = soup.find('div', id='content-inner')
        if content_inner:
            abs_div = content_inner.find('div', id='abs')
            if abs_div:
                # Look for the abstract text (usually in a blockquote or div after the dateline)
                abstract_blockquote = abs_div.find('blockquote', class_='abstract')
                if abstract_blockquote:
                    abstract_content = abstract_blockquote.get_text(strip=True)
                    # Remove "Abstract:" prefix if present
                    abstract_content = re.sub(r'^Abstract:\s*', '', abstract_content)
        
        # Extract category and subcategory from leftcolumn
        category = ''
        subcategory = ''
        leftcolumn = soup.find('div', class_='leftcolumn')
        if leftcolumn:
            subheader = leftcolumn.find('div', class_='subheader')
            if subheader:
                h1_tag = subheader.find('h1')
                if h1_tag:
                    category_text = h1_tag.get_text(strip=True)
                    # Parse format like "Mathematics > Numerical Analysis"
                    if ' > ' in category_text:
                        parts = category_text.split(' > ', 1)
                        category = parts[0].strip()
                        subcategory = parts[1].strip()
                    else:
                        # If no subcategory, put everything in category
                        category = category_text
        
        # Extract paper ID from URL
        paper_id = url.split('/')[-1] if '/' in url else url
        
        return {
            'paper_id': paper_id,
            'url': url,
            'og_title': og_title,
            'category': category,
            'subcategory': subcategory,
            'submitted_on': submitted_on,
            'abstract': abstract_content,
            'scraped_at': datetime.now().isoformat()
        }
        
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing content from {url}: {e}")
        return None

def save_to_csv(data, filename):
    """
    Save scraped data to CSV file.
    
    Args:
        data (dict): Paper metadata
        filename (str): CSV filename
    """
    file_exists = os.path.isfile(filename)
    
    # Define CSV fieldnames
    fieldnames = ['paper_id', 'url', 'og_title', 'category', 'subcategory', 'submitted_on', 'abstract', 'scraped_at']
    
    # Columns that should have quotes (all text columns except url)
    quoted_columns = {'paper_id', 'og_title', 'category', 'subcategory', 'submitted_on', 'abstract', 'scraped_at'}
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        # Write header if file is new
        if not file_exists:
            csvfile.write(','.join(fieldnames) + '\n')
        
        # Build the CSV row manually
        row_parts = []
        for field in fieldnames:
            value = str(data.get(field, ''))
            if field in quoted_columns:
                # Escape quotes by doubling them and wrap in quotes
                escaped_value = value.replace('"', '""')
                row_parts.append(f'"{escaped_value}"')
            else:
                # URL - no quotes
                row_parts.append(value)
        
        csvfile.write(','.join(row_parts) + '\n')
    
    print(f"Data saved to {filename}")

def get_max_paper_id(filename):
    """
    Get the maximum paper_id from the existing CSV file.
    
    Args:
        filename (str): CSV filename
        
    Returns:
        tuple: (max_paper_number, year_month_prefix) or (0, prefix_from_filename) if no file exists
    """
    # Extract year_month prefix from filename (e.g., "2511" from "2511_arxiv_papers.csv")
    default_prefix = filename.split('_')[0] if '_' in filename else '2511'
    
    if not os.path.isfile(filename):
        print(f"No existing CSV file found. Starting from {default_prefix}.00001")
        return 0, default_prefix
    
    try:
        paper_numbers = []
        latest_prefix = '2511'  # default
        
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                paper_id = row['paper_id'].strip().strip('"')  # Remove quotes if present
                
                # Extract year.month and paper number from format like "2511.00010"
                match = re.match(r'(\d{4})\.(\d{5})', paper_id)
                if match:
                    year_month = match.group(1)
                    paper_num = int(match.group(2))
                    paper_numbers.append(paper_num)
                    latest_prefix = year_month  # Keep track of the latest prefix
        
        if not paper_numbers:
            print(f"No valid paper IDs found. Starting from {default_prefix}.00001")
            return 0, default_prefix
        
        max_paper_num = max(paper_numbers)
        print(f"Found maximum paper ID: {latest_prefix}.{max_paper_num:05d}")
        return max_paper_num, latest_prefix
        
    except Exception as e:
        print(f"Error reading CSV file: {e}. Starting from {default_prefix}.00001")
        return 0, default_prefix

def get_year_month_prefix():
    """
    Get the current year-month prefix (e.g., '2511' for November 2025).
    
    Returns:
        str: Year-month prefix in format YYMM
    """
    now = datetime.now()
    year = now.year % 100  # Get last 2 digits of year
    month = now.month
    return f"{year:02d}{month:02d}"

def main():
    """Main function to scrape multiple arXiv papers starting from the maximum existing paper_id."""
    # Check if year_month prefix is provided as command-line argument
    if len(sys.argv) > 1:
        year_month_prefix = sys.argv[1]
        print(f"Using provided year-month prefix: {year_month_prefix}")
    else:
        year_month_prefix = get_year_month_prefix()
        print(f"Using current year-month prefix: {year_month_prefix}")
    
    # Construct filename based on year_month prefix
    csv_filename = f"{year_month_prefix}_arxiv_papers.csv"
    print(f"CSV file: {csv_filename}")
    
    # Get the maximum paper_id from existing CSV
    max_paper_num, detected_prefix = get_max_paper_id(csv_filename)
    # Get the maximum paper_id from existing CSV
    max_paper_num, detected_prefix = get_max_paper_id(csv_filename)
    
    # Use the detected prefix from file content if available, otherwise use the one from filename
    if detected_prefix != year_month_prefix and max_paper_num > 0:
        print(f"Warning: Detected prefix {detected_prefix} from file content differs from expected {year_month_prefix}")
        year_month_prefix = detected_prefix
    
    # Start from the next paper after the maximum found
    start_id = max_paper_num + 1
    end_id = start_id + 4200  # Get next papers
    base_url = f"https://arxiv.org/abs/{year_month_prefix}.{{:05d}}"
    
    print(f"Scraping arXiv papers from {year_month_prefix}.{start_id:05d} to {year_month_prefix}.{end_id:05d}")
    print("=" * 80)
    
    successful_scrapes = 0
    failed_scrapes = 0
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    for paper_num in range(start_id, end_id + 1):
        url = base_url.format(paper_num)
        print(f"\n[{paper_num - start_id + 1}/{end_id - start_id + 1}] Scraping: {url}")
        
        # Scrape the paper
        paper_data = scrape_arxiv_paper(url)
        
        if paper_data:
            consecutive_failures = 0  # Reset counter on success
            print(f"✓ Success - Title: {paper_data['og_title'][:80]}..." if len(paper_data['og_title']) > 80 else f"✓ Success - Title: {paper_data['og_title']}")
            print(f"  Category: {paper_data['category']}" + (f" > {paper_data['subcategory']}" if paper_data['subcategory'] else ""))
            print(f"  Submitted: {paper_data['submitted_on']}")
            
            # Only save to CSV if category is Computer Science
            if paper_data['category'] == 'Computer Science':
                save_to_csv(paper_data, csv_filename)
                print(f"  → Saved to CSV (Computer Science paper)")
                successful_scrapes += 1
            else:
                print(f"  → Skipped (Not Computer Science)")
        else:
            print(f"✗ Failed to scrape paper {url}")
            failed_scrapes += 1
            consecutive_failures += 1
            
            # Stop if we hit max consecutive failures
            if consecutive_failures >= max_consecutive_failures:
                print(f"\n⚠ Stopping: {max_consecutive_failures} consecutive failures detected.")
                print(f"Likely reached the end of available papers at {year_month_prefix}.{paper_num:05d}")
                break
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print(f"Scraping completed!")
    print(f"Computer Science papers saved: {successful_scrapes}")
    print(f"Failed to scrape: {failed_scrapes}")
    print(f"Total papers processed: {successful_scrapes + failed_scrapes}")
    
    if successful_scrapes > 0:
        print(f"\nComputer Science papers saved to {csv_filename}")

if __name__ == "__main__":
    main()