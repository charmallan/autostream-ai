import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  TrendingUp, 
  Globe, 
  Clock, 
  ExternalLink,
  Sparkles,
  Loader2,
  RefreshCw
} from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';
import toast from 'react-hot-toast';

const TrendDiscovery = () => {
  const { 
    searchTrends, 
    selectTrend, 
    trends, 
    selectedTrend, 
    isLoading,
    setCurrentStep
  } = useWorkflowStore();
  
  const [query, setQuery] = useState('');
  const [niche, setNiche] = useState('general');
  const [searched, setSearched] = useState(false);

  const niches = [
    { id: 'general', label: 'General', icon: Globe },
    { id: 'tech', label: 'Technology', icon: TrendingUp },
    { id: 'business', label: 'Business', icon: TrendingUp },
    { id: 'entertainment', label: 'Entertainment', icon: TrendingUp },
    { id: 'gaming', label: 'Gaming', icon: TrendingUp },
    { id: 'news', label: 'News', icon: Clock },
  ];

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search topic');
      return;
    }
    
    setSearched(true);
    await searchTrends(query, niche);
  };

  const handleSelectTrend = async (trend) => {
    try {
      await selectTrend(trend);
      toast.success(`Selected: ${trend.title}`);
    } catch (error) {
      toast.error('Failed to select trend');
    }
  };

  const handleRegenerate = async () => {
    if (!query.trim()) {
      toast.error('Please enter a search topic');
      return;
    }
    await searchTrends(query, niche);
    toast.success('Trends refreshed!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 
                    border border-primary-500/30 flex items-center justify-center"
        >
          <Sparkles className="w-8 h-8 text-primary-400" />
        </motion.div>
        <h1 className="text-2xl font-bold text-white mb-2">Discover Trending Topics</h1>
        <p className="text-dark-400">
          Find viral content ideas in your niche using AI-powered trend discovery
        </p>
      </div>

      {/* Search form */}
      <form onSubmit={handleSearch} className="card mb-6">
        <div className="grid lg:grid-cols-4 gap-4">
          <div className="lg:col-span-3">
            <label className="block text-sm font-medium text-dark-300 mb-2">
              What topic do you want to create content about?
            </label>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., AI, Cryptocurrency, Fitness, etc."
                className="input pl-12"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Niche
            </label>
            <select
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              className="input"
            >
              {niches.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="flex justify-end mt-4">
          <button type="submit" className="btn-primary flex items-center gap-2">
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Discover Trends
              </>
            )}
          </button>
        </div>
      </form>

      {/* Results */}
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="card text-center py-12"
          >
            <Loader2 className="w-10 h-10 mx-auto mb-4 text-primary-500 animate-spin" />
            <p className="text-dark-300">Scanning for trending topics...</p>
            <p className="text-sm text-dark-500 mt-2">This may take a few seconds</p>
          </motion.div>
        ) : searched && trends.length > 0 ? (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
                Trending Topics ({trends.length})
              </h2>
              <button
                onClick={handleRegenerate}
                className="btn-ghost flex items-center gap-2 text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>
            
            <div className="grid gap-4">
              {trends.map((trend, index) => (
                <motion.div
                  key={trend.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => handleSelectTrend(trend)}
                  className={`trend-item ${
                    selectedTrend?.id === trend.id ? 'trend-item-selected ring-2 ring-primary-500/30' : ''
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-lg bg-dark-700 flex items-center justify-center 
                                  text-sm font-semibold text-dark-300 flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white mb-1 truncate">
                        {trend.title}
                      </h3>
                      {trend.description && (
                        <p className="text-sm text-dark-400 line-clamp-2">
                          {trend.description}
                        </p>
                      )}
                      <div className="flex items-center gap-4 mt-2">
                        <span className="badge badge-primary text-xs">
                          {trend.source || 'Unknown'}
                        </span>
                        {trend.engagement && (
                          <span className="text-xs text-dark-500">
                            ~{trend.engagement.views || trend.engagement.likes || 'N/A'} views
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {selectedTrend?.id === trend.id && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center"
                        >
                          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        </motion.div>
                      )}
                      {trend.url && (
                        <a
                          href={trend.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="p-2 rounded-lg text-dark-400 hover:text-white hover:bg-dark-700"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {selectedTrend && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 bg-primary-500/10 border border-primary-500/30 rounded-xl flex items-center justify-between"
              >
                <div>
                  <p className="text-sm text-dark-400">Selected:</p>
                  <p className="font-medium text-white">{selectedTrend.title}</p>
                </div>
                <button
                  onClick={() => setCurrentStep('script')}
                  className="btn-primary"
                >
                  Continue to Script →
                </button>
              </motion.div>
            )}
          </motion.div>
        ) : searched && trends.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="card text-center py-12"
          >
            <TrendingUp className="w-12 h-12 mx-auto mb-4 text-dark-600" />
            <p className="text-dark-300 mb-2">No trends found for this topic</p>
            <p className="text-sm text-dark-500">Try a different search term or niche</p>
          </motion.div>
        ) : (
          <motion.div
            key="initial"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="card text-center py-16"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-dark-800 flex items-center justify-center">
              <TrendingUp className="w-10 h-10 text-dark-500" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Ready to Find Trends?</h3>
            <p className="text-dark-400 max-w-md mx-auto">
              Enter a topic above and we'll discover trending content ideas 
              across multiple platforms to help you create viral videos.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default TrendDiscovery;
