import random
from random_rhythms import Rhythm
from music_drummer import Drummer
# from music_bassline_generator import Bassline
# author use:
import sys
sys.path.append('./src')
from music_bassline_generator.music_bassline_generator import Bassline

def section_A(d, fills, lines, part=0):
    if part == 1:
        d.note('crash1', 1)
        d.rest('cymbals', 15)
    else:
        d.rest('cymbals', 16)
    d.rest('toms', 16)
    for _ in range(3):
        d.pattern(
            patterns={
                'kick':  '1000000010000000',
                'snare': '0000100000001000',
                'hihat': '1010101010101010',
            },
        )
    for _ in range(1):
        d.pattern(
            patterns={
                'kick':  '10000000',
                'snare': '00001000',
                'hihat': '10101010',
            },
        )
    fill = random.choice(fills)
    for duration in fill:
        d.note('snare', duration)
    d.rest(['kick', 'hihat'], 2)

def section_B(d, fills, lines, part=0):
    d.note('crash1', 1)
    d.rest('cymbals', 15)
    d.rest('toms', 14)
    for _ in range(3):
        d.pattern(
            patterns={
                'kick':  '1000001010000000',
                'snare': '0000100000001000',
                'hihat': '0010101010101010',
            },
        )
    for _ in range(1):
        d.pattern(
            patterns={
                'kick':  '10000001',
                'snare': '00001000',
                'hihat': '23101010',
            },
        )
    fill = random.choice(fills)
    for i,duration in enumerate(fill):
        if i < len(fills) - 1:
            d.note('snare', duration)
            d.rest('tom1', duration)
        else:
            d.rest('snare', duration)
            d.note('tom1', duration)
    d.rest(['kick', 'hihat'], 2)

if __name__ == "__main__":
    d = Drummer()
    d.set_bpm(100)
    d.set_ts()
    dr = Rhythm(
        measure_size=2,
        durations=[1/4, 1/2],
    )
    fills = [ dr.motif() for x in range(4) ]
    
    b = Bassline()
    br = Rhythm(
        measure_size=3,
        durations=[1/2, 1, 3/2],
    )
    lines = [ br.motif() for x in range(3) ]

    section_A(d, fills, lines)
    section_B(d, fills, lines)
    section_B(d, fills, lines)
    section_A(d, fills, lines, part=1)

    d.sync_parts()
    d.show('midi')
    # d.write()