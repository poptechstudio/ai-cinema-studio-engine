import {Composition} from 'remotion';
import {Main} from './Main';
import {PopTechComposition} from '../templates/PopTech';
import {GenericComposition} from '../templates/Generic';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* === Test composition (Phase 1) === */}
      <Composition
        id="Main"
        component={Main}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* === PopTech Brand Template === */}
      <Composition
        id="PopTech"
        component={PopTechComposition}
        durationInFrames={450}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          clips: [{videoUrl: '', duration: 5}, {videoUrl: '', duration: 5}],
          audioUrl: '',
          title: 'PopTech Cinema Engine',
          description: 'AI Cinema at API-cost pricing',
          ctaButton: {text: 'Get Started'},
        }}
      />
      <Composition
        id="PopTech-Vertical"
        component={PopTechComposition}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clips: [{videoUrl: '', duration: 5}, {videoUrl: '', duration: 5}],
          audioUrl: '',
          title: 'PopTech Cinema Engine',
          description: 'AI Cinema at API-cost pricing',
          ctaButton: {text: 'Get Started'},
        }}
      />

      {/* === Generic Client Template === */}
      <Composition
        id="Generic"
        component={GenericComposition}
        durationInFrames={600}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          clips: [{videoUrl: '', duration: 5}],
          audioUrl: '',
          branding: {primaryColor: '#2792dc', secondaryColor: '#0a0a0a'},
          metadata: {title: 'Client Project'},
        }}
      />
      <Composition
        id="Generic-Vertical"
        component={GenericComposition}
        durationInFrames={600}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          clips: [{videoUrl: '', duration: 5}],
          audioUrl: '',
          branding: {primaryColor: '#2792dc', secondaryColor: '#0a0a0a'},
          metadata: {title: 'Client Project'},
        }}
      />
    </>
  );
};
