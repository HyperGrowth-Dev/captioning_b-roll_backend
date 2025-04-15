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
      fontSize: '24px'
    }
  },
  { 
    name: 'Medium',
    value: 32,
    previewStyle: {
      fontSize: '32px'
    }
  },
  { 
    name: 'Large',
    value: 40,
    previewStyle: {
      fontSize: '40px'
    }
  },
  { 
    name: 'Extra Large',
    value: 48,
    previewStyle: {
      fontSize: '48px'
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
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoAspectRatio, setVideoAspectRatio] = useState(16/9);
  const [isFontPanelOpen, setIsFontPanelOpen] = useState(true);
  const [isColorPanelOpen, setIsColorPanelOpen] = useState(false);
  const [isFontSizePanelOpen, setIsFontSizePanelOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedVideoUrl, setProcessedVideoUrl] = useState(null);
  const [processingError, setProcessingError] = useState(null);
  const [showProcessedVideo, setShowProcessedVideo] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const videoRef = useRef(null);

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
    setIsFontSizePanelOpen(true);
  };

  const handleFontSizeSelect = (size) => {
    setSelectedFontSize(size);
    setIsFontSizePanelOpen(false);
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

  const handleProcessVideo = async () => {
    try {
      setIsProcessing(true);
      setProcessingError(null);
      setProcessedVideoUrl(null);
      setShowProcessedVideo(false);

      // Step 1: Upload video to S3
      console.log('Starting video upload...');
      const { key: inputKey } = await uploadVideo(selectedFile);
      console.log('Video uploaded successfully with key:', inputKey);

      // Step 2: Process video
      console.log('Starting video processing...');
      const processData = await processVideo(inputKey, {
        font: selectedFont.family,
        color: selectedColor.value,
        font_size: selectedFontSize.value
      });
      console.log('Video processing initiated:', processData);

      // Step 3: Poll for processed video
      console.log('Waiting for processed video...');
      setProcessingStatus('Waiting for video to be ready...');
      const downloadUrl = await downloadProcessedVideo(processData.output_key);
      console.log('Successfully got download URL:', downloadUrl);

      // Navigate to results
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
      <div className="w-full lg:w-1/2 h-auto lg:h-screen bg-purple-950/50 p-2 sm:p-4 flex items-center justify-center">
        <div className="w-full max-w-[280px] sm:max-w-[320px] md:max-w-[360px] mx-auto flex flex-col items-center justify-center space-y-2">
          {/* Video Preview */}
          <div 
            className="relative w-full rounded-xl overflow-hidden cyber-border bg-white"
            style={{
              maxWidth: '360px',
              aspectRatio: videoAspectRatio,
              margin: '0 auto'
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
                              className="min-h-[40px] sm:min-h-[48px] flex items-center justify-center"
                            >
                              <motion.span 
                                layout 
                                className="block text-sm sm:text-base text-black text-center" 
                                style={{
                                  ...selectedFont?.previewStyle,
                                  ...size.previewStyle
                                }}
                              >
                                Caption Text
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

            {/* Process Button */}
            <AnimatePresence mode="wait">
              {selectedFont && selectedColor && selectedFontSize && !isFontSizePanelOpen && (
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