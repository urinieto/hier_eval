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
        >> segments = st.get_segments_in_level(0)       # Same as above

    Get the available levels (note that a flat annotation will have 2 levels:
                              root + the annotated one):
        >> levels = st.levels

    Print the tree:
        >> print st

    To work with the nodes of the tree:
        >> node = st.root               # Access the root of the tree.
        >> child = node.children[0]     # Access the first child of a node.
        >> parent = child.parent        # This is redundant, but it shows
                                        # the ability to access the parent
                                        # of a node.
        >> segment = node.segment       # Access the segment of a given
                                        # node.

    To prune the tree at level "small_scale":
        >> st.prune_to_level("small_scale")

    To prune at level 3:
        >> st.prune_to_level(3)

    To collapse the tree at level "large_scale":
        >> st.collapse_to_level("large_scale")

    To collapse the tree at level 2:
        >> st.collapse_to_level(2)

The segments are stored in a simple class called Segment. To print a Segment,
simply:
        >> print segment

which will print the member variables of this class, which can be accessed
separately.

"""

__author__      = "Oriol Nieto"
__copyright__   = "Copyright 2015, Music and Audio Research Lab (MARL)"
__license__     = "MIT"
__version__     = "1.0"
__email__       = "oriol@nyu.edu"

import logging
import numpy as np
from collections import Counter


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

    def add_child(self, child):
        self._children.append(child)


class SegmentTree(object):
    """A hierarchical segmentation of a musical piece.
    """
    def __init__(self, hier_bounds, hier_labels, hier_levels=None):
        """TODO."""
        def times_to_intervals(times):
            """Given a set of times, convert them into intervals.

            Parameters
            ----------
            times: np.array(N)
                A set of times.

            Returns
            -------
            inters: np.array(N-1, 2)
                A set of intervals.
            """
            return np.asarray(zip(times[:-1], times[1:]))

        def get_segments_in_range(start, end, times, labels):
            """Gets the segments that are within a specific range at a certain
                level."""
            inters = times_to_intervals(times)
            segments = []
            for i, interval in enumerate(inters):
                if interval[0] >= start and interval[1] <= end:
                    segments.append(Segment(interval[0], interval[1],
                                            labels[i]))
            return segments

        def build_tree_rec(node, level_idx):
            """Builds the tree in a recursive way."""
            if level_idx >= len(self._levels) - 1:
                return

            for segment in get_segments_in_range(node.segment.start,
                                                 node.segment.end,
                                                 hier_bounds[level_idx],
                                                 hier_labels[level_idx]):
                new_node = Node(segment, self._levels[level_idx + 1], node)
                node.add_child(new_node)
                build_tree_rec(new_node, level_idx + 1)

        def build_tree():
            """Build the segment tree"""
            # Add the root level segment that comprises the entire track
            root_segment = Segment(0, hier_bounds[0][-1], "all")

            # Create the tree recursively
            level_idx = 0
            root_node = Node(root_segment, self._levels[level_idx])
            build_tree_rec(root_node, level_idx)
            return root_node

        # Assign standard levels if not passed as parameter
        if hier_levels is None:
            hier_levels = ["level_%d" % i for i in range(len(hier_bounds))]

        # Add the root level
        self._levels = np.concatenate((["root"], hier_levels))

        # Build actual tree
        self._root = build_tree()

    @property
    def root(self):
        return self._root

    @property
    def levels(self):
        return self._levels

    @property
    def jams_file(self):
        return self._jams_file

    def _is_level_correct(self, level=None, level_idx=None):
        """Makes sure that the level provided is correct."""
        if level is None and level_idx is None:
            logging.error("Parameter level or level_idx must be set.")
            return False
        if level_idx is not None and level_idx >= len(self._levels):
            logging.error("level_idx %d out of bounds." % level_idx)
            return False
        if level is not None and level not in self._levels:
            logging.error("level %s does not exist." % level)
            return False
        return True

    def _get_segments_rec(self, node, segments, level=None, level_idx=None):
        """Appends the segments of the corresponding level or level index
            into the segments list."""
        if level is None:
            level = self._levels[level_idx]

        # Append segment if we are in the right level
        if node.level == level:
            segments.append(node.segment)

        # Recursion
        for child in node.children:
            self._get_segments_rec(child, segments, level, level_idx)

    def _prune_to_level_rec(self, node, level=None, level_idx=None):
        """Prunes the tree to the specific level recursively."""
        if level is None:
            level = self._levels[level_idx]

        # Prune tree if we are at the right level
        if node.level == level:
            node._children = []

        # Recursion
        for child in node.children:
            self._prune_to_level_rec(child, level, level_idx)

    def get_segments_in_level(self, level=None, level_idx=None):
        """Return a list with all the segments in a certain level."""
        if not self._is_level_correct(level, level_idx):
            return []

        segments = []
        self._get_segments_rec(self._root, segments, level=level,
                               level_idx=level_idx)
        return segments

    def prune_to_level(self, level=None, level_idx=None):
        """Prunes to a specific level (included)."""
        if not self._is_level_correct(level, level_idx):
            return []

        # Prune tree recursively
        self._prune_to_level_rec(self._root, level, level_idx)

    def collapse_to_level(self, level=None, level_idx=None):
        """Collapses tree to a specifc level (included)."""
        if not self._is_level_correct(level, level_idx):
            return []

        # Get the segments of the specific level we want
        segments = self.get_segments_in_level(level, level_idx)

        if level is None:
            level = self._levels[level_idx]

        # Reset tree
        self._root._children = []
        for segment in segments:
            new_node = Node(segment, level, self._root)
            self._root.add_child(new_node)

        # Reset levels
        self._levels = ["root", level]

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
