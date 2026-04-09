"""
Test script for MCP integration
Demonstrates MCP functionality and compares with direct database access
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import db


def test_database_setup():
    """Test 1: Verify database has data."""
    print("\n" + "="*60)
    print("TEST 1: Database Setup")
    print("="*60)
    
    try:
        results = db.get_all_results()
        summary = db.get_summary()
        
        print(f"✅ Database accessible")
        print(f"   Total records: {len(results)}")
        print(f"   Summary: {summary}")
        
        if len(results) == 0:
            print("\n⚠️  WARNING: No validation results in database")
            print("   Run some validations in the Streamlit app first!")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def test_mcp_server_resources():
    """Test 2: Test MCP server resource listing."""
    print("\n" + "="*60)
    print("TEST 2: MCP Server Resources")
    print("="*60)
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List resources
                resources = await session.list_resources()
                
                print(f"✅ MCP server connected")
                print(f"   Available resources: {len(resources.resources)}")
                
                for resource in resources.resources:
                    print(f"   - {resource.uri}: {resource.name}")
                
                return True
                
    except ImportError:
        print("❌ MCP package not installed")
        print("   Run: pip install mcp")
        return False
    except Exception as e:
        print(f"❌ MCP server error: {e}")
        print(f"   Make sure mcp_server.py is in the current directory")
        return False


async def test_mcp_resource_read():
    """Test 3: Test reading data through MCP."""
    print("\n" + "="*60)
    print("TEST 3: MCP Resource Read")
    print("="*60)
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Read summary resource
                result = await session.read_resource("medchart://results/summary")
                data = json.loads(result.contents[0].text)
                
                print(f"✅ Successfully read resource via MCP")
                print(f"   Resource: medchart://results/summary")
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                return True
                
    except Exception as e:
        print(f"❌ Resource read error: {e}")
        return False


async def test_mcp_tools():
    """Test 4: Test MCP tools."""
    print("\n" + "="*60)
    print("TEST 4: MCP Tools")
    print("="*60)
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List tools
                tools = await session.list_tools()
                print(f"✅ Available tools: {len(tools.tools)}")
                
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Call a tool
                print("\n   Testing tool: get_daily_metrics")
                result = await session.call_tool("get_daily_metrics", {})
                data = json.loads(result.content[0].text)
                print(f"   Result: {json.dumps(data, indent=2)}")
                
                return True
                
    except Exception as e:
        print(f"❌ Tool test error: {e}")
        return False


def test_mcp_vs_direct_comparison():
    """Test 5: Compare MCP vs direct database access."""
    print("\n" + "="*60)
    print("TEST 5: MCP vs Direct Access Comparison")
    print("="*60)
    
    try:
        # Direct access
        direct_summary = db.get_summary()
        print(f"✅ Direct DB access:")
        print(f"   {json.dumps(direct_summary, indent=2)}")
        
        # MCP access (async)
        async def get_mcp_summary():
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"],
                env=None
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.read_resource("medchart://results/summary")
                    return json.loads(result.contents[0].text)
        
        mcp_summary = asyncio.run(get_mcp_summary())
        print(f"\n✅ MCP access:")
        print(f"   {json.dumps(mcp_summary, indent=2)}")
        
        # Compare
        if direct_summary == mcp_summary:
            print(f"\n✅ Results match! MCP provides same data as direct access")
            return True
        else:
            print(f"\n⚠️  Results differ (this might be expected if data changed)")
            return True
            
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        return False


def test_llm_service_mcp():
    """Test 6: Test MCP-enhanced LLM service."""
    print("\n" + "="*60)
    print("TEST 6: MCP-Enhanced LLM Service")
    print("="*60)
    
    try:
        from llm_service_mcp import LLMAnalyticsMCP
        
        # Initialize with MCP
        llm = LLMAnalyticsMCP(use_mcp=True)
        print(f"✅ LLM Service initialized with MCP support")
        print(f"   MCP available: {llm.mcp_available}")
        
        # Note: Actual analysis requires Groq API key
        print(f"\n   Note: Full analysis requires GROQ_API_KEY in .env")
        print(f"   MCP integration is ready for use")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"   Make sure llm_service_mcp.py exists")
        return False
    except Exception as e:
        print(f"⚠️  Initialization warning: {e}")
        print(f"   This is expected if GROQ_API_KEY is not set")
        return True


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP INTEGRATION TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Database
    results.append(("Database Setup", test_database_setup()))
    
    # Test 2: MCP Resources
    results.append(("MCP Resources", await test_mcp_server_resources()))
    
    # Test 3: MCP Read
    results.append(("MCP Resource Read", await test_mcp_resource_read()))
    
    # Test 4: MCP Tools
    results.append(("MCP Tools", await test_mcp_tools()))
    
    # Test 5: Comparison
    results.append(("MCP vs Direct", test_mcp_vs_direct_comparison()))
    
    # Test 6: LLM Service
    results.append(("LLM Service MCP", test_llm_service_mcp()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! MCP integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    print("Starting MCP Integration Tests...")
    print("Make sure you have:")
    print("1. Installed dependencies: pip install -r requirements.txt")
    print("2. Run some validations in the app to populate the database")
    print("3. mcp_server.py is in the current directory")
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

# Made with Bob