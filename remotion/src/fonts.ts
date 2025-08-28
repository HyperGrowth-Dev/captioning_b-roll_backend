export const fonts = {
  'Montserrat-Bold': 'Montserrat-Bold',
  'Montserrat-SemiBoldItalic': 'Montserrat-SemiBoldItalic',
  'Barlow-Bold': 'Barlow-Bold',
  'Barlow-BlackItalic': 'Barlow-BlackItalic',
  'Oswald-Regular': 'Oswald-Regular',
  'Oswald-SemiBold': 'Oswald-SemiBold',
  'DancingScript-SemiBold': 'DancingScript-SemiBold'
} as const;

export type FontName = keyof typeof fonts;

export const defaultFont = 'Montserrat-Bold'; 