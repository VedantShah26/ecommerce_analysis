import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Load environment variables
load_dotenv()

def create_database_connection():
    """Create connection to MySQL database."""
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ecommerce_analysis')
    )
    return connection

def get_data(connection):
    """Get transaction data for analysis."""
    query = """
    SELECT 
        customer_id,
        transaction_date,
        total_amount,
        product_category,
        country
    FROM transactions
    """
    return pd.read_sql(query, connection)

def prepare_time_series_data(df):
    """Prepare data for time series analysis."""
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    daily_sales = df.groupby('transaction_date')['total_amount'].sum().reset_index()
    daily_sales.set_index('transaction_date', inplace=True)
    return daily_sales

def forecast_sales(daily_sales):
    """Forecast future sales using Holt-Winters method."""
    # Create directory for predictions if it doesn't exist
    if not os.path.exists('predictions'):
        os.makedirs('predictions')
    
    # Handle missing values and ensure positive values
    daily_sales['total_amount'] = daily_sales['total_amount'].fillna(0)
    daily_sales['total_amount'] = daily_sales['total_amount'].clip(lower=0)
    
    # Ensure enough data points for seasonal decomposition
    if len(daily_sales) >= 14:  # At least 2 weeks of data
        # Decompose the time series
        decomposition = seasonal_decompose(daily_sales['total_amount'], period=7)
        
        # Plot decomposition
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 12))
        decomposition.observed.plot(ax=ax1)
        ax1.set_title('Observed')
        decomposition.trend.plot(ax=ax2)
        ax2.set_title('Trend')
        decomposition.seasonal.plot(ax=ax3)
        ax3.set_title('Seasonal')
        decomposition.resid.plot(ax=ax4)
        ax4.set_title('Residual')
        plt.tight_layout()
        plt.savefig('predictions/sales_decomposition.png')
        plt.close()
    
    # Fit Holt-Winters model with optimized parameters
    model = ExponentialSmoothing(
        daily_sales['total_amount'],
        seasonal_periods=7,
        trend='add',
        seasonal='add',
        initialization_method='estimated',
        use_boxcox=True
    ).fit(optimized=True)
    
    # Make predictions for next 30 days
    forecast_horizon = 30
    forecast = model.forecast(forecast_horizon)
    
    # Plot actual vs predicted
    plt.figure(figsize=(15, 6))
    plt.plot(daily_sales.index, daily_sales['total_amount'], label='Actual')
    plt.plot(forecast.index, forecast, label='Forecast', color='red')
    plt.title('Sales Forecast - Next 30 Days')
    plt.xlabel('Date')
    plt.ylabel('Sales Amount')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('predictions/sales_forecast.png')
    plt.close()
    
    # Print forecast metrics
    print("\nForecast Summary:")
    print(f"Average Daily Sales (Historical): ${daily_sales['total_amount'].mean():.2f}")
    print(f"Average Daily Sales (Forecast): ${forecast.mean():.2f}")
    print(f"Forecast Trend: {'Increasing' if forecast.mean() > daily_sales['total_amount'].mean() else 'Decreasing'}")
    
    return forecast

def calculate_customer_ltv(df):
    """Calculate and predict customer lifetime value."""
    # Calculate key customer metrics
    customer_metrics = df.groupby('customer_id').agg({
        'total_amount': ['count', 'sum', 'mean'],
        'transaction_date': ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = ['customer_id', 'frequency', 'monetary', 'avg_order_value', 
                              'first_purchase', 'last_purchase']
    
    # Calculate customer age and purchase frequency
    customer_metrics['customer_age'] = (
        pd.to_datetime(customer_metrics['last_purchase']) - 
        pd.to_datetime(customer_metrics['first_purchase'])
    ).dt.days
    
    # Handle zero customer age
    customer_metrics['customer_age'] = customer_metrics['customer_age'].clip(lower=1)
    
    customer_metrics['purchase_frequency'] = customer_metrics['frequency'] / customer_metrics['customer_age']
    
    # Calculate LTV (cap at reasonable maximum)
    customer_metrics['ltv'] = (
        customer_metrics['avg_order_value'] * 
        customer_metrics['purchase_frequency'] * 
        365  # Annualized
    ).clip(upper=1000000)  # Cap at 1 million
    
    # Remove infinite values and outliers
    customer_metrics = customer_metrics.replace([np.inf, -np.inf], np.nan).dropna()
    
    # Prepare features for LTV prediction
    features = ['frequency', 'monetary', 'avg_order_value', 'customer_age', 'purchase_frequency']
    X = customer_metrics[features]
    y = customer_metrics['ltv']
    
    # Remove outliers using IQR method
    Q1 = y.quantile(0.25)
    Q3 = y.quantile(0.75)
    IQR = Q3 - Q1
    mask = ~((y < (Q1 - 1.5 * IQR)) | (y > (Q3 + 1.5 * IQR)))
    X = X[mask]
    y = y[mask]
    
    # Split data and train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    
    # Calculate model performance
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\nModel Performance:")
    print(f"R² Score: {r2:.4f}")
    print(f"RMSE: ${rmse:.2f}")
    
    # Plot actual vs predicted LTV
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual LTV')
    plt.ylabel('Predicted LTV')
    plt.title(f'Customer Lifetime Value: Actual vs Predicted (R² = {r2:.4f})')
    plt.tight_layout()
    plt.savefig('predictions/ltv_prediction.png')
    plt.close()
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': abs(model.coef_)
    })
    feature_importance = feature_importance.sort_values('importance', ascending=True)
    
    plt.barh(feature_importance['feature'], feature_importance['importance'])
    plt.title('Feature Importance for LTV Prediction')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig('predictions/ltv_feature_importance.png')
    plt.close()
    
    return model, scaler, feature_importance

def main():
    try:
        # Create database connection
        print("Connecting to database...")
        connection = create_database_connection()
        
        # Get data
        print("Getting transaction data...")
        df = get_data(connection)
        
        # Prepare time series data
        print("Preparing time series data...")
        daily_sales = prepare_time_series_data(df)
        
        # Forecast sales
        print("Forecasting sales...")
        sales_forecast = forecast_sales(daily_sales)
        
        # Calculate and predict customer LTV
        print("Calculating customer lifetime value...")
        ltv_model, ltv_scaler, feature_importance = calculate_customer_ltv(df)
        
        print("Predictive analytics completed successfully! Check the 'predictions' folder for results.")
        
        # Save the results
        sales_forecast.to_csv('predictions/sales_forecast.csv')
        feature_importance.to_csv('predictions/ltv_feature_importance.csv')
        
    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main() 