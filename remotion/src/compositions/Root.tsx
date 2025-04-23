import { registerRoot, Composition } from 'remotion';
import { CaptionVideo } from './CaptionVideo';
import video from '../assets/fitness_test_vid.mov';

const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="CaptionVideo"
        component={CaptionVideo as any}
        durationInFrames={300}
        fps={30}
        width={576}
        height={1024}
        defaultProps={{
          videoSrc: video,
          captions: [
            {
              text: "Hello World",
              startFrame: 0,
              endFrame: 30
            }
          ],
          font: "Arial",
          fontSize: 48,
          color: "#ffffff",
          position: 0.8,
          transitions: { type: 'fade', duration: 15 }
        }}
      />
    </>
  );
};

registerRoot(RemotionRoot); 