from music21 import chord, note, stream, tempo
from pychord import Chord as pyChord
try:
    import sys
    sys.path.append('./src')
    from music_bassline_generator.music_bassline_generator import Bassline
except ImportError:
    from music_bassline_generator import Bassline

s = stream.Stream()
bass_part = stream.Part()
chord_part = stream.Part()

bass = Bassline(
    modal=True,
    octave=2,
    tonic=False,
    resolve=False,
    guitar=True,
)

for my_chord in ['C','G','Am','F']:
    c = pyChord(my_chord)
    c = chord.Chord(c.components(), type='whole')
    chord_part.append(c)
    notes = bass.generate(my_chord, 4)
    for n in notes:
        n = note.Note(n, type='quarter')
        bass_part.append(n)

s.append(tempo.MetronomeMark(number=90))
s.insert(0, chord_part)
s.insert(0, bass_part)
s.show('midi')
