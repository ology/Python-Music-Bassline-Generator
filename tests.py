import sys
sys.path.append('./src')
from music_bassline_generator.music_bassline_generator import Bassline
import unittest

class TestMusicBasslineGenerator(unittest.TestCase):
    BOGUS = 'foo'
    VERBOSE = 0

    def test_invalid_args(self):
        with self.assertRaisesRegex(ValueError, 'not a boolean'):
            Bassline(guitar=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not a boolean'):
            Bassline(modal=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not a boolean'):
            Bassline(chord_notes=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not a boolean'):
            Bassline(tonic=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not a boolean'):
            Bassline(verbose=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not a valid pitch'):
            Bassline(keycenter=self.BOGUS)
        with self.assertRaisesRegex(TypeError, 'not an array reference'):
            Bassline(intervals=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not a positive integer'):
            Bassline(octave=self.BOGUS)
        with self.assertRaisesRegex(TypeError, 'not a code reference'):
            Bassline(scale=self.BOGUS)
        with self.assertRaisesRegex(ValueError, 'not valid'):
            Bassline(wrap=self.BOGUS)

    def test_attrs(self):
        obj = Bassline(verbose=self.VERBOSE)
        self.assertEqual(obj.octave, 1)
        self.assertEqual(obj.intervals, [-3, -2, -1, 1, 2, 3])
        self.assertTrue(callable(obj.scale))

    def test_scale(self):
        obj = Bassline(verbose=self.VERBOSE)
        self.assertEqual(obj.scale('C7b5'), 'major')
        self.assertEqual(obj.scale('Dm7b5'), 'minor')
        self.assertEqual(obj.scale('D#/A#'), 'major')

    def test_modal(self):
        obj = Bassline(verbose=self.VERBOSE, modal=True)
        self.assertEqual(obj.scale('C7b5'), 'ionian')
        self.assertEqual(obj.scale('Dm7b5'), 'dorian')

    def test_generate(self):
        obj = Bassline(verbose=self.VERBOSE)
        self.assertEqual(len(obj.generate('C7b5', 4)), 4)
        self.assertEqual(len(obj.generate('D/A', 4)), 4)
        self.assertEqual(len(obj.generate('D', 4, 'C/G')), 4)
        self.assertEqual(len(obj.generate('D', 1)), 1)

        obj = Bassline(verbose=self.VERBOSE, tonic=True)
        expect = 24
        got = obj.generate('C', 4)
        self.assertEqual(got[0], expect)
        got = obj.generate('C', 1)
        self.assertEqual(got[0], expect)

        obj = Bassline(verbose=self.VERBOSE, modal=True)
        expect = 46
        got = obj.generate('Dm7', 99)
        self.assertTrue(all(x != expect for x in got))

        obj = Bassline(verbose=self.VERBOSE, modal=True, chord_notes=False)
        expect = 44
        got = obj.generate('Dm7b5', 99)
        self.assertTrue(all(x != expect for x in got))

    def test_wrap(self):
        obj = Bassline(
            verbose=self.VERBOSE,
            octave=3,
            wrap='C3',
            modal=True,
            keycenter='C'
        )
        got = obj.generate('C', 4)
        self.assertEqual(sum(1 for x in got if x <= 48), 4)

    def test_positions(self):
        obj = Bassline(
            verbose=self.VERBOSE,
            chord_notes=False,
            positions={'major': [1], 'minor': [1]}
        )
        expect = [26, 26, 26, 26]
        got = obj.generate('C', 4)
        self.assertEqual(got, expect)

if __name__ == '__main__':
    unittest.main()
