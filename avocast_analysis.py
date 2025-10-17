#!/usr/bin/env python3
"""
AvoCast - Avocado Price Forecasting Analysis
Data Exploration and Initial Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

print("=== AvoCast: Avocado Price Forecasting Analysis ===")
print("Phase 1: Data Loading and Exploration")
print("=" * 50)

# Load the avocado dataset
print("Loading avocado dataset...")
df = pd.read_csv('avocado.csv')

print(f"Dataset loaded successfully!")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Display basic information about the dataset
print("\n" + "=" * 50)
print("DATASET OVERVIEW")
print("=" * 50)

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset Info:")
print(df.info())

print("\nBasic Statistics:")
print(df.describe())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nUnique Values per Column:")
for col in df.columns:
    print(f"{col}: {df[col].nunique()} unique values")

# Explore the regions
print("\n" + "=" * 50)
print("REGIONAL ANALYSIS")
print("=" * 50)

print("\nUnique Regions:")
regions = df['region'].unique()
print(f"Total regions: {len(regions)}")
for i, region in enumerate(sorted(regions)):
    print(f"{i+1:2d}. {region}")

# Check if Washington D.C. data is available
dc_data = df[df['region'].str.contains('Washington', case=False, na=False)]
print(f"\nWashington D.C. related data:")
print(f"Rows found: {len(dc_data)}")
if len(dc_data) > 0:
    print("Available Washington regions:")
    print(dc_data['region'].unique())

# Check date range
print("\n" + "=" * 50)
print("DATE ANALYSIS")
print("=" * 50)

df['Date'] = pd.to_datetime(df['Date'])
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Total time span: {(df['Date'].max() - df['Date'].min()).days} days")

# Check data frequency
date_counts = df['Date'].value_counts().sort_index()
print(f"Data frequency: {date_counts.iloc[0]} records per date (assuming weekly data)")

# Analyze avocado types
print("\n" + "=" * 50)
print("AVOCADO TYPE ANALYSIS")
print("=" * 50)

print("Avocado types:")
print(df['type'].value_counts())

# Price analysis
print("\n" + "=" * 50)
print("PRICE ANALYSIS")
print("=" * 50)

print("Average Price Statistics:")
print(f"Overall mean price: ${df['AveragePrice'].mean():.2f}")
print(f"Price range: ${df['AveragePrice'].min():.2f} - ${df['AveragePrice'].max():.2f}")
print(f"Standard deviation: ${df['AveragePrice'].std():.2f}")

print("\nPrice by Type:")
price_by_type = df.groupby('type')['AveragePrice'].agg(['mean', 'std', 'min', 'max'])
print(price_by_type)

# Focus on Washington D.C. area data
print("\n" + "=" * 50)
print("WASHINGTON D.C. FOCUS")
print("=" * 50)

# Try different variations to find DC data
dc_variations = ['Washington', 'DC', 'District', 'Baltimore']
dc_found = False

for variation in dc_variations:
    dc_subset = df[df['region'].str.contains(variation, case=False, na=False)]
    if len(dc_subset) > 0:
        print(f"\nFound data for '{variation}' pattern:")
        print(f"Regions: {dc_subset['region'].unique()}")
        print(f"Records: {len(dc_subset)}")
        dc_found = True

if not dc_found:
    print("\nNo direct Washington D.C. data found.")
    print("Available major regions that might be suitable:")
    major_regions = df[df['region'].str.contains('Total|National|US', case=False, na=False)]['region'].unique()
    for region in major_regions:
        print(f"  - {region}")
    
    # Use TotalUS as alternative
    if 'TotalUS' in df['region'].values:
        print("\nUsing 'TotalUS' as representative data for analysis...")
        target_region = 'TotalUS'
    else:
        # Find the most comprehensive region
        region_counts = df['region'].value_counts()
        target_region = region_counts.index[0]
        print(f"\nUsing '{target_region}' as representative data (most data points)...")

else:
    # Use the first Washington-related region found
    target_region = dc_subset['region'].iloc[0]
    print(f"\nUsing '{target_region}' for analysis...")

# Filter data for target region
target_data = df[df['region'] == target_region].copy()
print(f"\nTarget region data summary:")
print(f"Region: {target_region}")
print(f"Records: {len(target_data)}")
print(f"Date range: {target_data['Date'].min()} to {target_data['Date'].max()}")
print(f"Types available: {target_data['type'].unique()}")

# Save the filtered data for further analysis
target_data.to_csv('avocado_target_region.csv', index=False)
print(f"\nFiltered data saved to 'avocado_target_region.csv'")

print("\n" + "=" * 50)
print("DATA EXPLORATION COMPLETE")
print("=" * 50)
print("Next steps:")
print("1. Data preprocessing for Prophet model")
print("2. Time series analysis and visualization")
print("3. Prophet model training and evaluation")

