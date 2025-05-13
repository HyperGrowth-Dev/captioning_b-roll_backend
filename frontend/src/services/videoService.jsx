import axios from 'axios';

// Use import.meta.env for Vite environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const uploadVideo = async (file) => {
  try {
    // Get upload URL from backend
    const { data: { upload_url, key } } = await axios.post(`${API_URL}/get-upload-url`);
    
    // Upload directly to S3
    await axios.put(upload_url, file, {
      headers: {
        'Content-Type': 'video/mp4',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Upload progress: ${percentCompleted}%`);
      },
    });
    
    return { key };
  } catch (error) {
    console.error('Error uploading video:', error);
    throw error;
  }
};

export const processVideo = async (inputKey, options) => {
  try {
    const formData = new FormData();
    formData.append('input_key', inputKey);
    formData.append('font', options.font);
    formData.append('color', options.color);
    formData.append('font_size', options.font_size);
    formData.append('position', options.position);
    formData.append('shadow_type', options.shadow_type || "none");
    formData.append('shadow_color', options.shadow_color || "black");
    formData.append('shadow_blur', options.shadow_blur || 12);
    formData.append('shadow_opacity', options.shadow_opacity || 0.9);
    formData.append('true_width', options.true_width);
    formData.append('true_height', options.true_height);

    const { data } = await axios.post(`${API_URL}/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  } catch (error) {
    console.error('Error processing video:', error);
    throw error;
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