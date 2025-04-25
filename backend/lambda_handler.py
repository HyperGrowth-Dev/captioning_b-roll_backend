import json
import os
import tempfile
import boto3
from typing import Dict, Any
from remotion_local_service import RemotionLocalService
from services.s3_service import S3Service

s3 = boto3.client('s3')
s3_service = S3Service()
remotion_service = RemotionLocalService()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for video processing
    
    Args:
        event: Lambda event containing video URL and processing parameters
        context: Lambda context
        
    Returns:
        Dictionary containing the output path and status
    """
    try:
        # Parse input parameters
        video_url = event.get('video_url')
        caption_clips = event.get('caption_clips', [])
        settings = event.get('settings', {})
        
        if not video_url:
            raise ValueError("video_url is required")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Process the video
            result = remotion_service.process_video(
                video_url=video_url,
                caption_clips=caption_clips,
                settings=settings
            )
            
            # Upload the processed video to S3
            output_path = result['output_path']
            output_key = f"processed/{os.path.basename(output_path)}"
            
            with open(output_path, 'rb') as f:
                s3.upload_fileobj(
                    f,
                    s3_service.bucket_name,
                    output_key,
                    ExtraArgs={
                        'ContentType': 'video/mp4',
                        'ACL': 'public-read'
                    }
                )
            
            # Generate presigned URL for the processed video
            presigned_url = s3_service.get_download_url(output_key)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'output_url': presigned_url,
                    'output_key': output_key
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 