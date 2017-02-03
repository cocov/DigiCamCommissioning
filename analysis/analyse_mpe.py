#!/usr/bin/env python3

# external modules

# internal modules
from data_treatement import mpe_hist
from spectra_fit import fit_low_light,fit_high_light
from utils import display, histogram, geometry
import logging,sys
import numpy as np
import logging
from tqdm import tqdm
from utils.logger import TqdmToLogger

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

    # Define the histograms
    mpes = histogram.Histogram(bin_center_min=options.adcs_min, bin_center_max=options.adcs_max,
                               bin_width=options.adcs_binwidth, data_shape=(len(options.scan_level),options.n_pixels,),
                               label='MPE',xlabel='Peak ADC',ylabel = '$\mathrm{N_{entries}}$')
    # Get the reference sampling time
    peaks = histogram.Histogram(filename = options.output_directory + options.synch_histo_filename)
    mpe_hist.run(mpes, options, peak_positions= peaks.data)

    # Save the histogram
    mpes.save(options.output_directory + options.histo_filename)

    # Delete the histograms
    del mpes,peaks

    return


def perform_analysis(options):
    """
    Perform a simple gaussian fit of the ADC histograms

    :param options: a dictionary containing at least the following keys:
        - 'output_directory' : the directory in which the histogram will be saved (str)
        - 'histo_filename'   : the name of the file containing the histogram
                                                 whose fit contains the gain,sigmas etc...(str)

    :return:
    """
    # Fit the baseline and sigma_e of all pixels
    mpes = histogram.Histogram(filename=options.output_directory + options.histo_filename)
    nlevel = mpes.data.shape[0]
    mpes_full = histogram.Histogram(filename=options.output_directory + options.full_histo_filename, fit_only= True)
    mpes_full_fit_result = np.copy(mpes_full.fit_result)
    del mpes_full
    mpes_full_fit_result = mpes_full_fit_result.reshape((1,) + mpes_full_fit_result.shape)
    mpes_full_fit_result = np.repeat(mpes_full_fit_result, nlevel, axis=0)

    log = logging.getLogger(sys.modules['__main__'].__name__+__name__)
    pbar = tqdm(total=mpes.data.shape[0]*mpes.data.shape[1])
    tqdm_out = TqdmToLogger(log, level=logging.INFO)

    def std_dev(x, y):
        avg = np.average(x, weights=y)
        return np.sqrt(np.average((x - avg) ** 2, weights=y))

    ## Now perform the mu and mu_XT fits
    for pixel in range(mpes.data.shape[1]):
        force_xt = False
        if pixel > 0: log.debug('Pixel #' + str(pixel - 1)+' treated')
        for level in range(mpes.data.shape[0]):
            pbar.update(1)
            if np.isnan(mpes_full_fit_result[0,pixel,0,0]): continue
            if np.nonzero(mpes.data[level, pixel])[0].shape[0] == 1: continue
            if std_dev(mpes.bin_centers, mpes.data[level, pixel]) > 400: continue
            if mpes.data[level, pixel, -1] > 0.02 * np.sum(mpes.data[level, pixel]): continue

            # check if the mu of the previous level is above 5
            fixed_param = []
            _fit_spectra = fit_low_light
            if level > 0 and mpes.fit_result[level - 1, pixel, 0, 0] > 30.:
                fixed_param = [
                    # in this case assign the cross talk estimation with smallest error
                    [1, mpes.fit_result[np.argmin(mpes.fit_result[0:level - 1:1, pixel, 1, 1]), pixel, 1, 0]],
                    [2, (1, 0)],  # gain
                    [3, (0, 0)],  # baseline
                    # [4,(2,0)], # sigma_e
                    [5, (3, 0)],  # sigma_1
                    [7, 0.]  # offset
                ]
                _fit_spectra = fit_high_light
            elif (level > 0 and mpes.fit_result[level - 1, pixel, 0, 0] > 5.) or force_xt:
                force_xt = True
                fixed_param = [
                    # in this case assign the cross talk estimation with smallest error
                    [1, mpes.fit_result[np.argmin(mpes.fit_result[0:level - 1:1, pixel, 1, 1]), pixel, 1, 0]],
                    [2, (1, 0)],  # gain
                    [3, (0, 0)],  # baseline
                    [4, (2, 0)],  # sigma_e
                    [5, (3, 0)],  # sigma_1
                    [7, 0.]  # offset
                ]
            else:
                fixed_param = [
                    [2, (1, 0)],  # gain
                    [3, (0, 0)],  # baseline
                    [4, (2, 0)],  # sigma_e
                    [5, (3, 0)],  # sigma_1
                    [7, 0.]  # offset
                ]
            mpes.fit(_fit_spectra.fit_func, _fit_spectra.p0_func, _fit_spectra.slice_func,
                     _fit_spectra.bounds_func, config=mpes_full_fit_result, fixed_param=fixed_param
                     , limited_indices=[(level, pixel,)], force_quiet=True, labels_func=_fit_spectra.label_func)

    mpes.save(options.output_directory + options.fit_filename)


def display_results(options):
    """
    Display the analysis results

    :param options:

    :return:
    """

    # Load the histogram
    adcs = histogram.Histogram(filename=options.output_directory + options.histo_filename)

    # Define Geometry
    geom = geometry.generate_geometry_0()

    # Perform some plots
    display.display_hist(adcs, geom, index_default=(700,), param_to_display=-1, limits=[1900., 2100.])

    input('press button to quit')

    return