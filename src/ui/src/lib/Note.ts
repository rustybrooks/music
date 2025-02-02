const note_list = {
  sharp: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
  flat: ['C', 'DB', 'D', 'EB', 'E', 'F', 'GB', 'G', 'AB', 'A', 'BB', 'B'],
};

export type NoteType = [string, number];

export function note_to_number(n: NoteType): number {
  const [note, octave] = n;
  let i = note_list.sharp.indexOf(note.toUpperCase());
  if (i === -1) {
    i = note_list.flat.indexOf(note.toUpperCase());
  }

  return 36 + octave * 12 + i;
}

export function number_to_note(n: number, is_sharp = false): NoteType {
  return [note_list[is_sharp ? 'sharp' : 'flat'][n % 12], Math.trunc((n - 36) / 12)];
}

export class Note {
  number = 0;
  note: NoteType | null = null;
  is_sharp = true;

  add(i: number) {
    return new Note(this.number + i, this.is_sharp);
  }

  constructor(note: NoteType);
  constructor(num: number, is_sharp: boolean);
  constructor(note: string, octave: number);
  constructor(n: any, is_sharp: any = true) {
    this.is_sharp = is_sharp;
    if (typeof n === 'string') {
      throw Error('What is happening here, why is_sharp');
      // this.number = note_to_number([n, is_sharp]);
    } else if (typeof n === 'number') {
      this.number = n;
      this.note = number_to_note(n, is_sharp);
    } else {
      this.number = note_to_number(n);
      this.note = n;
    }
  }
}
