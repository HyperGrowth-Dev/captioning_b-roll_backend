import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from dotenv import load_dotenv
import tempfile
import logging
from caption_processor import CaptionProcessor
from broll_analyzer import BrollAnalyzer
from utils import setup_logging, ensure_directory, TempDirManager
import traceback

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
        
    def extract_audio(self, video_path):
        """Extract audio from video and save as WAV"""
        try:
            logger.info(f"Loading video file: {video_path}")
            video = VideoFileClip(video_path)
            audio = video.audio
            
            # Create a temporary WAV file with specific parameters
            temp_dir = self.temp_manager.create_temp_dir(prefix='audio_')
            temp_audio = os.path.join(temp_dir, 'audio.wav')
            logger.info(f"Extracting audio to: {temp_audio}")
            audio.write_audiofile(temp_audio, fps=16000, nbytes=2, codec='pcm_s16le')
            return temp_audio
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return None

    def process_video(self, input_path, font="Montserrat-Bold", color="white", font_size=48):
        """Process a video file with custom font and color settings"""
        try:
            # Load video
            video = VideoFileClip(input_path)
            
            # Extract audio
            audio = video.audio
            audio_path = "temp/audio.wav"
            audio.write_audiofile(audio_path)
            
            # Generate captions
            segments = self.caption_processor.generate_captions(audio_path)
            
            # Create caption clips with custom settings
            caption_clips = self.caption_processor.create_caption_clips(
                segments, 
                video.w,  # video width
                video.h,  # video height
                font=font,
                color=color,
                font_size=font_size
            )
            
            # Combine video and captions
            final_video = CompositeVideoClip([video] + caption_clips)
            
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