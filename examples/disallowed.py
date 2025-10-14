from music21 import chord, note, stream, tempo
from pychord import Chord as pyChord
from chord_progression_network import Generator
# if author:
import sys
sys.path.append('./src')
from music_bassline_generator.music_bassline_generator import Bassline
# else:
# from music_bassline_generator import Bassline

s = stream.Stream()
bass_part = stream.Part()
chord_part = stream.Part()

def add_notes(p=None, notes=[], type='quarter'):
    for n in notes:
        n = note.Note(n, type=type)
        p.append(n)

weights = [ 1 for _ in range(1,5) ]

g = Generator(
    scale_name='ionian',
    net={
        1: [3,4,5,6],
        2: [],
        3: [1,4,5,6],
        4: [1,3,5,6],
        5: [1,3,4,6],
        6: [1,3,4,5],
        7: [],
    },
    weights={ i: weights for i in range(1,8) },
    chord_map=['','m','m','','','m','m'],
    chord_phrase=True,
)
phrase = g.generate()

bass = Bassline(
    modal=True,
    octave=2,
    tonic=False,
    resolve=False,
    # guitar=True,
)

num = 4

for my_chord in phrase:
    c = pyChord(my_chord)
    c = chord.Chord(c.components(), type='whole')
    chord_part.append(c)
    notes = bass.generate(my_chord, num)
    add_notes(bass_part, notes)

s.append(tempo.MetronomeMark(number=90))
s.insert(0, chord_part)
s.insert(0, bass_part)
s.show('midi')
