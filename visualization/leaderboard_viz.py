import pandas as pd
import numpy as np
from datetime import datetime
import glob
import os
import json

# Find all CSV files with "arxiv_papers" in the name in the data folder
csv_files = sorted(glob.glob('../data/*arxiv_papers.csv'))
print(f"Found {len(csv_files)} CSV files to consolidate:")
for f in csv_files:
    print(f"  - {os.path.basename(f)}")

# Load and concatenate all CSV files
print("\nLoading and consolidating data...")
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# Combine all dataframes
all_papers = pd.concat(dfs, ignore_index=True)
print(f"Total papers loaded: {len(all_papers):,}")

# Remove duplicates based on paper_id
all_papers = all_papers.drop_duplicates(subset=['paper_id'])
print(f"Unique papers: {len(all_papers):,}")

# Convert submission date to datetime (handle mixed formats)
all_papers['submitted_date'] = pd.to_datetime(all_papers['submitted_on'], format='mixed', dayfirst=False)

# Filter to only 2025 data
all_papers_2025 = all_papers[all_papers['submitted_date'].dt.year == 2025].copy()
print(f"Papers from 2025: {len(all_papers_2025):,}")

# Get date range
min_date = all_papers_2025['submitted_date'].min()
max_date = all_papers_2025['submitted_date'].max()
print(f"Date range: {min_date.date()} to {max_date.date()}")

# Create month column
all_papers_2025['year_month'] = all_papers_2025['submitted_date'].dt.to_period('M')
all_papers_2025['month_name'] = all_papers_2025['submitted_date'].dt.strftime('%B %Y')

# Get top subcategories
top_n = 10
subcategory_counts = all_papers_2025['subcategory'].value_counts()
top_subcategories = subcategory_counts.head(top_n).index.tolist()

print(f"\nTop {top_n} subcategories:")
for i, (subcat, count) in enumerate(subcategory_counts.head(top_n).items(), 1):
    percentage = (count / len(all_papers_2025)) * 100
    print(f"{i:2d}. {subcat:45s} {count:6,} papers ({percentage:5.2f}%)")

# Aggregate to "Others" for remaining subcategories
all_papers_2025['subcategory_grouped'] = all_papers_2025['subcategory'].apply(
    lambda x: x if x in top_subcategories else 'Others'
)

# Create monthly counts for each subcategory
monthly_data = all_papers_2025.groupby(['year_month', 'subcategory_grouped']).size().unstack(fill_value=0)

# Reorder columns to match top subcategories + Others
column_order = [col for col in top_subcategories if col in monthly_data.columns]
if 'Others' in monthly_data.columns:
    column_order.append('Others')
monthly_data = monthly_data[column_order]

# Convert to JSON format for HTML/JS
months = [str(period) for period in monthly_data.index]
month_labels = []
for period in monthly_data.index:
    date = period.to_timestamp()
    month_labels.append(date.strftime('%b %Y'))

# Prepare data for each subcategory
subcategories_data = []
for col in monthly_data.columns:
    subcategories_data.append({
        'name': col,
        'data': monthly_data[col].tolist(),
        'total': int(monthly_data[col].sum())
    })

# Sort by total descending
subcategories_data.sort(key=lambda x: x['total'], reverse=True)

# Calculate totals per month
monthly_totals = monthly_data.sum(axis=1).tolist()

# Define colors for each subcategory
colors = [
    '#E91E63',  # Pink
    '#FF9800',  # Orange
    '#4CAF50',  # Green
    '#2196F3',  # Blue
    '#9C27B0',  # Purple
    '#00BCD4',  # Cyan
    '#FFC107',  # Amber
    '#795548',  # Brown
    '#607D8B',  # Blue Grey
    '#F44336',  # Red
    '#9E9E9E',  # Grey for Others
]

# Assign colors
for i, subcat in enumerate(subcategories_data):
    subcat['color'] = colors[i % len(colors)]

# Calculate insights for Section 2
insights = []

for subcat_data in subcategories_data:
    name = subcat_data['name']
    data = subcat_data['data']
    
    # Calculate percentage data
    pct_data = [
        (data[i] / monthly_totals[i] * 100) if monthly_totals[i] > 0 else 0
        for i in range(len(data))
    ]
    
    # Skip if not enough data
    if len(pct_data) < 2:
        continue
    
    # Calculate CAGR (using first and last non-zero values)
    first_val = next((x for x in pct_data if x > 0), None)
    last_val = next((x for x in reversed(pct_data) if x > 0), None)
    
    if first_val and last_val and first_val > 0:
        num_periods = len([x for x in pct_data if x > 0]) - 1
        if num_periods > 0:
            cagr = ((last_val / first_val) ** (1 / num_periods) - 1) * 100
        else:
            cagr = 0
    else:
        cagr = 0
    
    # Calculate absolute change
    abs_change = last_val - first_val if (first_val and last_val) else 0
    
    # Calculate volatility (std dev)
    volatility = np.std(pct_data) if len(pct_data) > 1 else 0
    
    insights.append({
        'name': name,
        'cagr': cagr,
        'abs_change': abs_change,
        'volatility': volatility,
        'first_val': first_val or 0,
        'last_val': last_val or 0
    })

# Sort and identify key insights
insights_sorted_by_cagr = sorted(insights, key=lambda x: x['cagr'], reverse=True)
insights_sorted_by_change = sorted(insights, key=lambda x: x['abs_change'], reverse=True)
insights_sorted_by_volatility = sorted(insights, key=lambda x: x['volatility'])

top_gainer = insights_sorted_by_cagr[0] if insights_sorted_by_cagr else None
top_loser = insights_sorted_by_cagr[-1] if insights_sorted_by_cagr else None
most_stable = insights_sorted_by_volatility[0] if insights_sorted_by_volatility else None
biggest_jump = insights_sorted_by_change[0] if insights_sorted_by_change else None
biggest_drop = insights_sorted_by_change[-1] if insights_sorted_by_change else None

insights_html = ""
if top_gainer:
    insights_html += f"""
    <div class="insight-card">
        <div class="insight-icon">📈</div>
        <div class="insight-content">
            <div class="insight-title">Highest Growth</div>
            <div class="insight-name">{top_gainer['name']}</div>
            <div class="insight-value">+{top_gainer['cagr']:.1f}% CAGR</div>
            <div class="insight-detail">{top_gainer['first_val']:.1f}% → {top_gainer['last_val']:.1f}%</div>
        </div>
    </div>
    """

if top_loser and top_loser['cagr'] < 0:
    insights_html += f"""
    <div class="insight-card">
        <div class="insight-icon">📉</div>
        <div class="insight-content">
            <div class="insight-title">Biggest Decline</div>
            <div class="insight-name">{top_loser['name']}</div>
            <div class="insight-value">{top_loser['cagr']:.1f}% CAGR</div>
            <div class="insight-detail">{top_loser['first_val']:.1f}% → {top_loser['last_val']:.1f}%</div>
        </div>
    </div>
    """

if biggest_jump and biggest_jump['abs_change'] > 1:
    insights_html += f"""
    <div class="insight-card">
        <div class="insight-icon">🚀</div>
        <div class="insight-content">
            <div class="insight-title">Biggest Gain</div>
            <div class="insight-name">{biggest_jump['name']}</div>
            <div class="insight-value">+{biggest_jump['abs_change']:.1f} percentage points</div>
            <div class="insight-detail">{biggest_jump['first_val']:.1f}% → {biggest_jump['last_val']:.1f}%</div>
        </div>
    </div>
    """

# Calculate 6-month trailing average for Section 3
trailing_avg_data = []
window = 6

for subcat_data in subcategories_data:
    name = subcat_data['name']
    data = subcat_data['data']
    
    # Calculate percentage data
    pct_data = [
        (data[i] / monthly_totals[i] * 100) if monthly_totals[i] > 0 else 0
        for i in range(len(data))
    ]
    
    # Calculate 6-month trailing average
    trailing_avg = []
    for i in range(len(pct_data)):
        if i < window - 1:
            # Not enough data yet, use available data
            avg = np.mean(pct_data[:i+1])
        else:
            # Full 6-month window
            avg = np.mean(pct_data[i-window+1:i+1])
        trailing_avg.append(avg)
    
    trailing_avg_data.append({
        'name': name,
        'data': trailing_avg,
        'color': subcat_data['color']
    })

# Calculate insights for Section 3 (trailing average trends)
trailing_insights = []

for subcat in trailing_avg_data:
    name = subcat['name']
    data = subcat['data']
    
    # Skip if not enough data
    if len(data) < 2:
        continue
    
    # Calculate trend (comparing last 3 months avg vs first 3 months avg)
    if len(data) >= 6:
        recent_avg = np.mean(data[-3:])
        early_avg = np.mean(data[:3])
        trend_change = recent_avg - early_avg
        
        # Calculate overall trend direction (slope)
        x = np.arange(len(data))
        slope = np.polyfit(x, data, 1)[0]  # Linear regression slope
        
        trailing_insights.append({
            'name': name,
            'trend_change': trend_change,
            'slope': slope,
            'recent_avg': recent_avg,
            'early_avg': early_avg,
            'current_value': data[-1]
        })

# Sort and identify key insights for trailing average
trailing_sorted_by_change = sorted(trailing_insights, key=lambda x: x['trend_change'], reverse=True)
trailing_sorted_by_slope = sorted(trailing_insights, key=lambda x: abs(x['slope']), reverse=True)

trailing_top_gainer = trailing_sorted_by_change[0] if trailing_sorted_by_change else None
trailing_top_loser = trailing_sorted_by_change[-1] if trailing_sorted_by_change else None
trailing_strongest_trend = trailing_sorted_by_slope[0] if trailing_sorted_by_slope else None

trailing_insights_html = ""
if trailing_top_gainer:
    insights_html += f"""
    <div class="insight-card">
        <div class="insight-icon">📊</div>
        <div class="insight-content">
            <div class="insight-title">Smoothed Growth Leader</div>
            <div class="insight-name">{trailing_top_gainer['name']}</div>
            <div class="insight-value">+{trailing_top_gainer['trend_change']:.1f}pp trend</div>
            <div class="insight-detail">{trailing_top_gainer['early_avg']:.1f}% → {trailing_top_gainer['recent_avg']:.1f}% (6mo avg)</div>
        </div>
    </div>
    """

if trailing_top_loser and trailing_top_loser['trend_change'] < -0.5:
    trailing_insights_html += f"""
    <div class="insight-card">
        <div class="insight-icon">📉</div>
        <div class="insight-content">
            <div class="insight-title">Smoothed Decline</div>
            <div class="insight-name">{trailing_top_loser['name']}</div>
            <div class="insight-value">{trailing_top_loser['trend_change']:.1f}pp trend</div>
            <div class="insight-detail">{trailing_top_loser['early_avg']:.1f}% → {trailing_top_loser['recent_avg']:.1f}% (6mo avg)</div>
        </div>
    </div>
    """

if trailing_strongest_trend:
    direction = "upward" if trailing_strongest_trend['slope'] > 0 else "downward"
    icon = "📈" if trailing_strongest_trend['slope'] > 0 else "📉"
    trailing_insights_html += f"""
    <div class="insight-card">
        <div class="insight-icon">{icon}</div>
        <div class="insight-content">
            <div class="insight-title">Strongest Trend</div>
            <div class="insight-name">{trailing_strongest_trend['name']}</div>
            <div class="insight-value">Clear {direction} trajectory</div>
            <div class="insight-detail">Current: {trailing_strongest_trend['current_value']:.1f}% (6mo avg)</div>
        </div>
    </div>
    """

# Generate HTML
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv CS Papers Leaderboard 2025</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: #667eea;
            line-height: 1;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .content {{
            display: flex;
            flex-wrap: wrap;
        }}
        
        .chart-section {{
            flex: 1;
            min-width: 60%;
            padding: 40px;
        }}
        
        .leaderboard-section {{
            flex: 0 0 400px;
            background: #f8f9fa;
            padding: 40px 30px;
            border-left: 1px solid #e0e0e0;
        }}
        
        .section-title {{
            font-size: 1.5em;
            font-weight: 600;
            margin-bottom: 25px;
            color: #333;
        }}
        
        .chart-container {{
            position: relative;
            height: 650px;
        }}
        
        .leaderboard {{
            list-style: none;
        }}
        
        .leaderboard-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .leaderboard-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .rank {{
            font-size: 1.2em;
            font-weight: 700;
            color: #999;
            min-width: 35px;
        }}
        
        .color-badge {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 12px;
        }}
        
        .name {{
            flex: 1;
            font-size: 0.95em;
            color: #333;
            line-height: 1.3;
        }}
        
        .count {{
            font-size: 1.1em;
            font-weight: 600;
            color: #667eea;
            margin-right: 10px;
        }}
        
        .percentage {{
            font-size: 0.85em;
            color: #999;
        }}
        
        .insights-section {{
            flex: 0 0 350px;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow-y: auto;
            min-height: 650px;
        }}
        
        .insight-card {{
            display: flex;
            align-items: center;
            padding: 20px;
            margin-bottom: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .insight-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .insight-icon {{
            font-size: 2em;
            margin-right: 15px;
            min-width: 50px;
            text-align: center;
        }}
        
        .insight-content {{
            flex: 1;
        }}
        
        .insight-title {{
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        
        .insight-name {{
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .insight-value {{
            font-size: 1.3em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 3px;
        }}
        
        .insight-detail {{
            font-size: 0.9em;
            color: #666;
        }}
        
        @media (max-width: 1024px) {{
            .content {{
                flex-direction: column;
            }}
            
            .leaderboard-section {{
                flex: 1;
                border-left: none;
                border-top: 1px solid #e0e0e0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 arXiv CS Papers Leaderboard</h1>
            <p>Computer Science Research Trends • 2025</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value">{len(all_papers_2025):,}</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(monthly_data)}</div>
                <div class="stat-label">Months</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(top_subcategories) + 1}</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>
        
        <div class="content">
            <div class="chart-section">
                <h2 class="section-title">Section 1: Monthly Publication Trends (Absolute)</h2>
                <div class="chart-container">
                    <canvas id="monthlyChart"></canvas>
                </div>
            </div>
            
            <div class="leaderboard-section">
                <h2 class="section-title">Leaderboard</h2>
                <ul class="leaderboard" id="leaderboard">
                </ul>
            </div>
        </div>
        
        <div class="content" style="margin-top: 50px;">
            <div class="chart-section">
                <h2 class="section-title">Section 2: Monthly Distribution (Percentage)</h2>
                <div class="chart-container">
                    <canvas id="percentageChart"></canvas>
                </div>
            </div>
            <div class="insights-section">
                <h2 class="section-title">📊 Key Insights</h2>
                {insights_html}
            </div>
        </div>
        
        <div class="content" style="margin-top: 50px;">
            <div class="chart-section">
                <h2 class="section-title">Section 3: 6-Month Trailing Average (Percentage)</h2>
                <div class="chart-container">
                    <canvas id="trailingChart"></canvas>
                </div>
            </div>
            <div class="insights-section">
                <h2 class="section-title">📊 Trailing Insights</h2>
                {trailing_insights_html}
            </div>
        </div>
    </div>
    
    <script>
        const monthLabels = {json.dumps(month_labels)};
        const subcategoriesData = {json.dumps(subcategories_data)};
        const trailingAvgData = {json.dumps(trailing_avg_data)};
        const totalPapers = {len(all_papers_2025)};
        const monthlyTotals = {json.dumps(monthly_totals)};
        
        // Calculate max Y value for percentage chart (max percentage + 5% padding)
        const maxPercentage = Math.max(...subcategoriesData.map(subcat => 
            Math.max(...subcat.data.map((value, index) => 
                monthlyTotals[index] > 0 ? (value / monthlyTotals[index] * 100) : 0
            ))
        ));
        const chartMaxY = Math.ceil(maxPercentage + 5);
        
        // Store original colors
        const originalColors = subcategoriesData.map(s => s.color);
        
        // Function to dim colors
        function dimColor(color, opacity = 0.2) {{
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);
            return `rgba(${{r}}, ${{g}}, ${{b}}, ${{opacity}})`;
        }}
        
        // Create datasets for Chart.js (absolute values)
        const datasets = subcategoriesData.map(subcat => ({{
            label: subcat.name,
            data: subcat.data,
            backgroundColor: subcat.color,
            borderColor: subcat.color,
            borderWidth: 0,
        }}));
        
        // Create datasets for percentage chart
        const percentageDatasets = subcategoriesData.map(subcat => ({{
            label: subcat.name,
            data: subcat.data.map((value, index) => 
                monthlyTotals[index] > 0 ? (value / monthlyTotals[index] * 100) : 0
            ),
            backgroundColor: subcat.color,
            borderColor: subcat.color,
            borderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.3,
            fill: false
        }}));
        
        // Create the chart
        const ctx = document.getElementById('monthlyChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: monthLabels,
                datasets: datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        mode: 'x',
                        intersect: false,
                        position: 'nearest',
                        xAlign: 'left',
                        yAlign: 'top',
                        callbacks: {{
                            footer: function(tooltipItems) {{
                                let sum = 0;
                                tooltipItems.forEach(function(tooltipItem) {{
                                    sum += tooltipItem.parsed.y;
                                }});
                                return 'Total: ' + sum;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        stacked: true,
                        grid: {{
                            display: false
                        }},
                        ticks: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true,
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    axis: 'y',
                    intersect: true
                }},
                onHover: (event, activeElements) => {{
                    if (activeElements.length > 0) {{
                        const datasetIndex = activeElements[0].datasetIndex;
                        chart.data.datasets.forEach((dataset, index) => {{
                            if (index === datasetIndex) {{
                                dataset.backgroundColor = originalColors[index];
                            }} else {{
                                dataset.backgroundColor = dimColor(originalColors[index]);
                            }}
                        }});
                        chart.update('none');
                    }} else {{
                        chart.data.datasets.forEach((dataset, index) => {{
                            dataset.backgroundColor = originalColors[index];
                        }});
                        chart.update('none');
                    }}
                }}
            }}
        }});
        
        // Create the percentage chart
        const ctx2 = document.getElementById('percentageChart').getContext('2d');
        const chart2 = new Chart(ctx2, {{
            type: 'line',
            data: {{
                labels: monthLabels,
                datasets: percentageDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        mode: 'x',
                        intersect: false,
                        position: 'nearest',
                        xAlign: 'left',
                        yAlign: 'top',
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                label += context.parsed.y.toFixed(1) + '%';
                                return label;
                            }},
                            footer: function(tooltipItems) {{
                                let sum = 0;
                                tooltipItems.forEach(function(tooltipItem) {{
                                    sum += tooltipItem.parsed.y;
                                }});
                                return 'Total: ' + sum.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        max: chartMaxY,
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            font: {{
                                size: 11
                            }},
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    axis: 'y',
                    intersect: true
                }},
                onHover: (event, activeElements) => {{
                    if (activeElements.length > 0) {{
                        const datasetIndex = activeElements[0].datasetIndex;
                        chart2.data.datasets.forEach((dataset, index) => {{
                            if (index === datasetIndex) {{
                                dataset.backgroundColor = originalColors[index];
                                dataset.borderWidth = 4;
                            }} else {{
                                dataset.backgroundColor = dimColor(originalColors[index]);
                                dataset.borderWidth = 1;
                            }}
                        }});
                        chart2.update('none');
                    }} else {{
                        chart2.data.datasets.forEach((dataset, index) => {{
                            dataset.backgroundColor = originalColors[index];
                            dataset.borderWidth = 2;
                        }});
                        chart2.update('none');
                    }}
                }}
            }}
        }});
        
        // Populate leaderboard
        const leaderboard = document.getElementById('leaderboard');
        subcategoriesData.forEach((subcat, index) => {{
            const percentage = ((subcat.total / totalPapers) * 100).toFixed(1);
            const item = document.createElement('li');
            item.className = 'leaderboard-item';
            item.innerHTML = `
                <div class="rank">${{index + 1}}.</div>
                <div class="color-badge" style="background-color: ${{subcat.color}}"></div>
                <div class="name">${{subcat.name}}</div>
                <div class="count">${{subcat.total.toLocaleString()}}</div>
                <div class="percentage">${{percentage}}%</div>
            `;
            leaderboard.appendChild(item);
        }});
        
        // Create the trailing average chart (Section 3)
        const trailingDatasets = trailingAvgData.map(subcat => ({{
            label: subcat.name,
            data: subcat.data,
            borderColor: subcat.color,
            backgroundColor: subcat.color,
            tension: 0.3,
            fill: false,
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
        }}));
        
        const originalColorsTrailing = trailingDatasets.map(d => d.borderColor);
        
        // Calculate max Y for trailing chart
        const trailingMaxY = Math.ceil(Math.max(...trailingAvgData.flatMap(d => d.data)) + 5);
        
        const ctx3 = document.getElementById('trailingChart').getContext('2d');
        const chart3 = new Chart(ctx3, {{
            type: 'line',
            data: {{
                labels: monthLabels,
                datasets: trailingDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        mode: 'x',
                        intersect: false,
                        position: 'nearest',
                        xAlign: 'left',
                        yAlign: 'top',
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                label += context.parsed.y.toFixed(1) + '% (6mo avg)';
                                return label;
                            }},
                            footer: function(tooltipItems) {{
                                let sum = 0;
                                tooltipItems.forEach(function(tooltipItem) {{
                                    sum += tooltipItem.parsed.y;
                                }});
                                return 'Total: ' + sum.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        max: trailingMaxY,
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            font: {{
                                size: 11
                            }},
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    axis: 'y',
                    intersect: true
                }},
                onHover: (event, activeElements) => {{
                    if (activeElements.length > 0) {{
                        const datasetIndex = activeElements[0].datasetIndex;
                        chart3.data.datasets.forEach((dataset, index) => {{
                            if (index === datasetIndex) {{
                                dataset.backgroundColor = originalColorsTrailing[index];
                                dataset.borderWidth = 4;
                            }} else {{
                                dataset.backgroundColor = dimColor(originalColorsTrailing[index]);
                                dataset.borderWidth = 1;
                            }}
                        }});
                        chart3.update('none');
                    }} else {{
                        chart3.data.datasets.forEach((dataset, index) => {{
                            dataset.backgroundColor = originalColorsTrailing[index];
                            dataset.borderWidth = 2;
                        }});
                        chart3.update('none');
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

# Save HTML file
output_file = 'arxiv_leaderboard.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Saved: {output_file}")

print("\n" + "="*80)
print("LEADERBOARD SUMMARY")
print("="*80)
for i, subcat in enumerate(subcategories_data, 1):
    percentage = (subcat['total'] / len(all_papers_2025)) * 100
    print(f"{i:2d}. {subcat['name']:45s} {subcat['total']:6,} papers ({percentage:5.2f}%)")

print("\nDone! 🎉")
print(f"\nOpen the file: file://{os.path.abspath(output_file)}")
