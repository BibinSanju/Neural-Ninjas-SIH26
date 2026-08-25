import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LoginPage from './components/LoginPage';
import WorkspacesView from './components/WorkspacesView';
import ChatView from './components/ChatView';
import EmployeesView from './components/EmployeesView';
import AccessControlView from './components/AccessControlView';
import ModelUploadView from './components/ModelUploadView';
import { TasksView, KnowledgeView, AgentsView } from './components/AuxiliaryViews';
import NewWorkspaceModal from './components/NewWorkspaceModal';

export default function App() {
  // Login Authentication State
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Active View State
  const [activeView, setActiveView] = useState('workspaces');

  // Current Workspace State
  const [currentWs, setCurrentWs] = useState({
    id: 'TRD-8992-A',
    title: 'System Architecture Review'
  });

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Active LLM Model State
  const [activeModel, setActiveModel] = useState('Qwen2.5-Coder-32B');

  // Workspaces Data
  const [workspaces, setWorkspaces] = useState([
    {
      id: 'TRD-8992-A',
      title: 'System Architecture Review',
      desc: 'Comprehensive security analysis of the new microservices architecture proposal.',
      agentsCount: 2,
      resourcesCount: 4,
      activity: '2m ago',
      status: 'Active'
    },
    {
      id: 'TRD-8993-B',
      title: 'Security Compliance',
      desc: 'Quarterly compliance audit and automated policy verification.',
      agentsCount: 3,
      resourcesCount: 12,
      activity: '1h ago',
      status: 'Active'
    },
    {
      id: 'TRD-8994-C',
      title: 'Infrastructure Planning',
      desc: 'Drafting the hybrid cloud deployment strategy for Q3.',
      agentsCount: 1,
      resourcesCount: 7,
      activity: 'Yesterday',
      status: 'Draft'
    },
    {
      id: 'TRD-8995-D',
      title: 'Research Intelligence',
      desc: 'Historical archive of industrial AI research and benchmark results.',
      agentsCount: 4,
      resourcesCount: 23,
      activity: '3d ago',
      status: 'Archived'
    }
  ]);

  // Employee Directory
  const [employees, setEmployees] = useState([
    {
      id: 'emp-101',
      name: 'Sarah Jenkins',
      email: 'sarah.j@sovereign.ai',
      initials: 'SJ',
      department: 'SecOps',
      jobTitle: 'SecOps Lead & Architect',
      systemRole: 'Admin',
      assignedModel: 'Qwen2.5-Coder-32B',
      allowedFilesCount: 5,
      active: true
    },
    {
      id: 'emp-102',
      name: 'David Miller',
      email: 'david.m@sovereign.ai',
      initials: 'DM',
      department: 'Engineering',
      jobTitle: 'Senior Microservices Dev',
      systemRole: 'User',
      assignedModel: 'Qwen2.5-Coder-32B',
      allowedFilesCount: 3,
      active: true
    },
    {
      id: 'emp-103',
      name: 'Alex Chen',
      email: 'alex.c@sovereign.ai',
      initials: 'AC',
      department: 'Data Intelligence',
      jobTitle: 'AI Research Scientist',
      systemRole: 'User',
      assignedModel: 'Llama-3-70B',
      allowedFilesCount: 2,
      active: true
    },
    {
      id: 'emp-104',
      name: 'Elena Rostova',
      email: 'elena.r@sovereign.ai',
      initials: 'ER',
      department: 'Compliance',
      jobTitle: 'Policy Auditor',
      systemRole: 'User',
      assignedModel: 'Mistral-7B',
      allowedFilesCount: 2,
      active: true
    }
  ]);

  // Mounted Files
  const [files] = useState([
    { id: 'f-1', name: 'arch_v2_draft.md', size: '12kb', category: 'Architecture', type: 'file' },
    { id: 'f-2', name: '/src/auth', size: 'Dir', category: 'Source Code', type: 'folder' },
    { id: 'f-3', name: 'PROJECT_EXPLANATION.md', size: '7.8kb', category: 'Documentation', type: 'file' },
    { id: 'f-4', name: 'Q3_financial_audit.xlsx', size: '1.4mb', category: 'Financials', type: 'file' },
    { id: 'f-5', name: 'vulnerability_report.docx', size: '420kb', category: 'SecOps', type: 'file' }
  ]);

  // File Access Permissions per Employee: empId -> array of allowed fileIds
  const [filePermissions, setFilePermissions] = useState({
    'emp-101': ['f-1', 'f-2', 'f-3', 'f-4', 'f-5'], // Admin full access
    'emp-102': ['f-1', 'f-2', 'f-3'],              // Dev user
    'emp-103': ['f-1', 'f-3'],                     // Research user
    'emp-104': ['f-3', 'f-5']                      // Compliance user
  });

  // Models Registry
  const [models, setModels] = useState([
    {
      id: 'm-1',
      name: 'Qwen2.5-Coder-32B',
      format: 'GGUF (Q4_K_M)',
      size: '19.8 GB',
      params: '32B',
      status: 'Active (Ollama)',
      uploader: 'Admin System',
      active: true
    },
    {
      id: 'm-2',
      name: 'Llama-3-70B',
      format: 'SafeTensors',
      size: '39.5 GB',
      params: '70B',
      status: 'Active (Ollama)',
      uploader: 'Admin System',
      active: false
    },
    {
      id: 'm-3',
      name: 'Mistral-7B-Instruct',
      format: 'GGUF (Q8_0)',
      size: '7.2 GB',
      params: '7B',
      status: 'Standby',
      uploader: 'Sarah Jenkins',
      active: false
    }
  ]);

  const handleLogin = (userInfo) => {
    setCurrentUser(userInfo);
    setIsLoggedIn(true);
    setActiveView('workspaces');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
  };

  const openWorkspace = (id, title) => {
    setCurrentWs({ id, title });
    setActiveView('chat');
  };

  const handleCreateWorkspace = (title, desc) => {
    const newWs = {
      id: `TRD-${Math.floor(1000 + Math.random() * 9000)}-X`,
      title,
      desc: desc || 'No description provided.',
      agentsCount: 1,
      resourcesCount: 0,
      activity: 'Just now',
      status: 'Active'
    };
    setWorkspaces([newWs, ...workspaces]);
  };

  // If not logged in, render the Login Screen
  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const userRole = currentUser?.role || 'user';
  const currentEmpId = userRole === 'admin' ? 'emp-101' : 'emp-102';
  const currentUserPermissions = filePermissions[currentEmpId] || [];

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="main-wrapper">
        {/* Sidebar Nav */}
        <Sidebar 
          activeView={activeView} 
          setActiveView={setActiveView} 
          userRole={userRole} 
          onLogout={handleLogout} 
        />

        {/* Main Content View Panels */}
        <main className="content-area">
          {activeView === 'workspaces' && (
            <WorkspacesView 
              workspaces={workspaces} 
              openWorkspace={openWorkspace}
              onOpenModal={() => setIsModalOpen(true)}
            />
          )}

          {activeView === 'chat' && (
            <ChatView 
              currentWs={currentWs}
              userRole={userRole}
              userPermissions={currentUserPermissions}
              files={files}
              activeModel={activeModel}
            />
          )}

          {activeView === 'tasks' && <TasksView />}
          {activeView === 'knowledge' && <KnowledgeView />}
          {activeView === 'agents' && <AgentsView activeModel={activeModel} />}

          {/* ADMIN ONLY VIEWS */}
          {activeView === 'employees' && (
            <EmployeesView 
              employees={employees} 
              setEmployees={setEmployees} 
            />
          )}

          {activeView === 'access-control' && (
            <AccessControlView 
              employees={employees}
              files={files}
              filePermissions={filePermissions}
              setFilePermissions={setFilePermissions}
            />
          )}

          {/* MODEL HUB VIEW */}
          {activeView === 'model-upload' && (
            <ModelUploadView 
              userRole={userRole}
              models={models}
              setModels={setModels}
              activeModel={activeModel}
              setActiveModel={setActiveModel}
            />
          )}
        </main>
      </div>

      {/* New Workspace Modal */}
      <NewWorkspaceModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleCreateWorkspace}
      />
    </div>
  );
}
