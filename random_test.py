
import pygame
from pygame.locals import *
import sys, os, random

pygame.init()

X_SCREEN = 100
Y_SCREEN = 100


screen = pygame.display.set_mode([X_SCREEN, Y_SCREEN])
surface = pygame.Surface([X_SCREEN, Y_SCREEN])


persistence = 0.2
num_octaves = 8

randoms = []

def LinearInterpolate(a, b, x):
    return a*(1-x) + b*x

##  function Cubic_Interpolate(v0, v1, v2, v3,x)
##	P = (v3 - v2) - (v0 - v1)
##	Q = (v0 - v1) - P
##	R = v2 - v0
##	S = v1
##
##	return Px3 + Qx2 + Rx + S
##  end of function

def CubicInterpolate(v0, v1, v2, v3, x):
    P = (v3 - v2) - (v0 - v1)
    Q = (v0 - v1) - P
    R = v2 - v0
    S = v1
    return P*math.pow(x,3) + Q*math.pow(x,2) + R*x + S

def Noise(i, x, y):
##    random.seed(i)
    return random.random()

def SmoothedNoise(i, x, y):
    corners = (Noise(i, x-1, y-1) + Noise(i, x+1, y-1) + Noise(i, x-1, y+1) + Noise(i, x+1, y+1)) / 16
    sides = (Noise(i, x-1, y) + Noise(i, x+1, y) + Noise(i, x, y-1) + Noise(i, x, y+1) ) / 8
    center = Noise(i, x, y) / 4
    return corners + sides + center

def InterpolatedNoise(i, x, y):
    x_int = int(x)
    x_frac = x - x_int
    y_int = int(y)
    y_frac = y - y_int
##    print x, y, x_int, y_int, x_frac, y_frac

    v1 = SmoothedNoise(i, x_int, y_int)
    v2 = SmoothedNoise(i, x_int+1, y_int)
    v3 = SmoothedNoise(i, x_int, y_int+1)
    v4 = SmoothedNoise(i, x_int+1, y_int+1)

##    i1 = LinearInterpolate(v1, v2, x_frac)
##    i2 = LinearInterpolate(v3, v4, x_frac)
##    return LinearInterpolate(i1, i2, y_frac)

    return CubicInterpolate(v1, v2, v3, v4, x_frac)

def PerlinNoise_2D(x, y):
##    print x, y
    total = 0
    p = persistence
    n = num_octaves

    for i in range(0, n):
        frequency = math.pow(2,i)
        amplitude = math.pow(p,i)

        total += InterpolatedNoise(i, x*frequency, y*frequency) * amplitude

    return total


def generate():
    noise = []
    
    for x in range(X_SCREEN):
        a = []
        for y in range(Y_SCREEN):
            n = PerlinNoise_2D(float(x), float(y))
            a.append(n)
        noise.append(a)

    print noise

    surface.lock()
    for x in range(X_SCREEN):
        for y in range(Y_SCREEN):
            color = int(round(noise[x][y]*255.0/3.0))
            surface.set_at((x,y), (color,color,color))
    surface.unlock()


def mainloop():
    while 1:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT or key[K_ESCAPE]:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_F12:
                pygame.image.save(surface, "Perlin Noise.png")
        
        screen.blit(surface,(0,0))
        pygame.display.flip()

generate()
mainloop()