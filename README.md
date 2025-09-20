# Music Bassline-Generator
Generate musical basslines

## DESCRIPTION

This class generates randomized basslines based on named chords.

The "formula" implemented by this module is basically: "Play any notes of the chord, modal chord scale, or chord-root scale (and drop any notes replaced by extended jazz chords)."

The chords recognized by this module, are those known to `pychord`.

The logic and music theory implemented here, can generate some possibly sour notes. This is an approximate composition tool, and not a drop-in bass player! Import rendered MIDI into a DAW and alter notes until they sound suitable.

Named chords and the `keycenter` use `#` and `b` for accidentals.

To constrain the notes to a chosen set of scale degrees, use the `positions` attribute illustrated below.

The one and only public method in this class is `generate()`.
```python
generate(chord_name='C', n=4, next_chord=None) # defaults
```
This method generates `n` MIDI pitch numbers given a named `chord`. If `format` is set to `ISO`, the method returns named notes. If `next_chord` is `True`, then `generate()` can be called with a `next_chord="Am7"` type argument, and an intersection of the two scales is performed. If the `modal` attribute is set, then the chosen notes will be within the mode given the `keycenter` setting. If it is not set (the default), notes will be chosen as if the key has changed to the current chord.

## SYNOPSIS
```python
from music_bassline_generator import Bassline

bass = Bassline(
    keycenter='C', # tonic for modal accompaniment
    modal=False, # only choose notes within the mode
    chord_notes=True, # use chord notes outside the scale
    intervals=[-3, -2, -1, 1, 2, 3], # allowed voicegen intervals
    context=None, # Scale note number to start the phrase. None=random
    octave=1, # lowest MIDI octave
    tonic=False, # play the first scale note to start the generated phrase
    positions=None, # allowed notes for major and minor scales
    guitar=False, # transpose notes below E1 (midi #28) up an octave
    wrap=None, # transpose notes above this ISO named note, down an octave
    verbose=False, # show progress
)

scale = bass.scale_fn('C7b5') # 'major'
scale = bass.scale_fn('Dm7b5') # 'minor'
scale = bass.scale_fn('D#/A#') # 'major'

notes = bass.generate('C7b5', 4)
notes = bass.generate('D/A', 4)
notes = bass.generate('D', 4, 'C/G')
notes = bass.generate('D', 1)

bass = Bassline(modal=True)
mode = bass.scale_fn('C7b5') # 'ionian'
mode = bass.scale_fn('Dm7b5') # 'dorian'
notes = bass.generate('Dm7')
notes = bass.generate('Dm7b5')

bass = Bassline(
    octave=3,
    wrap='C3',
    modal=True,
)
notes = bass.generate('C', 4)

bass = Bassline(
    chord_notes=False,
    positions={'major': [x for x in range(6)], 'minor': [x for x in range(6)]} # no 7ths!
)
notes = bass.generate('C', 4)
```

## MUSICAL EXAMPLES
```python
from music21 import note, stream
from music_bassline_generator import Bassline

def add_notes(p, notes):
    print(notes)
    for n in notes:
        n = note.Note(n, type='quarter')
        p.append(n)

s = stream.Stream()
bass_part = stream.Part()

bass = Bassline(octave=2)

num = 4

# Autumn Leaves verse
for chord in ['Dm7','G7','CM7','FM7','Bm7b5','E7#9','Am7','D7']:
    notes = bass.generate(chord, num)
    add_notes(bass_part, notes)

s.insert(0, bass_part)

s.show()
```

```python
from music21 import chord, note, stream
from music_bassline_generator import Bassline
from pychord import Chord as pyChord

def add_notes(p, notes):
    for n in notes:
        n = note.Note(n, type='quarter')
        p.append(n)

s = stream.Stream()
bass_part = stream.Part()
chord_part = stream.Part()

bass = Bassline(modal=True, octave=2)

num = 4

# Autumn Leaves
for my_chord in ['Dm7','G7','CM7','FM7','Bm7b5','E7#9','Am7','D7']:
    c = pyChord(my_chord)
    c = chord.Chord(c.components(), type="whole")
    chord_part.append(c)
    notes = bass.generate(my_chord, num)
    add_notes(bass_part, notes)

s.insert(0, chord_part)
s.insert(0, bass_part)

s.show()
```