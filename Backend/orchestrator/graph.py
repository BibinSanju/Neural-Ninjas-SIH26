from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages
import os
import base64

from orchestrator.mcp_client import LocalMCPClient

# The state of our LangGraph
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize LLMs with keep_alive=0 to unload immediately and save VRAM
# Explicitly use :7b tags to match the pulled Ollama images!
supervisor_llm = ChatOllama(model="qwen2.5:7b", temperature=0, keep_alive=0)
coder_llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0, keep_alive=0)
kb_llm = ChatOllama(model="qwen2.5:7b", temperature=0, keep_alive=0)
synth_llm = ChatOllama(model="mistral:latest", temperature=0, keep_alive=0)
vision_llm = ChatOllama(model="qwen2.5vl:7b", temperature=0, keep_alive=0)

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
    async def search_knowledge_base(query: str, clearance_level: str) -> str:
        """Searches the internal knowledge base for the given query with the user's clearance_level."""
        return await mcp_client.call_tool("search_knowledge_base", {"query": query, "clearance_level": clearance_level})
        
    @tool
    async def generate_word_document(title: str, content: str, filepath: str) -> str:
        """Generates a .docx approval note or report."""
        return await mcp_client.call_tool("generate_word_document", {"title": title, "content": content, "filepath": filepath})
        
    @tool
    async def analyze_image(image_path: str, question: str) -> str:
        """Analyzes an image (e.g. diagrams, schematics, photos) to answer a question. 
        Pass the absolute path to the uploaded image file."""
        import base64
        try:
            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
                
            from langchain_core.messages import HumanMessage
            msg = HumanMessage(
                content=[
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            )
            # Delegate directly to the Vision LLM (llama3.2-vision)
            response = await vision_llm.ainvoke([msg])
            return response.content
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
        
    @tool
    async def generate_excel_spreadsheet(csv_data: str, filepath: str) -> str:
        """Generates a .xlsx spreadsheet with the provided tabular data."""
        return await mcp_client.call_tool("generate_excel_spreadsheet", {"csv_data": csv_data, "filepath": filepath})

    # 2. Build the Coder Specialist Agent
    coder_tools = [execute_python_code]
    coder_agent = create_react_agent(coder_llm, coder_tools)

    @tool
    async def transfer_to_coder(instructions: str) -> str:
        """Delegates math, logic, and python code execution tasks to the specialized Coder Agent. Give it clear instructions."""
        print(f"\n[Routing] Supervisor handing off to Coder Agent with instructions: {instructions}")
        result = await coder_agent.ainvoke({"messages": [HumanMessage(content=instructions)]}, config={"recursion_limit": 5})
        output = result["messages"][-1].content
        return f"Successfully executed. The Coder Agent returned: {output}\n(Supervisor Note: If the user requested a file or report, proceed to the Deliverable Synth Agent now.)"

    # 3. Build the Knowledge Base Specialist Agent
    kb_tools = [search_knowledge_base]
    kb_system_prompt = (
        "You are the Knowledge Base Agent. "
        "You have access to the search_knowledge_base tool. "
        "When the supervisor gives you instructions, they will provide a 'clearance_level'. "
        "You MUST pass this exact clearance_level as an argument to the search_knowledge_base tool."
    )
    kb_agent = create_react_agent(kb_llm, kb_tools, prompt=kb_system_prompt)
    
    @tool
    async def transfer_to_knowledge_base(instructions: str) -> str:
        """Delegates document retrieval and fact-finding tasks to the specialized Knowledge Base Agent. Give it clear instructions about what to search for and include the user's clearance_level."""
        print(f"\n[Routing] Supervisor handing off to Knowledge Base Agent with instructions: {instructions}")
        result = await kb_agent.ainvoke({"messages": [HumanMessage(content=instructions)]}, config={"recursion_limit": 5})
        output = result["messages"][-1].content
        return f"Successfully executed. The Knowledge Base Agent returned: {output}\n(Supervisor Note: Review the user's request and proceed to the next step, such as the Coder Agent if calculations are needed.)"

    # Vision Expert Integration
    @tool
    async def transfer_to_vision(image_path: str, question: str) -> str:
        """Delegates image and diagram analysis to the Vision Expert Agent. Pass the absolute image path and the specific question."""
        print(f"\n[Routing] Supervisor handing off to Vision Agent with image: {image_path}")
        output = await analyze_image.ainvoke({"image_path": image_path, "question": question})
        return f"Successfully executed. The Vision Agent returned: {output}"

    # 4. Build the Deliverable Synth Specialist Agent
    synth_tools = [generate_word_document, generate_excel_spreadsheet]
    synth_system_prompt = (
        "You are the Deliverable Synth Agent.\n"
        "You must generate the requested file by calling the appropriate tool.\n"
        "- For Word documents, call the `generate_word_document` tool.\n"
        "- For Excel spreadsheets, call the `generate_excel_spreadsheet` tool and pass the data as a CSV string.\n"
        "Call the tool directly. Do not explain what you are going to do."
    )
    synth_agent = create_react_agent(supervisor_llm, synth_tools, prompt=synth_system_prompt)

    @tool
    async def transfer_to_deliverable_synth(instructions: str) -> str:
        """Use this tool to generate Word documents or Excel spreadsheets. Pass all necessary context (numbers, tabular data, final answer, and filepath) in the instructions string so the agent can write the file."""
        print(f"\n[Routing] Supervisor handing off to Deliverable Synth Agent with instructions: {instructions}")
        result = await synth_agent.ainvoke({"messages": [HumanMessage(content=instructions)]}, config={"recursion_limit": 5})
        output = result["messages"][-1].content
        print(f"\n[Synth Agent Return]: {output}")
        return f"Successfully executed. The Deliverable Synth Agent returned: {output}"

    # 5. Build the Supervisor Master Agent
    supervisor_tools = [
        transfer_to_coder,
        transfer_to_knowledge_base,
        transfer_to_deliverable_synth,
        transfer_to_vision
    ]
    
    system_prompt = (
        "You are the Supervisor Agent for an internal AI Workbench.\n"
        "Your job is to read the user's request, create a plan, and delegate tasks to the specialist agents using your tools.\n\n"
        "Available Specialists:\n"
        "- Knowledge Base Agent (use `transfer_to_knowledge_base`): For searching internal documents and retrieving factual numbers.\n"
        "- Coder Agent (use `transfer_to_coder`): For ALL math, calculations, and python execution.\n"
        "- Deliverable Synth Agent (use `transfer_to_deliverable_synth`): For generating files, saving reports (.docx), and creating spreadsheets.\n"
        "- Vision Expert Agent (use `transfer_to_vision`): For analyzing images, diagrams, schematics, and photos provided by the user.\n\n"
        "Instructions:\n"
        "1. Delegate tasks sequentially (e.g. Knowledge Base -> Coder -> Deliverable Synth).\n"
        "2. CRITICAL: When handing off tasks between agents, you MUST explicitly include ALL raw numbers, arrays, and data in your instructions. Do not summarize; pass the exact numbers!\n"
        "3. CRITICAL: You will receive the user's CLEARANCE LEVEL in the initial prompt. You MUST include this clearance level in your instructions to the Knowledge Base Agent!\n"
        "4. CRITICAL: If the Knowledge Base Agent reports 'Access Denied', 'No relevant information found', or fails to find the required data, DO NOT proceed to the Coder or Synth agents! You must abort the workflow immediately and reply to the user that they lack clearance.\n"
        "5. Wait for each tool to return before deciding the next step.\n"
        "6. If the user asks for a file, you MUST pass the final data to the Deliverable Synth Agent to generate it.\n"
        "7. Do NOT stop until ALL parts of the user's request are fulfilled (unless aborted due to clearance)."
    )
    
    supervisor_agent = create_react_agent(supervisor_llm, supervisor_tools, prompt=system_prompt)
    
    return supervisor_agent
