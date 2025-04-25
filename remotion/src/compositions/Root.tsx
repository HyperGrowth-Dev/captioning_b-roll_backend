import { registerRoot, Composition } from 'remotion';
import CaptionVideo, { CaptionVideoPropsSchema } from './CaptionVideo';
import video from '../assets/fitness_test_vid.mov';

const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="CaptionVideo"
        component={CaptionVideo}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        schema={CaptionVideoPropsSchema}
        defaultProps={{
          videoSrc: video,
          captions: [
            {
              text: "This is a test caption",
              startFrame: 0,
              endFrame: 90
            },
            {
              text: "Another caption appears here",
              startFrame: 150,
              endFrame: 240
            },
            {
              text: "Final test caption",
              startFrame: 300,
              endFrame: 390
            }
          ],
          font: "Arial",
          fontSize: 32,
          color: "#ffffff",
          position: "bottom",
          effect: true
        }}
      />
    </>
  );
};

registerRoot(RemotionRoot); 