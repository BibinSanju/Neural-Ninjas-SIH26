from typing import Annotated, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os

from orchestrator.mcp_client import LocalMCPClient

# The state of our LangGraph
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # We could add more state like 'current_agent', 'scratchpad', etc.

# Initialize LLMs (User needs to have ollama running with these models pulled)
# E.g. `ollama run qwen2.5`
supervisor_llm = ChatOllama(model="qwen2.5", temperature=0)

# We will initialize the MCP client globally for the graph
MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mcp_server", "server.py")
mcp_client = LocalMCPClient(MCP_SERVER_PATH)

# We will dynamically populate tools once the client connects
langchain_tools = []

async def init_tools():
    """Connects to MCP and wraps its tools as Langchain tools."""
    await mcp_client.connect()
    mcp_tools = await mcp_client.get_tools()
    
    for t in mcp_tools:
        # Create a function dynamically for each tool
        def tool_wrapper(arguments: dict, tool_name=t.name):
            import asyncio
            # We must run this in the event loop properly.
            # For simplicity in this sync-wrapper inside an async graph, we can use a small hack or 
            # ideally the agents call it natively if we use async tools.
            # Langchain's `@tool` doesn't strictly need it to be sync if we do it right, but here's a wrapper:
            
            # This is a bit tricky: if we are in an async context, we can just await it.
            # Let's make the wrapper async.
            pass
            
        # A cleaner way is to define an explicit async wrapper per tool
        # In a full implementation, we'd map the JSON Schema to Pydantic models.

# --- Graph Nodes ---
# We use a simple ReAct agent approach for the supervisor for now.
# In a true multi-agent, we'd have sub-graphs. 
# Here we'll create a master agent that has access to all tools.

from langgraph.prebuilt import create_react_agent

async def create_agent_executor():
    """Initializes the MCP client, builds Langchain tools, and returns a compiled graph."""
    await mcp_client.connect()
    mcp_tools = await mcp_client.get_tools()
    
    tools_list = []
    
    # Manually wrap each tool for now to ensure type safety and async compatibility
    @tool
    async def execute_python_code(code: str) -> str:
        """Executes python code in an isolated Docker sandbox. Returns stdout and stderr."""
        return await mcp_client.call_tool("execute_python_code", {"code": code})
    tools_list.append(execute_python_code)
    
    @tool
    async def search_knowledge_base(query: str) -> str:
        """Searches the internal knowledge base for the given query."""
        return await mcp_client.call_tool("search_knowledge_base", {"query": query})
    tools_list.append(search_knowledge_base)
    
    @tool
    async def generate_word_document(title: str, content: str, filepath: str) -> str:
        """Generates a .docx approval note or report."""
        return await mcp_client.call_tool("generate_word_document", {"title": title, "content": content, "filepath": filepath})
    tools_list.append(generate_word_document)
    
    @tool
    async def generate_excel_spreadsheet(data_json: str, filepath: str) -> str:
        """Generates a .xlsx spreadsheet with the provided tabular data."""
        return await mcp_client.call_tool("generate_excel_spreadsheet", {"data_json": data_json, "filepath": filepath})
    tools_list.append(generate_excel_spreadsheet)
    
    # We bind tools to the LLM
    agent = create_react_agent(supervisor_llm, tools_list)
    return agent

# The graph is actually created inside the FastAPI app lifecycle.
