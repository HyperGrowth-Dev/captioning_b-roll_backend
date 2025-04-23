import subprocess
import json
import logging
import os
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FFmpegUtils:
    @staticmethod
    def get_video_info(video_path: str) -> Tuple[int, int, float]:
        """
        Get video dimensions and duration using FFmpeg
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Tuple of (width, height, duration)
        """
        try:
            # Run FFprobe to get video information
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-show_entries', 'format=duration',
                '-of', 'json',
                video_path
            ]
            
            logger.info(f"Running FFprobe command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {result.stderr}")
            
            # Parse the JSON output
            info = json.loads(result.stdout)
            width = info['streams'][0]['width']
            height = info['streams'][0]['height']
            duration = float(info['format']['duration'])
            
            logger.info(f"Video info: {width}x{height}, duration: {duration}s")
            return width, height, duration
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise

    @staticmethod
    def extract_audio(video_path: str, output_path: str) -> None:
        """
        Extract audio from video using FFmpeg
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the audio file
        """
        try:
            # Run FFmpeg to extract audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono audio
                '-y',  # Overwrite output file
                output_path
            ]
            
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            logger.info(f"Audio extracted successfully to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise 