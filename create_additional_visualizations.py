#!/usr/bin/env python3
"""
AvoCast - Additional Visualizations
Creating comprehensive charts for model evaluation
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

print("=== AvoCast: Creating Additional Visualizations ===")

# Load the data
forecast = pd.read_csv('prophet_forecast.csv')
train_data = pd.read_csv('prophet_train_data.csv')
test_data = pd.read_csv('prophet_test_data.csv')

# Convert date columns
forecast['ds'] = pd.to_datetime(forecast['ds'])
train_data['ds'] = pd.to_datetime(train_data['ds'])
test_data['ds'] = pd.to_datetime(test_data['ds'])

# 1. Residuals Analysis
print("Creating residuals analysis...")
test_forecast = forecast[forecast['ds'].isin(test_data['ds'])].copy()
test_merged = test_data.merge(test_forecast[['ds', 'yhat']], on='ds')
test_merged['residuals'] = test_merged['y'] - test_merged['yhat']

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Residuals over time
axes[0,0].plot(test_merged['ds'], test_merged['residuals'], 'o-', alpha=0.7)
axes[0,0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
axes[0,0].set_title('Residuals Over Time')
axes[0,0].set_xlabel('Date')
axes[0,0].set_ylabel('Residuals ($)')
axes[0,0].tick_params(axis='x', rotation=45)

# Residuals histogram
axes[0,1].hist(test_merged['residuals'], bins=10, alpha=0.7, edgecolor='black')
axes[0,1].set_title('Residuals Distribution')
axes[0,1].set_xlabel('Residuals ($)')
axes[0,1].set_ylabel('Frequency')

# Actual vs Predicted scatter
axes[1,0].scatter(test_merged['y'], test_merged['yhat'], alpha=0.7)
axes[1,0].plot([test_merged['y'].min(), test_merged['y'].max()], 
               [test_merged['y'].min(), test_merged['y'].max()], 
               'r--', alpha=0.7)
axes[1,0].set_title('Actual vs Predicted')
axes[1,0].set_xlabel('Actual Price ($)')
axes[1,0].set_ylabel('Predicted Price ($)')

# Q-Q plot approximation
from scipy import stats
stats.probplot(test_merged['residuals'], dist="norm", plot=axes[1,1])
axes[1,1].set_title('Q-Q Plot (Normality Check)')

plt.tight_layout()
plt.savefig('model_diagnostics.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Seasonal Decomposition Visualization
print("Creating seasonal decomposition visualization...")
fig, axes = plt.subplots(4, 1, figsize=(15, 12))

# Original time series
axes[0].plot(train_data['ds'], train_data['y'], 'b-', alpha=0.7, label='Training Data')
axes[0].plot(test_data['ds'], test_data['y'], 'g-', alpha=0.7, label='Test Data')
axes[0].set_title('Original Time Series - Avocado Prices')
axes[0].set_ylabel('Price ($)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Trend component
trend_data = forecast[['ds', 'trend']].copy()
axes[1].plot(trend_data['ds'], trend_data['trend'], 'r-', linewidth=2)
axes[1].set_title('Trend Component')
axes[1].set_ylabel('Trend ($)')
axes[1].grid(True, alpha=0.3)

# Yearly seasonality
yearly_data = forecast[['ds', 'yearly']].copy()
axes[2].plot(yearly_data['ds'], yearly_data['yearly'], 'orange', linewidth=2)
axes[2].set_title('Yearly Seasonality')
axes[2].set_ylabel('Seasonal Effect ($)')
axes[2].grid(True, alpha=0.3)

# Weekly seasonality
weekly_data = forecast[['ds', 'weekly']].copy()
axes[3].plot(weekly_data['ds'], weekly_data['weekly'], 'purple', linewidth=2)
axes[3].set_title('Weekly Seasonality')
axes[3].set_ylabel('Weekly Effect ($)')
axes[3].set_xlabel('Date')
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('seasonal_decomposition.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Forecast Uncertainty Analysis
print("Creating forecast uncertainty analysis...")
future_forecast = forecast[forecast['ds'] > test_data['ds'].max()].copy()

fig, axes = plt.subplots(2, 1, figsize=(15, 10))

# Forecast with uncertainty bands
axes[0].plot(train_data['ds'], train_data['y'], 'b-', alpha=0.7, label='Training Data')
axes[0].plot(test_data['ds'], test_data['y'], 'g-', alpha=0.7, label='Test Data')
axes[0].plot(future_forecast['ds'], future_forecast['yhat'], 'r-', linewidth=2, label='Forecast')
axes[0].fill_between(future_forecast['ds'], 
                    future_forecast['yhat_lower'], 
                    future_forecast['yhat_upper'], 
                    alpha=0.3, color='red', label='80% Confidence Interval')
axes[0].set_title('Forecast with Uncertainty Bands')
axes[0].set_ylabel('Price ($)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Uncertainty width over time
future_forecast['uncertainty_width'] = future_forecast['yhat_upper'] - future_forecast['yhat_lower']
axes[1].plot(future_forecast['ds'], future_forecast['uncertainty_width'], 'purple', linewidth=2)
axes[1].set_title('Forecast Uncertainty Width Over Time')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Uncertainty Width ($)')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('forecast_uncertainty.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Holiday Effects Visualization
print("Creating holiday effects visualization...")
holidays = pd.read_csv('prophet_holidays.csv')
holidays['ds'] = pd.to_datetime(holidays['ds'])

# Get holiday effects from forecast
holiday_effects = forecast[['ds']].copy()
for holiday in holidays['holiday'].unique():
    if holiday in forecast.columns:
        holiday_effects[holiday] = forecast[holiday]

fig, ax = plt.subplots(figsize=(15, 8))

# Plot base forecast
ax.plot(forecast['ds'], forecast['yhat'], 'b-', alpha=0.5, label='Base Forecast')

# Highlight holiday periods
colors = ['red', 'orange', 'green', 'purple']
for i, holiday in enumerate(holidays['holiday'].unique()):
    holiday_dates = holidays[holidays['holiday'] == holiday]['ds']
    for date in holiday_dates:
        ax.axvline(x=date, color=colors[i % len(colors)], alpha=0.7, linestyle='--', 
                  label=holiday if date == holiday_dates.iloc[0] else "")

ax.set_title('Holiday Effects on Avocado Prices')
ax.set_xlabel('Date')
ax.set_ylabel('Price ($)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('holiday_effects.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Performance Metrics Summary
print("Creating performance metrics summary...")
# Calculate additional metrics
test_merged = test_data.merge(test_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')
mae = np.mean(np.abs(test_merged['y'] - test_merged['yhat']))
mape = np.mean(np.abs((test_merged['y'] - test_merged['yhat']) / test_merged['y'])) * 100
rmse = np.sqrt(np.mean((test_merged['y'] - test_merged['yhat']) ** 2))

# Coverage probability (how often actual values fall within confidence intervals)
coverage = np.mean((test_merged['y'] >= test_merged['yhat_lower']) & 
                  (test_merged['y'] <= test_merged['yhat_upper'])) * 100

# Create metrics visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Metrics bar chart
metrics = ['MAE', 'MAPE (%)', 'RMSE', 'Coverage (%)']
values = [mae, mape, rmse, coverage]
colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold']

axes[0,0].bar(metrics, values, color=colors)
axes[0,0].set_title('Model Performance Metrics')
axes[0,0].set_ylabel('Value')
for i, v in enumerate(values):
    axes[0,0].text(i, v + max(values)*0.01, f'{v:.2f}', ha='center', va='bottom')

# Error distribution by month
test_merged['month'] = test_merged['ds'].dt.month
test_merged['abs_error'] = np.abs(test_merged['y'] - test_merged['yhat'])
monthly_error = test_merged.groupby('month')['abs_error'].mean()

axes[0,1].bar(monthly_error.index, monthly_error.values, color='lightblue')
axes[0,1].set_title('Average Absolute Error by Month')
axes[0,1].set_xlabel('Month')
axes[0,1].set_ylabel('MAE ($)')

# Prediction accuracy over time
test_merged['abs_pct_error'] = np.abs((test_merged['y'] - test_merged['yhat']) / test_merged['y']) * 100
axes[1,0].plot(test_merged['ds'], test_merged['abs_pct_error'], 'o-', color='red', alpha=0.7)
axes[1,0].set_title('Prediction Accuracy Over Time')
axes[1,0].set_xlabel('Date')
axes[1,0].set_ylabel('Absolute % Error')
axes[1,0].tick_params(axis='x', rotation=45)

# Confidence interval width
test_merged['ci_width'] = test_merged['yhat_upper'] - test_merged['yhat_lower']
axes[1,1].plot(test_merged['ds'], test_merged['ci_width'], 'o-', color='purple', alpha=0.7)
axes[1,1].set_title('Confidence Interval Width')
axes[1,1].set_xlabel('Date')
axes[1,1].set_ylabel('CI Width ($)')
axes[1,1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('performance_metrics.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nAdditional visualizations created:")
print("  - model_diagnostics.png: Residuals analysis and model diagnostics")
print("  - seasonal_decomposition.png: Detailed breakdown of time series components")
print("  - forecast_uncertainty.png: Future predictions with uncertainty analysis")
print("  - holiday_effects.png: Impact of holidays on price predictions")
print("  - performance_metrics.png: Comprehensive model performance evaluation")

print(f"\nModel Performance Summary:")
print(f"  - Mean Absolute Error: ${mae:.3f}")
print(f"  - Mean Absolute Percentage Error: {mape:.2f}%")
print(f"  - Root Mean Square Error: ${rmse:.3f}")
print(f"  - Confidence Interval Coverage: {coverage:.1f}%")

print("\n=== Additional Visualizations Complete ===")

