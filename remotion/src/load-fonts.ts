import * as Montserrat from '@remotion/google-fonts/Montserrat';
import * as Barlow from '@remotion/google-fonts/Barlow';
import * as Oswald from '@remotion/google-fonts/Oswald';
import * as DancingScript from '@remotion/google-fonts/DancingScript';

export const loadFonts = async () => {
  // Load Montserrat
  await Montserrat.loadFont('normal', {
    weights: ['700'],
  });
  await Montserrat.loadFont('italic', {
    weights: ['600'],
  });

  // Load Barlow
  await Barlow.loadFont('normal', {
    weights: ['700', '900'],
  });
  await Barlow.loadFont('italic', {
    weights: ['700', '900'],
  });

  // Load Oswald
  await Oswald.loadFont('normal', {
    weights: ['400', '600'],
  });

  // Load Dancing Script
  await DancingScript.loadFont('normal', {
    weights: ['600'],
  });
}; 