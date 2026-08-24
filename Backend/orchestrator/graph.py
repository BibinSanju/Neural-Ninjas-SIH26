from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages
import os

from orchestrator.mcp_client import LocalMCPClient

# The state of our LangGraph
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize LLMs
supervisor_llm = ChatOllama(model="qwen2.5", temperature=0)
coder_llm = ChatOllama(model="qwen2.5-coder", temperature=0)
kb_llm = ChatOllama(model="llama3.1", temperature=0)

# We will initialize the MCP client globally for the graph
MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mcp_server", "server.py")
mcp_client = LocalMCPClient(MCP_SERVER_PATH)

async def create_agent_executor():
    """Initializes the MCP client, builds Langchain tools, and returns a compiled Multi-Agent graph."""
    await mcp_client.connect()
    
    # 1. Define base MCP tools
    @tool
    async def execute_python_code(code: str) -> str:
        """Executes python code in an isolated Docker sandbox. Returns stdout and stderr."""
        return await mcp_client.call_tool("execute_python_code", {"code": code})
        
    @tool
    async def search_knowledge_base(query: str) -> str:
        """Searches the internal knowledge base for the given query."""
        return await mcp_client.call_tool("search_knowledge_base", {"query": query})
        
    @tool
    async def generate_word_document(title: str, content: str, filepath: str) -> str:
        """Generates a .docx approval note or report."""
        return await mcp_client.call_tool("generate_word_document", {"title": title, "content": content, "filepath": filepath})
        
    @tool
    async def generate_excel_spreadsheet(data_json: str, filepath: str) -> str:
        """Generates a .xlsx spreadsheet with the provided tabular data."""
        return await mcp_client.call_tool("generate_excel_spreadsheet", {"data_json": data_json, "filepath": filepath})

    # 2. Build the Coder Specialist Agent
    coder_tools = [execute_python_code]
    coder_agent = create_react_agent(coder_llm, coder_tools)

    @tool
    async def transfer_to_coder(instructions: str) -> str:
        """Delegates math, logic, and python code execution tasks to the specialized Coder Agent. Give it clear instructions."""
        print(f"\n[Routing] Supervisor handing off to Coder Agent with instructions: {instructions}")
        result = await coder_agent.ainvoke({"messages": [HumanMessage(content=instructions)]})
        # Return the coder's final answer back to the supervisor
        return result["messages"][-1].content

    # 3. Build the Knowledge Base Specialist Agent
    kb_tools = [search_knowledge_base]
    kb_agent = create_react_agent(kb_llm, kb_tools)
    
    @tool
    async def transfer_to_knowledge_base(instructions: str) -> str:
        """Delegates document retrieval and fact-finding tasks to the specialized Knowledge Base Agent. Give it clear instructions about what to search for."""
        print(f"\n[Routing] Supervisor handing off to Knowledge Base Agent with instructions: {instructions}")
        result = await kb_agent.ainvoke({"messages": [HumanMessage(content=instructions)]})
        # Return the KB agent's final answer back to the supervisor
        return result["messages"][-1].content

    # 4. Build the Supervisor Master Agent
    supervisor_tools = [
        generate_word_document,
        generate_excel_spreadsheet,
        transfer_to_coder,
        transfer_to_knowledge_base
    ]
    
    # We use a system prompt to enforce delegation
    system_prompt = (
        "You are the Supervisor Agent for an internal AI Workbench. "
        "You have access to tools for document generation. "
        "CRITICAL RULES: \n"
        "1. UNDER NO CIRCUMSTANCES are you allowed to perform arithmetic operations yourself (e.g., addition, multiplication). Even if the math is simple, YOU MUST ALWAYS delegate it using the 'transfer_to_coder' tool.\n"
        "2. You MUST NOT try to answer factual queries about internal documents yourself. If a task requires looking up facts or searching the knowledge base, you MUST use the 'transfer_to_knowledge_base' tool to delegate it to the Knowledge Base Agent.\n"
        "3. You may use BOTH tools sequentially if a task requires finding numbers in the manual and then calculating something with them."
    )
    
    supervisor_agent = create_react_agent(supervisor_llm, supervisor_tools, prompt=system_prompt)
    
    return supervisor_agent
