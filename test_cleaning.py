import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import re

class TestDataCleaning:
    """Test suite for data cleaning operations."""
    
    @pytest.fixture
    def sample_dirty_data(self):
        """Create sample dirty data for testing."""
        return pd.DataFrame({
            'id': [1, 2, 3, None, 5, 6],
            'name': ['John', 'Jane', '', 'Bob', None, 'Alice'],
            'email': ['john@test.com', 'jane@invalid', 'bob@test.com', '', 'alice@test.com', None],
            'age': [25, -5, 150, 30, None, 35],
            'salary': [50000, 0, 999999, None, 75000, 60000],
            'date_joined': ['2020-01-01', '2021-13-45', '2022-02-15', None, '2023-01-01', 'invalid_date']
        })
    
    @pytest.fixture
    def sample_clean_data(self):
        """Create sample clean data for comparison."""
        return pd.DataFrame({
            'id': [1, 2, 3, 5, 6],
            'name': ['John', 'Jane', 'Bob', 'Alice'],
            'email': ['john@test.com', 'bob@test.com', 'alice@test.com'],
            'age': [25, 30, 35],
            'salary': [50000, 75000, 60000],
            'date_joined': ['2020-01-01', '2022-02-15', '2023-01-01']
        })
    
    @pytest.fixture
    def temp_csv_file(self, sample_dirty_data):
        """Create temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_dirty_data.to_csv(f.name, index=False)
            yield f.name
        os.unlink(f.name)

    @pytest.mark.unit
    def test_remove_null_values(self, sample_dirty_data):
        """Test removal of null values from DataFrame."""
        def remove_nulls(df):
            return df.dropna()
        
        result = remove_nulls(sample_dirty_data)
        assert len(result) < len(sample_dirty_data)
        assert not result.isnull().any().any()
        # Verify specific rows are removed
        assert len(result) == 2  # Only rows with complete data
    
    @pytest.mark.unit
    def test_remove_empty_strings(self, sample_dirty_data):
        """Test removal of empty strings from DataFrame."""
        def remove_empty_strings(df):
            # Replace empty strings with NaN and then drop them
            df_clean = df.replace('', np.nan)
            return df_clean.dropna()
        
        result = remove_empty_strings(sample_dirty_data)
        # Check that empty strings are removed
        for col in result.select_dtypes(include=['object']).columns:
            assert not (result[col] == '').any()
    
    @pytest.mark.unit
    def test_validate_email_format(self, sample_dirty_data):
        """Test email format validation."""
        def validate_email(email):
            if pd.isna(email) or email == '':
                return False
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        
        def clean_emails(df):
            df = df.copy()
            df['email_valid'] = df['email'].apply(validate_email)
            return df[df['email_valid']].drop('email_valid', axis=1)
        
        result = clean_emails(sample_dirty_data)
        # Only valid emails should remain
        valid_emails = ['john@test.com', 'bob@test.com', 'alice@test.com']
        assert set(result['email'].dropna()) == set(valid_emails)
    
    @pytest.mark.unit
    def test_validate_age_range(self, sample_dirty_data):
        """Test age validation within reasonable range."""
        def validate_age(df):
            df = df.copy()
            # Keep ages between 0 and 120
            df['age'] = df['age'].apply(lambda x: x if pd.notna(x) and 0 <= x <= 120 else np.nan)
            return df.dropna(subset=['age'])
        
        result = validate_age(sample_dirty_data)
        # Check that invalid ages are removed
        assert all(0 <= age <= 120 for age in result['age'] if pd.notna(age))
        assert -5 not in result['age'].values
        assert 150 not in result['age'].values
    
    @pytest.mark.unit
    def test_validate_salary_range(self, sample_dirty_data):
        """Test salary validation within reasonable range."""
        def validate_salary(df):
            df = df.copy()
            # Keep salaries between 10,000 and 500,000
            df['salary'] = df['salary'].apply(
                lambda x: x if pd.notna(x) and 10000 <= x <= 500000 else np.nan
            )
            return df.dropna(subset=['salary'])
        
        result = validate_salary(sample_dirty_data)
        # Check that invalid salaries are removed
        assert all(10000 <= salary <= 500000 for salary in result['salary'] if pd.notna(salary))
        assert 0 not in result['salary'].values
        assert 999999 not in result['salary'].values
    
    @pytest.mark.unit
    def test_validate_date_format(self, sample_dirty_data):
        """Test date format validation."""
        def validate_dates(df):
            df = df.copy()
            df['date_joined'] = pd.to_datetime(df['date_joined'], errors='coerce')
            return df.dropna(subset=['date_joined'])
        
        result = validate_dates(sample_dirty_data)
        # Check that invalid dates are removed
        assert len(result) < len(sample_dirty_data)
        assert all(pd.notna(date) for date in result['date_joined'])
    
    @pytest.mark.integration
    def test_complete_data_cleaning_pipeline(self, sample_dirty_data):
        """Test complete data cleaning pipeline."""
        def clean_data_pipeline(df):
            # Step 1: Remove nulls and empty strings
            df = df.replace('', np.nan)
            
            # Step 2: Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            df['email'] = df['email'].apply(
                lambda x: x if pd.notna(x) and re.match(email_pattern, x) else np.nan
            )
            
            # Step 3: Validate age range
            df['age'] = df['age'].apply(
                lambda x: x if pd.notna(x) and 0 <= x <= 120 else np.nan
            )
            
            # Step 4: Validate salary range
            df['salary'] = df['salary'].apply(
                lambda x: x if pd.notna(x) and 10000 <= x <= 500000 else np.nan
            )
            
            # Step 5: Validate dates
            df['date_joined'] = pd.to_datetime(df['date_joined'], errors='coerce')
            
            # Step 6: Remove rows with critical missing data
            df = df.dropna(subset=['id', 'name'])
            
            return df
        
        result = clean_data_pipeline(sample_dirty_data)
        
        # Verify the cleaning worked
        assert len(result) > 0
        assert not result['id'].isnull().any()
        assert not result['name'].isnull().any()
        
        # Check data quality improvements
        assert len(result) <= len(sample_dirty_data)
    
    @pytest.mark.unit
    def test_data_type_conversion(self, sample_dirty_data):
        """Test proper data type conversion."""
        def convert_data_types(df):
            df = df.copy()
            # Convert id to integer (removing nulls first)
            df = df.dropna(subset=['id'])
            df['id'] = df['id'].astype(int)
            
            # Convert date strings to datetime
            df['date_joined'] = pd.to_datetime(df['date_joined'], errors='coerce')
            
            return df
        
        result = convert_data_types(sample_dirty_data)
        
        # Check data types
        assert result['id'].dtype == 'int64'
        assert pd.api.types.is_datetime64_any_dtype(result['date_joined'])
    
    @pytest.mark.unit
    def test_duplicate_removal(self):
        """Test removal of duplicate records."""
        # Create data with duplicates
        duplicate_data = pd.DataFrame({
            'id': [1, 2, 2, 3, 3, 4],
            'name': ['John', 'Jane', 'Jane', 'Bob', 'Bob', 'Alice'],
            'email': ['john@test.com', 'jane@test.com', 'jane@test.com', 
                     'bob@test.com', 'bob@test.com', 'alice@test.com']
        })
        
        def remove_duplicates(df):
            return df.drop_duplicates()
        
        result = remove_duplicates(duplicate_data)
        
        # Check duplicates are removed
        assert len(result) == 4  # Should have 4 unique records
        assert not result.duplicated().any()
    
    @pytest.mark.unit
    def test_outlier_detection(self):
        """Test outlier detection and removal."""
        # Create data with outliers
        outlier_data = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 100, 2, 3, 4, 1000]  # 100 and 1000 are outliers
        })
        
        def remove_outliers(df, column, method='iqr'):
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
            return df
        
        result = remove_outliers(outlier_data, 'values')
        
        # Check outliers are removed
        assert len(result) < len(outlier_data)
        assert 100 not in result['values'].values
        assert 1000 not in result['values'].values
    
    @pytest.mark.slow
    def test_large_dataset_cleaning(self):
        """Test cleaning performance on larger dataset."""
        # Create large dataset
        large_data = pd.DataFrame({
            'id': range(10000),
            'value': np.random.randn(10000),
            'category': np.random.choice(['A', 'B', 'C'], 10000)
        })
        
        # Add some null values
        large_data.loc[large_data.sample(frac=0.1).index, 'value'] = np.nan
        
        def clean_large_dataset(df):
            return df.dropna()
        
        import time
        start_time = time.time()
        result = clean_large_dataset(large_data)
        end_time = time.time()
        
        # Check performance and correctness
        assert len(result) < len(large_data)
        assert not result.isnull().any().any()
        assert (end_time - start_time) < 5  # Should complete within 5 seconds
    
    @pytest.mark.database
    def test_data_cleaning_with_file_io(self, temp_csv_file):
        """Test data cleaning with file input/output."""
        def clean_csv_file(input_file, output_file):
            # Read data
            df = pd.read_csv(input_file)
            
            # Clean data
            df_clean = df.dropna().drop_duplicates()
            
            # Write cleaned data
            df_clean.to_csv(output_file, index=False)
            
            return df_clean
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as output_file:
            try:
                result = clean_csv_file(temp_csv_file, output_file.name)
                
                # Verify output file exists and has correct data
                assert os.path.exists(output_file.name)
                
                # Read back and verify
                df_output = pd.read_csv(output_file.name)
                assert len(df_output) == len(result)
                assert not df_output.isnull().any().any()
                
            finally:
                os.unlink(output_file.name)