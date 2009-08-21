#!/usr/bin/python
# Second test of the ground display system
# Test3 - new slope decision system based on rotated wildcard grids

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
                ret = self.Test9(TileMap, x, y)
                #SecondMap[x][y][0], SecondMap[x][y][1] = self.Test9(TileMap, x, y)

        return(TileMap)

    def Test9(self, array, x, y):

        # Check to see if tile is at edge of map, this needs a special case
        if x == 0 or y == 0:
            # Check special corner cases
            if x == 0 and y == 0:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1
            elif x == 0 and y == (len(array)-1):
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1
            elif x == (len(array[0])-1) and y == 0:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1
            else:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1
        # to see if the tile is at the other edges of the map...
        elif x == (len(array[0])-1) or y == (len(array)-1):
            # Last special corner case
            if x == (len(array[0])-1) and y == (len(array)-1):
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1
            else:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1
        # Otherwise use the general tests
        else:
        # Straight slopes (high)
        # Needs some sort of more generic system for this really...

        # Rules to deal with cases where land needs to be raised
        # in these cases we really need to re-do all the calcs for the
        # surrounding tiles, to give a degree of recursivity

        #Could be made more efficient if rule can specify only 90 degrees...            
            q = self.TestRule(self.TileSiblings(array, x, y), [2,2,2,
                                                               1,0,1,
                                                               2,2,2,], 2)
            if q != 0:
                array[x][y][0] = array[x][y][0] + 1
                array[x][y][1] = 14
                return 1

            # Rules for straight slopes
            q = self.TestRule(self.TileSiblings(array, x, y), [2,0,0,
                                                               1,0,0,
                                                               2,0,0,], 2)
            if q == 1:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 0
                return 1
            elif q == 2:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 1
                return 1
            elif q == 3:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 2
                return 1
            elif q == 4:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 3
                return 1
            
            # Rules for "outside" curves
            q = self.TestRule(self.TileSiblings(array, x, y), [1,0,0,
                                                               0,0,0,
                                                               0,0,0,], 2)
            if q == 1:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 5
                return 1
            elif q == 2:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 6
                return 1
            elif q == 3:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 7
                return 1
            elif q == 4:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 4
                return 1

            # Rules for "inside" curves
            q = self.TestRule(self.TileSiblings(array, x, y), [2,1,2,
                                                               1,0,0,
                                                               2,0,0,], 2)
            if q == 1:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 8
                return 1
            elif q == 2:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 10
                return 1
            elif q == 3:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 12
                return 1
            elif q == 4:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 9
                return 1
            q = self.TestRule(self.TileSiblings(array, x, y), [0,1,0,
                                                               0,0,0,
                                                               0,0,1,], 2)
            if q == 4:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 8
                return 1
            elif q == 1:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 10
                return 1
            elif q == 2:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 12
                return 1
            elif q == 3:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 9
                return 1
            q = self.TestRule(self.TileSiblings(array, x, y), [0,1,0,
                                                               0,0,0,
                                                               1,0,0,], 2)
            if q == 1:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 8
                return 1
            elif q == 2:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 10
                return 1
            elif q == 3:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 12
                return 1
            elif q == 4:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 9
                return 1



            # Rules for double curves at corner of two mountains
            q = self.TestRule(self.TileSiblings(array, x, y), [1,0,0,
                                                               0,0,0,
                                                               0,0,1,], 2)
            if q == 1:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 13
                return 1
            elif q == 2:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 11
                return 1


            else:
                array[x][y][0] = array[x][y][0]
                array[x][y][1] = 14
                return 1

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
        """Takes 3 args, test, rule and rot
        test = pattern to test for match
        rule = rule to test pattern against
        rot = what rotations should be used:
              0 - no rotations
              1 - 180 degree rotation only
              2 - all 4 rotations
        returns:
        0 - no rot matches
        1 - 0 degrees matches (what's passed in)
        2 - 90 degrees matches
        3 - 180 degrees matches
        4 - 270 degrees matches"""

        # First, test the rule as passed in
        fail = 0
        for i in range(len(test)):
            # If entry is 2, don't bother testing
            if rule[i] != 2:
                # If they are not the same, mark it for failure
                if rule[i] == test[i]:
                    complete = 1
                else:
                    # If the rule doesn't match on any particular point,
                    # set fail to 1 and this rule varient isn't passed
                    fail = 1

        if fail == 0:
            return complete
        
        if rot >= 1:
        #Could probably save some time here by doing 180 degree case seperately, needs speed testing
            fail = 0
            complete = 0

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

            if rot != 1:        # If 1 then we're only testing 180 degrees, so skip this
                for i in range(len(test)):
                    # If entry is 2, don't bother testing
                    if rule_rot90[i] != 2:
                        # If they are not the same, mark it for failure
                        if rule_rot90[i] == test[i]:
                            complete = 2
                        else:
                            # If the rule doesn't match on any particular point,
                            # set fail to 1 and this rule varient isn't passed
                            fail = 1
                if fail == 0:
                    return complete
                fail = 0
                complete = 0

            rule_rot180 = []
            a = []
            a = rule_rot90[:]
            rule_rot180.append(a[6])
            rule_rot180.append(a[3])
            rule_rot180.append(a[0])
            rule_rot180.append(a[7])
            rule_rot180.append(a[4])
            rule_rot180.append(a[1])
            rule_rot180.append(a[8])
            rule_rot180.append(a[5])
            rule_rot180.append(a[2])

            for i in range(len(test)):
                # If entry is 2, don't bother testing
                if rule_rot180[i] != 2:
                    # If they are not the same, mark it for failure
                    if rule_rot180[i] == test[i]:
                        complete = 3
                    else:
                        # If the rule doesn't match on any particular point,
                        # set fail to 1 and this rule varient isn't passed
                        fail = 1

            if fail == 0:
                return complete
            if rot == 1:
                return 0
            else:
                fail = 0
                complete = 0

            if rot != 1:        # If 1 then we're only testing 180 degrees, so skip this

                rule_rot270 = []
                a = []
                a = rule_rot180[:]
                rule_rot270.append(a[6])
                rule_rot270.append(a[3])
                rule_rot270.append(a[0])
                rule_rot270.append(a[7])
                rule_rot270.append(a[4])
                rule_rot270.append(a[1])
                rule_rot270.append(a[8])
                rule_rot270.append(a[5])
                rule_rot270.append(a[2])

                for i in range(len(test)):
                    # If entry is 2, don't bother testing
                    if rule_rot270[i] != 2:
                        # If they are not the same, mark it for failure
                        if rule_rot270[i] == test[i]:
                            complete = 4
                        else:
                            # If the rule doesn't match on any particular point,
                            # set fail to 1 and this rule varient isn't passed
                            fail = 1
                if fail == 0:
                    return complete
                else:
                    return 0

        elif fail == 1:
            return 0


    def TileSiblings(self, array, x, y):
        """Returns a 9x9 heightmap for slope testing"""
        #x, y = xy

        siblings = []

        for xx in range(-1,2):
            for yy in range(-1,2):
                if (x+xx) < 0 or (x+xx) > (len(array[0])-1):
                    siblings.append(0)
                elif (y+yy) < 0 or (y+yy) > (len(array)-1):
                    siblings.append(0)
                else:
                    if array[x+xx][y+yy][0] > array[x][y][0]:
                        siblings.append(1)
                    elif array[x+xx][y+yy][0] < array[x][y][0]:
                        siblings.append(0)
                    elif array[x+xx][y+yy][0] == array[x][y][0]:
                        siblings.append(0)

        return siblings

##    def TileSibs(self, array, xy=(0,0)):
##        """Returns the 8 tiles surrounding the given tile"""
##        x, y = xy
##
##        siblings = []
##        siblings.append(self.array[x - 1][y - 1])
##        siblings.append(self.array[x - 1][y])
##        siblings.append(self.array[x - 1][y + 1])
##        siblings.append(self.array[x][y - 1])
##        #siblings.append(self.array[x][y])
##        siblings.append(self.array[x][y + 1])
##        siblings.append(self.array[x + 1][y - 1])
##        siblings.append(self.array[x + 1][y])
##        siblings.append(self.array[x + 1][y + 1])
##
##        return siblings

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
            #if blit_all == 1:
            self.screen.blit(self.background, (0, 0))
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
                #self.array[x + i][y + j][0], self.array[x + i][y + j][1] = world.Test9(self.array, x + i, y + j)
                ret = world.Test9(self.array, x + i, y + j)
                    
        
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
















