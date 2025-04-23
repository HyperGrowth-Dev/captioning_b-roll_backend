from typing import List, Dict, Any
from .remotion_service import RemotionService

class VideoProcessor:
    def __init__(self):
        self.remotion_service = RemotionService()

    async def process_video(
        self,
        video_path: str,
        captions: List[Dict[str, Any]],
        settings: Dict[str, Any]
    ) -> str:
        """
        Process a video with captions using Remotion
        
        Args:
            video_path: Path to the input video
            captions: List of caption objects with text and timing
            settings: Video processing settings (font, color, etc.)
            
        Returns:
            URL to the processed video
        """
        try:
            # Convert captions to Remotion format
            remotion_captions = [
                {
                    "text": caption["text"],
                    "startFrame": int(caption["start_time"] * 30),  # Assuming 30fps
                    "endFrame": int(caption["end_time"] * 30)
                }
                for caption in captions
            ]
            
            # Process video using Remotion
            output_url = await self.remotion_service.process_video(
                video_path=video_path,
                captions=remotion_captions,
                settings=settings
            )
            
            return output_url
            
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            raise 