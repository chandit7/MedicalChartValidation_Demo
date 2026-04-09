# 🚀 Setup and Run Guide - MCP Demo

## ⚠️ Prerequisites Check

You're seeing the error because Streamlit isn't installed or not in your PATH. Let's fix that!

---

## 📋 Step-by-Step Setup

### Step 1: Check Python Installation

```powershell
# Check Python version (need 3.7+)
python --version
```

**Expected output:** `Python 3.x.x` (where x >= 7)

If not installed, download from: https://www.python.org/downloads/

---

### Step 2: Navigate to Project Directory

```powershell
# Navigate to the medchart_demo folder
cd c:\Ramesh_Learning\Agentic_AI_Demo_Challenge\medchart_demo
```

---

### Step 3: Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**You should see `(venv)` in your prompt**

---

### Step 4: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**This installs:**
- streamlit (for the web UI)
- pandas (for data handling)
- groq (for LLM)
- pdfplumber (for PDF processing)
- python-dotenv (for environment variables)
- mcp (for Model Context Protocol)

---

### Step 5: Verify Installation

```powershell
# Check if streamlit is installed
streamlit --version

# Check if other packages are installed
python -c "import streamlit, pandas, groq; print('✅ All packages installed')"
```

**Expected output:**
```
Streamlit, version 1.x.x
✅ All packages installed
```

---

## 🎯 Running the Application

### Option 1: Run Original App (No MCP in UI)

```powershell
# Make sure you're in medchart_demo directory
cd c:\Ramesh_Learning\Agentic_AI_Demo_Challenge\medchart_demo

# Run the app
streamlit run app.py
```

**What you'll see:**
- Browser opens automatically
- Tab 4 shows AI Insights
- NO MCP indicators (Phase 1 - backend only)

---

### Option 2: Run MCP-Enhanced App (MCP in UI)

```powershell
# Make sure you're in medchart_demo directory
cd c:\Ramesh_Learning\Agentic_AI_Demo_Challenge\medchart_demo

# Run the enhanced app
streamlit run app_with_mcp.py
```

**What you'll see:**
- Browser opens automatically
- Tab 4 shows AI Insights
- MCP toggle in sidebar
- MCP status indicators
- Data access transparency

---

### Option 3: Test MCP Backend (No UI)

```powershell
# Test MCP integration without UI
python test_mcp_integration.py
```

**What you'll see:**
```
============================================================
MCP INTEGRATION TEST SUITE
============================================================

TEST 1: Database Setup ✅
TEST 2: MCP Server Resources ✅
TEST 3: MCP Resource Read ✅
TEST 4: MCP Tools ✅
TEST 5: MCP vs Direct ✅
TEST 6: LLM Service MCP ✅

Total: 6/6 tests passed
🎉 All tests passed!
```

---

## 🐛 Troubleshooting

### Error: "streamlit: command not found"

**Solution:**
```powershell
# Install streamlit explicitly
pip install streamlit

# Verify
streamlit --version
```

---

### Error: "No module named 'streamlit'"

**Solution:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

---

### Error: "Execution policy error" (Windows)

**Solution:**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate venv again
.\venv\Scripts\Activate.ps1
```

---

### Error: "No validation results in database"

**Solution:**
```powershell
# Run the app first
streamlit run app.py

# In the browser:
# 1. Go to Tab 1: Validate
# 2. Select "Use sample data"
# 3. Choose chart_MBR001.txt
# 4. Click "Run Validation"
# 5. Repeat for MBR002-MBR005
```

---

### Error: "GROQ_API_KEY not found"

**Solution:**
```powershell
# Create .env file
echo GROQ_API_KEY=your_key_here > .env

# Get free API key from: https://console.groq.com
```

---

## 📊 Quick Comparison

### To See Current App (No MCP in UI):
```powershell
streamlit run app.py
```
→ Tab 4 looks normal, works as before

### To See MCP-Enhanced App:
```powershell
streamlit run app_with_mcp.py
```
→ Tab 4 shows MCP toggle and indicators

### To Test MCP Backend:
```powershell
python test_mcp_integration.py
```
→ Runs automated tests, no UI needed

---

## ✅ Verification Checklist

Before running, make sure:

- [ ] Python 3.7+ installed
- [ ] In correct directory (`medchart_demo`)
- [ ] Virtual environment activated (optional but recommended)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Streamlit command works (`streamlit --version`)
- [ ] Database has data (run validations first)
- [ ] GROQ_API_KEY in .env file (for AI features)

---

## 🎯 What to Expect

### First Time Running:

1. **Install takes ~2-3 minutes**
   ```powershell
   pip install -r requirements.txt
   ```

2. **App starts in ~5-10 seconds**
   ```powershell
   streamlit run app.py
   ```

3. **Browser opens automatically**
   - URL: http://localhost:8501
   - If not, manually open the URL shown in terminal

4. **Generate test data**
   - Go to Tab 1
   - Validate 5 sample charts
   - This populates the database

5. **Test AI features**
   - Go to Tab 4
   - Try trend analysis
   - Ask natural language questions

---

## 🔄 Complete Setup Flow

```powershell
# 1. Navigate to directory
cd c:\Ramesh_Learning\Agentic_AI_Demo_Challenge\medchart_demo

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
streamlit --version

# 5. Run the app
streamlit run app.py

# 6. Open browser to http://localhost:8501

# 7. Generate test data (Tab 1)
# 8. Test AI features (Tab 4)
```

---

## 📞 Still Having Issues?

### Check These:

1. **Python version**
   ```powershell
   python --version  # Should be 3.7+
   ```

2. **Pip version**
   ```powershell
   pip --version  # Should be recent
   ```

3. **Current directory**
   ```powershell
   pwd  # Should be in medchart_demo
   ```

4. **Virtual environment**
   ```powershell
   # Should see (venv) in prompt
   ```

5. **Installed packages**
   ```powershell
   pip list | findstr streamlit
   ```

---

## 🎓 Summary

**To run the current app (no MCP in UI):**
```powershell
cd medchart_demo
pip install -r requirements.txt
streamlit run app.py
```

**To run the MCP-enhanced app:**
```powershell
cd medchart_demo
pip install -r requirements.txt
streamlit run app_with_mcp.py
```

**To test MCP backend:**
```powershell
cd medchart_demo
pip install -r requirements.txt
python test_mcp_integration.py
```

---

**Setup Time**: ~5 minutes
**First Run**: ~10 seconds
**Subsequent Runs**: ~5 seconds

Made with Bob 🤖