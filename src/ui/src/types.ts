const NOTEON = 'NoteOn';
const NOTEOFF = 'NoteOff';

export class MidiMessage {
  note: any = null;
  command: any = null;
  channel: any = null;
  velocity: any = null;

  constructor(m: MidiMessageType) {
    const [b1, b2, b3] = m.data;

    // eslint-disable-next-line no-bitwise
    const mevent = b1 >> 4;

    console.log('mevent', mevent);
    switch (mevent) {
      case 0x9:
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
        this.command = mevent; // Should probably just throw exception
    }

    console.log(mevent, b1, this.channel, this.note, this.velocity, this.command);
  }
}

export interface MidiCallback {
  (message: MidiMessage): void;
}

export interface MidiInputs {
  [id: number]: any;
}

export interface MidiOutputs {
  [id: number]: any;
}

export interface CallbackMap {
  [id: number]: { [id: number]: MidiCallback };
}

export interface MidiMessageType {
  data: number[];
}
