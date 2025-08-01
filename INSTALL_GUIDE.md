# 🛠️ Installation Guide for Driving Simulator Database Project

## 🚨 Quick Fix for Setup Errors

If you encountered the `setuptools.build_meta` error, try these solutions:

### Solution 1: Manual Package Installation

```powershell
# 1. Upgrade pip and setuptools first
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# 2. Install packages individually
python -m pip install psycopg2-binary
python -m pip install pandas
python -m pip install numpy
python -m pip install matplotlib
python -m pip install seaborn
python -m pip install python-dotenv
python -m pip install openpyxl
```

### Solution 2: Create Fresh Virtual Environment

```powershell
# 1. Deactivate current environment
deactivate

# 2. Remove problematic environment
rmdir /s .venv

# 3. Create new virtual environment
python -m venv .venv

# 4. Activate new environment
.venv\Scripts\activate

# 5. Upgrade pip immediately
python -m pip install --upgrade pip setuptools wheel

# 6. Run setup again
python setup.py
```

### Solution 3: Alternative Package Versions

If specific versions fail, try these alternatives:

```powershell
# Alternative package versions
python -m pip install psycopg2-binary==2.9.5
python -m pip install pandas==1.5.3
python -m pip install numpy==1.21.6
python -m pip install matplotlib==3.6.0
python -m pip install seaborn==0.11.2
python -m pip install python-dotenv==0.19.2
python -m pip install openpyxl==3.0.10
```

## 🔧 Environment Setup

### Option A: Using Conda (Recommended)

```powershell
# 1. Install Anaconda or Miniconda
# 2. Create conda environment
conda create -n driving_sim python=3.10
conda activate driving_sim

# 3. Install packages via conda
conda install pandas numpy matplotlib seaborn
conda install -c conda-forge psycopg2 python-dotenv openpyxl
```

### Option B: Using Virtual Environment

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Run enhanced setup
python setup.py
```

## 🐍 Python Version Compatibility

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.11+ | ✅ Recommended | Best compatibility |
| 3.10 | ✅ Excellent | Stable and fast |
| 3.9 | ✅ Good | Well tested |
| 3.8 | ⚠️ Minimum | Some packages may be outdated |
| 3.7 | ❌ Not supported | EOL, upgrade recommended |

## 🚀 Quick Start After Installation

1. **Configure Database**:
   ```powershell
   # Edit .env file with your PostgreSQL credentials
   notepad .env
   ```

2. **Test Installation**:
   ```powershell
   python -c "import pandas, numpy, matplotlib, psycopg2; print('✅ All packages imported successfully!')"
   ```

3. **Run Analysis**:
   ```powershell
   # Windows
   run_analysis.bat
   
   # Or manually
   python src/database/python_integration/simulator_db.py
   ```

## 🔍 Troubleshooting Common Issues

### Issue: `ModuleNotFoundError: No module named 'psycopg2'`
**Solution**: 
```powershell
python -m pip install psycopg2-binary --force-reinstall
```

### Issue: `ImportError: cannot import name 'Iterable' from 'collections'`
**Solution**: Upgrade Python to 3.9+ or downgrade packages

### Issue: Database connection failed
**Solution**: 
1. Ensure PostgreSQL is running
2. Check credentials in `.env` file
3. Test connection: `psql -h localhost -U postgres -d driving_sim`

### Issue: Permission denied on Windows
**Solution**: 
1. Run as Administrator
2. Or use `--user` flag: `python -m pip install --user package_name`

## 📞 Getting Help

If you continue to have issues:

1. **Check Python version**: `python --version`
2. **Check pip version**: `python -m pip --version`
3. **List installed packages**: `python -m pip list`
4. **Clear pip cache**: `python -m pip cache purge`
5. **Reinstall with verbose output**: `python -m pip install -v package_name`

## 🎯 Success Indicators

You know setup is successful when:
- ✅ All packages import without errors
- ✅ `.env` file is created and configured
- ✅ Database connection test passes
- ✅ Sample data generation works
- ✅ Visualizations display correctly

Ready to start analyzing driving simulator data! 🏎️📊