import logging
import boto3
import json
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemotionLambdaService:
    def __init__(self):
        logger.info("Initializing RemotionLambdaService")
        self.lambda_client = boto3.client('lambda')
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'hyper-editor'
        self.lambda_function_name = "remotion-render-4-0-273-mem2048mb-disk2048mb-120sec"
        self.serve_url = "https://remotionlambda-useast2-bvf5c7h3eb.s3.us-east-2.amazonaws.com/sites/caption-video/index.html"
        self.region = "us-east-2"
        
        # Lambda configuration
        self.ram = 3009  # Match reference config
        self.disk = 2048  # Match reference config
        self.timeout = 240  # Match reference config
        
        logger.info("RemotionLambdaService initialized successfully")

    async def render(self, input_props: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a video using Remotion Lambda
        
        Args:
            input_props: Dictionary containing the input properties for the render
            
        Returns:
            Dictionary containing the render response
        """
        try:
            # Extract video key from input_props
            video_src = input_props.get('videoSrc', '')
            video_key = video_src.split('/')[-1].split('?')[0]
            
            render_request = {
                'type': 'start',
                'serveUrl': self.serve_url,
                'composition': 'CaptionVideo',
                'inputProps': input_props,
                'codec': 'h264',
                'imageFormat': 'jpeg',
                'maxRetries': 1,
                'privacy': 'public',
                'framesPerLambda': 100,
                'memorySizeInMb': self.ram,
                'diskSizeInMb': self.disk,
                'timeoutInSeconds': self.timeout,
                'outputLocation': {
                    's3': {
                        'bucketName': self.bucket_name,
                        'key': f"processed/{os.path.basename(video_key)}"
                    }
                }
            }

            # Log the request
            logger.info(f"Sending render request: {json.dumps(render_request, indent=2)}")

            # Invoke Lambda function
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                Payload=json.dumps(render_request),
                InvocationType='RequestResponse'
            )

            # Get and decode logs if available
            if 'LogResult' in response:
                import base64
                logs = base64.b64decode(response['LogResult']).decode('utf-8')
                logger.info("=== Lambda Execution Logs ===")
                logger.info(logs)

            # Parse response
            payload = response['Payload'].read()
            logger.info(f"Raw response payload: {payload}")

            if not payload:
                return {
                    'status': 'processing',
                    'message': 'Video processing started',
                    'renderId': video_key
                }

            try:
                response_payload = json.loads(payload)
                logger.info(f"Parsed response payload: {json.dumps(response_payload, indent=2)}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Lambda response: {str(e)}")
                return {
                    'status': 'processing',
                    'message': 'Video processing started',
                    'renderId': video_key
                }

            if 'errorMessage' in response_payload:
                raise Exception(f"Render failed: {response_payload['errorMessage']}")

            return response_payload

        except Exception as e:
            logger.error(f"Error rendering video: {str(e)}")
            raise

    def cleanup(self):
        """Clean up any temporary resources"""
        pass  # Add cleanup logic if needed
