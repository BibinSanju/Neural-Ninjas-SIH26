import React, { useState } from 'react';
import { Lock, FileText, Folder, Check, X, Shield, Save } from 'lucide-react';

export default function AccessControlView({ employees, files, setFilePermissions, filePermissions }) {
  const [saveSuccess, setSaveSuccess] = useState(false);

  const togglePermission = (empId, fileId) => {
    setFilePermissions(prev => {
      const current = prev[empId] || [];
      const hasAccess = current.includes(fileId);
      const updated = hasAccess 
        ? current.filter(id => id !== fileId) 
        : [...current, fileId];
      return { ...prev, [empId]: updated };
    });
  };

  const handleSaveChanges = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>File Access Permission Matrix</h1>
          <p>Decide and authorize which employees can view, mount, and query sensitive files & code repositories.</p>
        </div>
        <button className="btn-primary" onClick={handleSaveChanges}>
          <Save size={16} />
          <span>{saveSuccess ? 'Permissions Saved!' : 'Save Access Policy'}</span>
        </button>
      </div>

      {/* Access Control Table Matrix */}
      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>System Role</th>
              {files.map(file => (
                <th key={file.id} style={{ textAlign: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <span style={{ textTransform: 'none', fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#fff' }}>
                      {file.name}
                    </span>
                    <span style={{ fontSize: '10px', color: '#64748b' }}>{file.category}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {employees.map(emp => {
              const empPerms = filePermissions[emp.id] || [];
              return (
                <tr key={emp.id}>
                  <td>
                    <div style={{ fontWeight: '600', color: '#fff' }}>{emp.name}</div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>{emp.department}</div>
                  </td>
                  <td>
                    <span className={`role-pill ${emp.systemRole.toLowerCase()}`}>
                      {emp.systemRole}
                    </span>
                  </td>
                  {files.map(file => {
                    const isGranted = empPerms.includes(file.id);
                    return (
                      <td key={file.id} style={{ textAlign: 'center' }}>
                        <button
                          style={{
                            width: '36px', height: '36px', borderRadius: '8px',
                            border: isGranted ? '1px solid #10b981' : '1px solid #242736',
                            backgroundColor: isGranted ? 'rgba(16, 185, 129, 0.15)' : 'rgba(26, 29, 43, 0.5)',
                            color: isGranted ? '#10b981' : '#64748b',
                            cursor: 'pointer',
                            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                            transition: 'all 0.15s ease'
                          }}
                          onClick={() => togglePermission(emp.id, file.id)}
                          title={isGranted ? 'Click to Revoke Access' : 'Click to Grant Access'}
                        >
                          {isGranted ? <Check size={18} /> : <X size={16} />}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
