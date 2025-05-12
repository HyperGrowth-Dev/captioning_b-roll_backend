import { renderMediaOnLambda, getFunctions, getRenderProgress } from '@remotion/lambda/client';
import { getOrCreateBucket } from '@remotion/lambda';
import path from 'path';
import fs from 'fs';

// Read the input JSON file passed as an argument
const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Please provide a path to the input JSON file');
  process.exit(1);
}

const renderVideo = async () => {
  try {
    // Read and parse the input JSON
    const input = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
    const { videoSrc, outputKey } = input;

    // Get the function name - this assumes you've already deployed the function
    const functions = await getFunctions({
      region: 'us-east-2',
      compatibleOnly: true,
    });

    if (functions.length === 0) {
      throw new Error('No compatible Remotion Lambda functions found');
    }

    if (!process.env.REMOTION_SERVE_URL) {
      throw new Error('REMOTION_SERVE_URL environment variable is required');
    }

    // Get the first compatible function
    const functionName = functions[0].functionName;

    // Render the video
    const { renderId, bucketName } = await renderMediaOnLambda({
      region: 'us-east-2',
      functionName,
      serveUrl: process.env.REMOTION_SERVE_URL,
      composition: 'CaptionVideo',
      inputProps: {
        videoSrc,
        captions: [],  // Empty captions for now
        font: "Barlow",
        fontSize: 48,
        color: "white",
        position: "bottom",
        highlightType: "background"
      },
      codec: 'h264',
      imageFormat: 'jpeg',
      maxRetries: 1,
      privacy: 'public',
      outName: outputKey
    });

    // Poll for completion
    while (true) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      const progress = await getRenderProgress({
        renderId,
        bucketName,
        functionName,
        region: 'us-east-2',
      });

      if (progress.done) {
        console.log(JSON.stringify({
          status: 'success',
          outputUrl: progress.outputFile,
          bucketName,
          renderId
        }));
        process.exit(0);
      }

      if (progress.fatalErrorEncountered) {
        console.error(JSON.stringify({
          status: 'error',
          errors: progress.errors
        }));
        process.exit(1);
      }
    }
  } catch (err) {
    console.error(JSON.stringify({
      status: 'error',
      message: err.message
    }));
    process.exit(1);
  }
};

renderVideo(); 