"""
Script to create all required directories for the project
"""

import os
from pathlib import Path

def create_project_directories():
    """Create all required directories for the automation testing project"""
    
    base_path = Path(__file__).parent.parent
    
    directories = [
        'src',
        'src/database',
        'src/database/python_integration',
        'src/database/schema',
        'src/database/migrations',
        'src/database/seeds',
        'src/simulator',
        'src/simulator/models',
        'src/simulator/analytics',
        'tests',
        'tests/database',
        'tests/simulator',
        'scripts',
        'docs',
        'data',
        'data/raw',
        'data/processed',
        'data/output'
    ]
    
    print("🏗️ Creating project directory structure...")
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Create __init__.py files for Python packages
    python_dirs = [
        'src',
        'src/database',
        'src/database/python_integration',
        'src/simulator',
        'src/simulator/models',
        'src/simulator/analytics',
        'tests',
        'tests/database',
        'tests/simulator'
    ]
    
    for directory in python_dirs:
        init_file = base_path / directory / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"📝 Created: {directory}/__init__.py")
    
    print("\n✅ Directory structure created successfully!")

if __name__ == "__main__":
    create_project_directories()