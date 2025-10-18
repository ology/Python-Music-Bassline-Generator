from music21 import note, chord, scale, pitch
from music_voicegen import MusicVoiceGen
from pychord import Chord as pyChord
import random
import re

class Bassline:
    E1 = 28  # lowest note on a bass guitar in standard tuning (MIDI)

    def __init__(
        self,
        keycenter='C',
        octave=1,
        modal=False,
        chord_notes=True,
        intervals=None,
        scale_fn=None,
        tonic=False,
        resolve=False,
        positions=None,
        guitar=False,
        wrap=None,
        format='midinum', # or 'ISO'
        context=None,
        verbose=False,
    ):
        self.guitar = guitar
        self.wrap = wrap
        self.modal = modal
        self.chord_notes = chord_notes
        self.keycenter = keycenter
        self.octave = octave
        self.intervals = intervals if intervals is not None else [-7, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 7]
        self.scale_fn = scale_fn if scale_fn is not None else self._default_scale_fn()
        self.tonic = tonic
        self.resolve = resolve
        self.positions = positions
        self.format = format
        self.context = context
        self.verbose = verbose

    def _default_scale_fn(self):
        if self.modal:
            def fn(chord_name):
                chord_note, _ = self._parse_chord(chord_name)
                modes = [
                    'ionian', 'dorian', 'phrygian', 'lydian',
                    'mixolydian', 'aeolian', 'locrian'
                ]
                key_scale = scale.MajorScale(self.keycenter)
                key_notes = [str(p)[:-1] for p in key_scale.getPitches(self.keycenter + '3')]
                try:
                    position = key_notes.index(chord_note)
                except ValueError:
                    position = 0
                return modes[position]
            return fn
        else:
            def fn(chord_name):
                if chord_name and chord_name[1:2] == 'm':
                    return 'minor'
                return 'major'
            return fn

    def generate(self, chord_name='C', n=4, next_chord=None):
        if '/' in chord_name:
            chord_name = chord_name.split('/')[0] # XXX NO
        chord_note, flavor = self._parse_chord(chord_name)
        next_chord_note = None
        if next_chord:
            next_chord_note, _ = self._parse_chord(next_chord)

        if self.verbose:
            print(f"CHORD: {chord_name} => {chord_note}, {flavor}")
 
        scale_name = self.scale_fn(chord_name)
        next_scale_name = self.scale_fn(next_chord) if next_chord else None

        if self.verbose:
            print(f"NEXT: {next_chord} => {next_chord_note} {next_scale_name}")

        my_chord = pyChord(chord_name)
        chord_obj = chord.Chord([ c + str(self.octave) for c in my_chord.components() ])
        notes = [self._pitchnum(n) for n in chord_obj.pitches]

        pitches = []
        if self.positions and scale_name:
            scale_obj = self._get_scale_obj(chord_note, scale_name)
            scale_pitches = [self._pitchnum(p) for p in scale_obj.getPitches(chord_note + str(self.octave), chord_note + str(self.octave + 1))]
            # print('N:',chord_note,'S:',scale_name,'O:',scale_obj,'P:',scale_pitches)
            for idx, p in enumerate(scale_pitches):
                if idx in self.positions.get(scale_name, []):
                    pitches.append(p)
        elif scale_name:
            scale_obj = self._get_scale_obj(chord_note, scale_name)
            pitches = [self._pitchnum(p) for p in scale_obj.getPitches(chord_note + str(self.octave), chord_note + str(self.octave + 1))]
        else:
            pitches = []

        next_pitches = []
        if next_scale_name and next_chord_note:
            next_scale_obj = self._get_scale_obj(next_chord_note, next_scale_name)
            next_pitches = [self._pitchnum(p) for p in next_scale_obj.getPitches(next_chord_note + str(self.octave), next_chord_note + str(self.octave + 1))]

        if self.verbose:
            print("NEXT PITCHES:", next_pitches)

        # Add unique chord notes to the pitches
        if self.chord_notes:
            if self.verbose:
                print("CHORD NOTES")
            for n1 in notes:
                if n1 not in pitches:
                    pitches.append(n1)
                    if self.verbose:
                        print(f"\tADD: {self._pitchname(n1)}")

        pitches = sorted(set(pitches))

        # Remove certain notes based on chord flavor
        tones = self._get_scale_tones(chord_note, scale_name)
        if self.verbose:
            print(f"\t{scale_name} SCALE: {tones}")
        fixed = []
        for p in pitches:
            n1 = note.Note()
            n1.pitch.midi = p
            x = n1.pitch.nameWithOctave[:-1]
            y = n1.pitch.getEnharmonic().nameWithOctave[:-1]
            if (
                ('#5' in flavor or 'b5' in flavor) and len(tones) > 4 and (x == tones[4] or y == tones[4])
            ) or (
                '7' in flavor and 'M7' not in flavor and 'm7' not in flavor and len(tones) > 6 and (x == tones[6] or y == tones[6])
            ) or (
                ('#9' in flavor or 'b9' in flavor) and len(tones) > 1 and (x == tones[1] or y == tones[1])
            ) or (
                'dim' in flavor and len(tones) > 2 and (x == tones[2] or y == tones[2])
            ) or (
                'dim' in flavor and len(tones) > 6 and (x == tones[6] or y == tones[6])
            ) or (
                'aug' in flavor and len(tones) > 6 and (x == tones[6] or y == tones[6])
            ):
                if self.verbose:
                    print(f"\tDROP: {x}")
                continue
            fixed.append(p)

        if self.guitar:
            fixed = sorted([p + 12 if p < self.E1 else p for p in fixed])

        if self.wrap:
            wrap_midi = note.Note(self.wrap).pitch.midi
            # fixed = sorted([p - 12 if p > wrap_midi else p for p in fixed])
            temp = []
            for p in fixed:
                if p > wrap_midi:
                    diff = p - wrap_midi
                    factor = 12
                    num = diff // factor
                    x = p - (factor * (num + 1))
                    temp.append(x)
            fixed = sorted(temp)

        fixed = sorted(fixed)
        if self.verbose:
            self._verbose_notes('NOTES', fixed)

        chosen = []
        if len(fixed) > 1:
            try:
                voice = MusicVoiceGen(pitches=fixed, intervals=self.intervals)
                if not self.context:
                    voice.context([random.choice(fixed)])
                else:
                    voice.context(self.context)
                chosen = [voice.rand() for _ in range(n)]
            except Exception:
                chosen = [fixed[0]] * n
        else:
            chosen = [fixed[0]] * n

        if self.tonic:
            chosen[0] = fixed[0]
        if self.resolve:
            chosen[-1] = fixed[0]

        if next_chord and next_pitches:
            intersect = list(set(fixed) & set(next_pitches))
            if self.verbose:
                self._verbose_notes('INTERSECT', intersect)
            if intersect:
                closest = self._closest(chosen[-2] if len(chosen) > 1 else chosen[-1], intersect)
                if closest is not None:
                    chosen[-1] = closest

        if self.verbose:
            self._verbose_notes('CHOSEN', chosen)

        if self.format == 'ISO':
            chosen = [ self._pitchname(n) for n in chosen ]
        return chosen

    def _parse_chord(self, chord_name):
        m = re.match(r'^([A-G][#b]?)(.*)$', chord_name)
        if m:
            return m.group(1), m.group(2)
        return chord_name, ''

    def _pitchnum(self, p):
        if isinstance(p, pitch.Pitch):
            return p.midi
        elif isinstance(p, str):
            return note.Note(p).pitch.midi
        elif isinstance(p, note.Note):
            return p.pitch.midi
        return int(p)

    def _pitchname(self, midi_num):
        return note.Note(midi_num).pitch.nameWithOctave

    def _get_scale_obj(self, tonic, scale_name):
        scale_map = {
            'major': scale.MajorScale,
            'minor': scale.MinorScale,
            'ionian': scale.MajorScale,
            'dorian': scale.DorianScale,
            'phrygian': scale.PhrygianScale,
            'lydian': scale.LydianScale,
            'mixolydian': scale.MixolydianScale,
            'aeolian': scale.MinorScale,
            'locrian': scale.LocrianScale,
            'chromatic': scale.ChromaticScale,
        }
        cls = scale_map.get(scale_name.lower(), scale.MajorScale)
        return cls(tonic)

    def _get_scale_tones(self, tonic, scale_name):
        try:
            sc = self._get_scale_obj(tonic, scale_name)
            return [str(p)[:-1] for p in sc.getPitches(tonic + '3')]
        except Exception:
            return []

    def _verbose_notes(self, title, notes):
        names = [self._pitchname(n) for n in notes]
        print(f"\t{title}: {names}")

    def _closest(self, key, lst):
        lst = [x for x in lst if x != key]
        if not lst:
            return None
        diffs = [abs(key - x) for x in lst]
        min_diff = min(diffs)
        closest = [lst[i] for i, d in enumerate(diffs) if d == min_diff]
        return random.choice(closest)
