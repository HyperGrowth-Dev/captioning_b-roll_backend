import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.all import resize, fadein, fadeout
import requests
from dotenv import load_dotenv
import tempfile
import logging
from caption_processor import CaptionProcessor
from broll_analyzer import BrollAnalyzer
from utils import setup_logging, ensure_directory, TempDirManager
import traceback
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Load environment variables
load_dotenv()

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

class VideoProcessor:
    def __init__(self):
        logger.info("Initializing VideoProcessor")
        self.caption_processor = CaptionProcessor()
        pexels_key = os.getenv('PEXELS_API_KEY')
        if not pexels_key:
            logger.error("PEXELS_API_KEY not found in environment variables")
            raise ValueError("PEXELS_API_KEY is required")
        self.broll_analyzer = BrollAnalyzer(pexels_key)
        self.temp_manager = TempDirManager()
        logger.info("Initialized temporary directory manager")

    def download_broll_video(self, url, temp_dir):
        """Download b-roll video from URL"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Create a temporary file for the video
            temp_path = os.path.join(temp_dir, f'broll_{hash(url)}.mp4')
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
        except Exception as e:
            logger.error(f"Error downloading b-roll video: {str(e)}")
            return None

    def create_broll_clip(self, video_path, duration=5.0, transition_duration=0.2):
        """Create a b-roll clip with transitions"""
        try:
            # Load the b-roll video
            broll = VideoFileClip(video_path)
            
            # Trim to desired duration
            broll = broll.subclip(0, min(duration, broll.duration))
            
            # Apply fade in/out transitions using the fx functions
            broll = fadein(broll, transition_duration)
            broll = fadeout(broll, transition_duration)
            
            return broll
        except Exception as e:
            logger.error(f"Error creating b-roll clip: {str(e)}")
            return None

    def process_video(self, input_path, font="Montserrat-Bold", color="white", font_size=32, position=0.7):
        """Process a video file with custom font and color settings"""
        try:
            # Load video
            video = VideoFileClip(input_path)
            main_width, main_height = video.w, video.h
            video_duration = video.duration
            
            # Extract audio
            audio = video.audio
            audio_path = "temp/audio.wav"
            audio.write_audiofile(audio_path)
            
            # Generate captions
            segments = self.caption_processor.generate_captions(audio_path)
            
            # Create caption clips with custom settings
            caption_clips = self.caption_processor.create_caption_clips(
                segments, 
                main_width,
                main_height,
                font=font,
                color=color,
                font_size=font_size,
                position=position
            )
            
            # Get b-roll suggestions from transcript segments
            broll_suggestions = {
                'broll_suggestions': self.broll_analyzer.get_broll_suggestions(
                    segments, 
                    video_duration,
                    video_width=main_width,
                    video_height=main_height
                )
            }
            
            # Save b-roll analysis in both formats
            #print_broll_analysis(broll_suggestions)  # Save as text file
            self.broll_analyzer.save_analysis(broll_suggestions)  # Save as JSON
            
            # Create a temporary directory for b-roll videos
            temp_dir = self.temp_manager.create_temp_dir(prefix='broll_')
            
            # Create clips list starting with main video
            all_clips = [(video, 0)]  # Main video with z_index 0
            
            # Add b-roll clips at suggested timestamps
            if broll_suggestions and 'broll_suggestions' in broll_suggestions:
                for suggestion in broll_suggestions['broll_suggestions']:
                    timestamp = suggestion['timestamp']
                    duration = 3.0  # Fixed duration of 3 seconds
                    
                    # Skip if timestamp is beyond video duration
                    if timestamp >= video_duration:
                        logger.warning(f"Skipping b-roll at timestamp {timestamp}s as it's beyond video duration ({video_duration}s)")
                        continue
                    
                    # Adjust duration if it would exceed video end
                    if timestamp + duration > video_duration:
                        duration = video_duration - timestamp
                        logger.info(f"Adjusted b-roll duration to {duration}s to fit within video")
                    
                    # Download the first b-roll option
                    if suggestion['broll_options']:
                        broll_url = suggestion['broll_options'][0]['url']
                        broll_path = self.download_broll_video(broll_url, temp_dir)
                        
                        if broll_path:
                            # Create b-roll clip with transitions
                            broll_clip = self.create_broll_clip(
                                broll_path,
                                duration=duration,
                                transition_duration=0.2  # Quick transitions
                            )
                            
                            if broll_clip:
                                # Resize b-roll to match main video dimensions
                                broll_clip = resize(broll_clip, width=main_width, height=main_height)
                                
                                # Set the start time for the b-roll clip
                                broll_clip = broll_clip.set_start(timestamp)
                                
                                # Add b-roll clip to the list with z_index
                                all_clips.append((broll_clip, 1))  # B-roll clip with z_index 1
            
            # Create the final composite video with z_index
            final_video = CompositeVideoClip(
                [clip for clip, _ in all_clips] + caption_clips,
                size=(main_width, main_height)
            )
            
            # Set the audio from the main video
            final_video = final_video.set_audio(audio)
            
            # Save processed video
            output_path = os.path.join('output', 'processed_video.mp4')
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp/temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            video.close()
            final_video.close()
            os.remove(audio_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise

def main():
    processor = VideoProcessor()
    
    # Process all videos in the input directory
    input_dir = 'input'
    for filename in os.listdir(input_dir):
        if filename.endswith(('.mp4', '.avi', '.mov')):
            input_path = os.path.join(input_dir, filename)
            print(f"\nProcessing {filename}...")
            processor.process_video(input_path)
            break  # Only process the first video

if __name__ == "__main__":
    main() 

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