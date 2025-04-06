import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { processVideo, downloadProcessedVideo } from '../services/videoService';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

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
  const [selectedFont, setSelectedFont] = useState(null);
  const [selectedColor, setSelectedColor] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoAspectRatio, setVideoAspectRatio] = useState(16/9);
  const [isFontPanelOpen, setIsFontPanelOpen] = useState(true);
  const [isColorPanelOpen, setIsColorPanelOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedVideoUrl, setProcessedVideoUrl] = useState(null);
  const [error, setError] = useState(null);
  const [showProcessedVideo, setShowProcessedVideo] = useState(false);
  const videoRef = useRef(null);

  useEffect(() => {
    if (location.state?.file) {
      const url = URL.createObjectURL(location.state.file);
      setVideoUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [location.state]);

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

  const handleProcessVideo = async () => {
    try {
      console.log('=== STARTING VIDEO PROCESSING ===');
      setIsProcessing(true);
      setError(null);
      console.log('Selected font:', selectedFont);
      console.log('Selected color:', selectedColor);
      console.log('Video file:', location.state.file);
      
      const result = await processVideo(location.state.file, selectedFont, selectedColor);
      console.log('=== PROCESSING RESULT ===', result);
      
      if (result.filename) {
        console.log('=== GETTING PROCESSED VIDEO URL ===');
        const processedUrl = await downloadProcessedVideo(result.filename);
        console.log('=== PROCESSED VIDEO URL CREATED ===', processedUrl);
        setProcessedVideoUrl(processedUrl);
        setShowProcessedVideo(true);
      } else {
        console.log('=== NO FILENAME IN RESULT ===');
      }
    } catch (error) {
      console.error('=== ERROR PROCESSING VIDEO ===', error);
      setError(error.message || 'Failed to process video');
    } finally {
      setIsProcessing(false);
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
    <div className="min-h-screen flex">
      {/* Video Preview Section - Fixed position */}
      <div className="fixed left-0 w-1/2 h-screen bg-purple-950/50 p-8 flex items-center justify-center">
        <div className="w-full max-w-2xl mx-auto flex flex-col items-center justify-center space-y-4">
          {/* Video Preview */}
          <div 
            className="relative w-full rounded-xl overflow-hidden cyber-border bg-white"
            style={{
              maxWidth: '480px',
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
            <div className="flex flex-col space-y-4">
              <div className="flex space-x-4">
                <button
                  onClick={() => setShowProcessedVideo(false)}
                  className={clsx(
                    'px-4 py-2 rounded-lg transition-all',
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
                    'px-4 py-2 rounded-lg transition-all',
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
                className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-all"
              >
                Download Processed Video
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Options Section - Fixed position and centered */}
      <div className="fixed right-0 w-1/2 h-screen flex items-center justify-center">
        <LayoutGroup>
          <motion.div 
            layout
            className="w-full max-w-md px-8 space-y-4"
          >
            {/* Font Selection Panel */}
            <motion.div layout>
              <motion.button
                layout
                onClick={toggleFontPanel}
                className="w-full p-4 cyber-border backdrop-blur-xl bg-purple-900/30 hover:bg-purple-800/40 
                         transition-colors duration-300 rounded-xl"
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-xl font-semibold text-purple-100">
                    Font Selection
                  </motion.h2>
                  {selectedFont && (
                    <motion.span layout className="text-sm text-purple-300">
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
                          <motion.div layout className="bg-white p-4">
                            <motion.span 
                              layout 
                              className="block text-xl text-black" 
                              style={font.previewStyle}
                            >
                              The quick brown fox jumps over the lazy dog
                            </motion.span>
                            <motion.div layout className="flex justify-between items-center mt-2">
                              <motion.span layout className="text-sm text-gray-600">{font.name}</motion.span>
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
                className={`w-full p-4 cyber-border backdrop-blur-xl transition-colors duration-300 rounded-xl
                          ${selectedFont ? 'bg-purple-900/30 hover:bg-purple-800/40 cursor-pointer' : 'bg-purple-900/10 cursor-not-allowed'}`}
                disabled={!selectedFont}
              >
                <motion.div layout className="flex items-center justify-between">
                  <motion.h2 layout className="text-xl font-semibold text-purple-100">
                    Color Selection
                  </motion.h2>
                  {selectedColor && (
                    <motion.div 
                      layout 
                      className={`w-6 h-6 rounded-full ${selectedColor.bgClass}`}
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
                          className={`w-full h-16 rounded-xl ${color.bgClass} transition-all duration-300 hover:scale-[1.02]`}
                          whileHover={{ scale: 1.02 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        />
                      ))}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Process Button */}
            <AnimatePresence mode="wait">
              {selectedFont && selectedColor && !isColorPanelOpen && (
                <motion.button
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  onClick={handleProcessVideo}
                  disabled={isProcessing}
                  className="w-full p-6 rounded-xl cyber-border backdrop-blur-xl bg-purple-600/30 hover:bg-purple-500/40 
                           transition-all duration-300 text-purple-100 text-xl font-semibold disabled:opacity-50 
                           disabled:cursor-not-allowed"
                  whileHover={{ scale: isProcessing ? 1 : 1.02 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  {isProcessing ? 'Processing...' : 'Process Video'}
                </motion.button>
              )}
            </AnimatePresence>
            
            {/* Error Message */}
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  layout
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="p-4 bg-red-500/20 text-red-300 rounded-lg"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </LayoutGroup>
      </div>
    </div>
  );
}

export default ProcessingPage;