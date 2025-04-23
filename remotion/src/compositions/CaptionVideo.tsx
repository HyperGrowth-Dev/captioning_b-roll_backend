import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, Sequence } from 'remotion';
import { TransitionSeries } from '@remotion/transitions';
import { AbsoluteFill, Video } from 'remotion';

interface Word {
  text: string;
  startFrame: number;
  endFrame: number;
}

interface Caption {
  text: string;
  startFrame: number;
  endFrame: number;
  words?: Word[];
}

interface CaptionVideoProps {
  videoSrc: string;
  captions: Caption[];
  font: string;
  fontSize: number;
  color: string;
  position: number;
  transitions?: {
    type: 'fade' | 'slide' | 'none';
    duration?: number;
  };
  highlightColor?: string;
}

export const CaptionVideo: React.FC<CaptionVideoProps> = ({
  videoSrc,
  captions,
  font,
  fontSize,
  color,
  position,
  transitions = { type: 'fade', duration: 15 },
  highlightColor = '#FFD700'
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const getTransitionEffect = () => {
    switch (transitions.type) {
      case 'fade':
        return {
          timing: { duration: transitions.duration ?? 15 }
        };
      case 'slide':
        return {
          timing: { duration: transitions.duration ?? 15 }
        };
      default:
        return null;
    }
  };

  const renderWord = (word: Word) => {
    const isHighlighted = frame >= word.startFrame && frame <= word.endFrame;
    return (
      <span
        key={`${word.text}-${word.startFrame}`}
        style={{
          color: isHighlighted ? highlightColor : '#ffffff',
          WebkitTextStroke: '2px black',
          transition: 'color 0.1s ease-in-out'
        }}
      >
        {word.text}{' '}
      </span>
    );
  };

  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      <Sequence from={0}>
        <Video 
          src={videoSrc} 
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'fill',
            position: 'absolute',
            top: 0,
            left: 0
          }}
        />
      </Sequence>
      <TransitionSeries>
        {captions.map((caption: Caption, index: number) => {
          const effect = getTransitionEffect();
          return (
            <TransitionSeries.Sequence
              key={index}
              durationInFrames={caption.endFrame - caption.startFrame}
              offset={caption.startFrame}
              {...(effect && {
                timing: effect.timing
              })}
            >
              <div
                style={{
                  fontFamily: font,
                  fontSize: fontSize * 1.5,
                  position: 'absolute',
                  left: '50%',
                  top: `${position * 100}%`,
                  transform: 'translate(-50%, -50%)',
                  textAlign: 'center',
                  width: '90%',
                  opacity: 1,
                  color: '#ffffff',
                  WebkitTextStroke: '2px black',
                  fontWeight: 'bold',
                  padding: '15px'
                }}
              >
                {caption.words ? (
                  caption.words.map(renderWord)
                ) : (
                  caption.text
                )}
              </div>
            </TransitionSeries.Sequence>
          );
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
}; 