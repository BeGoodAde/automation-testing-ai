# Makefile for automation testing project by Adelaja Isreal Bolarinwa

.PHONY: help install test clean setup lint format

help:  ## Show this help message
    @echo "🚀 Automation Testing AI - Project Commands"
    @echo "==========================================="
    @grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
    @echo "📦 Installing Node.js dependencies..."
    npm install
    @echo "🐍 Installing Python dependencies..."
    pip install -r requirements.txt
    @echo "✅ All dependencies installed!"

test:  ## Run all tests
    @echo "🧪 Running JavaScript tests..."
    npm test
    @echo "🐍 Running Python tests..."
    pytest tests/python/
    @echo "✅ All tests completed!"

test-js:  ## Run JavaScript tests only
    npm test

test-python:  ## Run Python tests only
    pytest tests/python/ -v

coverage:  ## Generate test coverage reports
    @echo "📊 Generating JavaScript coverage..."
    npm run test:coverage
    @echo "📊 Generating Python coverage..."
    pytest tests/python/ --cov=src/python --cov-report=html
    @echo "✅ Coverage reports generated in reports/test-coverage/"

lint:  ## Run code linting
    @echo "🔍 Linting JavaScript..."
    npx eslint src/javascript/
    @echo "🔍 Linting Python..."
    flake8 src/python/ tests/python/
    @echo "✅ Linting completed!"

format:  ## Format code
    @echo "🎨 Formatting Python code..."
    black src/python/ tests/python/
    isort src/python/ tests/python/
    @echo "✅ Code formatting completed!"

clean:  ## Clean generated files
    @echo "🧹 Cleaning up..."
    rm -rf reports/test-coverage/
    rm -rf __pycache__/
    rm -rf .pytest_cache/
    rm -rf node_modules/.cache/
    @echo "✅ Cleanup completed!"

setup:  ## Initial project setup
    @echo "🏗️ Setting up project..."
    python scripts/reorganize.py
    $(MAKE) install
    @echo "✅ Project setup completed!"

generate-data:  ## Generate sample data
    @echo "📊 Generating sample data..."
    python src/utils/data_generator.py
    @echo "✅ Sample data generated!"

run-analytics:  ## Run data analytics
    @echo "📈 Running data analytics..."
    python src/python/data_analyzer.py
    @echo "✅ Analytics completed!"

docs:  ## Generate documentation
    @echo "📚 Generating documentation..."
    # Add documentation generation commands here
    @echo "✅ Documentation generated!"

all: clean install test coverage lint  ## Run complete CI pipeline