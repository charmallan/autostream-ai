import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Download, 
  Share2, 
  RefreshCw, 
  CheckCircle,
  Loader2,
  Video,
  ChevronRight,
  Settings,
  Zap,
  Sparkles
} from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';
import toast from 'react-hot-toast';

const VideoPreview = () => {
  const { 
    generateVideo, 
    video, 
    assets, 
    audio,
    script,
    approveVideo,
    reset,
    isLoading,
    setCurrentStep
  } = useWorkflowStore();
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [quality, setQuality] = useState('high');
  const [useHeygem, setUseHeygem] = useState(true);
  const videoRef = useRef(null);

  useEffect(() => {
    if (video.url && videoRef.current) {
      videoRef.current.src = video.url;
    }
  }, [video.url]);

  const handleGenerate = async () => {
    try {
      await generateVideo(useHeygem, quality);
      toast.success('Video generated successfully!');
    } catch (error) {
      toast.error('Failed to generate video');
    }
  };

  const handlePlay = () => {
    if (!videoRef.current) return;
    
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleVideoEnded = () => {
    setIsPlaying(false);
  };

  const handleApprove = async () => {
    try {
      await approveVideo();
      toast.success('Video approved!');
    } catch (error) {
      toast.error('Failed to complete');
    }
  };

  const handleDownload = () => {
    if (!video.url) return;
    
    const a = document.createElement('a');
    a.href = video.url;
    a.download = `autostream-video-${Date.now()}.mp4`;
    a.click();
    toast.success('Download started!');
  };

  const handleNewProject = () => {
    reset();
    setCurrentStep('trends');
    toast.success('Started new project!');
  };

  const qualities = [
    { id: 'low', label: '720p', description: 'Faster render' },
    { id: 'medium', label: '1080p', description: 'Balanced' },
    { id: 'high', label: '1080p HD', description: 'High quality' },
    { id: '4k', label: '4K', description: 'Maximum quality' },
  ];

  // Check if ready to generate
  const canGenerate = assets.avatar && audio.path;

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
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-pink-500/20 to-rose-500/20 
                    border border-pink-500/30 flex items-center justify-center"
        >
          <Video className="w-8 h-8 text-pink-400" />
        </motion.div>
        <h1 className="text-2xl font-bold text-white mb-2">Video Generation</h1>
        <p className="text-dark-400">
          Generate your faceless video with AI-powered lip-sync
        </p>
      </div>

      {/* Generation settings */}
      {!video.outputPath && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card mb-6"
        >
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Quality selection */}
            <div>
              <h3 className="font-medium text-white mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5 text-primary-400" />
                Video Quality
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {qualities.map((q) => (
                  <button
                    key={q.id}
                    onClick={() => setQuality(q.id)}
                    className={`p-3 rounded-xl text-left transition-all duration-300
                              ${quality === q.id 
                                ? 'bg-primary-500/20 border border-primary-500/50' 
                                : 'bg-dark-800/50 border border-dark-700 hover:border-dark-600'
                              }`}
                  >
                    <span className={`font-medium ${quality === q.id ? 'text-primary-400' : 'text-white'}`}>
                      {q.label}
                    </span>
                    <p className="text-xs text-dark-400">{q.description}</p>
                  </button>
                ))}
              </div>
            </div>
            
            {/* HeyGem option */}
            <div>
              <h3 className="font-medium text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                Lip-Sync Technology
              </h3>
              <div className="space-y-3">
                <button
                  onClick={() => setUseHeygem(true)}
                  className={`w-full p-4 rounded-xl text-left transition-all duration-300
                            ${useHeygem 
                              ? 'bg-emerald-500/20 border border-emerald-500/50' 
                              : 'bg-dark-800/50 border border-dark-700 hover:border-dark-600'
                            }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center
                                   ${useHeygem ? 'border-emerald-500 bg-emerald-500' : 'border-dark-500'}`}>
                      {useHeygem && <CheckCircle className="w-4 h-4 text-white" />}
                    </div>
                    <div>
                      <span className={`font-medium ${useHeygem ? 'text-emerald-400' : 'text-white'}`}>
                        HeyGem Lip-Sync
                      </span>
                      <p className="text-xs text-dark-400">Realistic avatar lip-sync</p>
                    </div>
                  </div>
                </button>
                
                <button
                  onClick={() => setUseHeygem(false)}
                  className={`w-full p-4 rounded-xl text-left transition-all duration-300
                            ${!useHeygem 
                              ? 'bg-emerald-500/20 border border-emerald-500/50' 
                              : 'bg-dark-800/50 border border-dark-700 hover:border-dark-600'
                            }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center
                                   ${!useHeygem ? 'border-emerald-500 bg-emerald-500' : 'border-dark-500'}`}>
                      {!useHeygem && <CheckCircle className="w-4 h-4 text-white" />}
                    </div>
                    <div>
                      <span className={`font-medium ${!useHeygem ? 'text-emerald-400' : 'text-white'}`}>
                        Static Avatar
                      </span>
                      <p className="text-xs text-dark-400">Simple image overlay</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </div>
          
          {/* Generate button */}
          <div className="flex justify-center mt-6">
            <button
              onClick={handleGenerate}
              disabled={!canGenerate || isLoading}
              className="btn-primary flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Video...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Video
                </>
              )}
            </button>
          </div>
          
          {!canGenerate && (
            <p className="text-center text-sm text-dark-400 mt-4">
              Please complete all previous steps first
            </p>
          )}
        </motion.div>
      )}

      {/* Video preview */}
      <AnimatePresence>
        {video.outputPath && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* Preview card */}
            <div className="card mb-6">
              <div className="aspect-video bg-dark-900 rounded-xl overflow-hidden relative">
                {video.url ? (
                  <>
                    <video
                      ref={videoRef}
                      onEnded={handleVideoEnded}
                      className="w-full h-full object-contain"
                      poster={assets.avatar?.url}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-dark-900/80 via-transparent to-transparent" />
                    
                    {/* Play button overlay */}
                    {!isPlaying && (
                      <motion.button
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        onClick={handlePlay}
                        className="absolute inset-0 flex items-center justify-center"
                      >
                        <div className="w-20 h-20 rounded-full bg-primary-500/90 flex items-center justify-center
                                      shadow-xl shadow-primary-500/30 hover:scale-110 transition-transform">
                          <Play className="w-8 h-8 text-white ml-1" />
                        </div>
                      </motion.button>
                    )}
                    
                    {/* Controls overlay */}
                    <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
                      <button
                        onClick={handlePlay}
                        className="p-3 rounded-full bg-dark-800/80 hover:bg-dark-700 text-white"
                      >
                        {isPlaying ? (
                          <Pause className="w-5 h-5" />
                        ) : (
                          <Play className="w-5 h-5" />
                        )}
                      </button>
                      
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-dark-800/80">
                        <span className="text-xs text-dark-300">
                          {video.duration ? `${video.duration.toFixed(1)}s` : 'Ready'}
                        </span>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full">
                    <Video className="w-16 h-16 text-dark-600 mb-4" />
                    <p className="text-dark-400">Video ready for download</p>
                  </div>
                )}
              </div>
            </div>

            {/* Completion status */}
            <div className="card mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="font-medium text-white">Video Ready!</h3>
                  <p className="text-sm text-dark-400">Your faceless video has been generated</p>
                </div>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-3 bg-dark-900/50 rounded-lg">
                  <p className="text-xs text-dark-400">Duration</p>
                  <p className="font-medium text-white">
                    {video.duration ? `${video.duration.toFixed(1)}s` : 'N/A'}
                  </p>
                </div>
                <div className="p-3 bg-dark-900/50 rounded-lg">
                  <p className="text-xs text-dark-400">Resolution</p>
                  <p className="font-medium text-white">{video.resolution || '1080p'}</p>
                </div>
                <div className="p-3 bg-dark-900/50 rounded-lg">
                  <p className="text-xs text-dark-400">File Size</p>
                  <p className="font-medium text-white">
                    {video.file_size ? `${(video.file_size / 1024 / 1024).toFixed(2)} MB` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setCurrentStep('assets')}
                className="btn-ghost"
              >
                ← Back to Assets
              </button>
              
              <div className="flex items-center gap-4">
                <button
                  onClick={handleGenerate}
                  disabled={isLoading}
                  className="btn-secondary flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  Regenerate
                </button>
                
                <button
                  onClick={handleDownload}
                  disabled={!video.url}
                  className="btn-secondary flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
                
                <button
                  onClick={handleApprove}
                  className="btn-primary flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Complete
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Complete state */}
      <AnimatePresence>
        {useWorkflowStore.getState().currentStep === 'complete' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card text-center py-16"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 
                        flex items-center justify-center shadow-2xl shadow-emerald-500/30"
            >
              <CheckCircle className="w-12 h-12 text-white" />
            </motion.div>
            
            <h2 className="text-2xl font-bold text-white mb-2">Congratulations!</h2>
            <p className="text-dark-400 max-w-md mx-auto mb-8">
              Your faceless video has been successfully created. You can now download it 
              and share it on your social media platforms.
            </p>
            
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={handleDownload}
                className="btn-primary flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Video
              </button>
              
              <button
                onClick={handleNewProject}
                className="btn-secondary flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                New Project
              </button>
            </div>
            
            <div className="mt-8 pt-8 border-t border-dark-700">
              <p className="text-sm text-dark-500 mb-4">Share your creation</p>
              <div className="flex items-center justify-center gap-4">
                <button className="p-3 rounded-xl bg-dark-800 hover:bg-dark-700 text-dark-300 hover:text-white transition-colors">
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default VideoPreview;
