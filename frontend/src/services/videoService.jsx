import axios from 'axios';

// Use import.meta.env for Vite environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const uploadVideo = async (file, onProgress) => {
  try {
    console.log('Starting video upload process...');
    
    // Get upload URL from backend
    console.log('Requesting upload URL from backend...');
    const { data: { upload_url, key } } = await axios.post(`${API_URL}/get-upload-url`);
    console.log('Received upload URL:', upload_url);
    
    // Upload directly to S3
    console.log('Uploading to S3...');
    const response = await axios.put(upload_url, file, {
      headers: {
        'Content-Type': 'video/mp4',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Upload progress: ${percentCompleted}%`);
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });
    
    console.log('Upload completed successfully');
    return { key };
  } catch (error) {
    console.error('Error uploading video:', error);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error setting up request:', error.message);
    }
    throw error;
  }
};

export const processVideo = async (inputKey, options, onCaptionProgress, onRenderingProgress) => {
  try {
    console.log('Starting video processing with options:', { inputKey, options });
    
    // Create form data with individual fields
    const formData = new FormData();
    formData.append('input_key', inputKey);
    formData.append('font', options.font);
    formData.append('color', options.color);
    formData.append('font_size', options.font_size);
    formData.append('highlight_type', options.highlight_type);
    formData.append('video_width', options.video_width);
    formData.append('video_height', options.video_height);
    formData.append('broll_enabled', options.broll_enabled);

    console.log('Sending processing request to backend...');
    
    // Start caption progress simulation with cancellation support
    let captionSimulationCancelled = false;
    if (onCaptionProgress) {
      // Simulate caption progress in the background
      const simulateCaptionProgress = async () => {
        for (let i = 0; i <= 90 && !captionSimulationCancelled; i += 1) {
          onCaptionProgress(i);
          await new Promise(resolve => setTimeout(resolve, 300));
        }
      };
      simulateCaptionProgress(); // Don't await this - let it run in background
    }
    
    // Make the API call immediately (don't wait for progress simulation)
    const { data } = await axios.post(`${API_URL}/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Processing request successful:', data);

    // Cancel caption simulation and complete immediately
    captionSimulationCancelled = true;
    if (onCaptionProgress) {
      onCaptionProgress(100);
    }

    // Start rendering stage immediately when polling begins
    if (onRenderingProgress) {
      onRenderingProgress(0); // This will trigger the stage transition
    }

    // Poll for rendering progress
    let isComplete = false;
    let downloadUrl = null;
    let pollCount = 0;
    const maxPolls = 30; // Maximum 60 seconds of polling (30 * 2 seconds)
    
    while (!isComplete && pollCount < maxPolls) {
      try {
        const { data: progressData } = await axios.get(`${API_URL}/check_progress/${data.renderId}`);
        console.log('Progress check:', progressData);
        
        // Use the actual progress from Remotion if available, otherwise calculate based on poll count
        let renderingProgress = 0;
        if (progressData.progress !== undefined) {
          // Convert from decimal (0-1) to percentage (0-100)
          renderingProgress = Math.round(progressData.progress * 100);
        } else {
          // Fallback to poll-based progress if no actual progress is available
          renderingProgress = Math.min((pollCount / maxPolls) * 100, 95);
        }
        
        if (onRenderingProgress) {
          onRenderingProgress(renderingProgress);
        }
        
        if (progressData.status === 'done') {
          isComplete = true;
          downloadUrl = progressData.url;
          if (onRenderingProgress) {
            onRenderingProgress(100);
          }
        } else {
          pollCount++;
          // Wait 2 seconds before next check
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      } catch (error) {
        console.error('Error checking progress:', error);
        throw error;
      }
    }
    
    if (!isComplete) {
      throw new Error('Rendering timeout - video processing took too long');
    }
    
    return {
      renderId: data.renderId,
      download_url: downloadUrl
    };
  } catch (error) {
    console.error('Error processing video:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
      throw new Error(`Video processing failed: ${error.response.data.detail || error.response.data.message || 'Unknown error'}`);
    } else if (error.request) {
      console.error('No response received:', error.request);
      throw new Error('No response received from server. Please check your connection.');
    } else {
      console.error('Error setting up request:', error.message);
      throw new Error(`Failed to process video: ${error.message}`);
    }
  }
};