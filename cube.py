'''cube = [
  [ [cubelet, cubelet, cubelet],   # layer 0
    [cubelet, cubelet, cubelet],
    [cubelet, cubelet, cubelet] ],

  [ [cubelet, cubelet, cubelet],   # layer 1
    [cubelet, cubelet, cubelet],
    [cubelet, cubelet, cubelet] ],

  [ [cubelet, cubelet, cubelet],   # layer 2
    [cubelet, cubelet, cubelet],
    [cubelet, cubelet, cubelet] ],
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



