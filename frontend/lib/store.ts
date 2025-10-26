// Global state management using Zustand
// Manages uploaded media files, video URLs, and upload progress

import { create } from 'zustand';

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to encode email for URL
const encodeEmail = (email: string) => encodeURIComponent(email);

export interface MediaFile {
  id: string;
  filename: string;
  url: string;
  type: string;
  mediaType: 'video' | 'audio'; // NEW: Distinguish between video and audio files
  uploadedAt: Date;
  description: string;
  isAnalyzing: boolean;
  versionHistory: string[]; // Acts as the "undo" stack
  redoHistory: string[];    // Acts as the "redo" stack
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: 'pending' | 'completed' | 'error';
  videoUrl?: string; // Optional video/audio URL for editing results
  videoUrls?: string[]; // New: For multiple video outputs
  mediaType?: 'video' | 'audio'; // Type of media result
  mediaFilename?: string; // Filename for the result
}

export interface SavedVideo {
  id: number;
  user_id: number;
  filename: string;
  url: string;
  thumbnail?: string;
  description?: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  media_bin: string; // JSON string
  chat_history: string; // JSON string
}

interface AppState {
  // Media files
  mediaBin: MediaFile[];
  activeVideoId: string | null;
  activeAudioId: string | null;

  // Upload state
  isUploading: boolean;
  uploadProgress: number;

  // Playback state
  playbackState: {
    isPlaying: boolean;
    currentTime: number;
  };

  // Chat/Messages
  messages: ChatMessage[];
  currentThreadId: string | null;
  isThinking: boolean;
  authStatus: 'loading' | 'authenticated' | 'unauthenticated';
  isAuthenticated: boolean;
  user: { email: string } | null;
  token: string | null;

  // Project Management
  currentProject: Project | null;
  projects: Project[];
  savedVideos: SavedVideo[];
  isProjectLoading: boolean;

  // Actions
  addMediaFile: (file: Omit<MediaFile, 'versionHistory' | 'redoHistory'>) => void;
  setActiveVideoId: (id: string) => void;
  setActiveAudioId: (id: string) => void;
  revertToPreviousVersion: (videoId: string) => void;
  redoLastAction: (videoId: string) => void;
  deleteMediaFile: (id: string) => Promise<void>;
  setUploadProgress: (progress: number) => void;
  setIsUploading: (isUploading: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  handleSuccessfulEdit: (videoId: string, newUrl: string, messageId: string, messageContent: string) => void;
  addEditedMediaToLibrary: (url: string, filename: string, mediaType: 'video' | 'audio') => void;
  clearChat: () => Promise<void>;
  renameMediaFile: (id: string, newFilename: string) => void;
  updateMediaFileDescription: (id: string, description: string) => void;
  setPlaybackState: (updates: Partial<AppState['playbackState']>) => void;
  setActiveVideoVersion: (videoId: string, url: string) => void;
  setIsThinking: (isThinking: boolean) => void;
  login: (user: { email: string }, token: string) => void;
  logout: () => void;
  setAuthStatus: (status: 'authenticated' | 'unauthenticated') => void;

  // Project Management Actions
  loadProjects: () => Promise<void>;
  createProject: (name: string) => Promise<Project>;
  switchProject: (projectId: number) => Promise<void>;
  saveCurrentProject: () => Promise<void>;
  deleteProject: (projectId: number) => Promise<void>;

  // Saved Videos Actions
  saveVideo: (videoUrl: string, filename: string, description?: string) => Promise<void>;
  loadSavedVideos: () => Promise<void>;
  deleteSavedVideo: (videoId: number) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  mediaBin: [],
  activeVideoId: null,
  activeAudioId: null,
  isUploading: false,
  uploadProgress: 0,
  playbackState: { isPlaying: false, currentTime: 0 },
  messages: [],
  currentThreadId: null,
  isThinking: false,
  authStatus: 'loading',
  isAuthenticated: false,
  user: null,
  token: null,
  currentProject: null,
  projects: [],
  savedVideos: [],
  isProjectLoading: false,

  addMediaFile: (file) =>
    set((state) => {
      const newFile: MediaFile = {
        ...file,
        versionHistory: [file.url], // Start history with the original URL
        redoHistory: [],            // Redo history starts empty
      };
      return {
        mediaBin: [...state.mediaBin, newFile],
        activeVideoId: newFile.id
      };
    }),

  setActiveVideoId: (id: string) =>
    set({ activeVideoId: id }),

  setActiveAudioId: (id: string) =>
    set({ activeAudioId: id }),

  revertToPreviousVersion: (videoId) => set((state) => {
    const file = state.mediaBin.find(f => f.id === videoId);
    if (!file || file.versionHistory.length <= 1) return state; // Cannot revert original

    const lastVersion = file.versionHistory[file.versionHistory.length - 1];
    const newHistory = file.versionHistory.slice(0, -1);
    const previousUrl = newHistory[newHistory.length - 1];

    // Move the reverted version to the redo stack
    const newRedoHistory = [lastVersion, ...file.redoHistory];

    const newMediaBin = state.mediaBin.map(f =>
      f.id === videoId ? { ...f, versionHistory: newHistory, redoHistory: newRedoHistory } : f
    );

    const revertMessage: ChatMessage = {
      id: `revert-${Date.now()}`,
      role: 'assistant',
      content: '↩️ Video has been reverted to the previous version.',
      timestamp: new Date(),
      status: 'completed',
    };

    return {
      mediaBin: newMediaBin,
      messages: [...state.messages, revertMessage],
    };
  }),

  redoLastAction: (videoId) => set((state) => {
    const file = state.mediaBin.find(f => f.id === videoId);
    if (!file || file.redoHistory.length === 0) return state; // Nothing to redo

    const nextVersion = file.redoHistory[0];
    const newRedoHistory = file.redoHistory.slice(1);

    // Move the redone version back to the version history
    const newHistory = [...file.versionHistory, nextVersion];

    const newMediaBin = state.mediaBin.map(f =>
      f.id === videoId ? { ...f, versionHistory: newHistory, redoHistory: newRedoHistory } : f
    );

    const redoMessage: ChatMessage = {
      id: `redo-${Date.now()}`,
      role: 'assistant',
      content: '↪️ Redo successful. Restored the reverted version.',
      timestamp: new Date(),
      status: 'completed',
    };

    return {
      mediaBin: newMediaBin,
      messages: [...state.messages, redoMessage],
    };
  }),

  deleteMediaFile: async (id: string) => {
    set((state) => {
      const updatedFiles = state.mediaBin.filter(f => f.id !== id);
      const newActiveId = state.activeVideoId === id
        ? (updatedFiles[0]?.id ?? null)
        : state.activeVideoId;

      return {
        mediaBin: updatedFiles,
        activeVideoId: newActiveId
      };
    });
    // Persist the deletion to backend
    await get().saveCurrentProject();
  },

  setUploadProgress: (progress: number) =>
    set({ uploadProgress: progress }),

  setIsUploading: (isUploading: boolean) =>
    set({ isUploading: isUploading }),

  addMessage: (message: ChatMessage) =>
    set((state) => {
      // Prevent adding duplicate analysis messages
      if (message.id.startsWith('ai-desc-') && state.messages.some(m => m.id === message.id)) {
        return state;
      }
      return {
        messages: [...state.messages, message]
      };
    }),

  updateMessage: (id: string, updates: Partial<ChatMessage>) =>
    set((state) => ({
      messages: state.messages.map(msg =>
        msg.id === id ? { ...msg, ...updates } : msg
      )
    })),

  handleSuccessfulEdit: (videoId, newUrl, messageId, messageContent) => set(state => {
    // Update the assistant's message with the final content and the new video URL
    // NO LONGER updating mediaBin automatically - user must click "Add to Media" button
    const newMessages = state.messages.map(msg => {
      if (msg.id === messageId) {
        return {
          ...msg,
          content: messageContent,
          status: 'completed' as const,
          timestamp: new Date(),
          videoUrl: newUrl
        };
      }
      return msg;
    });

    return {
      messages: newMessages,
    };
  }),

  addEditedMediaToLibrary: (url, filename, mediaType) => set(state => {
    console.log('addEditedMediaToLibrary called with:', { url, filename, mediaType });
    const newFile: MediaFile = {
      id: `edited-${Date.now()}`,
      filename: filename,
      url: url,
      type: mediaType === 'video' ? 'video/mp4' : 'audio/mp3',
      mediaType: mediaType,
      uploadedAt: new Date(),
      description: `Edited ${mediaType}`,
      isAnalyzing: false,
      versionHistory: [url],
      redoHistory: [],
    };
    console.log('Created new file:', newFile);

    return {
      mediaBin: [...state.mediaBin, newFile],
    };
  }),

  clearChat: async () => {
    set({
      messages: [],
      currentThreadId: null,
    });
    // Persist the cleared chat to backend
    await get().saveCurrentProject();
  },

  renameMediaFile: (id: string, newFilename: string) =>
    set((state) => ({
      mediaBin: state.mediaBin.map(file =>
        file.id === id ? { ...file, filename: newFilename } : file
      )
    })),
  updateMediaFileDescription: (id: string, description: string) =>
    set((state) => ({
      mediaBin: state.mediaBin.map(file =>
        file.id === id ? { ...file, description: description } : file
      )
    })),

  setPlaybackState: (updates) => set(state => ({
    playbackState: { ...state.playbackState, ...updates }
  })),

  setActiveVideoVersion: (videoId, url) => set(state => {
    const newMediaBin = state.mediaBin.map(file => {
      if (file.id === videoId) {
        // This is different from a new edit; it doesn't create a new version in history,
        // it just sets the currently viewed URL for the main player.
        return { ...file, url: url };
      }
      return file;
    });
    return {
      mediaBin: newMediaBin,
      // When we load an old version, we should seek to the start and be paused.
      playbackState: { isPlaying: false, currentTime: 0 },
    };
  }),
  setIsThinking: (isThinking) => set({ isThinking }),
  login: (user, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userEmail', user.email);
    set({ isAuthenticated: true, user, token, authStatus: 'authenticated' });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    set({
      isAuthenticated: false,
      user: null,
      token: null,
      authStatus: 'unauthenticated',
      activeVideoId: null,
      activeAudioId: null,
      mediaBin: [],
      currentProject: null,
      projects: [],
      savedVideos: [],
      messages: [
        {
          id: 'init',
          role: 'assistant',
          content: "Welcome! Upload a video and let's start editing together.",
          timestamp: new Date(),
        },
      ]
    });
  },
  setAuthStatus: (status) => set({ authStatus: status }),

  // ==================== PROJECT MANAGEMENT ====================

  loadProjects: async () => {
    set({ isProjectLoading: true });
    const { user } = get();
    if (!user) {
      console.error('No user logged in');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/projects/?user_email=${encodeEmail(user.email)}`);
      if (response.ok) {
        let projects = await response.json();

        // If user has no projects, create a default one
        if (projects.length === 0) {
          console.log('No projects found, creating default project...');
          const defaultProject = await get().createProject('My First Project');
          projects = [defaultProject];
        }

        set({ projects });

        // If no current project and user has projects, load the first one
        if (!get().currentProject && projects.length > 0) {
          await get().switchProject(projects[0].id);
        }

        // Load saved videos (global, not per-project)
        await get().loadSavedVideos();
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      set({ isProjectLoading: false });
    }
  },

  createProject: async (name: string) => {
    const { user } = get();
    if (!user) throw new Error('User not authenticated');

    set({ isProjectLoading: true });
    try {
      const response = await fetch(`${API_URL}/api/projects/?user_email=${encodeEmail(user.email)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });

      if (response.ok) {
        const newProject = await response.json();
        set(state => ({
          projects: [...state.projects, newProject],
          isProjectLoading: false
        }));
        return newProject;
      } else {
        throw new Error('Failed to create project');
      }
    } catch (error) {
      set({ isProjectLoading: false });
      throw error;
    }
  },

  switchProject: async (projectId: number) => {
    const { user, saveCurrentProject } = get();
    if (!user) return;

    // Save current project before switching
    await saveCurrentProject();

    set({ isProjectLoading: true });
    try {
      const response = await fetch(`${API_URL}/api/projects/${projectId}?user_email=${encodeEmail(user.email)}`);
      if (response.ok) {
        const project = await response.json();

        // Parse project data
        const mediaBin = JSON.parse(project.media_bin || '[]');
        const messages = JSON.parse(project.chat_history || '[]').map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));

        set({
          currentProject: project,
          mediaBin,
          messages: messages.length > 0 ? messages : [{
            id: 'init',
            role: 'assistant',
            content: "Welcome! Upload a video and let's start editing together.",
            timestamp: new Date(),
          }],
          activeVideoId: null,
          activeAudioId: null,
          isProjectLoading: false
        });
      }
    } catch (error) {
      console.error('Failed to switch project:', error);
      set({ isProjectLoading: false });
    }
  },

  saveCurrentProject: async () => {
    const { currentProject, mediaBin, messages, user } = get();
    if (!currentProject || !user) return;

    try {
      // Serialize current state
      const mediaBinJson = JSON.stringify(mediaBin);
      const chatHistoryJson = JSON.stringify(messages);

      await fetch(`${API_URL}/api/projects/${currentProject.id}?user_email=${encodeEmail(user.email)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_bin: mediaBinJson,
          chat_history: chatHistoryJson
        })
      });
    } catch (error) {
      console.error('Failed to save project:', error);
    }
  },

  deleteProject: async (projectId: number) => {
    const { user } = get();
    if (!user) return;

    try {
      const response = await fetch(`${API_URL}/api/projects/${projectId}?user_email=${encodeEmail(user.email)}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        set(state => ({
          projects: state.projects.filter(p => p.id !== projectId),
          currentProject: state.currentProject?.id === projectId ? null : state.currentProject
        }));
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  },

  // ==================== SAVED VIDEOS (GLOBAL) ====================

  saveVideo: async (videoUrl: string, filename: string, description?: string) => {
    const { user } = get();
    if (!user) {
      console.error('No user logged in');
      return;
    }

    console.log('saveVideo called:', { videoUrl, filename, description, userEmail: user.email });

    try {
      const response = await fetch(
        `/api/saved-videos/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename,
            url: videoUrl,
            description,
            user_email: user.email,
          })
        }
      );

      console.log('saveVideo response status:', response.status);

      if (response.ok) {
        const savedVideo = await response.json();
        console.log('Video saved successfully:', savedVideo);
        set(state => {
          const newSavedVideos = [...state.savedVideos, savedVideo];
          console.log('Updated savedVideos:', newSavedVideos);
          return { savedVideos: newSavedVideos };
        });
      } else {
        const errorText = await response.text();
        console.error('Failed to save video. Status:', response.status, 'Error:', errorText);
        throw new Error(`Failed to save video: ${errorText}`);
      }
    } catch (error) {
      console.error('Failed to save video:', error);
      throw error;
    }
  },

  loadSavedVideos: async () => {
    const { user } = get();
    if (!user) {
      console.log('loadSavedVideos: No user logged in');
      return;
    }

    console.log('loadSavedVideos: Loading for user:', user.email);

    try {
      const response = await fetch(
        `/api/saved-videos/?user_email=${encodeEmail(user.email)}`
      );

      console.log('loadSavedVideos response status:', response.status);

      if (response.ok) {
        const savedVideos = await response.json();
        console.log('loadSavedVideos: Loaded videos:', savedVideos);
        set({ savedVideos });
      } else {
        const errorText = await response.text();
        console.error('loadSavedVideos error:', errorText);
      }
    } catch (error) {
      console.error('loadSavedVideos error:', error);
    }
  },

  deleteSavedVideo: async (videoId: number) => {
    const { user } = get();
    if (!user) return;

    try {
      const response = await fetch(
        `/api/saved-videos/?user_email=${encodeEmail(user.email)}&video_id=${videoId}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        set(state => ({
          savedVideos: state.savedVideos.filter(v => v.id !== videoId)
        }));
      }
    } catch (error) {
      console.error('Failed to delete video:', error);
    }
  },
}));
