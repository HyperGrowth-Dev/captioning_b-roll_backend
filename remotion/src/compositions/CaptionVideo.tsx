import React from 'react';
import { AbsoluteFill, useVideoConfig, Video, useCurrentFrame, delayRender, continueRender } from 'remotion';
import { TransitionSeries } from '@remotion/transitions';
import { slide } from '@remotion/transitions/slide';
import { loadFonts } from '../load-fonts';
import { z } from 'zod';
import { interpolate, interpolateColors } from 'remotion';

// Load fonts before rendering
loadFonts();

export const CaptionVideoPropsSchema = z.object({
  videoSrc: z.string(),
  captions: z.array(z.object({
    text: z.string(),
    startFrame: z.number(),
    endFrame: z.number(),
    words: z.array(z.object({
      text: z.string(),
      start: z.number(),
      end: z.number()
    })).optional()
  })),
  font: z.string(),
  fontSize: z.number(),
  color: z.string(),
  position: z.enum(['bottom', 'middle']),
  highlightType: z.enum(['background', 'fill'])
});

type CaptionVideoProps = z.infer<typeof CaptionVideoPropsSchema>;

const CaptionVideo: React.FC<CaptionVideoProps> = ({ 
  videoSrc, 
  captions, 
  font, 
  fontSize, 
  color, 
  position, 
  highlightType 
}) => {
  const { width, height, fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const [handle] = React.useState(() => delayRender());
  const [isVideoLoaded, setIsVideoLoaded] = React.useState(false);

  // Ensure videoSrc starts with a forward slash for local files
  const normalizedVideoSrc = videoSrc.startsWith('http') 
    ? videoSrc 
    : videoSrc.startsWith('/') 
      ? videoSrc 
      : `/${videoSrc}`;

  console.log('Received highlightType:', highlightType);

  React.useEffect(() => {
    const video = document.createElement('video');
    video.src = normalizedVideoSrc;
    
    // Set preload to auto to ensure the video starts loading immediately
    video.preload = 'auto';
    
    const handleLoad = () => {
      console.log("✅ Video loaded:", normalizedVideoSrc);
      setIsVideoLoaded(true);
      continueRender(handle);
    };

    const handleError = (event: Event | string) => {
      console.error("❌ Failed to load video:", normalizedVideoSrc, event);
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
  }, [normalizedVideoSrc, handle]);

  const renderWord = (word: string, start: number, end: number) => {
    const startFrame = Math.round(start * fps);
    const endFrame = Math.round(end * fps);
    
    console.log('Current frame:', frame);
    console.log('Word timing:', { word, startFrame, endFrame });
    
    const baseStyle = {
      display: 'inline-block',
      padding: '2px 4px',
      margin: '0 1px',
      transition: 'all 0.1s ease-in-out'
    };

    if (highlightType === 'background') {
      console.log('Using background highlight');
      return (
        <span
          style={{
            ...baseStyle,
            backgroundColor: frame >= startFrame && frame <= endFrame ? '#FFD700' : 'transparent',
            color: color,
            textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            borderRadius: '6px'
          }}
        >
          {word}
        </span>
      );
    } else {
      console.log('Using fill highlight');
      const progress = interpolate(
        frame,
        [startFrame - 3, startFrame, endFrame, endFrame + 2],
        [0, 1, 1, 0],
        {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp'
        }
      );

      return (
        <span
          style={{
            ...baseStyle,
            color: progress > 0 ? '#FFD700' : color,
            textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            transform: `scale(${1 + progress * 0.08})`,
            backgroundColor: 'transparent'
          }}
        >
          {word}
        </span>
      );
    }
  };

  return (
    <AbsoluteFill>
      {isVideoLoaded ? (
        <Video 
          src={normalizedVideoSrc} 
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
                    bottom: position === 'bottom' ? '25%' : '50%',
                    fontFamily: `"${font}", sans-serif`,
                    fontSize: `${fontSize * (height / 1080)}px`,
                    fontWeight: font.includes('Black') ? '900' : '700',
                    fontStyle: font.includes('Italic') ? 'italic' : 'normal',
                    zIndex: 1,
                    margin: '0 auto',
                    maxWidth: '80%',
                    left: '50%',
                    transform: position === 'bottom' 
                      ? 'translateX(-50%)' 
                      : 'translate(-50%, -50%)',
                    padding: '8px 16px',
                    borderRadius: '8px'
                  }}
                >
                  {caption.words ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '4px' }}>
                      {caption.words.map((word, wordIndex) => (
                        <React.Fragment key={wordIndex}>
                          {renderWord(word.text, word.start, word.end)}
                          {wordIndex < (caption.words?.length ?? 0) - 1 && ' '}
                        </React.Fragment>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: color, textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>
                      {caption.text}
                    </span>
                  )}
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