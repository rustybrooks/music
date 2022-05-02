import { useCallback, useEffect, useMemo, useState } from 'react';
import { useGetAndSet } from 'react-context-hook';
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
  // const [notes, setNotes] = useGetAndSet<NoteThing[]>('visualizerNotes', []);
  const [notes, setNotes] = useState<NoteThing[]>([]);

  const addSequencerEvent = useCallback(
    (event: SequencerEvent) => {
      const newNote = {
        note: new Note(event.message[1], false),
        start: event.tick,
        end: event.tick + 1000,
        id: event.id,
      };
      setNotes(n => [...n, newNote]);
    },
    [notes],
  );

  useEffect(() => {
    if (notes.length) {
      const newNotes = [...notes.filter(note => note.end >= now - 1000)];
      if (notes.length !== newNotes.length) {
        setNotes(newNotes);
      }
      setTimeout(() => setNow(window.performance.now()), 100);
    }
  }, [now, notes]);

  useEffect(() => {
    callbackCallback(addSequencerEvent);
  }, []);

  return (
    <div style={{ textAlign: 'center', padding: '.4rem' }}>
      <svg width="60rem" height="40rem" viewBox="0 0 200 100" version="1.1">
        <rect x="0" y1="0" width="200" height="100" />
        {notes.map(note => {
          const x = calcX(note.note);
          const y = (100 * (now - note.start - startOffset)) / windowMs;
          const height = (100 * (note.end - note.start)) / windowMs;
          return <rect key={note.id} fill="#fff" x={x} y={y} width="1" height={height} />;
        })}
      </svg>
    </div>
  );
}
