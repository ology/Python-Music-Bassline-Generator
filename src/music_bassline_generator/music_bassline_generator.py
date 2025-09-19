from itertools import permutations
from music21 import note, pitch
import random
import re

class Bassline:
    E1 = 28  # lowest note on a bass guitar in standard tuning

    def __init__(
        self,
        guitar=False,
        wrap=0,
        modal=False,
        chord_notes=True,
        keycenter='C',
        intervals=None,
        octave=1,
        scale=None,
        tonic=False,
        positions=None,
        verbose=False,
    ):
        self.guitar = bool(guitar)
        self.wrap = wrap
        self.modal = bool(modal)
        self.chord_notes = bool(chord_notes)
        self.keycenter = keycenter
        self.intervals = intervals if intervals is not None else [-3, -2, -1, 1, 2, 3]
        self.octave = octave
        self.scale = scale if scale else self._build_scale()
        self.tonic = bool(tonic)
        self.positions = positions
        self.verbose = bool(verbose)

    def _build_scale(self):
        if self.modal:
            def scale_func(chord):
                chord_note, _ = self._parse_chord(chord)
                modes = ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
                key_notes = get_scale_notes(self.keycenter, modes[0])
                try:
                    position = key_notes.index(chord_note)
                except ValueError:
                    position = 0
                scale = modes[position] if position >= 0 else modes[0]
                return scale
            return scale_func
        else:
            def scale_func(chord):
                import re
                return 'minor' if re.match(r'^[A-G][#b]?m', chord) else 'major'
            return scale_func

    def generate(self, chord=None, num=4, next_chord=None):
        chord = chord or 'C'
        num = num or 4

        if '/' in chord:
            chord = chord.split('/')[0]
        chord_note, flavor = self._parse_chord(chord)
        next_chord_note = None
        if next_chord:
            next_chord_note, _ = self._parse_chord(next_chord)

        if self.verbose:
            print(f"CHORD: {chord} => {chord_note}, {flavor}")
            if next_chord:
                print(f"NEXT: {next_chord} => {next_chord_note}")

        scale = self.scale(chord)
        next_scale = self.scale(next_chord) if next_chord else ''

        notes = [self.pitchnum(n) for n in chord_with_octave(chord, self.octave)]

        pitches = []
        if self.positions and scale:
            scale_notes = get_scale_MIDI(chord_note, self.octave, scale)
            for n, midi in enumerate(scale_notes):
                if n in self.positions.get(scale, []):
                    pitches.append(midi)
        elif scale:
            pitches = get_scale_MIDI(chord_note, self.octave, scale)
        else:
            pitches = []

        next_pitches = get_scale_MIDI(next_chord_note, self.octave, next_scale) if next_scale else []

        # Add unique chord notes to the pitches
        if self.chord_notes:
            if self.verbose:
                print("CHORD NOTES")
            for n in notes:
                if n not in pitches:
                    pitches.append(n)
                    if self.verbose:
                        x = self.pitchname(n)
                        print(f"\tADD: {x}")

        pitches = sorted(set(pitches))

        # Determine if we should skip certain notes given the chord flavor
        tones = get_scale_notes(chord_note, scale)
        if self.verbose:
            print(f"\t{scale} SCALE: {tones}")
        fixed = []
        for p in pitches:
            n = Note(p, 'midinum')
            x = n.format('isobase')
            # Inspect both # & b
            if '#' in x:
                n.en_eq('flat')
            elif 'b' in x:
                n.en_eq('sharp')
            y = n.format('isobase')
            if (
                ('#5' in flavor or 'b5' in flavor) and len(tones) > 4 and (x == tones[4] or y == tones[4])
                or ('7' in flavor and 'M7' not in flavor and 'm7' not in flavor and len(tones) > 6 and (x == tones[6] or y == tones[6]))
                or (('#9' in flavor or 'b9' in flavor) and len(tones) > 1 and (x == tones[1] or y == tones[1]))
                or ('dim' in flavor and len(tones) > 2 and (x == tones[2] or y == tones[2]))
                or ('dim' in flavor and len(tones) > 6 and (x == tones[6] or y == tones[6]))
                or ('aug' in flavor and len(tones) > 6 and (x == tones[6] or y == tones[6]))
            ):
                if self.verbose:
                    print(f"\tDROP: {x}")
                continue
            fixed.append(p)

        if self.guitar:
            fixed = sorted([n + 12 if n < self.E1 else n for n in fixed])

        if self.wrap:
            n = Note(self.wrap, 'ISO').format('midinum')
            fixed = sorted([x - 12 if x > n else x for x in fixed])

        fixed = list(sorted(set(fixed)))
        if self.verbose:
            self._verbose_notes('NOTES', fixed)

        chosen = []
        if len(fixed) > 1:
            try:
                voice = VoiceGen(pitches=fixed, intervals=self.intervals)
                voice.context(fixed[len(fixed) // 2])
                chosen = [voice.rand() for _ in range(num)]
            except Exception:
                chosen = [fixed[0]] * num
        else:
            chosen = [fixed[0]] * num

        if self.tonic:
            chosen[0] = fixed[0]

        if next_chord:
            intersect = list(set(fixed) & set(next_pitches))
            if self.verbose:
                self._verbose_notes('INTERSECT', intersect)
            if intersect:
                closest = self._closest(chosen[-2] if len(chosen) > 1 else chosen[-1], intersect)
                if closest is not None:
                    chosen[-1] = closest

        if self.verbose:
            self._verbose_notes('CHOSEN', chosen)

        return chosen

    @staticmethod
    def _parse_chord(chord):
        import re
        m = re.match(r'^([A-G][#b]?)(.*)$', chord)
        if m:
            return m.group(1), m.group(2)
        return None, None

    def _verbose_notes(self, title, notes):
        names = [self.pitchname(n) for n in notes]
        print(f"\t{title}: {names}")

    @staticmethod
    def _closest(key, lst):
        lst = [x for x in lst if x != key]
        if not lst:
            return None
        diffs = [abs(key - x) for x in lst]
        min_diff = min(diffs)
        closest = [lst[i] for i, d in enumerate(diffs) if d == min_diff]
        import random
        return random.choice(closest)

    # Placeholder methods for compatibility with the Perl code
    def pitchnum(self, note):
        # Should convert note name to MIDI number
        return note

    def pitchname(self, midinum):
        # Should convert MIDI number to note name
        return str(midinum)

# The following are placeholders for the required music theory functions/classes.
# In a real implementation, these would need to be replaced with actual logic or libraries.

def get_scale_notes(key, scale):
    # Return a list of note names for the given key and scale
    return []

def get_scale_MIDI(key, octave, scale):
    # Return a list of MIDI numbers for the given key, octave, and scale
    return []

def chord_with_octave(chord, octave):
    # Return a list of note names or MIDI numbers for the chord at the given octave
    return []

class Note:
    def __init__(self, value, mode):
        self.value = value
        self.mode = mode

    def format(self, fmt):
        return str(self.value)

    def en_eq(self, eq):
        pass

class VoiceGen:
    def __init__(self, pitches, intervals):
        self.pitches = pitches
        self.intervals = intervals
        self._context = pitches[0] if pitches else 0

    def context(self, note):
        self._context = note

    def rand(self):
        import random
        idx = self.pitches.index(self._context) if self._context in self.pitches else 0
        interval = random.choice(self.intervals)
        new_idx = idx + interval
        new_idx = max(0, min(new_idx, len(self.pitches) - 1))
        self._context = self.pitches[new_idx]
        return self._context
