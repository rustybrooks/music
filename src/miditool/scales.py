from . import notes
import itertools

scales = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "natural_minor": [2, 1, 2, 2, 1, 2, 2],
    "harmonic_minor": [2, 1, 2, 2, 1, 3, 1],
    "melodic_minor": [2, 1, 2, 2, 2, 2, 1],
    "hungarian_minor, ": [2, 1, 3, 1, 1, 3, 1],
    "neapolitan_minor": [1, 2, 2, 2, 2, 2, 1],
    "neapolitan_major": [1, 2, 2, 2, 2, 2, 1],
    "pentatonic_major": [2, 2, 3, 2, 3, ],
    "pentatonic_minor": [3, 2, 2, 3, 2, ],
    "whole_tone": [2, 2, 2, 2, 2, 2, ],
    "diminished": [2, 1, 2, 1, 2, 1, 2, 1],
    "enigmatic": [1, 3, 2, 2, 2, 1, 1],
    "chromatic": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "ionian": [2, 2, 1, 2, 2, 2, 1],
    "dorian": [2, 1, 2, 2, 2, 1, 2],
    "phrygian": [1, 2, 2, 2, 1, 2, 2],
    "lydian": [2, 2, 2, 1, 2, 2, 1],
    "mixolydian": [2, 2, 1, 2, 2, 1, 2],
    "aeolian": [2, 1, 2, 2, 1, 2, 2],
    "aeoliant": [1, 2, 2, 1, 2, 2, 2],
    "hexatonic": [2, 2, 2, 2, 2, 2],
    "augmented": [3, 1, 3, 1, 3],
}


def get_scale_numbers(root, scale_type, octaves=1):
    offsets = list(itertools.accumulate(scales[scale_type][:-1]))
    print("offsets", offsets)
    out = []
    for o in range(octaves):
        out.append(root + o*12)
        for offset in offsets:
            out.append(root+offset + o*12)

    return out
