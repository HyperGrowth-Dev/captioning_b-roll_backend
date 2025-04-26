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
    
    const formData = new FormData();
    formData.append('input_key', inputKey);
    formData.append('font', options.font);
    formData.append('color', options.color);
    formData.append('font_size', options.font_size);
    formData.append('highlight_type', options.highlight_type);
    
    // Add caption clips if they exist
    if (options.caption_clips) {
      formData.append('caption_clips', JSON.stringify(options.caption_clips));
    }

    console.log('Sending processing request to backend...');
    const { data } = await axios.post(`${API_URL}/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Processing request successful:', data);

    // Get the download URL for the processed video
    console.log('Requesting download URL for processed video...');
    const { data: { download_url } } = await axios.get(`${API_URL}/get-download-url/${data.output_key}`);
    console.log('Download URL received:', download_url);
    
    return {
      output_key: data.output_key,
      download_url
    };
  } catch (error) {
    console.error('Error processing video:', error);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
      throw new Error(`Video processing failed: ${error.response.data.detail || error.response.data.message || 'Unknown error'}`);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      throw new Error('No response received from server. Please check your connection.');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error setting up request:', error.message);
      throw new Error(`Failed to process video: ${error.message}`);
    }
  }
};

export const downloadProcessedVideo = async (outputKey) => {
  try {
    console.log('Starting to poll for processed video...');
    
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        console.log(`Polling attempt ${attempt + 1}/5`);
        const { data: { download_url } } = await axios.get(`${API_URL}/get-download-url/${outputKey}`);
        console.log('Successfully got download URL');
        return download_url;
      } catch (error) {
        if (error.response?.status === 404) {
          if (attempt === 4) {  // Last attempt
            throw new Error('Video processing timed out');
          }
          const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
          console.log(`File not ready, waiting ${delay}ms before next attempt...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        } else {
          throw error;
        }
      }
    }
  } catch (error) {
    console.error('Error getting download URL:', error);
    throw error;
  }
};

export const pollForProcessedVideo = async (outputKey, maxAttempts = 10) => {
  console.log('Starting to poll for processed video...');
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      console.log(`Polling attempt ${attempt + 1}/${maxAttempts}`);
      const { data: { download_url } } = await axios.get(`${API_URL}/get-download-url/${outputKey}`);
      console.log('Successfully got download URL');
      return download_url;
    } catch (error) {
      if (error.response?.status === 404) {
        if (attempt === maxAttempts - 1) {
          throw new Error('Video processing timed out');
        }
        const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
        console.log(`File not ready, waiting ${delay}ms before next attempt...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
};