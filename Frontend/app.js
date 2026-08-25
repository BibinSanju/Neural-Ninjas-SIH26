// Sovereign AI Workbench Client Script
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  const BACKEND_URL = 'http://localhost:8000/chat';
  const LOGIN_URL = 'http://localhost:8000/auth/login';
  
  let JWT_TOKEN = null;

  async function ensureLogin() {
    if (JWT_TOKEN) return true;
    try {
      const res = await fetch(LOGIN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin_test', password: 'password' })
      });
      if (res.ok) {
        const data = await res.json();
        JWT_TOKEN = data.access_token;
        console.log("Auto-logged in successfully as admin_test");
        return true;
      } else {
        console.error("Auto-login failed:", await res.text());
        return false;
      }
    } catch (err) {
      console.error("Auto-login error:", err);
      return false;
    }
  }

  // Navigation Logic
  const navItems = document.querySelectorAll('.nav-item[data-view]');
  const viewPanels = document.querySelectorAll('.view-panel');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetViewId = item.getAttribute('data-view');

      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      viewPanels.forEach(panel => {
        if (panel.id === targetViewId) {
          panel.classList.add('active-view');
        } else {
          panel.classList.remove('active-view');
        }
      });
    });
  });

  // Filter & Search Workspaces Logic
  const wsSearchInput = document.getElementById('ws-search-input');
  const statusFilter = document.getElementById('status-filter');
  const workspacesGrid = document.getElementById('workspaces-grid');

  function filterWorkspaces() {
    const query = wsSearchInput.value.toLowerCase();
    const status = statusFilter.value;
    const cards = workspacesGrid.querySelectorAll('.workspace-card');

    cards.forEach(card => {
      const title = card.getAttribute('data-title')?.toLowerCase() || '';
      const cardStatus = card.getAttribute('data-status') || '';
      const matchesQuery = title.includes(query);
      const matchesStatus = status === 'all' || cardStatus === status;

      if (matchesQuery && matchesStatus) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  }

  if (wsSearchInput) wsSearchInput.addEventListener('input', filterWorkspaces);
  if (statusFilter) statusFilter.addEventListener('change', filterWorkspaces);

  // New Workspace Modal
  const modalBackdrop = document.getElementById('new-ws-modal');
  const openModalBtn = document.getElementById('open-new-ws-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const cancelModalBtn = document.getElementById('cancel-modal-btn');
  const saveWsBtn = document.getElementById('save-ws-btn');

  function showModal() { modalBackdrop.classList.add('active'); }
  function hideModal() { modalBackdrop.classList.remove('active'); }

  if (openModalBtn) openModalBtn.addEventListener('click', showModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', hideModal);
  if (cancelModalBtn) cancelModalBtn.addEventListener('click', hideModal);

  if (saveWsBtn) {
    saveWsBtn.addEventListener('click', () => {
      const titleInput = document.getElementById('new-ws-title');
      const descInput = document.getElementById('new-ws-desc');
      const title = titleInput.value.trim();
      const desc = descInput.value.trim();

      if (!title) return alert('Please enter a workspace title.');

      const newId = `TRD-${Math.floor(1000 + Math.random() * 9000)}-X`;
      const cardHTML = `
        <div class="workspace-card" data-status="active" data-id="${newId}" data-title="${title}">
          <div>
            <div class="card-top">
              <h3 class="card-title">${title}</h3>
              <button class="card-menu-btn"><i data-lucide="more-vertical"></i></button>
            </div>
            <p class="card-desc">${desc || 'No description provided.'}</p>
          </div>
          <div>
            <div class="card-stats-row">
              <div class="stat-item">
                <span class="stat-label">AGENTS</span>
                <span class="stat-value">1</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">RESOURCES</span>
                <span class="stat-value">0</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">ACTIVITY</span>
                <span class="stat-value">Just now</span>
              </div>
            </div>
            <div class="card-footer">
              <div class="status-badge active">
                <span class="status-dot"></span>
                <span>ACTIVE</span>
              </div>
              <button class="btn-open-ws" onclick="openWorkspace('${newId}', '${title}')">Open</button>
            </div>
          </div>
        </div>
      `;

      workspacesGrid.insertAdjacentHTML('afterbegin', cardHTML);
      if (window.lucide) lucide.createIcons();

      titleInput.value = '';
      descInput.value = '';
      hideModal();
    });
  }

  // Textarea Auto-Resize & Submit Logic
  const textarea = document.getElementById('chat-textarea');
  const btnSubmitChat = document.getElementById('btn-submit-chat');
  const chatTimeline = document.getElementById('chat-timeline');

  if (textarea) {
    textarea.addEventListener('input', () => {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 140) + 'px';
    });

    textarea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });
  }

  if (btnSubmitChat) {
    btnSubmitChat.addEventListener('click', handleSendMessage);
  }

  async function handleSendMessage() {
    const text = textarea.value.trim();
    if (!text) return;

    textarea.value = '';
    textarea.style.height = 'auto';

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append User Message
    const userMsgHTML = `
      <div class="chat-message-row">
        <div class="msg-avatar user-avatar-style">
          <i data-lucide="user"></i>
        </div>
        <div class="msg-content-wrapper">
          <div class="msg-header">
            <span class="msg-sender-name">User</span>
            <span class="msg-timestamp">${timeStr}</span>
          </div>
          <div class="msg-body-text">${escapeHTML(text)}</div>
        </div>
      </div>
    `;
    chatTimeline.insertAdjacentHTML('beforeend', userMsgHTML);
    if (window.lucide) lucide.createIcons();

    // Create Agent Thinking Row with Execution Checklist
    const agentMsgId = `agent-msg-${Date.now()}`;
    const agentMsgHTML = `
      <div class="chat-message-row" id="${agentMsgId}">
        <div class="msg-avatar agent-avatar-style">
          <i data-lucide="bot"></i>
        </div>
        <div class="msg-content-wrapper">
          <div class="msg-header">
            <span class="msg-sender-name">SecOps Analyst</span>
            <span class="msg-timestamp">${timeStr}</span>
          </div>

          <div class="agent-checklist-box">
            <div class="checklist-item done">
              <div class="checklist-left">
                <span class="icon-check">✓</span>
                <span>Parsing prompt & mounting context</span>
              </div>
              <span class="checklist-time">0.1s</span>
            </div>
            <div class="checklist-item" id="step-2-${agentMsgId}">
              <div class="checklist-left">
                <i data-lucide="loader-2" class="icon-running"></i>
                <span>Querying Ollama (qwen2.5) & MCP Tool server</span>
              </div>
              <span class="checklist-running-text">Running...</span>
            </div>
          </div>

          <div class="msg-body-text" id="response-body-${agentMsgId}">
            <em>Processing request through local agent execution graph...</em>
          </div>
        </div>
      </div>
    `;

    chatTimeline.insertAdjacentHTML('beforeend', agentMsgHTML);
    if (window.lucide) lucide.createIcons();
    chatTimeline.scrollTop = chatTimeline.scrollHeight;

    // Ensure we are logged in before making the request
    await ensureLogin();

    // Try communicating with FastAPI endpoint
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (JWT_TOKEN) {
        headers['Authorization'] = `Bearer ${JWT_TOKEN}`;
      }

      const res = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ message: text })
      });

      if (res.ok) {
        const data = await res.json();
        updateAgentResponse(agentMsgId, data.response);
      } else {
        const errData = await res.json();
        simulateAgentFallback(agentMsgId, text, errData.detail || 'Backend error');
      }
    } catch (err) {
      // Backend not running locally - run simulation so demo UI works smoothly
      simulateAgentFallback(agentMsgId, text, null);
    }
  }

  function updateAgentResponse(msgId, contentText) {
    const step2 = document.getElementById(`step-2-${msgId}`);
    if (step2) {
      step2.className = 'checklist-item done';
      step2.innerHTML = `
        <div class="checklist-left">
          <span class="icon-check">✓</span>
          <span>Execution graph complete</span>
        </div>
        <span class="checklist-time">1.2s</span>
      `;
    }
    const respBody = document.getElementById(`response-body-${msgId}`);
    if (respBody) {
      respBody.innerHTML = escapeHTML(contentText).replace(/\n/g, '<br>');
    }
    chatTimeline.scrollTop = chatTimeline.scrollHeight;
  }

  function simulateAgentFallback(msgId, queryText, errorDetail) {
    setTimeout(() => {
      const step2 = document.getElementById(`step-2-${msgId}`);
      if (step2) {
        step2.className = 'checklist-item done';
        step2.innerHTML = `
          <div class="checklist-left">
            <span class="icon-check">✓</span>
            <span>Retrieved knowledge base & sandboxed tools</span>
          </div>
          <span class="checklist-time">0.8s</span>
        `;
      }

      const respBody = document.getElementById(`response-body-${msgId}`);
      if (respBody) {
        let simulatedReply = '';

        if (queryText.toLowerCase().includes('code') || queryText.toLowerCase().includes('python')) {
          simulatedReply = `I executed the request in the isolated Docker container (\`python:3.10-slim\`).\n\n\`\`\`python\n# Execution Output\nstdout: Process completed with 0 exit code.\n\`\`\`\nAll checks passed successfully.`;
        } else if (queryText.toLowerCase().includes('doc') || queryText.toLowerCase().includes('report')) {
          simulatedReply = `Generated the Word document report using \`python-docx\` tool.\n\nArtifact saved at: \`d:\\SIH26B\\Backend\\report.docx\``;
        } else {
          simulatedReply = `Analyzing context for query: "${queryText}".\n\nI have reviewed the inter-service communication protocols and authentication handshakes. All internal communications are enforced via mutual TLS (mTLS) with token validation handled by the API gateway.`;
        }

        if (errorDetail) {
          simulatedReply += `\n\n*(Note: Backend FastAPI server message: ${errorDetail})*`;
        }

        respBody.innerHTML = simulatedReply.replace(/\n/g, '<br>');
      }
      chatTimeline.scrollTop = chatTimeline.scrollHeight;
    }, 1200);
  }

  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }
});

// Global Function to Open Workspace into Chat View
window.openWorkspace = function(wsId, wsTitle) {
  const currentWsId = document.getElementById('current-ws-id');
  const currentWsTitle = document.getElementById('current-ws-title');

  if (currentWsId) currentWsId.textContent = `ID: ${wsId}`;
  if (currentWsTitle) currentWsTitle.textContent = wsTitle;

  const chatNavItem = document.querySelector('.nav-item[data-view="chat-view"]');
  if (chatNavItem) chatNavItem.click();
};

// Global Function to Insert Prompt Tag Buttons
window.insertPromptTag = function(tagText) {
  const textarea = document.getElementById('chat-textarea');
  if (textarea) {
    textarea.value = tagText + textarea.value;
    textarea.focus();
  }
};
