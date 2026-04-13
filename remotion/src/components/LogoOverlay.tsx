import React from 'react';
import {Img, useCurrentFrame, interpolate} from 'remotion';

type Position = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';

interface LogoOverlayProps {
  logoUrl: string;
  position?: Position;
  scale?: number;
  opacity?: number;
  animation?: 'none' | 'fade-in' | 'fade-in-out';
  animationDuration?: number;
  margin?: number;
}

const POSITION_STYLES: Record<Position, React.CSSProperties> = {
  'top-left': {top: 0, left: 0},
  'top-right': {top: 0, right: 0},
  'bottom-left': {bottom: 0, left: 0},
  'bottom-right': {bottom: 0, right: 0},
  'center': {top: '50%', left: '50%', transform: 'translate(-50%, -50%)'},
};

export const LogoOverlay: React.FC<LogoOverlayProps> = ({
  logoUrl,
  position = 'top-left',
  scale = 0.12,
  opacity = 0.85,
  animation = 'fade-in',
  animationDuration = 30,
  margin = 24,
}) => {
  const frame = useCurrentFrame();

  let animatedOpacity = opacity;
  if (animation === 'fade-in') {
    animatedOpacity = interpolate(frame, [0, animationDuration], [0, opacity], {
      extrapolateRight: 'clamp',
    });
  }

  const posStyle = POSITION_STYLES[position];

  return (
    <div
      style={{
        position: 'absolute',
        ...posStyle,
        padding: margin,
        opacity: animatedOpacity,
        zIndex: 10,
      }}
    >
      <Img
        src={logoUrl}
        style={{
          height: `${scale * 100}%`,
          width: 'auto',
          objectFit: 'contain',
        }}
      />
    </div>
  );
};
