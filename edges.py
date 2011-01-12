#!/usr/local/bin/python

from PIL import Image, ImageDraw, ImageFont
import math
import random
# compare a to b, b to c, c to d and d to a

max_edge_difference = 2

output = []

for a in range(5):
    for b in range(5):
        for c in range(5):
            for d in range(5):
                if 0 in [a,b,c,d]:
                    # Must be one vertex at 0
                    if not (abs(a-b) > 2 or abs(b-c) > 2 or abs(c-d) > 2 or abs(d-a) > 2):
                        # All sides must have at most 2 units of up/down movement
                        output.append([a,b,c,d])

g0 = []
g1 = []
g2 = []
g3 = []
g4 = []

print "with 0, not 1, 2, 3 or 4"
for o in output:
    if 0 in o and not 1 in o and not 2 in o and not 3 in o and not 4 in o:
        g0.append(o)
        print o
print "with 1, not 2, 3 or 4"
for o in output:
    if 1 in o and not 2 in o and not 3 in o and not 4 in o:
        g1.append(o)
        print o
print "with 2, not 3 or 4"
for o in output:
    if 2 in o and not 3 in o and not 4 in o:
        g2.append(o)
        print o
print "with 3"
for o in output:
    if 3 in o:
        g3.append(o)
        print o
print "with 4"
for o in output:
    if 4 in o:
        g4.append(o)
        print o
print len(output)


class TileDraw(object):
    """"""
    def __init__(self):
        """"""
        # Lookup table for gradients
        # [-2, -1, 0, 1, 2]
        # Transformed to [0,1,2,3,4] by +2
        self.start_0A = [self.up_x, self.up_3x4, self.up_x2, self.up_x4, self.up_0]
        self.start_0B = [self.down_0, self.down_x4, self.down_x2, self.down_3x4, self.down_x]
        self.start_1 = [self.up_0, self.up_x4, self.up_x2, self.up_3x4, self.up_x]
        self.start_2A = [self.up_x, self.up_3x4, self.up_x2, self.up_x4, self.up_0]
        self.start_2B = [self.down_0, self.down_x4, self.down_x2, self.down_3x4, self.down_x]
        self.start_3 = [self.down_x, self.down_3x4, self.down_x2, self.down_x4, self.down_0]
        self.start_C = [self.up_x2, self.up_x3, self.up_x4, self.up_x8, self.up_0, self.down_x8, self.down_x4, self.down_x3, self.down_x2]
    def up_x(self, x):
        return x
    def up_3x4(self, x):
        return int(math.ceil(x/2.0) + math.floor(x/4.0))
    def up_x2(self, x):
        return x / 2
    def up_x3(self, x):
        return x / 3
    def up_x4(self, x):
        return x / 4
    def up_x8(self, x):
        return x / 8
    def up_0(self, x):
        return 0
    def down_x(self, x):
        return - self.up_x(x)
    def down_3x4(self, x):
        return - self.up_3x4(x)
    def down_x2(self, x):
        return - self.up_x2(x)
    def down_x3(self, x):
        return - self.up_x3(x)
    def down_x4(self, x):
        return - self.up_x4(x)
    def down_x8(self, x):
        return - self.up_x8(x)
    def down_0(self, x):
        return - self.up_0(x)
    def draw_tile(self, p, pix, offx, offy, tile):
        """Draw a tile on the supplied pixel buffer"""
        self.p = p
        self.pix = pix
        self.offx = offx
        self.offy = offy
        # Determine which way around the tile is to be drawn
        # Either left+right to middle, or top+bottom to sides
        # Then, call draw_segment for the two halves of the tile
        self.draw_segment(1, tile[1], tile[0], tile[2])
        self.draw_segment(3, tile[3], tile[0], tile[2])
        return
        if tile[0] == tile[2]:
            self.draw_segment(1, tile[1], tile[0], tile[2])
            self.draw_segment(3, tile[3], tile[0], tile[2])
        else:
            self.draw_segment(0, tile[0], tile[1], tile[3])
            self.draw_segment(2, tile[2], tile[1], tile[3])
    def draw_segment(self, start_corner, start_height, end_height_A, end_height_B):
        """"""
        # Work out line gradient for both
        gradient_A = start_height - end_height_A + 2
        gradient_B = start_height - end_height_B + 2
        # start_height (and other heights) can be in range 0 to 4
        # Start corner is either left, top, right or bottom (0, 1, 2 or 3)
        if start_corner == 0:
            # Starting at left, so end_height_A is top, end_height_B is bottom
            # Since we're starting at A, range is 32
            for x in range(0, 32):
                for y in range(self.offy + 48 - start_height * self.p/8 - self.start_0A[gradient_A](x), 
                               self.offy + 49 - start_height * self.p/8 - self.start_0B[gradient_B](x)):
                    self.pix[self.offx + x, y] = (200,0,0)

        elif start_corner == 1:
            # Left corner to top corner, bottom constrained to left-right midline
            gradient_C = end_height_A - end_height_B + 4
            gradient_D = end_height_B - end_height_A + 4
            for x in range(0, 32):
                for y in range(self.offy + 48 - end_height_A * self.p/8 - self.start_1[gradient_A](x), 
                               self.offy + 49 - end_height_A * self.p/8 - self.start_C[gradient_C](x)):
                    self.pix[self.offx + x, y] = (100,0,0)
            # Right corner to top corner, bottom constrained to left-right midline
            for x in range(32, 64):
                for y in range(self.offy + 48 - end_height_B * self.p/8 - self.start_1[gradient_B](63 - x), 
                               self.offy + 49 - end_height_B * self.p/8 - self.start_C[gradient_D](63 - x)):
                    self.pix[self.offx + x, y] = (100,0,0)

        elif start_corner == 2:
            # Starting at left, so end_height_A is top, end_height_B is bottom
            # Since we're starting at A, range is 32
            for x in range(32, 64):
                for y in range(self.offy + 48 - start_height * self.p/8 - self.start_0A[gradient_A](63 - x), 
                               self.offy + 49 - start_height * self.p/8 - self.start_0B[gradient_B](63 - x)):
                    self.pix[self.offx + x, y] = (0,0,200)
        else:
            return
            # Left corner to bottom corner, top constrained to left-right midline
            gradient_C = end_height_A - end_height_B + 4
            gradient_D = end_height_B - end_height_A + 4
            for x in range(0, 32):
                for y in range(self.offy + 48 - end_height_A * self.p/8 - self.start_C[gradient_C](x),
                               self.offy + 49 - end_height_A * self.p/8 - self.start_3[gradient_A](x)):
                    self.pix[self.offx + x, y] = (100,100,0)
            # Right corner to bottom corner, top constrained to left-right midline
            for x in range(32, 64):
                for y in range(self.offy + 48 - end_height_B * self.p/8 - self.start_C[gradient_D](63 - x), 
                               self.offy + 49 - end_height_B * self.p/8 - self.start_3[gradient_B](63 - x)):
                    self.pix[self.offx + x, y] = (100,100,0)

def draw_polygon(x, y):
    for xx in range(0,32):
        yval = (xx / 2)
        for yy in range(48 - yval, 49 + yval):
            outpix[xx + x*64, yy + y*64] = (0,255,0)
            outpix[63-xx + x*64, yy + y*64] = (0,255,0)

def draw_heights(x, y, h):
    draw.line([(0+x*64, 48+y*64), (0+x*64, 48+y*64-h[0]*8)], fill=(255,0,0))
    draw.line([(32+x*64, 33+y*64), (32+x*64, 33+y*64-h[1]*8)], fill=(255,0,0))
    draw.line([(63+x*64, 48+y*64), (63+x*64, 48+y*64-h[2]*8)], fill=(255,0,0))
    draw.line([(31+x*64, 63+y*64), (31+x*64, 63+y*64-h[3]*8)], fill=(255,0,0))

    draw.line([(0+x*64, 48+y*64-h[0]*8), (31+x*64, 33+y*64-h[1]*8)], fill=(0,0,255))
    draw.line([(32+x*64, 33+y*64-h[1]*8), (63+x*64, 48+y*64-h[2]*8)], fill=(0,0,200))
    draw.line([(63+x*64, 48+y*64-h[2]*8), (32+x*64, 63+y*64-h[3]*8)], fill=(0,0,160))
    draw.line([(31+x*64, 63+y*64-h[3]*8), (0+x*64, 48+y*64-h[0]*8)], fill=(0,0,120))


out = Image.new("RGB", (640, 640), (231,255,255))

outpix = out.load()

draw = ImageDraw.Draw(out)

oi = 0

tdraw = TileDraw()

for y in range(10):
    for x in range(10):
        draw_polygon(x, y)
        try:
            tdraw.draw_tile(64, outpix, x*64, y*64, output[oi])
            #draw_heights(x, y, output[oi])
        except IndexError:
            pass
        oi += 1


del draw

print "Saving to testout.png"
out.save("testout.png", "PNG")









