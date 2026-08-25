import React, { useState } from 'react';
import { Plus, Search, MoreVertical } from 'lucide-react';

export default function WorkspacesView({ workspaces, openWorkspace, onOpenModal }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredWorkspaces = workspaces.filter(ws => {
    const matchesQuery = ws.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          ws.desc.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || ws.status.toLowerCase() === statusFilter;
    return matchesQuery && matchesStatus;
  });

  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Workspaces</h1>
          <p>Organize AI agents, documents, tools and conversations by project context.</p>
        </div>
        <button className="btn-primary" onClick={onOpenModal}>
          <Plus size={18} />
          <span>New Workspace</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-search">
          <Search size={16} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search workspaces..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-dropdowns">
          <select 
            className="custom-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Status: All</option>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="archived">Archived</option>
          </select>
          <select className="custom-select">
            <option value="recent">Sort: Recent</option>
            <option value="name">Sort: Name</option>
            <option value="agents">Sort: Agents</option>
          </select>
        </div>
      </div>

      {/* Workspaces Cards Grid (Matching Reference Image 2) */}
      <div className="workspaces-grid">
        {filteredWorkspaces.map(ws => (
          <div key={ws.id} className="workspace-card">
            <div>
              <div className="card-top">
                <h3 className="card-title">{ws.title}</h3>
                <button className="card-menu-btn"><MoreVertical size={16} /></button>
              </div>
              <p className="card-desc">{ws.desc}</p>
            </div>
            <div>
              <div className="card-stats-row">
                <div className="stat-item">
                  <span className="stat-label">AGENTS</span>
                  <span className="stat-value">{ws.agentsCount}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">RESOURCES</span>
                  <span className="stat-value">{ws.resourcesCount}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">ACTIVITY</span>
                  <span className="stat-value">{ws.activity}</span>
                </div>
              </div>
              <div className="card-footer">
                <div className={`status-badge ${ws.status.toLowerCase()}`}>
                  <span className="status-dot"></span>
                  <span>{ws.status}</span>
                </div>
                <button className="btn-open-ws" onClick={() => openWorkspace(ws.id, ws.title)}>
                  Open
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
