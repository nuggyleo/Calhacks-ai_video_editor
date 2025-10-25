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
  videoId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: 'pending' | 'completed' | 'error';
  videoUrl?: string; // Add optional video URL
}

interface AppState {
  // Media files
  mediaFiles: MediaFile[];
  currentVideoUrl: string | null;
  currentVideoId: string | null;
  
  // Upload state
  isUploading: boolean;
  uploadProgress: number;
  
  // Chat/Messages
  messages: ChatMessage[];
  currentThreadId: string | null;
  
  // Actions
  addMediaFile: (file: Omit<MediaFile, 'versionHistory' | 'redoHistory'>) => void;
  setCurrentVideo: (url: string, id: string) => void;
  revertToPreviousVersion: (videoId: string) => void;
  redoLastAction: (videoId: string) => void;
  deleteMediaFile: (id: string) => void;
  setUploadProgress: (progress: number) => void;
  setIsUploading: (isUploading: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  getMessagesByVideoId: (videoId: string) => ChatMessage[];
  deleteMessagesForVideo: (videoId: string) => void;
  renameMediaFile: (id: string, newFilename: string) => void;
  updateMediaFileDescription: (id: string, description: string) => void;
  setCurrentVideoUrl: (url: string, videoId: string) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  mediaFiles: [],
  currentVideoUrl: null,
  currentVideoId: null,
  isUploading: false,
  uploadProgress: 0,
  messages: [],
  currentThreadId: null,
  
  addMediaFile: (file) => 
    set((state) => {
      const newFile: MediaFile = {
        ...file,
        versionHistory: [file.url], // Start history with the original URL
        redoHistory: [],            // Redo history starts empty
      };
      return { 
        mediaFiles: [...state.mediaFiles, newFile],
        currentVideoUrl: newFile.url,
        currentVideoId: newFile.id
      };
    }),
    
  setCurrentVideo: (url: string, id: string) => 
    set((state) => {
      const file = state.mediaFiles.find(f => f.id === id);
      const history = file ? [...file.versionHistory, url] : [url];
      return {
        currentVideoUrl: url, 
        currentVideoId: id,
        mediaFiles: state.mediaFiles.map(f => 
          f.id === id ? { ...f, versionHistory: history } : f
        )
      };
    }),
  
  revertToPreviousVersion: (videoId) => set((state) => {
    const file = state.mediaFiles.find(f => f.id === videoId);
    if (!file || file.versionHistory.length <= 1) return state; // Cannot revert original

    const lastVersion = file.versionHistory[file.versionHistory.length - 1];
    const newHistory = file.versionHistory.slice(0, -1);
    const previousUrl = newHistory[newHistory.length - 1];
    
    // Move the reverted version to the redo stack
    const newRedoHistory = [lastVersion, ...file.redoHistory];

    const newMediaFiles = state.mediaFiles.map(f => 
      f.id === videoId ? { ...f, versionHistory: newHistory, redoHistory: newRedoHistory } : f
    );

    const revertMessage: ChatMessage = {
      id: `revert-${Date.now()}`,
      videoId: videoId,
      role: 'assistant',
      content: '↩️ Video has been reverted to the previous version.',
      timestamp: new Date(),
      status: 'completed',
    };

    return {
      mediaFiles: newMediaFiles,
      currentVideoUrl: previousUrl,
      messages: [...state.messages, revertMessage],
    };
  }),

  redoLastAction: (videoId) => set((state) => {
    const file = state.mediaFiles.find(f => f.id === videoId);
    if (!file || file.redoHistory.length === 0) return state; // Nothing to redo

    const nextVersion = file.redoHistory[0];
    const newRedoHistory = file.redoHistory.slice(1);
    
    // Move the redone version back to the version history
    const newHistory = [...file.versionHistory, nextVersion];

    const newMediaFiles = state.mediaFiles.map(f =>
      f.id === videoId ? { ...f, versionHistory: newHistory, redoHistory: newRedoHistory } : f
    );

    const redoMessage: ChatMessage = {
      id: `redo-${Date.now()}`,
      videoId: videoId,
      role: 'assistant',
      content: '↪️ Redo successful. Restored the reverted version.',
      timestamp: new Date(),
      status: 'completed',
    };

    return {
      mediaFiles: newMediaFiles,
      currentVideoUrl: nextVersion,
      messages: [...state.messages, redoMessage],
    };
  }),

  deleteMediaFile: (id: string) =>
    set((state) => {
      const updatedFiles = state.mediaFiles.filter(f => f.id !== id);
      const newCurrentId = state.currentVideoId === id 
        ? (updatedFiles[0]?.id ?? null)
        : state.currentVideoId;
      const newCurrentUrl = state.currentVideoId === id
        ? (updatedFiles[0]?.url ?? null)
        : state.currentVideoUrl;
      
      return {
        mediaFiles: updatedFiles,
        currentVideoId: newCurrentId,
        currentVideoUrl: newCurrentUrl
      };
    }),
    
  setUploadProgress: (progress: number) => 
    set({ uploadProgress: progress }),
    
  setIsUploading: (isUploading: boolean) => 
    set({ isUploading: isUploading }),
    
  addMessage: (message: ChatMessage) =>
    set((state) => ({
      messages: [...state.messages, message]
    })),
    
  updateMessage: (id: string, updates: Partial<ChatMessage>) =>
    set((state) => ({
      messages: state.messages.map(msg =>
        msg.id === id ? { ...msg, ...updates } : msg
      )
    })),
    
  getMessagesByVideoId: (videoId: string) =>
    get().messages.filter(msg => msg.videoId === videoId),
    
  deleteMessagesForVideo: (videoId: string) =>
    set((state) => ({
      messages: state.messages.filter(msg => msg.videoId !== videoId)
    })),
  renameMediaFile: (id: string, newFilename: string) =>
    set((state) => ({
      mediaFiles: state.mediaFiles.map(file =>
        file.id === id ? { ...file, filename: newFilename } : file
      )
    })),
  updateMediaFileDescription: (id: string, description: string) =>
    set((state) => ({
      mediaFiles: state.mediaFiles.map(file =>
        file.id === id ? { ...file, description: description } : file
      )
    })),
  setCurrentVideoUrl: (url, videoId) => set(state => {
    const newMediaFiles = state.mediaFiles.map(file => {
      if (file.id === videoId) {
        // A new edit clears the redo history
        return { ...file, versionHistory: [...file.versionHistory, url], redoHistory: [] };
      }
      return file;
    });
    return {
      currentVideoUrl: url,
      mediaFiles: newMediaFiles,
    };
  }),
}));
