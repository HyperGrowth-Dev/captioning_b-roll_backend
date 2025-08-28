import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { uploadVideo, processVideo } from '../services/videoService';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

const fonts = [
  { 
    name: 'Montserrat SemiBold Italic', 
    family: 'Montserrat-SemiBoldItalic',
    style: 'Modern & Professional',
    previewStyle: {
      fontFamily: 'Montserrat',
      fontWeight: 600,
      fontStyle: 'italic'
    }
  },
  { 
    name: 'Barlow Black Italic', 
    family: 'Barlow-BlackItalic',
    style: 'Bold & Dynamic',
    previewStyle: {
      fontFamily: 'Barlow',
      fontWeight: 900,
      fontStyle: 'italic'
    }
  },
  { 
    name: 'Barlow Bold', 
    family: 'Barlow-Bold',
    style: 'Strong & Clear',
    previewStyle: {
      fontFamily: 'Barlow',
      fontWeight: 700,
      fontStyle: 'normal'
    }
  },
  { 
    name: 'Montserrat Bold', 
    family: 'Montserrat-Bold',
    style: 'Impactful & Modern',
    previewStyle: {
      fontFamily: 'Montserrat',
      fontWeight: 700,
      fontStyle: 'normal'
    }
  },
  { 
    name: 'Oswald SemiBold', 
    family: 'Oswald-SemiBold',
    style: 'Distinctive & Bold',
    previewStyle: {
      fontFamily: 'Oswald',
      fontWeight: 600,
      fontStyle: 'normal'
    }
  },
  { 
    name: 'Oswald Regular', 
    family: 'Oswald-Regular',
    style: 'Clean & Readable',
    previewStyle: {
      fontFamily: 'Oswald',
      fontWeight: 400,
      fontStyle: 'normal'
    }
  }
];

const colors = [
  { 
    name: 'White',
    value: '#FFFFFF',
    textClass: 'text-white',
    bgClass: 'bg-white'
  },
  { 
    name: 'Yellow',
    value: '#FBBF24',
    textClass: 'text-yellow-400',
    bgClass: 'bg-yellow-400'
  },
  { 
    name: 'Green',
    value: '#34D399',
    textClass: 'text-emerald-400',
    bgClass: 'bg-emerald-400'
  },
  { 
    name: 'Blue',
    value: '#60A5FA',
    textClass: 'text-blue-400',
    bgClass: 'bg-blue-400'
  },
  { 
    name: 'Pink',
    value: '#F472B6',
    textClass: 'text-pink-400',
    bgClass: 'bg-pink-400'
  }
];

function ProcessingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(location.state?.file || null);
  const [selectedFont, setSelectedFont] = useState(null);
  const [selectedColor, setSelectedColor] = useState(null);
  const [highlightType, setHighlightType] = useState('background');
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoAspectRatio, setVideoAspectRatio] = useState(16/9);
  const [isFontPanelOpen, setIsFontPanelOpen] = useState(true);
  const [isColorPanelOpen, setIsColorPanelOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedVideoUrl, setProcessedVideoUrl] = useState(null);
  const [processingError, setProcessingError] = useState(null);
  const [showProcessedVideo, setShowProcessedVideo] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const videoRef = useRef(null);
  const [fontSize, setFontSize] = useState(32);
  const [isHighlightPanelOpen, setIsHighlightPanelOpen] = useState(false);
  const [brollEnabled, setBrollEnabled] = useState(null);
  const [isBrollPanelOpen, setIsBrollPanelOpen] = useState(false);
  const [currentStage, setCurrentStage] = useState(null);
  const [stageProgress, setStageProgress] = useState(0);

  // Set video URL when file is received
  useEffect(() => {
    if (location.state?.file) {
      const url = URL.createObjectURL(location.state.file);
      setVideoUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [location.state]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setProcessingError(null);
    }
  };

  const handleVideoLoad = () => {
    if (videoRef.current) {
      const { videoWidth, videoHeight } = videoRef.current;
      setVideoAspectRatio(videoWidth / videoHeight);
    }
  };

  const handleFontSelect = (font) => {
    setSelectedFont(font);
    setIsFontPanelOpen(false);
    setIsColorPanelOpen(true);
  };

  const handleColorSelect = (color) => {
    setSelectedColor(color);
    setIsColorPanelOpen(false);
    setIsHighlightPanelOpen(true);
  };

  const toggleFontPanel = () => {
    setIsFontPanelOpen(!isFontPanelOpen);
    if (!isFontPanelOpen) {
      setIsColorPanelOpen(false);
    }
  };

  const toggleColorPanel = () => {
    if (!selectedFont) return;
    setIsColorPanelOpen(!isColorPanelOpen);
    setIsFontPanelOpen(false);
  };

  const toggleHighlightPanel = () => {
    if (!selectedColor) return;
    setIsHighlightPanelOpen(!isHighlightPanelOpen);
  };

  const toggleBrollPanel = () => {
    if (!highlightType) return;
    setIsBrollPanelOpen(!isBrollPanelOpen);
  };

  const handleHighlightTypeSelect = (type) => {
    setHighlightType(type);
    setIsHighlightPanelOpen(false);
    setIsBrollPanelOpen(true);
  };

  const handleBrollSelect = (enabled) => {
    setBrollEnabled(enabled);
    setIsBrollPanelOpen(false);
  };

  const handleProcessVideo = async () => {
    try {
      setIsProcessing(true);
      setProcessingError(null);
      setProcessedVideoUrl(null);
      setShowProcessedVideo(false);
      setCurrentStage('upload');
      setStageProgress(0);

      // Get video dimensions from videoRef
      const videoWidth = videoRef.current?.videoWidth || 607;
      const videoHeight = videoRef.current?.videoHeight || 1080;

      // Step 1: Upload video to S3
      console.log('Starting video upload...');
      setProcessingStatus('Uploading video to cloud storage...');
      
      // Upload with real progress tracking
      const { key: inputKey } = await uploadVideo(selectedFile, (progress) => {
        setStageProgress(progress);
      });
      console.log('Video uploaded successfully with key:', inputKey);

      // Step 2: Process video (Caption generation)
      console.log('Starting video processing...');
      setCurrentStage('caption');
      setStageProgress(0);
      setProcessingStatus('Generating captions and processing video...');

      const processData = await processVideo(
        inputKey, 
        {
          font: selectedFont.family,
          color: selectedColor.value,
          font_size: fontSize,
          highlight_type: highlightType,
          video_width: videoWidth,
          video_height: videoHeight,
          broll_enabled: brollEnabled
        },
        (captionProgress) => {
          setStageProgress(captionProgress);
        },
        (renderingProgress) => {
          // Transition to rendering stage immediately when rendering starts
          setCurrentStage('rendering');
          setProcessingStatus('Rendering final video with captions...');
          setStageProgress(renderingProgress);
        }
      );
      console.log('Video processing initiated:', processData);

      // Navigate to results with the Remotion URL
      navigate('/results', { state: { downloadUrl: processData.download_url } });
    } catch (error) {
      console.error('Error processing video:', error);
      setProcessingError(error.message || 'Failed to process video');
      setCurrentStage('error');
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  };

  const handleDownload = async () => {
    if (processedVideoUrl) {
      const link = document.createElement('a');
      link.href = processedVideoUrl;
      link.setAttribute('download', 'processed_video.mp4');
      document.body.appendChild(link);
      link.click();
      link.remove();
    }
  };

  // Add useEffect to log state changes
  useEffect(() => {
    console.log('=== STATE UPDATE ===');
    console.log('Processed video URL:', processedVideoUrl);
    console.log('Show processed video:', showProcessedVideo);
    console.log('Is processing:', isProcessing);
  }, [processedVideoUrl, showProcessedVideo, isProcessing]);

  const getStageInfo = (stage) => {
    switch (stage) {
      case 'upload':
        return { name: 'Upload', color: 'bg-blue-500' };
      case 'caption':
        return { name: 'Caption Processing', color: 'bg-green-500' };
      case 'rendering':
        return { name: 'Rendering', color: 'bg-orange-500' };
      case 'complete':
        return { name: 'Complete', color: 'bg-green-600' };
      case 'error':
        return { name: 'Error', color: 'bg-red-500' };
      default:
        return { name: 'Processing', color: 'bg-gray-500' };
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-purple-950">
      {/* Video Preview Section - Responsive */}
      <div className="w-full lg:w-1/2 min-h-[50vh] lg:min-h-screen flex items-center justify-center p-4 lg:p-8">
        <div className="w-full max-w-lg mx-auto flex flex-col items-center justify-center space-y-4">
          {/* Video Preview */}
          <div 
            className="relative w-full rounded-xl overflow-hidden cyber-border bg-white"
            style={{
              aspectRatio: videoAspectRatio,
              maxWidth: '100%'
            }}
          >
            {videoUrl ? (
              <video
                ref={videoRef}
                src={showProcessedVideo ? processedVideoUrl : videoUrl}
                className="absolute inset-0 w-full h-full object-contain"
                autoPlay
                loop
                muted
                playsInline
                onLoadedMetadata={handleVideoLoad}
                onError={(e) => console.error('=== VIDEO ERROR ===', e)}
                onLoadStart={() => console.log('=== VIDEO LOAD STARTED ===')}
                onLoadedData={() => console.log('=== VIDEO DATA LOADED ===')}
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-purple-200/50 text-lg">No video selected</div>
              </div>
            )}
            
            {/* Blur and Sparkles overlay - Show until video is processed */}
            {(!processedVideoUrl || isProcessing) && (
              <>
                {/* Blur overlay */}
                <div className="preview-overlay" />
                
                {/* Sparkles layer */}
                <div className="absolute inset-0">
                  {[...Array(10)].map((_, i) => (
                    <div
                      key={i}
                      className="sparkle"
                      style={{
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        animationDelay: `${Math.random() * 2}s`
                      }}
                    />
                  ))}
                </div>
              </>
            )}
            
            {/* Processing overlay - Only show when processing */}
            {isProcessing && (
              <div className="absolute inset-0 processing-blur">
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
              </div>
            )}

            {/* Loading Bar Overlay */}
            {isProcessing && currentStage && (
              <div className="absolute inset-0 bg-black/80 flex items-center justify-center p-6">
                <div className="bg-purple-900/90 backdrop-blur-xl rounded-xl p-6 w-full max-w-md space-y-4">
                  {/* Stage Info */}
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <div className={`w-3 h-3 rounded-full ${getStageInfo(currentStage).color}`}></div>
                      <h3 className="text-purple-100 font-semibold text-lg">
                        {getStageInfo(currentStage).name}
                      </h3>
                    </div>
                    <p className="text-purple-300 text-sm">{processingStatus}</p>
                  </div>

                  {/* Stage Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-purple-300">
                      <span>Current Stage</span>
                      <span>{stageProgress}%</span>
                    </div>
                    <div className="w-full bg-purple-800 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${getStageInfo(currentStage).color}`}
                        style={{ width: `${stageProgress}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Stage Indicators */}
                  <div className="flex justify-between text-xs">
                    <div className={`flex items-center space-x-1 ${currentStage === 'upload' || currentStage === 'caption' || currentStage === 'rendering' || currentStage === 'complete' ? 'text-blue-400' : 'text-purple-600'}`}>
                      <div className={`w-2 h-2 rounded-full ${currentStage === 'upload' || currentStage === 'caption' || currentStage === 'rendering' || currentStage === 'complete' ? 'bg-blue-400' : 'bg-purple-600'}`}></div>
                      <span>Upload</span>
                    </div>
                    <div className={`flex items-center space-x-1 ${currentStage === 'caption' || currentStage === 'rendering' || currentStage === 'complete' ? 'text-green-400' : 'text-purple-600'}`}>
                      <div className={`w-2 h-2 rounded-full ${currentStage === 'caption' || currentStage === 'rendering' || currentStage === 'complete' ? 'bg-green-400' : 'bg-purple-600'}`}></div>
                      <span>Caption</span>
                    </div>
                    <div className={`flex items-center space-x-1 ${currentStage === 'rendering' || currentStage === 'complete' ? 'text-orange-400' : 'text-purple-600'}`}>
                      <div className={`w-2 h-2 rounded-full ${currentStage === 'rendering' || currentStage === 'complete' ? 'bg-orange-400' : 'bg-purple-600'}`}></div>
                      <span>Render</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Video Toggle Controls */}
          {processedVideoUrl && !isProcessing && (
            <div className="flex flex-col space-y-4 w-full max-w-lg">
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                <button
                  onClick={() => setShowProcessedVideo(false)}
                  className={clsx(
                    'px-4 py-2 rounded-lg transition-all text-sm sm:text-base',
                    !showProcessedVideo
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  )}
                >
                  Original Video
                </button>
                <button
                  onClick={() => setShowProcessedVideo(true)}
                  className={clsx(
                    'px-4 py-2 rounded-lg transition-all text-sm sm:text-base',
                    showProcessedVideo
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  )}
                >
                  Processed Video
                </button>
              </div>
              <button
                onClick={handleDownload}
                className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-all text-sm sm:text-base"
              >
                Download Processed Video
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Options Section - Responsive */}
      <div className="w-full lg:w-1/2 min-h-[50vh] lg:min-h-screen flex items-center justify-center p-4 lg:p-8">
        <LayoutGroup>
          <motion.div 
            layout
            className="w-full max-w-md mx-auto space-y-4"
          >
            {/* Font Selection Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleFontPanel}
                className="w-full p-3 sm:p-4 cyber-border backdrop-blur-xl bg-purple-900/30 hover:bg-purple-800/40 
                         transition-colors duration-300 rounded-xl"
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-lg sm:text-xl font-semibold text-purple-100">
                    Font Selection
                  </motion.h2>
                  {selectedFont && (
                    <motion.span layout className="text-xs sm:text-sm text-purple-300">
                      Selected: {selectedFont.name}
                    </motion.span>
                  )}
                </motion.div>
              </motion.button>

              <AnimatePresence mode="wait">
                {isFontPanelOpen && (
                  <motion.div
                    layout
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ 
                      opacity: 1,
                      height: 'auto',
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    exit={{ 
                      opacity: 0,
                      height: 0,
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    className="overflow-hidden"
                  >
                    <motion.div layout className="space-y-3 mt-4">
                      {fonts.map((font) => (
                        <motion.button
                          layout
                          key={font.name}
                          onClick={() => handleFontSelect(font)}
                          className="w-full overflow-hidden rounded-xl cyber-border"
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        >
                          <motion.div layout className="bg-white p-3 sm:p-4">
                            <motion.span 
                              layout 
                              className="block text-lg sm:text-xl text-black" 
                              style={font.previewStyle}
                            >
                              The quick brown fox jumps over the lazy dog
                            </motion.span>
                            <motion.div layout className="flex justify-between items-center mt-2">
                              <motion.span layout className="text-xs sm:text-sm text-gray-600">{font.name}</motion.span>
                              <motion.span layout className="text-xs text-gray-500">{font.style}</motion.span>
                            </motion.div>
                          </motion.div>
                        </motion.button>
                      ))}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Color Selection Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleColorPanel}
                className={`w-full p-3 sm:p-4 cyber-border backdrop-blur-xl transition-colors duration-300 rounded-xl
                          ${selectedFont ? 'bg-purple-900/30 hover:bg-purple-800/40 cursor-pointer' : 'bg-purple-900/10 cursor-not-allowed'}`}
                disabled={!selectedFont}
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-lg sm:text-xl font-semibold text-purple-100">
                    Color Selection
                  </motion.h2>
                  {selectedColor && (
                    <motion.div 
                      layout 
                      className="w-5 h-5 sm:w-6 sm:h-6 rounded-full"
                      style={{ backgroundColor: selectedColor.value }}
                    />
                  )}
                </motion.div>
              </motion.button>

              <AnimatePresence mode="wait">
                {isColorPanelOpen && (
                  <motion.div
                    layout
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ 
                      opacity: 1,
                      height: 'auto',
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    exit={{ 
                      opacity: 0,
                      height: 0,
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    className="overflow-hidden"
                  >
                    <motion.div layout className="space-y-3 mt-4">
                      {colors.map((color) => (
                        <motion.button
                          layout
                          key={color.name}
                          onClick={() => handleColorSelect(color)}
                          className={`w-full h-12 sm:h-16 rounded-xl transition-all duration-300 hover:scale-[1.02]`}
                          style={{ backgroundColor: color.value }}
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        />
                      ))}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Highlight Type Selection Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleHighlightPanel}
                className={`w-full p-3 sm:p-4 cyber-border backdrop-blur-xl transition-colors duration-300 rounded-xl
                          ${selectedColor ? 'bg-purple-900/30 hover:bg-purple-800/40 cursor-pointer' : 'bg-purple-900/10 cursor-not-allowed'}`}
                disabled={!selectedColor}
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-lg sm:text-xl font-semibold text-purple-100">
                    Highlight Type
                  </motion.h2>
                  {highlightType && (
                    <motion.span layout className="text-xs sm:text-sm text-purple-300">
                      Selected: {highlightType === 'background' ? 'Background' : 'Fill'}
                    </motion.span>
                  )}
                </motion.div>
              </motion.button>

              <AnimatePresence mode="wait">
                {isHighlightPanelOpen && (
                  <motion.div
                    layout
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ 
                      opacity: 1,
                      height: 'auto',
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    exit={{ 
                      opacity: 0,
                      height: 0,
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    className="overflow-hidden"
                  >
                    <motion.div layout className="space-y-3 mt-4">
                      <div className="grid grid-cols-2 gap-3 sm:gap-4">
                        <button
                          onClick={() => handleHighlightTypeSelect('background')}
                          className={`p-3 sm:p-4 rounded-xl cyber-border transition-all duration-300 ${
                            highlightType === 'background' 
                              ? 'bg-purple-600/50 border-purple-400' 
                              : 'bg-purple-900/30 hover:bg-purple-800/40'
                          }`}
                        >
                          <div className="text-purple-100 font-medium mb-2 text-sm sm:text-base">Background</div>
                          <div className="text-xs sm:text-sm text-purple-300">
                            <div className="space-x-1">
                              <span>Sample</span>
                              <span className="bg-yellow-500 px-1 rounded">Text</span>
                            </div>
                          </div>
                        </button>

                        <button
                          onClick={() => handleHighlightTypeSelect('fill')}
                          className={`p-3 sm:p-4 rounded-xl cyber-border transition-all duration-300 ${
                            highlightType === 'fill' 
                              ? 'bg-purple-600/50 border-purple-400' 
                              : 'bg-purple-900/30 hover:bg-purple-800/40'
                          }`}
                        >
                          <div className="text-purple-100 font-medium mb-2 text-sm sm:text-base">Fill</div>
                          <div className="text-xs sm:text-sm text-purple-300">
                            <div className="space-x-1">
                              <span className="text-yellow-500">Sample</span>
                              <span className="text-white">Text</span>
                            </div>
                          </div>
                        </button>
                      </div>
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* B-roll Enable/Disable Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleBrollPanel}
                className={`w-full p-3 sm:p-4 cyber-border backdrop-blur-xl transition-colors duration-300 rounded-xl
                          ${highlightType ? 'bg-purple-900/30 hover:bg-purple-800/40 cursor-pointer' : 'bg-purple-900/10 cursor-not-allowed'}`}
                disabled={!highlightType}
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-lg sm:text-xl font-semibold text-purple-100">
                    B-roll
                  </motion.h2>
                  {brollEnabled !== null && (
                    <motion.span layout className="text-xs sm:text-sm text-purple-300">
                      {brollEnabled ? 'Enabled' : 'Disabled'}
                    </motion.span>
                  )}
                </motion.div>
              </motion.button>

              <AnimatePresence mode="wait">
                {isBrollPanelOpen && (
                  <motion.div
                    layout
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ 
                      opacity: 1,
                      height: 'auto',
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    exit={{ 
                      opacity: 0,
                      height: 0,
                      transition: {
                        type: "spring",
                        stiffness: 70,
                        damping: 15
                      }
                    }}
                    className="overflow-hidden"
                  >
                    <motion.div layout className="space-y-3 mt-4">
                      <div className="grid grid-cols-2 gap-3 sm:gap-4">
                        <button
                          onClick={() => handleBrollSelect(true)}
                          className={`p-3 sm:p-4 rounded-xl cyber-border transition-all duration-300 ${
                            brollEnabled 
                              ? 'bg-purple-600/50 border-purple-400' 
                              : 'bg-purple-900/30 hover:bg-purple-800/40'
                          }`}
                        >
                          <div className="text-purple-100 font-medium mb-2 text-sm sm:text-base">Enabled</div>
                          <div className="text-xs sm:text-sm text-purple-300">
                            Add dynamic b-roll footage to enhance your video with additional visual content
                          </div>
                        </button>

                        <button
                          onClick={() => handleBrollSelect(false)}
                          className={`p-3 sm:p-4 rounded-xl cyber-border transition-all duration-300 ${
                            !brollEnabled 
                              ? 'bg-purple-600/50 border-purple-400' 
                              : 'bg-purple-900/30 hover:bg-purple-800/40'
                          }`}
                        >
                          <div className="text-purple-100 font-medium mb-2 text-sm sm:text-base">Disabled</div>
                          <div className="text-xs sm:text-sm text-purple-300">
                            Keep your original video footage without additional b-roll content
                          </div>
                        </button>
                      </div>
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Process Button */}
            <AnimatePresence mode="wait">
              {selectedFont && selectedColor && highlightType && brollEnabled !== null && !isBrollPanelOpen && (
                <motion.button
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  onClick={handleProcessVideo}
                  disabled={isProcessing}
                  className="w-full p-4 sm:p-6 rounded-xl cyber-border backdrop-blur-xl bg-purple-600/30 hover:bg-purple-500/40 
                           transition-all duration-300 text-purple-100 text-lg sm:text-xl font-semibold disabled:opacity-50 
                           disabled:cursor-not-allowed"
                  whileHover={{ scale: isProcessing ? 1 : 1.02 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  {isProcessing ? (
                    <>
                      <FontAwesomeIcon icon={faSpinner} className="animate-spin mr-2" />
                      Processing...
                    </>
                  ) : (
                    'Process Video'
                  )}
                </motion.button>
              )}
            </AnimatePresence>
            
            {/* Error Message */}
            <AnimatePresence mode="wait">
              {processingError && (
                <motion.div
                  layout
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="p-4 bg-red-500/20 text-red-300 rounded-lg"
                >
                  {typeof processingError === 'string' ? processingError : 
                   processingError?.message || processingError?.detail || 'An error occurred'}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </LayoutGroup>
      </div>

      {/* Error Display */}
      {processingError && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg">
          {typeof processingError === 'string' ? processingError : 
           processingError?.message || processingError?.detail || 'An error occurred'}
        </div>
      )}
    </div>
  );
}

export default ProcessingPage;