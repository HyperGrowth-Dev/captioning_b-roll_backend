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
        durationInFrames={900}
        fps={30}
        width={576}
        height={1024}
        schema={CaptionVideoPropsSchema}
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