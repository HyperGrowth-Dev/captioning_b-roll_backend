import os
import json
import logging
import subprocess
import tempfile
from typing import List, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemotionLocalService:
    def __init__(self):
        logger.info("Initializing RemotionLocalService")
        self.temp_dir = tempfile.gettempdir()
        self.remotion_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'remotion')
        
        # Validate Remotion directory exists
        if not os.path.exists(self.remotion_dir):
            raise ValueError(f"Remotion directory not found at: {self.remotion_dir}")
        
        logger.info("RemotionLocalService initialized successfully")

    def process_video(
        self,
        video_path: str,
        captions: List[Dict[str, Any]],
        settings: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Process a video with captions using local Remotion rendering
        
        Args:
            video_path: Path to the input video
            captions: List of caption objects with text and timing
            settings: Video processing settings (font, color, etc.)
            
        Returns:
            Dictionary containing the output path
        """
        try:
            logger.info(f"Starting local video processing for: {video_path}")
            
            # Create a temporary directory for this render
            with tempfile.TemporaryDirectory() as temp_dir:
                # Prepare input props
                input_props = {
                    "videoSrc": video_path,
                    "captions": [
                        {
                            "text": caption["text"],
                            "startFrame": caption["startFrame"],
                            "endFrame": caption["endFrame"],
                            "words": [
                                {
                                    "text": word["text"],
                                    "startFrame": int(word["start"] * settings.get("fps", 30)),
                                    "endFrame": int(word["end"] * settings.get("fps", 30))
                                }
                                for word in caption.get("words", [])
                            ],
                            "style": {
                                "font": settings.get('font', 'Arial'),
                                "fontSize": settings.get('fontSize', 32),
                                "color": settings.get('color', '#ffffff'),
                                "position": settings.get('position', 0.5),
                                "maxWidth": settings.get('maxWidth', 800)
                            }
                        }
                        for caption in captions
                    ],
                    "transitions": settings.get('transitions', {
                        "type": "fade",
                        "duration": 15
                    }),
                    "highlightColor": settings.get('highlightColor', '#FFD700')
                }
                
                # Write input props to a temporary file
                input_props_path = os.path.join(temp_dir, 'input_props.json')
                with open(input_props_path, 'w') as f:
                    json.dump(input_props, f)
                
                # Prepare output path
                output_path = os.path.join(temp_dir, 'output.mp4')
                
                # Run Remotion render command
                cmd = [
                    'npx', 'remotion', 'render',
                    'src/compositions/Root.tsx',
                    'CaptionVideo',
                    output_path,
                    '--props', input_props_path
                ]
                
                logger.info(f"Running Remotion render command: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    cwd=self.remotion_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Remotion render failed: {result.stderr}")
                    raise RuntimeError(f"Remotion render failed: {result.stderr}")
                
                logger.info("Remotion render completed successfully")
                
                # Return the output path
                return {
                    "output_path": output_path
                }
                
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise

    def cleanup(self, output_path: str):
        """Clean up temporary files"""
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}") 