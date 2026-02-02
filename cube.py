'''cube = [ y z x
  [ [000, 001, 002],   # layer 0
    [010, 011, 012],
    [020, 021, 022] ],

  [ [100, 101, 102],  y=1, z=0 ,x=0/1/2 # layer 1  right     102,112,122 y=1, z=0/1/2 ,x=2
    [110, 111, 112],  y=1, z=1 ,x=0/1/2                      101,111,121 y=1, z=0/1/2 ,x=1
    [120, 121, 122] ],y=1, z=2 ,x=0/1/2                      100,110,120 y=1, z=0/1/2 ,x=0
new[z][x] = old[x][2-z]
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
            cubelet['R'] = curr_cubelet['F']
            cubelet['B'] = curr_cubelet['R']
            cubelet['L'] = curr_cubelet['B']
            cubelet['F'] = curr_cubelet['L']
        elif direction == 'LEFT': # F-L-B-R-F 
            cubelet['L'] = curr_cubelet['F']
            cubelet['B'] = curr_cubelet['L']
            cubelet['R'] = curr_cubelet['B']
            cubelet['F'] = curr_cubelet['R']

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
    # right direction
    if direction=='RIGHT' or direction=='LEFT': # (z, x) -> (x, 2−z)
        # position
        old = [[cube[layer_index][z][x] for x in range(3)] for z in range(3)]
        for z in range(3):
            for x in range(3):
                cube[layer_index][z][x] = old[x][2-z]
        # face rotation
        for z in range(3):
            for x in range(3):
                rotate_cubelet_faces(cube[layer_index][z][x],axis='y',direction='RIGHT')

    # left direction
    # if direction=='LEFT': # (z, x) -> (x, 2−z)
    #     # position
    #     old = [[cube[layer_index][z][x] for x in range(3)] for z in range(3)]
    #     for z in range(3):
    #         for x in range(3):
    #             cube[layer_index][z][x] = old[2-x][z]
    #     # face rotation
    #     for z in range(3):
    #         for x in range(3):
    #             rotate_cubelet_faces(cube[layer_index][z][x],axis='y',direction='LEFT')

    # # up direction
    # if direction=='UP': # (y, z) -> (z, 2−y)
    #     # position
    #     old = [[cube[y][z][layer_index] for y in range(3)] for z in range(3)]
    #     for z in range(3):
    #         for x in range(3):
    #             cube[y][z][layer_index] = old[2-y][z]
    #     # face rotation
    #     for z in range(3):
    #         for x in range(3):
    #             rotate_cubelet_faces(cube[y][z][layer_index],axis='x',direction='UP')

    # # down direction
    # if direction=='DOWN': # (y, z) -> (z, 2−y)
    #     # position
    #     old = [[cube[y][z][layer_index] for y in range(3)] for z in range(3)]
    #     for z in range(3):
    #         for x in range(3):
    #             cube[y][z][layer_index] = old[2-y][z]
    #     # face rotation
    #     for z in range(3):
    #         for x in range(3):
    #             rotate_cubelet_faces(cube[y][z][layer_index],axis='x',direction='DOWN')

