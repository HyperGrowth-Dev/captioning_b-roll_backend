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

    def process_video(self, input_video_path):
        """Process video and add captions"""
        try:
            logger.info(f"Processing video: {input_video_path}")
            
            # Step 1: Extract audio
            audio_path = self.extract_audio(input_video_path)
            if not audio_path:
                return
            
            # Step 2: Generate captions using CaptionProcessor
            logger.info("Generating captions...")
            segments = self.caption_processor.generate_captions(audio_path)
            if not segments:
                logger.error("No segments generated from audio")
                return
            
            logger.info(f"Generated {len(segments)} segments")
            logger.debug(f"First segment: {segments[0] if segments else None}")
            
            # Save transcript
            self.caption_processor.save_transcript(segments)
            
            # Step 3: Analyze for b-roll opportunities
            logger.info("Analyzing for b-roll opportunities...")
            broll_analysis = self.broll_analyzer.analyze_transcript(segments)
            
            if not broll_analysis:
                logger.error("No b-roll analysis generated")
                return
                
            logger.info("B-roll analysis completed")
            logger.debug(f"Analysis content: {broll_analysis}")
            
            # Save b-roll analysis
            self.broll_analyzer.save_analysis(broll_analysis)
            
            # Print b-roll analysis in readable format
            print_broll_analysis(broll_analysis)
            
            # Step 4: Load the video
            logger.info("Loading video for caption overlay...")
            video = VideoFileClip(input_video_path)
            
            # Step 5: Create caption clips
            logger.info("Creating caption clips...")
            caption_clips = self.caption_processor.create_caption_clips(segments, video.w)
            
            # Step 6: Add captions to video
            logger.info("Compositing final video...")
            final_video = CompositeVideoClip([video] + caption_clips)
            
            # Create output directory if it doesn't exist
            ensure_directory('output')
            
            # Generate output filename
            output_path = os.path.join('output', 'processed_video.mp4')
            
            logger.info("Rendering final video...")
            final_video.write_videofile(output_path, 
                                      codec='libx264', 
                                      audio_codec='aac',
                                      threads=4,
                                      preset='medium')
            
            # Clean up
            video.close()
            final_video.close()
            
            logger.info(f"Video processing complete! Output saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            raise
        finally:
            # Clean up all temporary files
            self.temp_manager.cleanup_all()

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