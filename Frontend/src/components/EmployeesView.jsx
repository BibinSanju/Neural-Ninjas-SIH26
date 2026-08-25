import React, { useState } from 'react';
import { Users, Search, Filter, ShieldCheck, User, Key, CheckCircle, AlertTriangle } from 'lucide-react';

export default function EmployeesView({ employees, setEmployees }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [deptFilter, setDeptFilter] = useState('all');

  const filteredEmployees = employees.filter(emp => {
    const matchesSearch = emp.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          emp.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          emp.role.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDept = deptFilter === 'all' || emp.department === deptFilter;
    return matchesSearch && matchesDept;
  });

  const toggleEmployeeRole = (id) => {
    setEmployees(prev => prev.map(emp => {
      if (emp.id === id) {
        const newRole = emp.systemRole === 'Admin' ? 'User' : 'Admin';
        return { ...emp, systemRole: newRole };
      }
      return emp;
    }));
  };

  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Employee Management Directory</h1>
          <p>Admin panel to inspect employee credentials, assigned models, and system access levels.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-primary">
            <Users size={16} />
            <span>Add New Employee</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="filter-search">
          <Search size={16} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search employees by name, email, or role..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-dropdowns">
          <select 
            className="custom-select"
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
          >
            <option value="all">Department: All</option>
            <option value="Engineering">Engineering</option>
            <option value="SecOps">SecOps</option>
            <option value="Data Intelligence">Data Intelligence</option>
            <option value="Compliance">Compliance</option>
          </select>
        </div>
      </div>

      {/* Employees Table */}
      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Employee Name & Email</th>
              <th>Department</th>
              <th>Job Title</th>
              <th>System Role</th>
              <th>Assigned LLM Model</th>
              <th>File Access Level</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEmployees.map(emp => (
              <tr key={emp.id}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div className="user-avatar" style={{ width: '32px', height: '32px', fontSize: '11px' }}>
                      {emp.initials}
                    </div>
                    <div>
                      <div style={{ fontWeight: '600', color: '#fff' }}>{emp.name}</div>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>{emp.email}</div>
                    </div>
                  </div>
                </td>
                <td><span style={{ fontSize: '12px', color: '#94a3b8' }}>{emp.department}</span></td>
                <td><span style={{ fontSize: '13px', fontWeight: '500' }}>{emp.jobTitle}</span></td>
                <td>
                  <span className={`role-pill ${emp.systemRole.toLowerCase()}`}>
                    {emp.systemRole}
                  </span>
                </td>
                <td>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#818cf8' }}>
                    {emp.assignedModel}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '12px', color: '#cbd5e1' }}>
                    {emp.allowedFilesCount} Files Mounted
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: emp.active ? '#10b981' : '#f59e0b' }}>
                    <CheckCircle size={14} />
                    <span>{emp.active ? 'Active' : 'Suspended'}</span>
                  </div>
                </td>
                <td>
                  <button 
                    className="btn-secondary" 
                    style={{ padding: '4px 10px', fontSize: '11px' }}
                    onClick={() => toggleEmployeeRole(emp.id)}
                  >
                    Toggle Role ({emp.systemRole === 'Admin' ? 'Demote' : 'Promote'})
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
