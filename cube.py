'''cube = [ y z x
  [ [000, 001, 002],   # layer 0
    [010, 011, 012],
    [020, 021, 022] ],

  [ [100, 101, 102],   # layer 1
    [110, 111, 112],
    [120, 121, 122] ],

  [ [200, 201, 202],   # layer 2
    [210, 211, 212],
    [220, 221, 222] ],
]

 00 01 02
 10 11 12
 20 21 22
'''
cube = [[[{'U': None,'D': None,'L': None,'R': None,'F': None,'B': None} for k in range(3)] for j in range(3)] for i in range(3)]

for y in range(3):
    for z in range(3):
        for x in range(3):
            cubelet = cube[y][z][x]
            if z == 2:
                cubelet['F'] = 'WHITE'
            if z == 0:
                cubelet['B'] = 'YELLOW'
            if x == 0:
                cubelet['L'] = 'ORANGE'
            if x == 2:
                cubelet['R'] = 'RED'
            if y == 2:
                cubelet['U'] = 'GREEN'
            if y == 0:
                cubelet['D'] = 'BLUE'

def rotate_cubelet_faces(cubelet, axis, direction):
    # rotate around y (left/right)
    if axis == 'y': 
        curr_cubelet = cubelet.copy()
        if direction == 'RIGHT': # F-R-B-L-F
            cubelet['R'] = curr_cubelet['B']
            cubelet['B'] = curr_cubelet['L']
            cubelet['L'] = curr_cubelet['F']
            cubelet['F'] = curr_cubelet['R']
        elif direction == 'LEFT': # F-L-B-R-F 
            cubelet['L'] = curr_cubelet['B']
            cubelet['B'] = curr_cubelet['R']
            cubelet['R'] = curr_cubelet['F']
            cubelet['F'] = curr_cubelet['L']
    # rotate around x (up/down): U-B-D-F-U (clk)
    elif axis == 'x':
        pass

    
 
