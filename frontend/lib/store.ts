// Global state management using Zustand
// Manages uploaded media files, video URLs, and upload progress

import { create } from 'zustand';

export interface MediaFile {
  id: string;
  filename: string;
  url: string;
  type: string;
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
  videoUrl?: string; // Add optional video URL
}

interface AppState {
  // Media files
  mediaBin: MediaFile[];
  activeVideoId: string | null;

  // Upload state
  isUploading: boolean;
  uploadProgress: number;

  // Chat/Messages
  messages: ChatMessage[];
  currentThreadId: string | null;
  isThinking: boolean;
  authStatus: 'loading' | 'authenticated' | 'unauthenticated';
  isAuthenticated: boolean;
  user: { email: string } | null;
  token: string | null;
  
  // Actions
  addMediaFile: (file: Omit<MediaFile, 'versionHistory' | 'redoHistory'>) => void;
  setActiveVideoId: (id: string) => void;
  revertToPreviousVersion: (videoId: string) => void;
  redoLastAction: (videoId: string) => void;
  deleteMediaFile: (id: string) => void;
  setUploadProgress: (progress: number) => void;
  setIsUploading: (isUploading: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  handleSuccessfulEdit: (videoId: string, newUrl: string, messageId: string, messageContent: string) => void;
  renameMediaFile: (id: string, newFilename: string) => void;
  updateMediaFileDescription: (id: string, description: string) => void;
  setPlaybackState: (updates: Partial<AppState['playbackState']>) => void;
  setActiveVideoVersion: (videoId: string, url: string) => void;
  setIsThinking: (isThinking: boolean) => void;
  login: (user: { email: string }, token: string) => void;
  logout: () => void;
  setAuthStatus: (status: 'authenticated' | 'unauthenticated') => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  mediaBin: [],
  activeVideoId: null,
  isUploading: false,
  uploadProgress: 0,
  playbackState: { isPlaying: false, currentTime: 0 },
  messages: [],
  isThinking: false,
  authStatus: 'loading',
  isAuthenticated: false,
  user: null,
  token: null,
  
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

  deleteMediaFile: (id: string) =>
    set((state) => {
      const updatedFiles = state.mediaBin.filter(f => f.id !== id);
      const newActiveId = state.activeVideoId === id
        ? (updatedFiles[0]?.id ?? null)
        : state.activeVideoId;

      return {
        mediaBin: updatedFiles,
        activeVideoId: newActiveId
      };
    }),

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
    // 1. Update the media bin with the new URL and version history
    const newMediaBin = state.mediaBin.map(file => {
      if (file.id === videoId) {
        // A new edit clears the redo history
        return { ...file, url: newUrl, versionHistory: [...file.versionHistory, newUrl], redoHistory: [] };
      }
      return file;
    });

    // 2. Update the assistant's message with the final content and the new video URL
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

    // 3. Return the new state in a single, atomic update
    return {
      mediaBin: newMediaBin,
      messages: newMessages,
    };
  }),

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
    set({ isAuthenticated: false, user: null, token: null, authStatus: 'unauthenticated', currentVideoUrl: null, currentVideoId: null, mediaFiles: [], messages: [
      {
        id: 'init',
        role: 'assistant',
        content: "Welcome! Upload a video and let's start editing together.",
        timestamp: new Date(),
      },
    ]});
  },
  setAuthStatus: (status) => set({ authStatus: status }),
}));
