import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Settings, 
  FolderOpen, 
  HelpCircle,
  Menu,
  X,
  ChevronRight,
  Zap,
  History,
  CreditCard
} from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { currentStep, steps, reset, projectId } = useWorkflowStore();

  const navItems = [
    { id: 'trends', icon: Sparkles, label: 'Discovery' },
    { id: 'script', icon: Zap, label: 'Script' },
    { id: 'audio', icon: CreditCard, label: 'Voice' },
    { id: 'assets', icon: FolderOpen, label: 'Assets' },
    { id: 'video', icon: History, label: 'Render' },
  ];

  const currentStepIndex = steps.findIndex(s => s.id === currentStep);

  return (
    <div className="min-h-screen flex">
      {/* Sidebar - Desktop */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 280 : 80 }}
        className="hidden lg:flex flex-col bg-dark-900/50 backdrop-blur-xl border-r border-dark-700/50 
                   fixed left-0 top-0 h-full z-40"
      >
        {/* Logo */}
        <div className="p-6 border-b border-dark-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 
                          flex items-center justify-center shadow-lg shadow-primary-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <AnimatePresence>
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="overflow-hidden"
                >
                  <h1 className="font-bold text-lg text-white">AutoStream AI</h1>
                  <p className="text-xs text-dark-400">Video Automation</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item, index) => {
            const isActive = currentStep === item.id;
            const isPast = currentStepIndex > index;
            
            return (
              <motion.button
                key={item.id}
                onClick={() => useWorkflowStore.getState().setCurrentStep(item.id)}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300
                          ${isActive 
                            ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                            : isPast 
                              ? 'text-emerald-400 hover:bg-emerald-500/10' 
                              : 'text-dark-300 hover:bg-dark-800 hover:text-white'
                          }`}
              >
                <item.icon className={`w-5 h-5 flex-shrink-0 ${isPast ? 'text-emerald-500' : ''}`} />
                <AnimatePresence>
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      className="font-medium whitespace-nowrap overflow-hidden"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
                {isPast && sidebarOpen && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="ml-auto w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center"
                  >
                    <ChevronRight className="w-3 h-3 text-white" />
                  </motion.div>
                )}
              </motion.button>
            );
          })}
        </nav>

        {/* Bottom actions */}
        <div className="p-4 border-t border-dark-700/50 space-y-2">
          <motion.button
            whileHover={{ x: 4 }}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl 
                     text-dark-400 hover:bg-dark-800 hover:text-white transition-all duration-300"
          >
            <Settings className="w-5 h-5" />
            <AnimatePresence>
              {sidebarOpen && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="font-medium whitespace-nowrap overflow-hidden"
                >
                  Settings
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>
          
          <motion.button
            whileHover={{ x: 4 }}
            onClick={reset}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl 
                     text-dark-400 hover:bg-red-500/10 hover:text-red-400 transition-all duration-300"
          >
            <X className="w-5 h-5" />
            <AnimatePresence>
              {sidebarOpen && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="font-medium whitespace-nowrap overflow-hidden"
                >
                  Reset Flow
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>
        </div>

        {/* Toggle button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-dark-800 border border-dark-700 
                   rounded-full flex items-center justify-center text-dark-400 hover:text-white
                   shadow-lg hidden lg:flex"
        >
          <ChevronRight className={`w-4 h-4 transition-transform ${sidebarOpen ? 'rotate-180' : ''}`} />
        </button>
      </motion.aside>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="lg:hidden fixed inset-0 bg-dark-950/80 backdrop-blur-sm z-50"
            onClick={() => setMobileMenuOpen(false)}
          >
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'spring', damping: 25 }}
              onClick={(e) => e.stopPropagation()}
              className="w-72 h-full bg-dark-900 border-r border-dark-700 p-6"
            >
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 
                              flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="font-bold text-lg text-white">AutoStream AI</h1>
                  <p className="text-xs text-dark-400">Video Automation</p>
                </div>
              </div>
              
              <nav className="space-y-2">
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      useWorkflowStore.getState().setCurrentStep(item.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300
                              ${currentStep === item.id 
                                ? 'bg-primary-500/20 text-primary-400' 
                                : 'text-dark-300 hover:bg-dark-800 hover:text-white'
                              }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </button>
                ))}
              </nav>
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content */}
      <main 
        className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'lg:ml-[280px]' : 'lg:ml-[80px]'}`}
      >
        {/* Header */}
        <header className="sticky top-0 z-30 bg-dark-950/80 backdrop-blur-xl border-b border-dark-700/50">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="lg:hidden p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div>
                <h2 className="text-lg font-semibold text-white">
                  {steps.find(s => s.id === currentStep)?.name || 'AutoStream AI'}
                </h2>
                <p className="text-sm text-dark-400">
                  {steps.find(s => s.id === currentStep)?.description || 'Create viral videos effortlessly'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {projectId && (
                <span className="text-xs text-dark-500 font-mono">
                  ID: {projectId}
                </span>
              )}
              <button className="p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800">
                <HelpCircle className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
