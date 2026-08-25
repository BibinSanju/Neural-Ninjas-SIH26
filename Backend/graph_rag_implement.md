# AGENT INSTRUCTION: Implement Industrial GraphRAG with Graph-Native RBAC

## 1. Objective
Replace standard vector search with an integrated **Hybrid GraphRAG + Vector Indexing Engine** using a single containerized **Neo4j** instance. Enforce **Graph-Native Role-Based Access Control (RBAC)** to ensure industrial documents, P&ID schematics, and OISD compliance standards are accessed strictly according to user clearance levels. Do not use ChromaDB.

## 2. Technical Stack for this Module
*   **Database:** Neo4j Community / Enterprise Container (via Docker)
*   **Embeddings:** `BAAI/bge-large-en-v1.5` (via `sentence-transformers` running locally on CPU)
*   **LLM:** `llama3.1:8b-instruct-q4_K_M` (via local Ollama endpoint)
*   **Framework:** `langchain_community` (Neo4jGraph, HuggingFaceEmbeddings)

## 3. Step 1: Database Initialization & Schema
Execute the following to set up the Neo4j container with APOC plugins enabled:

```bash
docker run -d \
  --name neo4j-graphrag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/industrial_password_2026 \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.20.0