import os
from typing import List, Dict, Tuple
import logging
from collections import Counter
import re
import requests
import json
import traceback
from openai import OpenAI
import time
from utils import setup_logging, ensure_directory
import base64
from io import BytesIO
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)

class BrollAnalyzer:
    def __init__(self, pexels_api_key: str):
        logger.info("Initializing BrollAnalyzer")
        
        # Validate API key format
        if not pexels_api_key or len(pexels_api_key) < 32:
            logger.error(f"Invalid Pexels API key format: {pexels_api_key[:5]}...")
            raise ValueError("Invalid Pexels API key format - key should be at least 32 characters")
            
        self.pexels_api_key = pexels_api_key
        self.pexels_base_url = "https://api.pexels.com/videos"
        
        # Test the API with a simple search
        logger.info("Testing Pexels API with a simple search...")
        try:
            headers = {"Authorization": self.pexels_api_key}
            response = requests.get(f"{self.pexels_base_url}/search?query=nature&per_page=1", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('videos'):
                    logger.info("✓ Pexels API initialized and tested successfully")
                    logger.debug(f"Test search returned {len(data['videos'])} videos")
                else:
                    raise ValueError("Pexels API test failed - no results returned")
            else:
                raise ValueError(f"Pexels API test failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Pexels API: {str(e)}")
            logger.error(f"API initialization error details: {traceback.format_exc()}")
            raise
        
        # Initialize OpenAI client
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is required")
        try:
            self.openai_client = OpenAI(api_key=openai_key)
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

        # Minimum time between b-roll suggestions (in seconds)
        self.min_time_between_suggestions = 5.0

    def analyze_multiple_images(self, image_data_list: List[Dict], keyword: str) -> Dict:
        """Analyze multiple images in a single OpenAI call and select the best one"""
        try:
            logger.debug(f"Analyzing {len(image_data_list)} images for keyword: {keyword}")
            
            if not image_data_list:
                logger.warning("No images provided for analysis")
                return {'best_index': -1, 'analysis': 'No images provided'}
            
            # Prepare content for OpenAI (text + all images)
            content = [
                {
                    "type": "text", 
                    "text": f"""Analyze these {len(image_data_list)} images and determine which one best matches the keyword: "{keyword}"

Consider for each image:
1. Overall relevance to the keyword 
2. Subject matter and context
3. Visual content and composition

Compare all images and select the ONE that best represents the keyword. Consider:
- How clearly the image shows the concept
- How well it would work as b-roll footage
- Emotional/contextual fit

Respond in JSON format with:
{{
    "best_image_index": int (0-based index of the best image),
    "comparison_analysis": "string (brief explanation of why this image is the best choice)"
}}

The best_image_index should be the 0-based index of the image that best matches the keyword."""
                }
            ]
            
            # Add all images to the content
            for i, image_data in enumerate(image_data_list):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data['base64']}"
                    }
                })
            
            # Make the API call
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=800,
                    temperature=0.1
                )
                
                content_response = response.choices[0].message.content.strip()
                logger.info(f"OpenAI multi-image analysis response: {content_response}")
                
                # Parse JSON response
                try:
                    # Extract JSON from response
                    start = content_response.find('{')
                    end = content_response.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = content_response[start:end]
                        result = json.loads(json_str)
                    else:
                        result = json.loads(content_response)
                    
                    logger.debug(f"Multi-image analysis result: {result}")
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse OpenAI multi-image response: {str(e)}")
                    logger.error(f"Raw response: {content_response}")
                    # Fallback: return first image as best
                    return {
                        'best_image_index': 0,
                        'comparison_analysis': 'Failed to parse analysis, using first image',
                        'overall_confidence': 0.5,
                        'individual_scores': []
                    }
                    
            except Exception as e:
                logger.error(f"OpenAI multi-image API call failed: {str(e)}")
                return {
                    'best_image_index': 0,
                    'comparison_analysis': 'API call failed, using first image',
                    'overall_confidence': 0.5,
                    'individual_scores': []
                }
                
        except Exception as e:
            logger.error(f"Error in analyze_multiple_images: {str(e)}")
            return {
                'best_image_index': 0,
                'comparison_analysis': 'Analysis failed, using first image',
                'overall_confidence': 0.5,
                'individual_scores': []
            }

    def download_and_process_image(self, image_url: str) -> Dict:
        """Download and process a single image for analysis"""
        try:
            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content
            
            # Convert image to base64
            image = Image.open(BytesIO(image_data))
            # Resize if too large (OpenAI has size limits)
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                'url': image_url,
                'base64': image_base64,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to download/process image from {image_url}: {str(e)}")
            return {
                'url': image_url,
                'base64': None,
                'success': False,
                'error': str(e)
            }

    def get_keywords_from_openai(self, text: str, video_duration: float = None) -> List[Dict[str, float]]:
        """Use OpenAI to analyze text and suggest keywords for b-roll footage"""
        try:
            duration_constraint = f"\nThe video is {video_duration:.2f} seconds long. Only suggest timestamps between 0 and {video_duration:.2f} seconds." if video_duration else ""
            
            prompt = f"""Analyze this transcript and suggest specific keywords for finding relevant b-roll footage on Pexels.
            The transcript includes timestamps in the format [start_time - end_time] before each segment.
            Consider the overall context and themes of the video.
            For each suggestion, provide:
            1. A specific, visual keyword good for finding stock footage
            2. The timestamp where this b-roll would be most relevant (use the start time of the relevant segment)
            3. A confidence score (0-1) based on how well the keyword matches the context
            4. A brief explanation of why this b-roll would work well at this point{duration_constraint}
            
            Format the response as a JSON array of objects, each with:
            - 'keyword': string
            - 'timestamp': number (in seconds)
            - 'confidence': number (0-1)
            - 'explanation': string
            
            Only respond with the JSON array, no other text.
            
            Transcript to analyze:
            {text}
            """
            
            logger.debug(f"Sending transcript to OpenAI: {text}")
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a video editor's assistant, expert at finding relevant b-roll footage. You must respond with ONLY a JSON array of objects with 'keyword', 'timestamp', 'confidence', and 'explanation' fields."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content.strip()
                logger.debug(f"OpenAI raw response: {content}")
                
                # Try to extract JSON if the response contains extra text
                try:
                    # Find the first '[' and last ']' to extract the JSON array
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                    else:
                        json_str = content
                        
                    result = json.loads(json_str)
                    if isinstance(result, dict) and 'keywords' in result:
                        keywords = result['keywords']
                    else:
                        keywords = result  # Assume the model returned the array directly
                    logger.info(f"OpenAI suggested keywords: {keywords}")
                    return keywords
                except json.JSONDecodeError as json_error:
                    logger.error(f"Failed to parse OpenAI response as JSON: {str(json_error)}")
                    logger.error(f"Raw response was: {content}")
                    return []
                
            except Exception as api_error:
                logger.error(f"OpenAI API call failed: {str(api_error)}")
                logger.error(f"API error details: {traceback.format_exc()}")
                return []
            
        except Exception as e:
            logger.error(f"Error getting keywords from OpenAI: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            return []

    def get_broll_suggestions(self, segments: List[Dict], video_duration: float = None, video_width: int = None, video_height: int = None, fps: float = 30.0) -> List[Dict]:
        """Generate b-roll suggestions for the entire video transcript"""
        logger.info("Starting b-roll suggestions generation...")
        logger.info(f"Input segments count: {len(segments)}")
        logger.info(f"Video duration: {video_duration}, dimensions: {video_width}x{video_height}, FPS: {fps}")
        
        # Determine video orientation
        is_vertical = video_height and video_width and video_height > video_width
        orientation = "portrait" if is_vertical else "landscape"
        logger.info(f"Video orientation: {orientation} ({video_width}x{video_height})")
        
        # Combine all segments into a single transcript with timestamps
        transcript = "\n".join([
            f"[{segment['startFrame']/fps:.2f}s - {segment['endFrame']/fps:.2f}s] {segment['text']}"
            for segment in segments
        ])
        logger.info(f"Combined transcript length: {len(transcript)} characters")
        
        # Get keywords and timestamps from OpenAI
        suggestions = self.get_keywords_from_openai(transcript, video_duration)
        if not suggestions:
            logger.warning("No b-roll suggestions generated from transcript")
            return []
            
        logger.info(f"Generated {len(suggestions)} b-roll suggestions")
        logger.debug(f"Raw suggestions: {json.dumps(suggestions, indent=2)}")
        
        # Get b-roll footage for each suggestion
        final_suggestions = []
        for suggestion in suggestions:
            try:
                keyword = suggestion['keyword']
                timestamp = suggestion['timestamp']
                confidence = suggestion['confidence']
                explanation = suggestion['explanation']
                
                logger.info(f"Processing suggestion: keyword={keyword}, timestamp={timestamp}, confidence={confidence}")
                
                # Skip if timestamp is beyond video duration
                if video_duration and timestamp >= video_duration:
                    logger.warning(f"Skipping suggestion at {timestamp:.2f}s as it's beyond video duration ({video_duration:.2f}s)")
                    continue
                
                logger.info(f"Searching for b-roll at {timestamp:.2f}s with keyword: {keyword}")
                broll_results = self.search_broll(
                    keyword, 
                    5.0,
                    orientation=orientation,
                    target_width=video_width,
                    target_height=video_height,
                    target_fps=fps
                )
                
                if broll_results:
                    # Get the best video from the analyzed results
                    best_video = self.get_best_broll_video(broll_results, keyword)
                    
                    final_suggestion = {
                        'timestamp': timestamp,
                        'duration': 3.0,
                        'keyword': keyword,
                        'confidence': confidence,
                        'context': explanation,
                        'best_broll': best_video,
                        'broll_options': broll_results[:3]  # Keep top 3 for reference
                    }
                    final_suggestions.append(final_suggestion)
                    logger.info(f"Added b-roll suggestion at {timestamp:.2f}s with keyword: {keyword}")
                    logger.debug(f"Suggestion details: {json.dumps(final_suggestion, indent=2)}")
                else:
                    logger.warning(f"No b-roll results found for keyword: {keyword} at {timestamp:.2f}s")
                    
            except Exception as e:
                logger.error(f"Error processing suggestion for keyword '{keyword}' at {timestamp:.2f}s: {str(e)}")
                logger.error(f"Error details: {traceback.format_exc()}")
                continue
        
        logger.info(f"Successfully processed {len(final_suggestions)} b-roll suggestions")
        return final_suggestions

    def search_broll(self, keyword: str, duration: float, orientation: str = "horizontal", target_width: int = None, target_height: int = None, target_fps: float = None) -> List[Dict]:
        """Search for b-roll footage using Pexels API"""
        try:
            logger.info(f"Searching for b-roll with keyword: {keyword} (orientation: {orientation})")
            
            # Round target FPS to nearest whole number
            rounded_fps = round(target_fps) if target_fps else None
            if rounded_fps:
                logger.info(f"Target FPS: {target_fps} (rounded to {rounded_fps})")
            
            # Search for videos
            logger.debug(f"Making Pexels API call with keyword: {keyword}")
            try:
                headers = {"Authorization": self.pexels_api_key}
                response = requests.get(
                    f"{self.pexels_base_url}/search",
                    params={
                        "query": keyword,
                        "per_page": 10,  # Increased to get more options to filter
                        "orientation": orientation
                    },
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Pexels API call failed with status code: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return []
                
                data = response.json()
                videos = data.get('videos', [])
                logger.debug(f"API call successful, got {len(videos)} videos")
                
            except Exception as api_error:
                logger.error(f"Pexels API call failed: {str(api_error)}")
                logger.error(f"API error details: {traceback.format_exc()}")
                return []
            
            if not videos:
                logger.warning(f"No videos found for keyword: {keyword}")
                return []
            
            # Filter and process videos with multi-image analysis
            filtered_videos = []
            videos_with_images = []
            
            # First pass: collect all videos and their images
            for video in videos:
                try:
                    # Get the highest quality video file
                    video_files = video.get('video_files', [])
                    if not video_files:
                        continue
                    
                    # Sort by quality (prefer HD)
                    video_files.sort(key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
                    video_file = video_files[0]
                    
                    # Extract FPS from URL if available
                    fps_match = re.search(r'(\d+)fps', video_file.get('link', ''))
                    video_fps = int(fps_match.group(1)) if fps_match else None
                    
                    # Skip if video is too short
                    if video.get('duration', 0) < duration:
                        logger.debug(f"Skipping video with duration {video.get('duration')}s (too short)")
                        continue
                    
                    # Skip if orientation doesn't match
                    if orientation == "portrait" and video.get('width', 0) >= video.get('height', 0):
                        logger.debug("Skipping landscape video (portrait requested)")
                        continue
                    elif orientation == "landscape" and video.get('width', 0) < video.get('height', 0):
                        logger.debug("Skipping portrait video (landscape requested)")
                        continue
                    
                    # Get video thumbnail for analysis
                    image_url = video.get('image', '')
                    if not image_url:
                        # Try to get image from video_files
                        for vf in video_files:
                            if vf.get('file_type', '').startswith('image'):
                                image_url = vf.get('link', '')
                                break
                    
                    # Create video object
                    video_obj = {
                        'id': video.get('id'),
                        'url': video_file.get('link'),
                        'width': video_file.get('width'),
                        'height': video_file.get('height'),
                        'duration': video.get('duration'),
                        'fps': video_fps,
                        'image_url': image_url,
                        'video_index': len(videos_with_images)  # Track original position
                    }
                    
                    videos_with_images.append(video_obj)
                    
                except Exception as e:
                    logger.error(f"Error processing video: {str(e)}")
                    continue
            
            if not videos_with_images:
                logger.warning("No videos passed initial filtering")
                return []
            
            # Download and process all images
            logger.info(f"Downloading and processing {len(videos_with_images)} images for analysis")
            image_data_list = []
            valid_video_indices = []
            
            for i, video in enumerate(videos_with_images):
                if video['image_url']:
                    image_data = self.download_and_process_image(video['image_url'])
                    if image_data['success']:
                        image_data_list.append(image_data)
                        valid_video_indices.append(i)
                        logger.debug(f"Successfully processed image {i+1}/{len(videos_with_images)}")
                    else:
                        logger.warning(f"Failed to process image for video {video['id']}: {image_data.get('error', 'Unknown error')}")
                else:
                    logger.warning(f"No image URL for video {video['id']}")
            
            # Analyze all images together if we have any
            if image_data_list:
                logger.info(f"Analyzing {len(image_data_list)} images with OpenAI Vision")
                analysis_result = self.analyze_multiple_images(image_data_list, keyword)
                
                # Process the analysis results
                best_index = analysis_result.get('best_image_index', 0)
                comparison_analysis = analysis_result.get('comparison_analysis', 'No analysis available')
                overall_confidence = analysis_result.get('overall_confidence', 0.5)
                individual_scores = analysis_result.get('individual_scores', [])
                
                logger.info(f"Analysis complete. Best image index: {best_index}")
                logger.info(f"Overall confidence: {overall_confidence:.3f}")
                logger.info(f"Comparison analysis: {comparison_analysis}")
                
                # Create a mapping from analysis index to video index
                analysis_to_video_map = {}
                for i, video_idx in enumerate(valid_video_indices):
                    analysis_to_video_map[i] = video_idx
                
                # Find the best video based on analysis
                if best_index in analysis_to_video_map:
                    best_video_index = analysis_to_video_map[best_index]
                    best_video = videos_with_images[best_video_index]
                    
                    # Add analysis data to the best video
                    best_video.update({
                        'relevance_score': 1.0,  # Best video gets highest score
                        'confidence': overall_confidence,
                        'analysis': comparison_analysis,
                        'is_best_match': True
                    })
                    
                    # Add analysis data to other videos
                    for i, video_idx in enumerate(valid_video_indices):
                        if i != best_index:
                            video = videos_with_images[video_idx]
                            # Find individual score if available
                            individual_score = next((score for score in individual_scores if score.get('index') == i), None)
                            
                            video.update({
                                'relevance_score': individual_score.get('relevance_score', 0.5) if individual_score else 0.5,
                                'confidence': overall_confidence,
                                'analysis': individual_score.get('brief_analysis', 'Analyzed but not selected as best') if individual_score else 'Analyzed but not selected as best',
                                'is_best_match': False
                            })
                    
                    # Add default analysis for videos without images
                    for i, video in enumerate(videos_with_images):
                        if i not in valid_video_indices:
                            video.update({
                                'relevance_score': 0.3,
                                'confidence': 0.0,
                                'analysis': 'No image available for analysis',
                                'is_best_match': False
                            })
                    
                    # Sort videos by relevance score (best video first)
                    videos_with_images.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                    
                    # Filter out videos with very low relevance scores
                    min_relevance_threshold = 0.3
                    filtered_videos = [
                        video for video in videos_with_images 
                        if video.get('relevance_score', 0) >= min_relevance_threshold
                    ]
                    
                    logger.info(f"Found {len(filtered_videos)} videos with relevance score >= {min_relevance_threshold}")
                    logger.info(f"Best video ID: {best_video['id']} (Score: {best_video['relevance_score']:.3f})")
                    
                else:
                    logger.error(f"Best image index {best_index} not found in valid video indices")
                    # Fallback: return all videos with default scores
                    for video in videos_with_images:
                        video.update({
                            'relevance_score': 0.5,
                            'confidence': 0.0,
                            'analysis': 'Analysis failed, using default score',
                            'is_best_match': False
                        })
                    filtered_videos = videos_with_images
                    
            else:
                logger.warning("No images could be processed for analysis")
                # Fallback: return all videos with default scores
                for video in videos_with_images:
                    video.update({
                        'relevance_score': 0.5,
                        'confidence': 0.0,
                        'analysis': 'No image available for analysis',
                        'is_best_match': False
                    })
                filtered_videos = videos_with_images
            
            return filtered_videos
            
        except Exception as e:
            logger.error(f"Error in search_broll: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            return []

    def get_best_broll_video(self, videos: List[Dict], keyword: str) -> Dict:
        """Select the best b-roll video from a list of analyzed videos"""
        if not videos:
            return None
        
        # Find the video marked as best match, or get the highest scored one
        best_video = None
        
        # First, try to find the video marked as best match
        for video in videos:
            if video.get('is_best_match', False):
                best_video = video
                break
        
        # If no best match found, get the highest scored video
        if not best_video:
            sorted_videos = sorted(videos, key=lambda x: x.get('relevance_score', 0), reverse=True)
            best_video = sorted_videos[0]
        
        logger.info(f"Selected best video for keyword '{keyword}':")
        logger.info(f"  - Video ID: {best_video.get('id')}")
        logger.info(f"  - Relevance Score: {best_video.get('relevance_score', 0):.3f}")
        logger.info(f"  - Confidence: {best_video.get('confidence', 0):.3f}")
        logger.info(f"  - Is Best Match: {best_video.get('is_best_match', False)}")
        logger.info(f"  - Analysis: {best_video.get('analysis', 'No analysis')}")
        
        return best_video

    def analyze_transcript(self, segments: List[Dict], fps: float = 30.0) -> Dict:
        """Analyze entire transcript and return b-roll suggestions"""
        logger.info("Starting transcript analysis...")
        if not segments:
            logger.error("No segments provided for analysis")
            return None

        try:
            logger.info(f"Processing {len(segments)} segments")
            broll_suggestions = self.get_broll_suggestions(segments, fps=fps)
            
            analysis = {
                'broll_suggestions': broll_suggestions
            }
            
            logger.info(f"Analysis complete. Found {len(broll_suggestions)} suggestions")
            logger.debug(f"Analysis content: {analysis}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_transcript: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            return None

    def save_analysis(self, analysis: Dict, output_dir: str = 'output'):
        """Save the analysis results to a JSON file"""
        try:
            if not analysis:
                logger.error("No analysis data to save")
                return None

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'broll_analysis.json')
            
            # Convert timestamps to a more readable format
            formatted_analysis = {
                'broll_suggestions': [
                    {
                        'timestamp': f"{suggestion['timestamp']:.2f}s",
                        'duration': f"{suggestion['duration']:.2f}s",
                        'keyword': suggestion['keyword'],
                        'confidence': suggestion['confidence'],
                        'context': suggestion['context'],
                        'best_broll': suggestion.get('best_broll', {}),
                        'broll_options': suggestion['broll_options']
                    }
                    for suggestion in analysis['broll_suggestions']
                ]
            }
            
            logger.info(f"Saving analysis to: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_analysis, f, indent=2)
            
            logger.info(f"Analysis saved successfully to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
            return None 