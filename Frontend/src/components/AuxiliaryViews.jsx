import React from 'react';

export function TasksView() {
  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Automated Tasks</h1>
          <p>Monitor Docker sandboxed code runs, ChromaDB indexing, and artifact creations.</p>
        </div>
      </div>
      <div className="workspaces-grid">
        <div className="workspace-card">
          <h3 className="card-title">Docker Sandbox Run #1042</h3>
          <p className="card-desc">Executing Python benchmark suite in python:3.10-slim air-gapped container.</p>
          <div className="status-badge active"><span className="status-dot"></span><span>COMPLETED</span></div>
        </div>
        <div className="workspace-card">
          <h3 className="card-title">Word Document Generator</h3>
          <p className="card-desc">Created architecture_approval_note.docx with executive summary.</p>
          <div className="status-badge active"><span className="status-dot"></span><span>COMPLETED</span></div>
        </div>
      </div>
    </div>
  );
}

export function KnowledgeView() {
  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Knowledge Base (RAG)</h1>
          <p>Vector index powered by ChromaDB & BAAI/bge-large-en-v1.5 embeddings.</p>
        </div>
      </div>
      <div className="workspaces-grid">
        <div className="workspace-card">
          <h3 className="card-title">Internal System Manuals</h3>
          <p className="card-desc">Vector collection: internal_manuals (48 chunks indexed).</p>
          <div className="status-badge active"><span className="status-dot"></span><span>PERSISTED</span></div>
        </div>
      </div>
    </div>
  );
}

export function AgentsView({ activeModel }) {
  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>AI Agents</h1>
          <p>Configure models and tool capabilities for autonomous execution.</p>
        </div>
      </div>
      <div className="workspaces-grid">
        <div className="workspace-card">
          <h3 className="card-title">SecOps Analyst</h3>
          <p className="card-desc">Active Model: {activeModel} via Ollama. Tools: Sandbox, RAG, Word Gen.</p>
          <div className="status-badge active"><span className="status-dot"></span><span>READY</span></div>
        </div>
        <div className="workspace-card">
          <h3 className="card-title">Arch-Builder</h3>
          <p className="card-desc">Model: Llama-3-70B via Ollama. Tools: Architectural Diagrammer.</p>
          <div className="status-badge active"><span className="status-dot"></span><span>READY</span></div>
        </div>
      </div>
    </div>
  );
}
