import { loadFont as loadMontserrat } from '@remotion/google-fonts/Montserrat';
import { loadFont as loadBarlow } from '@remotion/google-fonts/Barlow';
import { loadFont as loadOswald } from '@remotion/google-fonts/Oswald';
import { loadFont as loadDancingScript } from '@remotion/google-fonts/DancingScript';

export const loadFonts = async () => {
  // Load Montserrat
  await loadMontserrat('normal', {
    weights: ['700'],
  });
  await loadMontserrat('italic', {
    weights: ['600'],
  });

  // Load Barlow
  await loadBarlow('normal', {
    weights: ['700', '900'],
  });
  await loadBarlow('italic', {
    weights: ['700', '900'],
  });

  // Load Oswald
  await loadOswald('normal', {
    weights: ['400', '600'],
  });

  // Load Dancing Script
  await loadDancingScript('normal', {
    weights: ['600'],
  });
}; 