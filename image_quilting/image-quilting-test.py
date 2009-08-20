#!/usr/bin/python
# Development of image quilting algorythm implementation
# Test 1, Implement random tiling

import os, sys
import pygame
import random
import Image

# paksize
p = 64
w = 32

# Value of transparent
TRANSPARENT = (231,255,255)


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
