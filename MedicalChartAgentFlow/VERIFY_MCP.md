# 🔍 How to Verify MCP Implementation

This guide provides step-by-step instructions to verify that the MCP implementation is working correctly.

---

## ⚡ Quick Verification (5 minutes)

### Step 1: Check Files Exist

```bash
cd medchart_demo

# Verify all MCP files are present
ls -la mcp_server.py
ls -la llm_service_mcp.py
ls -la test_mcp_integration.py
ls -la MCP_IMPLEMENTATION_GUIDE.md
```

**Expected Output:**
```
-rw-r--r-- 1 user user 5234 Apr 08 11:53 mcp_server.py
-rw-r--r-- 1 user user 9876 Apr 08 11:54 llm_service_mcp.py
-rw-r--r-- 1 user user 8765 Apr 08 11:55 test_mcp_integration.py
-rw-r--r-- 1 user user 12345 Apr 08 11:55 MCP_IMPLEMENTATION_GUIDE.md
```

✅ **Pass**: All files exist
❌ **Fail**: Files missing - check implementation

---

### Step 2: Install Dependencies

```bash
# Install MCP package
pip install mcp

# Verify installation
python -c "import mcp; print('✅ MCP installed:', mcp.__version__)"
```

**Expected Output:**
```
✅ MCP installed: 1.0.0
```

✅ **Pass**: MCP package installed
❌ **Fail**: Run `pip install mcp` again

---

### Step 3: Verify Database Has Data

```bash
# Check if database exists and has data
python -c "
import db
db.init_db()
results = db.get_all_results()
print(f'✅ Database has {len(results)} validation records')
if len(results) == 0:
    print('⚠️  WARNING: No data yet. Run validations in Streamlit app first!')
"
```

**Expected Output:**
```
[OK] Database initialized
✅ Database has 5 validation records
```

✅ **Pass**: Database has data
⚠️ **Warning**: No data - run validations first (see Step 3a below)

#### Step 3a: Generate Test Data (if needed)

```bash
# Run the Streamlit app and validate sample charts
streamlit run app.py

# In the app:
# 1. Go to Tab 1: Validate
# 2. Select "Use sample data"
# 3. Choose chart_MBR001.txt
# 4. Click "Run Validation"
# 5. Repeat for MBR002, MBR003, MBR004, MBR005
```

---

### Step 4: Test MCP Server Directly

```bash
# Test if MCP server can start
python mcp_server.py &
MCP_PID=$!

# Wait a moment
sleep 2

# Check if process is running
ps -p $MCP_PID

# Kill the test server
kill $MCP_PID
```

**Expected Output:**
```
  PID TTY          TIME CMD
 1234 pts/0    00:00:00 python
```

✅ **Pass**: MCP server starts successfully
❌ **Fail**: Check for import errors

---

### Step 5: Run Automated Tests

```bash
# Run the comprehensive test suite
python test_mcp_integration.py
```

**Expected Output:**
```
============================================================
MCP INTEGRATION TEST SUITE
============================================================

============================================================
TEST 1: Database Setup
============================================================
✅ Database accessible
   Total records: 5
   Summary: {'total': 5, 'approved': 3, 'rejected': 1, 'manual_review': 1}

============================================================
TEST 2: MCP Server Resources
============================================================
✅ MCP server connected
   Available resources: 3
   - medchart://results/all: All Validation Results
   - medchart://results/summary: Validation Summary
   - medchart://results/recent: Recent Validations

============================================================
TEST 3: MCP Resource Read
============================================================
✅ Successfully read resource via MCP
   Resource: medchart://results/summary
   Data: {
     "total": 5,
     "approved": 3,
     "rejected": 1,
     "manual_review": 1
   }

============================================================
TEST 4: MCP Tools
============================================================
✅ Available tools: 4
   - query_results_by_decision: Query validation results filtered by decision type
   - query_results_by_member: Query validation results for a specific member
   - get_trend_analysis_data: Get data for trend analysis over specified days
   - get_daily_metrics: Get validation metrics for the last 24 hours

   Testing tool: get_daily_metrics
   Result: {
     "total": 5,
     "approved": 3,
     "rejected": 1,
     "manual_review": 1
   }

============================================================
TEST 5: MCP vs Direct Access Comparison
============================================================
✅ Direct DB access:
   {
     "total": 5,
     "approved": 3,
     "rejected": 1,
     "manual_review": 1
   }

✅ MCP access:
   {
     "total": 5,
     "approved": 3,
     "rejected": 1,
     "manual_review": 1
   }

✅ Results match! MCP provides same data as direct access

============================================================
TEST 6: MCP-Enhanced LLM Service
============================================================
✅ LLM Service initialized with MCP support
   MCP available: True

   Note: Full analysis requires GROQ_API_KEY in .env
   MCP integration is ready for use

============================================================
TEST SUMMARY
============================================================
✅ PASS: Database Setup
✅ PASS: MCP Resources
✅ PASS: MCP Resource Read
✅ PASS: MCP Tools
✅ PASS: MCP vs Direct
✅ PASS: LLM Service MCP

Total: 6/6 tests passed

🎉 All tests passed! MCP integration is working correctly.
```

✅ **Pass**: All 6 tests passed
❌ **Fail**: Check error messages for specific issues

---

## 🔬 Detailed Verification (15 minutes)

### Test 1: Manual MCP Server Test

```bash
# Terminal 1: Start MCP server
cd medchart_demo
python mcp_server.py
```

Keep this running, then in a new terminal:

```bash
# Terminal 2: Test MCP client connection
cd medchart_demo
python -c "
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test():
    params = StdioServerParameters(
        command='python',
        args=['mcp_server.py']
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List resources
            resources = await session.list_resources()
            print('✅ Resources:', len(resources.resources))
            for r in resources.resources:
                print(f'   - {r.uri}')
            
            # Read a resource
            result = await session.read_resource('medchart://results/summary')
            print('✅ Data fetched successfully')

asyncio.run(test())
"
```

**Expected Output:**
```
✅ Resources: 3
   - medchart://results/all
   - medchart://results/summary
   - medchart://results/recent
✅ Data fetched successfully
```

---

### Test 2: Compare MCP vs Direct Access

```bash
python -c "
import asyncio
import json
import db
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Get data directly
direct = db.get_summary()
print('Direct DB:', json.dumps(direct, indent=2))

# Get data via MCP
async def get_via_mcp():
    params = StdioServerParameters(command='python', args=['mcp_server.py'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource('medchart://results/summary')
            return json.loads(result.contents[0].text)

mcp_data = asyncio.run(get_via_mcp())
print('MCP Access:', json.dumps(mcp_data, indent=2))

# Compare
if direct == mcp_data:
    print('✅ MATCH: Both methods return identical data')
else:
    print('❌ MISMATCH: Data differs')
"
```

**Expected Output:**
```
Direct DB: {
  "total": 5,
  "approved": 3,
  "rejected": 1,
  "manual_review": 1
}
MCP Access: {
  "total": 5,
  "approved": 3,
  "rejected": 1,
  "manual_review": 1
}
✅ MATCH: Both methods return identical data
```

---

### Test 3: Test MCP-Enhanced LLM Service

```bash
python -c "
from llm_service_mcp import LLMAnalyticsMCP

# Initialize with MCP
llm = LLMAnalyticsMCP(use_mcp=True)

print('✅ LLM Service initialized')
print(f'   MCP enabled: {llm.use_mcp}')
print(f'   MCP available: {llm.mcp_available}')

# Note: Full test requires GROQ_API_KEY
print('\n💡 To test full functionality:')
print('   1. Add GROQ_API_KEY to .env file')
print('   2. Run: llm.analyze_trends_mcp(days=7)')
"
```

**Expected Output:**
```
✅ MCP client initialized (ready to connect to server)
✅ LLM Service initialized
   MCP enabled: True
   MCP available: True

💡 To test full functionality:
   1. Add GROQ_API_KEY to .env file
   2. Run: llm.analyze_trends_mcp(days=7)
```

---

### Test 4: Test MCP Tools

```bash
python -c "
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_tools():
    params = StdioServerParameters(command='python', args=['mcp_server.py'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f'✅ Available tools: {len(tools.tools)}')
            
            # Call get_daily_metrics tool
            result = await session.call_tool('get_daily_metrics', {})
            data = json.loads(result.content[0].text)
            print(f'✅ Tool result: {json.dumps(data, indent=2)}')

asyncio.run(test_tools())
"
```

**Expected Output:**
```
✅ Available tools: 4
✅ Tool result: {
  "total": 5,
  "approved": 3,
  "rejected": 1,
  "manual_review": 1
}
```

---

## 🐛 Troubleshooting

### Issue 1: "Import mcp could not be resolved"

**Solution:**
```bash
pip install mcp
```

### Issue 2: "No module named 'mcp.server'"

**Solution:**
```bash
# The MCP package might not be available yet
# For now, the implementation is ready but requires the official MCP package
# Check: https://github.com/modelcontextprotocol/python-sdk
```

### Issue 3: "No validation results in database"

**Solution:**
```bash
# Run the Streamlit app and create some validations
streamlit run app.py

# Then validate the 5 sample charts (MBR001-MBR005)
```

### Issue 4: "MCP server won't start"

**Solution:**
```bash
# Check for syntax errors
python -m py_compile mcp_server.py

# Check imports
python -c "import db; print('✅ db module OK')"
```

### Issue 5: "Tests fail with connection error"

**Solution:**
```bash
# Make sure you're in the medchart_demo directory
cd medchart_demo

# Verify mcp_server.py is in current directory
ls -la mcp_server.py

# Run tests again
python test_mcp_integration.py
```

---

## ✅ Verification Checklist

Use this checklist to confirm everything is working:

- [ ] All MCP files exist (mcp_server.py, llm_service_mcp.py, etc.)
- [ ] MCP package installed (`pip install mcp`)
- [ ] Database has validation data (at least 1 record)
- [ ] MCP server starts without errors
- [ ] Test suite passes (6/6 tests)
- [ ] MCP resources can be listed
- [ ] MCP resources can be read
- [ ] MCP tools can be called
- [ ] MCP data matches direct database access
- [ ] LLM service initializes with MCP support

---

## 🎯 Success Criteria

**MCP implementation is verified when:**

1. ✅ All files are present and syntactically correct
2. ✅ MCP package is installed
3. ✅ Database has test data
4. ✅ MCP server can start and respond
5. ✅ All 6 automated tests pass
6. ✅ MCP data matches direct database access
7. ✅ No import or runtime errors

---

## 📊 Expected Test Results Summary

| Test | Expected Result | Pass Criteria |
|------|----------------|---------------|
| Database Setup | 5+ records | ✅ Records exist |
| MCP Resources | 3 resources listed | ✅ All 3 present |
| Resource Read | JSON data returned | ✅ Valid JSON |
| MCP Tools | 4 tools available | ✅ All 4 present |
| MCP vs Direct | Identical data | ✅ Data matches |
| LLM Service | MCP available=True | ✅ Initialized |

---

## 🚀 Next Steps After Verification

Once verification is complete:

1. **Review Documentation**
   - Read `MCP_IMPLEMENTATION_GUIDE.md`
   - Review `MCP_PHASE1_SUMMARY.md`

2. **Experiment with MCP**
   - Try different resource URIs
   - Call different tools
   - Compare performance

3. **Plan Phase 2**
   - UI integration
   - Performance benchmarking
   - Additional features

---

## 📞 Need Help?

If verification fails:

1. Check the **Troubleshooting** section above
2. Review error messages carefully
3. Ensure all prerequisites are met:
   - Python 3.7+
   - All dependencies installed
   - Database has data
   - In correct directory

---

**Verification Time**: ~5-15 minutes
**Difficulty**: Easy
**Prerequisites**: Python 3.7+, pip, basic command line knowledge

Made with Bob 🤖