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

# Initialize logger
logger = setup_logging(__name__, 'broll_analyzer.log')

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
                        
                    logger.debug(f"OpenAI suggested keywords: {keywords}")
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

    def get_broll_suggestions(self, segments: List[Dict], video_duration: float = None, video_width: int = None, video_height: int = None) -> List[Dict]:
        """Generate b-roll suggestions for the entire video transcript"""
        logger.info("Starting b-roll suggestions generation...")
        
        # Determine video orientation
        is_vertical = video_height and video_width and video_height > video_width
        orientation = "vertical" if is_vertical else "horizontal"
        logger.info(f"Video orientation: {orientation} ({video_width}x{video_height})")
        
        # Combine all segments into a single transcript with timestamps
        transcript = "\n".join([
            f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}"
            for segment in segments
        ])
        logger.info(f"Combined transcript length: {len(transcript)} characters")
        
        # Get keywords and timestamps from OpenAI
        suggestions = self.get_keywords_from_openai(transcript, video_duration)
        if not suggestions:
            logger.warning("No b-roll suggestions generated from transcript")
            return []
            
        logger.info(f"Generated {len(suggestions)} b-roll suggestions")
        
        # Get b-roll footage for each suggestion
        final_suggestions = []
        for suggestion in suggestions:
            try:
                keyword = suggestion['keyword']
                timestamp = suggestion['timestamp']
                confidence = suggestion['confidence']
                explanation = suggestion['explanation']
                
                # Skip if timestamp is beyond video duration
                if video_duration and timestamp >= video_duration:
                    logger.warning(f"Skipping suggestion at {timestamp:.2f}s as it's beyond video duration ({video_duration:.2f}s)")
                    continue
                
                logger.info(f"Searching for b-roll at {timestamp:.2f}s with keyword: {keyword}")
                broll_results = self.search_broll(
                    keyword, 
                    5.0,  # Default duration of 5 seconds
                    orientation=orientation,
                    target_width=video_width,
                    target_height=video_height
                )
                
                if broll_results:
                    final_suggestion = {
                        'timestamp': timestamp,
                        'duration': 3.0,  # Fixed duration of 3 seconds
                        'keyword': keyword,
                        'confidence': confidence,
                        'context': explanation,
                        'broll_options': broll_results[:3]  # Get top 3 b-roll options
                    }
                    final_suggestions.append(final_suggestion)
                    logger.info(f"Added b-roll suggestion at {timestamp:.2f}s with keyword: {keyword}")
                    logger.debug(f"Suggestion details: {final_suggestion}")
                else:
                    logger.warning(f"No b-roll results found for keyword: {keyword} at {timestamp:.2f}s")
                    
            except Exception as e:
                logger.error(f"Error processing suggestion for keyword '{keyword}' at {timestamp:.2f}s: {str(e)}")
                logger.error(f"Error details: {traceback.format_exc()}")
                continue
        
        logger.info(f"Successfully processed {len(final_suggestions)} b-roll suggestions")
        logger.info(f"Target aspect ratio: {video_width/video_height if video_width and video_height else 'N/A'}")
        return final_suggestions

    def search_broll(self, keyword: str, duration: float, orientation: str = "horizontal", target_width: int = None, target_height: int = None) -> List[Dict]:
        """Search for b-roll footage using Pexels API"""
        try:
            logger.info(f"Searching for b-roll with keyword: {keyword} (orientation: {orientation})")
            
            # Search for videos
            logger.debug(f"Making Pexels API call with keyword: {keyword}")
            try:
                headers = {"Authorization": self.pexels_api_key}
                response = requests.get(
                    f"{self.pexels_base_url}/search",
                    params={
                        "query": keyword,
                        "per_page": 15,  # Increased to get more options to filter
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
            
            logger.info(f"Found {len(videos)} videos for keyword: {keyword}")
            
            # Process and return video results
            results = []
            for i, video in enumerate(videos):
                try:
                    # Get the best quality video file
                    video_files = video.get('video_files', [])
                    if not video_files:
                        continue
                        
                    # Sort by quality and get the best one
                    video_file = sorted(video_files, key=lambda x: x.get('quality', 0), reverse=True)[0]
                    
                    # Check if the video dimensions match our target orientation
                    width = video_file.get('width', 0)
                    height = video_file.get('height', 0)
                    
                    # Skip if dimensions don't match orientation
                    if orientation == "vertical" and width > height:
                        continue
                    if orientation == "horizontal" and height > width:
                        continue
                    
                    # If we have target dimensions, prefer videos closer to our target size
                    if target_width and target_height:
                        # Calculate aspect ratio difference
                        target_ratio = target_width / target_height
                        video_ratio = width / height
                        ratio_diff = abs(target_ratio - video_ratio)
                        
                        # Skip if aspect ratio is too different
                        if ratio_diff > 0.2:  # Allow 20% difference in aspect ratio
                            continue
                    
                    result = {
                        'url': video_file.get('link'),
                        'duration': video_file.get('duration'),
                        'width': width,
                        'height': height,
                        'quality': video_file.get('quality'),
                        'keyword': keyword
                    }
                    results.append(result)
                    logger.debug(f"Processed video {i+1}: {result}")
                except Exception as e:
                    logger.error(f"Error processing video {i+1}: {str(e)}")
                    logger.error(f"Video processing error details: {traceback.format_exc()}")
                    continue
            
            # Sort results by how well they match our target dimensions
            if target_width and target_height:
                results.sort(key=lambda x: abs((x['width']/x['height']) - (target_width/target_height)))
            
            logger.info(f"Successfully processed {len(results)} videos for keyword: {keyword}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for b-roll: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            return []

    def analyze_transcript(self, segments: List[Dict]) -> Dict:
        """Analyze entire transcript and return b-roll suggestions"""
        logger.info("Starting transcript analysis...")
        if not segments:
            logger.error("No segments provided for analysis")
            return None

        try:
            logger.info(f"Processing {len(segments)} segments")
            broll_suggestions = self.get_broll_suggestions(segments)
            
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