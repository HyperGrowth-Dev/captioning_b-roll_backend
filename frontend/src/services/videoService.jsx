import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const processVideo = async (file, font, color) => {
  try {
    console.log('=== VIDEO SERVICE: STARTING PROCESS ===');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('font', font.family);
    formData.append('color', color.value);

    console.log('=== VIDEO SERVICE: SENDING REQUEST ===');
    const response = await axios.post(`${API_URL}/process-video`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`=== UPLOAD PROGRESS === ${percentCompleted}%`);
      },
    });

    console.log('=== VIDEO SERVICE: PROCESSING RESPONSE ===', response.data);
    return response.data;
  } catch (error) {
    console.error('=== VIDEO SERVICE: ERROR ===', error);
    throw error;
  }
};

export const downloadProcessedVideo = async (filename) => {
  try {
    console.log('=== VIDEO SERVICE: STARTING DOWNLOAD ===', filename);
    const response = await axios.get(`${API_URL}/download/${filename}`, {
      responseType: 'blob',
    });
    
    console.log('=== VIDEO SERVICE: BLOB RECEIVED ===', response.data);
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'video/mp4' }));
    console.log('=== VIDEO SERVICE: BLOB URL CREATED ===', url);
    return url;
  } catch (error) {
    console.error('=== VIDEO SERVICE: DOWNLOAD ERROR ===', error);
    throw error;
  }
};