# Troubleshooting Guide - Medical Chart Validation

## Virtual Environment Issues

### Issue: Python 3.13 venv creation fails or hangs

**Symptoms**:
```
python -m venv venv
# Hangs or shows KeyboardInterrupt error
```

**Root Cause**: Python 3.13 is newer than our tested versions (3.8-3.12). The venv module may have issues with pip installation.

**Solutions** (try in order):

### Solution 1: Create venv without pip, then install pip manually

```bash
# Create venv without pip
python -m venv venv --without-pip

# Activate the environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Download and install pip manually
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# Now install requirements
pip install -r requirements.txt
```

### Solution 2: Skip virtual environment (simplest for demo)

```bash
# Install packages globally (or in user space)
pip install --user streamlit>=1.28.0 pdfplumber>=0.10.0 pandas>=2.0.0

# Continue with implementation
cd medchart_demo
python -c "import db; db.init_db()"
streamlit run app.py
```

### Solution 3: Use Python 3.11 or 3.12 if available

```bash
# Check if you have Python 3.11 or 3.12
py -3.11 --version
# or
py -3.12 --version

# If available, use that version
py -3.11 -m venv venv
# or
py -3.12 -m venv venv

# Then activate and continue
venv\Scripts\activate
pip install -r requirements.txt
```

### Solution 4: Use conda instead of venv

```bash
# If you have Anaconda/Miniconda installed
conda create -n medchart python=3.11
conda activate medchart
pip install -r requirements.txt
```

---

## Recommended Approach for Your Situation

Since you have Python 3.13, I recommend **Solution 2** (skip virtual environment) for the demo:

```bash
# 1. Navigate to project directory
cd C:\Ramesh_Learning\Agentic_AI_Demo_Challenge

# 2. Create project folder
mkdir medchart_demo
cd medchart_demo

# 3. Install dependencies globally (safe for demo)
pip install streamlit pdfplumber pandas

# 4. Create the files (db.py, agents.py, app.py, etc.)
# Follow IMPLEMENTATION_GUIDE.md

# 5. Initialize database
python -c "import db; db.init_db()"

# 6. Run the app
streamlit run app.py
```

**Why this works**:
- No virtual environment needed for a demo
- Packages install in user space (won't affect system Python)
- Faster setup (no venv creation time)
- Works with any Python version 3.8+

---

## Python 3.13 Compatibility

**Good News**: All our dependencies support Python 3.13:
- ✅ Streamlit 1.28+ (supports 3.8-3.13)
- ✅ pdfplumber 0.10+ (supports 3.8-3.13)
- ✅ pandas 2.0+ (supports 3.9-3.13)
- ✅ sqlite3 (built-in, all versions)

**The Issue**: Only the venv creation process has a bug in Python 3.13, not the packages themselves.

---

## Alternative: Quick Test Without Installation

If you want to test if packages work before installing:

```bash
# Test if packages are already installed
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import pdfplumber; print('pdfplumber:', pdfplumber.__version__)"
python -c "import pandas; print('pandas:', pandas.__version__)"

# If any fail, install just that package
pip install streamlit
pip install pdfplumber
pip install pandas
```

---

## Common Installation Errors

### Error: "pip is not recognized"

**Solution**:
```bash
# Use python -m pip instead
python -m pip install streamlit pdfplumber pandas
```

### Error: "Permission denied"

**Solution**:
```bash
# Install in user space
pip install --user streamlit pdfplumber pandas
```

### Error: "Could not find a version that satisfies the requirement"

**Solution**:
```bash
# Update pip first
python -m pip install --upgrade pip

# Then install packages
pip install streamlit pdfplumber pandas
```

---

## Verification Steps

After installation, verify everything works:

```bash
# 1. Check Python version
python --version
# Should show: Python 3.13.x (or 3.11, 3.12)

# 2. Check installed packages
pip list | findstr "streamlit pdfplumber pandas"
# Should show all three packages

# 3. Test imports
python -c "import streamlit, pdfplumber, pandas; print('All packages OK')"
# Should print: All packages OK

# 4. Test Streamlit
streamlit hello
# Should open browser with Streamlit demo
```

---

## Next Steps After Fixing venv Issue

Once packages are installed (with or without venv):

1. **Create project structure**:
```bash
cd C:\Ramesh_Learning\Agentic_AI_Demo_Challenge\medchart_demo
mkdir sample_data
```

2. **Create files** (follow IMPLEMENTATION_GUIDE.md):
   - db.py
   - agents.py
   - app.py
   - requirements.txt
   - sample_data/gap_report.csv
   - sample_data/chart_MBR001.txt
   - sample_data/chart_MBR002.txt
   - sample_data/chart_MBR003.txt

3. **Initialize database**:
```bash
python -c "import db; db.init_db()"
```

4. **Run the app**:
```bash
streamlit run app.py
```

---

## Summary: Fastest Path Forward

```bash
# Skip venv, install globally
cd C:\Ramesh_Learning\Agentic_AI_Demo_Challenge
mkdir medchart_demo
cd medchart_demo
mkdir sample_data

# Install packages
pip install streamlit pdfplumber pandas

# Create all files from IMPLEMENTATION_GUIDE.md
# (db.py, agents.py, app.py, sample data files)

# Initialize and run
python -c "import db; db.init_db()"
streamlit run app.py
```

**Time to working demo**: ~30 minutes (without venv issues)

---

## Need More Help?

If you encounter other errors:

1. Share the exact error message
2. Share your Python version: `python --version`
3. Share your pip version: `pip --version`
4. Share installed packages: `pip list`

I'll help you resolve it!