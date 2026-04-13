import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';

interface EndCardProps {
  title?: string;
  buttonText?: string;
  buttonUrl?: string;
  contactEmail?: string;
  website?: string;
  credits?: string[];
  backgroundColor?: string;
  textColor?: string;
  accentColor?: string;
  animation?: 'zoom-in' | 'fade' | 'slide-up';
  fontFamily?: string;
}

export const EndCard: React.FC<EndCardProps> = ({
  title = 'Thank you',
  buttonText,
  contactEmail,
  website,
  credits,
  backgroundColor = '#0a0a0a',
  textColor = '#ffffff',
  accentColor = '#2792dc',
  animation = 'fade',
  fontFamily = 'system-ui, -apple-system, sans-serif',
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const scale = animation === 'zoom-in'
    ? spring({frame, fps, config: {damping: 200, mass: 0.8}})
    : 1;

  const opacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});

  const translateY = animation === 'slide-up'
    ? interpolate(frame, [0, 20], [40, 0], {extrapolateRight: 'clamp'})
    : 0;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        opacity,
        transform: `scale(${scale}) translateY(${translateY}px)`,
        fontFamily,
        zIndex: 30,
      }}
    >
      <div style={{fontSize: 42, fontWeight: 800, color: textColor, letterSpacing: '-0.02em', textAlign: 'center'}}>
        {title}
      </div>

      {buttonText && (
        <div
          style={{
            marginTop: 32,
            padding: '14px 40px',
            backgroundColor: accentColor,
            color: '#fff',
            fontSize: 22,
            fontWeight: 700,
            borderRadius: 8,
            letterSpacing: '0.02em',
          }}
        >
          {buttonText}
        </div>
      )}

      {(contactEmail || website) && (
        <div style={{marginTop: 24, fontSize: 16, color: textColor, opacity: 0.6, textAlign: 'center'}}>
          {contactEmail && <div>{contactEmail}</div>}
          {website && <div>{website}</div>}
        </div>
      )}

      {credits && credits.length > 0 && (
        <div style={{marginTop: 32, fontSize: 14, color: textColor, opacity: 0.4, textAlign: 'center'}}>
          {credits.map((credit, i) => <div key={i}>{credit}</div>)}
        </div>
      )}
    </div>
  );
};
