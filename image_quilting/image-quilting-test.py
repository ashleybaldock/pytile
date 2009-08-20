#!/usr/bin/python
# Development of image quilting algorythm implementation
# Test 1, Mk.2 - Implement random tiling

import os, sys
import pygame
import random
import Image

# paksize
p = 64
# Width of tile fragment
w = 32
# Overlap
v = 5

# Value of transparent
TRANSPARENT = (231,255,255)


# First, need a class which represents the input texture
class Texture:
    """A texture object, has methods related to it"""    
    def __init__(self, rect=None, val=0):
        self.texture = pygame.image.load("texture3a.png")
        self.texture.set_alpha(None)
        self.texture = self.texture.convert()
        self.tex_x = self.texture.get_width()
        self.tex_y = self.texture.get_height()
    def GetRegion(self, x, y):
        ret = pygame.Surface((x,y))
        from_x = random.randint(0, self.tex_x - x)
        from_y = random.randint(0, self.tex_y - y)
        ret.blit(self.texture, (0,0), (from_x, from_y, from_x + x, from_y + y))

        return ret

class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

    def __init__(self, width=1024,height=600):
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

        """Create the background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        #self.background.set_colorkey((231,255,255))
        #self.background.fill((0,0,0))

        
        # Find the width and height of the screen as multiples of w
        tiles_wide = self.width / w
        tiles_high = self.height / w

        #array = self.MakeTileArray(tiles_high, tiles_wide)

        for x in range(tiles_high):
            for y in range(tiles_wide):

                self.background.blit(self.texture.GetRegion(w,w), ((y * w),(x * w)))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()



            self.screen.blit(self.background, (0, 0))

            pygame.display.flip()

            pygame.time.wait(100)

if __name__ == "__main__":

    MainWindow = DisplayMain()
    MainWindow.MainLoop()
