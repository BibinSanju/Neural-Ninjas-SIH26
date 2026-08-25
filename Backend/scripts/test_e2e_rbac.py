import asyncio
import os
import sys

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_db, SessionLocal
from database.models import User, Role
import bcrypt
from scripts.ingest import ingest_file
from orchestrator.graph import create_agent_executor, mcp_client
from langchain_core.messages import HumanMessage

async def main():
    print("=== Initialize DB ===")
    init_db()
    db = SessionLocal()
    
    print("=== Creating Users ===")
    # Create Admin Role
    admin_role = db.query(Role).filter_by(name="Admin").first()
    if not admin_role:
        admin_role = Role(name="Admin")
        db.add(admin_role)
        
    # Create Operator Role
    operator_role = db.query(Role).filter_by(name="Operator").first()
    if not operator_role:
        operator_role = Role(name="Operator")
        db.add(operator_role)
        
    db.commit()
    
    # Create Admin User
    admin_user = db.query(User).filter_by(username="admin_test").first()
    if not admin_user:
        hashed = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = User(username="admin_test", password_hash=hashed, role_id=admin_role.id)
        db.add(admin_user)
        
    # Create Operator User
    operator_user = db.query(User).filter_by(username="operator_test").first()
    if not operator_user:
        hashed = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        operator_user = User(username="operator_test", password_hash=hashed, role_id=operator_role.id)
        db.add(operator_user)
        
    db.commit()
    
    print("=== Creating Test Document ===")
    test_filepath = "test_alpha_reactor.txt"
    with open(test_filepath, "w") as f:
        f.write("The Alpha Reactor is a highly classified energy source. It has a baseline structural integrity coefficient of 4.25. The absolute failure threshold is exactly 12.5 PSI.")
    
    print("=== Ingesting Document as Admin (Clearance 5) ===")
    # It will connect to Neo4j and use llama3.1 to extract graph + BAAI for vector
    # ingest_file(test_filepath, "doc-alpha-123", "test_alpha_reactor.txt", "5")
    
    print("=== Initializing Agent ===")
    agent_executor = await create_agent_executor()
    
    test_prompt = (
        "Find the Alpha Reactor specs (look for the structural integrity coefficient and failure threshold). "
        "Calculate the failure threshold raised to the power of the structural integrity coefficient. "
        "Finally, generate a Word document report named 'outputs/{filename}' containing the math results and specs."
    )
    
    print("\n\n" + "="*50)
    print("TEST CASE 1: ADMIN ACCESS (CLEARANCE 5)")
    print("="*50)
    
    admin_msg = f"USER CLEARANCE LEVEL: 5\nUSER REQUEST: {test_prompt.format(filename='admin_report.docx')}"
    
    result_admin = await agent_executor.ainvoke(
        {"messages": [HumanMessage(content=admin_msg)]}, 
        config={"recursion_limit": 15}
    )
    
    print("\n[Admin Final Response]:")
    print(result_admin["messages"][-1].content)
    
    print("\n\n" + "="*50)
    print("TEST CASE 2: OPERATOR ACCESS (CLEARANCE 1)")
    print("="*50)
    
    operator_msg = f"USER CLEARANCE LEVEL: 1\nUSER REQUEST: {test_prompt.format(filename='operator_report.docx')}"
    
    result_operator = await agent_executor.ainvoke(
        {"messages": [HumanMessage(content=operator_msg)]}, 
        config={"recursion_limit": 15}
    )
    
    print("\n[Operator Final Response]:")
    print(result_operator["messages"][-1].content)
    
    await mcp_client.disconnect()
    
    # Cleanup
    if os.path.exists(test_filepath):
        os.remove(test_filepath)
    print("Tests completed.")

if __name__ == "__main__":
    asyncio.run(main())
