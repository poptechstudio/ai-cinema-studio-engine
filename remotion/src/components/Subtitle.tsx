import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface SubtitleEntry {
  text: string;
  startFrame: number;
  endFrame: number;
}

interface SubtitleProps {
  entries: SubtitleEntry[];
  fontFamily?: string;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
  position?: 'bottom' | 'center' | 'top';
  padding?: number;
}

export const Subtitle: React.FC<SubtitleProps> = ({
  entries,
  fontFamily = 'system-ui, -apple-system, sans-serif',
  fontSize = 24,
  color = '#ffffff',
  backgroundColor = 'rgba(0, 0, 0, 0.6)',
  position = 'bottom',
  padding = 60,
}) => {
  const frame = useCurrentFrame();

  const active = entries.find(e => frame >= e.startFrame && frame < e.endFrame);
  if (!active) return null;

  const localFrame = frame - active.startFrame;
  const duration = active.endFrame - active.startFrame;
  const opacity = interpolate(localFrame, [0, 5, duration - 5, duration], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const positionMap: Record<string, React.CSSProperties> = {
    bottom: {bottom: padding, left: '50%', transform: 'translateX(-50%)'},
    center: {top: '50%', left: '50%', transform: 'translate(-50%, -50%)'},
    top: {top: padding, left: '50%', transform: 'translateX(-50%)'},
  };

  return (
    <div
      style={{
        position: 'absolute',
        ...positionMap[position],
        opacity,
        zIndex: 25,
        maxWidth: '85%',
      }}
    >
      <div
        style={{
          backgroundColor,
          padding: '8px 20px',
          borderRadius: 6,
          fontFamily,
          fontSize,
          fontWeight: 600,
          color,
          textAlign: 'center',
          lineHeight: 1.4,
          backdropFilter: 'blur(4px)',
        }}
      >
        {active.text}
      </div>
    </div>
  );
};
