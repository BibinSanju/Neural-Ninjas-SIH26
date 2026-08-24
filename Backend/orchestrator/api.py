from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uvicorn
import asyncio
import os
import sys

# Ensure the parent directory is in the path so we can import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.graph import create_agent_executor, mcp_client

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_executor
    print("Initializing Agent Executor and connecting to MCP Server...")
    agent_executor = await create_agent_executor()
    print("Initialization complete.")
    yield
    print("Disconnecting from MCP Server...")
    await mcp_client.disconnect()
    print("Disconnected.")

app = FastAPI(title="Sovereign AI Workbench API", lifespan=lifespan)

# Global reference to the compiled agent graph
agent_executor = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent is not initialized yet.")
    
    # We pass the user message to the graph
    inputs = {"messages": [HumanMessage(content=req.message)]}
    
    try:
        # We await the graph invocation
        # Note: langgraph invoke is synchronous by default unless using ainvoke
        result = await agent_executor.ainvoke(inputs)
        
        # The result contains the messages list, the last message is the AI response
        last_message = result["messages"][-1]
        return ChatResponse(response=last_message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
