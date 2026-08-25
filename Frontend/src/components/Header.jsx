import React from 'react';
import { Shield, Search, Bell, Settings, LogOut } from 'lucide-react';

export default function Header({ currentUser, onLogout }) {
  const isTargetAdmin = currentUser?.role === 'admin';

  return (
    <header className="top-navbar">
      <div className="brand-section">
        <div className="brand-logo">
          <Shield size={20} />
        </div>
        <span className="brand-title">Sovereign AI Workbench</span>
        <span className="brand-badge">SIH26</span>
      </div>

      <div className="top-search-bar">
        <Search size={16} className="search-icon" />
        <input type="text" placeholder="Search workspaces, agents, documents..." />
      </div>

      <div className="top-actions">
        <button className="icon-btn" title="Notifications">
          <Bell size={18} />
          <span className="btn-badge"></span>
        </button>

        <button className="icon-btn" title="Settings">
          <Settings size={18} />
        </button>

        {/* User Info Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: '6px' }}>
          <div className="user-avatar" title={currentUser?.name}>
            {isTargetAdmin ? 'AD' : 'US'}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '12.5px', fontWeight: '600', color: '#fff' }}>
              {currentUser?.name || 'User'}
            </span>
            <span className={`role-pill ${isTargetAdmin ? 'admin' : 'user'}`} style={{ fontSize: '9px', padding: '1px 6px', width: 'fit-content' }}>
              {isTargetAdmin ? 'ADMIN' : 'USER'}
            </span>
          </div>
        </div>

        <button 
          className="icon-btn" 
          title="Sign Out"
          onClick={onLogout}
          style={{ marginLeft: '8px' }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
