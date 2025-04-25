import React from 'react';
import { AbsoluteFill, useVideoConfig, Video, useCurrentFrame, delayRender, continueRender } from 'remotion';
import { TransitionSeries } from '@remotion/transitions';
import { slide } from '@remotion/transitions/slide';
import { loadFonts } from '../load-fonts';
import { z } from 'zod';

// Load fonts before rendering
loadFonts();

export const CaptionVideoPropsSchema = z.object({
  videoSrc: z.string(),
  captions: z.array(z.object({
    text: z.string(),
    startFrame: z.number(),
    endFrame: z.number()
  })),
  font: z.string(),
  fontSize: z.number(),
  color: z.string(),
  position: z.enum(['bottom', 'middle']),
  effect: z.boolean().optional()
});

type CaptionVideoProps = z.infer<typeof CaptionVideoPropsSchema>;

const CaptionVideo: React.FC<CaptionVideoProps> = ({ videoSrc, captions, font, fontSize, color, position, effect }) => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();
  const [handle] = React.useState(() => delayRender());
  const [isVideoLoaded, setIsVideoLoaded] = React.useState(false);

  React.useEffect(() => {
    const video = document.createElement('video');
    video.src = videoSrc;
    
    // Set preload to auto to ensure the video starts loading immediately
    video.preload = 'auto';
    
    const handleLoad = () => {
      console.log("✅ Video loaded:", videoSrc);
      setIsVideoLoaded(true);
      continueRender(handle);
    };

    const handleError = (event: Event | string) => {
      console.error("❌ Failed to load video:", videoSrc, event);
      setIsVideoLoaded(false);
      continueRender(handle);
    };

    video.onloadeddata = handleLoad;
    video.oncanplay = handleLoad;
    video.onerror = handleError;

    // Start loading the video
    video.load();

    return () => {
      video.onloadeddata = null;
      video.oncanplay = null;
      video.onerror = null;
    };
  }, [videoSrc, handle]);

  return (
    <AbsoluteFill>
      {isVideoLoaded ? (
        <Video 
          src={videoSrc} 
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            position: 'absolute',
            top: 0,
            left: 0,
            backgroundColor: '#000'
          }}
        />
      ) : (
        <div style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#000'
        }}>
          Loading video...
        </div>
      )}
      <TransitionSeries>
        {captions.map((caption, index) => {
          // Only show caption if current frame is within its time range
          if (frame >= caption.startFrame && frame <= caption.endFrame) {
            return (
              <TransitionSeries.Sequence
                key={index}
                offset={caption.startFrame}
                durationInFrames={caption.endFrame - caption.startFrame}
              >
                <div
                  style={{
                    position: 'absolute',
                    width: '100%',
                    textAlign: 'center',
                    bottom: position === 'bottom' ? '10%' : '50%',
                    fontFamily: `"${font}", sans-serif`,
                    fontSize: `${fontSize * (height / 1080)}px`,
                    color: color,
                    textShadow: '2px 2px 4px rgba(0,0,0,0.8), -2px -2px 4px rgba(0,0,0,0.8)',
                    fontWeight: font.includes('Black') ? '900' : '700',
                    fontStyle: font.includes('Italic') ? 'italic' : 'normal',
                    zIndex: 1,
                    margin: '0 auto',
                    maxWidth: '80%',
                    left: '50%',
                    transform: position === 'bottom' 
                      ? 'translateX(-50%)' 
                      : 'translate(-50%, -50%)',
                    backgroundColor: 'transparent',
                    padding: '8px 16px'
                  }}
                >
                  {caption.text}
                </div>
              </TransitionSeries.Sequence>
            );
          }
          return null;
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
};

export default CaptionVideo; 