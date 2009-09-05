#!/usr/bin/python

import sys, os, random, math

from numpy import *

# Perlin noise object, allows for generation of either an arbitrary amount of
# non-repetitive noise or for the generation of tileable textures

class Perlin2D(object):
    """Extensible Perlin noise, non-repeating"""
    def __init__(self, xdims, ydims, seed, inter, ppp, persistence, octaves):
        """Initialise the noise generator"""
        self.randoms = self.regen_seeds(seed, octaves)
        self.xdims = xdims
        self.ydims = ydims
        self.inter = inter
        self.ppp = ppp
        self.persistence = persistence
        self.octaves = octaves

        if inter == "linear":
            self.inter = self.linear_interpolate_2D
        elif inter == "cosine":
            self.inter = self.cosine_interpolate_2D

        self.gen_2D_noise()

    def gen_2D_noise(self):
        """Return a set of arrays representing each octave of noise"""
        self.octsets = []
        for o in range(self.octaves):
            # Generate set of X values for generating the set of y values
            xrandoms = self.regen_seeds(self.randoms[o], self.xdims + 1)
            a = []
            for x in xrandoms:
                random.seed(x)
                b = []
                for y in range(self.ydims + 1):
                    b.append(self.get_random())
                a.append(b)
            a = array(a)
            self.octsets.append(a)
        return True
    def get_at_point_2D(self, x, y):
        """Return some arbitrary point on the noise plane"""
        amps = []
        zvals = []
        # Find nearest points in x and y
        for o, octset in enumerate(self.octsets):
            # Doing this every time probably fine, 2^x is a quick operation
            pow2o = pow(2,o)
            positionX, remainderX = divmod(x, self.ppp / pow2o)
            positionY, remainderY = divmod(y, self.ppp / pow2o)
            if remainderX != 0:
                percentalongX = float(remainderX) / self.ppp * pow2o
            else:
                percentalongX = 0
            if remainderY != 0:
                percentalongY = float(remainderY) / self.ppp * pow2o
            else:
                percentalongY = 0

            zval = self.inter(octset[positionX][positionY],
                              octset[positionX+1][positionY],
                              octset[positionX][positionY+1],
                              octset[positionX+1][positionY+1], 
                              percentalongX, percentalongY)

            zvals.append(zval)
            amps.append(pow(self.persistence, o))

        return reduce(lambda x, y: x+(y[0]*y[1]), zip(zvals, amps), 0) / sum(amps) 

    def regen_seeds(self, random_seed, values):
        random.seed(random_seed)
        randoms = []
        for o in range(values):
            randoms.append(random.randint(0,100))
        return randoms

    def get_random(self):
        return random.uniform(-1,1)

    def linear_interpolate(self, a, b, x):
        return a*(1-x) + b*x

    def cosine_interpolate(self, a, b, x):
        ft = x * math.pi
        f = (1 - math.cos(ft)) * 0.5
        return a*(1-f) + b*f

    def cosine_interpolate_2D(self, v1, v2, v3, v4, x, y):
        A = self.cosine_interpolate(v1, v2, x)
        B = self.cosine_interpolate(v3, v4, x)
        return self.cosine_interpolate(A, B, y)

    def linear_interpolate_2D(self, v1, v2, v3, v4, x, y):
        A = self.linear_interpolate(v1, v2, x)
        B = self.linear_interpolate(v3, v4, x)
        return self.linear_interpolate(A, B, y)

