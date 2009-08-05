
import pygame
from pygame.locals import *
import sys, os, random, math

pygame.init()

# Size of the screen
X_SCREEN = 1000
Y_SCREEN = 500

# Padding around the screen
PADDING = 10

# Set offsets of origin of depiction of 1D noise
X_OFFSET_LEFT = 10
X_OFFSET_RIGHT = 200

# Midpoints of the two sets of axis
Y_TOP_OFFSET = Y_SCREEN / 4
Y_BOTTOM_OFFSET = Y_SCREEN / 4 * 3

# Midline of the screen
Y_MIDPOINT = Y_SCREEN / 2

# Set size of the 1D noise output
X_LIMIT = X_SCREEN - X_OFFSET_LEFT - X_OFFSET_RIGHT
Y_LIMIT = Y_SCREEN / 4

# Colours
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
CYAN = (0,255,255)
MAGENTA = (255,0,255)

period = 1
num_octaves = 8
# Octaves from 0 to X
# Octave 1 is period 1, Octave 2 is period 1/2, Octave 3 is period 1/4 etc.

# pixels per period (in x dimension), 20 is smallest which looks good
PPP = 400
# Random seed, this specifies what the output will look like
R = 50
# Persistence, this specifies how much smaller details affect the end result
PERSISTENCE = 0.2

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

def LinearInterpolate(a, b, x):
    return a*(1-x) + b*x

def CosineInterpolate(a, b, x):
    ft = x * math.pi
    f = (1 - math.cos(ft)) * 0.5
    return a*(1-f) + b*f

def regen_seed():
    random.seed()
    r = random.randint(0,100)
    return r

def generate(ppp, r, persistence):
    random.seed(r)
    allvals = []
    # First generate the seeds for each octave
    randoms = []
    for o in range(num_octaves):
        randoms.append(random.randint(0,100))
    # Octaves in range 1, num_octaves+1
    for o in range(num_octaves):
        random.seed(randoms[o])
        # Calculate length of one period for this octave in pixels
        # Total x length divided by the pixels per period value divided by the octave
        length, remainder = divmod(X_LIMIT, ppp / pow(2,o))
        if remainder > 0:
            allvals.append(gen_1D_values(length + 2))
        else:
            allvals.append(gen_1D_values(length + 1))


    surface.fill(BLACK)
    # draw top x axis
    pygame.draw.line(surface, WHITE, (X_OFFSET_LEFT,Y_TOP_OFFSET), (X_OFFSET_LEFT+X_LIMIT,Y_TOP_OFFSET))
    # draw midline
    pygame.draw.line(surface, WHITE, (0,Y_MIDPOINT), (X_SCREEN,Y_MIDPOINT))
    # draw bottom x axis
    pygame.draw.line(surface, WHITE, (X_OFFSET_LEFT,Y_BOTTOM_OFFSET), (X_OFFSET_LEFT+X_LIMIT,Y_BOTTOM_OFFSET))
    # draw y axis
    pygame.draw.line(surface, WHITE, (X_OFFSET_LEFT,0), (X_OFFSET_LEFT,Y_SCREEN))

    # Generate array of colours, divide 255 by number of octaves
    colours = []
    b = 100.0 / num_octaves
    c = 200.0 / num_octaves
    for d in range(num_octaves):
        colours.append((255 - int(c * d), 100, 155 + int(b * d)))

    surface.lock()
    for x in range(X_LIMIT):
        yvals = []
        for o, vals in enumerate(allvals):
            # Number of units along, number of pixels in one unit along
            # Frequency = pow(2,o)
            xdiv, xmod = divmod(x, ppp / pow(2,o))
            if xmod != 0:
                # Convert number of pixels along in a period into a % value for the interpolation function
                percentalong = float(xmod) / ppp * pow(2,o)
            else:
                percentalong = 0
            yvals.append(CosineInterpolate(vals[xdiv], vals[xdiv+1], percentalong))
        # Finally draw the individual and resultant lines
        amps = []
        for o, y in enumerate(yvals):
            # Amplitude = pow(persistence, o)
            amps.append(pow(persistence, o))
            surface.set_at((X_OFFSET_LEFT+x,Y_TOP_OFFSET-y*Y_LIMIT*amps[o]), colours[o])
                
        y = reduce(lambda x, y: x+(y[0]*y[1]), zip(yvals, amps), 0)# / len(yvals)
        
        surface.set_at((X_OFFSET_LEFT+x,Y_BOTTOM_OFFSET-y*Y_LIMIT), RED)
        

    # draw all random points on the line at correct interval
    for o, vals in enumerate(allvals):
        for n, v in enumerate(vals):
            amp = pow(persistence, o)
            pos = (X_OFFSET_LEFT+n*ppp/pow(2,o),Y_TOP_OFFSET-v*Y_LIMIT*amp)
            pygame.draw.circle(surface, GREEN, pos, 2)
            # For the main period also draw some red markers on the axis line
            if o == 0:
                pygame.draw.circle(surface, RED, (pos[0], Y_MIDPOINT), 3)
        pygame.draw.circle(surface, RED, pos, 3)
    surface.unlock()


def mainloop():
    ppp = PPP
    r = R
    persistence = PERSISTENCE
    generate(ppp, r, persistence)
    while 1:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT or key[K_ESCAPE]:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_F12:
                pygame.image.save(surface, "Perlin Noise.png")
            if event.type == KEYDOWN and event.key == K_r:
                r = regen_seed()
                generate(ppp, r, persistence)
            if event.type == KEYDOWN and event.key == K_p:
                ppp += 10
                generate(ppp, r, persistence)
            if event.type == KEYDOWN and event.key == K_o:
                ppp -= 10
                if ppp <= 0:
                    ppp = 20
                generate(ppp, r, persistence)
            if event.type == KEYDOWN and event.key == K_l:
                persistence += 0.05
                if persistence > 1:
                    persistence = 1
                generate(ppp, r, persistence)
            if event.type == KEYDOWN and event.key == K_k:
                persistence -= 0.05
                if persistence < 0.05:
                    persistence = 0.05
                generate(ppp, r, persistence)

        screen.blit(surface,(0,0))
        pygame.display.flip()

mainloop()


