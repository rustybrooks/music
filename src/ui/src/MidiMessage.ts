interface MidiMessageType {
  data: number[],
};

const NOTEON = 'NoteOn'
const NOTEOFF = 'NoteOff'

class MidiMessage {

  note : any = null;
  command : any = null;
  channel : any = null;
  velocity : any = null;

  constructor(m : MidiMessageType) {
    const [b1, b2, b3] = m.data

    const mevent = b1 >> 4

    console.log("mevent", mevent)
    switch (mevent) {
      case 0x9:
        this.channel = b1 & 0xF
        this.note = b2
        this.velocity = b3
        if (this.velocity > 0) {
          this.command = NOTEON
          this.note = b2
        } else {
          this.command = NOTEOFF
        }
        break
      case 0x8:
        this.channel = b1 & 0xF
        this.note = b2
        this.velocity = b3
        this.command = NOTEOFF
        break
      case 0xA:
        // Polyphonic Key Pressure (Aftertouch)
        break
      case 0xB:
        // Control Change
        break
      case 0xC:
        // Program Change
        break
      case 0xD:
        // Channel Pressure (Aftertouch)
        break
      case 0xE:
        // Pitch Wheel
        break
      default:
        this.command = mevent  // Should probably just throw exception
    }

    console.log(mevent, b1, this.channel, this.note, this.velocity, this.command)
  }
}

export default MidiMessage

