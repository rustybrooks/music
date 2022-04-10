import { Note } from '../Note';
import { NOTE_ON } from '../sequencers/TorsoConstants';
import { noteFreq } from './utils';

const audioContext = new window.AudioContext();

const mainGainNode = audioContext.createGain();
mainGainNode.connect(audioContext.destination);
mainGainNode.gain.value = 1;

const notes: { [id: number]: OscillatorNode } = {};

export async function startNote(note: Note, type: OscillatorType) {
  const osc = audioContext.createOscillator();
  osc.connect(mainGainNode);
  osc.type = type;
  osc.frequency.value = noteFreq[note.number];
  osc.start();
  notes[note.number] = osc;
}

export async function stopNote(note: Note) {
  if (!notes[note.number]) return;
  notes[note.number].stop();
}

export function synthMidiMessage(event: number[], tick: number) {
  const [type, note, velocity] = event;
  let cmd;
  if (type >= NOTE_ON && type < NOTE_ON + 16) {
    cmd = () => startNote(new Note(note, false), 'triangle');
  } else {
    cmd = () => stopNote(new Note(note, false));
  }

  setTimeout(cmd, tick - window.performance.now());
}
