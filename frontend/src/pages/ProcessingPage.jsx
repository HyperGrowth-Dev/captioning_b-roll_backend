import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { uploadVideo, processVideo, downloadProcessedVideo } from '../services/videoService';
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
  },
  { 
    name: 'RubikMaps Regular', 
    family: 'RubikMaps-Regular',
    style: 'Modern & Geometric',
    previewStyle: {
      fontFamily: 'RubikMaps',
      fontWeight: 400,
      fontStyle: 'normal'
    }
  },
  { 
    name: 'Nabla Regular', 
    family: 'Nabla-Regular-VariableFont_EDPT,EHLT',
    style: 'Playful & Modern',
    previewStyle: {
      fontFamily: 'Nabla',
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

const fontSizes = [
  { 
    name: 'Small',
    value: 24,
    previewStyle: {
      fontSize: '24px',
      '--text-scale': '1'
    }
  },
  { 
    name: 'Medium',
    value: 32,
    previewStyle: {
      fontSize: '32px',
      '--text-scale': '1'
    }
  },
  { 
    name: 'Large',
    value: 40,
    previewStyle: {
      fontSize: '40px',
      '--text-scale': '0.9'
    }
  },
  { 
    name: 'Extra Large',
    value: 48,
    previewStyle: {
      fontSize: '48px',
      '--text-scale': '0.8'
    }
  }
];

function ProcessingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(location.state?.file || null);
  const [selectedFont, setSelectedFont] = useState(null);
  const [selectedColor, setSelectedColor] = useState(null);
  const [selectedFontSize, setSelectedFontSize] = useState(null);
  const [selectedShadowType, setSelectedShadowType] = useState(null);
  const [selectedShadowColor, setSelectedShadowColor] = useState(null);
  const [selectedShadowBlur, setSelectedShadowBlur] = useState(null);
  const [previewText, setPreviewText] = useState("YOUR CAPTION TEXT");
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoAspectRatio, setVideoAspectRatio] = useState(16/9);
  const [captionPosition, setCaptionPosition] = useState(0.7); // 70% from top by default
  const [isDraggingCaption, setIsDraggingCaption] = useState(false);
  const [isNearCenter, setIsNearCenter] = useState(false); // New state for center snapping
  const [isFontPanelOpen, setIsFontPanelOpen] = useState(true);
  const [isColorPanelOpen, setIsColorPanelOpen] = useState(false);
  const [isFontSizePanelOpen, setIsFontSizePanelOpen] = useState(false);
  const [isShadowPanelOpen, setIsShadowPanelOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedVideoUrl, setProcessedVideoUrl] = useState(null);
  const [processingError, setProcessingError] = useState(null);
  const [showProcessedVideo, setShowProcessedVideo] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [showDragPrompt, setShowDragPrompt] = useState(false);
  const videoRef = useRef(null);
  const videoContainerRef = useRef(null);

  // Set video URL when file is received
  useEffect(() => {
    if (location.state?.file) {
      const url = URL.createObjectURL(location.state.file);
      setVideoUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [location.state]);

  // Add debug logging for state changes
  useEffect(() => {
    console.log('=== CAPTION STATE UPDATE ===');
    console.log('Selected Font:', selectedFont?.name);
    console.log('Selected Color:', selectedColor?.value);
    console.log('Selected Font Size:', selectedFontSize?.value);
  }, [selectedFont, selectedColor, selectedFontSize]);

  // Add drag handling functions
  const handleCaptionDragStart = (e) => {
    e.preventDefault();
    setIsDraggingCaption(true);
  };

  const handleCaptionDrag = (e) => {
    if (!isDraggingCaption || !videoContainerRef.current) return;
    
    const containerRect = videoContainerRef.current.getBoundingClientRect();
    const mouseY = e.clientY - containerRect.top;
    const containerHeight = containerRect.height;
    
    // Calculate position as percentage (0 to 1)
    let newPosition = mouseY / containerHeight;
    
    // Check if we're near the center (within 5% of 0.5)
    const isNear = Math.abs(newPosition - 0.5) < 0.05;
    setIsNearCenter(isNear);
    
    // Snap to center if near
    if (isNear) {
      newPosition = 0.5;
    }
    
    // Add constraints (15% from top, 20% from bottom)
    newPosition = Math.max(0.15, Math.min(0.8, newPosition));
    
    setCaptionPosition(newPosition);
  };

  const handleCaptionDragEnd = () => {
    setIsDraggingCaption(false);
  };

  useEffect(() => {
    if (isDraggingCaption) {
      const handleMouseMove = (e) => handleCaptionDrag(e);
      const handleMouseUp = () => handleCaptionDragEnd();

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDraggingCaption]);

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
      console.log('Original video dimensions:', videoWidth, 'x', videoHeight);
      console.log('Original video orientation:', videoHeight > videoWidth ? 'vertical' : 'horizontal');
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
    setIsFontSizePanelOpen(true);
  };

  const handleFontSizeSelect = (size) => {
    setSelectedFontSize(size);
    setIsFontSizePanelOpen(false);
    setIsShadowPanelOpen(true);
  };

  const handleShadowTypeSelect = (type) => {
    setSelectedShadowType(type);
    if (type === "none") {
      setIsShadowPanelOpen(false);
      setShowDragPrompt(true);
      // Auto-hide the prompt after 5 seconds
      setTimeout(() => setShowDragPrompt(false), 5000);
    }
  };

  const handleShadowColorSelect = (color) => {
    setSelectedShadowColor(color);
    setIsShadowPanelOpen(false);
    setShowDragPrompt(true);
    // Auto-hide the prompt after 5 seconds
    setTimeout(() => setShowDragPrompt(false), 5000);
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

  const toggleFontSizePanel = () => {
    if (!selectedColor) return;
    setIsFontSizePanelOpen(!isFontSizePanelOpen);
    setIsFontPanelOpen(false);
    setIsColorPanelOpen(false);
  };

  const toggleShadowPanel = () => {
    if (!selectedFontSize) return;
    setIsShadowPanelOpen(!isShadowPanelOpen);
    setIsFontPanelOpen(false);
    setIsColorPanelOpen(false);
    setIsFontSizePanelOpen(false);
  };

  const handleProcessVideo = async () => {
    try {
      setIsProcessing(true);
      setProcessingError(null);
      setProcessedVideoUrl(null);
      setShowProcessedVideo(false);

      // Get video dimensions
      const video = document.createElement('video');
      video.src = URL.createObjectURL(selectedFile);
      
      await new Promise((resolve) => {
        video.onloadedmetadata = () => {
          resolve();
        };
      });
      
      const trueWidth = video.videoWidth;
      const trueHeight = video.videoHeight;
      console.log('True video dimensions:', trueWidth, 'x', trueHeight);
      console.log('True video orientation:', trueHeight > trueWidth ? 'vertical' : 'horizontal');
      const { key: inputKey } = await uploadVideo(selectedFile);
      console.log('Video uploaded successfully with key:', inputKey);

      console.log('Starting video processing...');
      const processData = await processVideo(inputKey, {
        font: selectedFont.family,
        color: selectedColor.value,
        font_size: selectedFontSize.value,
        position: captionPosition,
        shadow_type: selectedShadowType || "none",
        shadow_color: selectedShadowColor?.value || "black",
        shadow_blur: selectedShadowBlur || 12,
        shadow_opacity: 0.9,
        true_width: trueWidth,
        true_height: trueHeight
      });
      console.log('Video processing initiated:', processData);

      console.log('Waiting for processed video...');
      setProcessingStatus('Waiting for video to be ready...');
      const downloadUrl = await downloadProcessedVideo(processData.output_key);
      console.log('Successfully got download URL:', downloadUrl);

      navigate('/results', { state: { downloadUrl } });
    } catch (error) {
      console.error('Error processing video:', error);
      setProcessingError(error.message || 'Failed to process video');
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

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Video Preview Section */}
      <div className="w-full lg:w-1/2 h-auto lg:h-screen bg-purple-950/50 p-2 sm:p-4 flex flex-col items-center justify-center">
        {/* Video Preview */}
        <div className="w-full max-w-[280px] sm:max-w-[320px] md:max-w-[360px] mx-auto flex flex-col items-center justify-center space-y-2">
          <div 
            className="relative w-full rounded-xl overflow-hidden cyber-border bg-white"
            style={{
              maxWidth: '360px',
              aspectRatio: videoAspectRatio,
              margin: '0 auto'
            }}
            ref={videoContainerRef}
          >
            {videoUrl ? (
              <>
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
                
                {/* Caption Preview Overlay */}
                {selectedFont && !isProcessing && (
                  <>
                    <div 
                      className={clsx(
                        "absolute inset-x-0 flex items-center justify-center z-10",
                        isDraggingCaption ? "cursor-grabbing" : "cursor-grab"
                      )}
                      style={{ 
                        top: `${captionPosition * 100}%`, 
                        transform: 'translateY(-50%)',
                        transition: isNearCenter ? 'all 0.1s ease-out' : 'none'
                      }}
                      onMouseDown={handleCaptionDragStart}
                    >
                      {/* Main text */}
                      <span
                        className="relative px-4 py-2"
                        style={{
                          ...selectedFont.previewStyle,
                          fontSize: `${selectedFontSize?.value || 32}px`,
                          color: selectedColor?.value || 'white',
                          textAlign: 'center',
                          maxWidth: '90%',
                          textShadow: selectedShadowType === "blur" 
                            ? `0 0 ${selectedShadowBlur || 12}px ${selectedShadowColor?.value || 'black'}`
                            : selectedShadowType === "offset"
                              ? `2px 2px 0 ${selectedShadowColor?.value || 'black'}`
                              : 'none',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          userSelect: 'none',
                          WebkitUserSelect: 'none',
                          display: 'block',
                          lineHeight: '1.2',
                          transform: 'scale(var(--text-scale, 1))',
                          transformOrigin: 'center center'
                        }}
                      >
                        {previewText}
                      </span>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-purple-200/50 text-lg">Video not found</div>
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
          </div>

          {/* Video Toggle Controls */}
          {processedVideoUrl && !isProcessing && (
            <div className="flex flex-col space-y-2 w-full">
              <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-2">
                <button
                  onClick={() => setShowProcessedVideo(false)}
                  className={clsx(
                    'px-3 py-1.5 text-sm rounded-lg transition-all w-full sm:w-auto',
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
                    'px-3 py-1.5 text-sm rounded-lg transition-all w-full sm:w-auto',
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
                className="px-3 py-1.5 text-sm rounded-lg bg-green-600 text-white hover:bg-green-700 transition-all w-full sm:w-auto"
              >
                Download Processed Video
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Options Section */}
      <div className="w-full lg:w-1/2 h-auto lg:h-screen flex items-center justify-center p-2 sm:p-4">
        <LayoutGroup>
          <motion.div 
            layout
            className="w-full max-w-[280px] sm:max-w-[320px] md:max-w-[360px] px-2 sm:px-4 space-y-2"
          >
            {/* Font Selection Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleFontPanel}
                className="w-full p-2 sm:p-3 cyber-border backdrop-blur-xl bg-purple-900/30 hover:bg-purple-800/40 
                         transition-colors duration-300 rounded-xl"
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-base sm:text-lg font-semibold text-purple-100">
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
                    <motion.div layout className="space-y-2 mt-2">
                      {fonts.map((font) => (
                        <motion.button
                          layout
                          key={font.name}
                          onClick={() => handleFontSelect(font)}
                          className="w-full overflow-hidden rounded-xl cyber-border"
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        >
                          <motion.div layout className="bg-white p-2 sm:p-3">
                            <motion.span 
                              layout 
                              className="block text-sm sm:text-base text-black" 
                              style={font.previewStyle}
                            >
                              The quick brown fox jumps over the lazy dog
                            </motion.span>
                            <motion.div layout className="flex justify-between items-center mt-1">
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
                className={`w-full p-2 sm:p-3 cyber-border backdrop-blur-xl transition-colors duration-300 rounded-xl
                          ${selectedFont ? 'bg-purple-900/30 hover:bg-purple-800/40 cursor-pointer' : 'bg-purple-900/10 cursor-not-allowed'}`}
                disabled={!selectedFont}
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-base sm:text-lg font-semibold text-purple-100">
                    Color Selection
                  </motion.h2>
                  {selectedColor && (
                    <motion.div 
                      layout 
                      className={`w-4 h-4 sm:w-5 sm:h-5 rounded-full ${selectedColor.bgClass}`}
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
                    <motion.div layout className="space-y-2 mt-2">
                      {colors.map((color) => (
                        <motion.button
                          layout
                          key={color.name}
                          onClick={() => handleColorSelect(color)}
                          className={`w-full h-12 sm:h-14 rounded-xl ${color.bgClass} transition-all duration-300 hover:scale-[1.02]`}
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        />
                      ))}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Font Size Selection Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleFontSizePanel}
                className={`w-full p-2 sm:p-3 cyber-border backdrop-blur-xl transition-colors duration-300 rounded-xl
                          ${selectedColor ? 'bg-purple-900/30 hover:bg-purple-800/40 cursor-pointer' : 'bg-purple-900/10 cursor-not-allowed'}`}
                disabled={!selectedColor}
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-base sm:text-lg font-semibold text-purple-100">
                    Font Size
                  </motion.h2>
                  {selectedFontSize && (
                    <motion.span layout className="text-xs sm:text-sm text-purple-300">
                      Selected: {selectedFontSize.name}
                    </motion.span>
                  )}
                </motion.div>
              </motion.button>

              <AnimatePresence mode="wait">
                {isFontSizePanelOpen && (
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
                    <motion.div layout className="space-y-2 mt-2">
                      {fontSizes.map((size) => (
                        <motion.button
                          layout
                          key={size.name}
                          onClick={() => handleFontSizeSelect(size)}
                          className="w-full overflow-hidden rounded-xl cyber-border"
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        >
                          <motion.div layout className="bg-white p-2 sm:p-3">
                            <motion.div 
                              layout 
                              className="flex items-center justify-center"
                              style={{
                                height: `${Math.max(size.value + 24, 64)}px`
                              }}
                            >
                              <motion.span 
                                layout 
                                className="block text-black text-center" 
                                style={{
                                  ...selectedFont?.previewStyle,
                                  fontSize: `${size.value}px`,
                                  lineHeight: 1
                                }}
                              >
                                Text
                              </motion.span>
                            </motion.div>
                            <motion.div layout className="flex justify-between items-center mt-1">
                              <motion.span layout className="text-xs sm:text-sm text-gray-600">{size.name}</motion.span>
                              <motion.span layout className="text-xs text-gray-500">{size.value}px</motion.span>
                            </motion.div>
                          </motion.div>
                        </motion.button>
                      ))}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Shadow Type Selection Panel */}
            <motion.button
              onClick={toggleShadowPanel}
              className="w-full p-2 sm:p-3 cyber-border backdrop-blur-xl bg-purple-900/30 hover:bg-purple-800/40 
                         transition-colors duration-300 rounded-xl"
            >
              <motion.div layout className="flex items-center justify-between">
                <motion.h2 layout className="text-base sm:text-lg font-semibold text-purple-100">
                  Shadow Effect
                </motion.h2>
                {selectedShadowType && (
                  <motion.span layout className="text-xs sm:text-sm text-purple-300">
                    Selected: {selectedShadowType}
                  </motion.span>
                )}
              </motion.div>
            </motion.button>

            <AnimatePresence mode="wait">
              {isShadowPanelOpen && (
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
                  className="w-full p-4 space-y-4"
                >
                  {/* Shadow Type Selection */}
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => handleShadowTypeSelect("none")}
                      className={clsx(
                        "p-3 rounded-lg transition-all",
                        selectedShadowType === "none" 
                          ? "bg-purple-600/50 text-purple-100" 
                          : "bg-purple-900/30 text-purple-300 hover:bg-purple-800/40"
                      )}
                    >
                      None
                    </button>
                    <button
                      onClick={() => handleShadowTypeSelect("blur")}
                      className={clsx(
                        "p-3 rounded-lg transition-all",
                        selectedShadowType === "blur" 
                          ? "bg-purple-600/50 text-purple-100" 
                          : "bg-purple-900/30 text-purple-300 hover:bg-purple-800/40"
                      )}
                    >
                      Blur Shadow
                    </button>
                    <button
                      onClick={() => handleShadowTypeSelect("offset")}
                      className={clsx(
                        "p-3 rounded-lg transition-all",
                        selectedShadowType === "offset" 
                          ? "bg-purple-600/50 text-purple-100" 
                          : "bg-purple-900/30 text-purple-300 hover:bg-purple-800/40"
                      )}
                    >
                      Offset Shadow
                    </button>
                  </div>

                  {/* Shadow Color Selection */}
                  {selectedShadowType && selectedShadowType !== "none" && (
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-purple-200">
                        Shadow Color
                      </label>
                      <div className="grid grid-cols-4 gap-2">
                        {[
                          { value: "black", label: "Black" },
                          { value: "white", label: "White" },
                          { value: "#FF4500", label: "Orange" },
                          { value: "#00FF00", label: "Green" },
                          { value: "#FF0000", label: "Red" },
                          { value: "#0000FF", label: "Blue" },
                          { value: "#FFFF00", label: "Yellow" },
                          { value: "#800080", label: "Purple" }
                        ].map((color) => (
                          <button
                            key={color.value}
                            onClick={() => handleShadowColorSelect(color)}
                            className={clsx(
                              "p-2 rounded-lg transition-all",
                              selectedShadowColor?.value === color.value
                                ? "ring-2 ring-purple-400"
                                : "hover:ring-2 hover:ring-purple-400/50"
                            )}
                            style={{ backgroundColor: color.value }}
                            title={color.label}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Process Button */}
            <AnimatePresence mode="wait">
              {selectedFont && selectedColor && selectedFontSize && !isFontSizePanelOpen && (
                <>
                  {/* Drag Instructions Prompt */}
                  <AnimatePresence>
                    {showDragPrompt && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="mb-4 p-3 rounded-lg bg-purple-600/20 backdrop-blur-sm border border-purple-500/30"
                      >
                        <p className="text-purple-200 text-sm text-center">
                          ✨ Drag the caption up or down to position it. It will automatically snap to the center when nearby.
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <motion.button
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    onClick={handleProcessVideo}
                    disabled={isProcessing}
                    className="w-full p-3 sm:p-4 rounded-xl cyber-border backdrop-blur-xl bg-purple-600/30 hover:bg-purple-500/40 
                             transition-all duration-300 text-purple-100 text-base sm:text-lg font-semibold disabled:opacity-50 
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
                </>
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
        <div className="fixed bottom-2 right-2 sm:bottom-4 sm:right-4 bg-red-500 text-white p-2 sm:p-3 rounded-lg shadow-lg max-w-[280px] sm:max-w-[320px] text-sm">
          {typeof processingError === 'string' ? processingError : 
           processingError?.message || processingError?.detail || 'An error occurred'}
        </div>
      )}
    </div>
  );
}

export default ProcessingPage;