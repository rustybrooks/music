export const NOTE_ON = 0x90;
export const NOTE_OFF = 0x80;

export const divisions = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64];
export const accentCurves = [
  [70, 20, 70, 20, 80, 90, 20, 60, 20, 60, 20, 60, 20, 90, 80, 20],
  [30, 20, 90, 30, 25, 20, 40, 50, 40, 70, 40, 30, 35, 60, 40, 25],
  [30, 40, 60, 30, 40, 40, 100, 35, 30, 35, 60, 40, 70, 40, 100, 20],
  [25, 60, 30, 35, 80, 25, 30, 60, 25, 35, 45, 80, 35, 45, 80, 35],
  [90, 25, 40, 65, 90, 25, 40, 65, 90, 25, 40, 65, 90, 25, 40, 65],
  [85, 15, 25, 55, 50, 15, 25, 85, 50, 10, 40, 50, 45, 10, 45, 55],
  [100, 15, 20, 25, 35, 45, 100, 15, 100, 15, 35, 15, 60, 15, 25, 35],
  [70, 20, 20, 70, 20, 70, 20, 70, 70, 20, 70, 70, 20, 70, 20, 20],
  [5, 12, 24, 36, 50, 62, 74, 86, 100, 12, 24, 36, 50, 62, 74, 86],
  [100, 86, 74, 62, 50, 36, 24, 12, 100, 86, 74, 62, 50, 36, 24, 12],
  [0, 25, 50, 75, 100, 75, 50, 25, 0, 25, 50, 75, 100, 75, 50, 25],
  [100, 75, 50, 25, 0, 25, 50, 75, 100, 75, 50, 25, 0, 25, 50, 75],
].map(c => c.map(x => (128 * x) / 100));
export const scales = ['chromatic', 'major', 'harmonic_minor', 'melodic_minor', 'hexatonic', 'augmented', 'pentatonic_minor'];
export const styles = [
  'chord',
  'upward',
  'downward',
  'converge',
  'diverge',
  'alternate_bass',
  'alternate_bass_2',
  'alternate_melody',
  'alternate_melody_2',
  'random',
];
export const phrases = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0, 0],
  [0, 1, 3, 2, 5, 4, 6, 5, 7, 6, 8, 7, 9],
  [0, 1, 5, 6, 2, 7, 8, 4, 3, 1, 0, 1, 2, 3],
];