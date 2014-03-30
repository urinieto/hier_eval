#!/usr/bin/env python

import os
import json

import segmenter

import jams

def get_all_levels(X, kmin, kmax):
    '''Return a list of segment boundaries/prunings for all values of k between kmin
    and kmax.

    Also returns a list of labels.
    '''

    levels = []
    labels = []

    for k in range(kmin, kmax):
        S, _ = segmenter.get_k_segments(X, k)
        levels.append(S)
        labels.append('level_%03d' % k)

    return levels, labels

def make_intervals(boundaries, beats):

    intervals = []
    for start_b, end_b in zip(boundaries[:-1], boundaries[1:]):
        intervals.append([beats[start_b], beats[end_b]])

    return intervals


def make_metadata(annotation):

    annotation.annotation_metadata.attribute = 'sections'
    annotation.annotation_metadata.annotation_tools = 'OLDA'

    pass

def add_level(annotation, level, intervals):


    for label, (start, end) in enumerate(intervals):
        section = annotation.create_datapoint()

        section.start.value = start
        section.end.value = end
        section.label.value = label

        section.start.confidence = 1.0
        section.end.confidence = 1.0
        section.label.confidence = 1.0

        section.label.context = level



def make_jams(levels, labels, beats):

    J = jams.Jams()

    J.metadata.duration = beats[-1]

    annotation = J.sections.create_annotation()
    make_metadata(annotation)

    for tag, bounds in zip(labels, levels):
        add_level(annotation, tag, make_intervals(bounds, beats))
    
    return J

if __name__ == '__main__':
    parameters = segmenter.process_arguments()

    # Load the features
    print '- ', os.path.basename(parameters['input_song'])

    X, beats    = segmenter.features(parameters['input_song'])

    # Load the boundary transformation
    W_bound     = segmenter.load_transform(parameters['transform_boundary'])
    print '\tapplying boundary transformation...'
    X_bound           = W_bound.dot(X)

    # Find the segment boundaries
    print '\tpredicting segments...'
    kmin, kmax  = segmenter.get_num_segs(beats[-1])
    levels, labels = get_all_levels(X_bound, kmin, kmax)

    J = make_jams(levels, labels, beats)

    with open(parameters['output_file'], 'w') as f:
        json.dump(J, f, indent=2)

