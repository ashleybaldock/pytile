#!/usr/bin/python
# Development of image quilting algorythm implementation
# Test 2, Mk.1 - Re-write system to output only two tiles
#                which will be fitted together using best-
#                fit algorythm and path of least error
# Test 2, Mk.3 - Implement cut path along two tiles

import os, sys
import pygame
import random
import Image
import math

# paksize
p = 64
# Width/height of tile fragment
w = 32
# Overlap
v = 6
# Number of tile-fragments (for wang-tile generation)
# X-dimension (left-right)
X = 2
# Y-dimension (top-bottom)
Y = 2
# Error threshold
R = 0.2
# Repitition (number of random tile combos to check)
rep = 1000

# Value of transparent
TRANSPARENT = (231,255,255)

# For all possible tiles in the source texture compare X number of tiles
# at the edges, if the overall error is below the error threshold, add
# this set of tiles to the list of possibles.

# Needs addition of code to do the path of least error cut for knitting
# together the images (probably do this by setting pixel transparencies
# before pasting one image onto another)


WangTiles = []
# ((Tile description), tile image number)
# top, left, bottom, right
WangTiles.append(((0,0,0,0), 0))     # 0
WangTiles.append(((1,1,1,1), 1))     # 14
WangTiles.append(((0,0,1,1), 2))     # 12
WangTiles.append(((1,1,0,0), 3))     # 3
WangTiles.append(((0,1,0,1), 4))     # 10
WangTiles.append(((1,0,1,0), 5))     # 5
WangTiles.append(((0,1,1,0), 6))     # 6
WangTiles.append(((1,0,0,1), 7))     # 9


# First, need a class which represents the input texture
class Texture:
    """Texture object for tiling"""    
    def __init__(self, rect=None, val=0):
        self.texture = pygame.image.load("texture3a.png")
        self.texture.set_alpha(None)
        self.texture = self.texture.convert()

        self.tex_x = self.texture.get_width()
        self.tex_y = self.texture.get_height()

        self.texture_pil = Image.fromstring("RGBX", (self.tex_x,self.tex_y), pygame.image.tostring(self.texture, "RGBX"))

    def CompareRegionError2(self, regions):
        """Compares two images to find the error between them"""
        reg1, type1, part1, reg2, type2, part2 = regions

        if type1 in [0,2]:
            region1 = self.tiles_X[reg1]
        else:
            region1 = self.tiles_Y[reg1]
        if type2 in [0,2]:
            region2 = self.tiles_X[reg2]
        else:
            region2 = self.tiles_Y[reg2]

        # Make pixel access objects
        r1 = region1.load()
        r2 = region2.load()

        # part1 of the form 0: top, 1: left, 2: bottom, 3: right
        if part1 == 0:      # top
            off_x1 = 0
            off_y1 = 0
            width = w
            height = v
        elif part1 == 1:    # left
            off_x1 = 0
            off_y1 = 0
            width = v
            height = w
        elif part1 == 2:    # bottom
            off_x1 = 0
            off_y1 = w - v
            width = w
            height = v
        elif part1 == 3:    # right
            off_x1 = w - v
            off_y1 = 0
            width = v
            height = w

        # part2 of the form 0: top, 1: left, 2: bottom, 3: right
        if part2 == 0:      # top
            off_x2 = 0
            off_y2 = 0
        elif part2 == 1:    # left
            off_x2 = 0
            off_y2 = 0
        elif part2 == 2:    # bottom
            off_x2 = 0
            off_y2 = w - v
        elif part2 == 3:    # right
            off_x2 = w - v
            off_y2 = 0

        # Now go through for all pixels and calculate the difference
        # between the two images

        diff_total = 0
        max_total = width * height * 255 * 3.0
        for x in range(width):
            for y in range(height):
                r1_r, r1_g, r1_b = r1[off_x1 + x, off_y1 + y]
                r2_r, r2_g, r2_b = r2[off_x2 + x, off_y2 + y]
                
                if r1_r > r2_r:
                    diff_r = r1_r - r2_r
                elif r1_r == r2_r:
                    diff_r = 0
                else:
                    diff_r = r2_r - r1_r

                if r1_g > r2_g:
                    diff_g = r1_g - r2_g
                elif r1_g == r2_g:
                    diff_g = 0
                else:
                    diff_g = r2_g - r1_g

                if r1_b > r2_b:
                    diff_b = r1_b - r2_b
                elif r1_b == r2_b:
                    diff_b = 0
                else:
                    diff_b = r2_b - r1_b

                # The smaller the value of diff_total, the smaller
                # the overall difference or error
##                diff_total = diff_total + (diff_r + diff_g + diff_b)
                diff_total = diff_total + math.sqrt((diff_r * diff_r) + (diff_g * diff_g) + (diff_b * diff_b))

        return diff_total

    def MakeWang(self):
        """Uses the texture to generate a set of wang tiles, by comparing
           the error value along the joins of random subsections from the
           source texture"""
        texture = Image.fromstring("RGBX", (self.texture.get_width(),self.texture.get_height()), pygame.image.tostring(self.texture, "RGBX"))

##        self.tiles_X = []
##        self.tiles_Y = []
        possibles = []


        error_list = []
        possible_list = []
        
        self.tiles_X = []
        self.tiles_X.append(Image.new("RGB",(w,w)))
        self.tiles_X.append(Image.new("RGB",(w,w)))

        self.tiles_Y = []
        self.tiles_Y.append(Image.new("RGB",(w,w)))
        self.tiles_Y.append(Image.new("RGB",(w,w)))

        for s in range(rep):
            # Generate 4 sets of coordinates for the 4 random patches of texture
            # These are stored each time in the possibles array
            possibles = []
            for i in range(X + Y):
                possibles.append((random.randint(0, self.tex_x - w), random.randint(0, self.tex_y - w)))

            # Now actually crop those sections out of the texture and store them in two lists
            # one for X and one for Y
            for i in range(X):
                a = texture.crop((possibles[i][0], possibles[i][1], possibles[i][0] + w, possibles[i][1] + w))
                self.tiles_X[i].paste(a,(0,0,w,w))

            for i in range(Y):
                a = texture.crop((possibles[i+X][0], possibles[i+X][1], possibles[i+X][0] + w, possibles[i+X][1] + w))
                self.tiles_Y[i].paste(a,(0,0,w,w))


            # Comparisons are added to a list, which keeps track of what has
            # been compared, comparisons are tuples of form:
            #   (X, direction, Y, direction, comp_error)
            # Where X is which X tile it is, Y is which Y tile it is
            # and direction indicates the edge of X and Y which are compared
            # (i.e. 0: top, 1: left, 2: bottom, 3: right
            # comp_error is the comparison error value obtained, this needs to
            # be added to the running total for each instance of this comparison

            # For each WangTile in the WangTiles list, perform all comparisons
            # between the tiles in the relavent arrays (unless this test has
            # already been performed, in which case skip it)


            # Test with just two tiles
            # Optimizing so that the right/left edges match up

            skip_list = []
            skip_error = []
            total_error = 0
            for i in range(len(WangTiles)):

                # top, left, bottom, right
                tile = WangTiles[i][0]
                comparison = []
                # comp AB
                #               tile varient number, X or Y type, comparison type
                comparison.append((tile[0], 0, 2, tile[1], 1, 0))
                # comp BC
                comparison.append((tile[1], 1, 3, tile[2], 2, 1))
                # comp CD
                comparison.append((tile[2], 2, 0, tile[3], 3, 2))
                # comp DA
                comparison.append((tile[3], 3, 1, tile[0], 0, 3))
                for j in range(4):
                    if comparison[j] in skip_list:
                        total_error = total_error + skip_error[skip_list.index(comparison[j])]
                    else:
                        skip_list.append(comparison[j])
                        error = self.CompareRegionError2(comparison[j])
                        total_error = total_error + error
                        skip_error.append(error)

                error_list.append(total_error)
                possible_list.append(possibles)


        sel = min(error_list)
        k = error_list.index(sel)
        possibles = possible_list[k]

        for i in range(X):
            a = texture.crop((possibles[i][0], possibles[i][1], possibles[i][0] + w, possibles[i][1] + w))
            self.tiles_X[i].paste(a,(0,0,w,w))

        for i in range(Y):
            a = texture.crop((possibles[i+X][0], possibles[i+X][1], possibles[i+X][0] + w, possibles[i+X][1] + w))
            self.tiles_Y[i].paste(a,(0,0,w,w))

        # Go through blitting all the wang tiles formed by these input tiles
        # to the example output image
        ret = pygame.Surface((w*2*(len(WangTiles)),w*2))
        for i in range(len(WangTiles)):
            aa = pygame.image.frombuffer((self.tiles_X[WangTiles[i][0][0]].tostring()), (w,w), "RGB")
            ret.blit(aa, (0+(i*w*2),0))
            aa = pygame.image.frombuffer((self.tiles_Y[WangTiles[i][0][1]].tostring()), (w,w), "RGB")
            ret.blit(aa, (0+(i*w*2),w-v))
            aa = pygame.image.frombuffer((self.tiles_Y[WangTiles[i][0][2]].tostring()), (w,w), "RGB")
            ret.blit(aa, (w-v+(i*w*2),0))
            aa = pygame.image.frombuffer((self.tiles_X[WangTiles[i][0][3]].tostring()), (w,w), "RGB")
            ret.blit(aa, (w-v+(i*w*2),w-v))


##    WangTiles.append(((0,0,0,0), 0))     # 0

##        # If the error is below the threshold, return this tile for blitting
##        ret = pygame.Surface((w*2,w*2))
##        aa = pygame.image.frombuffer((self.tiles_X[0].tostring()), (w,w), "RGB")
##        ret.blit(aa, (0,0))
##        aa = pygame.image.frombuffer((self.tiles_Y[0].tostring()), (w,w), "RGB")
##        ret.blit(aa, (0,w-v))
##        aa = pygame.image.frombuffer((self.tiles_Y[1].tostring()), (w,w), "RGB")
##        ret.blit(aa, (w-v,0))
##        aa = pygame.image.frombuffer((self.tiles_X[1].tostring()), (w,w), "RGB")
##        ret.blit(aa, (w-v,w-v))

        return ret

##            for i in range(len(WangTiles)):
##                print str(i)
##                # top, left, bottom, right
##                tile = WangTiles[i][0]
##                comparison = []
##                # comp AB
##                #               tile varient number, X or Y type, comparison type
##                comparison.append((tile[0], 0, 2, tile[1], 1, 0))
##                # comp BC
##                comparison.append((tile[1], 1, 3, tile[2], 2, 1))
##                # comp CD
##                comparison.append((tile[2], 2, 0, tile[3], 3, 2))
##                # comp DA
##                comparison.append((tile[3], 3, 1, tile[0], 0, 3))
##                for j in range(4):
##                    if comparison[j] in skip_list:
##                        total_error = total_error + skip_error[skip_list.index(comparison[j])]
##                    else:
##                        skip_list.append(comparison[j])
##                        error = self.CompareRegionError2(comparison[j])
##                        total_error = total_error + error
##                        skip_error.append(error)
            
##            possibles.append()
            
##            # If the error is below the threshold, return this tile for blitting
##            if total_error < 800000:
##                ret = pygame.Surface((w*2,w*2))
##                aa = pygame.image.frombuffer((self.tiles_X[0].tostring()), (w,w), "RGB")
##                ret.blit(aa, (0,0))
##                aa = pygame.image.frombuffer((self.tiles_Y[0].tostring()), (w,w), "RGB")
##                ret.blit(aa, (0,w-v))
##                aa = pygame.image.frombuffer((self.tiles_Y[1].tostring()), (w,w), "RGB")
##                ret.blit(aa, (w-v,0))
##                aa = pygame.image.frombuffer((self.tiles_X[1].tostring()), (w,w), "RGB")
##                ret.blit(aa, (w-v,w-v))
##
##                return ret
            

##    WangTiles = []
##    # ((Tile description), tile image number)
##    # top, left, bottom, right
##    WangTiles.append(((0,0,0,0), 0))     # 0
##    WangTiles.append(((1,1,1,1), 1))     # 14
##    WangTiles.append(((0,0,1,1), 2))     # 12
##    WangTiles.append(((1,1,0,0), 3))     # 3
##    WangTiles.append(((0,1,0,1), 4))     # 10
##    WangTiles.append(((1,0,1,0), 5))     # 5
##    WangTiles.append(((0,1,1,0), 6))     # 6
##    WangTiles.append(((1,0,0,1), 7))     # 9

##        for i in range(self.tex_x - w):
##            for j in range(self.tex_y - w):
##                # First compare left
##                r2 = self.texture_pil.crop((i, j, i + v, j + w))
##                reg2 = Image.new("RGB",(v,w))
##                reg2.paste(r2,(0,0,v,w))
##
##                r1 = self.GetSurfaceToCompare(x_pos, y_pos, existing_pil)
##                reg1 = Image.new("RGB",(v,w))
##                reg1.paste(r1,(0,0,v,w))
##
##                error1 = self.CompareRegionError(reg1, reg2)








class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

    def __init__(self, width=800,height=600):
        # Initialize PyGame
        pygame.init()
        
        # Set the window Size
        self.width = width
        self.height = height
        
        # Create the Screen
        self.screen = pygame.display.set_mode((self.width
                                               , self.height), pygame.RESIZABLE)
        
        self.dxoff = 0
        self.dyoff = 0
        
        # Init classes
        self.texture = Texture()

    def MainLoop(self):
        """This is a testing loop to display the output of the rendering tests"""

        # Create the background
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        #self.background.set_colorkey((231,255,255))
        #self.background.fill((0,0,0))

        
        # Find the width and height of the screen as multiples of w
##        tiles_wide = self.width / (w - v)
##        tiles_high = self.height / (w - v)
        tiles_wide = 4
        tiles_high = 5

        #array = self.MakeTileArray(tiles_high, tiles_wide)

        self.background.blit(self.texture.MakeWang(), (0,0))
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
                
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "r":
                        self.background.fill((0,0,0))
                        self.background.blit(self.texture.MakeWang(), (0,0))
                        self.screen.blit(self.background, (0, 0))
                        pygame.display.flip()

                else:
                    self.screen.blit(self.background, (0, 0))

                    pygame.display.flip()

                    pygame.time.wait(100)

if __name__ == "__main__":

    MainWindow = DisplayMain()
    MainWindow.MainLoop()

