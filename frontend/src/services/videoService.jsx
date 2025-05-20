import axios from 'axios';

// Use import.meta.env for Vite environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const uploadVideo = async (file) => {
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

export const processVideo = async (inputKey, options) => {
  try {
    console.log('Starting video processing with options:', { inputKey, options });
    
    // Create form data with individual fields
    const formData = new FormData();
    formData.append('input_key', inputKey);
    formData.append('font', options.font);
    formData.append('color', options.color);
    formData.append('font_size', options.font_size);
    formData.append('highlight_type', options.highlight_type);

    console.log('Sending processing request to backend...');
    const { data } = await axios.post(`${API_URL}/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Processing request successful:', data);

    // Poll for progress
    let isComplete = false;
    let downloadUrl = null;
    
    while (!isComplete) {
      try {
        const { data: progressData } = await axios.get(`${API_URL}/progress/${data.renderId}`);
        console.log('Progress check:', progressData);
        
        if (progressData.status === 'done') {
          isComplete = true;
          downloadUrl = progressData.url;
        } else {
          // Wait 2 seconds before next check
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      } catch (error) {
        console.error('Error checking progress:', error);
        throw error;
      }
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