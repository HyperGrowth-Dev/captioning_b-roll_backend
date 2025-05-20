// Default and maximum number of rows to display in the editor
export const INITIAL_ROWS = 5;
export const MAX_ROWS = 8;
// Frames per second for video rendering
export const FPS = 30;

// Name of the component being tested/rendered
export const COMP_NAME = "TestComponent";

// Video configuration
export const DURATION_IN_FRAMES = 500;
export const VIDEO_WIDTH = 1280; // 720p HD video dimensions
export const VIDEO_HEIGHT = 720;

// AWS deployment configuration
export const SITE_NAME = "sams-site";
export const LAMBDA_FUNCTION_NAME =
  "remotion-render-4-0-273-mem2048mb-disk2048mb-120sec";
export const REGION = "us-east-2";

// UI configuration
export const ROW_HEIGHT = 40; // Height of each row in pixels

// Zoom control configuration
export const ZOOM_CONSTRAINTS = {
  min: 1, // Minimum zoom level
  max: 10, // Maximum zoom level
  step: 0.1, // Smallest increment for manual zoom controls
  default: 1, // Default zoom level
  zoomStep: 0.15, // Zoom increment for zoom in/out buttons
  wheelStep: 0.3, // Zoom increment for mouse wheel
  transitionDuration: 100, // Animation duration in milliseconds
  easing: "cubic-bezier(0.4, 0.0, 0.2, 1)", // Smooth easing function for zoom transitions
};

// Render configuration
// NOTE: TO CHANGE RENDER TYPE, UPDATE THE RENDER_TYPE CONSTANT
export const RENDER_TYPE: "ssr" | "lambda" = "ssr";

// Autosave configuration
export const AUTO_SAVE_INTERVAL = 10000; // Autosave every 10 seconds
