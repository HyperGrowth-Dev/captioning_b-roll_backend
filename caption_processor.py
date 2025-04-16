import whisper
from moviepy.editor import TextClip, VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
import logging
import os
import numpy as np

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

    def create_caption_clips(self, segments, video_width, video_height, font="Montserrat-Bold", 
                            color="white", font_size=48, position=0.7, 
                            shadow_type="none", shadow_color="black", 
                            shadow_blur=8, shadow_opacity=0.9):
        """Create individual caption clips for each segment with custom font and color settings"""
        caption_clips = []
        
        # Get the absolute path to the font file
        font_path = os.path.join(self.fonts_dir, f"{font}.ttf")
        
        # Check if font file exists
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            font_path = "/System/Library/Fonts/Helvetica.ttc"
        
        # Calculate text positioning and sizing
        text_y_position = video_height * position
        max_text_width = int(video_width * 0.7)  # 70% of video width
        center_x = video_width // 2
        
        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip()
            
            if text:  # Only create clips for non-empty text
                if shadow_type == "blur":
                    # Create multiple blur layers with different intensities
                    blur_layers = [
                        {"radius": shadow_blur * 2, "opacity": shadow_opacity * 0.4},  # Outer blur
                        {"radius": shadow_blur * 1.5, "opacity": shadow_opacity * 0.6},  # Middle blur
                        {"radius": shadow_blur, "opacity": shadow_opacity}  # Inner blur
                    ]
                    
                    for layer in blur_layers:
                        # Create a PIL Image for the shadow
                        # Make it larger to accommodate the blur
                        padding = int(layer["radius"] * 3)  # Increased padding for larger blur
                        img = Image.new('RGBA', (max_text_width + padding * 2, 
                                               font_size * 2 + padding * 2), 
                                      (0, 0, 0, 0))
                        draw = ImageDraw.Draw(img)
                        pil_font = ImageFont.truetype(font_path, font_size)
                        
                        # Convert shadow color to RGBA
                        if shadow_color.startswith('#'):
                            r = int(shadow_color[1:3], 16)
                            g = int(shadow_color[3:5], 16)
                            b = int(shadow_color[5:7], 16)
                            shadow_color_rgba = (r, g, b, int(255 * layer["opacity"]))
                        else:
                            rgb = ImageColor.getrgb(shadow_color)
                            shadow_color_rgba = (*rgb, int(255 * layer["opacity"]))
                        
                        # Draw the shadow text
                        text_bbox = draw.textbbox((0, 0), text.upper(), font=pil_font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        x = (img.width - text_width) // 2
                        y = (img.height - text_height) // 2
                        draw.text((x, y), text.upper(), font=pil_font, fill=shadow_color_rgba)
                        
                        # Apply gaussian blur with larger radius
                        shadow_img = img.filter(ImageFilter.GaussianBlur(radius=layer["radius"]))
                        
                        # Convert to numpy array for MoviePy
                        shadow_array = np.array(shadow_img)
                        
                        # Create shadow clip
                        shadow_clip = (ImageClip(shadow_array)
                                     .set_duration(end_time - start_time)
                                     .set_start(start_time)
                                     .set_position((center_x - img.width//2,
                                                  text_y_position - img.height//2)))
                        
                        caption_clips.append(shadow_clip)
                
                # Create main text clip
                main_clip = (TextClip(text.upper(),
                                    font=font_path,
                                    fontsize=font_size,
                                    color=color,
                                    size=(max_text_width, None),
                                    method='caption',
                                    align='center')
                            .set_duration(end_time - start_time)
                            .set_start(start_time))
                
                # Position main clip
                main_clip = main_clip.set_position(
                    lambda t: (center_x - main_clip.w//2, text_y_position - main_clip.h//2)
                )
                
                caption_clips.append(main_clip)
        
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
