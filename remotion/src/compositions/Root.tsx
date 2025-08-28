import { Composition } from 'remotion';
import CaptionVideo, { CaptionVideoPropsSchema } from './CaptionVideo';
import { FontLoader } from '../components/FontLoader';
import { z } from 'zod';

const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="CaptionVideo"
        component={(props: z.infer<typeof CaptionVideoPropsSchema>) => (
          <FontLoader>
            <CaptionVideo {...props} />
          </FontLoader>
        )}
        durationInFrames={6000} // Increased default duration to accommodate longer videos
        width={576}
        height={1024}
        schema={CaptionVideoPropsSchema}
        calculateMetadata={({ props }: { props: z.infer<typeof CaptionVideoPropsSchema> }) => {
          const fps = props.fps || 30; // Default to 30fps if not provided
          
          // Calculate duration based on video duration, captions, and b-roll clips
          const lastCaptionFrame = Math.max(...(props.captions?.map(c => c.endFrame) || [0]));
          const lastBrollFrame = Math.max(...(props.brollClips?.map(c => c.endFrame) || [0]));
          const videoDurationInFrames = props.videoDuration ? Math.ceil(props.videoDuration * fps) : 0;
          const totalDuration = Math.max(videoDurationInFrames, lastCaptionFrame, lastBrollFrame);
          
          console.log('Video duration calculation:', {
            videoDurationInSeconds: props.videoDuration,
            videoDurationInFrames,
            lastCaptionFrame,
            lastBrollFrame,
            totalDuration,
            fps
          });
          
          return {
            durationInFrames: totalDuration,
            width: 576,
            height: 1024,
            fps: fps // Pass the FPS to the composition
          };
        }}
        defaultProps={{
          videoSrc: "",
          captions: [],
          brollClips: [],
          font: "Barlow-BlackItalic",
          fontSize: 48,
          color: "white",
          position: "bottom",
          highlightType: "background"
        }}
      />
    </>
  );
};

export default RemotionRoot; 