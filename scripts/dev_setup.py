"""
Complete development environment setup script
Handles all dependencies, configurations, and initial setup
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

class DevelopmentSetup:
    """Complete development environment setup"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        
    def log(self, message, level="INFO"):
        """Log messages with color coding"""
        colors = {
            "INFO": "\033[36m",    # Cyan
            "SUCCESS": "\033[32m", # Green
            "WARNING": "\033[33m", # Yellow
            "ERROR": "\033[31m"    # Red
        }
        reset = "\033[0m"
        print(f"{colors.get(level, '')}{level}: {message}{reset}")
    
    def run_command(self, command, description, required=True):
        """Run shell command with error handling"""
        try:
            self.log(f"Running: {description}")
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            self.log(f"✅ {description} completed", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ {description} failed: {e.stderr}"
            self.log(error_msg, "ERROR")
            if required:
                self.errors.append(error_msg)
            return False
    
    def check_prerequisites(self):
        """Check if required tools are installed"""
        self.log("🔍 Checking prerequisites...")
        
        prerequisites = [
            ("python --version", "Python"),
            ("node --version", "Node.js"),
            ("npm --version", "npm"),
            ("psql --version", "PostgreSQL")
        ]
        
        for command, name in prerequisites:
            if not self.run_command(command, f"Checking {name}", required=False):
                self.log(f"⚠️ {name} not found. Please install {name} first.", "WARNING")
                return False
        
        return True
    
    def create_directories(self):
        """Create all required project directories"""
        self.log("📁 Creating project directories...")
        
        directories = [
            'src/database/python_integration',
            'src/database/schema',
            'src/database/migrations',
            'src/database/seeds',
            'src/simulator/models',
            'src/simulator/analytics',
            'src/dashboard',
            'tests/database',
            'tests/simulator',
            'tests/integration',
            'tests/unit',
            'tests/performance',
            'scripts',
            'docs',
            'data/raw',
            'data/processed',
            'data/output',
            'logs',
            'config'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python packages
            if 'src/' in directory or 'tests/' in directory:
                init_file = dir_path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
        
        self.log("✅ Directories created successfully", "SUCCESS")
    
    def install_python_dependencies(self):
        """Install Python dependencies with error handling"""
        self.log("🐍 Installing Python dependencies...")
        
        # Upgrade pip first
        self.run_command(
            "python -m pip install --upgrade pip",
            "Upgrading pip"
        )
        
        # Install requirements
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            return self.run_command(
                f"pip install -r {requirements_file}",
                "Installing Python packages"
            )
        else:
            self.log("⚠️ requirements.txt not found", "WARNING")
            return False
    
    def install_node_dependencies(self):
        """Install Node.js dependencies"""
        self.log("📦 Installing Node.js dependencies...")
        
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            return self.run_command("npm install", "Installing Node.js packages")
        else:
            self.log("⚠️ package.json not found", "WARNING")
            return False
    
    def setup_database(self):
        """Set up PostgreSQL database"""
        self.log("🗄️ Setting up PostgreSQL database...")
        
        # Create database
        self.run_command(
            'psql -U postgres -c "CREATE DATABASE driving_sim;"',
            "Creating database",
            required=False  # Database might already exist
        )
        
        # Set up schema
        schema_file = self.project_root / 'src/database/schema/driving_simulator.sql'
        if schema_file.exists():
            return self.run_command(
                f'psql -U postgres -d driving_sim -f "{schema_file}"',
                "Creating database schema"
            )
        else:
            self.log("⚠️ Database schema file not found", "WARNING")
            return False
    
    def setup_environment(self):
        """Set up environment configuration"""
        self.log("⚙️ Setting up environment configuration...")
        
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if env_example.exists() and not env_file.exists():
            shutil.copy(env_example, env_file)
            self.log("✅ Created .env file from template", "SUCCESS")
            self.log("📝 Please update .env with your database credentials", "WARNING")
        
        # Create additional config files
        configs = {
            'pytest.ini': '''[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --cov=src --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    database: Database tests
    slow: Slow running tests''',
            
            '.gitignore': '''# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
venv/
env/

# Database
*.db
*.sqlite

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Coverage
coverage/
htmlcov/
.coverage

# Build
dist/
build/
*.egg-info/

# OS
.DS_Store
Thumbs.db

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep'''
        }
        
        for filename, content in configs.items():
            file_path = self.project_root / filename
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    f.write(content)
                self.log(f"✅ Created {filename}", "SUCCESS")
    
    def setup_pre_commit_hooks(self):
        """Set up pre-commit hooks for code quality"""
        self.log("🔧 Setting up pre-commit hooks...")
        
        pre_commit_config = self.project_root / '.pre-commit-config.yaml'
        if not pre_commit_config.exists():
            config_content = '''repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.49.0
    hooks:
      - id: eslint
        files: \\.(js|jsx)$
        types: [file]'''
            
            with open(pre_commit_config, 'w') as f:
                f.write(config_content)
        
        # Install pre-commit hooks
        self.run_command("pre-commit install", "Installing pre-commit hooks", required=False)
    
    def run_initial_tests(self):
        """Run initial tests to verify setup"""
        self.log("🧪 Running initial tests...")
        
        # Run JavaScript tests
        self.run_command("npm test", "Running JavaScript tests", required=False)
        
        # Run Python tests
        self.run_command("python -m pytest tests/ -v", "Running Python tests", required=False)
    
    def generate_sample_data(self):
        """Generate initial sample data"""
        self.log("🎲 Generating sample data...")
        
        simulator_script = self.project_root / 'src/database/python_integration/simulator_db.py'
        if simulator_script.exists():
            self.run_command(
                "python src/database/python_integration/simulator_db.py",
                "Generating sample data",
                required=False
            )
    
    def run_setup(self):
        """Run complete setup process"""
        self.log("🚀 Starting complete development environment setup", "INFO")
        self.log("=" * 60, "INFO")
        
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Directories", self.create_directories),
            ("Environment", self.setup_environment),
            ("Python Dependencies", self.install_python_dependencies),
            ("Node.js Dependencies", self.install_node_dependencies),
            ("Database Setup", self.setup_database),
            ("Pre-commit Hooks", self.setup_pre_commit_hooks),
            ("Sample Data", self.generate_sample_data),
            ("Initial Tests", self.run_initial_tests)
        ]
        
        completed_steps = 0
        total_steps = len(steps)
        
        for step_name, step_function in steps:
            try:
                if step_function():
                    completed_steps += 1
                self.log(f"Progress: {completed_steps}/{total_steps} steps completed", "INFO")
            except Exception as e:
                self.log(f"❌ Error in {step_name}: {str(e)}", "ERROR")
                self.errors.append(f"{step_name}: {str(e)}")
        
        # Final report
        self.log("", "INFO")
        self.log("=" * 60, "INFO")
        if self.errors:
            self.log(f"⚠️ Setup completed with {len(self.errors)} errors:", "WARNING")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        else:
            self.log("✅ Development environment setup completed successfully!", "SUCCESS")
        
        self.log("", "INFO")
        self.log("🎯 Next steps:", "INFO")
        self.log("  1. Update .env file with your database credentials", "INFO")
        self.log("  2. Run 'npm test' to verify JavaScript tests", "INFO")
        self.log("  3. Run 'npm run test:python' to verify Python tests", "INFO")
        self.log("  4. Start developing with 'npm run dev'", "INFO")

if __name__ == "__main__":
    setup = DevelopmentSetup()
    setup.run_setup()