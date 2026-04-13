import React from 'react';
import {Img, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface KenBurnsProps {
  imageUrl: string;
  startScale?: number;
  endScale?: number;
  panX?: number;
  panY?: number;
  durationFrames?: number;
}

export const KenBurns: React.FC<KenBurnsProps> = ({
  imageUrl,
  startScale = 1.0,
  endScale = 1.15,
  panX = 0,
  panY = 0,
  durationFrames,
}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const dur = durationFrames || durationInFrames;

  const scale = interpolate(frame, [0, dur], [startScale, endScale], {
    extrapolateRight: 'clamp',
  });

  const translateX = interpolate(frame, [0, dur], [0, panX], {
    extrapolateRight: 'clamp',
  });

  const translateY = interpolate(frame, [0, dur], [0, panY], {
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{width: '100%', height: '100%', overflow: 'hidden', position: 'absolute'}}>
      <Img
        src={imageUrl}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
        }}
      />
    </div>
  );
};
