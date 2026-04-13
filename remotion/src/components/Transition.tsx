import React from 'react';
import {useCurrentFrame, interpolate} from 'remotion';

type TransitionType = 'fade' | 'dissolve' | 'wipe-left' | 'wipe-right' | 'zoom';

interface TransitionProps {
  type?: TransitionType;
  durationFrames?: number;
  children: React.ReactNode;
  startFrame?: number;
}

export const Transition: React.FC<TransitionProps> = ({
  type = 'fade',
  durationFrames = 15,
  children,
  startFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;

  if (localFrame < 0) return null;

  let style: React.CSSProperties = {position: 'absolute', width: '100%', height: '100%'};

  switch (type) {
    case 'fade':
      style.opacity = interpolate(localFrame, [0, durationFrames], [0, 1], {extrapolateRight: 'clamp'});
      break;

    case 'dissolve':
      style.opacity = interpolate(localFrame, [0, durationFrames], [0, 1], {extrapolateRight: 'clamp'});
      style.filter = `blur(${interpolate(localFrame, [0, durationFrames], [4, 0], {extrapolateRight: 'clamp'})}px)`;
      break;

    case 'wipe-left': {
      const clipX = interpolate(localFrame, [0, durationFrames], [100, 0], {extrapolateRight: 'clamp'});
      style.clipPath = `inset(0 ${clipX}% 0 0)`;
      break;
    }

    case 'wipe-right': {
      const clipX = interpolate(localFrame, [0, durationFrames], [100, 0], {extrapolateRight: 'clamp'});
      style.clipPath = `inset(0 0 0 ${clipX}%)`;
      break;
    }

    case 'zoom': {
      const scale = interpolate(localFrame, [0, durationFrames], [1.3, 1], {extrapolateRight: 'clamp'});
      style.opacity = interpolate(localFrame, [0, durationFrames / 2], [0, 1], {extrapolateRight: 'clamp'});
      style.transform = `scale(${scale})`;
      break;
    }
  }

  return <div style={style}>{children}</div>;
};
