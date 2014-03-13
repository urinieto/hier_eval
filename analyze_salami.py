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
        /audio          : SALAMI audio files (not really necessary).
        /annotations    : SALAMI annotations using the JAMS format.

"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPLv3"
__version__ = "1.0"
__email__ = "oriol@nyu.edu"

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

def process(in_path, out_file):
    """Main process to analyze SALAMI."""
    annot_files = glob.glob(os.path.join(in_path, "annotations", "*.jams"))
    print len(annot_files)

def main():
    """Main function to parse the arguments and call the main process."""
    parser = argparse.ArgumentParser(description=
        "Analyzes the SALAMI dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_path",
                        action="store",
                        help="Path to the SALAMI dataset")
    parser.add_argument("-o", 
                        action="store", 
                        dest="out_file",
                        help="Output file to save the results",
                        default="salami_results.txt")

    args = parser.parse_args()
    start_time = time.time()
   
    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
        level=logging.INFO)

    # Run the process
    process(args.in_path, args.out_file)

    # Done!
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))

if __name__ == '__main__':
    main()