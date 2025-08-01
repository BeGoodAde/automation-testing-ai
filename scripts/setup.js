/**
 * Cross-platform setup script for PostgreSQL Integration
 * Works on Windows, macOS, and Linux
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class SetupManager {
    constructor() {
        this.isWindows = process.platform === 'win32';
        this.projectRoot = path.resolve(__dirname, '..');
    }

    log(message, type = 'info') {
        const colors = {
            info: '\x1b[36m',    // Cyan
            success: '\x1b[32m', // Green
            warning: '\x1b[33m', // Yellow
            error: '\x1b[31m',   // Red
            reset: '\x1b[0m'     // Reset
        };

        console.log(`${colors[type]}${message}${colors.reset}`);
    }

    async runCommand(command, description) {
        try {
            this.log(`📦 ${description}...`, 'info');
            const result = execSync(command, { 
                stdio: 'inherit', 
                cwd: this.projectRoot 
            });
            this.log(`✅ ${description} completed!`, 'success');
            return result;
        } catch (error) {
            this.log(`❌ Error during ${description}: ${error.message}`, 'error');
            throw error;
        }
    }

    async checkPrerequisites() {
        this.log('🔍 Checking prerequisites...', 'info');

        try {
            // Check Node.js
            execSync('node --version', { stdio: 'ignore' });
            this.log('✅ Node.js is installed', 'success');
        } catch {
            this.log('❌ Node.js is not installed. Please install Node.js first.', 'error');
            process.exit(1);
        }

        try {
            // Check Python
            execSync('python --version', { stdio: 'ignore' });
            this.log('✅ Python is installed', 'success');
        } catch {
            this.log('❌ Python is not installed. Please install Python first.', 'error');
            process.exit(1);
        }

        try {
            // Check PostgreSQL
            execSync('psql --version', { stdio: 'ignore' });
            this.log('✅ PostgreSQL is installed', 'success');
        } catch {
            this.log('❌ PostgreSQL is not installed. Please install PostgreSQL first.', 'error');
            this.log('Download from: https://www.postgresql.org/download/', 'warning');
            process.exit(1);
        }
    }

    async installDependencies() {
        this.log('📦 Installing dependencies...', 'info');

        // Install Node.js dependencies
        await this.runCommand('npm install', 'Installing Node.js packages');

        // Install Python dependencies
        await this.runCommand('pip install -r requirements.txt', 'Installing Python packages');
    }

    async setupDatabase() {
        this.log('🗄️ Setting up PostgreSQL database...', 'info');

        try {
            // Create database
            await this.runCommand(
                'psql -U postgres -c "CREATE DATABASE driving_sim;"',
                'Creating database'
            );
        } catch (error) {
            this.log('⚠️ Database might already exist, continuing...', 'warning');
        }

        // Check if schema file exists
        const schemaPath = path.join(this.projectRoot, 'src', 'database', 'schema', 'driving_simulator.sql');
        if (fs.existsSync(schemaPath)) {
            await this.runCommand(
                `psql -U postgres -d driving_sim -f "${schemaPath}"`,
                'Creating database schema'
            );
        } else {
            this.log('⚠️ Schema file not found, skipping schema creation', 'warning');
        }
    }

    async generateSampleData() {
        this.log('🎲 Generating sample data...', 'info');

        const pythonScript = path.join(this.projectRoot, 'src', 'database', 'python_integration', 'simulator_db.py');
        if (fs.existsSync(pythonScript)) {
            await this.runCommand(
                `python "${pythonScript}"`,
                'Generating sample data'
            );
        } else {
            this.log('⚠️ Python script not found, skipping data generation', 'warning');
        }
    }

    async createEnvironmentFile() {
        this.log('⚙️ Creating environment configuration...', 'info');

        const envPath = path.join(this.projectRoot, '.env');
        const envExamplePath = path.join(this.projectRoot, '.env.example');

        if (!fs.existsSync(envPath) && fs.existsSync(envExamplePath)) {
            fs.copyFileSync(envExamplePath, envPath);
            this.log('✅ Created .env file from template', 'success');
            this.log('📝 Please update .env with your database credentials', 'warning');
        }
    }

    async run() {
        try {
            this.log('🚀 Starting PostgreSQL Integration Setup', 'info');
            this.log('=' .repeat(50), 'info');

            await this.checkPrerequisites();
            await this.installDependencies();
            await this.createEnvironmentFile();
            await this.setupDatabase();
            await this.generateSampleData();

            this.log('', 'info');
            this.log('✅ Setup completed successfully!', 'success');
            this.log('', 'info');
            this.log('🎯 Next steps:', 'info');
            this.log('   1. Update .env file with your database credentials', 'info');
            this.log('   2. Run "npm run simulator:analyze" to perform analysis', 'info');
            this.log('   3. Check the generated Excel report', 'info');
            this.log('   4. View the reaction time analysis plots', 'info');

        } catch (error) {
            this.log('❌ Setup failed. Please check the errors above.', 'error');
            process.exit(1);
        }
    }
}

// Run setup if called directly
if (require.main === module) {
    const setup = new SetupManager();
    setup.run();
}

module.exports = SetupManager;