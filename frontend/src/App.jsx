import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import ProcessingPage from './pages/ProcessingPage';
import ResultsPage from './pages/ResultsPage';

function UploadPage() {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
      navigate('/processing', { state: { file: droppedFile } });
    } else {
      alert('Please upload a video file');
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      navigate('/processing', { state: { file: selectedFile } });
    } else {
      alert('Please upload a video file');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl relative">
        <div className="absolute inset-0 bg-purple-500/20 blur-3xl -z-10"></div>
        
        <h1 className="text-5xl font-bold text-center mb-2 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-violet-300 animate-[pulse_4s_ease-in-out_infinite]">
          AI Caption Editor
        </h1>
        <p className="text-center text-purple-200 mb-12 text-lg">
          Upload your video to add AI-generated captions and B-roll suggestions
        </p>
        
        <div
          className={clsx(
            "cyber-border backdrop-blur-xl rounded-2xl p-12",
            "flex flex-col items-center justify-center",
            "transition-all duration-300 glow",
            isDragging ? "bg-purple-900/30" : "bg-purple-950/30",
            "cursor-pointer group animate-[float_6s_ease-in-out_infinite]"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <input
            type="file"
            id="fileInput"
            className="hidden"
            accept="video/*"
            onChange={handleFileSelect}
          />
          
          <CloudArrowUpIcon className={clsx(
            "w-20 h-20 mb-6",
            "transition-all duration-300",
            isDragging ? "text-purple-400" : "text-purple-500/70 group-hover:text-purple-400",
            "animate-[float_4s_ease-in-out_infinite]"
          )} />
          
          <p className="text-xl mb-3 font-medium text-purple-100">
            {file ? file.name : 'Drop your video here'}
          </p>
          <p className="text-sm text-purple-300/80">
            {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : 'or click to browse'}
          </p>
        </div>

        {file && (
          <div className="mt-10 flex justify-center">
            <button
              className="cyber-border bg-purple-600/30 hover:bg-purple-500/40 text-purple-100 px-8 py-4 rounded-xl font-medium 
                         transition-all duration-300 backdrop-blur-lg hover:scale-105 transform"
              onClick={() => navigate('/processing', { state: { file } })}
            >
              Process Video
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/processing" element={<ProcessingPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
}

export default App;