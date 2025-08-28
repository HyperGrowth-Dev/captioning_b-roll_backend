import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [videoUrl, setVideoUrl] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('Location state:', location.state);
    if (!location.state?.downloadUrl) {
      setError('No video URL provided');
      return;
    }

    setVideoUrl(location.state.downloadUrl);
  }, [location.state]);

  const handleDownload = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.setAttribute('download', 'processed_video.mp4');
      document.body.appendChild(link);
      link.click();
      link.remove();
    }
  };

  const handleNewVideo = () => {
    navigate('/');
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 to-black">
        <div className="text-center p-8">
          <h1 className="text-4xl font-bold text-white mb-8">Error</h1>
          <p className="text-red-400 mb-8">{error}</p>
          <button
            onClick={handleNewVideo}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Upload New Video
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-purple-900 to-black p-8">
      <h1 className="text-4xl font-bold text-white mb-8">Your Processed Video</h1>
      
      {videoUrl && (
        <div className="w-full max-w-2xl mb-8 px-4">
          <video
            src={videoUrl}
            className="w-full rounded-lg shadow-lg"
            controls
            autoPlay
            loop
            muted
          />
        </div>
      )}
      
      <div className="flex space-x-4">
        <button
          onClick={handleDownload}
          className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
          Download Video
        </button>
        
        <button
          onClick={handleNewVideo}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          Upload New Video
        </button>
      </div>
    </div>
  );
}

export default ResultsPage; 