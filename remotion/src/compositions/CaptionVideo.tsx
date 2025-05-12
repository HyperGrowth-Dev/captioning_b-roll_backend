import React from 'react';
import { AbsoluteFill, useVideoConfig, OffthreadVideo, useCurrentFrame } from 'remotion';
import { TransitionSeries } from '@remotion/transitions';
import { z } from 'zod';
import '../styles/fonts.css';

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
  highlightType: z.enum(['background', 'fill']),
  useOffthreadVideo: z.boolean().optional(),
  onError: z.object({
    fallbackVideo: z.string()
  }).optional()
});

type CaptionVideoProps = z.infer<typeof CaptionVideoPropsSchema>;

const CaptionVideo: React.FC<CaptionVideoProps> = ({ 
  videoSrc, 
  captions, 
  font, 
  fontSize, 
  color, 
  position, 
  highlightType,
  useOffthreadVideo = true,
  onError
}) => {
  const { width, height, fps } = useVideoConfig();
  const frame = useCurrentFrame();

  const renderWord = (word: string, start: number, end: number) => {
    const currentTime = frame / fps;
    const isHighlighted = currentTime >= start && currentTime <= end;

    if (highlightType === 'background') {
      return (
        <span
          style={{
            display: 'inline-block',
            padding: '2px 4px',
            borderRadius: '4px',
            backgroundColor: isHighlighted ? '#FFFF00' : 'transparent',
            color: color,
            transition: 'background-color 0.3s ease-in-out',
          }}
        >
          {word}
        </span>
      );
    } else {
      return (
        <span
          style={{
            display: 'inline-block',
            padding: 0,
            backgroundColor: 'transparent',
            color: isHighlighted ? '#FFFF00' : color,
            transition: 'color 0.3s ease-in-out',
            fontWeight: 'inherit',
            textShadow: '2px 2px 4px rgba(0,0,0,0.6)'
          }}
        >
          {word}
        </span>
      );
    }
  };

  return (
    <AbsoluteFill>
      <OffthreadVideo 
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
        onError={(error) => {
          console.error('Video playback error:', error);
          if (onError?.fallbackVideo) {
            // If there's a fallback video, we could switch to it here
            // However, since this is a render, we'll just log the error
            console.log('Using fallback video:', onError.fallbackVideo);
          }
        }}
      />
      <TransitionSeries>
        {captions.map((caption, index) => {
          const currentTime = frame / fps;
          if (currentTime >= caption.startFrame / fps && currentTime <= caption.endFrame / fps) {
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
                    fontFamily: font,
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
