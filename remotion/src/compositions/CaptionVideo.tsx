import React from 'react';
import { AbsoluteFill, useVideoConfig, OffthreadVideo, useCurrentFrame, interpolate } from 'remotion';
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
  brollClips: z.array(z.object({
    url: z.string(),
    startFrame: z.number(),
    endFrame: z.number(),
    transitionDuration: z.number().optional() // Duration of fade transition in frames
  })).optional(),
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
  brollClips = [],
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

  // Add debug logging
  console.log('CaptionVideo props:', {
    videoSrc,
    captions,
    font,
    fontSize,
    color,
    position,
    highlightType
  });

  console.log('B-roll clips received:', brollClips);

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

  // Function to determine which video should be shown
  const getCurrentVideo = () => {
    console.log('Current frame:', frame);
    console.log('FPS:', fps);
    console.log('B-roll clips:', brollClips);
    
    for (const clip of brollClips) {
      console.log('Checking clip:', {
        startFrame: clip.startFrame,
        endFrame: clip.endFrame,
        currentFrame: frame,
        url: clip.url,
        transitionDuration: clip.transitionDuration
      });
      
      const transitionDuration = clip.transitionDuration || 8; // Default 0.27s transition at 30fps
      const startFrame = clip.startFrame;
      const endFrame = clip.endFrame;
      
      // Check if we're in a transition period
      if (frame >= startFrame && frame <= startFrame + transitionDuration) {
        // Fade in b-roll
        const progress = (frame - startFrame) / transitionDuration;
        console.log('Fade in progress:', progress);
        return {
          type: 'transition',
          mainOpacity: 1 - progress,
          brollOpacity: progress,
          brollUrl: clip.url
        };
      } else if (frame >= endFrame - transitionDuration && frame <= endFrame) {
        // Fade out b-roll
        const progress = (frame - (endFrame - transitionDuration)) / transitionDuration;
        console.log('Fade out progress:', progress);
        return {
          type: 'transition',
          mainOpacity: progress,
          brollOpacity: 1 - progress,
          brollUrl: clip.url
        };
      } else if (frame > startFrame && frame < endFrame) {
        // Full b-roll
        console.log('Full b-roll');
        return {
          type: 'broll',
          brollUrl: clip.url
        };
      }
    }
    
    // Default to main video
    return {
      type: 'main'
    };
  };

  const currentVideo = getCurrentVideo();
  console.log('Current video state:', currentVideo);

  return (
    <AbsoluteFill>
      {/* Main Video */}
      <div style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        opacity: currentVideo.type === 'broll' ? 0 : 
                currentVideo.type === 'transition' ? currentVideo.mainOpacity : 1
      }}>
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
              console.log('Using fallback video:', onError.fallbackVideo);
            }
          }}
        />
      </div>

      {/* B-roll Video (when active) */}
      {currentVideo.type !== 'main' && currentVideo.brollUrl && (
        <div style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          opacity: currentVideo.type === 'transition' ? currentVideo.brollOpacity : 1
        }}>
          <OffthreadVideo
            src={currentVideo.brollUrl}
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
              console.error('B-roll video error:', error);
              console.error('B-roll URL:', currentVideo.brollUrl);
            }}
          />
        </div>
      )}

      {/* Captions (always on top) */}
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
                    zIndex: 2, // Ensure captions are always on top
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
