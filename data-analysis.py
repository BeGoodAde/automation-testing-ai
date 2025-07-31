# Python Data Analysis with Copilot
# Advanced data analysis using pandas, numpy, and matplotlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Create sample dataset for analysis
# Generate realistic e-commerce sales data

class SalesAnalyzer:
    def __init__(self, data_file=None):
        # Initialize with sample data or load from file
        # Set up data cleaning and validation rules
        pass
    
    def load_data(self, file_path):
        # Load data from CSV, Excel, or JSON file
        # Handle different data formats and encodings
        # Validate data structure and types
        pass
    
    def clean_data(self):
        """Clean the dataset: handle missing values, standardize dates, remove duplicates"""
        if not hasattr(self, 'data') or self.data is None:
            print("❌ No data to clean. Please load data first.")
            return None
        
        df = self.data.copy()
        initial_records = len(df)
        print(f"🧹 Starting data cleaning process...")
        print(f"Initial dataset: {initial_records} records")
        
        # 1. Remove exact duplicates
        duplicates_before = df.duplicated().sum()
        df = df.drop_duplicates()
        duplicates_removed = duplicates_before
        print(f"✅ Removed {duplicates_removed} duplicate records")
        
        # 2. Handle missing values
        missing_summary = df.isnull().sum()
        if missing_summary.sum() > 0:
            print(f"📊 Missing values found:")
            for col, missing_count in missing_summary[missing_summary > 0].items():
                print(f"   - {col}: {missing_count} missing values")
            
            # Fill missing values based on column type
            for column in df.columns:
                if df[column].isnull().sum() > 0:
                    if df[column].dtype in ['int64', 'float64']:
                        # Fill numerical columns with median
                        df[column].fillna(df[column].median(), inplace=True)
                    else:
                        # Fill categorical columns with mode
                        df[column].fillna(df[column].mode()[0], inplace=True)
            print("✅ Missing values handled")
        else:
            print("✅ No missing values found")
        
        # 3. Standardize date formats
        try:
            df['order_date'] = pd.to_datetime(df['order_date'])
            print("✅ Date formats standardized")
        except Exception as e:
            print(f"⚠️ Date standardization warning: {e}")
        
        # 4. Validate and clean numerical data
        # Remove records with negative prices or quantities
        invalid_price = (df['price'] <= 0).sum()
        invalid_quantity = (df['quantity'] <= 0).sum()
        
        df = df[(df['price'] > 0) & (df['quantity'] > 0)]
        print(f"✅ Removed {invalid_price} records with invalid prices")
        print(f"✅ Removed {invalid_quantity} records with invalid quantities")
        
        # 5. Handle outliers using IQR method
        def remove_outliers(df, column):
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_count = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
            df_cleaned = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
            return df_cleaned, outliers_count
        
        # Remove outliers from total amount
        df, total_outliers = remove_outliers(df, 'total')
        print(f"✅ Removed {total_outliers} outliers from total amount")
        
        # 6. Validate data consistency
        # Check if total = price * quantity
        df['calculated_total'] = (df['price'] * df['quantity']).round(2)
        inconsistent = (abs(df['total'] - df['calculated_total']) > 0.01).sum()
        
        if inconsistent > 0:
            print(f"⚠️ Found {inconsistent} records with inconsistent totals, fixing...")
            df['total'] = df['calculated_total']
        
        df.drop('calculated_total', axis=1, inplace=True)
        
        # 7. Reset index after cleaning
        df.reset_index(drop=True, inplace=True)
        
        # Update the data
        self.data = df
        final_records = len(df)
        removed_records = initial_records - final_records
        
        print(f"\n🎯 Cleaning Summary:")
        print(f"   - Initial records: {initial_records}")
        print(f"   - Final records: {final_records}")
        print(f"   - Records removed: {removed_records}")
        print(f"   - Data quality improvement: {((final_records/initial_records)*100):.1f}%")
        
        return df
    
    def calculate_metrics(self):
        # Calculate key business metrics:
        # - Total revenue by period
        # - Average order value
        # - Customer acquisition cost
        # - Product performance metrics
        # - Seasonal trends
        pass
    
    def customer_segmentation(self):
        # Segment customers based on purchase behavior
        # RFM analysis (Recency, Frequency, Monetary)
        # Identify high-value customers
        # Analyze customer lifetime value
        pass
    
    def product_analysis(self):
        # Analyze product performance
        # Identify best and worst sellers
        # Calculate profit margins
        # Analyze inventory turnover
        pass
    
    def time_series_analysis(self):
        # Analyze sales trends over time
        # Identify seasonal patterns
        # Forecast future sales
        # Detect anomalies in sales data
        pass

class DataVisualizer:
    def __init__(self, analyzer):
        # Set up visualization themes and styles
        # Configure chart templates
        pass
    
    def create_dashboard(self):
        # Create comprehensive sales dashboard
        # Include multiple chart types and KPIs
        # Make it interactive and responsive
        pass
    
    def revenue_charts(self):
        # Create revenue visualization charts
        # Monthly/quarterly revenue trends
        # Revenue by product category
        # Geographic revenue distribution
        pass
    
    def customer_charts(self):
        # Customer analysis visualizations
        # Customer acquisition trends
        # Customer segment distribution
        # Customer lifetime value charts
        pass

# Sample data generation for practice
def generate_sample_data(num_records=1000):
    """Generate realistic e-commerce dataset for analysis practice"""
    np.random.seed(42)  # For reproducible results
    
    # Product categories and names
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty']
    products = {
        'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Tablet', 'Camera'],
        'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes'],
        'Home & Garden': ['Chair', 'Table', 'Lamp', 'Plant', 'Curtains'],
        'Books': ['Fiction Novel', 'Cookbook', 'Biography', 'Textbook', 'Magazine'],
        'Sports': ['Basketball', 'Tennis Racket', 'Yoga Mat', 'Running Shoes', 'Weights'],
        'Beauty': ['Lipstick', 'Foundation', 'Perfume', 'Skincare Set', 'Hair Product']
    }
    
    # Generate customer data
    customer_ids = [f'CUST_{i:04d}' for i in range(1, min(num_records//3, 500) + 1)]
    
    # Generate order data
    orders = []
    for i in range(num_records):
        # Random date within last 2 years
        start_date = datetime.now() - timedelta(days=730)
        random_days = np.random.randint(0, 730)
        order_date = start_date + timedelta(days=random_days)
        
        # Random customer
        customer_id = np.random.choice(customer_ids)
        
        # Random product
        category = np.random.choice(categories)
        product = np.random.choice(products[category])
        
        # Realistic pricing based on category
        base_prices = {
            'Electronics': (200, 1500),
            'Clothing': (20, 200),
            'Home & Garden': (30, 500),
            'Books': (10, 50),
            'Sports': (15, 300),
            'Beauty': (10, 100)
        }
        min_price, max_price = base_prices[category]
        price = round(np.random.uniform(min_price, max_price), 2)
        
        # Quantity (most orders are 1-3 items)
        quantity = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
        
        # Calculate total
        total = round(price * quantity, 2)
        
        orders.append({
            'order_id': f'ORD_{i:06d}',
            'customer_id': customer_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'product_name': product,
            'category': category,
            'price': price,
            'quantity': quantity,
            'total': total,
            'month': order_date.strftime('%Y-%m'),
            'day_of_week': order_date.strftime('%A')
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(orders)
    
    # Add some seasonal trends (higher sales in November-December)
    seasonal_boost = df['order_date'].apply(lambda x: 
        1.3 if x.split('-')[1] in ['11', '12'] else 1.0)
    df['total'] = df['total'] * seasonal_boost
    df['total'] = df['total'].round(2)
    
    return df

# Create and save sample dataset
def create_sample_dataset():
    """Create sample dataset and save to CSV"""
    print("Generating sample e-commerce dataset...")
    df = generate_sample_data(1000)
    
    # Save to CSV
    csv_path = 'sample_sales_data.csv'
    df.to_csv(csv_path, index=False)
    print(f"Sample dataset saved to {csv_path}")
    
    # Display basic info
    print(f"\nDataset Summary:")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['order_date'].min()} to {df['order_date'].max()}")
    print(f"Total revenue: ${df['total'].sum():,.2f}")
    print(f"Categories: {df['category'].unique()}")
    
    return df

# Machine learning for sales prediction
class SalesPredictor:
    def __init__(self, historical_data):
        # Initialize ML models for sales forecasting
        # Feature engineering and data preparation
        pass
    
    def prepare_features(self):
        # Create features for machine learning
        # Time-based features (day, month, season)
        # Product features (category, price, popularity)
        # Customer features (segment, history)
        pass
    
    def train_model(self):
        # Train multiple ML models
        # Linear regression, random forest, neural networks
        # Cross-validation and hyperparameter tuning
        pass
    
    def predict_sales(self, forecast_period=30):
        # Generate sales predictions
        # Include confidence intervals
        # Scenario analysis (optimistic, realistic, pessimistic)
        pass

if __name__ == "__main__":
    # Main execution workflow
    print("🚀 E-commerce Data Analysis with Copilot")
    print("=" * 50)
    
    # Create sample dataset
    df = create_sample_dataset()
    
    # Initialize analyzer with the data
    analyzer = SalesAnalyzer()
    analyzer.data = df  # Store data in analyzer
    
    # Quick analysis preview
    print("\n📊 Quick Analysis Preview:")
    print(f"Average order value: ${df['total'].mean():.2f}")
    print(f"Most popular category: {df['category'].value_counts().index[0]}")
    print(f"Best sales day: {df['day_of_week'].value_counts().index[0]}")
    
    # Show sample data
    print("\n📋 Sample Data Preview:")
    print(df.head())
    
    print("\n✨ Ready for analysis! Use Copilot to implement the methods above.")
