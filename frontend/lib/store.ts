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
  
  // Actions
  addMediaFile: (file: MediaFile) => void;
  setCurrentVideo: (url: string, id: string) => void;
  deleteMediaFile: (id: string) => void;
  setUploadProgress: (progress: number) => void;
  setIsUploading: (isUploading: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  getMessagesByVideoId: (videoId: string) => ChatMessage[];
  deleteMessagesForVideo: (videoId: string) => void;
  renameMediaFile: (id: string, newFilename: string) => void;
  updateMediaFileDescription: (id: string, description: string) => void;
  setCurrentVideoUrl: (url: string) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  mediaFiles: [],
  currentVideoUrl: null,
  currentVideoId: null,
  isUploading: false,
  uploadProgress: 0,
  messages: [],
  
  addMediaFile: (file: MediaFile) => 
    set((state) => ({ 
      mediaFiles: [...state.mediaFiles, file],
      currentVideoUrl: file.url,
      currentVideoId: file.id
    })),
    
  setCurrentVideo: (url: string, id: string) => 
    set({ currentVideoUrl: url, currentVideoId: id }),
  
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
  setCurrentVideoUrl: (url) => set({ currentVideoUrl: url }),
}));
