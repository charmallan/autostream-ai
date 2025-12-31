import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  Image, 
  Palette, 
  Layers, 
  X, 
  Loader2,
  Check,
  ChevronRight,
  Trash2,
  Eye
} from 'lucide-react';
import useWorkflowStore from '../hooks/useWorkflow';
import toast from 'react-hot-toast';

const AssetUploader = () => {
  const { 
    uploadAvatar, 
    uploadLogo, 
    uploadBackground, 
    assets,
    approveVideo,
    isLoading,
    setCurrentStep
  } = useWorkflowStore();
  
  const [uploading, setUploading] = useState({ avatar: false, logo: false, background: false });
  const [preview, setPreview] = useState(null);

  const onDrop = useCallback(async (file, type) => {
    if (!file) return;
    
    setUploading(prev => ({ ...prev, [type]: true }));
    
    try {
      let response;
      switch (type) {
        case 'avatar':
          response = await uploadAvatar(file);
          break;
        case 'logo':
          response = await uploadLogo(file);
          break;
        case 'background':
          response = await uploadBackground(file);
          break;
      }
      
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} uploaded successfully!`);
    } catch (error) {
      toast.error(`Failed to upload ${type}`);
    } finally {
      setUploading(prev => ({ ...prev, [type]: false }));
    }
  }, [uploadAvatar, uploadLogo, uploadBackground]);

  const { getRootProps: getAvatarProps, getInputProps: getAvatarInputProps, isDragActive: isAvatarDragActive } = 
    useDropzone({ onDrop: (files) => onDrop(files[0], 'avatar'), accept: {'image/*': []}, maxFiles: 1 });
  
  const { getRootProps: getLogoProps, getInputProps: getLogoInputProps, isDragActive: isLogoDragActive } = 
    useDropzone({ onDrop: (files) => onDrop(files[0], 'logo'), accept: {'image/*': []}, maxFiles: 1 });
  
  const { getRootProps: getBgProps, getInputProps: getBgInputProps, isDragActive: isBgDragActive } = 
    useDropzone({ onDrop: (files) => onDrop(files[0], 'background'), accept: {'image/*': ['video/*']}, maxFiles: 1 });

  const removeAsset = (type) => {
    // In a real app, this would call an API to remove the asset
    const newAssets = { ...assets };
    delete newAssets[type];
    useWorkflowStore.setState({ assets: newAssets });
    toast.success(`${type} removed`);
  };

  const handleApprove = async () => {
    if (!assets.avatar) {
      toast.error('Please upload an avatar');
      return;
    }
    
    try {
      await approveVideo();
      toast.success('Assets configured!');
    } catch (error) {
      toast.error('Failed to proceed');
    }
  };

  const renderAssetCard = (type, title, icon, dropzoneProps, inputProps, isActive, uploading, asset, color) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-10 h-10 rounded-xl bg-${color}-500/20 flex items-center justify-center`}>
          <icon className={`w-5 h-5 text-${color}-400`} />
        </div>
        <div>
          <h3 className="font-medium text-white">{title}</h3>
          <p className="text-xs text-dark-400">Required for video generation</p>
        </div>
        {asset && (
          <span className="ml-auto badge badge-success flex items-center gap-1">
            <Check className="w-3 h-3" />
            Ready
          </span>
        )}
      </div>
      
      <AnimatePresence mode="wait">
        {asset ? (
          <motion.div
            key="preview"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="relative"
          >
            <div className="aspect-video bg-dark-900 rounded-xl overflow-hidden relative">
              <img
                src={asset.url}
                alt={title}
                className="w-full h-full object-contain"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-dark-900/80 via-transparent to-transparent" />
              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
                <span className="text-xs text-dark-300 truncate max-w-[200px]">
                  {asset.filename}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPreview({ type, asset })}
                    className="p-2 rounded-lg bg-dark-800/80 hover:bg-dark-700 text-dark-300"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => removeAsset(type)}
                    className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="upload"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            {...dropzoneProps}
            className={`upload-zone ${isActive ? 'upload-zone-active' : ''}`}
          >
            <input {...inputProps} />
            {uploading ? (
              <div className="flex flex-col items-center">
                <Loader2 className="w-8 h-8 text-primary-400 animate-spin mb-2" />
                <p className="text-dark-300">Uploading...</p>
              </div>
            ) : (
              <>
                <div className={`w-12 h-12 rounded-xl bg-${color}-500/10 flex items-center justify-center`}>
                  <Upload className={`w-6 h-6 text-${color}-400`} />
                </div>
                <div className="text-center">
                  <p className="text-white font-medium mb-1">
                    {isActive ? 'Drop file here' : `Upload ${title.toLowerCase()}`}
                  </p>
                  <p className="text-sm text-dark-400">
                    PNG, JPG, or supported formats
                  </p>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );

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
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 
                    border border-amber-500/30 flex items-center justify-center"
        >
          <Layers className="w-8 h-8 text-amber-400" />
        </motion.div>
        <h1 className="text-2xl font-bold text-white mb-2">Asset Configuration</h1>
        <p className="text-dark-400">
          Upload your avatar, logo, and background for the video
        </p>
      </div>

      {/* Asset grid */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        {renderAssetCard(
          'avatar',
          'Avatar',
          Image,
          getAvatarProps(),
          getAvatarInputProps(),
          isAvatarDragActive,
          uploading.avatar,
          assets.avatar,
          'primary'
        )}
        
        {renderAssetCard(
          'logo',
          'Logo (Optional)',
          Palette,
          getLogoProps(),
          getLogoInputProps(),
          isLogoDragActive,
          uploading.logo,
          assets.logo,
          'emerald'
        )}
        
        {renderAssetCard(
          'background',
          'Background',
          Layers,
          getBgProps(),
          getBgInputProps(),
          isBgDragActive,
          uploading.background,
          assets.background,
          'purple'
        )}
      </div>

      {/* Tips */}
      <div className="card mb-8">
        <h3 className="font-medium text-white mb-3">Recommended Specifications</h3>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div className="p-3 bg-dark-900/50 rounded-lg">
            <p className="text-dark-400 mb-1">Avatar</p>
            <p className="text-dark-200">1080x1920 PNG with transparent background</p>
          </div>
          <div className="p-3 bg-dark-900/50 rounded-lg">
            <p className="text-dark-400 mb-1">Logo</p>
            <p className="text-dark-200">200x200 PNG with transparent background</p>
          </div>
          <div className="p-3 bg-dark-900/50 rounded-lg">
            <p className="text-dark-400 mb-1">Background</p>
            <p className="text-dark-200">1080x1920 image or short video loop</p>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentStep('audio')}
          className="btn-ghost"
        >
          ← Back to Voice
        </button>
        
        <button
          onClick={handleApprove}
          disabled={!assets.avatar || isLoading}
          className="btn-primary flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Check className="w-4 h-4" />
              Configure Video
            </>
          )}
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Preview modal */}
      <AnimatePresence>
        {preview && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-dark-950/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setPreview(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative max-w-2xl w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setPreview(null)}
                className="absolute -top-12 right-0 p-2 text-dark-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
              <img
                src={preview.asset.url}
                alt={preview.type}
                className="w-full rounded-xl shadow-2xl"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default AssetUploader;
