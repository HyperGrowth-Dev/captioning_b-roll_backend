import whisper
import logging
import os
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CaptionProcessor:
    def __init__(self, fps: int = 30):
        logger.info("Initializing CaptionProcessor")
        logger.info(f"Loading Whisper model with fps={fps}...")
        self.model = whisper.load_model("base")
        self.max_segment_duration = 5.0  # Maximum duration for a segment in seconds
        self.max_words_per_segment = 5  # Maximum number of words per segment
        self.fps = fps  # Initialize fps attribute
        
        # Get the absolute path to the static/fonts directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.fonts_dir = os.path.join(self.base_dir, 'static', 'fonts')
        logger.info(f"Fonts directory: {self.fonts_dir}")

    def split_long_segment(self, segment):
        """Split a segment into smaller ones with at most 3 words each"""
        logger.debug(f"Splitting segment: {segment}")
        words = segment.get('words', [])
        if not words:
            logger.debug("No words in segment, returning original")
            return [segment]

        new_segments = []
        current_words = []
        current_start = segment['start']
        word_count = 0

        for word in words:
            word_count += 1
            current_words.append(word)
            
            # Split after every 3 words
            if word_count >= self.max_words_per_segment:
                # Create new segment
                new_segment = {
                    'start': current_start,
                    'end': word['end'],
                    'text': ' '.join(w['word'] for w in current_words),
                    'words': current_words.copy()
                }
                logger.debug(f"Created new segment: {new_segment}")
                new_segments.append(new_segment)
                
                # Reset for next segment
                current_words = []
                current_start = word['end']
                word_count = 0

        # Add remaining words if any
        if current_words:
            new_segment = {
                'start': current_start,
                'end': words[-1]['end'],
                'text': ' '.join(w['word'] for w in current_words),
                'words': current_words
            }
            logger.debug(f"Created final segment: {new_segment}")
            new_segments.append(new_segment)

        logger.info(f"Split segment into {len(new_segments)} parts")
        return new_segments

    def generate_captions(self, audio_path):
        """Generate captions from audio using Whisper with word-level timestamps"""
        try:
            logger.info(f"Starting transcription of audio file: {audio_path}")
            # First pass with word timestamps
            result = self.model.transcribe(
                audio_path,
                word_timestamps=True,
                max_initial_timestamp=self.max_segment_duration
            )
            
            # Post-process segments to split long ones
            original_segments = result["segments"]
            processed_segments = []
            
            for segment in original_segments:
                # Check if segment is too long
                duration = segment['end'] - segment['start']
                word_count = len(segment.get('words', []))
                
                logger.debug(f"Processing segment: duration={duration}, word_count={word_count}")
                
                if duration > self.max_segment_duration or word_count > self.max_words_per_segment:
                    # Split the segment
                    logger.info(f"Splitting long segment: duration={duration}, word_count={word_count}")
                    split_segments = self.split_long_segment(segment)
                    processed_segments.extend(split_segments)
                else:
                    processed_segments.append(segment)
            
            logger.info(f"Transcription successful! Created {len(processed_segments)} segments")
            return processed_segments
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return None

    def create_caption_clips(self, segments: List[Dict], video_width: int, video_height: int, font: str = "Barlow-BlackItalic", color: str = "white", font_size: int = 32) -> List[Dict]:
        """Create individual caption clips with word-level timing information."""
        logger.info(f"Starting caption clip creation for {len(segments)} segments")
        
        caption_clips = []
        
        # Calculate text positioning based on video dimensions
        logger.info("Step 3: Calculating text positioning")
        text_y_position = video_height * 0.7  # 70% from the top
        max_text_width = video_width * 0.8  # 80% of video width
        logger.debug(f"Text position: y={text_y_position}, max_width={max_text_width}")
        
        logger.info("Step 4: Processing segments")
        for i, segment in enumerate(segments):
            logger.debug(f"Processing segment {i+1}/{len(segments)}: {segment['text']}")
            words = []
            if 'words' in segment:
                logger.debug(f"Processing {len(segment['words'])} words for segment {i+1}")
                for word in segment['words']:
                    logger.debug(f"Processing word: {word['word']} ({word['start']}-{word['end']})")
                    words.append({
                        'text': word['word'],
                        'start': word['start'],
                        'end': word['end']
                    })
            
            logger.debug(f"Creating caption clip for segment {i+1}")
            caption_clip = {
                'text': segment['text'],
                'startFrame': int(segment['start'] * self.fps),
                'endFrame': int(segment['end'] * self.fps),
                'words': words if words else None  # Only include words if there are any
            }
            logger.debug(f"Created caption clip: {caption_clip}")
            caption_clips.append(caption_clip)
        
        logger.info(f"Step 5: Successfully created {len(caption_clips)} caption clips")
        return caption_clips

    def save_transcript(self, segments, output_dir='output'):
        """Save transcript to a text file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            transcript_path = os.path.join(output_dir, 'transcript.txt')
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                for segment in segments:
                    # Write the text with timestamp
                    f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}\n")
                    
                    # Optionally write word-level timestamps
                    if 'words' in segment:
                        f.write("  Words: ")
                        for word in segment['words']:
                            f.write(f"{word['word']} ({word['start']:.2f}s-{word['end']:.2f}s) ")
                        f.write("\n")
                    f.write("\n")
            
            print(f"Transcript saved to: {transcript_path}")
            
            return transcript_path
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None 