import pygame
from pygame.locals import *
 
from vec2d import *
 
gray = (100,100,100)
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

def draw_track(screen, control_points, component):
    # Calculate bezier curve points and tangents
    cps, tangents = calculate_bezier(control_points, 30)
    # Setup constants
    sleeper_spacing = 15
    sleeper_width = 5
    sleeper_length = 18
    rail_spacing = 10
    rail_width = 2
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
            n_sleepers = (a_to_b + start_vector).get_length() / (ab_n * sleeper_spacing).get_length()
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
            # Finally calculate overflow for the next loop
            overflow = (a_to_b + start_vector).get_length() % (ab_n * sleeper_spacing).get_length()

        # Finally draw all the sleeper points
        for p in sleeper_points:
            pygame.draw.polygon(screen, brown, p, 0)
##        pygame.draw.polygon(screen, yellow, sleeper_points[0], 0)

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
            pygame.draw.circle(screen, green, p, 3)
##        pygame.draw.circle(screen, yellow, cps[0], 8)

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 500))

    box = [vec2d(300,300), vec2d(100,300), vec2d(100,100), vec2d(300,100)]
##    box = [vec2d(300,200), vec2d(100,200), vec2d(100,100), vec2d(300,100)]
    # endpoints addressed by box endpoints, in range 0-23
    # top, top-right, right, bottom-right, bottom, bottom-left, left, top-left
    # Endpoints calculated automatically later
    # Endpoints calculated from the_box
    # top, right, bottom, left are the midpoints of the box's sides
    # others are midpoint of the lines between the box's midpoints
    # Get all the box midpoints
    track_spacing = 25
    box_midpoints = []
    box_allmidpoints = []
    for p in range(len(box)):
        box_midpoints.append(find_midpoint(box[p-1], box[p]))
##        box_allmidpoints.append([find_midpoint(box[p-1], box[p]), (box[p] - box[p-1]).normalized()])
    for p in range(len(box_midpoints)):
        box_allmidpoints.append([box_midpoints[p-1], (box[p-1] - box[p-2]).normalized()])
        box_allmidpoints.append([find_midpoint(box_midpoints[p-1], box_midpoints[p]), (box_midpoints[p] - box_midpoints[p-1]).normalized()])
    box_endpoints = []
    for p in range(len(box_allmidpoints)):
        box_endpoints.append([box_allmidpoints[p][0] - box_allmidpoints[p][1] * track_spacing, box_allmidpoints[p][1].perpendicular()])
        box_endpoints.append([box_allmidpoints[p][0], box_allmidpoints[p][1].perpendicular()])
        box_endpoints.append([box_allmidpoints[p][0] + box_allmidpoints[p][1] * track_spacing, box_allmidpoints[p][1].perpendicular()])
    ### Control points that are later used to calculate the curve
    control_points = [vec2d(350,50), vec2d(400,250), vec2d(500,200), vec2d(450, 450)]
 
    ### The currently selected point
    selected = None

    paths = [
##             [14, 0],
##             [14, 3],
##             [12, 5],
##             [12, 2],
##             [15, 5],
##             [17, 3],
##             [17, 0],
##             [15, 2],
            ]
    start_point = None
    instructions = ["Click on a pair of red dots to draw a track between them",
                    "Drag blue control points to alter the free-form track curve"]
    clock = pygame.time.Clock()
    pts = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for p in control_points:
                    if abs(p.x - event.pos[X]) < 10 and abs(p.y - event.pos[Y]) < 10 :
                        selected = p
                for p in box_endpoints:
                    if abs(p[0].x - event.pos[X]) < 5 and abs(p[0].y - event.pos[Y]) < 5 :
                        if start_point == None:
                            start_point = box_endpoints.index(p)
                        elif box_endpoints.index(p) != start_point:
                            new_path = [start_point, box_endpoints.index(p)]
                            if new_path not in paths:
                                paths.append(new_path)
                            start_point = None
##            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
##                x,y = pygame.mouse.get_pos()
##                control_points.append(vec2d(x,y))
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                selected = None

        font = pygame.font.SysFont("Arial", 12)
        ### Draw stuff
        screen.fill(darkgreen)
        # Draw tile box
        pygame.draw.lines(screen, True, black, box)
        pygame.draw.lines(screen, True, darkblue, box_midpoints)
        if start_point != None:
            pygame.draw.circle(screen, green, box_endpoints[start_point][0], 7)
        for p in box_endpoints:
            pygame.draw.circle(screen, red, p[0], 3)
            pygame.draw.line(screen, darkblue, p[0], p[0] + 20 * p[1])
            screen.blit(font.render(str(box_endpoints.index(p)), False, black), p[0] - p[1] * 16)

        font = pygame.font.SysFont("Arial", 18)
        for t in range(len(instructions)):
            screen.blit(font.render(instructions[t], False, black), (20,420 + t*20))


        curve_factor = 60
        # Draw a track for every entry in paths
        paths_to_draw = []
        for p in paths:
            a = box_endpoints[p[0]][0]
            b = box_endpoints[p[0]][0] + box_endpoints[p[0]][1] * curve_factor
            c = box_endpoints[p[1]][0] + box_endpoints[p[1]][1] * curve_factor
            d = box_endpoints[p[1]][0]
            paths_to_draw.append([a,b,c,d])
        for p in paths_to_draw:
            draw_track(screen, p, "sleepers")
        for p in paths_to_draw:
            draw_track(screen, p, "track")
##        for p in paths_to_draw:
##            draw_track(screen, p, "controls")

        if selected is not None:
            selected.x, selected.y = pygame.mouse.get_pos()
            pygame.draw.circle(screen, green, selected, 10)


        draw_track(screen, control_points, "sleepers")
        draw_track(screen, control_points, "track")
        draw_track(screen, control_points, "controls")
        draw_track(screen, control_points, "hints")

        # Draw bezier box hints
##        for p in range(0, len(points2), 1):
##            pygame.draw.line(screen, black, points2[p], points3[p])
##        for p in points2:
##            pygame.draw.circle(screen, black, p, 2)
##        for p in points3:
##            pygame.draw.circle(screen, black, p, 2)
        ### Flip screen
        pygame.display.flip()
        clock.tick(100)
        #print clock.get_fps()
##        running = False
    
if __name__ == '__main__':
    main()