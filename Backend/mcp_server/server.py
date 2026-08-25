import asyncio
import sys
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from tools.sandbox import execute_python_code
from tools.rag import search_knowledge_base
from tools.artifacts import generate_word_document, generate_excel_spreadsheet

app = Server("ai-workbench-mcp")

async def list_tools(ctx, request: types.PaginatedRequestParams) -> types.ListToolsResult:
    """List available tools."""
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="execute_python_code",
                description="Executes python code in an isolated Docker sandbox. Returns stdout and stderr.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "The python code to execute"}
                    },
                    "required": ["code"]
                }
            ),
            types.Tool(
                name="search_knowledge_base",
                description="Searches the internal knowledge base for the given query using GraphRAG.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query to look up in the vector store"},
                        "clearance_level": {"type": "string", "description": "The user's clearance level (e.g. 1, 3, 5) for RBAC filtering"}
                    },
                    "required": ["query", "clearance_level"]
                }
            ),
            types.Tool(
                name="generate_word_document",
                description="Generates a .docx approval note or report.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the document"},
                        "content": {"type": "string", "description": "Markdown formatted content of the document"},
                        "filepath": {"type": "string", "description": "Destination file path (e.g. report.docx)"}
                    },
                    "required": ["title", "content", "filepath"]
                }
            ),
            types.Tool(
                name="generate_excel_spreadsheet",
                description="Generates a .xlsx spreadsheet with the provided tabular data.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "csv_data": {
                            "type": "string",
                            "description": "A multi-line CSV string containing the headers and rows to be written to the spreadsheet."
                        },
                        "filepath": {"type": "string", "description": "Destination file path (e.g. data.xlsx)"}
                    },
                    "required": ["csv_data", "filepath"]
                }
            )
        ]
    )

async def call_tool(ctx, request: types.CallToolRequestParams) -> types.CallToolResult:
    name = request.name
    arguments = request.arguments or {}
    if name == "execute_python_code":
        result = await execute_python_code(arguments["code"])
        return types.CallToolResult(content=[types.TextContent(type="text", text=result)])
    elif name == "search_knowledge_base":
        result = await search_knowledge_base(arguments["query"], arguments["clearance_level"])
        return types.CallToolResult(content=[types.TextContent(type="text", text=result)])
    elif name == "generate_word_document":
        result = await generate_word_document(arguments["title"], arguments["content"], arguments["filepath"])
        return types.CallToolResult(content=[types.TextContent(type="text", text=result)])
    elif name == "generate_excel_spreadsheet":
        result = await generate_excel_spreadsheet(arguments["csv_data"], arguments["filepath"])
        return types.CallToolResult(content=[types.TextContent(type="text", text=result)])
    else:
        raise ValueError(f"Unknown tool: {name}")

app.add_request_handler("tools/list", types.PaginatedRequestParams, list_tools)
app.add_request_handler("tools/call", types.CallToolRequestParams, call_tool)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        print("MCP server started and listening on stdio...", file=sys.stderr)
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
