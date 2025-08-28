import React, { useState } from 'react';

function VideoUploader() {
  const [file, setFile] = useState(null);
  const [font, setFont] = useState('Montserrat-Bold');
  const [color, setColor] = useState('white');
  const [fontSize, setFontSize] = useState(32);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [highlightType, setHighlightType] = useState("background");
  const [brollEnabled, setBrollEnabled] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('B-roll enabled:', brollEnabled);
    setProcessing(true);
    setError(null);

    console.log('Selected highlight type:', highlightType);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('font', font);
    formData.append('color', color);
    formData.append('font_size', fontSize);
    formData.append('highlight_type', highlightType);
    formData.append('broll_enabled', brollEnabled);

    console.log('FormData highlight_type:', formData.get('highlight_type'));

    try {
      const response = await fetch('http://localhost:8000/process-video', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-6">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900">Video Caption Generator</h2>
          <p className="mt-2 text-sm text-gray-600">
            Upload a video and customize your captions
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Section */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Upload Video
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
              <div className="space-y-1 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500">
                    <span>Upload a file</span>
                    <input
                      type="file"
                      accept="video/*"
                      className="sr-only"
                      onChange={(e) => setFile(e.target.files[0])}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">MP4, MOV up to 100MB</p>
              </div>
            </div>
            {file && (
              <p className="mt-2 text-sm text-gray-500">
                Selected: {file.name}
              </p>
            )}
          </div>

          {/* Font Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Caption Font
            </label>
            <select
              value={font}
              onChange={(e) => setFont(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="Montserrat-Bold">Montserrat Bold</option>
              <option value="DancingScript-SemiBold">Dancing Script</option>
              <option value="Barlow-Bold">Barlow Bold</option>
              <option value="Oswald-Regular">Oswald Regular</option>
              <option value="Oswald-SemiBold">Oswald SemiBold</option>
            </select>
          </div>

          {/* Color Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Caption Color
            </label>
            <select
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="white">White</option>
              <option value="yellow">Yellow</option>
              <option value="#FF4500">Orange Red</option>
              <option value="rgb(255, 215, 0)">Gold</option>
              <option value="black">Black</option>
              <option value="#00FF00">Neon Green</option>
            </select>
          </div>

          {/* Highlight Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Highlight Type
            </label>
            <div className="mt-2 space-y-4">
              <div className="flex items-center space-x-3">
                <input
                  type="radio"
                  id="background"
                  name="highlightType"
                  value="background"
                  checked={highlightType === "background"}
                  onChange={(e) => setHighlightType(e.target.value)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="background" className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Background Highlight</span>
                    <div className="px-3 py-2 bg-gray-100 rounded-md">
                      <span className="text-gray-900">Example text</span>
                    </div>
                  </div>
                </label>
              </div>
              <div className="flex items-center space-x-3">
                <input
                  type="radio"
                  id="fill"
                  name="highlightType"
                  value="fill"
                  checked={highlightType === "fill"}
                  onChange={(e) => setHighlightType(e.target.value)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="fill" className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Word-by-Word Highlight</span>
                    <div className="px-3 py-2 bg-gray-100 rounded-md">
                      <span className="text-gray-900">Example <span className="bg-yellow-300">text</span></span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          {/* Font Size Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Font Size: {fontSize}px
            </label>
            <input
              type="range"
              min="24"
              max="96"
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
              className="mt-1 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>24px</span>
              <span>96px</span>
            </div>
          </div>

          {/* B-roll Enabled Checkbox */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              B-roll Enabled
            </label>
            <input
              type="checkbox"
              checked={brollEnabled}
              onChange={(e) => setBrollEnabled(e.target.checked)}
              className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!file || processing}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
              !file || processing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
            }`}
          >
            {processing ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Processing...
              </>
            ) : (
              'Generate Captions'
            )}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Success Message & Download Link */}
        {result && (
          <div className="mt-4 bg-green-50 border-l-4 border-green-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-green-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">
                  Video processed successfully!
                </p>
                <div className="mt-4">
                  <a
                    href={`http://localhost:8000${result.download_url}`}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    download
                  >
                    Download Video
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoUploader; 