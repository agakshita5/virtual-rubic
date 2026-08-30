'''cube = [ y z x
  [ [000, 001, 002],    # layer 0
    [010, 011, 012],
    [020, 021, 022] ],

  [ [100, 101, 102],    # layer 1
    [110, 111, 112],
    [120, 121, 122] ],

  [ [200, 201, 202],    # layer 2
    [210, 211, 212],
    [220, 221, 222] ],
]

 00 01 02
 10 11 12
 20 21 22
'''

import random

SOLVED_COLORS = {'F': 'WHITE', 'B': 'YELLOW', 'L': 'ORANGE',
                 'R': 'RED',   'U': 'GREEN',  'D': 'BLUE'}

def build_solved():
    fresh = [[[{'U': None,'D': None,'L': None,'R': None,'F': None,'B': None}
               for k in range(3)] for j in range(3)] for i in range(3)]
    for y in range(3):
        for z in range(3):
            for x in range(3):
                cubelet = fresh[y][z][x]
                if z == 2:
                    cubelet['F'] = SOLVED_COLORS['F']
                if z == 0:
                    cubelet['B'] = SOLVED_COLORS['B']
                if x == 0:
                    cubelet['L'] = SOLVED_COLORS['L']
                if x == 2:
                    cubelet['R'] = SOLVED_COLORS['R']
                if y == 2:
                    cubelet['U'] = SOLVED_COLORS['U']
                if y == 0:
                    cubelet['D'] = SOLVED_COLORS['D']
    return fresh

cube = build_solved()

def reset():
    # mutate in place so anything already holding `cube` keeps a live reference
    cube[:] = build_solved()

def rotate_cubelet_faces(cubelet, axis, direction):
    # rotate around y (left/right)
    if axis == 'y': 
        curr_cubelet = cubelet.copy()
        if direction == 'RIGHT': # F-R-B-L-F
            cubelet['R'] = curr_cubelet['F']
            cubelet['B'] = curr_cubelet['R']
            cubelet['L'] = curr_cubelet['B']
            cubelet['F'] = curr_cubelet['L']
        elif direction == 'LEFT': # F-L-B-R-F 
            cubelet['L'] = curr_cubelet['F']
            cubelet['B'] = curr_cubelet['L']
            cubelet['R'] = curr_cubelet['B']
            cubelet['F'] = curr_cubelet['R']

    # rotate around z (anticlockwise/clockwise) - (acw/cw)
    elif axis == 'z': 
            curr_cubelet = cubelet.copy()
            if direction == 'CW': # U-R-D-L-U
                cubelet['R'] = curr_cubelet['U']
                cubelet['D'] = curr_cubelet['R']
                cubelet['L'] = curr_cubelet['D']
                cubelet['U'] = curr_cubelet['L']
            elif direction == 'ACW': # U-L-D-R-U
                cubelet['L'] = curr_cubelet['U']
                cubelet['D'] = curr_cubelet['L']
                cubelet['R'] = curr_cubelet['D']
                cubelet['U'] = curr_cubelet['R']

    # rotate around x (up/down)
    elif axis == 'x':
        curr_cubelet = cubelet.copy()
        if direction == 'UP': # F-U-B-D-F
            cubelet['U'] = curr_cubelet['F']
            cubelet['B'] = curr_cubelet['U']
            cubelet['D'] = curr_cubelet['B']
            cubelet['F'] = curr_cubelet['D']
        elif direction == 'DOWN': # F-D-B-U-F 
            cubelet['D'] = curr_cubelet['F']
            cubelet['B'] = curr_cubelet['D']
            cubelet['U'] = curr_cubelet['B']
            cubelet['F'] = curr_cubelet['U']

def rotate_slice(axis, layer_index, direction):
    if axis=='y': # rotate (z,x) grid
        # position
        old = [[cube[layer_index][z][x] for x in range(3)] for z in range(3)]
        if direction=='RIGHT':
            for z in range(3):
                for x in range(3):
                    cube[layer_index][z][x] = old[x][2-z]
        elif direction=='LEFT':
            for z in range(3):
                for x in range(3):
                    cube[layer_index][z][x] = old[2-x][z]

        # face rotation
        for z in range(3):
            for x in range(3):
                rotate_cubelet_faces(cube[layer_index][z][x],axis='y',direction=direction)

    elif axis=='x': # rotate (y,z) grid
        # position
        old = [[cube[y][z][layer_index] for z in range(3)] for y in range(3)]
        if direction=='UP':
            for y in range(3):
                for z in range(3):
                    cube[y][z][layer_index] = old[2-z][y]
        elif direction=='DOWN':
            for y in range(3):
                for z in range(3):
                    cube[y][z][layer_index] = old[z][2-y]

        # face rotation
        for y in range(3):
            for z in range(3):
                rotate_cubelet_faces(cube[y][z][layer_index], axis='x', direction=direction)

    elif axis=='z': # rotate (y,x) grid
            # position
            old = [[cube[y][layer_index][x] for x in range(3)] for y in range(3)]
            if direction=='CW':
                for y in range(3):
                    for x in range(3):
                        cube[y][layer_index][x] = old[x][2-y]
            elif direction=='ACW':
                for y in range(3):
                    for x in range(3):
                        cube[y][layer_index][x] = old[2-x][y]
    
            # face rotation
            for y in range(3):
                for x in range(3):
                    rotate_cubelet_faces(cube[y][layer_index][x], axis='z', direction=direction)

# a face turn is clockwise as seen looking at that face from outside the cube
MOVE_TO_ROTATION = {
    'U': ('y', 2, 'LEFT'),   'D': ('y', 0, 'RIGHT'),
    'R': ('x', 2, 'UP'),     'L': ('x', 0, 'DOWN'),
    'F': ('z', 2, 'CW'),     'B': ('z', 0, 'ACW'),
    # slice moves, each following the face it is named after
    'M': ('x', 1, 'DOWN'),   # follows L
    'E': ('y', 1, 'RIGHT'),  # follows D
    'S': ('z', 1, 'CW'),     # follows F
}

OPPOSITE = {'LEFT': 'RIGHT', 'RIGHT': 'LEFT',
            'UP': 'DOWN',    'DOWN': 'UP',
            'CW': 'ACW',     'ACW': 'CW'}

def move(notation):
    """apply one move in standard notation: R, R'(anticlockwise), R2"""
    face, suffix = notation[0].upper(), notation[1:]
    if face not in MOVE_TO_ROTATION:
        raise ValueError(f"unknown face in move {notation!r}")

    axis, layer_index, direction = MOVE_TO_ROTATION[face]
    if suffix == "'":
        rotate_slice(axis, layer_index, OPPOSITE[direction])
    elif suffix == '2':
        rotate_slice(axis, layer_index, direction)
        rotate_slice(axis, layer_index, direction)
    elif suffix == '':
        rotate_slice(axis, layer_index, direction)
    else:
        raise ValueError(f"unknown suffix in move {notation!r}")
    return notation

def apply(sequence):
    """apply a sequence, given as "R U R' U'" or as a list of moves."""
    if isinstance(sequence, str):
        sequence = sequence.split()
    for notation in sequence:
        move(notation)
    return list(sequence)

def invert(sequence):
    """the sequence that undoes `sequence` — reversed, with each move flipped."""
    if isinstance(sequence, str):
        sequence = sequence.split()
    undo = []
    for notation in reversed(sequence):
        if notation.endswith("'"):
            undo.append(notation[:-1])
        elif notation.endswith('2'):
            undo.append(notation)          # a half turn is its own inverse
        else:
            undo.append(notation + "'")
    return undo

def scramble(n=25, seed=None):
    rng = random.Random(seed)
    faces = ['U', 'D', 'L', 'R', 'F', 'B']
    moves, last = [], None
    for _ in range(n):
        face = rng.choice([f for f in faces if f != last])   # no trivial undo
        last = face
        moves.append(face + rng.choice(['', "'", '2']))
    apply(moves)
    return moves

'''
each face is read as a 3x3 grid the way we see it looking at that face from outside
row 0 is the top of that view, column 0 the left
The lambdas map a (row, col) on a face to the (y, z, x) of the cubelet carrying that sticker

  U : looking down, back at top of view,  right = +x
  D : looking up, front at top of view,   right = +x
  F : the plain front view                right = +x
  B : looking from behind,                right = -x
  R : looking from the right,             right = -z
  L : looking from the left,              right = +z
'''

FACELET_MAP = {
    'U': lambda r, c: (2, r, c),
    'D': lambda r, c: (0, 2 - r, c),
    'F': lambda r, c: (2 - r, 2, c),
    'B': lambda r, c: (2 - r, 0, 2 - c),
    'R': lambda r, c: (2 - r, 2 - c, 2),
    'L': lambda r, c: (2 - r, c, 0),
}

def get_facelets():
    """state as 6 faces x 3x3 colors"""
    facelets = {}
    for face, index in FACELET_MAP.items():
        grid = []
        for r in range(3):
            row = []
            for c in range(3):
                y, z, x = index(r, c)
                row.append(cube[y][z][x][face])
            grid.append(row)
        facelets[face] = grid
    return facelets # key: face(char), value: grid(list)

def is_solved():
    # all faceletes' color match to center color grid[1][1]
    return all(sticker == grid[1][1] for grid in get_facelets().values() for row in grid for sticker in row)

def print_net(facelets=None):
    f = facelets or get_facelets()
    short = lambda c: c[0] if c else '?'
    pad = '      '
    for row in f['U']:
        print(pad + ' '.join(short(c) for c in row))
    for r in range(3):
        print(' '.join(short(c) for c in f['L'][r]) + ' ' +
              ' '.join(short(c) for c in f['F'][r]) + ' ' +
              ' '.join(short(c) for c in f['R'][r]) + ' ' +
              ' '.join(short(c) for c in f['B'][r]))
    for row in f['D']:
        print(pad + ' '.join(short(c) for c in row))
