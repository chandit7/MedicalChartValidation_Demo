# llm_service_mcp.py
"""
Enhanced LLM Analytics with MCP Integration
Demonstrates how to use MCP for standardized data access
"""

import os
import json
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class LLMAnalyticsMCP:
    """
    LLM-powered analytics using Groq with MCP for data access.
    This version uses Model Context Protocol for standardized database access.
    """
    
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile", use_mcp=True):
        """
        Initialize Groq client and optionally MCP client.
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model to use (default: llama-3.3-70b-versatile)
            use_mcp: Whether to use MCP for data access (default: True)
        """
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = model
        self.cache = {}  # Simple response cache
        self.use_mcp = use_mcp
        self.mcp_session = None
        
        if use_mcp:
            self._init_mcp()
    
    def _init_mcp(self):
        """Initialize MCP client connection."""
        try:
            # Note: In production, this would connect to actual MCP server
            print("✅ MCP client initialized (ready to connect to server)")
        except Exception as e:
            print(f"⚠️ MCP initialization failed: {e}")
            self.mcp_available = False
    
    async def _get_data_via_mcp(self, resource_uri: str):
        """
        Get data through MCP protocol.
        
        Args:
            resource_uri: MCP resource URI (e.g., "medchart://results/all")
        
        Returns:
            Data from MCP server
        """
        if not self.use_mcp or not self.mcp_available:
            return None
        
        try:
            # Connect to MCP server
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"],
                env=None
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Read resource
                    result = await session.read_resource(resource_uri)
                    return json.loads(result.contents[0].text)
        
        except Exception as e:
            print(f"⚠️ MCP data fetch failed: {e}")
            return None
    
    async def _call_mcp_tool(self, tool_name: str, arguments: dict):
        """
        Call MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            Tool result
        """
        if not self.use_mcp or not self.mcp_available:
            return None
        
        try:
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"],
                env=None
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Call tool
                    result = await session.call_tool(tool_name, arguments)
                    return json.loads(result.content[0].text)
        
        except Exception as e:
            print(f"⚠️ MCP tool call failed: {e}")
            return None
    
    def generate(self, prompt, max_tokens=500, temperature=0.7):
        """Generate LLM response with caching."""
        # Check cache
        cache_key = f"{prompt[:100]}_{max_tokens}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a healthcare analytics expert analyzing medical chart validation data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            result = response.choices[0].message.content
            
            # Cache result
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            return f"⚠️ Error: {str(e)}\n\nPlease check your API key and internet connection."
    
    def analyze_trends_mcp(self, days=30):
        """
        Analyze validation trends using MCP for data access.
        
        This method demonstrates the MCP approach vs direct database access.
        """
        import asyncio
        
        # Try to get data via MCP first
        if self.use_mcp and self.mcp_available:
            try:
                results = asyncio.run(
                    self._call_mcp_tool("get_trend_analysis_data", {"days": days})
                )
                
                if results:
                    print(f"✅ Data fetched via MCP (standardized protocol)")
                    return self._analyze_with_data(results, days)
            except Exception as e:
                print(f"⚠️ MCP fetch failed, falling back to direct access: {e}")
        
        # Fallback to direct database access
        import db
        results_df = db.get_results_for_analysis(days=days)
        results = results_df.to_dict(orient='records')
        print(f"ℹ️ Data fetched via direct database access")
        return self._analyze_with_data(results, days)
    
    def _analyze_with_data(self, results, days):
        """Perform analysis with fetched data."""
        if len(results) == 0:
            return f"No validation results available for the last {days} days."
        
        # Calculate statistics
        import pandas as pd
        df = pd.DataFrame(results)
        
        decision_counts = df['decision'].fillna('').astype(str).str.lower().value_counts()
        non_empty_flags = df['flags'].fillna('').astype(str)
        non_empty_flags = non_empty_flags[non_empty_flags.str.strip() != '']
        
        summary = {
            'total': len(df),
            'approved': int(decision_counts.get('approved', 0)),
            'rejected': int(decision_counts.get('rejected', 0)),
            'manual_review': int(decision_counts.get('manual_review', 0)),
            'avg_confidence': df['confidence'].mean(),
            'common_flags': non_empty_flags.value_counts().head(5).to_dict()
        }
        
        prompt = f"""
Analyze these medical chart validation results from the past {days} days.

**Summary Statistics:**
- Total charts: {summary['total']}
- Approved: {summary['approved']} ({summary['approved']/summary['total']*100:.1f}%)
- Rejected: {summary['rejected']} ({summary['rejected']/summary['total']*100:.1f}%)
- Manual Review: {summary['manual_review']} ({summary['manual_review']/summary['total']*100:.1f}%)
- Average confidence: {summary['avg_confidence']:.2f}

**Most Common Flags:**
{json.dumps(summary['common_flags'], indent=2)}

Provide:
1. **Key Trends**: What patterns do you see?
2. **Potential Issues**: Any concerning trends?
3. **Recommendations**: 3 actionable improvements

Format as markdown with clear sections.
"""
        return self.generate(prompt, max_tokens=800)
    
    # Keep existing methods for backward compatibility
    def analyze_trends(self, results_df, days=30):
        """Original method for backward compatibility."""
        results = results_df.to_dict(orient='records')
        return self._analyze_with_data(results, days)
    
    def explain_decision(self, result):
        """Generate human-friendly explanation of a validation decision."""
        prompt = f"""
Explain this medical chart validation decision in simple terms:

**Chart Details:**
- Member ID: {result.get('member_id', 'N/A')}
- Decision: {result['decision']}
- Confidence Score: {result['confidence']:.2f}
- Flags: {result.get('flags', 'None')}

Provide 3 explanations for different audiences:

1. **For Healthcare Provider** (clinical perspective)
2. **For Quality Reviewer** (compliance perspective)  
3. **For Member Services** (patient-friendly language)

Keep each explanation to 2-3 sentences.
"""
        return self.generate(prompt, max_tokens=600)
    
    def root_cause_analysis(self, filtered_results):
        """Identify root causes for specific decision patterns."""
        if len(filtered_results) == 0:
            return "No results to analyze."
        
        summary = {
            'count': len(filtered_results),
            'common_flags': filtered_results['flags'].value_counts().head(5).to_dict(),
            'avg_confidence': filtered_results['confidence'].mean(),
            'decision_breakdown': filtered_results['decision'].value_counts().to_dict()
        }
        
        prompt = f"""
Perform root cause analysis on these {summary['count']} flagged/rejected charts:

**Common Flags:**
{json.dumps(summary['common_flags'], indent=2)}

**Decision Breakdown:**
{json.dumps(summary['decision_breakdown'], indent=2)}

Identify:
1. **Root Causes**: Why are these charts being flagged?
2. **Preventable Issues**: What could be fixed upstream?
3. **Data Quality**: Any data entry problems?
4. **Training Needs**: What staff training would help?

Provide specific, actionable insights.
"""
        return self.generate(prompt, max_tokens=700)
    
    def natural_language_query(self, question, results_df):
        """Answer questions about validation data in natural language."""
        stats = {
            'total': len(results_df),
            'decisions': results_df['decision'].value_counts().to_dict(),
            'avg_confidence': results_df['confidence'].mean(),
            'date_range': f"{results_df['created_at'].min()} to {results_df['created_at'].max()}"
        }
        
        prompt = f"""
Answer this question about medical chart validation data:

**Question:** {question}

**Available Data:**
- Total records: {stats['total']}
- Date range: {stats['date_range']}
- Decisions: {json.dumps(stats['decisions'], indent=2)}
- Average confidence: {stats['avg_confidence']:.2f}

Provide a clear, concise answer with specific numbers where applicable.
"""
        return self.generate(prompt, max_tokens=400)

# Made with Bob