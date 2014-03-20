#!/usr/bin/env python
"""
Implementation of a hierarchical segment annotation using a rooted tree.

The root of the tree has always one segment representing the entire track. The 
label of this segment is "all" and the level is called "root".

Usage:

    Initialize tree from JAMS file:
        >> import tree as T
        >> st = T.SegmentTree("path/to/SALAMI_636.jams")
    
    Get all the segment in the first level of the tree: 
        >> segments = st.get_segments_in_level("root")
        >> segments = st.get_segments_in_level_idx[0] # Same as above

    Get the available levels (note that a flat annotation will have 2 levels:
                              root + the annotated one):
        >> levels = st.levels

    Print the tree:
        >> print st


The segments are stored in a simple class called Segment. To print a Segment,
simply:
        >> print segment

which will print the member variables of this class, which can be accessed
separately.

"""

__author__      = "Oriol Nieto"
__copyright__   = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__     = "GPLv3"
__version__     = "1.0"
__email__       = "oriol@nyu.edu"

import argparse
import glob
import logging
import os
import pylab as plt
import numpy as np
import time
from scipy.spatial import distance
from collections import Counter

# Not so common modules
import jams
import mir_eval

class Segment(object):
    """Musical segment.

    Represented by a start and end times, a label, and their associated
    confident values.
    """
    def __init__(self, start, end, label, start_conf=None, 
            end_conf=None, label_conf=None):
        self._start = start
        self._end = end
        self._label = label
        self._start_conf = start_conf
        self._end_conf = end_conf
        self._label_conf = label_conf

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def label(self):
        return self._label

    @property
    def start_conf(self):
        return self._start_conf

    @property
    def end_conf(self):
        return self._end_conf

    @property
    def label_conf(self):
        return self._label_conf

    def __str__(self):
        """Render the object as a readable string."""
        s = "Segment at %s:\n" % hex(id(self))
        s += "\tstart:\t%.2f\n" % self.start
        s += "\tend:\t%.2f\n" % self.end
        s += "\tlabel:\t%s" % self.label
        return s


class Node(object):
    """A node of a segment tree."""
    def __init__(self, segment, level, parent=None):
        """Initialize a Node. If parent is None, then the node is the 
        root of the tree."""
        self._segment = segment
        self._level = level
        self._parent = parent
        self._children = []

    @property
    def segment(self):
        return self._segment

    @property
    def level(self):
        return self._level

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    def add_child(self,child):
        self._children.append(child)
            

class SegmentTree(object):
    """A hierarchical segmentation of a musical piece.
    """
    def __init__(self, jam_file, annotation_id=0):
        """Initialize a segment tree using a jam annotation file and a
        specific annotation id in case the jam file contains multiple
        annotations."""
        self._jam = jams.load(jam_file)

        def get_levels():
            """Obtains the set of unique levels contained in the jams 
               sorted by the number of segments they contain."""
            levels = []
            annotation = self._jam.sections[annotation_id]
            [levels.append(segment.label.context) \
                                for segment in annotation.data]
            c = Counter(levels) # Count frequency
            return np.asarray(c.keys())[np.argsort(c.values())] # Sort

        def get_segments_in_range(start, end, level):
            """Gets the segments that are within a specific range at a certain
                level."""
            intervals, labels = mir_eval.input_output.load_jams_range(jam_file, 
                    "sections", annotator=annotation_id, context=level)
            segments = []
            for i, interval in enumerate(intervals):
                if interval[0] >= start and interval[1] <= end:
                    segments.append(Segment(interval[0], interval[1], 
                                            labels[i]))
            return segments

        def build_tree_rec(node, level_idx):
            """Builds the tree in a recursive way."""
            if level_idx >= len(self._levels) - 1:
                return

            for segment in get_segments_in_range(node.segment.start, 
                    node.segment.end, self._levels[level_idx+1]): 
                new_node = Node(segment, self._levels[level_idx+1], node)
                node.add_child(new_node)
                build_tree_rec(new_node, level_idx+1)

        def build_tree():
            """Build the segment tree"""
            # Add the root level segment that comprises the entire track
            root_segment = Segment(0, self._jam.metadata.duration, "all")

            # Create the tree recursively
            level_idx = 0
            root_node = Node(root_segment, self._levels[level_idx])
            build_tree_rec(root_node, level_idx)
            return root_node

    
        # Get the levels of the annotations in the jams file
        self._levels = get_levels()

        # Add the root level
        self._levels = np.concatenate((["root"], self._levels))

        # Build the tree
        self._root = build_tree()

    @property
    def root(self):
        return self._root
    
    @property
    def levels(self):
        return self._levels

    def _get_segments_rec(self, node, segments, level=None, level_idx=None):
        """Appends the segments of the corresponding level or level index
            into the segments list."""
        # Sanity Checks
        if level is None and level_idx is None:
            logging.error("Parameter level or level_idx must be set.")
            return
        if level_idx is not None and level_idx >= len(self._levels):
            logging.error("level_idx %d out of bounds." % level_idx)
            return
        if level is not None and level not in self._levels:
            logging.error("level %s does not exist." % level)
            return
        
        if level is None:
            level = self._levels[level_idx]

        # Append segment if we are in the right level
        if node.level == level:
            segments.append(node.segment)

        # Recursion
        for child in node.children:
            self._get_segments_rec(child, segments, level, level_idx)


    def get_segments_in_level_idx(self, level_idx):
        """Return a list with all the segments in a certain level index."""
        segments = []
        self._get_segments_rec(self._root, segments, level_idx=level_idx)
        return segments

    def get_segments_in_level(self, level):
        """Return a list with all the segments in a certain level."""
        segments = []
        self._get_segments_rec(self._root, segments, level=level)
        return segments

    def print_tree(self, node):
        """Prints the tree recursively from top to bottom."""
        print node.segment
        print "\tlevel:", node.level

        for child in node.children:
            self.print_tree(child)

        return ""

    def __str__(self):
        """Render the object as a readable string."""
        return self.print_tree(self._root)
        
            
