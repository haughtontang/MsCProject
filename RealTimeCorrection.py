# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 09:18:29 2020

@author: Don Haughton
"""

import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc
import GPCorrection as gpc

'''
The first run of the MS is finished so we have the first file, convert what was generated in this file
into peak objects to be used in the future for alignment
'''

def create_peak_objects(filepath, mgf_path):
    
    peaks = um.peak_creator(filepath)
    um.assign_ms2(mgf_path, peaks)
    
    return peaks

'''
This function is dealing with the second run (file) of peaks in real time, in my head
the function accepts one peak at a time, this is stored in a list then when the size of that
list reaches a certain limit its contents are converted into peak objects. These objects, along with the peak
objects that came from file 1 are used to perform the first alignment and create some anchors for the GPR model

My only concern is the way ive set this up bellow I dont think its built for a continuous flow of data,
im not entirely sure how you'd set a method up in that way. In any case, this is only pseudocode so can revist
later
'''

'''
If I'm always dealing with lists of peaks this function may not be necessary.
If this is the case, the list of live runs peaks can just call the above function to
arrange it into a list of peak objects
'''

def incoming_peaks(real_time_run):
    
    #Should be dealing with list of peaks, will leave whats bellow commented out in case Needed later
    '''
    list_of_live_runs = []
    
    #Not sure of an appropriate value for this, can revist later on. 
    
    limit = 50
    
    while len(list_of_live_runs) < limit:
        
        list_of_live_runs.append(real_time_run)
        
    '''
    The way that peak_creator is set up this wont work, maybe need to create a similar
    but realted method that does the exact same thing but without the file reader
    '''    
    '''
    #Create peaks from this list
    
    list_of_peaks = um.peak_creator(real_time_run)
    
    #The file paths may also have to be arguments to this function
    
    first_file = first_run_peaks(filepath, mfg_path)
    
    #sort these based on intensity
    
    first_file.sort(key = lambda x: x.intensity, reverse = True)
    list_of_peaks.sort(key = lambda x: x.intensity, reverse = True)
    
    #perform alignment
    
    ps = alignment(first_file, list_of_peaks)
    
    return ps
  
#Seperate alignment method to clean up the incoming_peaks function and later functions
  
def alignment(first_run_peaks, incoming_peaks):
    
    pseudo_peaksets = ps.align(first_run_peaks, incoming_peaks, 1.5)
    
    peaksets = ps.make_peaksets(pseudo_peaksets)
    
    return peaksets

def create_model(peakset_list, variance, lengthscale):
    
    anchors = ps.ms2_comparion(peakset_list)
    
    first_run_rt, incoming_rt = plot.rt_extract_convert(anchors)

    #Get the values of RT-RT from the 2 files respectively, this will be used to make the GP model

    rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
        
    #Need to make it the list into an array so it can be used in the GP
    
    X = np.array(multi2_rt).reshape(len(incoming_rt),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    kernel = GPy.kern.RBF(input_dim=1, variance= variance, lengthscale= lengthscale)
    model = GPy.models.GPRegression(X,Y, kernel = kernel)   
    
    return model

def create_optimized_gp_model(list_of_peaks_firstrun, list_of_peaks_liverun):
    
    '''
    I can recycle the code I've written in GPCorrection.py
    In its current state ive written it as a script but with a bit of work
    it can be molded into useable methods that can be easily plugged in here
    
    This method then will create the optimal GP model for correcting RT
    
    In its current state it return the best variance and LS to be used for the hyperparams
    Though I can adapt that so that it just returns the model. This model can then be used with other
    methods for correcting in real time.
    
    The variance and LS rarely change, so this function will only need to be
    utilized once, after that the only thing that'll update the model will be the anchors
    
    Because of that i dont need it to return the model, ill need it to return the var and ls figures
    '''
    
    return gpc.GP_optimization(list_of_peaks_firstrun, list_of_peaks_liverun)

def add_peak(peakset_list, peak):
     '''
     Parameters
     ----------
     peakset_list: list of peakset objects
     peak : Peak Object
     DESCRIPTION: searches for a match in a list of peaksets, if one is found 
     then it is appended to that list

     Returns
     -------
     None
     '''
     
     #Convert the peak into a list to be used in the alignment method of peakset
     
     peak = list(peak)
     
     for peakset in peakset_list:
         
         if len(peakset.peaks) <2:
             
             potential_match = peakset.peaks
             
             peakset = alignment(peak, potential_match)
             
     return peakset

#This could be set up as a recursive method?
    
def correct_rt(GP_model, real_time_run, ps_list):
    
    peak = um.peak_creator(real_time_run)
    
    #Take the RT and convert it to a vairable
    
    rt = peak.get_rt()
    
    #Convert this variable into a numpy array before passing to the model
    
    rt = np.array(rt).reshape(len(rt),1)
    
    #Get mean and variance for the current rt based on the model
    
    mean, var =  mean, var = GP_model.predict(rt, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
    
    mean = list(mean.flatten())
            
    #This method corrects the RT by adding the predictions (mean) produced by the model
    
    um.correct_rt(peak, mean)
    
    '''
    Create a method that takes a single peak as an argument and loops over an existing
    ps list and looks to find align it to an existing peak. If the peak doesnt align, then its
    added to the list as a singlet peakset. This method returns the updated ps list
    '''
    '''
    #Add peak method
    
    new_ps_list = add_peak(ps_list, peak)
    
    #if a match is found then perform alignment again
    
    if len(ps_list) != len(new_ps_list):
        
        model = create_model(new_ps_list, variance, lengthscale)
        
    '''    
    
    #After the alignment has been performed call the create_optimized_gp_model function
    
    #This line can be the recursive call to the correct_rt function
    
    #The stopping condition to the method will be when real_time_run = 0 or something similar (just an idea for now)
    
    '''
    Alternatively I can have a conditional statement that monitors the variance from .predict()
    If this number grows too large then another anchor is created. This would require me to write another function
    That acheieves this
    '''
 
#Make a main method that can be easily called and performs everything

def main(first_run_fp, first_run_mgf, live_run, live_run_mgf):

    #Make peak objects

    first_run = create_peak_objects(first_run_fp, first_run_mgf)
    
    live_peaks = create_peak_objects(live_run, live_run_mgf)
    
    #Align the peaks
    
    peaksets = alignment(first_run, live_peaks)
    
    #Find the optimal optimization parameters
    
    var, ls = create_optimized_gp_model(peaksets)
    
    #Create the model
    
    model = create_model(peaksets, var, ls)
    
    #Correct RT
    
    correct_rt(model, live_peaks, peaksets)
    
    #Return a .csv file of correct times or something along those lines



        
    
    