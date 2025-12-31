import { motion } from 'framer-motion';
import { Check, ChevronRight } from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';

const WorkflowStepper = () => {
  const { currentStep, steps } = useWorkflowStore();
  const currentIndex = steps.findIndex(s => s.id === currentStep);

  return (
    <div className="mb-8">
      {/* Desktop stepper */}
      <div className="hidden lg:flex items-center justify-between">
        {steps.filter(s => s.id !== 'complete').map((step, index) => {
          const isActive = currentStep === step.id;
          const isCompleted = currentIndex > index;
          const isPending = currentIndex < index;
          
          return (
            <div key={step.id} className="flex items-center flex-1">
              {/* Step circle */}
              <motion.div
                initial={false}
                animate={{
                  scale: isActive ? 1.1 : 1,
                  backgroundColor: isActive 
                    ? 'rgb(99, 102, 241)' 
                    : isCompleted 
                      ? 'rgb(16, 185, 129)' 
                      : 'rgb(51, 65, 85)'
                }}
                className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full 
                          border-2 transition-all duration-300
                          ${isActive ? 'border-primary-400 shadow-lg shadow-primary-500/30' : ''}`}
              >
                {isCompleted ? (
                  <Check className="w-5 h-5 text-white" />
                ) : (
                  <span className={`font-semibold text-sm ${isActive ? 'text-white' : 'text-dark-400'}`}>
                    {index + 1}
                  </span>
                )}
                
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute inset-0 rounded-full border-2 border-primary-400"
                  />
                )}
              </motion.div>
              
              {/* Step info */}
              <div className={`ml-3 flex-1 ${isActive ? 'opacity-100' : 'opacity-60'}`}>
                <p className={`font-medium ${isActive ? 'text-white' : 'text-dark-300'}`}>
                  {step.name}
                </p>
                <p className="text-xs text-dark-500">{step.description}</p>
              </div>
              
              {/* Connector line */}
              {index < steps.filter(s => s.id !== 'complete').length - 1 && (
                <div className="flex-1 h-0.5 mx-4 bg-dark-700">
                  <motion.div
                    initial={{ width: '0%' }}
                    animate={{
                      width: isCompleted || isActive ? '100%' : '0%'
                    }}
                    className="h-full bg-emerald-500"
                    transition={{ duration: 0.5 }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Mobile progress bar */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">
            {steps.find(s => s.id === currentStep)?.name}
          </span>
          <span className="text-sm text-dark-400">
            Step {currentIndex + 1} of {steps.length - 1}
          </span>
        </div>
        <div className="progress-bar h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${((currentIndex + 1) / (steps.length - 1)) * 100}%` }}
            className="progress-fill"
          />
        </div>
      </div>

      {/* Step navigation buttons */}
      <div className="hidden lg:flex items-center justify-between mt-6">
        <button
          onClick={() => useWorkflowStore.getState().previousStep()}
          disabled={currentIndex <= 0}
          className="btn-ghost disabled:opacity-30 disabled:cursor-not-allowed"
        >
          ← Previous
        </button>
        
        <div className="flex items-center gap-2 text-sm text-dark-400">
          <span>Progress:</span>
          <span className="font-semibold text-primary-400">
            {Math.round(((currentIndex + 1) / (steps.length - 1)) * 100)}%
          </span>
        </div>
        
        <button
          onClick={() => useWorkflowStore.getState().nextStep()}
          disabled={currentIndex >= steps.length - 2}
          className="btn-ghost disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Skip →
        </button>
      </div>
    </div>
  );
};

export default WorkflowStepper;
