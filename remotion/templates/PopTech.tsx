import React from 'react';
import {AbsoluteFill, Video, Audio, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {LogoOverlay, LowerThird, EndCard, Transition} from '../src/components';

export interface PopTechClip {
  videoUrl: string;
  duration: number; // seconds
}

export interface PopTechProps {
  clips: PopTechClip[];
  audioUrl: string;
  title: string;
  description?: string;
  ctaButton: {
    text: string;
    url?: string;
  };
  logoUrl?: string;
  brandColors?: {
    primary: string;
    secondary: string;
  };
  transitionType?: 'fade' | 'dissolve' | 'wipe-left';
  transitionDuration?: number;
  endCardDuration?: number;
}

const DEFAULT_COLORS = {primary: '#2792dc', secondary: '#0a0a0a'};
const END_CARD_SECONDS = 3;

export const PopTechComposition: React.FC<PopTechProps> = ({
  clips,
  audioUrl,
  title,
  description,
  ctaButton,
  logoUrl,
  brandColors = DEFAULT_COLORS,
  transitionType = 'fade',
  transitionDuration = 10,
  endCardDuration = END_CARD_SECONDS,
}) => {
  const {fps} = useVideoConfig();

  // Calculate clip timings
  let currentFrame = 0;
  const clipTimings = clips.map(clip => {
    const start = currentFrame;
    const dur = Math.round(clip.duration * fps);
    currentFrame += dur;
    return {...clip, startFrame: start, durationFrames: dur};
  });

  const clipsEndFrame = currentFrame;
  const endCardFrames = endCardDuration * fps;
  const lowerThirdStart = Math.round(fps * 1.5); // 1.5s in
  const lowerThirdDuration = Math.round(fps * 4);

  return (
    <AbsoluteFill style={{backgroundColor: brandColors.secondary}}>
      {/* Video clips */}
      {clipTimings.map((clip, idx) => (
        <Sequence key={idx} from={clip.startFrame} durationInFrames={clip.durationFrames}>
          <Transition type={idx === 0 ? 'fade' : transitionType} durationFrames={transitionDuration}>
            <Video src={clip.videoUrl} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          </Transition>
        </Sequence>
      ))}

      {/* Audio */}
      <Audio src={audioUrl} />

      {/* Logo */}
      {logoUrl && (
        <LogoOverlay logoUrl={logoUrl} position="top-left" scale={0.08} opacity={0.85} animation="fade-in" />
      )}

      {/* Lower third */}
      <LowerThird
        primaryText={title}
        secondaryText={description}
        backgroundColor="rgba(0, 0, 0, 0.75)"
        accentColor={brandColors.primary}
        startFrame={lowerThirdStart}
        durationFrames={lowerThirdDuration}
      />

      {/* End card */}
      <Sequence from={clipsEndFrame - endCardFrames}>
        <EndCard
          title={ctaButton.text}
          buttonText="Learn More"
          contactEmail="hello@poptechstudio.ai"
          website="poptechstudio.ai"
          backgroundColor={brandColors.secondary}
          accentColor={brandColors.primary}
          animation="zoom-in"
        />
      </Sequence>
    </AbsoluteFill>
  );
};
