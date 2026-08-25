import React, { useState } from 'react';
import { X } from 'lucide-react';

export default function NewWorkspaceModal({ isOpen, onClose, onSave }) {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return alert('Please enter a workspace title.');
    onSave(title, desc);
    setTitle('');
    setDesc('');
    onClose();
  };

  return (
    <div className="modal-backdrop active">
      <div className="modal-window">
        <div className="modal-header">
          <h3 className="modal-title">Create New Workspace</h3>
          <button className="icon-btn" onClick={onClose}><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '14px' }}>
            <label>Workspace Title</label>
            <input 
              type="text" 
              placeholder="e.g. Vulnerability Audit Q3" 
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label>Description</label>
            <textarea 
              rows={3} 
              placeholder="Brief explanation of the project context..."
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary">Create Workspace</button>
          </div>
        </form>
      </div>
    </div>
  );
}
