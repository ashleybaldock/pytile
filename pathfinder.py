# coding: UTF-8
#
# This file is part of the pyTile project
#
# http://entropy.me.uk/pytile
#
## Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.
##
## Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
##
## 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
##
## 3. The name of the author may not be used to endorse or promote products derived from this software without specific prior written permission from the author.
##
## 4. Products derived from this software may not be called "pyTile" nor may "pyTile" appear in their names without specific prior written permission from the author.
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 



import os, sys
import pygame
import random

import world
World = world.World()

import copy

import logger
debug = logger.Log()

# Pre-compute often used multiples
p = 64
p2 = p / 2
p4 = p / 4
p4x3 = p4 * 3
p8 = p / 8
p16 = p / 16

#tile height difference
ph = 8

#
class Lookup(dict):
    """A dictionary which can lookup value by key, or keys by value"""
    def __init__(self, items=[]):
        """items can be a list of pair_lists or a dictionary"""
        dict.__init__(self, items)
 
    def get_key(self, value):
        """find the key(s) as a list given a value"""
        return [item[0] for item in self.items() if item[1] == value]
 
    def get_value(self, key):
        """find the value given a key"""
        return self[key]

class AStarError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class AStar(object):
    # Variables that persist through instances of this class
    # Reference with Pathfinder.var
    # G = the movement cost to move from the starting point A to a given square on the grid, following the path generated to get there
    # H = the estimated movement cost to move from that given square on the grid to the final destination
    # F = G + H

    width = 1
    def __init__(self):
        """"""
        # Needs to store:
        # Tile location (UID)
        # Parent tile location (UID)
        # G cost to this square via best route so far
        # H cost from this square to the target
        # F cost (G + H)
        # (x, y): ((px, py), g, h, f)
        self.open = {}
        self.closed = {}

    def get_lowest_f(self):
        """Returns the tile(s) from the open list with the lowest F value, which should be considered next"""
        return [item[0] for item in a.items() if item[1] == min(a.values(), key=lambda x: x[3])]

    def in_open_list(self, node):
        """Returns true if the node specified is on the open list"""
        return self.open.has_key(node)

    def in_closed_list(self, node):
        """Returns true if the node specified is on the closed list"""
        return self.closed.has_key(node)

    def get_adjacent(self, node):
        """Finds adjacent nodes to the current node"""
        xmin = max(node[0]-1, 0)
        xmax = min(node[0]+1, World.WorldX)
        ymin = max(node[0]-1, 0)
        ymax = min(node[0]+1, World.WorldY)

        return [(x,y) for x in range(xmin, xmax) for y in range(ymin, ymax)]

    def get_move_cost(self, node1, node2):
        """Returns the cost to move from node1 to node2"""
        # If node1 x and node2 x are the same, or node1 y and node2 y are the same then cost is 10, else it's 14
        if node1[0] == node2[0] or node1[1] == node2[1]:
            cost = 10
        else:
            cost = 14
        debug("Movement cost from %s to %s is: %s" % (node1, node2, cost))
        return cost

    def heuristic(self, node, target):
        """Returns approximate cost to move from node to target"""
        # Using the Chebyshev distance allowing for diagonal movement
        xdistance = abs(node[0] - target[0])
        ydistance = abs(node[0] - target[0])
        if xdistance > ydistance:
            H = 14*ydistance + 10*(xdistance-ydistance)
        else:
            H = 14*xdistance + 10*(ydistance-xdistance)
        debug("Heuristic distance from %s to %s calculated as: %s" % (node, target, H))
        return H


    def find_path(self, start, end):
        """Implementation of the a* algorithm"""
        # This operates across the world, based on the start and end tile specified

        # Not taking terrain into account, world is flat grid etc.

        # Add start to open list
        # (x, y): ((px, py), g, h, f)
        debug("Pathfinding start, adding: %s to open list as starting node, parent: %s, values: %s" % (start, start, (0,0,0)))
        self.open[start] = (start, 0, 0, 0)

        # Loop
        done = False
        while not done:
            debug(self.open)
            debug(self.closed)

            # For lowest F cost in open list:
            lowf = self.get_lowest_f()[0]
            debug("lowf is: %s" % lowf)

            # Find neighbours, 8 tiles surrounding it
            adj = self.get_adjacent(lowf)
            debug("adj is: %s" % adj)

            for a in adj:
                # Check if each of these is in closed list, if so do nothing with it
                if not in_closed_list(a):
                    # If not in closed list, check if it's in the open list
                    if not in_open_list(a):
                        # If it is not in the open list, add it to the open list with this square as its parent
                        # Cost to get here is cost to get to parent plus cost from parent to this node
                        g = self.open[lowf][1] + self.get_move_cost(lowf, a)
                        # Heuristic for this node to target
                        h = self.heuristic(a, target)
                        debug("Adding %s to open list with parent: %s and values: %s" % (a, lowf, (g,h,g+h)))
                        self.open[a] = (lowf, g, h, g+h)
                    # If it is in the open list, check if the path via the current square is better (compare G cost)
                    else:
                        g = self.open[lowf][1] + self.get_move_cost(lowf, a)
                        if g < self.open[a][1]:
                            # Path via this node is better, change parent to this node
                            h = self.heuristic(a, target)
                            debug("Changing parent of %s to: %s, new values: %s" % (a, lowf, (g,h,g+h)))
                            self.open[a] = (lowf, g, h, g+h)

            # Move current node from open to closed list
            debug("Moving node: %s from open to closed list" % lowf)
            self.closed[lowf] = self.open.pop(lowf)

            # Check for completion, is target in closed list?
            if self.closed.has_key(target):
                debug("Completion test passed, target: %s is in closed list, calculating path..." % target)
                done = True
                path = [target]
                part = target
                # Follow chain of parent relations back to the start
                while part != start:
                    # Add parent
                    part = self.closed[part][0]
                    path.append(part)
                debug("Path calculated as: %s" % path)
                    
            # Is the open list empty?
            if len(self.open) == 0:
                debug("Completion test passed, open list is empty, pathfinding failure")
                done = True
                path = None

        # Stop when target square is added to the closed list = route
        # Stop when open list is empty and the target square has not been found = no route
        return path
        



