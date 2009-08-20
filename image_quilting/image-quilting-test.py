#!/usr/bin/python
# Development of image quilting algorythm implementation
# Test 1, Mk.2 - Implement random tiling
# Test 1, Mk.3 - Implement overlapping tiles
# Test 1, Mk.4 - Optimization
# Test 1, Mk.5 - Implement 2-D overlapping tiles (y dimension also)

import os, sys
import pygame
import random
import Image

# paksize
p = 64
# Width/height of tile fragment
w = 32
# Overlap
v = 5

# Value of transparent
TRANSPARENT = (231,255,255)


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

    def CompareRegionError(self, region1, region2):
        """Compares two surfaces to find the error between them"""
##        # Convert to PIL format
##        region1 = Image.fromstring("RGBX", (v,w), pygame.image.tostring(region1a, "RGBX"))
##        region2 = Image.fromstring("RGBX", (v,w), pygame.image.tostring(region2a, "RGBX"))
        
##        # The two regions must be of the same size, else this will fail
##        if region1.size != region2.size:
##            return 1

        width, height = region1.size

        # Make pixel access objects
        r1 = region1.load()
        r2 = region2.load()

        # Now go through for all pixels and calculate the difference
        # between the two images
        
        diff_total = 0
        max_total = width * height * 255 * 3.0
        for x in range(width):
            for y in range(height):
                r1_r, r1_g, r1_b = r1[x,y]
                r2_r, r2_g, r2_b = r2[x,y]
                
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
                diff_total = diff_total + (diff_r + diff_g + diff_b)

        percent_error = diff_total / max_total
        return percent_error

##        # Now convert back to pygame format
##        region1 = pygame.image.frombuffer((region1.tostring()), (p,p), "RGBX")
##        region2 = pygame.image.frombuffer((region2.tostring()), (p,p), "RGBX")

    def GetSurfaceToCompare(self, x, y, existing):
        """Gets the right shaped bit from the output image to compare
        to the next square"""
##        a = pygame.Surface((v,w))
##        a.blit(existing, (0,0), ((x*w)-(x*v),(y*w)-(y*v), (x*w)-(x*v)+v,(y*w)-(y*v)+w))
        a = existing.crop(((x*w)-(x*v),(y*w)-(y*v), (x*w)-(x*v)+v,(y*w)-(y*v)+w))

        return a

    def GetRegion(self, x, y, x_pos, y_pos, existing):
        """Returns a square of texture which will neatly match with the existing
        texture available"""
        bleh = 0

        existing_pil = Image.fromstring("RGBX", (existing.get_width(),existing.get_height()), pygame.image.tostring(existing, "RGBX"))

        # If x is 0, this is the top row, so only compare
        # the left values
        if x_pos == 0:
            # If x and y are 0, this is the top-left corner,
            # thus pick a start tile at random
            if y_pos == 0:
                ret = pygame.Surface((x,y))
                from_x = random.randint(0, self.tex_x - x)
                from_y = random.randint(0, self.tex_y - y)
                ret.blit(self.texture, (0,0), (from_x, from_y, from_x + x, from_y + y))
                return ret
            # Otherwise, compare only the left-hand overlap
            else:
                # If x is 0 then this is the left-most column,
                # thus only consider the top overlap
                possible_list = []
                error_list = []
                for i in range(self.tex_x - w):
                    for j in range(self.tex_y - w):
                        r2 = self.texture_pil.crop((i, j, i + w, j + v))
                        reg2 = Image.new("RGB",(w,v))
                        reg2.paste(r2,(0,0,w,v))

                        r1 = existing_pil.crop(((x_pos*w)-(x_pos*v),(y_pos*w)-(y_pos*v), (x_pos*w)-(x_pos*v)+w,(y_pos*w)-(y_pos*v)+v))
                        reg1 = Image.new("RGB",(w,v))
                        reg1.paste(r1,(0,0,w,v))

                        error = self.CompareRegionError(reg1, reg2)

                        possible_list.append((i, j))
                        error_list.append(error)
        else:
            if y_pos == 0:
                possible_list = []
                error_list = []
                for i in range(self.tex_x - w):
                    for j in range(self.tex_y - w):
                        r2 = self.texture_pil.crop((i, j, i + v, j + w))
                        reg2 = Image.new("RGB",(v,w))
                        reg2.paste(r2,(0,0,v,w))

                        r1 = self.GetSurfaceToCompare(x_pos, y_pos, existing_pil)
                        reg1 = Image.new("RGB",(v,w))
                        reg1.paste(r1,(0,0,v,w))

                        error = self.CompareRegionError(reg1, reg2)

                        possible_list.append((i, j))
                        error_list.append(error)

            # Otherwise, consider both top and left overlaps
            else:
                possible_list = []
                error_list = []
                for i in range(self.tex_x - w):
                    for j in range(self.tex_y - w):
                        # First compare left
                        r2 = self.texture_pil.crop((i, j, i + v, j + w))
                        reg2 = Image.new("RGB",(v,w))
                        reg2.paste(r2,(0,0,v,w))

                        r1 = self.GetSurfaceToCompare(x_pos, y_pos, existing_pil)
                        reg1 = Image.new("RGB",(v,w))
                        reg1.paste(r1,(0,0,v,w))

                        error1 = self.CompareRegionError(reg1, reg2)

                        # Now compare the top
                        r2 = self.texture_pil.crop((i, j, i + w, j + v))
                        reg2 = Image.new("RGB",(w,v))
                        reg2.paste(r2,(0,0,w,v))

                        r1 = existing_pil.crop(((x_pos*w)-(x_pos*v),(y_pos*w)-(y_pos*v), (x_pos*w)-(x_pos*v)+w,(y_pos*w)-(y_pos*v)+v))
                        reg1 = Image.new("RGB",(w,v))
                        reg1.paste(r1,(0,0,w,v))

                        error2 = self.CompareRegionError(reg1, reg2)

                        possible_list.append((i, j))
                        error_list.append(error1 + error2)


        sel = min(error_list)
        k = error_list.index(sel)
##            k = random.randint(0,len(error_list))
        si, sj = possible_list[k]
        
        ret = pygame.Surface((x,y))
        ret.blit(self.texture, (0,0), (si, sj, si + x, sj + y))

        return ret

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

        for y in range(tiles_high):
            for x in range(tiles_wide):

##                self.background.blit(self.texture.GetRegion(w,w, x, y, self.background.copy()), ((x*w),(y*w)))
                self.background.blit(self.texture.GetRegion(w,w, x, y, self.background), ((x * w) - (x * v),(y * w) - (y * v)))
                self.screen.blit(self.background, (0, 0))
                pygame.display.flip()
                
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "r":
                        self.background.fill((0,0,0))
                        for x in range(tiles_wide):
                            for y in range(tiles_high):

                                self.background.blit(self.texture.GetRegion(w,w, x, y, self.background), ((x * w) - (x * v),(y * w) - (y * v)))
                                self.screen.blit(self.background, (0, 0))
                                pygame.display.flip()

                else:
                    self.screen.blit(self.background, (0, 0))

                    pygame.display.flip()

                    pygame.time.wait(100)

if __name__ == "__main__":

    MainWindow = DisplayMain()
    MainWindow.MainLoop()
