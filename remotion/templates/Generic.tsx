import React from 'react';
import {AbsoluteFill, Video, Audio, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {LogoOverlay, LowerThird, EndCard, Subtitle, KenBurns, Transition} from '../src/components';

export interface GenericClip {
  videoUrl?: string;
  imageUrl?: string; // For Ken Burns on stills
  duration: number;
}

export interface GenericBranding {
  logoUrl?: string;
  logoPosition?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  primaryColor: string;
  secondaryColor: string;
  fontFamily?: string;
}

export interface GenericMetadata {
  title: string;
  clientName?: string;
  episodeTitle?: string;
  airDate?: string;
  credits?: string[];
  contactEmail?: string;
  website?: string;
}

export interface GenericProps {
  clips: GenericClip[];
  audioUrl: string;
  branding: GenericBranding;
  metadata: GenericMetadata;
  subtitles?: Array<{text: string; startFrame: number; endFrame: number}>;
  transitionType?: 'fade' | 'dissolve' | 'wipe-left' | 'wipe-right' | 'zoom';
  transitionDuration?: number;
  endCardDuration?: number;
  lowerThirdStart?: number;
  lowerThirdDuration?: number;
}

export const GenericComposition: React.FC<GenericProps> = ({
  clips,
  audioUrl,
  branding,
  metadata,
  subtitles = [],
  transitionType = 'fade',
  transitionDuration = 15,
  endCardDuration = 4,
  lowerThirdStart = 30,
  lowerThirdDuration = 120,
}) => {
  const {fps} = useVideoConfig();
  const fontFamily = branding.fontFamily || 'system-ui, -apple-system, sans-serif';

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

  // Build lower third text
  const primaryText = metadata.clientName
    ? `${metadata.clientName} — ${metadata.title}`
    : metadata.title;
  const secondaryText = [metadata.episodeTitle, metadata.airDate].filter(Boolean).join(' | ');

  return (
    <AbsoluteFill style={{backgroundColor: branding.secondaryColor}}>
      {/* Video/image clips */}
      {clipTimings.map((clip, idx) => (
        <Sequence key={idx} from={clip.startFrame} durationInFrames={clip.durationFrames}>
          <Transition type={idx === 0 ? 'fade' : transitionType} durationFrames={transitionDuration}>
            {clip.imageUrl ? (
              <KenBurns imageUrl={clip.imageUrl} startScale={1.0} endScale={1.12} panX={-10} />
            ) : clip.videoUrl ? (
              <Video src={clip.videoUrl} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            ) : (
              <AbsoluteFill style={{backgroundColor: branding.secondaryColor}} />
            )}
          </Transition>
        </Sequence>
      ))}

      {/* Audio */}
      <Audio src={audioUrl} />

      {/* Logo */}
      {branding.logoUrl && (
        <LogoOverlay
          logoUrl={branding.logoUrl}
          position={branding.logoPosition || 'top-left'}
          scale={0.08}
          opacity={0.85}
          animation="fade-in"
        />
      )}

      {/* Lower third */}
      <LowerThird
        primaryText={primaryText}
        secondaryText={secondaryText || undefined}
        backgroundColor="rgba(0, 0, 0, 0.75)"
        accentColor={branding.primaryColor}
        fontFamily={fontFamily}
        startFrame={lowerThirdStart}
        durationFrames={lowerThirdDuration}
      />

      {/* Subtitles */}
      {subtitles.length > 0 && (
        <Subtitle entries={subtitles} fontFamily={fontFamily} />
      )}

      {/* End card */}
      <Sequence from={clipsEndFrame - endCardFrames}>
        <EndCard
          title={metadata.title}
          credits={metadata.credits}
          contactEmail={metadata.contactEmail}
          website={metadata.website}
          backgroundColor={branding.secondaryColor}
          accentColor={branding.primaryColor}
          animation="fade"
          fontFamily={fontFamily}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
