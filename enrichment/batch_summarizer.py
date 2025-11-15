#!/usr/bin/env python3
"""
Script to enrich arXiv papers with AI summaries in place.
Finds rows with empty summaries and processes them in batches.

Usage:
    python batch_summarizer.py          # Process 10 papers (default)
    python batch_summarizer.py 50       # Process 50 papers
    python batch_summarizer.py 100      # Process 100 papers
"""

import sys
import pandas as pd
from codex_abstract_summarizer import summarize_abstract

# Configuration
CSV_FILE = '../data/2511_arxiv_papers.csv'
DEFAULT_BATCH_SIZE = 10

def main():
    # Get batch size from command line argument or use default
    batch_size = DEFAULT_BATCH_SIZE
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
            if batch_size <= 0:
                print("Error: Batch size must be a positive integer")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid batch size '{sys.argv[1]}'. Using default: {DEFAULT_BATCH_SIZE}")
            batch_size = DEFAULT_BATCH_SIZE
    
    # Load CSV
    print(f"Loading {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    
    # Find rows with empty summaries
    empty_summaries = df['summary'].isna() | (df['summary'] == '')
    empty_indices = df[empty_summaries].index.tolist()
    
    if not empty_indices:
        print("✓ All papers already have summaries!")
        return
    
    # Get first N rows that need summaries
    to_process = empty_indices[:batch_size]
    
    print(f"\nFound {len(empty_indices)} papers without summaries")
    print(f"Processing next {len(to_process)} papers (rows {to_process[0]} to {to_process[-1]})...")
    print("=" * 80)
    
    # Process each row
    for idx in to_process:
        paper = df.loc[idx]
        print(f"\n[{to_process.index(idx) + 1}/{len(to_process)}] Processing: {paper['paper_id']}")
        print(f"Title: {paper['og_title'][:80]}...")
        
        try:
            # Get summary from Codex using the proper prompt
            summary = summarize_abstract(paper['abstract'])
            
            # Update the dataframe
            df.at[idx, 'summary'] = summary
            
            # Save immediately after each successful summary
            df.to_csv(CSV_FILE, index=False)
            
            print(f"✓ Summary: {summary}")
            print(f"✓ Saved to CSV")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print("✓ Batch processing complete!")
    
    # Show remaining
    remaining = len(df[df['summary'].isna() | (df['summary'] == '')])
    print(f"\nRemaining papers without summaries: {remaining}")

if __name__ == "__main__":
    main()
