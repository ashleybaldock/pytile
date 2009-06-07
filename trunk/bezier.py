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

FPS_REFRESH = 500
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

xWorld = 4
yWorld = 4


class MouseSprite(pygame.sprite.Sprite):
    """Small invisible sprite to use for mouse/sprite collision testing"""
    # This sprite never gets drawn, so no need to worry about what it looks like
    image = None
    mask = None
    def __init__(self, (mouseX, mouseY)):
        pygame.sprite.Sprite.__init__(self)
        if MouseSprite.image is None:
            MouseSprite.image = pygame.Surface((1,1))
        if MouseSprite.mask is None:
            s = pygame.Surface((1,1))
            s.fill((1,1,1))
            MouseSprite.mask = pygame.mask.from_surface(s, 0)
        self.mask = MouseSprite.mask
        self.image = MouseSprite.image
        self.rect = pygame.Rect(mouseX, mouseY, 1,1)
    def update(self, (x, y)):
        self.rect = pygame.Rect(x, y, 1,1)


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
        self.control_hint = None

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
        self.update()
    def add_path(self, path):
        """Add another path to this tile"""
        self.paths.append(path)
        self.update()

    def set_control_hint(self, endpoint_number):
        """Add a control hint to this sprite, used to indicate which endpoints are active"""
        self.control_hint = endpoint_number
    def find_control_points(self, position):
        """Find the control points closest to the mouse cursor, relative to this tile"""
        wx, wy = position
        x = wx - self.xpos
        y = wy - self.ypos
        control_points = []
        for n, c in enumerate(self.box_endpoints):
            # If the position is within 10 pixels of the control point position, this is a valid control point
            if abs(x - c[0][0]) < 10 and abs(y - c[0][1]) < 10:
                control_points.append(n)
        print "control_points: %s\nwx: %s, wy: %s, x: %s, y: %s" % (control_points,wx,wy,x,y)
        # Return only one control point
        if control_points:
            return control_points[0]
        else:
            return None
                
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
        # Reset the image to blank
        self.image.fill(black)
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
            # Draw control hints for this tile
            if self.control_hint:
                print "self.control_hint: %s" % self.control_hint
                pygame.draw.circle(self.image, green, self.box_endpoints[self.control_hint][0], 7)
            # Draw the remaining box endpoints
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

        self.mouseSprite = None

    def collide_locate(self, mousepos, collideagainst, start=None):
        """Locates the sprite(s) that the mouse position intersects with"""
        # Draw mouseSprite at cursor position
        if self.mouseSprite:
            self.mouseSprite.sprite.update(mousepos)
        else:
            self.mouseSprite = pygame.sprite.GroupSingle(MouseSprite(mousepos))
        # Find sprites that the mouseSprite intersects with
        collision_list1 = pygame.sprite.spritecollide(self.mouseSprite.sprite, collideagainst, False)
        if collision_list1:
            tilecontrols = []
            for t in collision_list1:
                # For each tile collided with, calculate which of its control points the mouse event is closest to (if any)
                cp = t.find_control_points(mousepos)
                if cp:
                    tilecontrols.append([t.position[0], t.position[1], cp])
            return tilecontrols
        else:
            return None

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        # Initiate the clock
        self.clock = pygame.time.Clock()

        self.box_size = 200

        # Settings for FPS counter
        self.fps_refresh = FPS_REFRESH
        self.fps_elapsed = 0

        # The currently selected point
        self.selected = None

        self.instructions = ["Click on a pair of red dots to:",
                             "D - draw a track between them",
##                             "R - remove the track between them",
                             ]

        # Layers to draw, first listed drawn first
        layers = [
##                  "hints",
                  "ballast",
                  "sleepers",
                  "rails",
                  "box",
                  ]

        # 2D array, [x][y]
        self.sprite_lookup = []
        self.sprites = pygame.sprite.LayeredUpdates()
        self.searchsprites = pygame.sprite.Group()

        for x in range(xWorld):
            a = []
            for y in range(yWorld):
                d = {}
                for c, b in enumerate(layers):
                    d[b] = Tile(self.box_size, (x,y), b)
                    self.sprites.add(d[b], layer=c)
                    if c == 0:
                        self.searchsprites.add(d[b])
                a.append(d)
            self.sprite_lookup.append(a)

        self.start_positions = []

        while True:
            self.clock.tick(0)
            # If there's a quit event, don't bother parsing the event queue
            if pygame.event.peek(pygame.QUIT):
                pygame.display.quit()
                sys.exit()

            # Clear the stack of dirty tiles
            self.dirty = []
            clear = False
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    print "Mouse button event starts"
                    if self.start_positions:
                        print "existing operation in progress..."
                        end_positions = self.collide_locate(event.pos, self.searchsprites)
                        if end_positions:
                            for e in end_positions:
                                for s in self.start_positions:
                                    if e[0] == s[0] and e[1] == s[1]:
                                        for key, value in self.sprite_lookup[s[0]][s[1]].iteritems():
                                            value.set_control_hint(None)
                                            value.add_path([s[2], e[2]])
                                            value.update()
                                        clear = True
                                        self.refresh_screen = True
                                        print "adding path: %s->%s to tile: (%s,%s)" % (s[2], e[2],s[0],s[1])
                                    else:
                                        for key, value in self.sprite_lookup[s[0]][s[1]].iteritems():
                                            value.set_control_hint(None)
                                            value.update()
                    else:
                        print "new operation..."
                        self.start_positions = self.collide_locate(event.pos, self.searchsprites)
                        if self.start_positions:
                            for s in self.start_positions:
                                for key, value in self.sprite_lookup[s[0]][s[1]].iteritems():
                                    value.set_control_hint(s[2])
                                    value.update()
                            self.refresh_screen = True
                        print "end operation"

            if clear:
                self.start_positions = None


            # Draw instructions to screen
            for t in range(len(self.instructions)):
                self.screen.blit(self.font.render(self.instructions[t], False, black), (10,10 + t*20))


            # Write some useful info on the top bar
            self.fps_elapsed += self.clock.get_time()
            if self.fps_elapsed >= self.fps_refresh:
                self.fps_elapsed = 0
                pygame.display.set_caption("FPS: %i" %
                                           (self.clock.get_fps()))

            # Update sprites in the sprite groups which need updating
##            if self.refresh_screen:
##                self.sprites.update()
            rectlist = self.sprites.draw(self.screen)

            # Refresh the screen if necessary, or just draw the updated bits
            self.refresh_screen = True
            if self.refresh_screen:
                pygame.display.update()
                self.screen.fill(darkgreen)
                self.refresh_screen = False
            else:
                pygame.display.update(self.dirty)


    
if __name__ == "__main__":
##    sys.stderr = debug
##    sys.stdout = debug
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    MainWindow = DisplayMain(WINDOW_WIDTH, WINDOW_HEIGHT)
    MainWindow.MainLoop()
