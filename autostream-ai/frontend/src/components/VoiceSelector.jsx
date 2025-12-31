import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { 
  Volume2, Play, Pause, Loader2, Check, ChevronRight, Music, Sliders, Mic,
  Plus, Upload, Trash2, Sparkles, Brain, Wand2, Settings, Users, Star,
  VolumeX, Info, Download, Copy
} from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';
import toast from 'react-hot-toast';
import * as api from '../services/api';

const VoiceSelector = () => {
  const { 
    loadVoices, voices, generateAudio, approveAudio, audio, script,
    isLoading, setCurrentStep
  } = useWorkflowStore();
  
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [selectedEngine, setSelectedEngine] = useState('all');
  const [isPlaying, setIsPlaying] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [engines, setEngines] = useState({});
  const [clonedVoices, setClonedVoices] = useState([]);
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [showEngineInfo, setShowEngineInfo] = useState(false);
  const [engineSettings, setEngineSettings] = useState({
    text_temp: 0.7,
    waveform_temp: 0.7,
    stability: 0.5,
    similarity_boost: 0.75
  });
  const [uploadingClone, setUploadingClone] = useState(false);
  const audioRef = useRef(null);

  // Load engines and voices on mount
  useEffect(() => {
    loadEngines();
    loadVoices();
    loadClonedVoices();
  }, []);

  useEffect(() => {
    if (audio.path && audioRef.current) {
      audioRef.current.src = audio.path;
    }
  }, [audio]);

  const loadEngines = async () => {
    try {
      const response = await api.getAvailableVoices();
      // This would be an enhanced endpoint in a real implementation
      setEngines({
        piper: { name: 'Piper', description: 'Fast, high-quality offline TTS', available: true, free: true, quality: 'high' },
        bark: { name: 'Bark', description: 'Expressive with laughter & emotions', available: true, free: true, quality: 'very_high', features: ['laughter', 'sighs', 'emotions'] },
        xtts: { name: 'Coqui XTTS', description: 'Voice cloning support', available: true, free: true, quality: 'very_high', features: ['voice_cloning'] },
        elevenlabs: { name: 'ElevenLabs', description: 'Premium AI voices', available: false, free: false, quality: 'premium' },
        gtts: { name: 'Google TTS', description: 'Basic online TTS', available: true, free: true, quality: 'basic' }
      });
    } catch (error) {
      console.error('Failed to load engines:', error);
    }
  };

  const loadClonedVoices = async () => {
    // This would call an API endpoint in a real implementation
    setClonedVoices([
      // Sample cloned voices for demo
    ]);
  };

  const handlePlayPreview = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleGenerate = async () => {
    if (!selectedVoice) {
      toast.error('Please select a voice');
      return;
    }
    
    try {
      await generateAudio(selectedVoice, engineSettings.stability, engineSettings.similarity_boost);
      setGenerated(true);
      toast.success('Audio generated successfully!');
    } catch (error) {
      toast.error('Failed to generate audio');
    }
  };

  const handleApprove = async () => {
    try {
      await approveAudio();
      toast.success('Audio approved!');
    } catch (error) {
      toast.error('Failed to proceed');
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleCreateClone = async (files, cloneName) => {
    setUploadingClone(true);
    try {
      // In a real implementation, this would call the API
      toast.success(`Creating voice clone "${cloneName}"...`);
      setShowCloneModal(false);
      // After creation, reload cloned voices
      loadClonedVoices();
    } catch (error) {
      toast.error('Failed to create voice clone');
    } finally {
      setUploadingClone(false);
    }
  };

  const getFilteredVoices = () => {
    let filtered = voices;
    if (selectedEngine !== 'all') {
      filtered = voices.filter(v => v.engine === selectedEngine);
    }
    // Add cloned voices
    const allVoices = [...filtered];
    clonedVoices.forEach(clone => {
      if (selectedEngine === 'all' || selectedEngine === 'xtts') {
        allVoices.push({
          ...clone,
          engine: 'xtts',
          description: clone.description || 'Custom voice clone',
          isCloned: true
        });
      }
    });
    return allVoices;
  };

  const getEngineColor = (engine) => {
    const colors = {
      piper: 'from-blue-500 to-cyan-500',
      bark: 'from-purple-500 to-pink-500',
      xtts: 'from-orange-500 to-red-500',
      elevenlabs: 'from-emerald-500 to-teal-500',
      gtts: 'from-gray-500 to-gray-400'
    };
    return colors[engine] || 'from-primary-500 to-purple-500';
  };

  const getEngineIcon = (engine) => {
    const icons = {
      piper: Brain,
      bark: Sparkles,
      xtts: Users,
      elevenlabs: Star,
      gtts: Volume2
    };
    return icons[engine] || Volume2;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-6xl mx-auto"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 
                    border border-purple-500/30 flex items-center justify-center"
        >
          <Volume2 className="w-8 h-8 text-purple-400" />
        </motion.div>
        <h1 className="text-2xl font-bold text-white mb-2">Voice Studio</h1>
        <p className="text-dark-400">
          Choose from multiple TTS engines including Bark's expressive voices and voice cloning
        </p>
      </div>

      {/* Engine Selection Tabs */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary-400" />
            TTS Engines
          </h2>
          <button
            onClick={() => setShowEngineInfo(!showEngineInfo)}
            className="btn-ghost text-sm flex items-center gap-1"
          >
            <Info className="w-4 h-4" />
            Engine Info
          </button>
        </div>

        <AnimatePresence>
          {showEngineInfo && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 p-4 bg-dark-900/50 rounded-xl"
            >
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(engines).map(([key, engine]) => {
                  const Icon = getEngineIcon(key);
                  return (
                    <div key={key} className="p-3 bg-dark-800/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className={`w-4 h-4 bg-gradient-to-r ${getEngineColor(key)} bg-clip-text text-transparent`} />
                        <span className="font-medium text-white">{engine.name}</span>
                        {!engine.available && (
                          <span className="badge badge-warning text-xs">Install</span>
                        )}
                      </div>
                      <p className="text-xs text-dark-400">{engine.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`badge ${engine.free ? 'badge-success' : 'badge-primary'} text-xs`}>
                          {engine.free ? 'Free' : 'Paid'}
                        </span>
                        <span className="text-xs text-dark-500">Quality: {engine.quality}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedEngine('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedEngine === 'all' 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
            }`}
          >
            All Voices
          </button>
          {Object.entries(engines).map(([key, engine]) => {
            const Icon = getEngineIcon(key);
            return (
              <button
                key={key}
                onClick={() => setSelectedEngine(key)}
                className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                  selectedEngine === key 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                {engine.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Clone Voice Button */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Users className="w-5 h-5 text-orange-400" />
              Voice Cloning
            </h2>
            <p className="text-sm text-dark-400">Create custom voices from reference audio samples</p>
          </div>
          <button
            onClick={() => setShowCloneModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Clone
          </button>
        </div>

        {clonedVoices.length > 0 && (
          <div className="mt-4 grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {clonedVoices.map((clone) => (
              <div key={clone.id} className="p-3 bg-dark-800/50 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-orange-400" />
                  <div>
                    <p className="font-medium text-white text-sm">{clone.name}</p>
                    <p className="text-xs text-dark-400">{clone.description}</p>
                  </div>
                </div>
                <button className="p-2 hover:bg-dark-700 rounded-lg text-dark-400 hover:text-red-400">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Voice Selection Grid */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Mic className="w-5 h-5 text-primary-400" />
          Available Voices ({getFilteredVoices().length})
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {getFilteredVoices().map((voice) => {
            const Icon = getEngineIcon(voice.engine || 'gtts');
            return (
              <motion.div
                key={voice.id}
                onClick={() => setSelectedVoice(voice.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`p-4 rounded-xl cursor-pointer transition-all ${
                  selectedVoice === voice.id 
                    ? 'bg-primary-500/20 border-2 border-primary-500' 
                    : 'bg-dark-800/50 border border-dark-700 hover:border-dark-600'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getEngineColor(voice.engine || 'gtts')} 
                                  flex items-center justify-center`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-medium text-white">{voice.name}</h3>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-dark-400">{voice.gender || 'Neutral'}</span>
                        {voice.isCloned && (
                          <span className="badge badge-warning text-xs">Cloned</span>
                        )}
                      </div>
                    </div>
                  </div>
                  {selectedVoice === voice.id && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center"
                    >
                      <Check className="w-4 h-4 text-white" />
                    </motion.div>
                  )}
                </div>
                <p className="text-sm text-dark-400 mb-2">{voice.description}</p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); copyToClipboard(voice.sample_text || 'Hello, this is a test.'); }}
                    className="text-xs text-dark-500 hover:text-white flex items-center gap-1"
                  >
                    <Copy className="w-3 h-3" />
                    Copy sample
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Engine Settings */}
      {selectedVoice && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card mb-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-emerald-400" />
            Engine Settings
          </h2>

          {/* Bark-specific settings */}
          {selectedVoice.startsWith('bark') && (
            <div className="mb-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h3 className="font-medium text-purple-300">Bark Expressive Settings</h3>
              </div>
              <p className="text-sm text-dark-400 mb-4">
                Bark supports expressive features like laughter, sighs, and emotions. 
                Use special tokens in your script for more control:
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Text Temperature: {engineSettings.text_temp.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={engineSettings.text_temp}
                    onChange={(e) => setEngineSettings(s => ({ ...s, text_temp: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <p className="text-xs text-dark-500 mt-1">Higher = more creative/varied output</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Waveform Temperature: {engineSettings.waveform_temp.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={engineSettings.waveform_temp}
                    onChange={(e) => setEngineSettings(s => ({ ...s, waveform_temp: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <p className="text-xs text-dark-500 mt-1">Higher = more audio variation</p>
                </div>
              </div>
              <div className="mt-4 p-3 bg-dark-900/50 rounded-lg">
                <p className="text-xs text-dark-400 mb-2">Bark Special Tokens (add to script):</p>
                <div className="flex flex-wrap gap-2">
                  {[',', '!?', '...', '[laughter]', '[sighs]', '[music]'].map(token => (
                    <button
                      key={token}
                      onClick={() => copyToClipboard(token)}
                      className="px-2 py-1 bg-dark-700 hover:bg-dark-600 rounded text-xs text-dark-300"
                    >
                      {token}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Standard settings */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Stability: {Math.round(engineSettings.stability * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={engineSettings.stability}
                onChange={(e) => setEngineSettings(s => ({ ...s, stability: parseFloat(e.target.value) }))}
                className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-dark-500 mt-1">Higher = more consistent output</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Similarity Boost: {Math.round(engineSettings.similarity_boost * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={engineSettings.similarity_boost}
                onChange={(e) => setEngineSettings(s => ({ ...s, similarity_boost: parseFloat(e.target.value) }))}
                className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-dark-500 mt-1">Higher = more similar to original voice</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Generate button */}
      <div className="flex justify-center mb-6">
        <button
          onClick={handleGenerate}
          disabled={!selectedVoice || isLoading}
          className="btn-primary flex items-center gap-2 text-lg px-8 py-4"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Wand2 className="w-5 h-5" />
              Generate Audio
            </>
          )}
        </button>
      </div>

      {/* Audio Preview */}
      <AnimatePresence>
        {generated && audio.path && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="card"
          >
            <h2 className="text-lg font-semibold text-white mb-4">Audio Preview</h2>
            
            {/* Waveform visualization */}
            <div className="h-32 bg-gradient-to-r from-dark-900/80 to-dark-800/80 rounded-xl mb-4 flex items-center justify-center overflow-hidden relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="flex items-end justify-center gap-0.5 h-24 px-8">
                  {[...Array(80)].map((_, i) => (
                    <motion.div
                      key={i}
                      animate={{
                        height: isPlaying ? [15, Math.random() * 70 + 20, 15] : 15
                      }}
                      transition={{
                        duration: 0.4,
                        repeat: isPlaying ? Infinity : 0,
                        delay: i * 0.03
                      }}
                      className={`w-1.5 rounded-full ${
                        selectedVoice?.startsWith('bark') 
                          ? 'bg-gradient-to-t from-purple-500 to-pink-500' 
                          : 'bg-gradient-to-t from-primary-500 to-purple-500'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
            
            <audio ref={audioRef} onEnded={handleAudioEnded} className="hidden" />
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={handlePlayPreview}
                  className="w-14 h-14 rounded-full bg-gradient-to-r from-primary-500 to-purple-500 
                           flex items-center justify-center hover:scale-105 transition-transform"
                >
                  {isPlaying ? (
                    <Pause className="w-6 h-6 text-white" />
                  ) : (
                    <Play className="w-6 h-6 text-white ml-1" />
                  )}
                </button>
                <div>
                  <p className="font-medium text-white">Generated Audio</p>
                  <p className="text-sm text-dark-400">
                    {audio.duration ? `${audio.duration.toFixed(1)} seconds` : 'Ready to play'}
                    {audio.voice && ` • ${audio.voice.name}`}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {audio.duration && (
                  <div className="badge badge-success">
                    {Math.round(audio.duration)}s
                  </div>
                )}
                <button className="btn-ghost flex items-center gap-1 text-sm">
                  <Download className="w-4 h-4" />
                  Download
                </button>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-between mt-6 pt-6 border-t border-dark-700">
              <button onClick={() => setCurrentStep('script')} className="btn-ghost">
                ← Back to Script
              </button>
              
              <div className="flex items-center gap-4">
                <button onClick={handleGenerate} disabled={isLoading} className="btn-secondary text-sm">
                  Regenerate
                </button>
                <button onClick={handleApprove} disabled={isLoading} className="btn-primary flex items-center gap-2">
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4" />
                      Approve & Continue
                    </>
                  )}
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* No script warning */}
      {!script.content && (
        <div className="card text-center py-12">
          <Volume2 className="w-16 h-16 mx-auto mb-4 text-dark-600" />
          <p className="text-dark-300 mb-2">No script available</p>
          <p className="text-sm text-dark-500 mb-4">Please complete the script step first</p>
          <button onClick={() => setCurrentStep('script')} className="btn-primary">
            Go to Script
          </button>
        </div>
      )}

      {/* Voice Clone Modal */}
      <AnimatePresence>
        {showCloneModal && (
          <VoiceCloneModal
            onClose={() => setShowCloneModal(false)}
            onCreate={handleCreateClone}
            isLoading={uploadingClone}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Voice Clone Modal Component
const VoiceCloneModal = ({ onClose, onCreate, isLoading }) => {
  const [files, setFiles] = useState([]);
  const [cloneName, setCloneName] = useState('');
  const [description, setDescription] = useState('');

  const onDrop = useDropzone({
    accept: { 'audio/*': ['.wav', '.mp3', '.ogg', '.flac'] },
    maxFiles: 5,
    onDrop: (acceptedFiles) => {
      setFiles(prev => [...prev, ...acceptedFiles]);
    }
  });

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (files.length === 0) {
      toast.error('Please upload at least one reference audio file');
      return;
    }
    if (!cloneName.trim()) {
      toast.error('Please enter a name for your voice clone');
      return;
    }
    onCreate(files, cloneName);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-dark-950/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="relative w-full max-w-lg card"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-dark-700 rounded-lg text-dark-400"
        >
          ✕
        </button>

        <div className="mb-6">
          <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
            <Users className="w-6 h-6 text-orange-400" />
            Create Voice Clone
          </h2>
          <p className="text-dark-400 text-sm">
            Upload reference audio samples to create a custom voice clone using Coqui XTTS
          </p>
        </div>

        <div className="space-y-4">
          {/* Name input */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Voice Name *
            </label>
            <input
              type="text"
              value={cloneName}
              onChange={(e) => setCloneName(e.target.value)}
              placeholder="e.g., My Custom Voice"
              className="input"
            />
          </div>

          {/* Description input */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Description (optional)
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Deep male voice, news anchor style"
              className="input"
            />
          </div>

          {/* File upload */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Reference Audio Files * (1-5 files)
            </label>
            <div
              {...onDrop.getRootProps()}
              className={`upload-zone ${onDrop.isDragActive ? 'upload-zone-active' : ''}`}
            >
              <input {...onDrop.getInputProps()} />
              <Upload className="w-8 h-8 text-dark-400 mb-2" />
              <p className="text-dark-300 font-medium">Drop audio files here</p>
              <p className="text-sm text-dark-500">or click to browse</p>
            </div>

            {/* File list */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Music className="w-5 h-5 text-primary-400" />
                      <span className="text-sm text-white">{file.name}</span>
                      <span className="text-xs text-dark-500">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 hover:bg-dark-700 rounded text-dark-400 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tips */}
          <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
            <h3 className="font-medium text-amber-400 mb-2 flex items-center gap-2">
              <Info className="w-4 h-4" />
              Tips for Best Results
            </h3>
            <ul className="text-sm text-dark-300 space-y-1">
              <li>• Use 3-5 audio samples for best quality</li>
              <li>• Each sample should be 10-30 seconds long</li>
              <li>• Use clear speech without background noise</li>
              <li>• Vary tone and emotion across samples</li>
              <li>• Supported formats: WAV, MP3, OGG, FLAC</li>
            </ul>
          </div>
        </div>

        <div className="flex justify-end gap-4 mt-6 pt-6 border-t border-dark-700">
          <button onClick={onClose} className="btn-ghost">
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isLoading || files.length === 0 || !cloneName.trim()}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Create Voice Clone
              </>
            )}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default VoiceSelector;
