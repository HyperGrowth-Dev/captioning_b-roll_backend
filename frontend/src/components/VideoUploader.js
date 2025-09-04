import React, { useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

function VideoUploader() {
  const { isAuthenticated, loginWithRedirect, logout, getAccessTokenSilently, user } = useAuth0();
  const [file, setFile] = useState(null);
  const [font, setFont] = useState('Montserrat-Bold');
  const [color, setColor] = useState('#FFFFFF');
  const [fontSize, setFontSize] = useState(48);
  const [highlightType, setHighlightType] = useState('background');
  const [brollEnabled, setBrollEnabled] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      await loginWithRedirect();
      return;
    }

    console.log('B-roll enabled:', brollEnabled);
    setProcessing(true);
    setError(null);

    console.log('Selected highlight type:', highlightType);

    try {
      // Get the access token for API calls
      const token = await getAccessTokenSilently();
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('font', font);
      formData.append('color', color);
      formData.append('font_size', fontSize);
      formData.append('highlight_type', highlightType);
      formData.append('broll_enabled', brollEnabled);

      console.log('FormData highlight_type:', formData.get('highlight_type'));

      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Success:', result);
      setProcessing(false);
      
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
      setProcessing(false);
    }
  };

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-6">
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900">Video Caption Generator</h2>
            <p className="mt-2 text-sm text-gray-600">
              Please log in to upload and process videos
            </p>
          </div>
          
          <button
            onClick={() => loginWithRedirect()}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Log In with Auth0
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-6">
        {/* User Info Header */}
        <div className="mb-6 text-center">
          <h2 className="text-2xl font-bold text-gray-900">Video Caption Generator</h2>
          <p className="mt-2 text-sm text-gray-600">
            Welcome, {user?.name || user?.email || 'User'}!
          </p>
          <button
            onClick={() => logout({ returnTo: window.location.origin })}
            className="mt-2 text-sm text-indigo-600 hover:text-indigo-500"
          >
            Log Out
          </button>
        </div>

        {/* Your existing form content */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Video File
            </label>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setFile(e.target.files[0])}
              className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              required
            />
          </div>

          {/* Font selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Font
            </label>
            <select
              value={font}
              onChange={(e) => setFont(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="Montserrat-Bold">Montserrat Bold</option>
              <option value="Arial">Arial</option>
              <option value="Helvetica">Helvetica</option>
            </select>
          </div>

          {/* Color selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Text Color
            </label>
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="mt-1 block w-full h-10 rounded-md border-gray-300"
            />
          </div>

          {/* Font size */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Font Size: {fontSize}px
            </label>
            <input
              type="range"
              min="24"
              max="72"
              value={fontSize}
              onChange={(e) => setFontSize(parseInt(e.target.value))}
              className="mt-1 block w-full"
            />
          </div>

          {/* Highlight type */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Highlight Type
            </label>
            <select
              value={highlightType}
              onChange={(e) => setHighlightType(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="background">Background</option>
              <option value="outline">Outline</option>
              <option value="none">None</option>
            </select>
          </div>

          {/* B-roll toggle */}
          <div className="flex items-center">
            <input
              id="broll-enabled"
              type="checkbox"
              checked={brollEnabled}
              onChange={(e) => setBrollEnabled(e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor="broll-enabled" className="ml-2 block text-sm text-gray-900">
              Enable B-roll suggestions
            </label>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={processing || !file}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {processing ? 'Processing...' : 'Process Video'}
          </button>

          {/* Error display */}
          {error && (
            <div className="text-red-600 text-sm text-center">
              Error: {error}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

export default VideoUploader;