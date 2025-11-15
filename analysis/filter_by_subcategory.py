import pandas as pd
import glob
import os

# Get the parent directory (where CSV files are located)
parent_dir = os.path.dirname(os.path.dirname(__file__))

# Find all CSV files matching the pattern (monthly papers) in data folder
csv_pattern = os.path.join(parent_dir, 'data', '25[0-9][0-9]_arxiv_papers.csv')
csv_files = sorted(glob.glob(csv_pattern))

print(f"Found {len(csv_files)} CSV files:")
for file in csv_files:
    print(f"  - {os.path.basename(file)}")

# Read and concatenate all CSV files
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)
    print(f"Loaded {os.path.basename(file)}: {len(df)} papers")

# Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)
print(f"\nTotal papers combined: {len(combined_df)}")

# Get unique subcategories
subcategories = combined_df['subcategory'].unique()
print(f"\nFound {len(subcategories)} unique subcategories")

# Sample size per subcategory
sample_size = 3850

# Create output directory for subcategory CSVs
output_dir = os.path.join(os.path.dirname(__file__), 'sample_outputs')
os.makedirs(output_dir, exist_ok=True)
print(f"\nOutput directory: {output_dir}")

# Process each subcategory and collect stats
results = []
for subcategory in subcategories:
    # Filter for this subcategory
    subcat_df = combined_df[combined_df['subcategory'] == subcategory]
    
    # Select only paper_id and abstract columns
    subcat_filtered = subcat_df[['paper_id', 'abstract']]
    
    total_count = len(subcat_filtered)
    
    # Random sample
    if total_count >= sample_size:
        subcat_sampled = subcat_filtered.sample(n=sample_size, random_state=42)
        sampled_count = sample_size
    else:
        subcat_sampled = subcat_filtered
        sampled_count = total_count
    
    # Create filename from subcategory (sanitize for filesystem)
    safe_filename = subcategory.replace('/', '_').replace(' ', '_').replace(',', '').lower()
    output_file = os.path.join(output_dir, f'{safe_filename}.csv')
    
    # Export to CSV
    subcat_sampled.to_csv(output_file, index=False)
    
    # Store results
    results.append({
        'subcategory': subcategory,
        'total': total_count,
        'sampled': sampled_count
    })

# Create results dataframe and sort by total count descending
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('total', ascending=False).reset_index(drop=True)

# Display table
print("\n" + "="*80)
print("SUBCATEGORY SAMPLES")
print("="*80)
print(f"{'Subcategory':<50} {'Total':>10} {'Sampled':>10}")
print("-"*80)
for _, row in results_df.iterrows():
    print(f"{row['subcategory']:<50} {row['total']:>10,} {row['sampled']:>10,}")
print("="*80)
print(f"{'TOTAL':^50} {results_df['total'].sum():>10,} {results_df['sampled'].sum():>10,}")
print("="*80)

print(f"\n✓ All subcategory samples exported to: {output_dir}")
print(f"  Total subcategories processed: {len(subcategories)}")
