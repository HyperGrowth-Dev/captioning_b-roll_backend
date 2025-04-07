import whisper
from moviepy.video.VideoClip import TextClip
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaptionProcessor:
    def __init__(self):
        print("Loading Whisper model...")
        self.model = whisper.load_model("base")
        self.max_segment_duration = 5.0  # Maximum duration for a segment in seconds
        self.max_words_per_segment = 3  # Maximum number of words per segment
        
        # Get the absolute path to the static/fonts directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.fonts_dir = os.path.join(self.base_dir, 'static', 'fonts')

    def split_long_segment(self, segment):
        """Split a segment into smaller ones with at most 3 words each"""
        words = segment.get('words', [])
        if not words:
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
            new_segments.append(new_segment)

        return new_segments

    def generate_captions(self, audio_path):
        """Generate captions from audio using Whisper with word-level timestamps"""
        try:
            print("Transcribing audio with Whisper...")
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
                
                if duration > self.max_segment_duration or word_count > self.max_words_per_segment:
                    # Split the segment
                    split_segments = self.split_long_segment(segment)
                    processed_segments.extend(split_segments)
                else:
                    processed_segments.append(segment)
            
            print(f"Transcription successful! Created {len(processed_segments)} segments")
            return processed_segments
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None

    def create_caption_clips(self, segments, video_width, video_height, font="Montserrat-Bold", color="white", font_size=48):
        """Create individual caption clips for each segment with custom font and color settings"""
        caption_clips = []
        
        # Get the absolute path to the font file
        font_path = os.path.join(self.fonts_dir, f"{font}.ttf")
        print(f"Using font path: {font_path}")  # Debug print
        print(f"Using font size: {font_size}")  # Debug print
        
        # Check if font file exists
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")  # Debug print
            # Fallback to system font
            font_path = "/System/Library/Fonts/Helvetica.ttc"
            print(f"Falling back to: {font_path}")  # Debug print
        
        # Calculate text positioning based on video dimensions
        # Position text in the bottom third of the video
        text_y_position = video_height * 0.7  # 70% from the top
        max_text_width = video_width * 0.8  # 80% of video width
        padding = 20  # Padding in pixels
        
        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip()
            
            if text:  # Only create clips for non-empty text
                # Create text with custom settings
                caption_clip = (TextClip(text.upper(),
                                    font=font_path,
                                    fontsize=font_size,
                                    color=color,
                                    size=(max_text_width, None),  # Set max width, height auto
                                    method='caption',  # Enable word wrapping
                                    align='center')  # Center align text
                            .set_duration(end_time - start_time)
                            .set_position(('center', text_y_position))
                            .set_start(start_time))
                
                caption_clips.append(caption_clip)
        
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