import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from tools.sandbox import execute_python_code
from tools.rag import search_knowledge_base
from tools.artifacts import generate_word_document, generate_excel_spreadsheet

app = Server("ai-workbench-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
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
        Tool(
            name="search_knowledge_base",
            description="Searches the internal knowledge base for the given query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to look up in the vector store"}
                },
                "required": ["query"]
            }
        ),
        Tool(
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
        Tool(
            name="generate_excel_spreadsheet",
            description="Generates a .xlsx spreadsheet with the provided tabular data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_json": {"type": "string", "description": "A JSON string representing an array of objects (rows)"},
                    "filepath": {"type": "string", "description": "Destination file path (e.g. data.xlsx)"}
                },
                "required": ["data_json", "filepath"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "execute_python_code":
        result = await execute_python_code(arguments["code"])
        return [TextContent(type="text", text=result)]
    elif name == "search_knowledge_base":
        result = await search_knowledge_base(arguments["query"])
        return [TextContent(type="text", text=result)]
    elif name == "generate_word_document":
        result = await generate_word_document(arguments["title"], arguments["content"], arguments["filepath"])
        return [TextContent(type="text", text=result)]
    elif name == "generate_excel_spreadsheet":
        result = await generate_excel_spreadsheet(arguments["data_json"], arguments["filepath"])
        return [TextContent(type="text", text=result)]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
