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
            self.openai_client = OpenAI()
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

        # Minimum time between b-roll suggestions (in seconds)
        self.min_time_between_suggestions = 5.0

    def get_keywords_from_openai(self, text: str) -> List[Dict[str, float]]:
        """Use OpenAI to analyze text and suggest keywords for b-roll footage"""
        try:
            prompt = f"""Analyze this text and suggest 1-3 specific keywords for finding relevant b-roll footage on Pexels. 
            The keywords should be specific and visual, good for finding stock footage.
            Format the response as a JSON array of objects, each with 'keyword' and 'confidence' (0-1) fields.
            Only respond with the JSON array, no other text.
            
            Text to analyze: "{text}"
            """
            
            logger.debug(f"Sending text to OpenAI: {text}")
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a video editor's assistant, expert at finding relevant b-roll footage. You must respond with ONLY a JSON array of objects with 'keyword' and 'confidence' fields."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=150
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

    def get_broll_suggestions(self, segments: List[Dict]) -> List[Dict]:
        """Generate b-roll suggestions throughout the video"""
        logger.info("Starting b-roll suggestions generation...")
        suggestions = []
        last_suggestion_time = -self.min_time_between_suggestions

        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            # Skip if we're too close to the last suggestion
            if start_time - last_suggestion_time < self.min_time_between_suggestions:
                logger.debug(f"Skipping segment at {start_time:.2f}s - too close to last suggestion")
                continue
            
            # Get keywords from OpenAI
            keywords = self.get_keywords_from_openai(text)
            if not keywords:
                logger.debug(f"No keywords found for segment at {start_time:.2f}s")
                continue
                
            logger.info(f"Found {len(keywords)} keywords for segment at {start_time:.2f}s")
            
            # Try each keyword in order of confidence
            for keyword_info in sorted(keywords, key=lambda x: x['confidence'], reverse=True):
                keyword = keyword_info['keyword']
                confidence = keyword_info['confidence']
                
                try:
                    logger.info(f"Searching for b-roll at {start_time:.2f}s with keyword: {keyword}")
                    broll_results = self.search_broll(keyword, end_time - start_time)
                    
                    if broll_results:
                        suggestion = {
                            'timestamp': start_time,
                            'duration': end_time - start_time,
                            'keyword': keyword,
                            'confidence': confidence,
                            'context': text[:100] + "...",
                            'broll_options': broll_results[:3]  # Get top 3 b-roll options
                        }
                        suggestions.append(suggestion)
                        last_suggestion_time = start_time
                        logger.info(f"Added b-roll suggestion at {start_time:.2f}s with keyword: {keyword}")
                        logger.debug(f"Suggestion details: {suggestion}")
                        break  # Stop trying keywords once we find good b-roll
                    else:
                        logger.warning(f"No b-roll results found for keyword: {keyword} at {start_time:.2f}s")
                except Exception as e:
                    logger.error(f"Error getting b-roll for keyword '{keyword}' at {start_time:.2f}s: {str(e)}")
                    logger.error(f"Error details: {traceback.format_exc()}")
                    continue
            
        logger.info(f"Generated {len(suggestions)} b-roll suggestions")
        return suggestions

    def search_broll(self, keyword: str, duration: float) -> List[Dict]:
        """Search for b-roll footage using Pexels API"""
        try:
            logger.info(f"Searching for b-roll with keyword: {keyword}")
            
            # Search for videos
            logger.debug(f"Making Pexels API call with keyword: {keyword}")
            try:
                headers = {"Authorization": self.pexels_api_key}
                response = requests.get(
                    f"{self.pexels_base_url}/search",
                    params={
                        "query": keyword,
                        "per_page": 5
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
                    
                    result = {
                        'url': video_file.get('link'),
                        'duration': video_file.get('duration'),
                        'width': video_file.get('width'),
                        'height': video_file.get('height'),
                        'quality': video_file.get('quality'),
                        'keyword': keyword
                    }
                    results.append(result)
                    logger.debug(f"Processed video {i+1}: {result}")
                except Exception as e:
                    logger.error(f"Error processing video {i+1}: {str(e)}")
                    logger.error(f"Video processing error details: {traceback.format_exc()}")
                    continue
            
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