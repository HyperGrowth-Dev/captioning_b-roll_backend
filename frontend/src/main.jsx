import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Import fonts
import '@fontsource/montserrat/400.css';
import '@fontsource/montserrat/600.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/barlow/400.css';
import '@fontsource/barlow/700.css';
import '@fontsource/barlow/900.css';
import '@fontsource/oswald/400.css';
import '@fontsource/oswald/600.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)