#!/usr/bin/python
#Second test of the ground display system

import os, sys
import pygame
import random

#paksize
p = 64

#tile height difference
ph = 8

class Tile(pygame.sprite.Sprite):
    """All types of ground tile"""
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
            Tile.tile_images[16].blit(Tile.image, (0,0), ((0 * p), (1 * p), p,p))
        # Pre-load this sprite's image, so that it is only loaded once
        self.image = Tile.tile_images[val]
        self.rect = self.image.get_rect()
        
        if rect != None:
            self.rect = rect

class World:
    """Holds all world-related variables and methods"""

                    # Display variables (need moving to world class?)
    dxoff = 0       # Horizontal offset position of displayed area
    dyoff = 0       # Vertical offset (from top)

    def __init__(self, width=640,height=480):
        self.dxoff = 0
        self.dyoff = 0

    def MakeArray(self):
        #TileMap = []

        TileMap = [[[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [1,14], [1,14], [1,14], [0,14], [0,14], [0,14], [0,14], [1,14], [1,14], [1,14], [1,14], [1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [1,14], [1,14], [1,14], [0,14], [0,14], [0,14], [0,14], [1,14], [2,14], [2,14], [2,14], [1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [1,14], [1,14], [1,14], [1,14], [1,14], [0,14], [0,14], [1,14], [2,14], [2,14], [2,14], [1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [1,14], [1,14], [1,14], [0,14], [0,14], [1,14], [2,14], [2,14], [2,14], [1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [1,14], [1,14], [1,14], [0,14], [0,14], [1,14], [1,14], [1,14], [1,14], [1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [-1,14], [-1,14], [-1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [-1,14], [-1,14], [-1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [-1,14], [-1,14], [-1,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                   [[0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14], [0,14]],
                    ]


##        for i in range(20):
##            a = []
##            for j in range(20):
##                if j > 3 and j < 7:
##                    if i > 3 and i < 7:
##                        a.append([2,14])
##                    else:
##                        a.append([1,14])
##                elif j > 5 and j < 9:
##                    if i > 5 and i < 9:
##                        a.append([2,14])
##                    else:
##                        a.append([1,14])
##
##                elif j > 10 and j < 14:
##                    if i > 10 and i < 14:
##                        a.append([0,14])
##                    else:
##                        a.append([1,14])
##
##                else:
##                    a.append([1,14])
##            TileMap.append(a)

        # Find correct slopes - slopes will belong to the higher terrain level
        # Go through all tiles, and check to see if any slopes are required (change in height
        # between tile and its neighbours) if so, assign correct slope type
        # to the tile in question
        SecondMap = []
        for x in range(len(TileMap[0])):
            a = []
            for y in range(len(TileMap)):
                a.append([0,0])
            SecondMap.append(a)
                
        for x in range(len(TileMap[0])):
            for y in range(len(TileMap)):
                SecondMap[x][y][0], SecondMap[x][y][1] = self.Test9(TileMap, x, y)

        return(SecondMap)

    def Test9(self, array, x, y):

        # Check to see if tile is at edge of map, this needs a special case
        if x == 0 or y == 0:
            # Check special corner cases
            if x == 0 and y == 0:
                return((array[x][y][0], 14))
            elif x == 0 and y == (len(array)-1):
                return((array[x][y][0], 14))
            elif x == (len(array[0])-1) and y == 0:
                return((array[x][y][0], 14))
            else:
                return((array[x][y][0], 14))
        # to see if the tile is at the other edges of the map...
        elif x == (len(array[0])-1) or y == (len(array)-1):
            # Last special corner case
            if x == (len(array[0])-1) and y == (len(array)-1):
                return((array[x][y][0], 14))
            else:
                return((array[x][y][0], 14))
        # Otherwise use the general tests
        else:
            # Straight slopes (high)
            # Needs some sort of more generic system for this really...

            # Rules to deal with cases where land needs to be raised
            # in these cases we really need to re-do all the calcs for the
            # surrounding tiles, to give a degree of recursivity
            if self.TestRule(self.TileSiblings(array, x, y), [2,2,2,
                                                              1,0,1,
                                                              2,2,2,], 0) == 1:
                #self.Test9(array, x, y)
                return((array[x][y][0] + 1, 14))
            if self.TestRule(self.TileSiblings(array, x, y), [2,2,2,
                                                              1,0,1,
                                                              2,2,2,], 3) == 3:
                return((array[x][y][0] + 1, 14))


            # Group 1 ----------------------------------------------
            if self.TestRule(self.TileSiblings(array, x, y), [2,0,2,
                                                              1,0,2,
                                                              2,0,2,], 0) == 1:
                return((array[x][y][0], 0))
            if self.TestRule(self.TileSiblings(array, x, y), [2,0,2,
                                                              1,0,2,
                                                              2,0,2,], 1) == 2:
                return((array[x][y][0], 2))
            if self.TestRule(self.TileSiblings(array, x, y), [2,0,2,
                                                              1,0,2,
                                                              2,0,2,], 3) == 3:
                return((array[x][y][0], 1))
            if self.TestRule(self.TileSiblings(array, x, y), [2,0,2,
                                                              1,0,2,
                                                              2,0,2,], 5) == 5:
                return((array[x][y][0], 3))


            else:
                return((array[x][y][0], 14))
## Check:
## (x-1),(y-1)
## (x-1),y
## (x-1),(y+1)
## x,(y-1)
## x,y
## x,(y+1)
## (x+1),(y-1)
## (x+1),y
## (x+1),(y+1)

    def TestRule(self, test, rule, rot=0):
        """Takes 3 args, test and rule and rot
        test = what to test against
        rule = rule to test
        rot = should rotations be tested? default is 0 (no) 1 for yes
        returns 1 if there is a straight match,
        2 if first rotation matches, 3 if second, 4 if third,
        returns 0 if no match"""

        # Rule takes the form [x,x,x, y,y,y, z,z,z]
        # Can be either 0 (same height as middle), 1 (higher than middle) or 2 (ignore)
        # Compare only parts which aren't to be ignored
        fail = 0
        if rot == 0:
            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule[i] == test[i]:
                        fail = 1
                    else:
                        return 0
        # Test mirrored version
        elif rot == 1:
            rule_mirrored = []
            a = []
            a = rule[:]
            rule_mirrored.append(a[2])
            rule_mirrored.append(a[1])
            rule_mirrored.append(a[0])
            rule_mirrored.append(a[5])
            rule_mirrored.append(a[4])
            rule_mirrored.append(a[3])
            rule_mirrored.append(a[8])
            rule_mirrored.append(a[7])
            rule_mirrored.append(a[6])
            
            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_mirrored[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_mirrored[i] == test[i]:
                        fail = 2
                    else:
                        return 0
        # Test flipped version
        elif rot == 2:
            rule_flipped = []
            a = []
            a = rule[:]
            rule_flipped.append(a[6])
            rule_flipped.append(a[7])
            rule_flipped.append(a[8])
            rule_flipped.append(a[3])
            rule_flipped.append(a[4])
            rule_flipped.append(a[5])
            rule_flipped.append(a[0])
            rule_flipped.append(a[1])
            rule_flipped.append(a[2])
            
            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_flipped[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_flipped[i] == test[i]:
                        fail = 3
                    else:
                        return 0
        # Rotated version (90 degrees)
        elif rot == 3:
            rule_rot90 = []
            a = []
            a = rule[:]
            rule_rot90.append(a[6])
            rule_rot90.append(a[3])
            rule_rot90.append(a[0])
            rule_rot90.append(a[7])
            rule_rot90.append(a[4])
            rule_rot90.append(a[1])
            rule_rot90.append(a[8])
            rule_rot90.append(a[5])
            rule_rot90.append(a[2])
            
            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_rot90[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_rot90[i] == test[i]:
                        fail = 3
                    else:
                        return 0
        # Rotated version (180 degrees)
        elif rot == 4:
            rule_rot180 = []
            rule_rot180 = rule[:]
            rule_rot180.reverse()
            
            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_rot180[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_rot180[i] == test[i]:
                        fail = 3
                    else:
                        return 0
        # Rotated version (270 degrees)
        elif rot == 5:
            rule_rot270 = []
            a = []
            a = rule[:]
            rule_rot270.append(a[2])
            rule_rot270.append(a[5])
            rule_rot270.append(a[8])
            rule_rot270.append(a[1])
            rule_rot270.append(a[4])
            rule_rot270.append(a[7])
            rule_rot270.append(a[0])
            rule_rot270.append(a[3])
            rule_rot270.append(a[6])
            
            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_rot270[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_rot270[i] == test[i]:
                        fail = 5
                    else:
                        return 0


        return fail

    def TileSiblings(self, array, x, y):
        """Returns a 9x9 heightmap for slope testing"""
        #x, y = xy

        siblings = []
        for xx in range(-1,2):
            for yy in range(-1,2):
                if array[x+xx][y+yy][0] > array[x][y][0]:
                    siblings.append(1)
                elif array[x+xx][y+yy][0] < array[x][y][0]:
                    siblings.append(0)
                elif array[x+xx][y+yy][0] == array[x][y][0]:
                    siblings.append(0)
        
##        siblings.append(array[x - 1][y - 1][0])
##        siblings.append(array[x - 1][y][0])
##        siblings.append(array[x - 1][y + 1][0])
##        siblings.append(array[x][y - 1][0])
##        siblings.append(array[x][y][0])
##        siblings.append(array[x][y + 1][0])
##        siblings.append(array[x + 1][y - 1][0])
##        siblings.append(array[x + 1][y][0])
##        siblings.append(array[x + 1][y + 1][0])

        return siblings

    def TileSibs(self, array, xy=(0,0)):
        """Returns the 8 tiles surrounding the given tile"""
        x, y = xy

        siblings = []
        siblings.append(self.array[x - 1][y - 1])
        siblings.append(self.array[x - 1][y])
        siblings.append(self.array[x - 1][y + 1])
        siblings.append(self.array[x][y - 1])
        #siblings.append(self.array[x][y])
        siblings.append(self.array[x][y + 1])
        siblings.append(self.array[x + 1][y - 1])
        siblings.append(self.array[x + 1][y])
        siblings.append(self.array[x + 1][y + 1])

        return siblings

class DisplayMain:
    """This handles the main initialisation
    and startup for the display"""

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

        self.array = world.MakeArray()   # array of tiles, make or load
        self.WorldX = len(self.array[0])      #lazy method, needs change
        self.WorldY = len(self.array)
        self.WidthX = (self.WorldX + self.WorldY) * (p/2)
        self.HeightY = ((self.WorldX + self.WorldY) * (p/4)) + (p/2)
        
        self.dxoff = 0
        self.dyoff = 0

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        """Load All of our Sprites"""
        self.LoadSprites()
        self.PaintLand()
        
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
                #elif event.type == pygame.KEYDOWN:
                    #if ((event.key == pygame.K_RIGHT)
                    #or (event.key == pygame.K_LEFT)
                    #or (event.key == pygame.K_UP)
                    #or (event.key == pygame.K_DOWN)):
                        #self.MoveScreen(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If LMB pressed...
                    if (event.button == 1):
                        self.ModifyHeight()


                elif event.type == pygame.MOUSEMOTION:
                    # When the mouse is moved, check to see if...
                    b = event.buttons
                    
                    if pygame.font:
                        font = pygame.font.Font(None, 24)
                        self.textitems.append(font.render("Mouse State: " + str(b), 1, (255, 255, 255)))
                        
                    #pygame.event.event_name()
                        # Is the right mouse button held? If so, do scrolling & refresh whole screen
                    if (event.buttons == (0,0,1)):
                        self.MoveScreen("mouse")
                        blit_all = 1
                        # If neither mouse button held, then simply
                        # check which tile is active, and highlight it
                    else:
                        pygame.mouse.get_rel()  #Reset mouse position for scrolling
                        self.HighlightTile()
                        
                        
            #self.screen.blit(self.background, (0, 0))
            self.tile_sprites.draw(self.screen)
            self.water_sprites.draw(self.screen)
            if pygame.font:
                font = pygame.font.Font(None, 2)
                for j in range(len(self.textitems)):
                    self.screen.blit(self.textitems[j], (0,j*20))
            self.highlight.draw(self.screen)
            pygame.display.flip()

    def LoadSprites(self):
        """Load the sprites that we need"""

        self.tile_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.highlight = pygame.sprite.Group()

    def MoveScreen(self, key):
        """Moves the screen"""
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
        
        self.PaintLand()
        self.HighlightTile()

    def ModifyHeight(self):
        """Raises or lowers the height of a tile"""
        # Raise height of a single tile
        isopos = self.ScreenToIso(pygame.mouse.get_pos())
        x, y = isopos
        self.array[x][y][0] = self.array[x][y][0] + 1
        
        #sibs = world.TileSibs(self.array, isopos)
        for i in range(-1,2):
            for j in range(-1,2):
                #if x != j and y != i:
                self.array[x + i][y + j][0], self.array[x + i][y + j][1] = world.Test9(self.array, x + i, y + j)

        
        self.PaintLand()
        # Raise height of a single point (4 surrounding tiles)
        # Lower height of a single tile
        # Lower height of a single point (4 surrounding tiles)

    def ScreenToIso(self, wxy=(0,0)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        TileRatio = 2
        wx, wy = wxy

        #wx = wx# + self.dxoff
        #wy = wy# + self.dyoff
        #dx = wx - p + self.dxoff
        #dy = wy + (p/2) + self.dyoff
        dx = wx - (self.WidthX/2) - self.dxoff
        dy = wy - (p/2) - self.dyoff
        # Don't really understand how this bit works...
        x = int((dy + dx / TileRatio) * (TileRatio / 2) / (p/2))
        y = int((dy - dx / TileRatio) * (TileRatio / 2) / (p/2))
        if x < 0 or y < 0:
            return (0,0)
        if x >= (self.WorldX) or y >= (self.WorldY):
            return (0,0)
        
        return (x,y)


    def HighlightTile(self, iso_coords=(0,0)):
        """Highlight a particular tile, takes one argument:
        iso_coords - coords of tile to highlight"""
        isopos = self.ScreenToIso(pygame.mouse.get_pos())
        x, y = isopos
        self.highlight.empty()
        #tohighlight = self.TileSiblings(isopos)

        xpos = (self.WidthX / 2) + (x * (p/2)) - (y * (p/2)) - (p/2) + self.dxoff
        ypos = (x * (p/4)) + (y * (p/4)) - (self.array[x][y][0] * ph) + self.dyoff
        self.highlight.add(Tile(pygame.Rect(xpos, ypos, p, p), 16))


        
    def PaintLand(self):
        """Paint the land tiles on the screen"""
        self.tile_sprites.empty()

        for y in range(self.WorldY):
            for x in range(self.WorldX):
                xpos = (self.WidthX / 2) + (x * (p/2)) - (y * (p/2)) - (p/2) + self.dxoff
                if self.array[x][y][1] != 14:
                    hh = self.array[x][y][0]
                else:
                    hh = self.array[x][y][0]
                ypos = (x * (p/4)) + (y * (p/4)) - (hh * ph) + self.dyoff
                self.tile_sprites.add(Tile(pygame.Rect(xpos, ypos, p, p), self.array[x][y][1]))

        # Paint the water tiles
        self.water_sprites.empty()

        for y in range(self.WorldY):
            for x in range(self.WorldX):
                xpos = (self.WidthX / 2) + (x * (p/2)) - (y * (p/2)) - (p/2) + self.dxoff
                ypos = (x * (p/4)) + (y * (p/4)) - ((hh + 1) * ph) + self.dyoff
                if self.array[x][y][0] < 1:
                    self.water_sprites.add(Tile(pygame.Rect(xpos, ypos, p, p), 15))

if __name__ == "__main__":
    world = World()
    MainWindow = DisplayMain()
    MainWindow.MainLoop()
















