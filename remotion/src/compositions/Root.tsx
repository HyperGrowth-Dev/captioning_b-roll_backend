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
        durationInFrames={900} // Default duration, will be overridden by calculateMetadata
        fps={30}
        width={576}
        height={1024}
        schema={CaptionVideoPropsSchema}
        calculateMetadata={({ props }: { props: z.infer<typeof CaptionVideoPropsSchema> }) => {
          // Calculate duration based on the last caption or b-roll clip
          const lastCaptionFrame = Math.max(...(props.captions?.map(c => c.endFrame) || [0]));
          const lastBrollFrame = Math.max(...(props.brollClips?.map(c => c.endFrame) || [0]));
          const videoDuration = Math.max(lastCaptionFrame, lastBrollFrame);
          // Add a small buffer (1 second) to ensure we don't cut off the end
          return {
            durationInFrames: videoDuration + 30, // 30 frames = 1 second at 30fps
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