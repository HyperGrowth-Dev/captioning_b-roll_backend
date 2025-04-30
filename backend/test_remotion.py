import asyncio
import os
import sys
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.remotion_service import RemotionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_remotion_lambda():
    try:
        # Initialize the Remotion service
        remotion_service = RemotionService()
        
        # Test settings
        test_settings = {
            'font': 'Montserrat-Bold',
            'color': 'white',
            'fontSize': 32,
            'fps': 30,
            'position': 0.7,
            'maxWidth': 1536,
            'highlightColor': '#FFD700',
            'durationInFrames': 300
        }
        
        # Get the absolute path to the test video
        test_video_path = os.path.abspath(os.path.join('input', 'fitness_test_vid.mov'))
        
        logger.info("Starting Remotion Lambda test...")
        logger.info(f"Testing with video: {test_video_path}")
        
        # Process the video
        output_url = await remotion_service.process_video(test_video_path, test_settings)
        
        logger.info(f"Test completed successfully!")
        logger.info(f"Output URL: {output_url}")
        
        return output_url
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_remotion_lambda()) 