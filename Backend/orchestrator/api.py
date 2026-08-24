import os
import sys
import json
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Ensure the parent directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.graph import create_agent_executor, mcp_client
from database.db import init_db, get_db
from database.models import Chat, User
from orchestrator.routers.auth import router as auth_router
from orchestrator.routers.files import router as files_router
from orchestrator.routers.files import get_current_user
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    print("Initializing Database...")
    init_db()
    
    global agent_executor
    print("Initializing Agent Executor and connecting to MCP Server...")
    agent_executor = await create_agent_executor()
    print("Initialization complete.")
    yield
    print("Disconnecting from MCP Server...")
    await mcp_client.disconnect()
    print("Disconnected.")

app = FastAPI(title="Sovereign AI Workbench API", lifespan=lifespan)

# Include Routers
app.include_router(auth_router)
app.include_router(files_router)

# Global reference to the compiled agent graph
agent_executor = None

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    routing_flow: list

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent is not initialized yet.")
    
    # We pass the user message to the graph
    inputs = {"messages": [HumanMessage(content=req.message)]}
    
    try:
        # We await the graph invocation
        result = await agent_executor.ainvoke(inputs)
        
        # Build the routing flow visually from the messages
        routing_flow = ["Supervisor (Qwen2.5)"]
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                if msg.name == "transfer_to_coder":
                    routing_flow.append("Delegation -> Coder Agent (Qwen2.5-Coder)")
                    routing_flow.append("Tool executed: execute_python_code (Docker Sandbox)")
                    routing_flow.append("Delegation Return -> Coder Agent (Qwen2.5-Coder)")
                else:
                    routing_flow.append(f"Tool executed: {msg.name}")
                routing_flow.append("Supervisor (Qwen2.5)")
        
        # The last message is the final AI response
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        # Save to DB
        chat_record = Chat(
            user_id=current_user.id,
            session_id=req.session_id,
            user_msg=req.message,
            chatbot_msg=response_text,
            routing_flow=routing_flow
        )
        db.add(chat_record)
        db.commit()
        
        return ChatResponse(response=response_text, routing_flow=routing_flow)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history")
def get_chat_history(session_id: str = "default", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.session_id == session_id).order_by(Chat.timestamp.asc()).all()
    return chats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
