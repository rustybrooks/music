import { Note } from '../Note';
import { NOTE_ON } from '../sequencers/TorsoConstants';
import { noteFreq } from './utils';

export const audioContext = new window.AudioContext();

const mainGainNode = audioContext.createGain();
mainGainNode.connect(audioContext.destination);
mainGainNode.gain.value = 1 / 8;

const notes: { [id: number]: OscillatorNode } = {};

export async function startNote(note: Note, _velocity: number, type: OscillatorType, when = 0) {
  const osc = audioContext.createOscillator();
  osc.connect(mainGainNode);
  osc.type = type;
  osc.frequency.value = noteFreq[note.number];
  osc.start(when);
  notes[note.number] = osc;
}

export async function stopNote(note: Note, when: number = 0) {
  if (!notes[note.number]) return;
  notes[note.number].stop(when);
}

export function synthMidiMessage(event: number[], tick: number) {
  const [type, note, velocity] = event;
  if (type >= NOTE_ON && type < NOTE_ON + 16) {
    startNote(new Note(note, false), velocity, 'triangle', tick);
  } else {
    stopNote(new Note(note, false), tick);
  }
}

startNote(new Note(65, false), 0, 'triangle');
stopNote(new Note(65, false), 0);
