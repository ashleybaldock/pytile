
import pygame
from pygame.locals import *
import sys, os, random, math

pygame.init()

# Size of the screen
X_SCREEN = 1000
Y_SCREEN = 500

# Set offsets of origin of depiction of 1D noise
X_OFFSET = 70
Y_OFFSET = Y_SCREEN / 2

# Set size of the 1D noise output
X_LIMIT = X_SCREEN - 2 * X_OFFSET
Y_LIMIT = Y_SCREEN / 2 - 10

# Colours
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

period = 1
num_octaves = 4
# pixels per period (in x dimension), 20 is smallest which looks good
PPP = 100
# In y dimension the equivalent value is taken by multiplying by the Y_LIMIT, assuming a value between 0 and 1


screen = pygame.display.set_mode([X_SCREEN, Y_SCREEN])
surface = pygame.Surface([X_SCREEN, Y_SCREEN])

persistence = 0.2

# Random values should always be between 0 and 1
def get_random():
    return random.random()

def gen_1D_values(length):
    vals = []
    for l in range(length):
        vals.append(get_random())
    return vals

def LinearInterpolate(a, b, x):
    return a*(1-x) + b*x

def CosineInterpolate(a, b, x):
    ft = x * math.pi
    f = (1 - math.cos(ft)) * 0.5
    return a*(1-f) + b*f

def generate(ppp):

    allvals = []
    for o in range(num_octaves+1):
        if o != 0:
            length = X_LIMIT / ppp * o
            allvals.append(gen_1D_values(length + 2*o))
        else:
            allvals.append(None)

    print allvals

    surface.fill(BLACK)
    # draw x axis
    pygame.draw.line(surface, WHITE, (X_OFFSET,Y_OFFSET), (X_OFFSET+X_LIMIT,Y_OFFSET))
    # draw y axis
    pygame.draw.line(surface, WHITE, (X_OFFSET,Y_OFFSET-Y_LIMIT), (X_OFFSET,Y_OFFSET+Y_LIMIT))

    # Generate array of colours, divide 255 by number of octaves
    colours = []
    b = 100.0 / o
    c = 200.0 / o
    for d in range(o):
        colours.append((255 - int(c * d), 0, 155 + int(b * d)))

    surface.lock()
    for o, vals in enumerate(allvals):
        if vals:
            for x in range(X_LIMIT):
                # Number of units along, number of pixels in one unit along
                xdiv, xmod = divmod(x, ppp / o)
                if xmod != 0:
                    # Convert number of pixels along in a period into a % value for the interpolation function
                    percentalong = float(xmod) / ppp * o
                else:
                    percentalong = 0
##                y = LinearInterpolate(vals[xdiv], vals[xdiv+1], percentalong)
##                print xdiv, xdiv+1, percentalong
                y = CosineInterpolate(vals[xdiv], vals[xdiv+1], percentalong)
                surface.set_at((X_OFFSET+x,Y_OFFSET-y*Y_LIMIT), colours[o-1])
    surface.unlock()

    

    # draw all random points on the line at correct interval
    surface.lock()
    for o, vals in enumerate(allvals):
        if vals:
            for n, v in enumerate(vals):
                pos = (X_OFFSET+n*ppp/o,Y_OFFSET-v*Y_LIMIT)
                pygame.draw.circle(surface, BLUE, pos, 2)
            pygame.draw.circle(surface, GREEN, pos, 2)
    surface.unlock()


def mainloop():
    ppp = PPP
    while 1:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT or key[K_ESCAPE]:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_F12:
                pygame.image.save(surface, "Perlin Noise.png")
            if event.type == KEYDOWN and event.key == K_r:
                generate(ppp)
            if event.type == KEYDOWN and event.key == K_p:
                ppp += 10
                generate(ppp)
            if event.type == KEYDOWN and event.key == K_o:
                ppp -= 10
                if ppp <= 0:
                    ppp = 20
                generate(ppp)
        
        screen.blit(surface,(0,0))
        pygame.display.flip()

generate(PPP)
mainloop()


##def LinearInterpolate(a, b, x):
##    return a*(1-x) + b*x
##
##def CubicInterpolate(v0, v1, v2, v3, x):
##    P = (v3 - v2) - (v0 - v1)
##    Q = (v0 - v1) - P
##    R = v2 - v0
##    S = v1
##    return P*math.pow(x,3) + Q*math.pow(x,2) + R*x + S
##
##def Noise(i, x, y):
####    random.seed(i)
##    return random.random()
##
##def SmoothedNoise(i, x, y):
##    corners = (Noise(i, x-1, y-1) + Noise(i, x+1, y-1) + Noise(i, x-1, y+1) + Noise(i, x+1, y+1)) / 16
##    sides = (Noise(i, x-1, y) + Noise(i, x+1, y) + Noise(i, x, y-1) + Noise(i, x, y+1) ) / 8
##    center = Noise(i, x, y) / 4
##    return corners + sides + center
##
##def InterpolatedNoise(i, x, y):
##    x_int = int(x)
##    x_frac = x - x_int
##    y_int = int(y)
##    y_frac = y - y_int
####    print x, y, x_int, y_int, x_frac, y_frac
##
##    v1 = SmoothedNoise(i, x_int, y_int)
##    v2 = SmoothedNoise(i, x_int+1, y_int)
##    v3 = SmoothedNoise(i, x_int, y_int+1)
##    v4 = SmoothedNoise(i, x_int+1, y_int+1)
##
####    i1 = LinearInterpolate(v1, v2, x_frac)
####    i2 = LinearInterpolate(v3, v4, x_frac)
####    return LinearInterpolate(i1, i2, y_frac)
##
##    return CubicInterpolate(v1, v2, v3, v4, x_frac)
##
##def PerlinNoise_2D(x, y):
####    print x, y
##    total = 0
##    p = persistence
##    n = num_octaves
##
##    for i in range(0, n):
##        frequency = math.pow(2,i)
##        amplitude = math.pow(p,i)
##
##        total += InterpolatedNoise(i, x*frequency, y*frequency) * amplitude
##
##    return total
##
##
