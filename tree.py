#!/usr/bin/env python
"""
This script analyzes the SALAMI dataset as follows:

For each SALAMI track that has two large scale annotations (A, B) and
two small scale annotations (a, b):
    - Compute the F-measures with windows of 3 and 0.5 seconds of:
        - (A, B)  (where A is the annotation and B is the estimation)
        - (A, b)
        - (a, B)
        - (a, b)
    - Do the same but switching the order:
        - (B, A)
        - ...
    - Write results in an output file

To use this script:

    ./analyze_salami.py salami_path -o results.txt

Where salami_path points to the SALAMI folder formatted as follows:
    /root
        /audio          : SALAMI audio files. Each file starts with the
                            "SALAMI_" prefix.
        /annotations    : SALAMI annotations using the JAMS format. Each file 
                            starts with the "SALAMI_" prefix.

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

# Not so common modules
import jams
import librosa
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
		

class SegmentTree(object):
	"""A hierarchical segmentation of a musical piece.
	"""
	def __init__(self, jam_file, annotation_id=0):
		"""Initialize a segment tree using a jam annotation file and a
		specific annotation id in case the jam file contains multiple
		annotations."""
		self.jam = jams.load(jam_file)

		def get_levels():
			levels = []
			annotation = self.jam.sections[annotation_id]
			[levels.append(segment.label.context) for segment in \
					annotation.data if segment.label.context not in levels]
			return levels

		levels = get_levels()
		print levels

		
