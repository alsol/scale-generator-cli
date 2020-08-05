from itertools import cycle
from collections import namedtuple
from enum import Enum

notes = [
    'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
]


class ScaleMode(Enum):
    MAJOR = (2, 2, 1, 2, 2, 2, 1)
    MINOR = (2, 1, 2, 2, 1, 2, 2)


class PentatonicMode(Enum):
    MAJOR = (4, 7)
    MINOR = (2, 6)

    def apply(self, scale):
        return list(note for i, note in enumerate(scale) if i + 1 not in self.value)

    @staticmethod
    def find_by_scale_mode(scale_type: ScaleMode):
        return PentatonicMode.MAJOR if scale_type == ScaleMode.MAJOR else PentatonicMode.MINOR


class ChordMask(Enum):
    MAJOR = ('', 'm', 'm', '', '', 'm', 'dim', '')
    MINOR = ('m', '', '', 'm', 'm', 'dim', '')

    def apply(self, scale):
        for note, chord in zip(scale, self.value):
            yield note + chord

    @staticmethod
    def find_by_scale_mode(scale_type: ScaleMode):
        return ChordMask.MAJOR if scale_type == ScaleMode.MAJOR else ChordMask.MINOR


class NoteIterator:
    def __init__(self, base_note: str):
        if base_note not in notes:
            raise Exception("Unable to find note " + base_note)
        self.__current_index = notes.index(base_note)
        self.current_note = base_note

    def next(self, step=1):
        return self.shift(step=step)

    def __next__(self):
        return self.next()

    def previous(self, step=1):
        return self.shift(-1 * step)

    def shift(self, step=1):
        self.__current_index = (self.__current_index + step) % len(notes)
        self.current_note = notes[self.__current_index]
        return self.current_note

    def __str__(self):
        return self.current_note


def generate_scale(base_note=notes[0], steps: ScaleMode = ScaleMode.MAJOR):
    result = [base_note]

    iterator = NoteIterator(base_note)
    for step in steps.value:
        result.append(iterator.next(step))

    return result


freq_coeff = round(2 ** (1 / float(len(notes))), 7)
def __calculate_freqs():

    root_note = 'A'
    prev_freq = 440

    iterator = NoteIterator(root_note)

    result = {
        root_note: prev_freq
    }

    while True:
        current = iterator.next()
        if current == root_note:
            break

        new_freq = prev_freq * freq_coeff
        result[current] = new_freq
        prev_freq = new_freq

    for key, value in result.items():
        result[key] = round(value, 2)

    return result


if __name__ == "__main__":
    freqs = __calculate_freqs()
    root = 'C'
    print('%s minor: %s' % (root, '   '.join(generate_scale(root, steps=ScaleMode.MINOR))))
    for note, freq in freqs.items():
        print("%3s: %-4d hz" % (note, freq))
    print("%3s: %-4d hz" % ('A', 880))
