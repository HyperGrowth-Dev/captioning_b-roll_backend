// Video downscaling utility for frontend
export class VideoDownscaler {
  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
  }

  /**
   * Downscale a video file to a target resolution
   * @param {File} videoFile - The original video file
   * @param {number} maxWidth - Maximum width (default: 1920)
   * @param {number} maxHeight - Maximum height (default: 1080)
   * @param {number} quality - Video quality 0-1 (default: 0.8)
   * @returns {Promise<Blob>} - Downscaled video blob
   */
  async downscaleVideo(videoFile, maxWidth = 1920, maxHeight = 1080, quality = 0.8) {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      video.onloadedmetadata = () => {
        // Calculate new dimensions maintaining aspect ratio
        const { width, height } = this.calculateDimensions(
          video.videoWidth, 
          video.videoHeight, 
          maxWidth, 
          maxHeight
        );
        
        canvas.width = width;
        canvas.height = height;
        
        // Set up MediaRecorder
        const stream = canvas.captureStream(30); // 30 FPS
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'video/webm;codecs=vp9',
          videoBitsPerSecond: 4000000 // 4 Mbps
        });
        
        const chunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            chunks.push(event.data);
          }
        };
        
        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: 'video/webm' });
          resolve(blob);
        };
        
        // Start recording
        mediaRecorder.start();
        
        // Play video and draw frames
        video.currentTime = 0;
        video.play();
        
        const drawFrame = () => {
          if (video.ended || video.paused) {
            mediaRecorder.stop();
            return;
          }
          
          ctx.drawImage(video, 0, 0, width, height);
          requestAnimationFrame(drawFrame);
        };
        
        drawFrame();
      };
      
      video.onerror = () => {
        reject(new Error('Failed to load video'));
      };
      
      video.src = URL.createObjectURL(videoFile);
    });
  }
  
  /**
   * Calculate new dimensions maintaining aspect ratio
   */
  calculateDimensions(originalWidth, originalHeight, maxWidth, maxHeight) {
    const aspectRatio = originalWidth / originalHeight;
    
    let newWidth = originalWidth;
    let newHeight = originalHeight;
    
    // Scale down if width exceeds max
    if (newWidth > maxWidth) {
      newWidth = maxWidth;
      newHeight = newWidth / aspectRatio;
    }
    
    // Scale down if height exceeds max
    if (newHeight > maxHeight) {
      newHeight = maxHeight;
      newWidth = newHeight * aspectRatio;
    }
    
    return {
      width: Math.round(newWidth),
      height: Math.round(newHeight)
    };
  }
  
  /**
   * Check if video needs downscaling
   */
  needsDownscaling(videoFile, maxWidth = 1920, maxHeight = 1080) {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      
      video.onloadedmetadata = () => {
        const needsScaling = video.videoWidth > maxWidth || video.videoHeight > maxHeight;
        resolve({
          needsScaling,
          originalWidth: video.videoWidth,
          originalHeight: video.videoHeight,
          originalSize: videoFile.size
        });
      };
      
      video.onerror = () => {
        resolve({ needsScaling: false, error: 'Could not read video metadata' });
      };
      
      video.src = URL.createObjectURL(videoFile);
    });
  }
} 