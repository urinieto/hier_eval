#!/usr/bin/env python
"""
A few unit tests to verify the implementationn of the SegmentTree.
"""

__author__      = "Oriol Nieto"
__copyright__   = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__     = "GPLv3"
__version__     = "1.0"
__email__       = "oriol@nyu.edu"

import unittest
from tree import SegmentTree


class TestSegmentTree(unittest.TestCase):

    def setUp(self):
        """Load JAMS. One flat (Isophonics) and one hierarchichal (SALAMI)."""
        self.flat_st = SegmentTree("test/Isophonics_01_-_"
                                   "A_Hard_Day\'s_Night.jams")
        self.hier_st = SegmentTree("test/SALAMI_636.jams")

    def test_hier_levels(self):
        """Checks the levels of the hierarchical tree."""
        # 4 levels: root, function, large_scale and small_scale
        self.assertEqual(len(self.hier_st.levels), 4)

    def test_flat_levels(self):
        """Checks the levels of the flat tree."""
        # 2 levels: root and function
        self.assertEqual(len(self.flat_st.levels), 2)

    def test_hier_segment_retrieval(self):
        """Checks whether we are able to retrieve all segments of a
            hierarchical tree."""
        # Root level
        self.assertEqual(len(self.hier_st.get_segments_in_level("root")), 1)
        self.assertEqual(len(self.hier_st.get_segments_in_level(level_idx=0)),
                         1)
        # Function level
        self.assertEqual(len(self.hier_st.get_segments_in_level("function")),
                         11)
        self.assertEqual(len(self.hier_st.get_segments_in_level(level_idx=1)),
                         11)
        # Large scale level
        self.assertEqual(len(self.hier_st.get_segments_in_level(
                         "large_scale")), 11)
        self.assertEqual(len(self.hier_st.get_segments_in_level(level_idx=2)),
                         11)
        # Small scale level
        self.assertEqual(len(self.hier_st.get_segments_in_level(
                         "small_scale")), 33)
        self.assertEqual(len(self.hier_st.get_segments_in_level(level_idx=3)),
                         33)

    def test_flat_segment_retrieval(self):
        """Checks whether we are able to retrieve all segments of a
            flat tree."""
        # Root level
        self.assertEqual(len(self.flat_st.get_segments_in_level("root")), 1)
        self.assertEqual(len(self.flat_st.get_segments_in_level(level_idx=0)),
                         1)
        # Function level
        self.assertEqual(len(self.flat_st.get_segments_in_level("function")),
                         12)
        self.assertEqual(len(self.flat_st.get_segments_in_level(level_idx=1)),
                         12)

    def test_pruning(self):
        """Checks the prunning function."""
        # Prune at Function level
        self.hier_st.prune_to_level("function")
        self.assertEqual(len(self.hier_st.get_segments_in_level("function")),
                         11)
        self.assertEqual(len(self.hier_st.get_segments_in_level("large_scale")
                             ), 0)

    def test_collapse(self):
        """Checks the collapse function."""
        # Reload in case we prunned it before
        self.hier_st = SegmentTree("test/SALAMI_636.jams")
        self.hier_st.collapse_to_level("small_scale")
        self.assertEqual(len(self.hier_st.get_segments_in_level(
                         "small_scale")), 33)
        self.assertEqual(len(self.hier_st.get_segments_in_level(
                         "large_scale")), 0)
        self.assertEqual(len(self.hier_st.get_segments_in_level(
                         "root")), 1)
        self.assertEqual(len(self.hier_st.levels), 2)


if __name__ == '__main__':
    unittest.main()
