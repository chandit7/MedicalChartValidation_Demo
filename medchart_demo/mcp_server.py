"""
MCP Server for MedChart Database Access
Provides standardized access to validation results through Model Context Protocol
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
import db

# Initialize MCP Server
app = Server("medchart-database")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available database resources."""
    return [
        Resource(
            uri="medchart://results/all",
            name="All Validation Results",
            description="Complete history of all medical chart validations",
            mimeType="application/json"
        ),
        Resource(
            uri="medchart://results/summary",
            name="Validation Summary",
            description="Aggregated statistics of validation decisions",
            mimeType="application/json"
        ),
        Resource(
            uri="medchart://results/recent",
            name="Recent Validations",
            description="Validation results from the last 30 days",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read database resource by URI."""
    if uri == "medchart://results/all":
        results = db.get_all_results()
        return json.dumps(results, indent=2)
    
    elif uri == "medchart://results/summary":
        summary = db.get_summary()
        return json.dumps(summary, indent=2)
    
    elif uri == "medchart://results/recent":
        results_df = db.get_results_for_analysis(days=30)
        results = results_df.to_dict(orient='records')
        return json.dumps(results, indent=2)
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available database tools."""
    return [
        Tool(
            name="query_results_by_decision",
            description="Query validation results filtered by decision type",
            inputSchema={
                "type": "object",
                "properties": {
                    "decision": {
                        "type": "string",
                        "enum": ["approved", "rejected", "manual_review"],
                        "description": "Decision type to filter by"
                    }
                },
                "required": ["decision"]
            }
        ),
        Tool(
            name="query_results_by_member",
            description="Query validation results for a specific member",
            inputSchema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID to query"
                    }
                },
                "required": ["member_id"]
            }
        ),
        Tool(
            name="get_trend_analysis_data",
            description="Get data for trend analysis over specified days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze",
                        "default": 30
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_daily_metrics",
            description="Get validation metrics for the last 24 hours",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute database tool."""
    
    if name == "query_results_by_decision":
        decision = arguments.get("decision")
        all_results = db.get_all_results()
        filtered = [r for r in all_results if r["decision"] == decision]
        return [TextContent(
            type="text",
            text=json.dumps(filtered, indent=2)
        )]
    
    elif name == "query_results_by_member":
        member_id = arguments.get("member_id")
        all_results = db.get_all_results()
        filtered = [r for r in all_results if r["member_id"] == member_id]
        return [TextContent(
            type="text",
            text=json.dumps(filtered, indent=2)
        )]
    
    elif name == "get_trend_analysis_data":
        days = arguments.get("days", 30)
        results_df = db.get_results_for_analysis(days=days)
        results = results_df.to_dict(orient='records')
        return [TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
    
    elif name == "get_daily_metrics":
        daily = db.get_daily_summary()
        return [TextContent(
            type="text",
            text=json.dumps(daily, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob