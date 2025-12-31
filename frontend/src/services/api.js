import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Health check
export const healthCheck = () => api.get('/health');

// Workflow state
export const getWorkflowState = () => api.get('/api/workflow/state');

// Trend discovery
export const searchTrends = (query, niche = 'general', limit = 10) => 
  api.post('/api/trends/search', { query, niche, limit });

export const selectTrend = (trend) => 
  api.post('/api/trends/select', trend);

// Script generation
export const generateScript = (topic, description, tone = 'professional', length = 'short') =>
  api.post('/api/script/generate', { 
    query: topic, 
    description, 
    tone, 
    length,
    use_crewai: false 
  });

export const updateScript = (content) =>
  api.post('/api/script/update', { content });

export const approveScript = () =>
  api.post('/api/script/approve');

// Audio generation
export const getAvailableVoices = () =>
  api.get('/api/voices');

export const generateAudio = (text, voiceId, stability = 0.5, similarityBoost = 0.75) =>
  api.post('/api/audio/generate', {
    voice_id: voiceId,
    stability,
    similarity_boost: similarityBoost
  });

export const approveAudio = () =>
  api.post('/api/audio/approve');

// Asset management
export const uploadAvatar = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/assets/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const uploadLogo = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/assets/logo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const uploadBackground = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/assets/background', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const listAssets = (assetType) =>
  api.get(`/api/assets/list/${assetType}`);

// Video generation
export const generateVideo = (useHeygem = true, quality = 'high') =>
  api.post('/api/video/generate', {
    use_heygem: useHeygem,
    quality
  });

export const getVideoProgress = (projectId) =>
  api.get(`/api/video/progress/${projectId}`);

export const approveVideo = () =>
  api.post('/api/video/approve');

// Project management
export const createProject = (name) =>
  api.post('/api/projects/create', null, { params: { name } });

export const listProjects = () =>
  api.get('/api/projects');

// Settings
export const getOllamaModels = () =>
  api.get('/api/settings/ollama/models');

export const changeOllamaModel = (modelName) =>
  api.post('/api/settings/ollama/change-model', null, { params: { model_name: modelName } });

// Error handler
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
