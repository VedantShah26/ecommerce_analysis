# E-Commerce Customer Segmentation and Purchase Behavior Analysis

This project performs advanced customer segmentation and purchase behavior analysis on an e-commerce dataset using various machine learning techniques and data visualization tools.

## Project Structure
```
ecommerce_analysis/
├── data/                      # Data files
│   └── ecommerce_transactions.csv
├── src/                       # Source code
│   ├── data_preprocessing.py
│   ├── customer_segmentation.py
│   ├── visualization.py
│   └── predictive_analytics.py
├── predictions/              # Generated predictions and forecasts
│   ├── sales_forecast.csv
│   ├── sales_forecast.png
│   ├── sales_decomposition.png
│   ├── ltv_prediction.png
│   └── ltv_feature_importance.png
├── visualizations/          # Generated visualizations
│   ├── purchase_distribution.png
│   ├── payment_methods.png
│   ├── product_categories.png
│   ├── purchase_frequency.png
│   ├── geographic_distribution.png
│   └── daily_sales.png
├── sql/                     # SQL scripts
│   └── schema.sql
├── requirements.txt         # Project dependencies
├── .env                    # Environment variables (not in repo)
└── README.md               # Project documentation
```

## Technologies Used
- Python 3.8+
- MySQL for data storage
- Pandas & NumPy for data manipulation
- Matplotlib & Seaborn for visualization
- Scikit-learn for machine learning
- Statsmodels for time series analysis
- Git for version control

## Key Features
1. Customer Segmentation Analysis
   - Purchase behavior patterns
   - Customer lifetime value prediction
   - Geographic distribution analysis

2. Sales Forecasting
   - 30-day sales predictions
   - Seasonal decomposition analysis
   - Trend analysis

3. Predictive Analytics
   - Customer lifetime value modeling
   - Feature importance analysis
   - Model performance metrics

## Setup Instructions
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MySQL database:
   - Create a database named 'ecommerce_analysis'
   - Run the SQL scripts in the sql/ directory

4. Configure environment variables:
   - Create a .env file with your MySQL credentials:
     ```
     DB_HOST=localhost
     DB_USER=your_username
     DB_PASSWORD=your_password
     DB_NAME=ecommerce_analysis
     ```

## Running the Analysis
1. Data Preprocessing:
   ```bash
   python src/data_preprocessing.py
   ```

2. Customer Segmentation:
   ```bash
   python src/customer_segmentation.py
   ```

3. Visualization Generation:
   ```bash
   python src/visualization.py
   ```

4. Predictive Analytics:
   ```bash
   python src/predictive_analytics.py
   ```

## Analysis Results
The analysis generates several key insights:
- Average daily sales: $34,415.85
- 30-day sales forecast: $33,909.96
- Customer lifetime value predictions with R² = 1.0000
- Detailed visualizations of customer behavior and sales patterns

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 