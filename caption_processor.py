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
                            shadow_blur=12, shadow_opacity=0.9,
                            highlight_color="#FFD700", highlight_enabled=True):
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
        max_text_width = int(video_width * 0.7)
        center_x = video_width // 2
        
        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip()
            words = segment.get('words', [])
            
            if text:  # Only create clips for non-empty text
                # Calculate dimensions for both shadow and main text
                pil_font = ImageFont.truetype(font_path, font_size)
                lines = text.upper().split('\n')
                max_line_width = 0
                total_height = 0
                line_heights = []
                
                # Calculate proper text dimensions including descenders and capital letters
                for line in lines:
                    # Get the full text metrics
                    ascent, descent = pil_font.getmetrics()
                    text_bbox = pil_font.getbbox(line)
                    line_width = text_bbox[2] - text_bbox[0]
                    # Use the full height including both ascent and descent
                    line_height = ascent + descent
                    max_line_width = max(max_line_width, line_width)
                    line_heights.append(line_height)
                    total_height += line_height
                
                # Add padding for line spacing and text height
                line_spacing = int(font_size * 0.2)  # 20% of font size for line spacing
                vertical_padding = int(font_size * 0.3)  # 30% of font size for top and bottom padding
                total_height += (len(lines) - 1) * line_spacing + vertical_padding * 2
                
                # Create base image for the entire text (non-highlighted)
                padding = int(font_size * 0.2)
                base_img = Image.new('RGBA', (max_line_width + padding * 2, 
                                            int(total_height) + padding * 2), 
                                   (0, 0, 0, 0))
                base_draw = ImageDraw.Draw(base_img)
                
                # Convert main color to RGBA
                if color.startswith('#'):
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    main_color_rgba = (r, g, b, 255)
                else:
                    rgb = ImageColor.getrgb(color)
                    main_color_rgba = (*rgb, 255)
                
                # Draw each line of main text with proper vertical positioning
                current_y = padding + vertical_padding
                for i, line in enumerate(lines):
                    text_bbox = pil_font.getbbox(line)
                    line_width = text_bbox[2] - text_bbox[0]
                    x = (base_img.width - line_width) // 2
                    base_draw.text((x, current_y), line, font=pil_font, fill=main_color_rgba)
                    current_y += line_heights[i] + (line_spacing if i < len(lines) - 1 else 0)
                
                # Create base clip
                base_array = np.array(base_img)
                base_clip = (ImageClip(base_array)
                            .set_duration(end_time - start_time)
                           .set_start(start_time)
                           .set_position((center_x - base_img.width//2,
                                        text_y_position - base_img.height//2)))
                
                caption_clips.append(base_clip)
                
                # If highlighting is enabled, create individual word clips
                if highlight_enabled and words:
                    # Convert highlight color to RGBA
                    if highlight_color.startswith('#'):
                        r = int(highlight_color[1:3], 16)
                        g = int(highlight_color[3:5], 16)
                        b = int(highlight_color[5:7], 16)
                        highlight_color_rgba = (r, g, b, 180)  # Semi-transparent background
                    else:
                        rgb = ImageColor.getrgb(highlight_color)
                        highlight_color_rgba = (*rgb, 180)  # Semi-transparent background
                    
                    # Create clips for each word
                    for word in words:
                        word_text = word['word'].upper()
                        word_start = word['start']
                        word_end = word['end']
                        
                        # Create word image
                        word_img = Image.new('RGBA', (max_line_width + padding * 2, 
                                                    int(total_height) + padding * 2), 
                                          (0, 0, 0, 0))
                        word_draw = ImageDraw.Draw(word_img)
                        
                        # Find the word's position in the text
                        current_y = padding + vertical_padding
                        word_found = False
                        
                        for i, line in enumerate(lines):
                            if word_text in line:
                                text_bbox = pil_font.getbbox(line)
                                line_width = text_bbox[2] - text_bbox[0]
                                x = (word_img.width - line_width) // 2
                                
                                # Get word dimensions
                                word_bbox = pil_font.getbbox(word_text)
                                word_width = word_bbox[2] - word_bbox[0]
                                word_height = word_bbox[3] - word_bbox[1]
                                
                                # Calculate word position
                                word_x = x + line.find(word_text) * (line_width / len(line))
                                
                                # Calculate the exact vertical position using the text bounding box
                                word_y = current_y + word_bbox[1]  # Use the top of the text bounding box
                                
                                word_draw.rectangle([
                                    word_x,
                                    word_y,
                                    word_x + word_width,
                                    word_y + word_height
                                ], fill=highlight_color_rgba)
                                
                                word_found = True
                                break
                            
                            current_y += line_heights[i] + (line_spacing if i < len(lines) - 1 else 0)
                        
                        if word_found:
                            # Create word clip
                            word_array = np.array(word_img)
                            word_clip = (ImageClip(word_array)
                                       .set_duration(word_end - word_start)
                                       .set_start(start_time + word_start - segment['start'])
                                       .set_position((center_x - word_img.width//2,
                                                    text_y_position - word_img.height//2)))
                            
                            caption_clips.append(word_clip)
                
                # Add shadow if enabled
                if shadow_type == "blur":
                    # Create shadow image
                    shadow_img = Image.new('RGBA', (max_line_width + padding * 2, 
                                                  int(total_height) + padding * 2), 
                                         (0, 0, 0, 0))
                    shadow_draw = ImageDraw.Draw(shadow_img)
                    
                    # Convert shadow color to RGBA
                    if shadow_color.startswith('#'):
                        r = int(shadow_color[1:3], 16)
                        g = int(shadow_color[3:5], 16)
                        b = int(shadow_color[5:7], 16)
                        shadow_color_rgba = (r, g, b, int(255 * shadow_opacity))
                    else:
                        rgb = ImageColor.getrgb(shadow_color)
                        shadow_color_rgba = (*rgb, int(255 * shadow_opacity))
                    
                    # Draw each line of text with proper vertical positioning
                    current_y = padding + vertical_padding
                    for i, line in enumerate(lines):
                        text_bbox = pil_font.getbbox(line)
                        line_width = text_bbox[2] - text_bbox[0]
                        x = (shadow_img.width - line_width) // 2
                        shadow_draw.text((x, current_y), line, font=pil_font, fill=shadow_color_rgba)
                        current_y += line_heights[i] + (line_spacing if i < len(lines) - 1 else 0)
                    
                    # Apply gaussian blur
                    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
                    
                    # Create shadow clip
                    shadow_array = np.array(shadow_img)
                    shadow_clip = (ImageClip(shadow_array)
                                 .set_duration(end_time - start_time)
                                 .set_start(start_time)
                                 .set_position((center_x - shadow_img.width//2,
                                              text_y_position - shadow_img.height//2)))
                    
                    caption_clips.append(shadow_clip)
                elif shadow_type == "offset":
                    # Create offset shadow
                    offset_img = Image.new('RGBA', (max_line_width + padding * 2, 
                                                  int(total_height) + padding * 2), 
                                         (0, 0, 0, 0))
                    offset_draw = ImageDraw.Draw(offset_img)
                    
                    # Convert shadow color to RGBA
                    if shadow_color.startswith('#'):
                        r = int(shadow_color[1:3], 16)
                        g = int(shadow_color[3:5], 16)
                        b = int(shadow_color[5:7], 16)
                        shadow_color_rgba = (r, g, b, int(255 * shadow_opacity))
                    else:
                        rgb = ImageColor.getrgb(shadow_color)
                        shadow_color_rgba = (*rgb, int(255 * shadow_opacity))
                    
                    # Draw each line of text with proper vertical positioning and offset
                    current_y = padding + vertical_padding
                    for i, line in enumerate(lines):
                        text_bbox = pil_font.getbbox(line)
                        line_width = text_bbox[2] - text_bbox[0]
                        x = (offset_img.width - line_width) // 2
                        offset_draw.text((x + 4, current_y + 4), line, font=pil_font, fill=shadow_color_rgba)
                        current_y += line_heights[i] + (line_spacing if i < len(lines) - 1 else 0)
                    
                    # Create offset shadow clip
                    offset_array = np.array(offset_img)
                    offset_clip = (ImageClip(offset_array)
                                 .set_duration(end_time - start_time)
                                 .set_start(start_time)
                                 .set_position((center_x - offset_img.width//2,
                                              text_y_position - offset_img.height//2)))
                    
                    caption_clips.append(offset_clip)
        
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
