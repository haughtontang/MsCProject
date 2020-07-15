# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 12:20:18 2020

@author: Don Haughton
"""
import GPy
from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import UsefulMethods as um
import SimilarityCalc as sc
import numpy as np

#Method for creating numpy arrays that are needed for the model

def create_params(peak_file1, peak_file2):
    '''
    Parameters
    ----------
    peak_file1 : file path for a picked peak file
    peak_file2 : file path for a picked peak file
    DESCRIPTION: Takes a file path, creats a list of peak objects, matches then to
    create peaksets, extracts the RTs, converts to numpy arrays; ready to be
    used to create a GP model
    
    Returns
    -------
    X and Y variables needed to create a GP model
    '''
    
    #Create list of Peak Objects
    
    multi1 = um.peak_creator(peak_file1)
    multi2 = um.peak_creator(peak_file2)
    
    #Sort by intensity
    
    multi1.sort(key = lambda x: x.intensity)
    multi2.sort(key = lambda x: x.intensity)
    
    #For the model we want high quality matching peaksets so the RT threshold is
    #Set to only 1 second
    
    pps = ps.align(multi1, multi2,0.025)
    
    #Create peakset objects
    
    peaksets = ps.make_peaksets(pps)
    
    #Again, we want high quality peaksets so we want to validate them by their MS2 spectra
    
    ms2_validated_peaksets = ps.ms2_comparison(peaksets)
    
    #Extract the RT from the Matched peaksets that are validated by m/z, rt and MS2
    
    multi1_rt, multi2_rt = plot.rt_extract_convert(ms2_validated_peaksets)
    
    #Creates the RT minus list that is needed to build the model
    
    rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
    
    #The model requires numpy arrays for its argument, numpy is used here to convert the list of RTs to arrays
    
    X = np.array(multi2_rt).reshape(len(multi2_rt),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    return X, Y

def make_model(X, Y, kernel):
    
    '''
    Parameters
    ----------
    X : Input variable
    Y : Observed change
    kernel : kernel object from GPy
    DESCRIPTION: creates a regression model using the GPy package

    Returns
    -------
    Model for a Gaussian Process

    '''
    
    return GPy.models.GPRegression(X,Y, kernel = kernel)   

def correct_rt(model, file_to_correct, RT_tolerance)
    
    