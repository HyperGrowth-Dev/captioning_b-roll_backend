import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, TextClip
from moviepy.video.fx.all import resize, fadein, fadeout
import requests
from dotenv import load_dotenv
import tempfile
import logging
from caption_processor import CaptionProcessor
from broll_analyzer import BrollAnalyzer
from utils import setup_logging, ensure_directory, TempDirManager
from utils.ffmpeg_utils import FFmpegUtils
import traceback
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import asyncio
from backend.services.remotion_service import RemotionService
import argparse
import sys

# Load environment variables
load_dotenv()

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level for more detailed logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set boto3 and botocore to WARNING level to reduce noise
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Initialize logger
logger = setup_logging(__name__, 'video_processor.log')

def print_broll_analysis(analysis: dict, output_file: str = 'broll_suggestions.txt'):
    """Print b-roll analysis in a readable format to a text file"""
    try:
        # Ensure output directory exists
        ensure_directory('output')
        output_path = os.path.join('output', output_file)
        
        logger.info(f"Writing b-roll analysis to: {output_path}")
        logger.debug(f"Analysis content: {analysis}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== B-ROLL SUGGESTIONS ===\n\n")
            
            # Print b-roll suggestions
            f.write("B-ROLL SUGGESTIONS BY TIMESTAMP:\n")
            f.write("=" * 50 + "\n\n")
            
            if not analysis.get('broll_suggestions'):
                f.write("No b-roll suggestions found.\n")
                logger.warning("No b-roll suggestions found in analysis")
            else:
                logger.info(f"Found {len(analysis['broll_suggestions'])} b-roll suggestions")
                for suggestion in analysis['broll_suggestions']:
                    f.write(f"Time: {suggestion['timestamp']}s\n")
                    f.write(f"Duration: {suggestion['duration']}s\n")
                    f.write(f"Keyword: {suggestion['keyword']}\n")
                    f.write(f"Confidence: {suggestion['confidence']:.2f}\n")
                    f.write(f"Context: {suggestion['context']}\n")
                    f.write("\nB-roll options:\n")
                    
                    for i, option in enumerate(suggestion['broll_options'], 1):
                        f.write(f"\nOption {i}:\n")
                        f.write(f"  URL: {option['url']}\n")
                        f.write(f"  Quality: {option['quality']}\n")
                        f.write(f"  Resolution: {option['width']}x{option['height']}\n")
                    
                    f.write("\n" + "-" * 50 + "\n\n")
            
            logger.info(f"B-roll analysis printed to: {output_path}")
            
    except Exception as e:
        logger.error(f"Error printing b-roll analysis: {str(e)}")
        logger.error(f"Analysis content: {analysis}")

# class VideoProcessor:
#     def __init__(self):
#         logger.info("Initializing VideoProcessor")
#         self.caption_processor = CaptionProcessor(fps=30)  # Set default fps to 30
#         pexels_key = os.getenv('PEXELS_API_KEY')
#         if not pexels_key:
#             logger.error("PEXELS_API_KEY not found in environment variables")
#             raise ValueError("PEXELS_API_KEY is required")
#         self.broll_analyzer = BrollAnalyzer(pexels_key)
#         self.temp_manager = TempDirManager()
#         logger.info("Initialized temporary directory manager")

#     def download_broll_video(self, url, temp_dir):
#         """Download b-roll video from URL"""
#         try:
#             response = requests.get(url, stream=True)
#             response.raise_for_status()
            
#             # Create a temporary file for the video
#             temp_path = os.path.join(temp_dir, f'broll_{hash(url)}.mp4')
            
#             with open(temp_path, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)
            
#             return temp_path
#         except Exception as e:
#             logger.error(f"Error downloading b-roll video: {str(e)}")
#             return None

#     def create_broll_clip(self, video_path, duration=5.0, transition_duration=0.2):
#         """Create a b-roll clip with transitions"""
#         try:
#             # Load the b-roll video
#             broll = VideoFileClip(video_path)
            
#             # Trim to desired duration
#             broll = broll.subclip(0, min(duration, broll.duration))
            
#             # Apply fade in/out transitions using the fx functions
#             broll = fadein(broll, transition_duration)
#             broll = fadeout(broll, transition_duration)
            
#             return broll
#         except Exception as e:
#             logger.error(f"Error creating b-roll clip: {str(e)}")
#             return None

#     async def process_video(self, input_path, font="Montserrat-Bold", color="white", font_size=32):
#         """Process a video file with custom font and color settings"""
#         try:
#             # Get video info using FFmpeg
#             main_width, main_height, video_duration = FFmpegUtils.get_video_info(input_path)
            
#             # Extract audio using FFmpeg
#             audio_path = "temp/audio.wav"
#             os.makedirs("temp", exist_ok=True)
#             FFmpegUtils.extract_audio(input_path, audio_path)
            
#             # Generate captions
#             segments = self.caption_processor.generate_captions(audio_path)
            
#             # Get b-roll suggestions
#             broll_suggestions = self.broll_analyzer.get_broll_suggestions(
#                 segments,
#                 video_duration=video_duration,
#                 video_width=main_width,
#                 video_height=main_height
#             )
            
#             # Download and process b-roll clips
#             broll_clips = []
#             for suggestion in broll_suggestions:
#                 if suggestion['broll_options']:
#                     # Get the first b-roll option
#                     broll_option = suggestion['broll_options'][0]
                    
#                     # Download the b-roll video
#                     temp_dir = "temp/broll"
#                     os.makedirs(temp_dir, exist_ok=True)
#                     broll_path = self.download_broll_video(broll_option['url'], temp_dir)
                    
#                     if broll_path:
#                         # Convert to Remotion format
#                         broll_clips.append({
#                             'url': broll_path,
#                             'startFrame': int(suggestion['timestamp'] * 30),  # Assuming 30fps
#                             'endFrame': int((suggestion['timestamp'] + suggestion['duration']) * 30),
#                             'transitionDuration': 15  # 0.5s transition at 30fps
#                         })
            
#             # Create caption clips with custom settings
#             caption_data = self.caption_processor.create_caption_clips(
#                 segments, 
#                 main_width,
#                 main_height,
#                 font=font,
#                 color=color,
#                 font_size=font_size
#             )
            
#             # Initialize RemotionService
#             remotion_service = RemotionService()
            
#             # Process video with Remotion
#             settings = {
#                 'font': font,
#                 'color': color,
#                 'fontSize': font_size,
#                 'fps': 30,
#                 'position': 0.7,
#                 'maxWidth': main_width * 0.8,
#                 'highlightColor': '#FFD700',
#                 'videoUrl': input_path,
#                 'brollClips': broll_clips  # Add b-roll clips to settings
#             }
            
#             output_url = await remotion_service.process_video(
#                 input_path,
#                 settings
#             )
            
#             # Clean up
#             os.remove(audio_path)
#             for clip in broll_clips:
#                 if os.path.exists(clip['url']):
#                     os.remove(clip['url'])
            
#             return output_url
            
#         except Exception as e:
#             logger.error(f"Error processing video: {str(e)}")
#             raise

async def debug_process_video(input_path: str, font: str = "Montserrat-Bold", color: str = "white", font_size: int = 32):
    """Debug function to process a single video with detailed logging"""
    try:
        logger.info(f"Starting debug process for video: {input_path}")
        
        # Step 1: Get video info
        logger.info("Step 1: Getting video info...")
        video_width, video_height, video_duration, fps = FFmpegUtils.get_video_info(input_path)
        logger.debug(f"Video dimensions: {video_width}x{video_height}, duration: {video_duration}s, fps: {fps}")
        
        # Step 2: Extract audio
        logger.info("Step 2: Extracting audio...")
        audio_path = "temp/audio.wav"
        os.makedirs("temp", exist_ok=True)
        FFmpegUtils.extract_audio(input_path, audio_path)
        logger.debug(f"Audio extracted to: {audio_path}")
        
        # Step 3: Generate captions
        caption_processor = CaptionProcessor(fps=fps)  # Pass the actual FPS
        segments = caption_processor.generate_captions(audio_path)
        
        # Create caption clips
        caption_clips = caption_processor.create_caption_clips(
            segments,
            video_width=video_width,
            video_height=video_height,
            font=font,
            color=color,
            font_size=font_size
        )
        video_url = "https://hyper-editor.s3.us-east-2.amazonaws.com/uploads/d2025482-4a7b-4f4b-b055-72e29fffb1c2.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBwaCXVzLWVhc3QtMiJHMEUCIFbwr6i4Vslhk7wNe0liGlBYtdkmtDJ7zLxZHrPcT7WiAiEA6Uc%2BggZR44JptFDrUkUAxuFkc90B02u2NuUWK1YIHjoqwgMI9f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw4ODg1NzcwNDMwMDMiDCwRJuwauIv%2FuIsJhCqWAx%2Bsl8bzrHRcIKateGQigBOaO7ngGx7EWsJAcs%2B7Msk3o9i1fYDYcEMFcwygLP%2FGOzlxRXfrfg5gVMLS97uXjAKs96OTg6mSzaWCvn1hyXCDkHiR9Fhn5egtlsM2pjB2fNBFdLj3BIz7mQ5idx3vz%2FpZijpazZd6t%2FqjWWSwUdkMbkRD%2FI75tfRnOmQQS1SWi8dXmVW2PjuzEiG7nlsXedgwjekJ0FZcvwPTaGkgBChfgll8g4oeMtz1HLleUdJYtDqAkgr0uPTj1Efa%2FeXxjVvzMMuZn3Ys5V9mOTq6N5yrf5zZHA%2BiaHv6xim3BcGp%2F9CHGSM1C14FPEwG1W99CH3ea%2FGR0yEBuQ0n9kwZSjT65sLa47yoy88Vg0ZkasxcMa8ax34s7lgQ%2BtUhJOR%2FYc%2BdZzZiHOHQiZd%2Bx6ysViSAL0elI5d7ThrBFk%2FFf9G81pJIeSXPXwG13vVVWzxnrTW5sysTI8ZgVuh3mMZyQXdyxxOn2jD6kvR3PjI7DmlCl3Uvtc%2B%2F3KEydoE4TgDVoT%2Bn3fGTV0wwrdqswgY63gKW3ZENCB4J5PwW0ZmrTvMu29s20oB5aGWcKlbiroNS8fjraWYFlZTh%2BOYVYAWjF7L%2FrEW6kSUnPWZuPkqhnMqPAq4UbAsVe%2FSvpROOoIr2gN6Ovs3%2FoZyKq39YvkFUEQWO2lPmFSb5Odc8YNwMkDs3B3w0HC2hZlJFYtRX4NArknnNiZ%2FBa2jJ4PQg7qtSBmIpm9tVEWOZgQKME3hqqvfxXGtQdXZp4t3TvwjPGLQcpTZIkUPNhIOAKaBPoBPZIkjANYkgAkV4BwuZxp9mNs0oDGSs52O4yYA1tmmwBUr8HeAJwkXavIIg%2BWR1b7cJWYZ39OMhKgqyHSPeOURBgumdMcJk3uIqpmumX0YHVpy1CmBq0CGh8Vdm6TcYAzhSmd4YIfxP9cIu4xqX1sjcfpSz%2BQbDFKFw%2FLwoJ70lMat4EKqjDUUNSpO7WE5%2BwMLV3YDvVXFqs1AvYqFGsyCaoA%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA45Y2RVI5TUDOZD5R%2F20250612%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250612T194052Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=37c21e2cda430fa051a1724c2e97415fd5e4385aaf866b6d018342381607aa0d"
        # Process video using Remotion
        remotion_service = RemotionService()
        output_key = "output"
        result = remotion_service.process_video(
            video_url,                # e.g., "https://s3.amazonaws.com/bucket/video.mp4"
            output_key,               # e.g., "processed/myvideo.mp4"
            caption_clips,            # e.g., a list of caption dicts
            broll_enabled=True,       # or False
            video_width=video_width,          # or your desired width
            video_height=video_height,        # or your desired height
            fps=fps,                   # or your video's FPS
            font="Montserrat-Bold",   # or your desired font
            color="white",            # or your desired color
            font_size=32,             # or your desired font size
            highlight_type="fill" # or "none", etc.
        )
        
        
    except Exception as e:
        logger.error(f"Error in debug process: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def main():

    await debug_process_video(
            input_path="input/brett_1.mp4"
        )

if __name__ == "__main__":
    asyncio.run(main())

def resize(clip, width=None, height=None, newsize=None):
    """Resize a video clip while maintaining aspect ratio"""
    if newsize is not None:
        target_width, target_height = newsize
    else:
        target_width, target_height = width, height
    
    def resizer(pic, target_size):
        pilim = Image.fromarray(pic)
        original_width, original_height = pilim.size
        
        # Calculate aspect ratios
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height
        
        # Calculate new dimensions while maintaining aspect ratio
        if original_ratio > target_ratio:
            # Image is wider than target
            new_width = target_width
            new_height = int(target_width / original_ratio)
        else:
            # Image is taller than target
            new_height = target_height
            new_width = int(target_height * original_ratio)
        
        # Resize the image
        resized_pil = pilim.resize((new_width, new_height), Image.LANCZOS)
        
        # Create a new image with the target size and paste the resized image in the center
        new_im = Image.new('RGB', (target_width, target_height), (0, 0, 0))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        new_im.paste(resized_pil, (paste_x, paste_y))
        
        return np.array(new_im)
    
    fl = lambda pic: resizer(pic.astype('uint8'), (target_width, target_height))
    newclip = clip.fl_image(fl)
    return newclip 