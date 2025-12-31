import { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import WorkflowStepper from './components/WorkflowStepper';
import TrendDiscovery from './components/TrendDiscovery';
import ScriptEditor from './components/ScriptEditor';
import VoiceSelector from './components/VoiceSelector';
import AssetUploader from './components/AssetUploader';
import VideoPreview from './components/VideoPreview';
import ProgressBar from './components/ProgressBar';
import useWorkflowStore from './hooks/useWorkflow';
import * as api from './services/api';

function App() {
  const { 
    currentStep, 
    steps,
    isLoading,
    error,
    resetError,
    reset,
    createProject,
    loadModels
  } = useWorkflowStore();
  
  const [healthStatus, setHealthStatus] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Initialize project and check health on mount
  useEffect(() => {
    const init = async () => {
      try {
        // Create a new project
        await createProject('My Video Project');
        
        // Check backend health
        const response = await api.healthCheck();
        setHealthStatus(response.data);
      } catch (err) {
        console.error('Initialization error:', err);
        setHealthStatus({ status: 'degraded', services: {} });
      }
    };
    
    init();
  }, []);

  // Load available models
  useEffect(() => {
    loadModels();
  }, []);

  const renderStep = () => {
    switch (currentStep) {
      case 'trends':
        return <TrendDiscovery />;
      case 'script':
        return <ScriptEditor />;
      case 'audio':
        return <VoiceSelector />;
      case 'assets':
        return <AssetUploader />;
      case 'video':
        return <VideoPreview />;
      case 'complete':
        return <VideoPreview />; // VideoPreview handles complete state
      default:
        return <TrendDiscovery />;
    }
  };

  const currentStepIndex = steps.findIndex(s => s.id === currentStep);
  const overallProgress = ((currentStepIndex + 1) / steps.length) * 100;

  return (
    <Layout>
      {/* Error toast */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #334155'
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#f1f5f9'
            }
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#f1f5f9'
            }
          }
        }}
      />

      {/* Health status banner */}
      {healthStatus && healthStatus.status !== 'healthy' && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl flex items-center gap-4"
        >
          <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="font-medium text-amber-400">Some services may be unavailable</p>
            <p className="text-sm text-dark-300">
              {Object.entries(healthStatus.services || {})
                .filter(([_, available]) => !available)
                .map(([name]) => name.charAt(0).toUpperCase() + name.slice(1))
                .join(', ') || 'Checking services...'}
            </p>
          </div>
          <button
            onClick={() => setHealthStatus(null)}
            className="p-2 rounded-lg hover:bg-amber-500/20 text-amber-400"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </motion.div>
      )}

      {/* Workflow stepper */}
      <WorkflowStepper />

      {/* Overall progress */}
      <div className="mb-6">
        <ProgressBar progress={overallProgress} color="emerald" />
      </div>

      {/* Error display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="font-medium text-red-400">Error occurred</p>
              <p className="text-sm text-dark-300">{error}</p>
            </div>
          </div>
          <button
            onClick={resetError}
            className="p-2 rounded-lg hover:bg-red-500/20 text-red-400"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </motion.div>
      )}

      {/* Main content area */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {renderStep()}
        </motion.div>
      </AnimatePresence>

      {/* Loading overlay */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm z-50 flex items-center justify-center"
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="card text-center py-12 px-8"
          >
            <div className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-dark-700 border-t-primary-500 animate-spin" />
            <p className="text-lg font-medium text-white mb-2">Processing...</p>
            <p className="text-sm text-dark-400">This may take a few moments</p>
          </motion.div>
        </motion.div>
      )}
    </Layout>
  );
}

export default App;
