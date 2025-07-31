# Test the data cleaning functionality with proper Python implementation
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Generate sample data function for testing
def generate_sample_data(num_records=1000):
    """Generate realistic e-commerce sales data for testing"""
    
    # Product catalog
    products = {
        'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones'],
        'Home': ['Coffee Mug', 'Plant Pot', 'Desk Chair', 'Table Lamp'],
        'Books': ['Cookbook', 'Novel', 'Textbook', 'Magazine'],
        'Sports': ['Running Shoes', 'Yoga Mat', 'Water Bottle', 'Fitness Tracker']
    }
    
    # Generate data
    data = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(num_records):
        # Random date in 2024
        random_days = random.randint(0, 365)
        order_date = start_date + timedelta(days=random_days)
        
        # Random category and product
        category = random.choice(list(products.keys()))
        product = random.choice(products[category])
        
        # Base prices by category
        base_prices = {'Electronics': 500, 'Home': 25, 'Books': 15, 'Sports': 50}
        base_price = base_prices[category]
        price = round(base_price * random.uniform(0.5, 2.0), 2)
        
        # Quantity (weighted towards 1-2 items)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 30, 15, 4, 1])[0]
        
        # Revenue
        revenue = round(price * quantity, 2)
        
        # Create record
        record = {
            'order_id': f'ORD_{i+1:04d}',
            'customer_id': f'CUST_{random.randint(1, 200):03d}',
            'order_date': order_date.strftime('%Y-%m-%d'),
            'product_name': product,
            'category': category,
            'price': price,
            'quantity': quantity,
            'total': revenue,
            'month': order_date.strftime('%Y-%m'),
            'day_of_week': order_date.strftime('%A')
        }
        
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Introduce some data quality issues for testing cleaning
    # Add some missing values
    missing_indices = random.sample(range(len(df)), k=int(len(df) * 0.05))  # 5% missing
    df.loc[missing_indices[:len(missing_indices)//2], 'customer_id'] = np.nan
    df.loc[missing_indices[len(missing_indices)//2:], 'price'] = np.nan
    
    # Add some duplicates
    duplicate_rows = df.sample(n=int(len(df) * 0.02))  # 2% duplicates
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    # Add some invalid data
    invalid_indices = random.sample(range(len(df)), k=10)
    df.loc[invalid_indices[:5], 'price'] = -1  # Invalid negative prices
    df.loc[invalid_indices[5:], 'quantity'] = 0  # Invalid zero quantities
    
    return df

# SalesAnalyzer class with cleaning functionality
class SalesAnalyzer:
    def __init__(self, data=None):
        self.data = data
        self.original_data = None
    
    def clean_data(self):
        """Clean the dataset: handle missing values, standardize dates, remove duplicates"""
        if self.data is None:
            print("❌ No data to clean. Please load data first.")
            return None
        
        # Store original data
        self.original_data = self.data.copy()
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
                print(f"   {col}: {missing_count} missing values")
            
            # Fill missing values based on column type
            for column in df.columns:
                if df[column].isnull().sum() > 0:
                    if df[column].dtype in ['int64', 'float64']:
                        # For numerical columns, use median
                        median_value = df[column].median()
                        df[column].fillna(median_value, inplace=True)
                        print(f"   ✅ Filled {column} missing values with median: {median_value}")
                    else:
                        # For categorical columns, use mode
                        mode_value = df[column].mode()[0] if not df[column].mode().empty else 'Unknown'
                        df[column].fillna(mode_value, inplace=True)
                        print(f"   ✅ Filled {column} missing values with mode: {mode_value}")
        else:
            print("✅ No missing values found")
        
        # 3. Remove invalid data
        invalid_prices = (df['price'] <= 0).sum()
        invalid_quantities = (df['quantity'] <= 0).sum()
        
        df = df[(df['price'] > 0) & (df['quantity'] > 0)]
        print(f"✅ Removed {invalid_prices} records with invalid prices")
        print(f"✅ Removed {invalid_quantities} records with invalid quantities")
        
        # 4. Standardize date formats
        try:
            df['order_date'] = pd.to_datetime(df['order_date'])
            print("✅ Standardized date formats")
        except Exception as e:
            print(f"⚠️ Warning: Could not standardize dates: {e}")
        
        # 5. Data consistency checks
        # Recalculate total = price × quantity
        df['calculated_total'] = df['price'] * df['quantity']
        inconsistent_totals = (abs(df['total'] - df['calculated_total']) > 0.01).sum()
        
        if inconsistent_totals > 0:
            df['total'] = df['calculated_total']
            print(f"✅ Fixed {inconsistent_totals} inconsistent total calculations")
        
        df = df.drop('calculated_total', axis=1)  # Remove helper column
        
        # 6. Remove outliers (using IQR method)
        Q1 = df['total'].quantile(0.25)
        Q3 = df['total'].quantile(0.75)
        IQR = Q3 - Q1
        
        outlier_threshold_lower = Q1 - 1.5 * IQR
        outlier_threshold_upper = Q3 + 1.5 * IQR
        
        outliers_before = len(df)
        df = df[(df['total'] >= outlier_threshold_lower) & (df['total'] <= outlier_threshold_upper)]
        outliers_removed = outliers_before - len(df)
        print(f"✅ Removed {outliers_removed} outlier records")
        
        # Final summary
        final_records = len(df)
        records_removed = initial_records - final_records
        data_quality_improvement = (records_removed / initial_records) * 100
        
        print(f"\n📈 Data Cleaning Summary:")
        print(f"   Initial records: {initial_records}")
        print(f"   Final records: {final_records}")
        print(f"   Records removed: {records_removed}")
        print(f"   Data quality improvement: {data_quality_improvement:.1f}%")
        
        # Update instance data
        self.data = df
        return df

# Test the cleaning functionality
def test_data_cleaning():
    print("🧪 Testing Data Cleaning Functionality")
    print("=" * 50)

    # Generate sample data with quality issues
    print("1. Generating sample dataset with data quality issues...")
    df = generate_sample_data(1000)
    print(f"Generated {len(df)} records")
    
    print(f"\nInitial data quality assessment:")
    print(f"   Missing values: {df.isnull().sum().sum()}")
    print(f"   Duplicate records: {df.duplicated().sum()}")
    print(f"   Invalid prices (≤ 0): {(df['price'] <= 0).sum()}")
    print(f"   Invalid quantities (≤ 0): {(df['quantity'] <= 0).sum()}")

    # Initialize analyzer
    print("\n2. Initializing SalesAnalyzer...")
    analyzer = SalesAnalyzer(df)

    # Test cleaning function
    print("\n3. Testing data cleaning...")
    cleaned_df = analyzer.clean_data()

    print(f"\n4. Post-cleaning data quality assessment:")
    print(f"   Missing values: {cleaned_df.isnull().sum().sum()}")
    print(f"   Duplicate records: {cleaned_df.duplicated().sum()}")
    print(f"   Invalid prices (≤ 0): {(cleaned_df['price'] <= 0).sum()}")
    print(f"   Invalid quantities (≤ 0): {(cleaned_df['quantity'] <= 0).sum()}")

    print(f"\n5. Cleaned dataset shape: {cleaned_df.shape}")
    print(f"\n6. Sample of cleaned data:")
    print(cleaned_df.head())

    print(f"\n7. Data types after cleaning:")
    print(cleaned_df.dtypes)

    print(f"\n8. Summary statistics:")
    print(cleaned_df.describe())

    print("\n✅ Data cleaning test completed successfully!")
    return cleaned_df

if __name__ == "__main__":
    test_data_cleaning()