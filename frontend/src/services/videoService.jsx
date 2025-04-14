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
    const { data: { download_url } } = await axios.get(`${API_URL}/download/${outputKey}`);
    return download_url;
  } catch (error) {
    console.error('Error getting download URL:', error);
    throw error;
  }
};