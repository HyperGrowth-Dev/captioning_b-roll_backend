import subprocess
import json
import logging
import os
from typing import Tuple, Optional
import ffmpeg

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
            # First check if the video has an audio stream
            probe = ffmpeg.probe(video_path)
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            
            if not audio_streams:
                logger.warning(f"No audio stream found in video: {video_path}")
                # Create an empty WAV file with silence
                cmd = [
                    'ffmpeg',
                    '-f', 'lavfi',
                    '-i', 'anullsrc=r=16000:cl=mono',
                    '-t', '1',  # 1 second of silence
                    '-y',
                    output_path
                ]
            else:
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

    @staticmethod
    def preprocess_video(input_path: str, output_path: str, max_resolution: int = 1080) -> None:
        """Preprocess video to a more manageable size while maintaining quality"""
        try:
            # Get video info
            probe = ffmpeg.probe(input_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            
            # Calculate new dimensions maintaining aspect ratio
            if height > max_resolution:
                new_height = max_resolution
                new_width = int(width * (max_resolution / height))
            else:
                new_width = width
                new_height = height
            
            # Process video
            stream = ffmpeg.input(input_path)
            
            # Split video and audio streams
            video = stream.video.filter('scale', new_width, new_height)
            audio = stream.audio
            
            # Combine streams back together
            stream = ffmpeg.output(video, audio, output_path, 
                                 vcodec='libx264',
                                 acodec='aac',
                                 video_bitrate='4M',
                                 audio_bitrate='192k')
            
            ffmpeg.run(stream, overwrite_output=True)
        except Exception as e:
            logger.error(f"Error preprocessing video: {str(e)}")
            raise 