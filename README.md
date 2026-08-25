# 🛡️ Sovereign Air-Gapped AI Workbench
### Zero-Trust Multi-Agent Orchestration & Deterministic Engineering System for Industrial, Energy & PSU Infrastructure

[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Confidential-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20Inference-black.svg?logo=ollama)](https://ollama.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-GraphRAG%20%2B%20APOC-008CC1.svg?logo=neo4j)](https://neo4j.com/)
[![Docker](https://img.shields.io/badge/Docker-Ephemeral%20Air--Gapped%20Sandbox-2496ED.svg?logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg?logo=react)](https://vitejs.dev/)
[![Compliance](https://img.shields.io/badge/Compliance-NCIIPC%20%7C%20CERT--In%20%7C%20OISD%20%7C%20ASME-success.svg)](#security-compliance--air-gapping)

---

## 📌 Executive Summary

The **Sovereign Air-Gapped AI Workbench** is an enterprise-grade, fully local, multi-agent AI system engineered specifically for **Public Sector Undertakings (PSUs)**, energy plants, refineries, defense, and critical industrial installations. 

Operating under complete **air-gap constraints (Zero Outbound Internet)**, the platform replaces generic, hallucination-prone LLM chats with a deterministic, cryptographically auditable, and hierarchical multi-agent workflow:
- **Zero Data Exfiltration**: Runs 100% on local GPU hardware via Ollama/vLLM.
- **Hierarchical Zero-Trust RBAC (E0–E9)**: Native Department of Public Enterprises (DPE) grade-level token verification and graph-native document clearance filtering.
- **Deterministic Math & Code Sandboxing**: Python calculations are executed in zero-network, memory-capped ephemeral Docker containers with automated self-healing execution loops.
- **Industrial GraphRAG**: Combines Neo4j knowledge graphs with hybrid vector indexing (`BAAI/bge-large-en-v1.5`) for multi-hop entity reasoning across P&ID schematics, OISD safety standards, and operating manuals.
- **Chief Engineer Staging & Merkle Audit**: Generates production-ready PSU Approval Notes (`.docx`) and Active Calculation Workbooks (`.xlsx`) locked behind a SHA-256 Merkle audit trail and a 1-click sovereign sign-off console.

---

## 🏛️ System Architecture

<p align="center">
  <img src="docs/architecture.png" alt="Sovereign Air-Gapped AI Workbench Architecture" width="100%" />
</p>

The end-to-end architecture is divided into three distinct, fail-safe operational stages:

<details>
<summary><b>📊 Click to view / edit Raw Mermaid Flowchart</b></summary>

```mermaid
flowchart TD
    %% STAGE 1: INGESTION, DPE RBAC & DAG PLANNING
    subgraph STAGE_1 ["STAGE 1: INGESTION, DPE RBAC & DAG PLANNING"]
        style STAGE_1 fill:#f8fafc,stroke:#94a3b8,stroke-width:2px,stroke-dasharray: 4 4

        SRC["<b>1. Ingestion Sources</b><br/>• Desktop Client UI: React / WebSockets<br/>• Confidential scanned blueprints & P&ID drawings"]
        RBAC["<b>2. RBAC & Policy Pre-Processing</b><br/>• Zero-Trust grade-level access control<br/>• E0–E9 clearance tokens<br/>• NCIIPC & CERT-In PII redaction<br/>• LangGraph DAG task decomposition"]
        DEC_1{"<b>Decision 1</b><br/>DPE Clearance &<br/>Schema Valid?"}
        
        DENIED["<b>Access Denied</b><br/>Log Security Incident & Abort"]
        VALID["<b>Task Validated</b><br/>Emit DAG Job UUID"]

        SRC --> RBAC
        RBAC --> DEC_1
        DEC_1 -- "No" --> DENIED
        DEC_1 -- "Yes" --> VALID
    end

    %% STAGE 2: MULTI-AGENT SWARM & MCP SANDBOX
    subgraph STAGE_2 ["STAGE 2: MULTI-AGENT SWARM & MCP SANDBOX"]
        style STAGE_2 fill:#f1f5f9,stroke:#64748b,stroke-width:2px,stroke-dasharray: 4 4

        ROUTER["<b>3. Dynamic Model Router & DAG Dispatcher</b><br/>• Ollama / vLLM GPU Manager<br/>• 4-Bit Auto-Swapper on Local GPU<br/>• Dispatches tasks to specialized agents"]
        
        subgraph AGENT_SWARM ["Specialized Local Agent Swarm"]
            style AGENT_SWARM fill:#ede9fe,stroke:#8b5cf6,stroke-width:1.5px
            VISION["<b>Vision Agent</b><br/><i>Qwen2.5-VL</i><br/>Native P&ID & Image Parsing"]
            CODER["<b>Code & Math Agent</b><br/><i>Qwen2.5-Coder-7B</i><br/>ASME & Engineering Math"]
            GRAPHRAG["<b>Hybrid GraphRAG Agent</b><br/><i>ChromaDB / Neo4j</i><br/>Multi-hop Entity Reasoning"]
            SYNTH_AGENT["<b>Deliverable Synth Agent</b><br/><i>Qwen2.5-7B</i><br/>Official Bureaucratic Formatter"]
        end

        MCP["<b>MCP Server (JSON-RPC Interface)</b><br/>Standardized Tool Context Protocol"]

        subgraph AIR_GAP_ENV ["Air-Gapped Sandbox Environment"]
            style AIR_GAP_ENV fill:#e0f2fe,stroke:#0284c7,stroke-width:1.5px
            SANDBOX["<b>5. Ephemeral Docker Sandbox</b><br/>• Isolated Docker Python Container<br/>• Zero-Network / Memory Capped (512MB)<br/>• OISD / ASME Physics Guardrails"]
            LOCAL_DATA["<b>Local Data & Knowledge</b><br/>• Neo4j Knowledge Graph & Hybrid Vectors<br/>• OISD / SOP Manuals & Standards<br/>• Sovereign Local-Only Retrieval"]
            ART_GEN["<b>Artifact Generator</b><br/>• python-docx + openpyxl<br/>• .docx and .xlsx output<br/>• Staging inspection cache"]
        end

        DEC_2{"<b>Decision 2</b><br/>Calculations Valid &<br/>Safety Margins Passed?"}
        HEAL["<b>Self-Healing Loop</b><br/>Stderr trace fed back to Coder Agent"]
        VERIFIED["<b>100% Verified Technical Output</b><br/>Zero-Hallucination Confirmed"]

        VALID --> ROUTER
        ROUTER --> VISION & CODER & GRAPHRAG & SYNTH_AGENT
        
        VISION & CODER & GRAPHRAG & SYNTH_AGENT <--> MCP
        MCP <--> SANDBOX & LOCAL_DATA & ART_GEN

        SANDBOX --> DEC_2
        DEC_2 -- "No / Error" --> HEAL
        HEAL --> CODER
        DEC_2 -- "Yes" --> VERIFIED
    end

    %% STAGE 3: SYNTHESIS, REVIEW & MERKLE AUDIT
    subgraph STAGE_3 ["STAGE 3: SYNTHESIS, REVIEW & MERKLE AUDIT"]
        style STAGE_3 fill:#f8fafc,stroke:#94a3b8,stroke-width:2px,stroke-dasharray: 4 4

        ENGINE["<b>6. Deliverable Synthesis Engine</b><br/>• DeepSeek-R1-8B / Qwen2.5<br/>• Official bureaucratic note formatter<br/>• Binary builders: python-docx + openpyxl<br/>• Generates PSU Approval Notes & Workbooks"]
        
        REVIEW["<b>7. Engineering Staging & Chief Engineer Review</b><br/>• Bounding Box Visualizer for Schematics<br/>• Safety Margin Inspector & Unit Cross-Verifier<br/>• Review Console: <code>PENDING_SIGNATURE</code><br/>• 1-Click Sovereign Sign-Off & Approval"]
        
        AUDIT["<b>8. Immutable Audit & Air-Gapped Deliverables</b><br/>• SHA-256 Merkle Audit Chain<br/>• Appends User Clearance, Execution Code & Logs<br/>• Official PSU Approval Note (.docx)<br/>• Active Calculation Workbook (.xlsx)"]

        VERIFIED --> ENGINE
        ENGINE --> REVIEW
        REVIEW --> AUDIT
    end

    %% Node styling
    style SRC fill:#0284c7,stroke:#0369a1,color:#ffffff
    style RBAC fill:#0f766e,stroke:#115e59,color:#ffffff
    style DEC_1 fill:#c2410c,stroke:#9a3412,color:#ffffff
    style DENIED fill:#991b1b,stroke:#7f1d1d,color:#ffffff
    style VALID fill:#065f46,stroke:#064e3b,color:#ffffff
    style ROUTER fill:#0f766e,stroke:#115e59,color:#ffffff
    style VISION fill:#7c3aed,stroke:#6d28d9,color:#ffffff
    style CODER fill:#7c3aed,stroke:#6d28d9,color:#ffffff
    style GRAPHRAG fill:#7c3aed,stroke:#6d28d9,color:#ffffff
    style SYNTH_AGENT fill:#7c3aed,stroke:#6d28d9,color:#ffffff
    style MCP fill:#d97706,stroke:#b45309,color:#ffffff
    style SANDBOX fill:#991b1b,stroke:#7f1d1d,color:#ffffff
    style LOCAL_DATA fill:#991b1b,stroke:#7f1d1d,color:#ffffff
    style ART_GEN fill:#991b1b,stroke:#7f1d1d,color:#ffffff
    style DEC_2 fill:#c2410c,stroke:#9a3412,color:#ffffff
    style HEAL fill:#991b1b,stroke:#7f1d1d,color:#ffffff
    style VERIFIED fill:#065f46,stroke:#064e3b,color:#ffffff
    style ENGINE fill:#7c3aed,stroke:#6d28d9,color:#ffffff
    style REVIEW fill:#0284c7,stroke:#0369a1,color:#ffffff
    style AUDIT fill:#0f766e,stroke:#115e59,color:#ffffff
```
</details>

---

## 🔄 Detailed Architectural Breakdown

### 🔹 Stage 1: Ingestion, DPE RBAC & DAG Planning
1. **Ingestion Sources**:
   - **Frontend Workbench UI**: Built with React 18, Vite, Lucide Icons, and real-time WebSockets for streaming agent logs and DAG routing states.
   - **Confidential Documents**: Accepts scanned engineering blueprints, P&ID schematics, standard operating procedures (SOPs), and OISD safety compliance guidelines (PDF, TXT, CSV, MD).
2. **RBAC & Policy Pre-Processing**:
   - **Zero-Trust Token Extraction**: Resolves caller clearance grade (E0–E9) against the SQL database.
   - **PII & Data Redaction**: Strips sensitive personal markers according to **NCIIPC & CERT-In** guidelines before prompt handoff.
   - **LangGraph Supervisor Decomposition**: LangGraph decomposes user objectives into a deterministic Directed Acyclic Graph (DAG) of micro-tasks.
3. **Decision Gate 1 (Clearance & Schema Validation)**:
   - Evaluates if the authenticated user has sufficient privileges for the target workspace and document domain.
   - ❌ **Fail**: Access denied, security event logged in the immutable audit registry, workflow immediately halted.
   - ✅ **Pass**: Emits unique `DAG Job UUID` and forwards execution payload to Stage 2.

---

### 🔹 Stage 2: Multi-Agent Swarm & MCP Sandbox
1. **Dynamic Model Router & DAG Dispatcher**:
   - Manages local LLM inference over Ollama / vLLM.
   - Utilizes low-VRAM model swapping (`keep_alive=0`) to run 7B–32B parameter models sequentially on local workstation/server GPUs without memory overflow.
2. **Specialized Local Agent Swarm**:
   - 👁️ **Vision Agent (`Qwen2.5-VL`)**: Performs optical recognition on P&ID blueprints, piping tags, valve numbers, and technical schematics.
   - 💻 **Code & Math Agent (`Qwen2.5-Coder-7B`)**: Generates rigorous Python code for ASME pressure vessel equations, hydraulic calculations, and thermal safety margins.
   - 🧠 **Hybrid GraphRAG Agent (`Neo4j` + `BGE-Large`)**: Executes multi-hop entity traversal and vector search on industrial SOPs and compliance manuals with graph-native clearance filtering (`node.clearance_level <= user_clearance`).
   - 📝 **Deliverable Synth Agent (`Qwen2.5-7B` / `DeepSeek-R1-8B`)**: Formats calculation findings and engineering memos into official PSU administrative formats.
3. **Model Context Protocol (MCP) Server**:
   - Centralized JSON-RPC stdio server exposing sandboxed tools to all agents in the swarm.
4. **Air-Gapped Sandbox Environment**:
   - **Ephemeral Docker Sandbox**: Spins up an isolated `python:3.10-slim` container with `network_mode="none"`, `mem_limit="512m"`, and `cpu_quota=50000`. Auto-destroys upon execution completion.
   - **Local Knowledge Base**: In-memory / containerized Neo4j with APOC plugins, storing verified entities (`Document`, `Component`, `Standard`, `Parameter`).
   - **Artifact Generator**: Generates formatted `.docx` files and `.xlsx` workbooks using `python-docx` and `openpyxl`.
5. **Decision Gate 2 (Calculation Validity & Safety Margin Checks)**:
   - Validates execution outputs against engineering safety thresholds (e.g., maximum allowable working pressure, thermal tolerances).
   - 🔁 **Self-Healing Loop**: If Python code encounters syntax errors or runtime exceptions, the `stderr` trace is fed back into `Qwen2.5-Coder` for automatic repair and re-execution (up to 5 recursions).
   - ✅ **Verified Output**: 100% verified, non-hallucinatory calculation results passed to Stage 3.

---

### 🔹 Stage 3: Synthesis, Review & Merkle Audit
1. **Deliverable Synthesis Engine**:
   - Assembles final engineering notes, calculation summaries, and referenced compliance clauses into official PSU templates.
2. **Engineering Staging & Chief Engineer Review**:
   - Renders bounding-box overlays on P&ID blueprints in the UI.
   - Displays real-time status as `PENDING_SIGNATURE`.
   - Requires explicit 1-Click Sovereign Sign-Off by authorized personnel (E6+ Chief Engineer / DGM).
3. **Immutable Audit & Air-Gapped Deliverables**:
   - Computes a cryptographic **SHA-256 Merkle Chain** linking the user's identity, timestamp, raw input prompt, intermediate code, execution logs, and final document checksum.
   - Delivers validated `.docx` PSU Approval Notes and `.xlsx` calculation workbooks ready for air-gapped archival.

---

## 👥 Role-Based Access Control (RBAC) Matrix

The workbench implements a Zero-Trust role hierarchy patterned after Indian Public Sector Undertaking (PSU) grade-levels:

| Grade | Executive Designation | Typical Roles | Clearance Level | Permitted Operations |
| :--- | :--- | :--- | :---: | :--- |
| **E0–E1** | Assistant Engineer / Officer | Field Operator, Lab Tech | `Level 1` | `VIEW`, basic drafting, local sandbox tests |
| **E2–E3** | Senior Engineer / Officer | Maintenance Eng, Shift In-Charge | `Level 2` | `VIEW`, `CREATE`, `UPDATE` operational logs |
| **E4–E5** | Manager / Senior Manager | Unit Operations Lead, Safety Manager | `Level 3` | `VIEW`, `CREATE`, `UPDATE`, confidential SOP access |
| **E6–E7** | Chief Engineer / DGM | Technical Authority, Plant Head | `Level 4` | `VIEW`, `CREATE`, `UPDATE`, `APPROVE`, `EXPORT` |
| **E8–E9** | GM / Executive Director / CMD | Director Technical, Super Admin | `Level 5` | Full system governance, `AUDIT`, `ROLE_MANAGE`, `ADMIN` |

---

## 🗂️ Repository Structure

```tree
Neural-Ninjas-SIH26/
├── README.md                           # Comprehensive documentation & architecture specification
├── .gitignore                          # Git ignore rules for Python, Node, Vite, and DB files
├── Backend/
│   ├── requirements.txt                # Python backend dependencies
│   ├── test_mcp.py                     # Standalone validation script for MCP JSON-RPC server
│   ├── graph_rag_implement.md          # Implementation guidelines for Neo4j GraphRAG engine
│   ├── database/
│   │   ├── db.py                       # SQLAlchemy engine & SQLite / PostgreSQL session factory
│   │   ├── models.py                   # Data models (Users, Roles, Departments, Permissions, Chats, Files)
│   │   └── seed_rbac.py                # Database seeder for PSU departments, roles, and permissions
│   ├── mcp_server/
│   │   ├── server.py                   # FastMCP / JSON-RPC stdio tool provider
│   │   └── tools/
│   │       ├── sandbox.py              # Ephemeral Docker container execution engine
│   │       ├── rag.py                  # Hybrid GraphRAG search tool with native RBAC filtering
│   │       └── artifacts.py            # .docx and .xlsx file generation tools
│   ├── orchestrator/
│   │   ├── api.py                      # FastAPI REST application & CORS middleware
│   │   ├── graph.py                    # LangGraph multi-agent swarm & Supervisor state machine
│   │   ├── mcp_client.py               # Async stdio client connecting Orchestrator to MCP Server
│   │   └── routers/
│   │       ├── auth.py                 # JWT authentication & employee login/registration endpoints
│   │       └── files.py                # File upload, clearance tagging & document management
│   └── scripts/
│       ├── ingest.py                   # Document loader, LLMGraphTransformer & Neo4j vector indexer
│       └── test_e2e_rbac.py            # End-to-end integration test for RBAC clearance boundaries
└── Frontend/
    ├── package.json                    # Node.js dependencies (React, Vite, Lucide Icons)
    ├── vite.config.js                  # Vite configuration & dev server setup
    ├── index.html                      # HTML5 entrypoint
    ├── app.js                          # Standalone demo client
    ├── style.css                       # Global modern UI stylesheets
    └── src/
        ├── main.jsx                    # React application root
        ├── index.css                   # Tailwind / CSS tokens & dark glassmorphism styling
        ├── App.jsx                     # Master application container & routing state
        └── components/
            ├── Header.jsx              # Top navigation bar with active model indicator & user badge
            ├── Sidebar.jsx             # Navigation sidebar (Workspaces, Chat, Employees, Access Control)
            ├── LoginPage.jsx           # PSU Employee portal login & credential verification
            ├── WorkspacesView.jsx      # Workspace selector & project metadata cards
            ├── ChatView.jsx            # Multi-agent chat interface with live DAG routing timeline
            ├── EmployeesView.jsx       # Employee directory with department and grade filters
            ├── AccessControlView.jsx   # Role and permission matrix configuration console
            ├── ModelUploadView.jsx     # Local LLM model registry & GGUF / Ollama swapper
            ├── NewWorkspaceModal.jsx   # Modal for provisioning new engineering review projects
            └── AuxiliaryViews.jsx      # Tasks, Knowledge Base & Active Swarm agent monitors
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, Lucide Icons, CSS3 | High-performance air-gapped UI, live streaming chat, dynamic routing visualizer |
| **Backend Framework** | FastAPI, Uvicorn, Pydantic v2 | High-throughput async REST API and session management |
| **Agent Orchestration** | LangGraph, LangChain, MCP SDK | State graph management, multi-agent delegation, and tool handoffs |
| **Local LLM Inference** | Ollama / vLLM (4-bit & 8-bit quantized) | GPU execution of `Qwen2.5`, `Qwen2.5-Coder`, `Qwen2.5-VL`, `Llama3.1` |
| **Sandboxed Code Execution**| Docker Python 3.10-slim (`network=none`) | Isolated mathematical calculations, ASME safety validation, and data verification |
| **Knowledge Engine** | Neo4j 5.20 (APOC) + `bge-large-en-v1.5` | Graph-native document relationships, entity knowledge graphs, and hybrid vector search |
| **Document Generation** | `python-docx`, `openpyxl` | Production generation of PSU Approval Notes and Excel calculation workbooks |
| **Security & Persistence**| SQLAlchemy, SQLite/PostgreSQL, PyJWT, bcrypt | Zero-Trust authentication, clearance verification, and tamper-resistant audit logs |

---

## 🚀 Installation & Setup Guide

### 📋 Prerequisites
1. **Operating System**: Windows 10/11, Linux (Ubuntu 22.04+), or macOS with Docker Desktop.
2. **Python**: Version `3.10` or higher.
3. **Node.js**: Version `18.0.0` or higher.
4. **Docker**: Docker Engine running locally with Docker CLI accessible.
5. **Ollama**: Installed and running locally (`http://localhost:11434`).

---

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/BibinSanju/Neural-Ninjas-SIH26.git
cd Neural-Ninjas-SIH26

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Python Backend Dependencies
```bash
pip install -r Backend/requirements.txt
```

### Step 3: Pull Local Models in Ollama
Ensure Ollama is running, then pull the required specialist models:
```bash
# Supervisor & General Reasoning
ollama pull qwen2.5:latest

# Code, Math & ASME Verification
ollama pull qwen2.5-coder:latest

# Graph Extraction & Entity Analysis
ollama pull llama3.1:latest

# (Optional) Deliverable Synthesis & Deep Reasoning
ollama pull mistral:latest
```

### Step 4: Start Neo4j Graph Database (Docker)
Run the official Neo4j container with APOC plugins enabled for GraphRAG:
```bash
docker run -d \
  --name neo4j-graphrag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/industrial_password_2026 \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.20.0
```

### Step 5: Seed Database & RBAC Roles
Initialize the database tables and populate the default PSU departments, roles, and clearance levels:
```bash
python Backend/database/seed_rbac.py
```

### Step 6: Ingest Documents into GraphRAG (Optional)
To ingest a technical manual or P&ID specification with a specific clearance level:
```bash
python Backend/scripts/ingest.py \
  --filepath "path/to/industrial_sop.pdf" \
  --doc_id "SOP-OISD-118" \
  --filename "OISD-118-Safety-Standard.pdf" \
  --clearance 3
```

### Step 7: Launch Backend API & Orchestrator
```bash
uvicorn Backend.orchestrator.api:app --reload --port 8000
```
*API will be available at:* `http://localhost:8000`  
*Interactive Swagger Documentation:* `http://localhost:8000/docs`

### Step 8: Launch Frontend Workbench
In a separate terminal:
```bash
cd Frontend
npm install
npm run dev
```
*Frontend Workbench will be accessible at:* `http://localhost:5173`

---

## 🔒 Security, Compliance & Air-Gapping

1. **Air-Gap Compliance (Zero Outbound Traffic)**:
   - All LLM inference is performed locally via Ollama.
   - Ephemeral Docker execution containers run with `--network none` to prevent socket creation, DNS requests, and outbound telemetry.
2. **Deterministic Computation**:
   - Math and ASME equations are never solved inside LLM text generation. 
   - The Code Agent writes pure Python scripts executed in the Docker sandbox; results are verified against boundary conditions before inclusion in deliverables.
3. **Graph-Native Clearance Enforcement**:
   - Document chunks in Neo4j are stamped with `clearance_level` integer properties.
   - Vector similarity search uses database-level metadata filters (`filter={"clearance_level": {"$lte": user_clearance}}`). Users without sufficient clearance cannot retrieve or infer restricted data.
4. **Tamper-Proof Audit Logging**:
   - Every multi-agent handoff, tool execution, user clearance check, and sign-off is logged with UTC timestamps and SHA-256 checksums in the local database.

---

## 🧪 Testing & Verification

### 1. Test MCP Server & Tools
Verify that the JSON-RPC stdio MCP server can communicate and execute tools:
```bash
python Backend/test_mcp.py
```

### 2. Run End-to-End RBAC Security Test
Verify that clearance boundaries prevent unauthorized access while allowing authorized execution:
```bash
python Backend/scripts/test_e2e_rbac.py
```

---

## 👥 Contributors
Developed by **Team Neural Ninjas** for Smart India Hackathon (SIH 2026).

---

## 📜 License
Proprietary and Confidential. Developed for industrial engineering infrastructure, PSU security benchmarks, and hackathon evaluation.
