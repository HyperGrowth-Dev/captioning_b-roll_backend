import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const processVideo = async (file, font, color) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('font', font.family);
    formData.append('color', color.value);

    const response = await axios.post(`${API_URL}/process-video`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Upload Progress: ${percentCompleted}%`);
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error processing video:', error);
    throw error;
  }
};

export const downloadProcessedVideo = async (filename) => {
  try {
    const response = await axios.get(`${API_URL}/download/${filename}`, {
      responseType: 'blob',
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Error downloading video:', error);
    throw error;
  }
};