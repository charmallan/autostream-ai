import { motion } from 'framer-motion';

const ProgressBar = ({ progress = 0, showLabel = true, size = 'md', color = 'primary' }) => {
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };
  
  const colors = {
    primary: 'from-primary-500 to-purple-500',
    emerald: 'from-emerald-500 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
    red: 'from-red-500 to-rose-500'
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-dark-400">Progress</span>
          <span className="text-sm font-medium text-white">{Math.round(progress)}%</span>
        </div>
      )}
      <div className={`progress-bar ${sizes[size]} bg-dark-700`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={`h-full bg-gradient-to-r ${colors[color]} rounded-full`}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
