import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, Sequence } from 'remotion';
import { TransitionSeries } from '@remotion/transitions';
import { AbsoluteFill, Video } from 'remotion';
import { z } from 'zod';

export const WordSchema = z.object({
  text: z.string(),
  startFrame: z.number(),
  endFrame: z.number()
});

export const CaptionSchema = z.object({
  text: z.string(),
  startFrame: z.number(),
  endFrame: z.number(),
  words: z.array(WordSchema).optional()
});

export const CaptionVideoPropsSchema = z.object({
  videoSrc: z.string(),
  captions: z.array(CaptionSchema),
  font: z.string(),
  fontSize: z.number(),
  color: z.string(),
  position: z.number(),
  transitions: z.object({
    type: z.enum(['fade', 'slide', 'none']),
    duration: z.number().optional()
  }).optional(),
  highlightColor: z.string().optional()
});

type CaptionVideoProps = z.infer<typeof CaptionVideoPropsSchema>;

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

  // Debug current frame and captions
  console.log('Current frame:', frame);
  console.log('Captions:', captions);

  // Convert video source to data URL if it's a local file
  const videoUrl = React.useMemo(() => {
    if (videoSrc.startsWith('data:')) {
      return videoSrc;
    }
    if (videoSrc.startsWith('http://') || videoSrc.startsWith('https://')) {
      return videoSrc;
    }
    throw new Error('Video source must be a data URL or HTTP/HTTPS URL');
  }, [videoSrc]);

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

  const renderWord = (word: z.infer<typeof WordSchema>) => {
    const isHighlighted = frame >= word.startFrame && frame <= word.endFrame;
    const opacity = isHighlighted ? 1 : 0.3;
    
    return (
      <span
        key={`${word.text}-${word.startFrame}`}
        style={{
          color: isHighlighted ? highlightColor : color,
          opacity,
          WebkitTextStroke: '2px black',
          transition: 'all 0.1s ease-in-out',
          fontWeight: 'bold',
          display: 'inline-block',
          margin: '0 2px'
        }}
      >
        {word.text}
      </span>
    );
  };

  const renderCaption = (caption: z.infer<typeof CaptionSchema>) => {
    if (!caption.words) {
      return caption.text;
    }

    // Show all words that have started, with proper highlighting
    return caption.words.map(renderWord);
  };

  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      {/* Video with optimized settings */}
      <Video 
        src={videoUrl}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          position: 'absolute',
          top: 0,
          left: 0,
          // Add hardware acceleration hints
          transform: 'translateZ(0)',
          backfaceVisibility: 'hidden',
          perspective: '1000px',
          willChange: 'transform'
        }}
        // Add video configuration props
        volume={1}
        playbackRate={1}
        muted={false}
        // Add video optimization props
        className="video-element"
        // Add video rendering hints
        onError={(e) => console.error('Video error:', e)}
      />
      
      {/* Captions with simplified transition logic */}
      {captions.map((caption: z.infer<typeof CaptionSchema>, index: number) => {
        const isVisible = frame >= caption.startFrame && frame <= caption.endFrame;
        
        if (!isVisible) return null;

        return (
          <div
            key={index}
            style={{
              position: 'absolute',
              bottom: `${position * 100}%`,
              left: '50%',
              transform: 'translateX(-50%)',
              width: '90%',
              textAlign: 'center',
              fontFamily: font,
              fontSize: `${fontSize}px`,
              color: color,
              textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
              padding: '20px',
              boxSizing: 'border-box',
              backgroundColor: 'rgba(0,0,0,0.5)',
              borderRadius: '10px',
              zIndex: 1,
              minHeight: `${fontSize * 2}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: 1,
              transition: 'opacity 0.2s ease-in-out'
            }}
          >
            {renderCaption(caption)}
          </div>
        );
      })}
    </AbsoluteFill>
  );
}; 