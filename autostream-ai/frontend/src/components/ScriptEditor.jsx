import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Sparkles, 
  Edit3, 
  Clock, 
  Type, 
  RefreshCw,
  Loader2,
  Check,
  ChevronRight,
  Copy,
  Save
} from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';
import toast from 'react-hot-toast';

const ScriptEditor = () => {
  const { 
    generateScript, 
    updateScript, 
    approveScript, 
    script, 
    selectedTrend,
    isLoading,
    setCurrentStep
  } = useWorkflowStore();
  
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('short');
  const [editedContent, setEditedContent] = useState(script.content || '');
  const [hasChanges, setHasChanges] = useState(false);
  const [generated, setGenerated] = useState(false);

  const tones = [
    { id: 'professional', label: 'Professional', description: 'Informative and authoritative' },
    { id: 'casual', label: 'Casual', description: 'Friendly and conversational' },
    { id: 'funny', label: 'Funny', description: 'Humorous and entertaining' },
    { id: 'dramatic', label: 'Dramatic', description: 'Suspenseful and emotional' },
    { id: 'inspirational', label: 'Inspirational', description: 'Motivating and uplifting' },
  ];

  const lengths = [
    { id: 'short', label: 'Short', duration: '30-60 sec', words: '75-150 words' },
    { id: 'medium', label: 'Medium', duration: '1-2 min', words: '150-300 words' },
    { id: 'long', label: 'Long', duration: '2-5 min', words: '300-750 words' },
  ];

  useEffect(() => {
    if (script.content) {
      setEditedContent(script.content);
      setGenerated(true);
    }
  }, [script.content]);

  const handleGenerate = async () => {
    try {
      await generateScript(tone, length);
      setGenerated(true);
      toast.success('Script generated successfully!');
    } catch (error) {
      toast.error('Failed to generate script');
    }
  };

  const handleEdit = (e) => {
    setEditedContent(e.target.value);
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      await updateScript(editedContent);
      setHasChanges(false);
      toast.success('Script saved!');
    } catch (error) {
      toast.error('Failed to save script');
    }
  };

  const handleApprove = async () => {
    if (hasChanges) {
      await handleSave();
    }
    try {
      await approveScript();
      toast.success('Script approved!');
    } catch (error) {
      toast.error('Failed to proceed');
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(editedContent);
    toast.success('Copied to clipboard!');
  };

  const wordCount = editedContent.split(/\s+/).filter(Boolean).length;
  const duration = Math.round((wordCount / 150) * 60); // ~150 words per minute

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-5xl mx-auto"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 
                    border border-emerald-500/30 flex items-center justify-center"
        >
          <FileText className="w-8 h-8 text-emerald-400" />
        </motion.div>
        <h1 className="text-2xl font-bold text-white mb-2">Script Generator</h1>
        <p className="text-dark-400">
          {selectedTrend 
            ? `Creating script for: "${selectedTrend.title}"` 
            : 'Generate a viral-worthy script using AI'}
        </p>
      </div>

      {/* Configuration */}
      {!generated && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card mb-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-400" />
            Script Settings
          </h2>
          
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Tone selection */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-3">
                Script Tone
              </label>
              <div className="grid grid-cols-1 gap-2">
                {tones.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTone(t.id)}
                    className={`p-3 rounded-xl text-left transition-all duration-300
                              ${tone === t.id 
                                ? 'bg-primary-500/20 border border-primary-500/50' 
                                : 'bg-dark-800/50 border border-dark-700 hover:border-dark-600'
                              }`}
                  >
                    <span className={`font-medium ${tone === t.id ? 'text-primary-400' : 'text-white'}`}>
                      {t.label}
                    </span>
                    <p className="text-xs text-dark-400 mt-1">{t.description}</p>
                  </button>
                ))}
              </div>
            </div>
            
            {/* Length selection */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-3">
                Script Length
              </label>
              <div className="grid grid-cols-1 gap-2">
                {lengths.map((l) => (
                  <button
                    key={l.id}
                    onClick={() => setLength(l.id)}
                    className={`p-3 rounded-xl text-left transition-all duration-300
                              ${length === l.id 
                                ? 'bg-primary-500/20 border border-primary-500/50' 
                                : 'bg-dark-800/50 border border-dark-700 hover:border-dark-600'
                              }`}
                  >
                    <span className={`font-medium ${length === l.id ? 'text-primary-400' : 'text-white'}`}>
                      {l.label}
                    </span>
                    <div className="flex gap-4 mt-1 text-xs text-dark-400">
                      <span>{l.duration}</span>
                      <span>{l.words}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          <div className="flex justify-end mt-6">
            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="btn-primary flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Script
                </>
              )}
            </button>
          </div>
        </motion.div>
      )}

      {/* Script editor */}
      <AnimatePresence>
        {generated && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* Script info bar */}
            <div className="card mb-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Type className="w-4 h-4 text-dark-400" />
                    <span className="text-dark-300">
                      <span className="font-semibold text-white">{wordCount}</span> words
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-dark-400" />
                    <span className="text-dark-300">
                      <span className="font-semibold text-white">{duration}</span> sec
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Edit3 className="w-4 h-4 text-dark-400" />
                    <span className={`badge ${hasChanges ? 'badge-warning' : 'badge-success'}`}>
                      {hasChanges ? 'Unsaved changes' : 'Saved'}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={copyToClipboard}
                    className="btn-ghost flex items-center gap-2 text-sm"
                  >
                    <Copy className="w-4 h-4" />
                    Copy
                  </button>
                  <button
                    onClick={handleGenerate}
                    disabled={isLoading}
                    className="btn-secondary flex items-center gap-2 text-sm"
                  >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    Regenerate
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={!hasChanges || isLoading}
                    className="btn-ghost flex items-center gap-2 text-sm"
                  >
                    <Save className="w-4 h-4" />
                    Save
                  </button>
                </div>
              </div>
            </div>

            {/* Script content */}
            <div className="card">
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Script Content
              </label>
              <textarea
                value={editedContent}
                onChange={handleEdit}
                className="script-editor h-80"
                placeholder="Your script will appear here..."
              />
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-between mt-6">
              <button
                onClick={() => setCurrentStep('trends')}
                className="btn-ghost"
              >
                ← Back to Trends
              </button>
              
              <div className="flex items-center gap-4">
                {hasChanges && (
                  <span className="text-sm text-amber-400">
                    Please save your changes before continuing
                  </span>
                )}
                <button
                  onClick={handleApprove}
                  disabled={isLoading}
                  className="btn-primary flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving...
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
    </motion.div>
  );
};

export default ScriptEditor;
