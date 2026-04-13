import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const scale = spring({
    frame,
    fps,
    config: {damping: 200},
  });

  const isVertical = height > width;

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
      }}
    >
      <div
        style={{
          opacity,
          transform: `scale(${scale})`,
          textAlign: 'center',
          padding: isVertical ? '0 40px' : '0 80px',
        }}
      >
        <div
          style={{
            fontSize: isVertical ? 48 : 72,
            fontWeight: 800,
            color: '#ffffff',
            fontFamily: 'system-ui, sans-serif',
            letterSpacing: '-0.02em',
            lineHeight: 1.1,
          }}
        >
          PopTech Cinema
        </div>
        <div
          style={{
            fontSize: isVertical ? 20 : 28,
            color: '#888888',
            fontFamily: 'system-ui, sans-serif',
            marginTop: 16,
            fontWeight: 300,
          }}
        >
          AI Production Engine
        </div>
      </div>
    </AbsoluteFill>
  );
};
