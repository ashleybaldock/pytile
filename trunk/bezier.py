import pygame
from pygame.locals import *

import os, sys
 
from vec2d import *
 
grey = (100,100,100)
lightgray = (200,200,200)
red = (255,0,0)
darkred = (192,0,0)
green = (0,255,0)
darkgreen = (0,128,0)
blue = (0,0,255)
darkblue = (0,0,192)
brown = (72,64,0)
silver = (224,216,216)
X,Y,Z = 0,1,2
black = (0,0,0)
white = (255,255,255)
yellow = (255,255,0)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

xWorld = 4
yWorld = 4

 
def calculate_bezier(p, steps = 30):
    """
    Calculate a bezier curve from 4 control points and return a 
    list of the resulting points.
    
    The function uses the forward differencing algorithm described here: 
    http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
    """
    
    t = 1.0 / steps
    temp = t*t
    
    f = p[0]
    fd = 3 * (p[1] - p[0]) * t
    fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
    fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t
    
    fddd = fddd_per_2 + fddd_per_2
    fdd = fdd_per_2 + fdd_per_2
    fddd_per_6 = fddd_per_2 * (1.0 / 3)
    
    points = []
    tangents = []
    for x in range(steps):
        points.append(f)
        tangents.append(fd)
        f = f + fd + fdd_per_2 + fddd_per_6
        fd = fd + fdd + fddd_per_2
        fdd = fdd + fddd
        fdd_per_2 = fdd_per_2 + fddd_per_2
    points.append(f)
    tangents.append(fd)
    return (points, tangents)

def get_at_width(point, tangent, width):
    newpoint = point + tangent.perpendicular_normal() * width
    return newpoint

def get_point_at_width(a, b, width):
    a_to_b = b - a
    c = a + a_to_b.perpendicular_normal() * width
    d = b + a_to_b.perpendicular_normal() * width
    return d

def draw_curve(points, colour, screen):
    b_points = calculate_bezier(points)
    pygame.draw.lines(screen, colour, False, b_points)

def find_midpoint(a, b):
    """"""
    a_to_b = b - a
    return a + a_to_b / 2.0


    # Calculate bezier curve points and tangents
    cps, tangents = calculate_bezier(control_points, 30)
    # Setup constants
    sleeper_spacing = 15
    sleeper_width = 5
    sleeper_length = 18
    rail_spacing = 10
    rail_width = 2
    ballast_width = 30
    overflow = - sleeper_spacing / 2.0
    # It's like it's drawing one less per segment than it should?? Maybe something to do with the lengths being calculated?
    # It's drawing one less segment because it's calculating the number of intervals between sleepers, but the number of sleepers is one more than this!
    if component == "sleepers":
        sleeper_points = []
        start = True
        for p in range(1, len(cps)):
            # Find gradient of a->b
            b = cps[p]
            a = cps[p-1]
            a_to_b = b - a
            ab_n = a_to_b.normalized()
            # Vector to add to start vector, to get offset start location
            start_vector = overflow * ab_n
            
            # Number of sleepers to draw in this section
            n_sleepers, overflow = divmod((a_to_b + start_vector).get_length(), (ab_n * sleeper_spacing).get_length())
            n_sleepers = int(n_sleepers)
            # Loop through n_sleepers, draw a sleeper at the start of each sleeper spacing interval
            if start:
                s = 0
                start = False
            else:
                s = 1
            for n in range(s, n_sleepers+1):
                sleeper_points.append([get_at_width(a - start_vector + n*ab_n*sleeper_spacing - ab_n*0.5*sleeper_width, a_to_b, -sleeper_length),
                                       get_at_width(a - start_vector + n*ab_n*sleeper_spacing - ab_n*0.5*sleeper_width, a_to_b, sleeper_length),
                                       get_at_width(a - start_vector + n*ab_n*sleeper_spacing + ab_n*0.5*sleeper_width, a_to_b, sleeper_length),
                                       get_at_width(a - start_vector + n*ab_n*sleeper_spacing + ab_n*0.5*sleeper_width, a_to_b, -sleeper_length)])

        # Finally draw all the sleeper points
        for p in sleeper_points:
            pygame.draw.polygon(screen, brown, p, 0)

    if component == "ballast":
        # Draw the ballast under the track, this will be a polygon in the rough shape of the trackwork which will then be replaced with a texture
        # Polygon defined by the two lines at either side of the track
        ballast_points = []
        # Add one side
        for p in range(0, len(cps)):
            ballast_points.append(get_at_width(cps[p], tangents[p], ballast_width))
        ballast_points.reverse()
        for p in range(0, len(cps)):
            ballast_points.append(get_at_width(cps[p], tangents[p], -ballast_width))
        pygame.draw.polygon(screen, grey, ballast_points, 0)

    if component == "track":
        points2 = []
        for p in range(0, len(cps)):
            points2.append(get_at_width(cps[p], tangents[p], rail_spacing))
        pygame.draw.lines(screen, silver, False, points2, rail_width)
        points3 = []
        for p in range(0, len(cps)):
            points3.append(get_at_width(cps[p], tangents[p], -rail_spacing))
        pygame.draw.lines(screen, silver, False, points3, rail_width)

    if component == "controls":
        # Draw bezier curve control points
        for p in control_points:
            pygame.draw.circle(screen, blue, p, 4)
        pygame.draw.lines(screen, lightgray, False, [control_points[0],control_points[1]])
        pygame.draw.lines(screen, lightgray, False, [control_points[2],control_points[3]])
        # Draw the base bezier curve
        pygame.draw.lines(screen, red, False, cps)

    if component == "hints":
        # Draw hints as to the curve sections
        for p in cps:
            pygame.draw.circle(screen, green, (int(p[0]),int(p[1])), 3)


class Tile(pygame.sprite.Sprite):
    """A tile containing tracks, drawn in layers"""
##    image = None
    font = None
    def __init__(self, size, position, type, track_spacing=25, curve_factor=60):
        pygame.sprite.Sprite.__init__(self)
        if Tile.font is None:
            Tile.font = pygame.font.SysFont("Arial", 12)
        self.size = size
        self.track_spacing = track_spacing
        self.curve_factor = curve_factor
        self.position = position
        # Type determines which part of the image this sprite draws (rails, sleepers, ballast or hints)
        self.type = type
        # Init variables
        self.paths = []

        self.box = [vec2d(size, size),
               vec2d(0, size),
               vec2d(0, 0),
               vec2d(size, 0)]

        self.box_midpoints = []
        self.box_allmidpoints = []
        for p in range(len(self.box)):
            self.box_midpoints.append(find_midpoint(self.box[p-1], self.box[p]))
        for p in range(len(self.box_midpoints)):
            self.box_allmidpoints.append([self.box_midpoints[p-1], (self.box[p-1] - self.box[p-2]).normalized()])
            self.box_allmidpoints.append([find_midpoint(self.box_midpoints[p-1], self.box_midpoints[p]), (self.box_midpoints[p] - self.box_midpoints[p-1]).normalized()])
        self.box_endpoints = []
        for p in range(len(self.box_allmidpoints)):
            self.box_endpoints.append([self.box_allmidpoints[p][0] - self.box_allmidpoints[p][1] * track_spacing, self.box_allmidpoints[p][1].perpendicular()])
            self.box_endpoints.append([self.box_allmidpoints[p][0], self.box_allmidpoints[p][1].perpendicular()])
            self.box_endpoints.append([self.box_allmidpoints[p][0] + self.box_allmidpoints[p][1] * track_spacing, self.box_allmidpoints[p][1].perpendicular()])

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(black)
        self.image.set_colorkey(black, pygame.RLEACCEL)
        self.rect = self.calc_rect
    def add_path(self, path):
        """Add another path to this tile"""
        self.paths.append(path)
    def calc_rect(self):
        """Calculate the current rect of this tile"""
        x = self.position[0]
        y = self.position[1]
        p = self.size
        p2 = self.size / 2
        # Global screen positions
        self.xpos = xWorld*p2 - (x * p2) + (y * p2) - p2
##        self.ypos = (x * p4) + (y * p4) - (z * ph)
        self.ypos = (x * p2) + (y * p2)
        # Rect position takes into account the offset
        self.rect = (self.xpos, self.ypos, p, p)
        return self.rect
    def update(self):
        """Draw the image this tile represents"""
        # Draw a track for every entry in paths
        paths_to_draw = []
        for p in self.paths:
            a = self.box_endpoints[p[0]][0]
            b = self.box_endpoints[p[0]][0] + self.box_endpoints[p[0]][1] * self.curve_factor
            c = self.box_endpoints[p[1]][0] + self.box_endpoints[p[1]][1] * self.curve_factor
            d = self.box_endpoints[p[1]][0]
            paths_to_draw.append([a,b,c,d])
        if self.type == "rails":
            for p in paths_to_draw:
                self.draw_track(p, "rails")
        elif self.type == "sleepers":
            for p in paths_to_draw:
                self.draw_track(p, "sleepers")
        elif self.type == "ballast":
            for p in paths_to_draw:
                self.draw_track(p, "ballast")
        elif self.type == "hints":
            for p in paths_to_draw:
                self.draw_track(p, "hints")
        elif self.type == "box":
            # Draw the outline of the box
            pygame.draw.lines(self.image, True, darkblue, self.box)
            pygame.draw.lines(self.image, True, darkblue, self.box_midpoints)
##        if start_point != None:
##            pygame.draw.circle(box_surface, green, box_endpoints[start_point][0], 7)
            for p in self.box_endpoints:
                pygame.draw.circle(self.image, red, (int(p[0][0]),int(p[0][1])), 3)
                pygame.draw.line(self.image, darkblue, p[0], p[0] + 20 * p[1])
                s = Tile.font.render(str(self.box_endpoints.index(p)), False, green)
                x,y = s.get_size()
                x = x/2
                y = y/2
                self.image.blit(s, p[0] + 5 * p[1] - (x,y))
        self.rect = self.calc_rect()
    def draw_track(self, control_points, component):
        """Draw the varying track components onto the sprite's image"""
        # Calculate bezier curve points and tangents
        cps, tangents = calculate_bezier(control_points, 30)
        # Setup constants
        sleeper_spacing = 15
        sleeper_width = 5
        sleeper_length = 18
        rail_spacing = 10
        rail_width = 2
        ballast_width = 30
        overflow = - sleeper_spacing / 2.0
        if component == "sleepers":
            sleeper_points = []
            start = True
            for p in range(1, len(cps)):
                # Find gradient of a->b
                b = cps[p]
                a = cps[p-1]
                a_to_b = b - a
                ab_n = a_to_b.normalized()
                # Vector to add to start vector, to get offset start location
                start_vector = overflow * ab_n
                
                # Number of sleepers to draw in this section
                n_sleepers, overflow = divmod((a_to_b + start_vector).get_length(), (ab_n * sleeper_spacing).get_length())
                n_sleepers = int(n_sleepers)
                # Loop through n_sleepers, draw a sleeper at the start of each sleeper spacing interval
                if start:
                    s = 0
                    start = False
                else:
                    s = 1
                for n in range(s, n_sleepers+1):
                    sleeper_points.append([get_at_width(a - start_vector + n*ab_n*sleeper_spacing - ab_n*0.5*sleeper_width, a_to_b, -sleeper_length),
                                           get_at_width(a - start_vector + n*ab_n*sleeper_spacing - ab_n*0.5*sleeper_width, a_to_b, sleeper_length),
                                           get_at_width(a - start_vector + n*ab_n*sleeper_spacing + ab_n*0.5*sleeper_width, a_to_b, sleeper_length),
                                           get_at_width(a - start_vector + n*ab_n*sleeper_spacing + ab_n*0.5*sleeper_width, a_to_b, -sleeper_length)])

            # Finally draw all the sleeper points
            for p in sleeper_points:
                pygame.draw.polygon(self.image, brown, p, 0)

        if component == "ballast":
            # Draw the ballast under the track, this will be a polygon in the rough shape of the trackwork which will then be replaced with a texture
            # Polygon defined by the two lines at either side of the track
            ballast_points = []
            # Add one side
            for p in range(0, len(cps)):
                ballast_points.append(get_at_width(cps[p], tangents[p], ballast_width))
            ballast_points.reverse()
            for p in range(0, len(cps)):
                ballast_points.append(get_at_width(cps[p], tangents[p], -ballast_width))
            # Draw out to the image
            pygame.draw.polygon(self.image, grey, ballast_points, 0)

        if component == "rails":
            points2 = []
            for p in range(0, len(cps)):
                points2.append(get_at_width(cps[p], tangents[p], rail_spacing))
            points3 = []
            for p in range(0, len(cps)):
                points3.append(get_at_width(cps[p], tangents[p], -rail_spacing))
            # Draw out to the image
            pygame.draw.lines(self.image, silver, False, points2, rail_width)
            pygame.draw.lines(self.image, silver, False, points3, rail_width)

        if component == "controls":
            # Draw bezier curve control points
            for p in control_points:
                pygame.draw.circle(screen, blue, p, 4)
            # Draw out to the image
            pygame.draw.lines(self.image, lightgray, False, [control_points[0],control_points[1]])
            pygame.draw.lines(self.image, lightgray, False, [control_points[2],control_points[3]])
            # Draw the base bezier curve
            pygame.draw.lines(self.image, red, False, cps)

        if component == "hints":
            # Draw hints as to the curve sections
            for p in cps:
                pygame.draw.circle(self.image, green, p, 3)
    ##        pygame.draw.circle(screen, yellow, cps[0], 8)



class DisplayMain(object):
    """This handles the main initialisation
    and startup for the display"""
    def __init__(self, width, height):
        # Initialize PyGame
        pygame.init()
        
        # Set the window Size
        self.screen_width = width
        self.screen_height = height
        
        # Create the Screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))#, pygame.RESIZABLE)

        #tell pygame to keep sending up keystrokes when they are held down
        pygame.key.set_repeat(500, 30)

        # Setup fonts
        self.font = pygame.font.Font(None, 12)
        self.font = pygame.font.SysFont("Arial", 16)

        # Set up variables
        self.refresh_screen = True

    def add_tile(self, size, position):
        """Add a track tile"""
##        self.rails_sprites.add(Tile(size, position, "rails"))
##        self.sleepers_sprites.add(Tile(size, position, "sleepers"))
##        self.ballast_sprites.add(Tile(size, position, "ballast"))
        self.hints_sprites.add(Tile(size, position, "hints"))
        self.box_sprites.add(Tile(size, position, "box"))

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        # Initiate the clock
        self.clock = pygame.time.Clock()

        self.box_size = 200
     
        # The currently selected point
        self.selected = None

        self.instructions = ["D - Click on a pair of red dots to draw a track between them",
                             "R - Click on a pair of red dots to remove the track between them"]

        self.rails_sprites = pygame.sprite.Group()
        self.sleepers_sprites = pygame.sprite.Group()
        self.ballast_sprites = pygame.sprite.Group()
        self.hints_sprites = pygame.sprite.Group()
        self.box_sprites = pygame.sprite.Group()

        x_boxes = self.screen_width / self.box_size
        y_boxes = self.screen_height / self.box_size
        for x in range(xWorld):
            for y in range(yWorld):
                self.add_tile(self.box_size, (x, y))


        self.sprite_groups = [self.box_sprites, self.ballast_sprites, self.sleepers_sprites, self.rails_sprites]#, hints_sprites]
        for x in self.sprite_groups:
            for y in x:
                y.add_path([13,1])


        while True:
            self.clock.tick(0)
            # If there's a quit event, don't bother parsing the event queue
            if pygame.event.peek(pygame.QUIT):
                pygame.display.quit()
                sys.exit()

            # Clear the stack of dirty tiles
            self.dirty = []

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()
##                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
##                    for p in control_points:
##                        if abs(p.x - event.pos[X]) < 10 and abs(p.y - event.pos[Y]) < 10 :
##                            self.selected = p
##                    for p in box_collidepoints:
##                        if abs(p[0].x - event.pos[X]) < 10 and abs(p[0].y - event.pos[Y]) < 10 :
##                            if start_point == None:
##                                start_point = box_collidepoints.index(p)
##                            elif box_collidepoints.index(p) != start_point:
##                                new_path = [start_point, box_collidepoints.index(p)]
##                                if new_path not in paths:
##                                    paths.append(new_path)
##                                start_point = None
##                elif event.type == MOUSEBUTTONUP and event.button == 1:
##                    self.selected = None

            ### Draw stuff
            self.screen.fill(darkgreen)


            # Draw instructions to screen
            for t in range(len(self.instructions)):
                self.screen.blit(self.font.render(self.instructions[t], False, black), (20,420 + t*20))


            # Update sprites in the sprite groups which need updating
            for x in self.sprite_groups:
                x.update()
                rectlist = x.draw(self.screen)

            # Refresh the screen if necessary, or just draw the updated bits
            if self.refresh_screen:
                pygame.display.update()
                self.screen.fill((0,0,0))
##                self.refresh_screen = False
            else:
                pygame.display.update(self.dirty)


    
if __name__ == "__main__":
##    sys.stderr = debug
##    sys.stdout = debug
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()
