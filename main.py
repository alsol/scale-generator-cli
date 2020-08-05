#!/usr/bin/env python3

import json
from enum import Enum
from recordtype import recordtype
from typing import Tuple
from notes import NoteIterator
from notes import generate_scale
from notes import ScaleMode, PentatonicMode, ChordMask

Tuning = recordtype("Tuning", "strings drop notes bias title")


class Color(Enum):
    Black = '\033[30m'
    Red = '\033[31m'
    Green = '\033[32m'
    Brown = '\033[33m'
    Blue = '\033[34m'
    Purple = '\033[35m'
    Cyan = '\033[36m'
    Gray = '\033[37m'
    NC = '\033[0m'

    def wrap(self, value: str):
        return self.value + value + Color.NC.value


def generate_tuning_title(tuning: Tuning) -> str:
    if tuning.drop or tuning.bias != 0:
        base_title = ("drop " if tuning.drop else "") + tuning.notes[-1].upper()
    else:
        base_title = "standard"
    return ((str(tuning.strings) if tuning.strings > 6 else "") + " " + base_title).strip()


def render_fingerboard(tuning: Tuning,
                       scale_title: str,
                       scale: Tuple[str],
                       pentatonic: Tuple[str] = None,
                       chords: Tuple[str] = None):
    print("           Tuning: %-19s (%s)" % (" ".join(tuning.notes), tuning.title))
    print("    Current scale: %-19s (%s)" % (" ".join(current_scale), scale_title))
    if pentatonic:
        print("       Pentatonic: %-19s (%s)" % (" ".join(pentatonic), scale_title))
    if chords:
        print("Chord progression: %s\n" % " ".join(chords))

    scale_mask = set(pentatonic) if pentatonic else scale
    tone = scale[0]

    note_range = range(24)

    for note in tuning.notes:
        print("%s||" % (note if note in scale else ' '), end='')

        note_iter = NoteIterator(note)
        for _ in note_range:
            next_note = note_iter.next()
            color = Color.Red if next_note == tone else Color.NC
            next_note = next_note if next_note in scale_mask else ' '
            print((color.wrap('%-3s') + '|') % next_note, end='')

        print(" - ")

    print(" ||", end='')
    for i in note_range:
        print("%-3d|" % (i + 1), end='')
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Scale generator')
    parser.add_argument('--strings', '-s', default=6, type=int,
                        help="number of guitar strings on the fretboard")
    parser.add_argument('--bias', '-b', default=0, type=int, help='bias over the standard tone')
    parser.add_argument('--drop', '-d', default=False, type=bool, help='use "drop" tuning')
    parser.add_argument('--tone', '-t', type=str, required=True, help="base tone for scale")
    parser.add_argument('--mode', '-m', type=str, default=ScaleMode.MAJOR.name.lower(), help="")
    parser.add_argument('--pentatonic', '-p', type=bool, default=False, help="render scale in pentatonic mode")
    args = parser.parse_args()

    tone = args.tone
    mode = args.mode.lower()
    if mode == 'major':
        mode = ScaleMode.MAJOR
    elif mode == 'minor':
        mode = ScaleMode.MINOR
    else:
        raise Exception("Unknown scale mode: " + args.mode)

    tuning = Tuning(strings=args.strings, bias=args.bias, drop=args.drop, notes=[], title="standard")

    with open("tunings.json", 'r') as json_tuning:
        default_notes = json.load(json_tuning)["standard"]
        tuning.notes = [default_notes[index % len(default_notes)] for index in range(tuning.strings)]
        tuning.notes = [NoteIterator(note).shift(tuning.bias * 2) for note in tuning.notes]
        if tuning.drop:
            tuning.notes[-1] = NoteIterator(tuning.notes[-1]).previous(2)
        tuning.title = generate_tuning_title(tuning)

    current_scale = generate_scale(tone, steps=mode)
    pentatonic = PentatonicMode.find_by_scale_mode(mode).apply(current_scale) if args.pentatonic else None
    chords = ChordMask.find_by_scale_mode(mode).apply(current_scale)

    render_fingerboard(tuning, current_scale[0] + " " + mode.name.capitalize(), current_scale, pentatonic, chords)
