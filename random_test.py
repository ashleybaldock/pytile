#!/usr/local/bin/python

import pygame
from pygame.locals import *
import sys, os, random, math

from numpy import *

import noise

pygame.init()

# Size of the screen
X_SCREEN = 1000
Y_SCREEN = 500

# Padding around the screen
PADDING = 10

# Set offsets of origin of depiction of 1D noise
X_OFFSET_LEFT = 10
X_OFFSET_RIGHT = 400

# Midpoints of the two sets of axis
Y_TOP_OFFSET = Y_SCREEN / 4
Y_BOTTOM_OFFSET = Y_SCREEN / 4 * 3

# Midline of the screen
Y_MIDPOINT = Y_SCREEN / 2

# Set size of the 1D noise output
X_LIMIT = X_SCREEN - X_OFFSET_LEFT - X_OFFSET_RIGHT
Y_LIMIT = Y_SCREEN / 4

D3_WIDTH = 100
D3_HEIGHT = 100
D3_X = 100
D3_Y = 100

D3_OFF_X = X_SCREEN - 60 - D3_WIDTH * 2.5
D3_OFF_Y = Y_SCREEN / 2 - D3_HEIGHT * 2 + 50

D3_STRETCH = 2

# Colours
WHITE = (255,255,255)
SILVER = (128,128,128)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
CYAN = (0,255,255)
MAGENTA = (255,0,255)

# Octave 1 is period 1, Octave 2 is period 1/2, Octave 3 is period 1/4 etc.

# pixels per period (in x dimension)
PPP = 300
# Random seed, this specifies what the output will look like
# Noise generation is entirely deterministic based on this seed
R = 64
# Persistence, this specifies how much smaller details affect the end result
PERSISTENCE = 0.7
# Octaves, number of frequency ranges
OCTAVES = 6

# Interpolation method
INTER_METHOD = "linear"
INTER_METHOD = "cosine"

# Setup display surfaces
screen = pygame.display.set_mode([X_SCREEN, Y_SCREEN])
surface = pygame.Surface([X_SCREEN, Y_SCREEN])


# Random values should always be between 0 and 1
def get_random():
    return random.uniform(-1,1)
    return random.random()

def gen_1D_values(length):
    vals = []
    for l in range(length):
        vals.append(get_random())
    return vals
def gen_1D_value(r, position):
    random.seed(r)
    val = 0
    for l in range(position):
        val = get_random()
    return val

def LinearInterpolate(a, b, x):
    return a*(1-x) + b*x

def CosineInterpolate(a, b, x):
    ft = x * math.pi
    f = (1 - math.cos(ft)) * 0.5
    return a*(1-f) + b*f

def cosine_interpolate_2D(v1, v2, v3, v4, x, y):
    A = CosineInterpolate(v1, v2, x)
    B = CosineInterpolate(v3, v4, x)
    return CosineInterpolate(A, B, y)

def linear_interpolate_2D(v1, v2, v3, v4, x, y):
    A = LinearInterpolate(v1, v2, x)
    B = LinearInterpolate(v3, v4, x)
    return LinearInterpolate(A, B, y)

def regen_seed():
    random.seed()
    r = random.randint(0,100)
    return r

def regen_seeds(random_seed, values):
    random.seed(random_seed)
    randoms = []
    for o in range(values):
        randoms.append(random.randint(0,100))
    return randoms

def pad_array(a):
    """Pad an array around the edges to make it suitable for smoothing"""
    b = insert(a, -1, a[-1,...], axis=0)
    b = insert(b, 0, b[0,...], axis=0)
    b = insert(b, -1, b[...,-1], axis=1)
    b = insert(b, 0, b[...,0], axis=1)
    return b

def get_neighbours(a, x, y):
    """Return array containing height values of the neighbours of a particular value in the input array"""
    b = a[x-1:x+2,y-1:y+2]
    return b


k = fromfunction(lambda x,y: 10*x+y, (5,4), dtype=int)

q = pad_array(k)

print q
print get_neighbours(q, 2, 3)

def get_at_point_1D(p, randoms, ppp, persistence, octaves):
    # Returns an array of points representing the raw octave values and resultant value at a point
    # Takes the point, ppp, persistence and octaves values
    amps = []
    yvals = []
    # Divide p by ppp to find how many random points along we are, do this for each octave
    for o in range(octaves):
        pow2o = pow(2,o)
        position, remainder = divmod(p, ppp / pow2o)
        # Convert number of pixels along in a period into a % value for the interpolation function
        if remainder != 0:
            percentalong = float(remainder) / ppp * pow2o
        else:
            percentalong = 0

        if INTER_METHOD == "linear":
            interpolate = LinearInterpolate
        elif INTER_METHOD == "cosine":
            interpolate = CosineInterpolate

        yval = interpolate(gen_1D_value(randoms[o],position),
                           gen_1D_value(randoms[o],position+1),
                           percentalong)

        yvals.append(yval)
        amps.append(pow(persistence, o))

    # Return yvalues for component points, amplitudes for those yvalues and the overall output for this point
    return (yvals, amps, reduce(lambda x, y: x+(y[0]*y[1]), zip(yvals, amps), 0) / sum(amps))


def generate(ppp, r, persistence, octaves):
    # Generate array of colours, divide 255 by number of octaves
    colours = []
    b = 100.0 / octaves
    c = 200.0 / octaves
    for d in range(octaves):
        colours.append((255 - int(c * d), 100, 155 + int(b * d)))

    surface.fill(BLACK)
    # draw top x axis
    pygame.draw.line(surface, SILVER, (X_OFFSET_LEFT,Y_TOP_OFFSET), (X_OFFSET_LEFT+X_LIMIT,Y_TOP_OFFSET))
    # draw midline
    pygame.draw.line(surface, WHITE, (0,Y_MIDPOINT), (X_OFFSET_LEFT+X_LIMIT,Y_MIDPOINT))
    # draw bottom x axis
    pygame.draw.line(surface, SILVER, (X_OFFSET_LEFT,Y_BOTTOM_OFFSET), (X_OFFSET_LEFT+X_LIMIT,Y_BOTTOM_OFFSET))
    # draw y axis
    pygame.draw.line(surface, WHITE, (X_OFFSET_LEFT,0), (X_OFFSET_LEFT,Y_SCREEN))

    # Draw the 2D graph representation
    surface.lock()
    randoms = regen_seeds(r, octaves)
    for x in range(X_LIMIT):
        yvals, amps, result = get_at_point_1D(x, randoms, ppp, persistence, octaves)
        for n, amp, y in map(lambda x,y: (x[0],x[1],y), enumerate(amps), yvals):
            surface.set_at((int(X_OFFSET_LEFT+x),int(Y_TOP_OFFSET-y*Y_LIMIT*amp)), colours[n])
        surface.set_at((int(X_OFFSET_LEFT+x),int(Y_BOTTOM_OFFSET-result*Y_LIMIT)), RED)
    surface.unlock()

    # Draw the 3D graph representation
    surface.lock()
    # Generate a 2D perlin noise object based on initial seed and other values
    perlin2D = noise.Perlin2D(D3_WIDTH, D3_HEIGHT, r, "cosine", ppp, persistence, octaves)

    for x in range(D3_WIDTH):
        for y in range(D3_HEIGHT):
            xx = (D3_WIDTH/2 + x - y) * 2
            yy = (D3_HEIGHT + x + y)
            # Calculate the height of the map at this point
            zval = perlin2D.get_at_point_2D(x, y)

            # zval will be in range -1<n<1
            # Multiply this by the graph's height extent
            SCALE = 100.0
            if zval < 0:
                zs = -1
            else:
                zs = 1
            z = zval*SCALE
            if z < 0:
                R = 0
                B = abs(z/SCALE*100+155)
            else:
                R = abs(z/SCALE*100+155)
                B = 0
            # Draw a point to represent this height value
            surface.set_at((int(D3_OFF_X+xx), int(D3_OFF_Y+yy-z)), (R, 0, B))
    surface.unlock()

def mainloop():
    ppp = PPP
    r = R
    persistence = PERSISTENCE
    octaves = OCTAVES
    generate(ppp, r, persistence, octaves)
    while 1:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT or key[K_ESCAPE]:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_F12:
                pygame.image.save(surface, "random_test.png")
            if event.type == KEYDOWN and event.key == K_r:
                r = regen_seed()
                generate(ppp, r, persistence, octaves)
            if event.type == KEYDOWN and event.key == K_p:
                ppp += 10
                generate(ppp, r, persistence, octaves)
            if event.type == KEYDOWN and event.key == K_o:
                ppp -= 10
                if ppp <= 0:
                    ppp = 20
                generate(ppp, r, persistence, octaves)
            if event.type == KEYDOWN and event.key == K_l:
                persistence += 0.05
                if persistence > 1:
                    persistence = 1
                generate(ppp, r, persistence, octaves)
            if event.type == KEYDOWN and event.key == K_k:
                persistence -= 0.05
                if persistence < 0.05:
                    persistence = 0.05
                generate(ppp, r, persistence, octaves)
            if event.type == KEYDOWN and event.key == K_m:
                octaves += 1
                if octaves > 8:
                    octaves = 8
                generate(ppp, r, persistence, octaves)
            if event.type == KEYDOWN and event.key == K_n:
                octaves -= 1
                if octaves < 1:
                    octaves = 1
                generate(ppp, r, persistence, octaves)

        screen.blit(surface,(0,0))
        pygame.display.flip()

if __name__ == "__main__":
    mainloop()


