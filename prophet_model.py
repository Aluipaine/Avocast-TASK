#!/usr/bin/env python3
"""
AvoCast - Prophet Model Development
Data Preparation and Time Series Forecasting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.plot import plot_cross_validation_metric
import holidays
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

print("=== AvoCast: Prophet Model Development ===")
print("Phase 2: Data Preparation and Model Training")
print("=" * 50)

# Load the filtered data
print("Loading BaltimoreWashington avocado data...")
df = pd.read_csv('avocado_target_region.csv')
print(f"Loaded {len(df)} records")

# Data preparation for Prophet
print("\n" + "=" * 50)
print("DATA PREPARATION FOR PROPHET")
print("=" * 50)

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Focus on conventional avocados for initial model (more data points)
conventional_data = df[df['type'] == 'conventional'].copy()
print(f"Using conventional avocado data: {len(conventional_data)} records")

# Prepare data for Prophet (requires 'ds' and 'y' columns)
prophet_data = conventional_data[['Date', 'AveragePrice']].copy()
prophet_data.columns = ['ds', 'y']

# Sort by date
prophet_data = prophet_data.sort_values('ds').reset_index(drop=True)

print(f"Prophet data prepared:")
print(f"Date range: {prophet_data['ds'].min()} to {prophet_data['ds'].max()}")
print(f"Price range: ${prophet_data['y'].min():.2f} to ${prophet_data['y'].max():.2f}")

# Check for missing dates and fill if necessary
print("\nChecking for missing dates...")
date_range = pd.date_range(start=prophet_data['ds'].min(), 
                          end=prophet_data['ds'].max(), 
                          freq='W')
missing_dates = set(date_range) - set(prophet_data['ds'])
print(f"Missing dates: {len(missing_dates)}")

if len(missing_dates) > 0:
    print("Filling missing dates with interpolated values...")
    # Create complete date range
    complete_dates = pd.DataFrame({'ds': date_range})
    prophet_data = complete_dates.merge(prophet_data, on='ds', how='left')
    
    # Interpolate missing values
    prophet_data['y'] = prophet_data['y'].interpolate(method='linear')
    print(f"Data after filling: {len(prophet_data)} records")

# Train/Test Split (80/20)
print("\n" + "=" * 50)
print("TRAIN/TEST SPLIT")
print("=" * 50)

split_date = prophet_data['ds'].quantile(0.8)
train_data = prophet_data[prophet_data['ds'] <= split_date].copy()
test_data = prophet_data[prophet_data['ds'] > split_date].copy()

print(f"Training data: {len(train_data)} records ({prophet_data['ds'].min()} to {split_date.strftime('%Y-%m-%d')})")
print(f"Test data: {len(test_data)} records ({test_data['ds'].min().strftime('%Y-%m-%d')} to {prophet_data['ds'].max().strftime('%Y-%m-%d')})")

# Create US holidays for the model
print("\n" + "=" * 50)
print("HOLIDAY SETUP")
print("=" * 50)

# Create holiday dataframe
us_holidays = holidays.US(years=range(2015, 2020))
holiday_df = pd.DataFrame([
    {'holiday': 'thanksgiving', 'ds': date, 'lower_window': -1, 'upper_window': 1}
    for date, name in us_holidays.items() 
    if 'thanksgiving' in name.lower()
])

# Add other major holidays that might affect avocado consumption
major_holidays = []
for year in range(2015, 2020):
    # New Year's Day
    major_holidays.append({'holiday': 'new_years', 'ds': pd.to_datetime(f'{year}-01-01'), 'lower_window': 0, 'upper_window': 1})
    # Super Bowl Sunday (first Sunday in February)
    super_bowl = pd.to_datetime(f'{year}-02-01')
    while super_bowl.weekday() != 6:  # Sunday is 6
        super_bowl += timedelta(days=1)
    major_holidays.append({'holiday': 'super_bowl', 'ds': super_bowl, 'lower_window': -1, 'upper_window': 1})
    # Cinco de Mayo
    major_holidays.append({'holiday': 'cinco_de_mayo', 'ds': pd.to_datetime(f'{year}-05-05'), 'lower_window': 0, 'upper_window': 1})

holiday_df = pd.concat([holiday_df, pd.DataFrame(major_holidays)], ignore_index=True)
print(f"Created holiday dataframe with {len(holiday_df)} holiday periods")
print("Holidays included:")
for holiday in holiday_df['holiday'].unique():
    count = len(holiday_df[holiday_df['holiday'] == holiday])
    print(f"  - {holiday}: {count} occurrences")

# Initialize and configure Prophet model
print("\n" + "=" * 50)
print("PROPHET MODEL CONFIGURATION")
print("=" * 50)

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,  # We have weekly data
    holidays=holiday_df,
    seasonality_mode='additive',
    changepoint_prior_scale=0.05,  # Controls flexibility of trend changes
    holidays_prior_scale=10.0,     # Controls holiday effects
    seasonality_prior_scale=10.0,  # Controls seasonality effects
    interval_width=0.80           # 80% confidence intervals
)

print("Model configuration:")
print(f"  - Yearly seasonality: Enabled")
print(f"  - Weekly seasonality: Enabled")
print(f"  - Daily seasonality: Disabled")
print(f"  - Holidays: {len(holiday_df)} holiday periods")
print(f"  - Seasonality mode: Additive")
print(f"  - Changepoint prior scale: 0.05")

# Train the model
print("\n" + "=" * 50)
print("MODEL TRAINING")
print("=" * 50)

print("Training Prophet model...")
model.fit(train_data)
print("Model training completed!")

# Make predictions on test set
print("\nGenerating predictions for test period...")
test_forecast = model.predict(test_data[['ds']])

# Calculate accuracy metrics
print("\n" + "=" * 50)
print("MODEL EVALUATION")
print("=" * 50)

# Calculate MAE and MAPE
actual = test_data['y'].values
predicted = test_forecast['yhat'].values

mae = np.mean(np.abs(actual - predicted))
mape = np.mean(np.abs((actual - predicted) / actual)) * 100
rmse = np.sqrt(np.mean((actual - predicted) ** 2))

print(f"Test Set Performance:")
print(f"  - Mean Absolute Error (MAE): ${mae:.3f}")
print(f"  - Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
print(f"  - Root Mean Square Error (RMSE): ${rmse:.3f}")

# Generate future predictions
print("\n" + "=" * 50)
print("FUTURE FORECASTING")
print("=" * 50)

# Create future dataframe for 52 weeks (1 year) ahead
future = model.make_future_dataframe(periods=52, freq='W')
print(f"Forecasting {52} weeks into the future...")

# Generate forecast
forecast = model.predict(future)
print("Forecast generated successfully!")

# Save results
print("\n" + "=" * 50)
print("SAVING RESULTS")
print("=" * 50)

# Save the model data
train_data.to_csv('prophet_train_data.csv', index=False)
test_data.to_csv('prophet_test_data.csv', index=False)
forecast.to_csv('prophet_forecast.csv', index=False)
holiday_df.to_csv('prophet_holidays.csv', index=False)

print("Files saved:")
print("  - prophet_train_data.csv: Training dataset")
print("  - prophet_test_data.csv: Test dataset") 
print("  - prophet_forecast.csv: Complete forecast results")
print("  - prophet_holidays.csv: Holiday definitions")

# Create basic visualizations
print("\n" + "=" * 50)
print("CREATING VISUALIZATIONS")
print("=" * 50)

# 1. Forecast plot
fig1 = model.plot(forecast)
plt.title('AvoCast: Avocado Price Forecast - BaltimoreWashington')
plt.ylabel('Average Price ($)')
plt.xlabel('Date')
plt.tight_layout()
plt.savefig('forecast_plot.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Components plot
fig2 = model.plot_components(forecast)
plt.suptitle('AvoCast: Forecast Components Analysis', fontsize=16)
plt.tight_layout()
plt.savefig('forecast_components.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Test vs Predicted plot
plt.figure(figsize=(12, 6))
plt.plot(test_data['ds'], test_data['y'], 'o-', label='Actual', color='blue', alpha=0.7)
plt.plot(test_data['ds'], test_forecast['yhat'], 'o-', label='Predicted', color='red', alpha=0.7)
plt.fill_between(test_data['ds'], 
                test_forecast['yhat_lower'], 
                test_forecast['yhat_upper'], 
                alpha=0.3, color='red', label='Confidence Interval')
plt.title('AvoCast: Test Set Performance')
plt.xlabel('Date')
plt.ylabel('Average Price ($)')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('test_performance.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualizations created:")
print("  - forecast_plot.png: Complete forecast visualization")
print("  - forecast_components.png: Trend and seasonality components")
print("  - test_performance.png: Test set accuracy visualization")

# Summary statistics
print("\n" + "=" * 50)
print("FORECAST SUMMARY")
print("=" * 50)

# Get forecast for next 12 weeks
next_12_weeks = forecast.tail(12)
print("Next 12 weeks forecast:")
for _, row in next_12_weeks.iterrows():
    print(f"  {row['ds'].strftime('%Y-%m-%d')}: ${row['yhat']:.2f} (${row['yhat_lower']:.2f} - ${row['yhat_upper']:.2f})")

# Trend analysis
trend_change = forecast['trend'].iloc[-1] - forecast['trend'].iloc[-53]  # Year-over-year
print(f"\nYear-over-year trend change: ${trend_change:.3f}")

if trend_change > 0:
    print("📈 Prices are trending upward")
elif trend_change < 0:
    print("📉 Prices are trending downward") 
else:
    print("➡️ Prices are relatively stable")

print("\n" + "=" * 50)
print("PROPHET MODEL DEVELOPMENT COMPLETE")
print("=" * 50)
print("Next steps:")
print("1. Detailed model evaluation and cross-validation")
print("2. Advanced visualizations and insights")
print("3. Business recommendations and dashboard design")

