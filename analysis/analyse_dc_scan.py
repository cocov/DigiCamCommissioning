#!/usr/bin/env python3

# external modules

# internal modules
from data_treatement import mpe_hist
from analysis import analyse_hvoff
from utils import display, histogram, geometry
import logging,sys
import numpy as np
import logging
from tqdm import tqdm
from utils.logger import TqdmToLogger
import matplotlib.pyplot as plt
__all__ = ["create_histo", "perform_analysis", "display_results"]


def create_histo(options):
    """
    Create a list of ADC histograms and fill it with data

    :param options: a dictionary containing at least the following keys:
        - 'output_directory' : the directory in which the histogram will be saved (str)
        - 'histo_filename'   : the name of the file containing the histogram      (str)
        - 'synch_histo_filename'   : the name of the file containing the histogram      (str)
        - 'file_basename'    : the base name of the input files                   (str)
        - 'directory'        : the path of the directory containing input files   (str)
        - 'file_list'        : the list of base filename modifiers for the input files
                                                                                  (list(str))
        - 'evt_max'          : the maximal number of events to process            (int)
        - 'n_evt_per_batch'  : the number of event per fill batch. It can be
                               optimised to improve the speed vs. memory          (int)
        - 'n_pixels'         : the number of pixels to consider                   (int)
        - 'scan_level'       : number of unique poisson dataset                   (int)
        - 'adcs_min'         : the minimum adc value in histo                     (int)
        - 'adcs_max'         : the maximum adc value in histo                     (int)
        - 'adcs_binwidth'    : the bin width for the adcs histo                   (int)

    :return:
    """

    baseline = histogram.Histogram(filename=options.directory + options.baseline_filename)



    amplitudes = histogram.Histogram(bin_center_min=options.adcs_min, bin_center_max=options.adcs_max,
                               bin_width=options.adcs_binwidth,
                               data_shape=(len(options.scan_level), len(options.pixel_list),),
                               label='MPE', xlabel='ADC', ylabel='$\mathrm{N_{entries}}$')

    mpe_hist.run(amplitudes, options, baseline=baseline.fit_result[:,0])
    amplitudes.save(options.output_directory + options.histo_filename)

    del baseline, amplitudes

    return


def perform_analysis(options):

    return


def display_results(options):
    """
    Display the analysis results

    :param options:

    :return:
    """

    amplitudes = histogram.Histogram(filename=options.output_directory + options.histo_filename)
    display.display_hist(amplitudes, options)

    return