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
        self.data = None
        self.data_file = data_file
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path):
        """Load data from CSV, Excel, or JSON file with Copilot assistance"""
        # Handle different data formats and encodings
        # Validate data structure and types
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            print(f"✅ Data loaded successfully from {file_path}")
            print(f"📊 Shape: {self.data.shape}")
            return self.data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def clean_data(self):
        """Remove duplicates and handle missing values with Copilot assistance"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        # Remove duplicates and handle missing values
        # Standardize date formats
        # Validate numerical data ranges
        # Handle outliers and anomalies
        initial_shape = self.data.shape
        
        # Remove duplicates
        self.data = self.data.drop_duplicates()
        
        # Handle missing values
        self.data = self.data.fillna(method='ffill')  # Forward fill
        
        # Convert date columns
        if 'order_date' in self.data.columns:
            self.data['order_date'] = pd.to_datetime(self.data['order_date'])
        
        print(f"🧹 Data cleaned: {initial_shape} → {self.data.shape}")
        return self.data
    
    def calculate_metrics(self):
        """Calculate key business metrics with Copilot assistance"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        # Calculate key business metrics:
        # - Total revenue by period
        # - Average order value
        # - Customer acquisition cost
        # - Product performance metrics
        # - Seasonal trends
        metrics = {
            'total_revenue': self.data['total'].sum(),
            'average_order_value': self.data['total'].mean(),
            'total_orders': len(self.data),
            'unique_customers': self.data['customer_id'].nunique(),
            'unique_products': self.data['product_name'].nunique(),
            'top_category': self.data['category'].value_counts().index[0],
            'revenue_by_category': self.data.groupby('category')['total'].sum().to_dict()
        }
        
        print("📊 Key Business Metrics:")
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                print(f"   {key}: {value:,.2f}")
            else:
                print(f"   {key}: {value}")
        
        return metrics
    
    def customer_segmentation(self):
        """Segment customers based on purchase behavior (RFM analysis)"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        # Segment customers based on purchase behavior
        # RFM analysis (Recency, Frequency, Monetary)
        # Identify high-value customers
        # Analyze customer lifetime value
        
        # Convert order_date to datetime if needed
        self.data['order_date'] = pd.to_datetime(self.data['order_date'])
        current_date = self.data['order_date'].max()
        
        rfm = self.data.groupby('customer_id').agg({
            'order_date': lambda x: (current_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'total': 'sum'  # Monetary
        }).rename(columns={
            'order_date': 'recency',
            'order_id': 'frequency',
            'total': 'monetary'
        })
        
        # Create RFM scores
        rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
        
        # Combine scores
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        
        print("👥 Customer Segmentation (RFM Analysis):")
        print(f"   Total customers analyzed: {len(rfm)}")
        print(f"   Average recency: {rfm['recency'].mean():.1f} days")
        print(f"   Average frequency: {rfm['frequency'].mean():.1f} orders")
        print(f"   Average monetary: ${rfm['monetary'].mean():.2f}")
        
        return rfm
    
    def product_analysis(self):
        """Analyze product performance with Copilot assistance"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        # Analyze product performance
        # Identify best and worst sellers
        # Calculate profit margins (assuming 30% margin)
        # Analyze inventory turnover
        
        product_metrics = self.data.groupby('product_name').agg({
            'total': ['sum', 'mean', 'count'],
            'quantity': 'sum'
        }).round(2)
        
        product_metrics.columns = ['total_revenue', 'avg_order_value', 'order_count', 'total_quantity']
        product_metrics = product_metrics.sort_values('total_revenue', ascending=False)
        
        # Add profit estimation (30% margin)
        product_metrics['estimated_profit'] = product_metrics['total_revenue'] * 0.3
        
        print("🛍️ Product Performance Analysis:")
        print("   Top 5 Products by Revenue:")
        print(product_metrics.head().to_string())
        
        return product_metrics
    
    def time_series_analysis(self):
        """Analyze sales trends over time with Copilot assistance"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        # Analyze sales trends over time
        # Identify seasonal patterns
        # Forecast future sales
        # Detect anomalies in sales data
        
        self.data['order_date'] = pd.to_datetime(self.data['order_date'])
        
        # Monthly trends
        monthly_sales = self.data.groupby(self.data['order_date'].dt.to_period('M')).agg({
            'total': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Daily trends
        daily_sales = self.data.groupby('day_of_week')['total'].sum().sort_values(ascending=False)
        
        print("📈 Time Series Analysis:")
        print("   Monthly Sales Trend:")
        print(monthly_sales.to_string())
        print("\n   Best Sales Days:")
        print(daily_sales.to_string())
        
        return monthly_sales, daily_sales

class DataVisualizer:
    def __init__(self, analyzer):
        # Set up visualization themes and styles
        # Configure chart templates
        self.analyzer = analyzer
        self.data = analyzer.data if analyzer else None
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def create_dashboard(self):
        """Create comprehensive sales dashboard with Copilot assistance"""
        if self.data is None:
            print("❌ No data available for visualization")
            return None
        
        # Create comprehensive sales dashboard
        # Include multiple chart types and KPIs
        # Make it interactive and responsive
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('📊 E-commerce Sales Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Revenue by Category
        category_revenue = self.data.groupby('category')['total'].sum().sort_values(ascending=False)
        axes[0,0].pie(category_revenue.values, labels=category_revenue.index, autopct='%1.1f%%')
        axes[0,0].set_title('Revenue by Category')
        
        # 2. Monthly Sales Trend
        self.data['order_date'] = pd.to_datetime(self.data['order_date'])
        monthly_sales = self.data.groupby(self.data['order_date'].dt.to_period('M'))['total'].sum()
        monthly_sales.plot(kind='line', ax=axes[0,1])
        axes[0,1].set_title('Monthly Sales Trend')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Daily Sales Pattern
        daily_pattern = self.data.groupby('day_of_week')['total'].mean()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_pattern = daily_pattern.reindex(day_order)
        daily_pattern.plot(kind='bar', ax=axes[1,0])
        axes[1,0].set_title('Average Daily Sales')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. Price Distribution
        axes[1,1].hist(self.data['total'], bins=30, alpha=0.7)
        axes[1,1].set_title('Order Value Distribution')
        axes[1,1].set_xlabel('Order Value ($)')
        axes[1,1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('sales_dashboard.png', dpi=300, bbox_inches='tight')
        print("📊 Dashboard saved as 'sales_dashboard.png'")
        plt.show()
        
        return fig
    
    def revenue_charts(self):
        """Create revenue visualization charts with Copilot assistance"""
        if self.data is None:
            print("❌ No data available for visualization")
            return None
        
        # Create revenue visualization charts
        # Monthly/quarterly revenue trends
        # Revenue by product category
        # Geographic revenue distribution (if available)
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Monthly revenue
        self.data['order_date'] = pd.to_datetime(self.data['order_date'])
        monthly_revenue = self.data.groupby(self.data['order_date'].dt.to_period('M'))['total'].sum()
        monthly_revenue.plot(kind='bar', ax=axes[0])
        axes[0].set_title('Monthly Revenue')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Category revenue
        category_revenue = self.data.groupby('category')['total'].sum().sort_values(ascending=False)
        category_revenue.plot(kind='bar', ax=axes[1])
        axes[1].set_title('Revenue by Category')
        axes[1].tick_params(axis='x', rotation=45)
        
        # Revenue distribution
        axes[2].boxplot(self.data['total'])
        axes[2].set_title('Revenue Distribution')
        axes[2].set_ylabel('Order Value ($)')
        
        plt.tight_layout()
        plt.savefig('revenue_charts.png', dpi=300, bbox_inches='tight')
        print("📊 Revenue charts saved as 'revenue_charts.png'")
        plt.show()
        
        return fig
    
    def customer_charts(self):
        """Customer analysis visualizations with Copilot assistance"""
        if self.data is None:
            print("❌ No data available for visualization")
            return None
        
        # Customer analysis visualizations
        # Customer acquisition trends
        # Customer segment distribution
        # Customer lifetime value charts
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Customer order frequency
        customer_orders = self.data['customer_id'].value_counts()
        axes[0].hist(customer_orders, bins=20, alpha=0.7)
        axes[0].set_title('Customer Order Frequency Distribution')
        axes[0].set_xlabel('Number of Orders')
        axes[0].set_ylabel('Number of Customers')
        
        # Customer value distribution
        customer_value = self.data.groupby('customer_id')['total'].sum()
        axes[1].hist(customer_value, bins=20, alpha=0.7)
        axes[1].set_title('Customer Lifetime Value Distribution')
        axes[1].set_xlabel('Total Spent ($)')
        axes[1].set_ylabel('Number of Customers')
        
        plt.tight_layout()
        plt.savefig('customer_charts.png', dpi=300, bbox_inches='tight')
        print("📊 Customer charts saved as 'customer_charts.png'")
        plt.show()
        
        return fig

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
        self.data = historical_data
        self.features = None
        self.model = None
    
    def prepare_features(self):
        """Create features for machine learning with Copilot assistance"""
        # Create features for machine learning
        # Time-based features (day, month, season)
        # Product features (category, price, popularity)
        # Customer features (segment, history)
        
        if self.data is None:
            print("❌ No data available")
            return None
        
        # Convert date to datetime
        self.data['order_date'] = pd.to_datetime(self.data['order_date'])
        
        # Time-based features
        self.data['year'] = self.data['order_date'].dt.year
        self.data['month'] = self.data['order_date'].dt.month
        self.data['day'] = self.data['order_date'].dt.day
        self.data['weekday'] = self.data['order_date'].dt.weekday
        self.data['quarter'] = self.data['order_date'].dt.quarter
        
        # Seasonal features
        self.data['is_weekend'] = self.data['weekday'].isin([5, 6])
        self.data['is_holiday_season'] = self.data['month'].isin([11, 12])
        
        print("✅ Features prepared for machine learning")
        return self.data
    
    def train_model(self):
        """Train multiple ML models with Copilot assistance"""
        # Train multiple ML models
        # Linear regression, random forest, neural networks
        # Cross-validation and hyperparameter tuning
        print("🤖 ML model training would be implemented here")
        print("💡 Use libraries like scikit-learn, xgboost, or tensorflow")
        pass
    
    def predict_sales(self, forecast_period=30):
        """Generate sales predictions with Copilot assistance"""
        # Generate sales predictions
        # Include confidence intervals
        # Scenario analysis (optimistic, realistic, pessimistic)
        print(f"📈 Sales prediction for {forecast_period} days would be implemented here")
        print("💡 This would return forecasted sales with confidence intervals")
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
    
    # Perform analysis
    print("\n📊 Performing Analysis...")
    metrics = analyzer.calculate_metrics()
    
    print("\n👥 Customer Segmentation...")
    rfm = analyzer.customer_segmentation()
    
    print("\n🛍️ Product Analysis...")
    product_analysis = analyzer.product_analysis()
    
    print("\n📈 Time Series Analysis...")
    monthly_sales, daily_sales = analyzer.time_series_analysis()
    
    # Create visualizations
    print("\n📊 Creating Visualizations...")
    visualizer = DataVisualizer(analyzer)
    
    try:
        dashboard = visualizer.create_dashboard()
        revenue_charts = visualizer.revenue_charts()
        customer_charts = visualizer.customer_charts()
    except Exception as e:
        print(f"⚠️ Visualization error: {e}")
        print("💡 This might be due to display settings. Charts are saved as PNG files.")
    
    print("\n✨ Analysis completed! Check the generated PNG files for visualizations.")
    print("💡 Use Copilot to enhance and extend the analysis methods above.")
