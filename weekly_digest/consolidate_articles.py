#!/usr/bin/env python3
"""
Consolidate the last 16 weeks of articles into previous_articles.md
"""

import os
import re
from pathlib import Path
from datetime import datetime


def extract_week_number(filename):
    """Extract week number from filename like '25Wk1_article.md' or '25Wk1_articles.md'"""
    match = re.match(r'(\d{2})Wk(\d+)_articles?\.md', filename)
    if match:
        year = int(match.group(1))
        week = int(match.group(2))
        return (year, week)
    return None


def main():
    # Get the articles directory
    articles_dir = Path(__file__).parent / 'articles'
    
    # Find all article files
    article_files = []
    for file in articles_dir.glob('*Wk*.md'):
        week_info = extract_week_number(file.name)
        if week_info:
            article_files.append((week_info, file))
    
    # Sort by year and week (most recent first)
    article_files.sort(key=lambda x: (x[0][0], x[0][1]), reverse=True)
    
    # Take the last 16 weeks
    last_16_weeks = article_files[:16]
    
    if not last_16_weeks:
        print("No article files found")
        return
    
    # Create consolidated content
    output_path = articles_dir / 'previous_articles.md'
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write("# Previous articles\n\n")
        
        # Write each article in reverse chronological order
        for (year, week), file_path in last_16_weeks:
            print(f"Adding: {file_path.name}")
            
            # Read the article content
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read().strip()
            
            # Write to consolidated file
            outfile.write(content)
            outfile.write("\n\n---\n\n")
    
    print(f"\nConsolidated {len(last_16_weeks)} articles into: {output_path}")
    print(f"Articles included (most recent first):")
    for (year, week), file_path in last_16_weeks:
        print(f"  - 20{year} Week {week}: {file_path.name}")


if __name__ == '__main__':
    main()
