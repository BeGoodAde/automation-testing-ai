"""
Deployment script for driving simulator analytics application
Supports local, Docker, and cloud deployments
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse

class DeploymentManager:
    """Handles different deployment strategies"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def log(self, message, level="INFO"):
        """Log with colors"""
        colors = {"INFO": "\033[36m", "SUCCESS": "\033[32m", "ERROR": "\033[31m"}
        reset = "\033[0m"
        print(f"{colors.get(level, '')}{level}: {message}{reset}")
    
    def run_command(self, command, description):
        """Run command with error handling"""
        try:
            self.log(f"Running: {description}")
            result = subprocess.run(command, shell=True, check=True, cwd=self.project_root)
            self.log(f"✅ {description} completed", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"❌ {description} failed: {e}", "ERROR")
            return False
    
    def deploy_local(self):
        """Deploy locally for development"""
        self.log("🚀 Starting local deployment...")
        
        commands = [
            ("python scripts/dev_setup.py", "Setting up development environment"),
            ("npm run db:create", "Creating database"),
            ("npm run db:setup", "Setting up database schema"),
            ("python src/database/python_integration/simulator_db.py", "Generating sample data")
        ]
        
        for command, description in commands:
            if not self.run_command(command, description):
                return False
        
        self.log("✅ Local deployment completed!", "SUCCESS")
        self.log("🌐 Access your application at: http://localhost:5000", "INFO")
        
        # Start the application
        os.system("python src/dashboard/app.py")
        
    def deploy_docker(self):
        """Deploy using Docker"""
        self.log("🐳 Starting Docker deployment...")
        
        commands = [
            ("docker-compose down", "Stopping existing containers"),
            ("docker-compose build", "Building application image"),
            ("docker-compose up -d", "Starting services")
        ]
        
        for command, description in commands:
            if not self.run_command(command, description):
                return False
        
        self.log("✅ Docker deployment completed!", "SUCCESS")
        self.log("🌐 Access your application at: http://localhost:80", "INFO")
        self.log("📊 PostgreSQL available at: localhost:5432", "INFO")
        
    def deploy_production(self):
        """Deploy to production"""
        self.log("🏭 Starting production deployment...")
        
        # Create production environment file
        env_content = """
DB_HOST=postgres
DB_NAME=driving_sim
DB_USER=postgres
DB_PASSWORD=secure_production_password
FLASK_ENV=production
SECRET_KEY=generate-secure-secret-key-here
"""
        
        with open(self.project_root / '.env.prod', 'w') as f:
            f.write(env_content)
        
        commands = [
            ("docker-compose -f docker-compose.yml -f docker-compose.prod.yml build", "Building production images"),
            ("docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d", "Starting production services")
        ]
        
        for command, description in commands:
            if not self.run_command(command, description):
                return False
        
        self.log("✅ Production deployment completed!", "SUCCESS")
        self.log("🔒 Remember to:", "INFO")
        self.log("  1. Update SECRET_KEY in .env.prod", "INFO")
        self.log("  2. Configure SSL certificates", "INFO")
        self.log("  3. Set up monitoring and backups", "INFO")

def main():
    parser = argparse.ArgumentParser(description='Deploy Driving Simulator Analytics')
    parser.add_argument('mode', choices=['local', 'docker', 'production'], 
                       help='Deployment mode')
    
    args = parser.parse_args()
    
    deployer = DeploymentManager()
    
    if args.mode == 'local':
        deployer.deploy_local()
    elif args.mode == 'docker':
        deployer.deploy_docker()
    elif args.mode == 'production':
        deployer.deploy_production()

if __name__ == "__main__":
    main()