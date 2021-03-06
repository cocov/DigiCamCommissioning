
#!/usr/bin/env python3

# external modules
import logging,sys
import numpy as np
from tqdm import tqdm
from utils.logger import TqdmToLogger


# internal modules
from data_treatement import visualise_trace
from utils import display, histogram, geometry

__all__ = ["create_histo", "perform_analysis", "display_results", "save"]


def create_histo(options):
    """
    """

    print('Nothing implemented')

    return


def perform_analysis(options):
    """
    """

    print('Nothing implemented')

    return


def display_results(options):
    """
    """
    viewer = visualise_trace.EventViewer(options)
    #viewer.save()
    #viewer.animate_pixel_scan(pixel_list=options.pixel_list, filename='test.mp4')
    #viewer.animate_muon_scan(filename=options.movie_filename, n_frames=options.n_frames)
    viewer.draw()


    #viewer.heat_map_animation(filename=options.movie_filename, n_frames=options.n_frames, limits_colormap=options.limits_colormap)


    return


def save(options):

    print('Nothing implemented')

    return




