import { create } from 'zustand';
import * as api from '../services/api';

const useWorkflowStore = create((set, get) => ({
  // State
  currentStep: 'trends',
  steps: [
    { id: 'trends', name: 'Trends', description: 'Discover trending topics' },
    { id: 'script', name: 'Script', description: 'Generate your script' },
    { id: 'audio', name: 'Audio', description: 'Create voiceover' },
    { id: 'assets', name: 'Assets', description: 'Configure visuals' },
    { id: 'video', name: 'Video', description: 'Generate video' },
    { id: 'complete', name: 'Complete', description: 'Review & export' },
  ],
  
  projectId: null,
  isLoading: false,
  error: null,
  
  // Data
  trends: [],
  selectedTrend: null,
  script: { content: '', title: '', duration: 0 },
  audio: { path: '', url: '', duration: 0 },
  assets: { avatar: null, logo: null, background: null },
  video: { outputPath: '', url: '', progress: 0 },
  
  voices: [],
  availableModels: [],
  
  // Actions
  setCurrentStep: (step) => set({ currentStep: step }),
  
  nextStep: () => {
    const { currentStep, steps } = get();
    const currentIndex = steps.findIndex(s => s.id === currentStep);
    if (currentIndex < steps.length - 1) {
      set({ currentStep: steps[currentIndex + 1].id });
    }
  },
  
  previousStep: () => {
    const { currentStep, steps } = get();
    const currentIndex = steps.findIndex(s => s.id === currentStep);
    if (currentIndex > 0) {
      set({ currentStep: steps[currentIndex - 1].id });
    }
  },
  
  // Trend actions
  searchTrends: async (query, niche = 'general') => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.searchTrends(query, niche, 10);
      set({ trends: response.data, isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  selectTrend: async (trend) => {
    set({ isLoading: true, error: null });
    try {
      await api.selectTrend(trend);
      set({ selectedTrend: trend, isLoading: false });
      get().nextStep();
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  // Script actions
  generateScript: async (tone = 'professional', length = 'short') => {
    const { selectedTrend } = get();
    if (!selectedTrend) throw new Error('No trend selected');
    
    set({ isLoading: true, error: null });
    try {
      const response = await api.generateScript(
        selectedTrend.title,
        selectedTrend.description || '',
        tone,
        length
      );
      set({ 
        script: { 
          content: response.data.content, 
          title: response.data.title,
          duration: response.data.duration_estimate 
        },
        isLoading: false 
      });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  updateScript: async (content) => {
    try {
      await api.updateScript(content);
      set({ script: { ...get().script, content } });
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  approveScript: async () => {
    try {
      await api.approveScript();
      get().nextStep();
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Audio actions
  loadVoices: async () => {
    try {
      const response = await api.getAvailableVoices();
      set({ voices: response.data });
    } catch (error) {
      console.error('Failed to load voices:', error);
    }
  },
  
  generateAudio: async (voiceId, stability = 0.5, similarityBoost = 0.75) => {
    const { script } = get();
    if (!script.content) throw new Error('No script available');
    
    set({ isLoading: true, error: null });
    try {
      const response = await api.generateAudio(
        script.content,
        voiceId,
        stability,
        similarityBoost
      );
      set({ 
        audio: {
          path: response.data.path,
          url: response.data.url,
          duration: response.data.duration
        },
        isLoading: false 
      );
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  approveAudio: async () => {
    try {
      await api.approveAudio();
      get().nextStep();
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Asset actions
  uploadAvatar: async (file) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.uploadAvatar(file);
      set({ 
        assets: { ...get().assets, avatar: response.data.avatar },
        isLoading: false 
      });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  uploadLogo: async (file) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.uploadLogo(file);
      set({ 
        assets: { ...get().assets, logo: response.data.logo },
        isLoading: false 
      });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  uploadBackground: async (file) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.uploadBackground(file);
      set({ 
        assets: { ...get().assets, background: response.data.background },
        isLoading: false 
      });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  // Video actions
  generateVideo: async (useHeygem = true, quality = 'high') => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.generateVideo(useHeygem, quality);
      set({ 
        video: {
          outputPath: response.data.path,
          url: response.data.url,
          progress: 100
        },
        isLoading: false
      });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },
  
  // Project actions
  createProject: async (name = 'New Project') => {
    try {
      const response = await api.createProject(name);
      set({ projectId: response.data.project_id });
      return response.data;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Settings
  loadModels: async () => {
    try {
      const response = await api.getOllamaModels();
      set({ availableModels: response.data });
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  },
  
  // Utility
  resetError: () => set({ error: null }),
  
  reset: () => {
    set({
      currentStep: 'trends',
      projectId: null,
      isLoading: false,
      error: null,
      trends: [],
      selectedTrend: null,
      script: { content: '', title: '', duration: 0 },
      audio: { path: '', url: '', duration: 0 },
      assets: { avatar: null, logo: null, background: null },
      video: { outputPath: '', url: '', progress: 0 },
    });
  },
}));

export default useWorkflowStore;
