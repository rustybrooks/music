note_list = {
    "sharp": ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
    "flat": ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
}


def notestr_to_number(n):
    nl = [n[:-1], int(n[-1])]
    print(f"notestr {n} - {nl}")
    return note_to_number(nl)


def note_to_number(n):
    if isinstance(n, int):
        return n

    note, octave = n
    i = note_list['sharp'].index(note.upper())
    if i == -1:
        i = note_list['flat'].index(note.upper())

    return 36 + octave*12 + i


def number_to_note(n, is_sharp=True):
    return [note_list['sharp' if is_sharp else 'flat'][n % 12], (n-36) // 12]
