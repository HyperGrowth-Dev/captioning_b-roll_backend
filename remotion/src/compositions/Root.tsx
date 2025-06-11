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
        durationInFrames={2000} // Increased default duration to accommodate longer videos
        fps={30}
        width={576}
        height={1024}
        schema={CaptionVideoPropsSchema}
        calculateMetadata={({ props }: { props: z.infer<typeof CaptionVideoPropsSchema> }) => {
          // Calculate duration based on the last caption or b-roll clip
          const lastCaptionFrame = Math.max(...(props.captions?.map(c => c.endFrame) || [0]));
          const lastBrollFrame = Math.max(...(props.brollClips?.map(c => c.endFrame) || [0]));
          const videoDuration = Math.max(lastCaptionFrame, lastBrollFrame);
          
          // Add a larger buffer (2 seconds) to ensure we don't cut off the end
          const totalDuration = videoDuration + 60; // 60 frames = 2 seconds at 30fps
          
          console.log('Video duration calculation:', {
            lastCaptionFrame,
            lastBrollFrame,
            videoDuration,
            totalDuration,
            brollClips: props.brollClips?.map(clip => ({
              url: clip.url,
              startFrame: clip.startFrame,
              endFrame: clip.endFrame
            }))
          });
          
          return {
            durationInFrames: totalDuration,
            width: 576,
            height: 1024
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