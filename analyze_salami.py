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


def read_annotation(annot_file, annotator, context):
    """Reads the JAM annotation in annot_file."""
    times, labels = mir_eval.input_output.load_jams_range(annot_file, 
                    "sections", annotator=annotator, context=context)
    return times


def eval_boundaries(annot_bounds, est_bounds, window, trim):
    """Evaluates the annotated and estimated boundaries with a specific
        window size and trimming option."""
    return mir_eval.segment.boundary_detection(annot_bounds, est_bounds, 
                                                window=window, trim=trim)


def evaluate_annotations(annot_file, trim=False):
    """Evaluates the annotations inside the annot_file JAMS file.

    Returns:
    - res: np.asarray
        Results contained in a np.array matrix where the rows are the following
        annotation combinations:
            (A,B),(A,b),(a,B),(a,b),(B,A),(b,A),(B,a),(b,a)
        And the columns are the following metrics:
            P0.5, R0.5, F0.5, P3, R3, F3
    """
    
    windows = [0.5, 3]                  # Window times 
    annot_combinations = [[0,1],[1,0]]  # Order of the annotators
    res = []                            # Results

    for annotators in annot_combinations:
        try:
            A = read_annotation(annot_file, annotators[0], "large_scale")
            B = read_annotation(annot_file, annotators[1], "large_scale")
            a = read_annotation(annot_file, annotators[0], "small_scale")
            b = read_annotation(annot_file, annotators[1], "small_scale")
        except:
            # logging.warning("Less than 2 annotations in file %s" % annot_file)
            return None

        time_comps = [(A,B),(A,b),(a,B),(a,b)]

        for times in time_comps:
            for window in windows:
                res.append(eval_boundaries(times[0], times[1], window, trim))

    N = len(time_comps) * len(annot_combinations)
    M = len(windows) * 3 # 3 metrics per window: F-measure, Precision, Recall
    return np.resize(res, (N,M))


def write_results(results, out_file):
    """Writes the results in the output file."""
    mean_results = results.mean(axis=0)
    out_str = "Comp\tP0.5\tR0.5\tF0.5\tP3\tR3\tF3\n"
    comps = ["(A,B)","(A,b)","(a,B)","(a,b)","(B,A)","(b,A)","(B,a)","(b,a)"]
    for i, res in enumerate(mean_results):
        out_str += comps[i] + "\t"
        for single_res in res:
            out_str += "%.2f\t" % (100*single_res)
        out_str = out_str[:-1] + "\n"
    with open(out_file, "w") as f:
        f.write(out_str)


def process(in_path, out_file, trim):
    """Main process to analyze SALAMI."""
    prefix = "SALAMI_"
    annot_files = glob.glob(os.path.join(in_path, "annotations", 
                                                    "%s*.jams" % prefix))

    logging.info("Analyzing the SALAMI dataset located in %s ..." % in_path)
    all_res = []
    for annot_file in annot_files:
        curr_res = evaluate_annotations(annot_file, trim=trim)
        if curr_res is None:
            continue
        all_res.append(curr_res)
    all_res = np.asarray(all_res)
    logging.info("Analyzed %d files." % all_res.shape[0])
    
    logging.info("Writing results into %s ..." % out_file)
    write_results(all_res, out_file)

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
    parser.add_argument("-t", 
                        action="store_true",
                        dest="trim",
                        help="Trims the first and last boundaries",
                        default=False)

    args = parser.parse_args()
    start_time = time.time()
   
    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
        level=logging.INFO)

    # Run the process
    process(args.in_path, args.out_file, args.trim)

    # Done!
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))

if __name__ == '__main__':
    main()
