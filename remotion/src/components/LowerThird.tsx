import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';

interface LowerThirdProps {
  primaryText: string;
  secondaryText?: string;
  backgroundColor?: string;
  textColor?: string;
  accentColor?: string;
  position?: 'bottom' | 'top';
  animation?: 'slide-up' | 'slide-left' | 'fade';
  fontFamily?: string;
  startFrame?: number;
  durationFrames?: number;
}

export const LowerThird: React.FC<LowerThirdProps> = ({
  primaryText,
  secondaryText,
  backgroundColor = 'rgba(0, 0, 0, 0.75)',
  textColor = '#ffffff',
  accentColor = '#2792dc',
  position = 'bottom',
  animation = 'slide-up',
  fontFamily = 'system-ui, -apple-system, sans-serif',
  startFrame = 0,
  durationFrames = 120,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = frame - startFrame;

  if (localFrame < 0 || localFrame > durationFrames) return null;

  const fadeInDuration = 15;
  const fadeOutStart = durationFrames - 15;

  let translateY = 0;
  let translateX = 0;
  let opacity = 1;

  if (animation === 'slide-up') {
    translateY = interpolate(localFrame, [0, fadeInDuration], [60, 0], {
      extrapolateRight: 'clamp',
    });
    if (localFrame > fadeOutStart) {
      translateY = interpolate(localFrame, [fadeOutStart, durationFrames], [0, 60], {
        extrapolateLeft: 'clamp',
      });
    }
  } else if (animation === 'slide-left') {
    translateX = interpolate(localFrame, [0, fadeInDuration], [-300, 0], {
      extrapolateRight: 'clamp',
    });
  }

  opacity = interpolate(localFrame, [0, fadeInDuration], [0, 1], {
    extrapolateRight: 'clamp',
  });
  if (localFrame > fadeOutStart) {
    opacity = interpolate(localFrame, [fadeOutStart, durationFrames], [1, 0], {
      extrapolateLeft: 'clamp',
    });
  }

  return (
    <div
      style={{
        position: 'absolute',
        [position]: 80,
        left: 40,
        right: 40,
        opacity,
        transform: `translate(${translateX}px, ${translateY}px)`,
        zIndex: 20,
      }}
    >
      {/* Accent bar */}
      <div style={{width: 50, height: 4, backgroundColor: accentColor, marginBottom: 8, borderRadius: 2}} />
      {/* Text container */}
      <div
        style={{
          backgroundColor,
          padding: '14px 24px',
          borderRadius: 6,
          backdropFilter: 'blur(8px)',
        }}
      >
        <div style={{fontFamily, fontSize: 28, fontWeight: 700, color: textColor, letterSpacing: '-0.01em'}}>
          {primaryText}
        </div>
        {secondaryText && (
          <div style={{fontFamily, fontSize: 18, fontWeight: 400, color: textColor, opacity: 0.75, marginTop: 4}}>
            {secondaryText}
          </div>
        )}
      </div>
    </div>
  );
};
