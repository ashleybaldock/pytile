
import pygame
from pygame.locals import *
import sys, os, random

pygame.init()

X_SCREEN = 200
Y_SCREEN = 200


screen = pygame.display.set_mode([X_SCREEN, Y_SCREEN])
surface = pygame.Surface([X_SCREEN, Y_SCREEN])


persistence = 0.8
num_octaves = 3

randoms = []

def Interpolate(a, b, x):
    return a*(1-x) + b*x

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

    i1 = Interpolate(v1, v2, x_frac)
    i2 = Interpolate(v3, v4, x_frac)

    return Interpolate(i1, i2, y_frac)

def PerlinNoise_2D(x, y):
##    print x, y
    total = 0
    p = persistence
    n = num_octaves

    for i in range(0, n):
        frequency = 2*i
        amplitude = p*i

        total += InterpolatedNoise(i, x*frequency, y*frequency) * amplitude

    return total


def generate():
    noise = []

    surface.lock()
    for x in range(X_SCREEN):
        a = []
        for y in range(Y_SCREEN):
            n = PerlinNoise_2D(float(x), float(y))
            a.append(n)
            print n
            color = int(round(n*255.0))
            print color
            surface.set_at((x,y), (color,color,color))
        noise.append(a)

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