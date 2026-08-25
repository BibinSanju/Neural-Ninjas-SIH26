import React from 'react';
import { 
  Cpu, LayoutGrid, MessageSquare, CheckSquare, Database, 
  Bot, Users, Lock, UploadCloud, HelpCircle, LogOut 
} from 'lucide-react';

export default function Sidebar({ activeView, setActiveView, userRole, onLogout }) {
  return (
    <nav className="sidebar-nav">
      <div className="sidebar-top">
        <div className="sidebar-project-header">
          <div className="project-icon">
            <Cpu size={18} />
          </div>
          <div className="project-info-text">
            <div className="title">Project Alpha</div>
            <div className="sub">Confidential Engineering</div>
          </div>
        </div>

        <div className="nav-menu">
          <div className="nav-section-title">General</div>
          
          <div 
            className={`nav-item ${activeView === 'workspaces' ? 'active' : ''}`}
            onClick={() => setActiveView('workspaces')}
          >
            <div className="nav-item-left">
              <LayoutGrid size={18} className="nav-icon" />
              <span>Workspace</span>
            </div>
          </div>

          <div 
            className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            <div className="nav-item-left">
              <MessageSquare size={18} className="nav-icon" />
              <span>Chat</span>
            </div>
          </div>

          <div 
            className={`nav-item ${activeView === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveView('tasks')}
          >
            <div className="nav-item-left">
              <CheckSquare size={18} className="nav-icon" />
              <span>Tasks</span>
            </div>
          </div>

          <div 
            className={`nav-item ${activeView === 'knowledge' ? 'active' : ''}`}
            onClick={() => setActiveView('knowledge')}
          >
            <div className="nav-item-left">
              <Database size={18} className="nav-icon" />
              <span>Knowledge</span>
            </div>
          </div>

          <div 
            className={`nav-item ${activeView === 'agents' ? 'active' : ''}`}
            onClick={() => setActiveView('agents')}
          >
            <div className="nav-item-left">
              <Bot size={18} className="nav-icon" />
              <span>Agents</span>
            </div>
          </div>

          {/* ADMIN ONLY MENU ITEMS */}
          <div className="nav-section-title" style={{ marginTop: '12px' }}>
            {userRole === 'admin' ? 'Admin Management' : 'Model Access'}
          </div>

          {userRole === 'admin' && (
            <>
              <div 
                className={`nav-item ${activeView === 'employees' ? 'active' : ''}`}
                onClick={() => setActiveView('employees')}
              >
                <div className="nav-item-left">
                  <Users size={18} className="nav-icon" />
                  <span>Employees</span>
                </div>
                <span className="admin-tag-badge">ADMIN</span>
              </div>

              <div 
                className={`nav-item ${activeView === 'access-control' ? 'active' : ''}`}
                onClick={() => setActiveView('access-control')}
              >
                <div className="nav-item-left">
                  <Lock size={18} className="nav-icon" />
                  <span>Access Control</span>
                </div>
                <span className="admin-tag-badge">ADMIN</span>
              </div>
            </>
          )}

          <div 
            className={`nav-item ${activeView === 'model-upload' ? 'active' : ''}`}
            onClick={() => setActiveView('model-upload')}
          >
            <div className="nav-item-left">
              <UploadCloud size={18} className="nav-icon" />
              <span>{userRole === 'admin' ? 'Upload Model' : 'Model Hub'}</span>
            </div>
            {userRole === 'admin' && <span className="admin-tag-badge">ADMIN</span>}
          </div>
        </div>
      </div>

      <div className="sidebar-bottom">
        <div className="nav-item">
          <div className="nav-item-left">
            <HelpCircle size={18} className="nav-icon" />
            <span>Help</span>
          </div>
        </div>
        <div className="nav-item" onClick={onLogout}>
          <div className="nav-item-left">
            <LogOut size={18} className="nav-icon" />
            <span>Logout</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
