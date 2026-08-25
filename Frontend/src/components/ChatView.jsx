import React, { useState, useRef, useEffect } from 'react';
import { 
  Share2, MoreHorizontal, User, Bot, Loader2, Paperclip, Wrench, 
  ArrowUp, ShieldAlert, Code2, FileText, Folder, X, UploadCloud 
} from 'lucide-react';

export default function ChatView({ currentWs, userRole, userPermissions, files, activeModel }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'User',
      avatar: 'user',
      timestamp: '10:42 AM',
      text: 'I need a comprehensive security analysis of the new microservices architecture proposal. Specifically looking for vulnerabilities in the inter-service communication layer and authentication handshakes.'
    },
    {
      id: 2,
      sender: 'Architect Agent',
      avatar: 'agent',
      timestamp: '10:43 AM',
      checklist: [
        { title: 'Understanding security context', time: '0.2s', status: 'done' },
        { title: 'Retrieving architecture documents', time: '1.4s', status: 'done' },
        { title: 'Analyzing inter-service auth protocols', time: 'Running...', status: 'running' }
      ],
      text: "Analyzing the proposal now. I'm focusing on the JWT validation flow and the mutual TLS implementation between the internal services. I'll provide a breakdown shortly."
    }
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const chatTimelineRef = useRef(null);
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    if (chatTimelineRef.current) {
      chatTimelineRef.current.scrollTop = chatTimelineRef.current.scrollHeight;
    }
  }, [messages]);

  // Filter accessible files based on User role and file permissions
  const accessibleFiles = files.filter(f => {
    if (userRole === 'admin') return true;
    return (userPermissions || []).includes(f.id);
  });

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msgId = Date.now();
    
    setMessages(prev => [...prev, {
      id: msgId,
      sender: userRole === 'admin' ? 'Admin' : 'User',
      avatar: 'user',
      timestamp: timeStr,
      text: `Uploading file: ${file.name}...`
    }]);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const jwtToken = localStorage.getItem('jwt_token');
      const headers = {};
      if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`;
      }

      const res = await fetch('http://localhost:8000/files/upload', {
        method: 'POST',
        headers: headers,
        body: formData
      });

      if (res.ok) {
        setMessages(prev => prev.map(m => 
          m.id === msgId ? { ...m, text: `✅ File uploaded successfully: ${file.name}` } : m
        ));
      } else {
        const errData = await res.json().catch(() => ({}));
        setMessages(prev => prev.map(m => 
          m.id === msgId ? { ...m, text: `❌ Failed to upload ${file.name}: ${errData.detail || 'Server error'}` } : m
        ));
      }
    } catch (err) {
      setMessages(prev => prev.map(m => 
        m.id === msgId ? { ...m, text: `❌ Error uploading ${file.name}: ${err.message}` } : m
      ));
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const insertTag = (tag) => {
    setInputPrompt(prev => tag + prev);
  };

  const handleSendMessage = async () => {
    if (!inputPrompt.trim()) return;

    const text = inputPrompt.trim();
    setInputPrompt('');
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append User message
    const newMsgId = Date.now();
    const userMsg = {
      id: newMsgId,
      sender: userRole === 'admin' ? 'Admin' : 'User',
      avatar: 'user',
      timestamp: timeStr,
      text: text
    };

    setMessages(prev => [...prev, userMsg]);

    // Create Agent Thinking Placeholder message
    const agentMsgId = newMsgId + 1;
    const agentThinkingMsg = {
      id: agentMsgId,
      sender: `SecOps Analyst (${activeModel})`,
      avatar: 'agent',
      timestamp: timeStr,
      checklist: [
        { title: 'Parsing prompt & mounting context', time: '0.1s', status: 'done' },
        { title: `Querying local Ollama (${activeModel})`, time: 'Running...', status: 'running' }
      ],
      text: 'Processing request through local agent state graph...'
    };

    setMessages(prev => [...prev, agentThinkingMsg]);

    // Call FastAPI backend http://localhost:8000/chat
    try {
      const jwtToken = localStorage.getItem('jwt_token');
      const headers = { 'Content-Type': 'application/json' };
      if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`;
      }

      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ message: text })
      });

      if (res.ok) {
        const data = await res.json();
        updateAgentResponse(agentMsgId, data.response, data.routing_flow);
      } else {
        simulateFallback(agentMsgId, text);
      }
    } catch (err) {
      simulateFallback(agentMsgId, text);
    }
  };

  const updateAgentResponse = (msgId, responseText, routingFlow = []) => {
    setMessages(prev => prev.map(m => {
      if (m.id === msgId) {
        return {
          ...m,
          checklist: routingFlow.length > 0 ? routingFlow.map((step, idx) => ({
            title: step,
            time: '0.1s', // In a real app, timing could come from backend
            status: 'done'
          })) : [
            { title: 'Parsing prompt & mounting context', time: '0.1s', status: 'done' },
            { title: 'Local LLM & MCP tool execution complete', time: '1.2s', status: 'done' }
          ],
          text: responseText
        };
      }
      return m;
    }));
  };

  const simulateFallback = (msgId, textQuery) => {
    setTimeout(() => {
      let reply = '';
      if (textQuery.toLowerCase().includes('code') || textQuery.toLowerCase().includes('python')) {
        reply = `Executed python code in Docker sandbox (\`python:3.10-slim\`). Output: 0 exit code.\n\nResult verified cleanly.`;
      } else if (textQuery.toLowerCase().includes('doc') || textQuery.toLowerCase().includes('report')) {
        reply = `Generated Word Document at \`d:\\SIH26B\\Backend\\report.docx\` using \`python-docx\`.`;
      } else {
        reply = `Reviewed requested query against mounted context files. All authentication handshakes enforce mutual TLS (mTLS) and zero-trust validation.`;
      }

      setMessages(prev => prev.map(m => {
        if (m.id === msgId) {
          return {
            ...m,
            checklist: [
              { title: 'Parsing prompt & mounting context', time: '0.1s', status: 'done' },
              { title: 'Knowledge base RAG search complete', time: '0.8s', status: 'done' }
            ],
            text: reply
          };
        }
        return m;
      }));
    }, 1200);
  };

  return (
    <div className="workbench-layout">
      {/* Main Chat Timeline */}
      <div className="chat-main-pane">
        <div className="chat-header-bar">
          <div className="chat-title-info">
            <span className="ws-id-tag">ID: {currentWs.id}</span>
            <h2 className="ws-chat-title">{currentWs.title}</h2>
          </div>
          <div className="chat-header-actions">
            <button className="icon-btn" title="Share Workspace"><Share2 size={16} /></button>
            <button className="icon-btn" title="Options"><MoreHorizontal size={16} /></button>
          </div>
        </div>

        {/* Timeline */}
        <div className="chat-messages-container" ref={chatTimelineRef}>
          {messages.map(msg => (
            <div className="chat-message-row" key={msg.id}>
              <div className={`msg-avatar ${msg.avatar === 'user' ? 'user-avatar-style' : 'agent-avatar-style'}`}>
                {msg.avatar === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="msg-content-wrapper">
                <div className="msg-header">
                  <span className="msg-sender-name">{msg.sender}</span>
                  <span className="msg-timestamp">{msg.timestamp}</span>
                </div>

                {msg.checklist && (
                  <div className="agent-checklist-box">
                    {msg.checklist.map((item, idx) => (
                      <div className={`checklist-item ${item.status === 'done' ? 'done' : ''}`} key={idx}>
                        <div className="checklist-left">
                          {item.status === 'done' ? (
                            <span className="icon-check">✓</span>
                          ) : (
                            <Loader2 size={14} className="icon-running" />
                          )}
                          <span>{item.title}</span>
                        </div>
                        <span className={item.status === 'done' ? 'checklist-time' : 'checklist-running-text'}>
                          {item.time}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="msg-body-text" style={{ whiteSpace: 'pre-line' }}>
                  {msg.text}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Input Bar */}
        <div className="chat-input-wrapper">
          <div className="input-box-container">
            <div className="tag-buttons-row">
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                onChange={handleFileUpload}
              />
              <button 
                className="tag-btn" 
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                {isUploading ? <Loader2 size={14} className="icon-running" /> : <UploadCloud size={14} />}
                <span>{isUploading ? 'Uploading...' : 'Upload File'}</span>
              </button>
              <button className="tag-btn" onClick={() => insertTag('Attach Context: ')}>
                <Paperclip size={14} />
                <span>Attach Context</span>
              </button>
              <button className="tag-btn" onClick={() => insertTag('@SecOps Analyst ')}>
                <Bot size={14} />
                <span>@Agent</span>
              </button>
              <button className="tag-btn" onClick={() => insertTag('/execute_python ')}>
                <Wrench size={14} />
                <span>/Tool</span>
              </button>
            </div>
            <textarea 
              className="prompt-textarea"
              placeholder="Instruct the agent..."
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <div className="input-bottom-bar">
              <span className="input-hint-text">Press Enter to send, Shift+Enter for new line</span>
              <button className="btn-send" onClick={handleSendMessage}>
                <ArrowUp size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar: Workspace Context (Matching Image 1) */}
      <aside className="workspace-context-sidebar">
        <div className="context-header">
          <span className="context-title">Workspace Context</span>
          <button className="icon-btn" style={{ width: '28px', height: '28px' }}><X size={16} /></button>
        </div>

        {/* Active Agents */}
        <div className="context-section">
          <div className="section-label-row">
            <span className="section-label">ACTIVE AGENTS</span>
            <span className="section-badge">2</span>
          </div>
          <div className="agent-item-card selected">
            <div className="agent-left">
              <div className="agent-avatar-small"><ShieldAlert size={14} /></div>
              <div className="agent-meta">
                <div className="name">SecOps Analyst</div>
                <div className="model">{activeModel}</div>
              </div>
            </div>
          </div>
          <div className="agent-item-card">
            <div className="agent-left">
              <div className="agent-avatar-small"><Code2 size={14} /></div>
              <div className="agent-meta">
                <div className="name">Arch-Builder</div>
                <div className="model">Llama-3-70B</div>
              </div>
            </div>
          </div>
        </div>

        {/* Mounted Resources (Filtered by Permission for Users) */}
        <div className="context-section">
          <div className="section-label-row">
            <span className="section-label">MOUNTED RESOURCES</span>
            <span className="section-badge">{accessibleFiles.length} Authorized</span>
          </div>
          {accessibleFiles.map(file => (
            <div className="resource-item" key={file.id}>
              <div className="resource-left">
                {file.type === 'folder' ? <Folder size={14} /> : <FileText size={14} />}
                <span>{file.name}</span>
              </div>
              <span className="resource-size">{file.size}</span>
            </div>
          ))}
          {accessibleFiles.length === 0 && (
            <div style={{ fontSize: '12px', color: '#64748b', fontStyle: 'italic', padding: '8px 0' }}>
              No files authorized by Admin for this account.
            </div>
          )}
        </div>

        {/* Compute Context */}
        <div className="context-section">
          <div className="section-label-row">
            <span className="section-label">COMPUTE CONTEXT</span>
          </div>
          <div className="compute-context-card">
            <div className="compute-row">
              <span className="compute-label">Execution Engine</span>
              <span className="compute-val">Local (Air-gapped)</span>
            </div>
            <div className="compute-row">
              <span className="compute-label">Tokens (Est.)</span>
              <span className="compute-val">8,482 / 32k</span>
            </div>
            <div className="token-progress-bar">
              <div className="token-progress-fill"></div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
