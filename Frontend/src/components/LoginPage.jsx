import React, { useState } from 'react';
import { Shield, Lock, Mail, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('sarah.j@sovereign.ai');
  const [password, setPassword] = useState('admin123');
  const [selectedRole, setSelectedRole] = useState('admin');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return alert('Please enter your email and password.');

    const name = selectedRole === 'admin' ? 'Sarah Jenkins (Admin)' : 'David Miller (User)';
    const backendUsername = selectedRole === 'admin' ? 'admin_test' : 'operator_test';
    const backendPassword = 'password';

    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: backendUsername, password: backendPassword })
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('jwt_token', data.access_token);
        onLogin({
          email,
          name,
          role: selectedRole,
          department: selectedRole === 'admin' ? 'SecOps & Architecture' : 'Engineering'
        });
      } else {
        alert('Backend authentication failed. Please ensure the backend API is running.');
      }
    } catch (err) {
      alert('Network error connecting to backend API.');
    }
  };

  const handleQuickDemo = async (role) => {
    if (role === 'admin') {
      setEmail('sarah.j@sovereign.ai');
      setPassword('admin123');
      setSelectedRole('admin');
    } else {
      setEmail('david.m@sovereign.ai');
      setPassword('user123');
      setSelectedRole('user');
    }
    
    // Auto submit using the synthetic event approach, or just call the logic
    const backendUsername = role === 'admin' ? 'admin_test' : 'operator_test';
    const backendPassword = 'password';
    
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: backendUsername, password: backendPassword })
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('jwt_token', data.access_token);
        
        onLogin({
          email: role === 'admin' ? 'sarah.j@sovereign.ai' : 'david.m@sovereign.ai',
          name: role === 'admin' ? 'Sarah Jenkins (Admin)' : 'David Miller (User)',
          role: role,
          department: role === 'admin' ? 'SecOps & Architecture' : 'Engineering'
        });
      } else {
        alert('Backend authentication failed. Please ensure the backend API is running.');
      }
    } catch (err) {
      alert('Network error connecting to backend API.');
    }
  };

  return (
    <div className="login-backdrop">
      <div className="login-card">
        <div className="login-brand-header">
          <div className="brand-logo" style={{ width: '48px', height: '48px', margin: '0 auto 12px auto' }}>
            <Shield size={28} />
          </div>
          <h1 className="login-title">Sovereign AI Workbench</h1>
          <p className="login-subtitle">Confidential Enterprise AI Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Work Email</label>
            <div className="input-with-icon">
              <Mail size={16} className="input-icon" />
              <input 
                type="email" 
                placeholder="name@sovereign.ai" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>
            <div className="input-with-icon">
              <Lock size={16} className="input-icon" />
              <input 
                type="password" 
                placeholder="••••••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Account Role</label>
            <div className="role-selection-grid">
              <div 
                className={`role-select-box ${selectedRole === 'admin' ? 'active' : ''}`}
                onClick={() => setSelectedRole('admin')}
              >
                <ShieldCheck size={18} />
                <div>
                  <div className="title">Administrator</div>
                  <div className="sub">Full employee & model controls</div>
                </div>
              </div>

              <div 
                className={`role-select-box ${selectedRole === 'user' ? 'active' : ''}`}
                onClick={() => setSelectedRole('user')}
              >
                <UserCheck size={18} />
                <div>
                  <div className="title">Standard User</div>
                  <div className="sub">Access workspace & use models</div>
                </div>
              </div>
            </div>
          </div>

          <button type="submit" className="btn-login">
            <span>Sign In to Workbench</span>
            <ArrowRight size={16} />
          </button>
        </form>

        <div className="demo-login-divider">
          <span>Or Quick Demo Login As</span>
        </div>

        <div className="demo-btns-row">
          <button className="btn-demo admin" onClick={() => handleQuickDemo('admin')}>
            <ShieldCheck size={16} />
            <span>Login as Admin</span>
          </button>
          <button className="btn-demo user" onClick={() => handleQuickDemo('user')}>
            <UserCheck size={16} />
            <span>Login as User</span>
          </button>
        </div>
      </div>
    </div>
  );
}
