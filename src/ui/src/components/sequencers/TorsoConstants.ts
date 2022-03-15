import { accentCurves, divisions, phrases, scales, styles } from '../../lib/sequencers/TorsoConstants';
import { TorsoTrack, TorsoTrackSlice } from '../../lib/sequencers/Torso';

export const maxSteps = 16;

export enum Mode {
  'TRACKS',
  'PATTERNS',
  SAVE,
  BANKS,
  SELECT,
  TEMP,
  MULTI,
  CLEAR,
  COPY,
  STEPS,
  MANUAL_STEPS,
  PULSES,
  ROTATE,
  CYCLES,
  DIVISION,
  VELOCITY,
  SUSTAIN,
  PITCH,
  HARMONY,
  MUTE,
  REPEATS,
  REPEAT_OFFSET,
  REPEAT_TIME,
  REPEAT_PACE,
  VOICING,
  MELODY,
  PHRASE,
  ACCENT,
  ACCENT_CURVE,
  STYLE,
  SCALE,
  ROOT,
  LENGTH,
  QUANTIZE,
  TIMING,
  DELAY,
  RANDOM,
  RANDOM_RATE,
  TEMPO,
  CHANNEL,
}

export interface Knob {
  label: string;
  alt_label: string;
  keybind: string;
  mode?: Mode;
  property?: keyof TorsoTrack;
  min?: number;
  max?: number;
  type?: string;
  alt_mode?: Mode;
  alt_min?: number;
  alt_max?: number;
  alt_property?: keyof TorsoTrack;
  alt_suppress_dial?: boolean;
  alt_type?: string;
  list?: any[];
  alt_list?: any[];
}

export const knobs: Array<Array<Knob>> = [
  [
    {
      label: 'steps',
      alt_label: '',
      keybind: 'a',
      mode: Mode.STEPS,
      property: 'getSteps',
      min: 1,
      max: maxSteps,
      type: 'int',
      alt_mode: Mode.MANUAL_STEPS,
      alt_property: 'getManualSteps',
      alt_suppress_dial: true,
    },
    {
      label: 'pulses',
      alt_label: 'rotate',
      keybind: 's',
      mode: Mode.PULSES,
      property: 'getPulses',
      min: 1,
      max: maxSteps,
      type: 'int',
      alt_mode: Mode.ROTATE,
      alt_property: 'getRotate',
      alt_min: 0,
      alt_max: 15,
    },
    {
      label: 'cycles',
      alt_label: '',
      keybind: 'd',
    },
    {
      label: 'division',
      alt_label: '',
      keybind: 'f',
      mode: Mode.DIVISION,
      property: 'division',
      list: divisions,
    },
    {
      label: 'velocity',
      alt_label: '',
      keybind: 'g',
      mode: Mode.VELOCITY,
      property: 'velocity',
      min: 0,
      max: 127,
      type: 'int',
    },
    {
      label: 'sustain',
      alt_label: '',
      keybind: 'h',
      mode: Mode.SUSTAIN,
      property: 'sustain',
      min: 0,
      max: 1,
      type: 'float',
    },

    {
      label: 'pitch',
      alt_label: 'harmony',
      keybind: 'j',
      mode: Mode.PITCH,
      property: 'pitch',
      min: -36,
      max: 36,
      type: 'int',
      alt_mode: Mode.HARMONY,
      alt_property: 'harmony', // FIXME min/max etc?
    },
    {
      label: 'length',
      keybind: 'k',
      mode: Mode.LENGTH,
      alt_mode: Mode.QUANTIZE,
      alt_label: 'quantize',
    },
    {
      label: 'tempo',
      alt_label: '',
      keybind: 'l',
      mode: Mode.TEMPO,
      property: 'bpm',
      min: 30,
      max: 300,
      type: 'int',
    },
  ],
  [
    {
      label: 'repeats',
      alt_label: 'offset',
      keybind: 'z',
      mode: Mode.REPEATS,
      property: 'repeats',
      min: 0,
      max: 15,
      type: 'int',
      alt_mode: Mode.REPEAT_OFFSET,
      alt_property: 'repeat_offset',
      alt_min: 0,
      alt_max: 15,
      alt_type: 'int',
    },
    {
      label: 'time',
      alt_label: 'pace',
      keybind: 'x',
      mode: Mode.REPEAT_TIME,
      property: 'repeat_time',
      list: divisions,
      alt_mode: Mode.REPEAT_PACE,
    },
    {
      label: 'voicing',
      alt_label: 'style',
      keybind: 'c',
      mode: Mode.VOICING,
      property: 'voicing',
      min: 0,
      max: 15,
      type: 'int',
      alt_mode: Mode.STYLE,
      alt_property: 'style',
      alt_list: styles,
    },
    {
      label: 'melody',
      alt_label: 'phrase',
      keybind: 'v',
      mode: Mode.MELODY,
      property: 'melody',
      min: 0,
      max: 1,
      type: 'float',
      alt_mode: Mode.PHRASE,
      alt_property: 'phrase',
      alt_list: phrases,
    },
    {
      label: 'accent',
      alt_label: 'curve',
      keybind: 'b',
      mode: Mode.ACCENT,
      property: 'accent',
      min: 0,
      max: 1,
      type: 'float',
      alt_mode: Mode.ACCENT_CURVE,
      alt_property: 'accent_curve',
      alt_list: accentCurves,
    },
    {
      label: 'timing',
      alt_label: 'delay',
      keybind: 'n',
      mode: Mode.TIMING,
      property: 'timing',
      min: 0,
      max: 1,
      type: 'float',
      alt_mode: Mode.DELAY,
      alt_property: 'delay',
    },
    {
      label: 'scale',
      alt_label: 'root',
      keybind: 'm',
      mode: Mode.SCALE,
      property: 'getScale',
      list: scales,
      alt_mode: Mode.ROOT,
      alt_property: 'root',
      min: 0,
      max: 12,
      type: 'int',
    },
    {
      label: 'midi ch',
      alt_label: '',
      keybind: ',',
      mode: Mode.CHANNEL,
      property: 'channel',
      min: 0,
      max: 16,
      type: 'int',
    },
    {
      label: 'random',
      alt_label: 'rate',
      keybind: '.',
      // 'mode': Mode.RANDOM, 'property': 'random', 'min': 0, 'max': 1, 'type': "float",  # this is gonna be special
      alt_mode: Mode.RANDOM_RATE,
      alt_list: divisions,
    },
  ],
];

export const buttons = [
  [
    ['/1', '', '1'],
    ['/2', '', '2'],
    ['/4', '', '3'],
    ['/8', '', '4'],
    ['/16', '', '5'],
    ['/32', '', '6'],
    ['/64', '', '7'],
    ['', '', '8'],
    [],
    ['play', 'stop', '9', ['play_pause', null]],
    [],
    ['clear', 'copy', '-', ['set_clear', 'release_mode']],
    ['ctrl', '', '=', ['set_control', 'release_control']],
  ],
  [
    ['', 'chrom', 'q'],
    ['', 'major', 'w'],
    ['/3', 'minor', 'e'],
    ['/6', 'melo', 'r'],
    ['/12', 'hex', 't'],
    ['/24', 'aug', 'y'],
    ['/48', 'penta', 'u'],
    ['', 'user', 'i'],
    [],
    ['bank', 'save', 'p', ['set_bank', 'release_mode']],
    ['pattern', 'select', '[', ['set_pattern', 'release_mode']],
    ['temp', 'multi', ']'],
    ['mute', '', '/', ['set_mute', 'release_mode']],
  ],
];

// extract keyMap out for use in UI
export const keyMap: {
  [id: string]: [string, number, number];
} = {};
for (const row of [0, 1]) {
  for (const [i, knob] of knobs[row].entries()) {
    keyMap[knob.keybind] = ['knob', row, i];
  }
  for (const [i, button] of buttons[row].entries()) {
    const kv: string | string[] = button[2];
    if (kv) {
      if (typeof kv === 'string') {
        keyMap[kv] = ['button', row, i];
      } else {
        console.log("what's this", button, kv);
      }
    }
  }
}
