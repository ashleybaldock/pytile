#!/usr/bin/python

import os, sys
import pygame
import random, math
from copy import copy

##in_data = [8,1,3,10,2,4,7,6,9,5]
##in_data = [4,1,3,2,16,9,10,14,8,7]

def parent(i):
    """Find parent node of node i"""
    return (i - 1) / 2
def left(i):
    """Find left child node of node i"""
    return 2 * i + 1
def right(i):
    """Find right child node of node i"""
    return 2 * i + 2

# Comparator functions should take two objects, a and b, and return true if a is above b in the heap,
# false otherwise
def gt_comparator(a, b):
    """Comparison function, tests if object "a" should come before object "b" in the heap"""
    if a < b:
        return True
    else:
        return False

def max_heapify(A, lengthA, i, comparator):
    """Repair max heap property of max heap "A" from node "i" down"""
    l = left(i)
    r = right(i)
    if l < lengthA and comparator(A[l], A[i]):
        largest = l
    else:
        largest = i
    if r < lengthA and comparator(A[r], A[largest]):
        largest = r
    if largest != i:
        t = A[i]
        A[i] = A[largest]
        A[largest] = t
        A = max_heapify(A, lengthA, largest, comparator)
    return A

def build_max_heap(A, lengthA, comparator):
    """Build a max heap from unsorted data"""
    for i in range(lengthA / 2, -1, -1):
        A = max_heapify(A, lengthA, i, comparator)
    return A


# Needs a way to change the position of only certain elements within the heap, probably best
# done by removing them from the heap and then re-adding them based on their new comparison
# However this may be slow, better to swap them in-place with the root node, then re-heapify
# the heap from the root down
# Do this for every changed node in sequence, quicker than rebuilding the entire thing from scratch?

# Output will always be to the drawing routine, so needs to output a sorted array, and be able to
# insert/update only the elements which have changed


def heapsort(A, comparator):
    """Sort unordered input array A in-place using heapsort"""
    lengthA = len(A)
    A = build_max_heap(A, lengthA, comparator)
    B = []
    for i in range(lengthA, 1, -1):
        # Swap item at the end of the tree with the root node, then re-heapify from the root node
        t = A[i-1]
        A[i-1] = A[0]
        A[0] = t
        # Reduce the length by 1 each time, to store the output in the same array
        lengthA -= 1
        max_heapify(A, lengthA, 0, comparator)
    return A

if __name__ == "__main__":
    for j in range(10):
        fail = False
        i = []
        for k in range(30):
            i.append(random.randint(0,100))
        out = heapsort(copy(i), gt_comparator)
        for m in range(len(out)-1):
            if gt_comparator(out[m], out[m+1]):
                fail = True
        if fail:
            time.time()
            print i
            print out
            print "FAIL!"
        else:
            print i
            print out
            print "WIN!"

    
