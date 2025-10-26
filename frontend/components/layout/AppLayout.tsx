// This component establishes the main three-column layout of the application.
// It uses CSS Grid or Flexbox to create the distinct sections for media,
// the video player, and the chat interface. It ensures the layout is
// responsive and visually balanced.

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  const {
    user,
    logout,
    currentProject,
    projects,
    savedVideos,
    loadProjects,
    loadSavedVideos,
    createProject,
    switchProject,
    saveCurrentProject,
    deleteSavedVideo
  } = useAppStore();
  const router = useRouter();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showProjectsModal, setShowProjectsModal] = useState(false);
  const [showSavedVideos, setShowSavedVideos] = useState(false);
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const [username, setUsername] = useState(user?.email.split('@')[0] || '');
  const [isEditingName, setIsEditingName] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState<number | null>(null);
  const [editingProjectName, setEditingProjectName] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load projects on mount
  useEffect(() => {
    if (user) {
      loadProjects();
    }
  }, [user]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImage(reader.result as string);
        // TODO: Save to backend/localStorage
      };
      reader.readAsDataURL(file);
    }
  };

  const handleNameSave = () => {
    // TODO: Save to backend
    setIsEditingName(false);
  };

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;

    setIsCreatingProject(true);
    try {
      const project = await createProject(newProjectName.trim());
      await switchProject(project.id);
      setNewProjectName('');
      setShowProjectsModal(false);
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setIsCreatingProject(false);
    }
  };

  const handleSwitchProject = async (projectId: number) => {
    await switchProject(projectId);
    setShowProjectsModal(false);
    setShowUserMenu(false);
  };

  const handleRenameProject = async (projectId: number) => {
    if (!editingProjectName.trim() || !user) return;

    try {
      await fetch(`http://localhost:8000/api/projects/${projectId}?user_email=${user.email}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editingProjectName.trim() })
      });

      // Update local state
      const updatedProjects = projects.map(p =>
        p.id === projectId ? { ...p, name: editingProjectName.trim() } : p
      );
      useAppStore.setState({
        projects: updatedProjects,
        currentProject: currentProject?.id === projectId
          ? { ...currentProject, name: editingProjectName.trim() }
          : currentProject
      });

      setEditingProjectId(null);
      setEditingProjectName('');
    } catch (error) {
      console.error('Failed to rename project:', error);
    }
  };

  const handleDeleteProject = async (projectId: number) => {
    if (!user) return;
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/projects/${projectId}?user_email=${user.email}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        const updatedProjects = projects.filter(p => p.id !== projectId);
        useAppStore.setState({ projects: updatedProjects });

        // If deleted current project, switch to first available or create new
        if (currentProject?.id === projectId) {
          if (updatedProjects.length > 0) {
            await switchProject(updatedProjects[0].id);
          } else {
            const newProject = await createProject('My First Project');
            await switchProject(newProject.id);
          }
        }
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  // Auto-save current project periodically
  useEffect(() => {
    if (!currentProject) return;

    const interval = setInterval(() => {
      saveCurrentProject();
    }, 30000); // Save every 30 seconds

    return () => clearInterval(interval);
  }, [currentProject, saveCurrentProject]);

  const handleDeleteSavedVideo = async (videoId: number) => {
    if (!confirm('Are you sure you want to delete this saved video? This action cannot be undone.')) return;

    try {
      await deleteSavedVideo(videoId);
    } catch (error) {
      console.error('Failed to delete saved video:', error);
      alert('Failed to delete video. Please try again.');
    }
  };

  return (
    <main className="bg-black text-white h-screen w-screen flex flex-col">
      {/* Top Navigation Bar */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="font-lobster text-2xl bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Cue
          </h1>
          {currentProject && (
            <div className="flex items-center gap-2 text-sm text-gray-400 border-l border-gray-700 pl-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
              </svg>
              <span className="text-white font-medium">{currentProject.name}</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-4">
          {/* User Menu */}
          <div className="relative" ref={menuRef}>
            <div
              className="flex items-center gap-2 text-sm cursor-pointer hover:opacity-80 transition-opacity"
              onMouseEnter={() => setShowUserMenu(true)}
            >
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center font-semibold overflow-hidden">
                {profileImage ? (
                  <img src={profileImage} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  user?.email.charAt(0).toUpperCase()
                )}
              </div>
              <span className="text-gray-300">{username}</span>
            </div>

            {/* Dropdown Menu */}
            {showUserMenu && (
              <div
                className="absolute right-0 top-full mt-2 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50"
                onMouseLeave={() => setShowUserMenu(false)}
              >
                <div className="p-4 space-y-4">
                  {/* Profile Section */}
                  <div className="flex items-center gap-3 pb-3 border-b border-gray-700">
                    <div className="relative">
                      <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center font-bold text-lg overflow-hidden">
                        {profileImage ? (
                          <img src={profileImage} alt="Profile" className="w-full h-full object-cover" />
                        ) : (
                          user?.email.charAt(0).toUpperCase()
                        )}
                      </div>
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="absolute -bottom-1 -right-1 w-6 h-6 bg-purple-600 hover:bg-purple-700 rounded-full flex items-center justify-center transition-colors"
                        title="Upload photo"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="17 8 12 3 7 8" />
                          <line x1="12" x2="12" y1="3" y2="15" />
                        </svg>
                      </button>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="hidden"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      {isEditingName ? (
                        <input
                          type="text"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          onBlur={handleNameSave}
                          onKeyDown={(e) => e.key === 'Enter' && handleNameSave()}
                          className="w-full bg-gray-700 text-white px-2 py-1 rounded text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                          autoFocus
                        />
                      ) : (
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-white truncate">{username}</p>
                          <button
                            onClick={() => setIsEditingName(true)}
                            className="text-gray-400 hover:text-white"
                            title="Edit name"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                            </svg>
                          </button>
                        </div>
                      )}
                      <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                    </div>
                  </div>

                  {/* Menu Items */}
                  <div className="space-y-1">
                    {/* My Projects */}
                    <button
                      className="w-full flex items-center justify-between gap-3 px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded-lg transition-colors text-left"
                      onClick={() => setShowProjectsModal(true)}
                    >
                      <div className="flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                        </svg>
                        <span>My Projects</span>
                      </div>
                      <span className="text-xs text-gray-500">({projects.length})</span>
                    </button>

                    {/* Saved Videos */}
                    <button
                      className="w-full flex items-center justify-between gap-3 px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded-lg transition-colors text-left"
                      onClick={async () => {
                        console.log('Opening Saved Videos modal, reloading...');
                        await loadSavedVideos();
                        setShowSavedVideos(true);
                      }}
                    >
                      <div className="flex items-center gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                          <polyline points="17 21 17 13 7 13 7 21" />
                          <polyline points="7 3 7 8 15 8" />
                        </svg>
                        <span>Saved Videos</span>
                      </div>
                      <span className="text-xs text-gray-500">({savedVideos.length})</span>
                    </button>

                    <button
                      className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-400 hover:bg-gray-700 rounded-lg transition-colors text-left"
                      onClick={handleLogout}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                        <polyline points="16 17 21 12 16 7" />
                        <line x1="21" x2="9" y1="12" y2="12" />
                      </svg>
                      <span>Log Out</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Projects Modal */}
      {showProjectsModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setShowProjectsModal(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-3xl max-h-[80vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="bg-gray-800 px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                </svg>
                <h2 className="text-xl font-semibold text-white">My Projects</h2>
              </div>
              <button
                onClick={() => setShowProjectsModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-80px)]">
              {/* Create New Project */}
              <div className="mb-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-300 mb-3">Create New Project</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Enter project name..."
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleCreateProject()}
                    className="flex-1 bg-gray-700 text-white px-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    disabled={isCreatingProject}
                  />
                  <button
                    onClick={handleCreateProject}
                    disabled={!newProjectName.trim() || isCreatingProject}
                    className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19" />
                      <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                    {isCreatingProject ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </div>

              {/* Project List */}
              {projects.length === 0 ? (
                <div className="text-center py-12">
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-gray-600 mx-auto mb-4">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                  </svg>
                  <p className="text-gray-400 text-lg">No projects yet</p>
                  <p className="text-gray-600 text-sm mt-2">Create your first project above</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {projects.map((project) => (
                    <div
                      key={project.id}
                      onClick={() => {
                        // If the clicked project is already selected, open it.
                        if (selectedProjectId === project.id) {
                          handleSwitchProject(project.id);
                        } else {
                          // Otherwise, just highlight it.
                          setSelectedProjectId(project.id);
                        }
                      }}
                      className={`p-4 rounded-lg border transition-all cursor-pointer ${selectedProjectId === project.id
                        ? 'bg-purple-600/20 border-purple-500' // This is the highlighted project
                        : 'bg-gray-800 border-gray-700 hover:border-gray-600' // All others are default
                        }`}
                    >
                      <div className="flex items-center justify-between">
                        {/* Project Name */}
                        <div className="flex-1 flex items-center gap-3">
                          {editingProjectId === project.id ? (
                            <input
                              type="text"
                              value={editingProjectName}
                              onChange={(e) => setEditingProjectName(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') handleRenameProject(project.id);
                                if (e.key === 'Escape') {
                                  setEditingProjectId(null);
                                  setEditingProjectName('');
                                }
                              }}
                              onBlur={() => handleRenameProject(project.id)}
                              className="flex-1 bg-gray-700 text-white px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                              autoFocus
                            />
                          ) : (
                            <>
                              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 flex-shrink-0">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                              </svg>
                              <div className="flex-1">
                                <h3 className="text-white font-medium">{project.name}</h3>
                                <p className="text-xs text-gray-500 mt-1">
                                  Updated {new Date(project.updated_at).toLocaleDateString()}
                                </p>
                              </div>
                              {currentProject?.id === project.id && (
                                <span className="px-2 py-1 bg-gray-600 text-white text-xs rounded font-medium ml-auto">
                                  Current
                                </span>
                              )}
                            </>
                          )}
                        </div>

                        {/* Actions */}
                        {editingProjectId !== project.id && (
                          <div className="flex items-center gap-2 ml-4">
                            <button
                              onClick={(e) => {
                                e.stopPropagation(); // Prevent the div's onClick from firing
                                setEditingProjectId(project.id);
                                setEditingProjectName(project.name);
                              }}
                              className="text-gray-400 hover:text-blue-400 transition-colors p-2"
                              title="Rename project"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                              </svg>
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation(); // Prevent the div's onClick from firing
                                handleDeleteProject(project.id);
                              }}
                              className="text-gray-400 hover:text-red-400 transition-colors p-2"
                              title="Delete project"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                              </svg>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Saved Videos Modal */}
      {showSavedVideos && (() => {
        console.log('Saved Videos Modal opened. Current savedVideos:', savedVideos);
        return null;
      })()}
      {showSavedVideos && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setShowSavedVideos(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-4xl max-h-[80vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="bg-gray-800 px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-400">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                  <polyline points="17 21 17 13 7 13 7 21" />
                  <polyline points="7 3 7 8 15 8" />
                </svg>
                <h2 className="text-xl font-semibold text-white">Saved Videos</h2>
                <span className="text-sm text-gray-400">(Global Collection)</span>
                <span className="text-xs text-gray-500">({savedVideos.length} videos)</span>
              </div>
              <button
                onClick={() => setShowSavedVideos(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-80px)]">
              {savedVideos.length === 0 ? (
                <div className="text-center py-12">
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-gray-600 mx-auto mb-4">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                    <polyline points="17 21 17 13 7 13 7 21" />
                    <polyline points="7 3 7 8 15 8" />
                  </svg>
                  <p className="text-gray-400 text-lg">No saved videos yet</p>
                  <p className="text-gray-600 text-sm mt-2">Videos you save will appear here</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {savedVideos.map((video) => (
                    <div key={video.id} className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden hover:border-purple-500 transition-colors group">
                      <div className="aspect-video bg-gray-900 flex items-center justify-center relative">
                        <video
                          src={video.url}
                          className="w-full h-full object-cover"
                          preload="metadata"
                        />
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                          <a
                            href={video.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-purple-600 hover:bg-purple-700 p-2 rounded-full transition-colors"
                            title="Open"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polygon points="5 3 19 12 5 21 5 3" />
                            </svg>
                          </a>
                          <button
                            onClick={() => handleDeleteSavedVideo(video.id)}
                            className="bg-red-600 hover:bg-red-700 p-2 rounded-full transition-colors"
                            title="Delete"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="3 6 5 6 21 6" />
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      <div className="p-3">
                        <p className="text-white font-medium text-sm truncate">{video.filename}</p>
                        {video.description && (
                          <p className="text-gray-400 text-xs mt-1 line-clamp-2">{video.description}</p>
                        )}
                        <p className="text-gray-600 text-xs mt-2">
                          {new Date(video.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {children}
      </div>
    </main>
  );
};

export default AppLayout;
