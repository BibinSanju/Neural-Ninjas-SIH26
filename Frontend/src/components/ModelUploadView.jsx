import React, { useState } from 'react';
import { UploadCloud, HardDrive } from 'lucide-react';

export default function ModelUploadView({ userRole, models, setModels, activeModel, setActiveModel }) {
  const [modelName, setModelName] = useState('');
  const [modelType, setModelType] = useState('GGUF');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const handleSimulateUpload = () => {
    if (userRole !== 'admin') return;
    if (!modelName) return alert('Please enter a model name.');

    setIsUploading(true);
    let progress = 0;
    const interval = setInterval(() => {
      progress += 20;
      setUploadProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setIsUploading(false);
        setUploadProgress(0);

        const newModel = {
          id: `mod-${Date.now()}`,
          name: modelName,
          format: modelType,
          size: '14.2 GB',
          params: '32B',
          status: 'Deployed (Ollama)',
          uploader: 'Admin',
          active: false
        };

        setModels(prev => [newModel, ...prev]);
        setModelName('');
        alert(`Model "${modelName}" deployed successfully to local Ollama inference engine!`);
      }
    }, 400);
  };

  return (
    <div className="workspaces-container">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>{userRole === 'admin' ? 'Model Registry & Custom Weight Uploader' : 'Available LLM Models'}</h1>
          <p>
            {userRole === 'admin' 
              ? 'Upload local open-weight models (GGUF/SafeTensors) and configure Ollama inference execution.'
              : 'Select available deployed LLM models for running local reasoning, RAG searches, and code sandboxing.'
            }
          </p>
        </div>
      </div>

      {/* Model Upload Section - ADMIN ONLY */}
      {userRole === 'admin' && (
        <div className="workspace-card" style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <UploadCloud size={24} style={{ color: 'var(--accent-purple)' }} />
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#fff' }}>Upload New Model Weights</h3>
            <span className="admin-tag-badge">ADMIN AUTHORIZED</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label>Model Name / Identifier</label>
              <input 
                type="text" 
                placeholder="e.g. Qwen2.5-Coder-32B-Instruct" 
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Format</label>
              <select className="custom-select" value={modelType} onChange={(e) => setModelType(e.target.value)}>
                <option value="GGUF">GGUF (Quantized Q4_K_M)</option>
                <option value="SafeTensors">SafeTensors (FP16)</option>
                <option value="Ollama Modelfile">Ollama Modelfile</option>
              </select>
            </div>
          </div>

          <div 
            className="upload-dropzone"
            onClick={handleSimulateUpload}
          >
            <HardDrive size={36} style={{ color: 'var(--accent-purple)', marginBottom: '12px' }} />
            <h4 style={{ color: '#fff', fontSize: '15px', marginBottom: '4px' }}>
              {isUploading ? `Uploading Model File... (${uploadProgress}%)` : 'Click or Drag GGUF / SafeTensors model files here'}
            </h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
              Supports files up to 100GB. Model will be validated and automatically registered in Ollama.
            </p>
          </div>
        </div>
      )}

      {/* Deployed Models Grid (Clean view for Users without red restriction box) */}
      <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#fff', marginBottom: '16px' }}>Deployed Models</h3>
      <div className="workspaces-grid">
        {models.map(mod => (
          <div key={mod.id} className="workspace-card">
            <div>
              <div className="card-top">
                <h3 className="card-title">{mod.name}</h3>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#818cf8' }}>{mod.format}</span>
              </div>
              <p className="card-desc">Parameters: {mod.params} | Size: {mod.size}</p>
            </div>
            <div>
              <div className="card-stats-row">
                <div className="stat-item">
                  <span className="stat-label">STATUS</span>
                  <span className="stat-value" style={{ fontSize: '12px', color: '#10b981' }}>{mod.status}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">UPLOADER</span>
                  <span className="stat-value">{mod.uploader}</span>
                </div>
              </div>
              <div className="card-footer">
                <span className="status-badge active">
                  <span className="status-dot"></span>
                  <span>{activeModel === mod.name ? 'CURRENT ACTIVE' : 'AVAILABLE'}</span>
                </span>
                <button 
                  className="btn-open-ws"
                  style={{
                    backgroundColor: activeModel === mod.name ? 'var(--accent-purple)' : 'var(--bg-surface)',
                    color: '#fff'
                  }}
                  onClick={() => setActiveModel(mod.name)}
                >
                  {activeModel === mod.name ? 'In Use' : 'Select Model'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
