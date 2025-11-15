#!/usr/bin/env python3
"""
Weekly arXiv Papers Extractor

This script extracts papers from the last completed week for the weekly research digest.
It automatically:
1. Determines today's date and finds the last Friday
2. Calculates which week of the year that Friday belongs to
3. Extracts all papers submitted during that week (Monday-Sunday)
4. Samples 3,850 random papers
5. Exports only paper_id and abstract columns to a CSV

Output format: samples/2025WK46.csv

Usage:
    python extract_weekly_papers.py [2025WK46]
    python extract_weekly_papers.py              # Uses last Friday's week
    
Optional argument:
    YEARWKWEEK    Week in format like 2025WK46, 2025WK44, etc.
"""

import pandas as pd
import glob
from datetime import datetime, timedelta
import os
import sys
import re

def get_last_friday_and_week():
    """
    Get the last Friday's date and calculate its ISO week number.
    
    Returns:
        tuple: (last_friday_date, year, week_number)
    """
    today = datetime.now()
    
    # Calculate days since last Friday (Friday = 4 in weekday(), where Monday = 0)
    days_since_friday = (today.weekday() - 4) % 7
    
    # If today is Saturday (5) or Sunday (6), go back to last Friday
    # Otherwise, if it's Monday-Friday, go back to the previous Friday
    if today.weekday() >= 5:  # Weekend
        last_friday = today - timedelta(days=days_since_friday)
    else:  # Monday to Friday
        if days_since_friday == 0:  # Today is Friday
            last_friday = today
        else:
            last_friday = today - timedelta(days=days_since_friday)
    
    # Get ISO calendar week number
    iso_calendar = last_friday.isocalendar()
    year = iso_calendar[0]
    week_number = iso_calendar[1]
    
    return last_friday, year, week_number

def get_week_date_range(reference_date):
    """
    Get the Monday and Sunday dates for the week containing the reference date.
    
    Args:
        reference_date (datetime): Reference date (typically last Friday)
        
    Returns:
        tuple: (monday_date, sunday_date)
    """
    # Find Monday of that week (Monday = 0)
    days_since_monday = reference_date.weekday()
    monday = reference_date - timedelta(days=days_since_monday)
    
    # Sunday is 6 days after Monday
    sunday = monday + timedelta(days=6)
    
    return monday, sunday

def load_all_csvs():
    """
    Load and combine all CSV files from the data folder.
    
    Returns:
        tuple: (DataFrame, file_count) or (None, 0) if no files found
    """
    csv_pattern = '../data/*_arxiv_papers.csv'
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found matching pattern: {csv_pattern}")
        return None, 0
    
    # Sort by filename (YYMM prefix)
    csv_files = sorted(csv_files)
    print(f"Loading {len(csv_files)} CSV files from data folder...")
    
    try:
        dfs = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)
            print(f"  ✓ Loaded {len(df)} papers from {csv_file}")
        
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"\n✓ Combined total: {len(combined_df)} papers from {len(csv_files)} files")
        return combined_df, len(csv_files)
    except Exception as e:
        print(f"Error loading CSVs: {e}")
        return None, 0

def filter_papers_by_week(df, monday, sunday):
    """
    Filter papers submitted during the specified week.
    
    Args:
        df (DataFrame): Papers dataframe
        monday (datetime): Monday of target week
        sunday (datetime): Sunday of target week
        
    Returns:
        DataFrame: Filtered papers from that week
    """
    # Convert submitted_on to datetime (now using YYYY-MM-DD format)
    df['submitted_on_dt'] = pd.to_datetime(df['submitted_on'], format='%Y-%m-%d', errors='coerce')
    
    # Filter papers between Monday and Sunday (inclusive)
    week_papers = df[
        (df['submitted_on_dt'] >= monday) & 
        (df['submitted_on_dt'] <= sunday)
    ].copy()
    
    print(f"\nWeek range: {monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}")
    print(f"Found {len(week_papers)} papers submitted during this week")
    
    return week_papers

def sample_and_export(df, year, week_number, sample_size=3850):
    """
    Sample papers and export to CSV with only paper_id and abstract columns.
    
    Args:
        df (DataFrame): Papers dataframe
        year (int): Year
        week_number (int): ISO week number
        sample_size (int): Number of papers to sample (default: 3850)
        
    Returns:
        str: Output filename
    """
    # Sample papers (or use all if fewer than sample_size)
    actual_sample_size = min(sample_size, len(df))
    
    if actual_sample_size < len(df):
        sampled_df = df.sample(n=actual_sample_size, random_state=42)
        print(f"\nRandomly sampled {actual_sample_size} papers from {len(df)} total")
    else:
        sampled_df = df.copy()
        print(f"\nUsing all {actual_sample_size} papers (fewer than {sample_size} available)")
    
    # Select only paper_id and abstract columns
    export_df = sampled_df[['paper_id', 'abstract']].copy()
    
    # Create output filename in format: 2025WK46.csv
    output_filename = f"samples/{year}WK{week_number}.csv"
    
    # Ensure samples directory exists
    os.makedirs('samples', exist_ok=True)
    
    # Export to CSV
    export_df.to_csv(output_filename, index=False)
    print(f"Exported {len(export_df)} papers to: {output_filename}")
    print(f"Columns: paper_id, abstract")
    
    return output_filename

def get_week_from_string(week_str):
    """
    Parse week string like '2025WK46' and return year and week number.
    
    Args:
        week_str (str): Week string in format YYYYWKWW (e.g., 2025WK46)
        
    Returns:
        tuple: (year, week_number) or (None, None) if invalid
    """
    match = re.match(r'^(\d{4})WK(\d{1,2})$', week_str, re.IGNORECASE)
    if match:
        year = int(match.group(1))
        week = int(match.group(2))
        if 1 <= week <= 53:
            return year, week
    return None, None

def get_monday_from_week(year, week_number):
    """
    Get the Monday date for a given ISO week.
    
    Args:
        year (int): Year
        week_number (int): ISO week number
        
    Returns:
        datetime: Monday of that week
    """
    # January 4th is always in week 1
    jan4 = datetime(year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    target_monday = week1_monday + timedelta(weeks=week_number - 1)
    return target_monday

def main():
    """Main function to extract weekly papers."""
    print("=" * 80)
    print("Weekly arXiv Papers Extractor")
    print("=" * 80)
    
    # Check if week string is provided as argument
    if len(sys.argv) > 1:
        week_str = sys.argv[1]
        year, week_number = get_week_from_string(week_str)
        
        if year is None:
            print(f"\nError: Invalid week format '{week_str}'")
            print("Use format: 2025WK46, 2025WK44, etc.")
            print(f"Example: python extract_weekly_papers.py 2025WK46")
            return
        
        print(f"\nUsing specified week: {year}WK{week_number}")
        reference_date = get_monday_from_week(year, week_number)
    else:
        # Use last Friday's week
        reference_date, year, week_number = get_last_friday_and_week()
        print(f"\nToday: {datetime.now().strftime('%d-%b-%Y (%A)')}")
        print(f"Last Friday: {reference_date.strftime('%d-%b-%Y')}")
    
    print(f"Target week: {year}WK{week_number}")
    
    # Step 2: Get the week's date range (Monday to Sunday)
    monday, sunday = get_week_date_range(reference_date)
    
    # Step 3: Load all CSV files
    df, file_count = load_all_csvs()
    if df is None:
        print("\nError: Could not load CSV files. Exiting.")
        return
    
    # Show data coverage
    df['submitted_on_dt'] = pd.to_datetime(df['submitted_on'], format='%Y-%m-%d', errors='coerce')
    valid_dates = df['submitted_on_dt'].dropna()
    if len(valid_dates) > 0:
        print(f"Data coverage: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
    
    # Add week column (format: YYYYWkXX)
    df['week'] = df['submitted_on_dt'].apply(
        lambda x: f"{x.isocalendar()[0]}Wk{x.isocalendar()[1]}" if pd.notna(x) else None
    )
    
    # Create pivot table showing count per week
    print("\n" + "=" * 80)
    print("Papers per week distribution:")
    print("=" * 80)
    week_counts = df['week'].value_counts().sort_index()
    for week, count in week_counts.items():
        if week:  # Skip None values
            print(f"{week}: {count} papers")
    print("=" * 80)
    
    # Step 4: Filter papers from that week
    week_papers = filter_papers_by_week(df, monday, sunday)
    
    if len(week_papers) == 0:
        print("\nWarning: No papers found for the specified week.")
        print("This might mean:")
        print("  - The latest CSV doesn't cover this week yet")
        print("  - Papers from this week haven't been scraped yet")
        print("\nTip: Try a different week with available data")
        print(f"Example: python extract_weekly_papers.py 2025WK44")
        return
    
    # Step 5: Sample and export
    output_file = sample_and_export(week_papers, year, week_number)
    
    print("\n" + "=" * 80)
    print("Extraction completed successfully!")
    print("=" * 80)
    print(f"\nOutput file: {output_file}")
    print(f"Week: {year}WK{week_number} ({monday.strftime('%d-%b-%y')} to {sunday.strftime('%d-%b-%y')})")
    print("\nNext steps:")
    print("  1. Use the generated CSV as input for your article generation prompt")
    print("  2. Check weekly_digest/articles/ for previous week articles")
    print("  3. Run the article generation prompt with context from previous weeks")

if __name__ == "__main__":
    main()
