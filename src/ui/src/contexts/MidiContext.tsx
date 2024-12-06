import React from 'react';
import { CallbackMap, MidiInputs, MidiOutputs } from '../types';

export type MidiContextType = {
  midiInputs: MidiInputs;
  midiOutputs: MidiOutputs;
  midiAccess: WebMidi.MIDIAccess | null;
  midiCallbackMap: CallbackMap;
};

export const MidiContext = React.createContext<MidiContextType>({
  midiInputs: {},
  midiOutputs: {},
  midiAccess: null,
  midiCallbackMap: {},
});
