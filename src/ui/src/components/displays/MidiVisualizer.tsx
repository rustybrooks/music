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
  return (200 * note.number) / (8 * 12);
}

export function MidiVisualizer({
  startOffset = null,
  windowMs = 5000,
  callbackCallback = null,
}: {
  startOffset?: number;
  windowMs?: number;
  callbackCallback: any;
}) {
  const [now, setNow] = useState(window.performance.now());
  const [notes, setNotes] = useState<NoteThing[]>([]);

  const addSequencerEvent = (event: SequencerEvent) => {
    console.log('new seq event', event);
  };

  useEffect(() => {
    setTimeout(() => setNow(window.performance.now()), 50);
  }, [now]);

  useEffect(() => {
    callbackCallback(addSequencerEvent);
  }, []);

  return (
    <div style={{ textAlign: 'center', padding: '.4rem' }}>
      <svg width="80rem" height="40rem" viewBox="0 0 200 100" version="1.1">
        <rect x="0" y1="0" width="200" height="100" />
        {notes.map(note => {
          return (
            <rect
              key={note.id}
              fill="#fff"
              x={calcX(note.note)}
              y={(100 * (now - note.start - startOffset)) / windowMs}
              width="1"
              height={(100 * (note.end - note.start)) / windowMs}
            />
          );
        })}
      </svg>
    </div>
  );
}
