#!/usr/bin/env python3
"""
Script to interact with Codex CLI to summarize academic paper abstracts.
Processes batches of abstracts and returns results in a DataFrame.
"""

import subprocess
import shlex
import pandas as pd
from typing import List, Optional


def ask_codex(prompt: str) -> str:
    """Send a prompt to Codex CLI and get response."""
    escaped_prompt = shlex.quote(prompt)
    
    result = subprocess.run(
        f'codex exec {escaped_prompt}',
        shell=True,
        capture_output=True,
        text=True
    )
    
    return result.stdout.strip()


def summarize_abstract(abstract: str) -> str:
    """
    Summarize a single abstract using Codex.
    
    Args:
        abstract: The paper abstract to summarize
        
    Returns:
        The summary from Codex
    """
    prompt = f"""Describe what they built/discovered in 20-25 words. Be specific and clear, but cut unnecessary words.

Abstract: "{abstract}"
"""
    
    return ask_codex(prompt)


def summarize_abstracts_batch(df: pd.DataFrame, abstract_column: str = 'abstract') -> pd.DataFrame:
    """
    Process a batch of abstracts and add summaries to the dataframe.
    
    Args:
        df: DataFrame containing abstracts
        abstract_column: Name of the column containing abstracts
        
    Returns:
        DataFrame with new 'summary' column added
    """
    df = df.copy()
    summaries = []
    
    print(f"Processing {len(df)} abstracts...")
    print("-" * 80)
    
    for idx, row in df.iterrows():
        abstract = row[abstract_column]
        print(f"Processing paper {idx + 1}/{len(df)}...")
        
        try:
            summary = summarize_abstract(abstract)
            summaries.append(summary)
            print(f"✓ Summary: {summary[:80]}...")
        except Exception as e:
            print(f"✗ Error: {e}")
            summaries.append(None)
        
        print()
    
    df['summary'] = summaries
    print("-" * 80)
    print(f"Completed: {len([s for s in summaries if s])} successful, {len([s for s in summaries if not s])} failed")
    
    return df


if __name__ == "__main__":
    # Example: Test with a small batch
    test_data = {
        'title': ['Test Paper 1'],
        'abstract': ["""Reliably determining the performance of Retrieval-Augmented Generation (RAG) systems depends on comprehensive test questions. While a proliferation of evaluation frameworks for LLM-powered applications exists, current practices lack a systematic method to ensure these test sets adequately cover the underlying knowledge base, leaving developers with significant blind spots. To address this, we present a novel, applied methodology to quantify the semantic coverage of RAG test questions against their underlying documents. Our approach leverages existing technologies, including vector embeddings and clustering algorithms, to create a practical framework for validating test comprehensiveness. Our methodology embeds document chunks and test questions into a unified vector space, enabling the calculation of multiple coverage metrics: basic proximity, content-weighted coverage, and multi-topic question coverage. Furthermore, we incorporate outlier detection to filter irrelevant questions, allowing for the refinement of test sets. Experimental evidence from two distinct use cases demonstrates that our framework effectively quantifies test coverage, identifies specific content areas with inadequate representation, and provides concrete recommendations for generating new, high-value test questions. This work provides RAG developers with essential tools to build more robust test suites, thereby improving system reliability and extending to applications such as identifying misaligned documents."""]
    }
    
    df = pd.DataFrame(test_data)
    result_df = summarize_abstracts_batch(df)
    
    print("\nResult DataFrame:")
    print("=" * 80)
    print(result_df[['title', 'summary']])

