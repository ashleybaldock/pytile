#!/usr/bin/python
#This will be a test of the ground display system

import os, sys
import pygame
import random

p = 64
ph = 8

class Tile(pygame.sprite.Sprite):
    """Contains all ground-related tiles, needs rendering system"""
    image = None
    
    def __init__(self, rect=None, val=0):

        # All sprite classes should extend pygame.sprite.Sprite. This
        # gives you several important internal methods that you probably
        # don't need or want to write yourself. Even if you do rewrite
        # the internal methods, you should extend Sprite, so things like
        # isinstance(obj, pygame.sprite.Sprite) return true on it.
        pygame.sprite.Sprite.__init__(self)
        if Tile.image is None:
            Tile.image = pygame.image.load("ground.png")
            Tile.image.convert_alpha()
            Tile.tile_images = []
            for i in range(0,15):
                Tile.tile_images.append(pygame.Surface((p,p), pygame.HWSURFACE, Tile.image))
                Tile.tile_images[i].blit(Tile.image, (0,0), ((i * p), 0, p,p))
                
            Tile.tile_images.append(pygame.Surface((p,p), pygame.HWSURFACE, Tile.image))
            Tile.tile_images[15].blit(Tile.image, (0,0), ((0 * p), (6 * p), p,p))
            
            Tile.tile_images.append(pygame.Surface((p,p), pygame.HWSURFACE, Tile.image))
            Tile.tile_images[16].blit(Tile.image, (0,0), ((14 * p), (8 * p), p,p))
        # Pre-load this sprite's image, so that it is only loaded once
        self.image = Tile.tile_images[val]
        self.rect = self.image.get_rect()
        
        if rect != None:
            self.rect = rect

class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

                    # Display variables (need moving to world class?)
    dxoff = 0     # Horizontal offset position of the displayed area of the map
    dyoff = 0     # Vertical offset (from top) of the displayed area of the map
    x_dist = 20     # Distance to move the screen when arrow keys are pressed
    y_dist = 20     # in x and y dimensions
    
        
    def __init__(self, width=640,height=480):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        """Set the window Size"""
        self.width = width
        self.height = height
        """Create the Screen"""
        self.screen = pygame.display.set_mode((self.width
                                               , self.height))

        self.tile_array = self.MakeArray()   # array of tiles, make or load
        self.WorldX = len(self.tile_array[0])
        self.WorldY = len(self.tile_array)
        self.textitems = []

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        """Load All of our Sprites"""
        self.LoadSprites()
        self.PaintScreen()
        
        """tell pygame to keep sending up keystrokes when they are
        held down"""
        pygame.key.set_repeat(500, 30)
        
        """Create the background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0,0,0))
        
        #Must ensure mouse is over screen (needs fixing properly)
        pygame.mouse.set_pos(((self.background.get_width()/2),(self.background.get_height()/2)))

        while 1:
            blit_all = 0
            self.screen.blit(self.background, (0, 0))
            self.textitems = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if ((event.key == pygame.K_RIGHT)
                    or (event.key == pygame.K_LEFT)
                    or (event.key == pygame.K_UP)
                    or (event.key == pygame.K_DOWN)):
                        self.MoveScreen(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    # When the mouse is moved, check to see if...
                    b = event.buttons
                    
                    if pygame.font:
                        font = pygame.font.Font(None, 24)
                        self.textitems.append(font.render("Mouse State: " + str(b), 1, (255, 255, 255)))

                    #if pygame.font:
                        #font = pygame.font.Font(None, 24)
                        #text = font.render("Mouse State: " + str(b), 1, (255, 255, 255))
                        #textpos = text.get_rect(centerx=self.background.get_width()/2)
                        #self.screen.blit(text, textpos)


                    #pygame.event.event_name()
                        # Is the right mouse button held? If so, do scrolling & refresh whole screen
                    if (event.buttons == (0,0,1)):
                        self.MoveScreen("mouse")
                        blit_all = 1
                        # Is the left mouse button held? If so, interact with tile
                    
                        # If neither mouse button held, then simply
                        # check which tile is active, and highlight it
                    else:
                        pygame.mouse.get_rel()  #Reset mouse position for scrolling
                        self.HighlightTile()
                        
                        
            #self.screen.blit(self.background, (0, 0))
            self.tile_sprites.draw(self.screen)
            self.water_sprites.draw(self.screen)
            #self.screen.blit(text, textpos)
            if pygame.font:
                font = pygame.font.Font(None, 24)
                for j in range(len(self.textitems)):
                    self.screen.blit(self.textitems[j], (0,j*24))

            self.highlight.draw(self.screen)
            pygame.display.flip()

    def TileSiblings(self, xy=(0,0)):
        """Returns the 8 tiles surrounding the given tile"""
        x, y = xy

        siblings = []
        siblings.append(self.tile_array[x - 1][y - 1])
        siblings.append(self.tile_array[x - 1][y])
        siblings.append(self.tile_array[x - 1][y + 1])
        siblings.append(self.tile_array[x][y - 1])
        #siblings.append(self.array[x][y])
        siblings.append(self.tile_array[x][y + 1])
        siblings.append(self.tile_array[x + 1][y - 1])
        siblings.append(self.tile_array[x + 1][y])
        siblings.append(self.tile_array[x + 1][y + 1])

        return siblings
        
    def MakeArray2(self):
        TileMap = [[(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   [(0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), 
                    (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14), (0,14)],
                   ]
        return(TileMap)

    def MakeArray(self):
        TileMap = []
        for i in range(20):
            a = []
            for j in range(20):
                if j > 5 and j < 10:
                    if i > 5 and i < 10:
                        a.append((1,14))
                    elif i == 5:
                        a.append((0,1))
                    elif i == 10:
                        a.append((0,3))
                    else:
                        a.append((0,14))
                elif j == 5:
                    if i > 5 and i < 10:
                        a.append((0,0))
                    elif i == 5:
                        a.append((0,5))
                    elif i == 10:
                        a.append((0,4))
                    else:
                        a.append((0,14))
                elif j == 10:
                    if i > 5 and i < 10:
                        a.append((0,2))
                    elif i == 5:
                        a.append((0,6))
                    elif i == 10:
                        a.append((0,7))
                    else:
                        a.append((0,14))
                else:
                    a.append((0,14))
                    
            TileMap.append(a)
        return(TileMap)


    def LoadSprites(self):
        """Load the sprites that we need"""
        #self.array = self.MakeArray()


        #[Initialise map method - excerpt]
        #-- basic info about the tile size
        #p = 64
        #X and Y dims of array
        #WorldX = len(self.array)
        #WorldY = len(self.array[1])
        #Vertical offset from top of window
        #WorldVerticalOffset = 64
        #Overall size of iso-world
        #IsoWidth = WorldX * (p/2) + WorldY * (p/2)
        #IsoHeight = WorldX * (p/2) + WorldY * (p/2) + WorldVerticalOffset
        #Horizontal position of first tile
        #hOffset = IsoWidth/2
        
        self.tile_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.highlight = pygame.sprite.Group()

        #for x in range(9):
        #    for y in range(9):
        #        self.tile_sprites.add(Tile(pygame.Rect(((hOffset - y*(p/2)) + x*(p)), y*(p/4), p, p)))

    def MoveScreen(self, key):
        if (key == pygame.K_RIGHT):
            self.dxoff = self.dxoff + self.x_dist
        elif (key == pygame.K_LEFT):
            self.dxoff = self.dxoff - self.x_dist
        elif (key == pygame.K_UP):
            self.dyoff = self.dyoff - self.y_dist
        elif (key == pygame.K_DOWN):
            self.dyoff = self.dyoff + self.y_dist
        if (key == "mouse"):
            b = pygame.mouse.get_rel()
            self.dxoff = self.dxoff + b[0]
            self.dyoff = self.dyoff + b[1]
            
        #pygame.mouse.set_pos(((self.background.get_width()/2),(self.background.get_height()/2)))
        #pygame.mouse.get_rel()
        
        self.PaintScreen()

    def ScreenToIso(self, wxy=(0,0)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        TileRatio = 2
        wx, wy = wxy
        # Figure inversion owing to problems elsewhere in drawing
        # Probably swapped axes for Iso
        wx = 640 - wx
        wy = 480 - wy
        wx = self.dxoff - wx
        wy = self.dyoff - wy
        dx = wx - p
        dy = wy + (p/2)
        # Don't really understand how this bit works...
        x = int((dy + dx / TileRatio) * (TileRatio / 2) / (p/2))
        y = int((dy - dx / TileRatio) * (TileRatio / 2) / (p/2))
        if x < 0 or y < 0:
            return (0,0)
        if x >= (self.WorldX) or y >= (self.WorldY):
            return (0,0)
        
        return (x,x)


    def HighlightTile(self, iso_coords=(0,0)):
        """Highlight a particular tile, takes one argument:
        iso_coords - coords of tile to highlight"""
        isopos = self.ScreenToIso(pygame.mouse.get_pos())
        x, y = isopos
        self.highlight.empty()
        tohighlight = self.TileSiblings(isopos)


        #siblings.append(self.array[x - 1][y - 1])
        #siblings.append(self.array[x - 1][y])
        #siblings.append(self.array[x - 1][y + 1])
        #siblings.append(self.array[x][y - 1])
        #siblings.append(self.array[x][y])
        #siblings.append(self.array[x][y + 1])
        #siblings.append(self.array[x + 1][y - 1])
        #siblings.append(self.array[x + 1][y])
        #siblings.append(self.array[x + 1][y + 1])

        
        for a in range(len(tohighlight)):
            for xx in range(-1,2):
                for yy in range(-1,2):
                    ypos = self.dyoff - ((x + xx) * (p/4)) - ((y + yy) * (p/4)) - (self.tile_array[(x + xx)][(y + yy)][0] * ph)
                    xpos = self.dxoff - ((x + xx) * (p/2)) + ((y + yy) * (p/2))
                    self.highlight.add(Tile(pygame.Rect(xpos, ypos, p, p), 16))
            
        #self.highlight.add(Tile(pygame.Rect(xpos, ypos, p, p), 16))
        #ypos = self.dyoff - (x * (p/4)) - (y * (p/4)) - (self.tile_array[x][y][0] * ph)
        #xpos = self.dxoff - (x * (p/2)) + (y * (p/2))

    def PaintScreen(self):
        self.tile_sprites.empty()
        for x in range(self.WorldX):
            for y in range(self.WorldY):
                #Vertical offset from top - y*1/2p - x*1/2p
                ypos = self.dyoff - (x * (p/4)) - (y * (p/4)) - (self.tile_array[x][y][0] * ph)
                xpos = self.dxoff - (x * (p/2)) + (y * (p/2))
                self.tile_sprites.add(Tile(pygame.Rect(xpos, ypos, p, p), self.tile_array[x][y][1]))

        self.water_sprites.empty()

#        for x in range(self.WorldX):
#            for y in range(self.WorldY):
#                #Vertical offset from top - y*1/2p - x*1/2p
#                ypos = self.dyoff - (x * (p/4)) - (y * (p/4)) - ((self.tile_array[x][y][0] + 1) * ph)
#                xpos = self.dxoff - (x * (p/2)) + (y * (p/2))
#                self.water_sprites.add(Tile(pygame.Rect(xpos, ypos, p, p), 15))


        for x in range(20):
            for y in range(20):
                if y < 6 or y > 9:
                    ypos = self.dyoff - (x * (p/4)) - (y * (p/4)) - (1 * ph)
                    xpos = self.dxoff - (x * (p/2)) + (y * (p/2))
                    self.water_sprites.add(Tile(pygame.Rect(xpos, ypos, p, p), 15))
                elif x < 6 or x > 9:
                    ypos = self.dyoff - (x * (p/4)) - (y * (p/4)) - (1 * ph)
                    xpos = self.dxoff - (x * (p/2)) + (y * (p/2))
                    self.water_sprites.add(Tile(pygame.Rect(xpos, ypos, p, p), 15))

if __name__ == "__main__":
    MainWindow = DisplayMain()
    MainWindow.MainLoop()











    
