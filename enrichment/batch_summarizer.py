#!/usr/bin/env python3
"""
Script to process a batch of arXiv papers with Codex summarization.
"""

import pandas as pd
from codex_abstract_summarizer import summarize_abstracts_batch

# Load the CSV file from the data folder
df = pd.read_csv('../data/2511_arxiv_papers.csv')

# Take first 3 papers for testing
test_batch = df.head(3)

print("Testing with 3 papers from data/2511_arxiv_papers.csv")
print("=" * 80)

# Process the batch
result = summarize_abstracts_batch(test_batch, abstract_column='abstract')

# Display results
print("\nResults:")
print("=" * 80)
for idx, row in result.iterrows():
    print(f"\nPaper {idx + 1}:")
    print(f"Title: {row['og_title']}")
    print(f"Summary: {row['summary']}")
    print("-" * 80)

# Save results to CSV in data folder
output_file = '../data/2511_arxiv_papers_with_summaries_test.csv'
result.to_csv(output_file, index=False)
print(f"\n✓ Results saved to: {output_file}")
