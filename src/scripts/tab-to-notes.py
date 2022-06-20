#!/usr/bin/env python

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)

import argparse
from miditool import notes

root = [['E', 0], ['A', 1], ['D', 1], ['G', 1], ['B', 2], ['E', 2]]
root_numbers = [notes.note_to_number(x) for x in root]


def decode(t):
    out = []
    for i, num in enumerate(t):
        num = num.lower()
        if num == 'x':
            pass
        else:
            note = root_numbers[i] + int(num)
            out.append(notes.number_to_note(note))

    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('tab', nargs='*')
    options = parser.parse_args()

    for tab in options.tab:
        print(decode(tab))