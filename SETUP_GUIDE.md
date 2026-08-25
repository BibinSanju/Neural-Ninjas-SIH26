# 🚀 Sovereign AI Workbench - Deployment Guide

This guide provides the exact step-by-step instructions to deploy the Sovereign AI Workbench from scratch on a new laptop or presentation machine.

## Prerequisites
Before you begin, ensure the new machine has the following installed:
1. **Python 3.10+**
2. **Node.js (v18+) & npm**
3. **Docker** (for the Neo4j Graph Database)
4. **Ollama** (for local AI inference)

---

## 1️⃣ Clone the Repository
Open a terminal and clone your main branch:
```bash
git clone https://github.com/<your-username>/Neural-Ninjas-SIH26.git
cd Neural-Ninjas-SIH26
```

---

## 2️⃣ Start the Neo4j Database (GraphRAG)
The Knowledge Base Agent requires Neo4j to store document embeddings and graph connections. Start it using Docker:
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/industrial_password_2026 \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    neo4j:latest
```
*(Wait a few seconds for the database container to initialize).*

---

## 3️⃣ Pull the Required Local AI Models
The orchestration graph depends on four specific models running locally. Open a terminal and run:
```bash
# 1. Pull the Master Supervisor and Knowledge Base Agent model
ollama pull qwen2.5:7b

# 2. Pull the Coder Specialist Agent model
ollama pull qwen2.5-coder:7b

# 3. Pull the Deliverable Synth Agent model
ollama pull mistral:latest

# 4. Pull the Vision Expert Agent model
ollama pull qwen2.5vl:7b
```

---

## 4️⃣ Setup and Run the Backend
The backend utilizes FastAPI, LangGraph, and the Model Context Protocol (MCP).

Open a new terminal in the `Backend` directory:
```bash
cd Backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Backend Server
uvicorn orchestrator.api:app --reload --port 8000
```
*(You should see logs indicating the Database initialized and the MCP server connected successfully).*

---

## 5️⃣ Setup and Run the Frontend
The frontend is a React application built with Vite.

Open a **new** terminal in the `Frontend` directory:
```bash
cd Frontend

# Install node dependencies
npm install

# Start the development server
npm run dev
```

---

## 6️⃣ Access the Workbench
1. Open your browser and navigate to **http://localhost:3000** (or whichever port Vite assigned, often 3000 or 5173).
2. The UI will automatically authenticate you as the `Admin` for testing purposes based on the hardcoded bypass.
3. **Test the Vision Model**: Click "Upload File", select an image, and ask *"What is in this image?"*
4. **Test the Knowledge Base**: Upload a document and ask a question about its contents!

🎉 **You are now successfully running the fully air-gapped Sovereign AI Workbench!**
