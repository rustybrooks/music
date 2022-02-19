import { accentCurves, divisions, phrases, scales, styles } from '../../lib/sequencers/TorsoConstants';

const MODE_TRACKS = 'tracks';
const MODE_PATTERNS = 'patterns';
const MODE_SAVE = 'save';
const MODE_BANKS = 'banks';
const MODE_SELECT = 'select';
const MODE_TEMP = 'temp';
const MODE_MULTI = 'multi';
const MODE_CLEAR = 'clear';
const MODE_COPY = 'copy';

const MODE_STEPS = 'steps';
const MODE_MANUAL_STEPS = 'manual_steps';
const MODE_PULSES = 'pulses';
const MODE_ROTATE = 'rotate';
const MODE_CYCLES = 'cycles';
const MODE_DIVISION = 'division';
const MODE_VELOCITY = 'velocity';
const MODE_SUSTAIN = 'sustain';
const MODE_PITCH = 'pitch';
const MODE_HARMONY = 'harmony';
const MODE_MUTE = 'mute';
const MODE_REPEATS = 'repeats';
const MODE_REPEAT_OFFSET = 'repeat_offset';
const MODE_REPEAT_TIME = 'repeat_time';
const MODE_REPEAT_PACE = 'repeat_pace';
const MODE_VOICING = 'voicing';
const MODE_MELODY = 'melody';
const MODE_PHRASE = 'phrase';
const MODE_ACCENT = 'accent';
const MODE_ACCENT_CURVE = 'accent_curve';
const MODE_STYLE = 'style';
const MODE_SCALE = 'scale';
const MODE_ROOT = 'root';
const MODE_LENGTH = 'length';
const MODE_QUANTIZE = 'quantize';
const MODE_TIMING = 'timing';
const MODE_DELAY = 'delay';
const MODE_RANDOM = 'random';
const MODE_RANDOM_RATE = 'random_rate';
const MODE_TEMPO = 'tempo';
const MODE_CHANNEL = 'channel';

const MAX_PULSE = 64;

export const knobs = [
  [
    {
      label: 'steps',
      alt_label: '',
      keybind: 'a',
      mode: MODE_STEPS,
      property: 'steps',
      min: 1,
      max: 'MAX_STEPS',
      type: 'int',
      alt_mode: MODE_MANUAL_STEPS,
      alt_property: 'manual_steps',
      alt_suppress_dial: true,
    },
    {
      label: 'pulses',
      alt_label: 'rotate',
      keybind: 's',
      mode: MODE_PULSES,
      property: 'pulses',
      min: 1,
      max: 'MAX_STEPS',
      type: 'int',
      alt_mode: MODE_ROTATE,
      alt_property: 'rotate',
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
      mode: MODE_DIVISION,
      property: 'division',
      list: divisions,
    },
    {
      label: 'velocity',
      alt_label: '',
      keybind: 'g',
      mode: MODE_VELOCITY,
      property: 'velocity',
      min: 0,
      max: 127,
      type: 'int',
    },
    {
      label: 'sustain',
      alt_label: '',
      keybind: 'h',
      mode: MODE_SUSTAIN,
      property: 'sustain',
      min: 0,
      max: 1,
      type: 'float',
    },

    {
      label: 'pitch',
      alt_label: 'harmony',
      keybind: 'j',
      mode: MODE_PITCH,
      property: 'pitch',
      min: -36,
      max: 36,
      type: 'int',
      alt_mode: MODE_HARMONY,
      alt_property: 'harmony', // FIXME min/max etc?
    },
    {
      keybind: 'k',
      mode: MODE_LENGTH,
      label: 'length',
      alt_mode: MODE_QUANTIZE,
      alt_label: 'quantize',
    },
    {
      label: 'tempo',
      alt_label: '',
      keybind: 'l',
      mode: MODE_TEMPO,
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
      mode: MODE_REPEATS,
      property: 'repeats',
      min: 0,
      max: 15,
      type: 'int',
      alt_mode: MODE_REPEAT_OFFSET,
      alt_property: 'repeat_offset',
      alt_min: 0,
      alt_max: 15,
      alt_type: 'int',
    },
    {
      label: 'time',
      alt_label: 'pace',
      keybind: 'x',
      mode: MODE_REPEAT_TIME,
      property: 'repeat_time',
      list: divisions,
      alt_mode: MODE_REPEAT_PACE,
    },
    {
      label: 'voicing',
      alt_label: 'style',
      keybind: 'c',
      mode: MODE_VOICING,
      property: 'voicing',
      min: 0,
      max: 15,
      type: 'int',
      alt_mode: MODE_STYLE,
      alt_property: 'style',
      alt_list: styles,
    },
    {
      label: 'melody',
      alt_label: 'phrase',
      keybind: 'v',
      mode: MODE_MELODY,
      property: 'melody',
      min: 0,
      max: 1,
      type: 'float',
      alt_mode: MODE_PHRASE,
      alt_property: 'phrase',
      alt_list: phrases,
    },
    {
      label: 'accent',
      alt_label: 'curve',
      keybind: 'b',
      mode: MODE_ACCENT,
      property: 'accent',
      min: 0,
      max: 1,
      type: 'float',
      alt_mode: MODE_ACCENT_CURVE,
      alt_property: 'accent_curve',
      alt_list: accentCurves,
    },
    {
      label: 'timing',
      alt_label: 'delay',
      keybind: 'n',
      mode: MODE_TIMING,
      property: 'timing',
      min: 0,
      max: 1,
      type: 'float',
      alt_mode: MODE_DELAY,
      alt_property: 'delay',
    },
    {
      label: 'scale',
      alt_label: 'root',
      keybind: 'm',
      mode: MODE_SCALE,
      property: 'scale',
      list: scales,
      alt_mode: MODE_ROOT,
      alt_property: 'root',
      min: 0,
      max: 12,
      type: 'int',
    },
    {
      label: 'midi ch',
      alt_label: '',
      keybind: 'comma',
      mode: MODE_CHANNEL,
      property: 'channel',
      min: 0,
      max: 16,
      type: 'int',
    },
    {
      label: 'random',
      alt_label: 'rate',
      keybind: 'period',
      // 'mode': MODE_RANDOM, 'property': 'random', 'min': 0, 'max': 1, 'type': "float",  # this is gonna be special
      alt_mode: MODE_RANDOM_RATE,
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
    null,
    ['play', 'stop', '9', ['play_pause', null]],
    [null, null, null],
    ['clear', 'copy', 'minus', ['set_clear', 'release_mode']],
    ['ctrl', '', 'equal', ['set_control', 'release_control']],
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
    null,
    ['bank', 'save', 'p', ['set_bank', 'release_mode']],
    ['pattern', 'select', 'bracketleft', ['set_pattern', 'release_mode']],
    ['temp', 'multi', 'bracketright'],
    ['mute', '', 'backslash', ['set_mute', 'release_mode']],
  ],
];
