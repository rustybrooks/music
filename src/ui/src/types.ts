const NOTEON = 'NoteOn';
const NOTEOFF = 'NoteOff';

export class MidiMessage {
  note: number | null = null;
  command: string | null = null;
  channel: number | null = null;
  velocity: number | null = null;

  constructor(m: MidiMessageType) {
    const [b1, b2, b3] = m.data;

    // eslint-disable-next-line no-bitwise
    const mevent = b1 >> 4;

    switch (mevent) {
      case 0x9:
        // eslint-disable-next-line no-bitwise
        this.channel = b1 & 0xf;
        this.note = b2;
        this.velocity = b3;
        if (this.velocity > 0) {
          this.command = NOTEON;
          this.note = b2;
        } else {
          this.command = NOTEOFF;
        }
        break;
      case 0x8:
        // eslint-disable-next-line no-bitwise
        this.channel = b1 & 0xf;
        this.note = b2;
        this.velocity = b3;
        this.command = NOTEOFF;
        break;
      case 0xa:
        // Polyphonic Key Pressure (Aftertouch)
        break;
      case 0xb:
        // Control Change
        break;
      case 0xc:
        // Program Change
        break;
      case 0xd:
        // Channel Pressure (Aftertouch)
        break;
      case 0xe:
        // Pitch Wheel
        break;
      default:
        throw Error(`Unknown midi event: message=${m} event=${mevent}`);
      // this.command = mevent; // Should probably just throw exception
    }
  }
}

export interface MidiCallback {
  (message: MidiMessage): void;
}

export type MidiInput = {
  connection: string;
  id: string;
  manufacturer: string;
  name: string;
  onmidimessage: any;
  onstatechange: any;
  state: string;
  type: string;
  version: string;
};

export interface MidiInputs {
  [id: string]: MidiInput;
}

export type MidiOutput = {
  connection: string;
  id: string;
  manufacturer: string;
  name: string;
  onmidimessage: any;
  onstatechange: any;
  state: string;
  type: string;
  version: string;
  object: WebMidi.MIDIOutput;
};

export interface MidiOutputs {
  [id: string]: MidiOutput;
}

export interface CallbackMap {
  [id: string]: { [id: string]: MidiCallback };
}

export interface MidiMessageType {
  data: number[];
}
