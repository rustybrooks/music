import { useCallback, useEffect, useState } from 'react';
import { Note } from '../../lib/Note';
import { SequencerEvent } from '../../lib/sequencers/Torso';

interface NoteThing {
  note: Note;
  start: number;
  end: number;
  id: number;
}

function calcX(note: Note) {
  return (200 * (note.number - 24)) / (8 * 12);
}

export function MidiVisualizer({ windowMs = 5000, callbackCallback = null }: { windowMs?: number; callbackCallback: any }) {
  const [now, setNow] = useState(window.performance.now());
  const [notes, setNotes] = useState<{ [id: number]: NoteThing }>({});

  const addSequencerEvent = useCallback(
    (events: SequencerEvent[]) => {
      const newNotes: typeof notes = {};
      for (const event of events) {
        let newNote: NoteThing;
        if (event.startId === null) {
          newNote = {
            note: new Note(event.message[1], false),
            start: event.tick,
            end: event.tick + 1e6,
            id: event.id,
          };
          newNotes[event.id] = newNote;
        } else {
          newNote = newNotes[event.startId];
          newNote.end = event.tick;
        }
      }

      setNotes(n => ({ ...n, ...newNotes }));
    },
    [notes],
  );

  useEffect(() => {
    if (Object.keys(notes).length) {
      const newNotes = Object.fromEntries(Object.entries(notes).filter(entry => entry[1].end >= now - windowMs));
      if (Object.keys(notes).length !== Object.keys(newNotes).length) {
        setNotes(newNotes);
      }
      setTimeout(() => setNow(window.performance.now()), 50);
    }
  }, [now, notes]);

  useEffect(() => {
    callbackCallback(addSequencerEvent);
  }, [addSequencerEvent]);

  return (
    <div style={{ textAlign: 'center', padding: '.4rem' }}>
      <svg width="50rem" height="25rem" viewBox="0 0 200 100" version="1.1">
        <rect x="0" y1="0" width="200" height="100" />
        {Object.values(notes).map(note => {
          const height = (100 * (note.end - note.start)) / windowMs;
          const x = calcX(note.note);
          const y = (100 * (now - note.start - height)) / windowMs;
          return <rect key={note.id} fill="#fff" x={x} y={y} width="1" height={height} />;
        })}
      </svg>
    </div>
  );
}
