# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 12:20:18 2020

@author: Don Haughton
"""
import GPy
from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import UsefulMethods as um
import numpy as np

#Method for creating numpy arrays that are needed for the model

def create_params(peak_file1, peak_file2, ms2_validation, mgf_path1, mgf_path2):
    '''
    Parameters
    ----------
    peak_file1 : file path for a picked peak file
    peak_file2 : file path for a picked peak file
    ms2_validation: boolean- select True if matched peaksets require MS2 validation
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
    
    #Assign ms2 spectra if user requires it
    
    if ms2_validation == True:
    
        um.assign_ms2(mgf_path1, multi1)
        um.assign_ms2(mgf_path2, multi2)
    
    #Sort by intensity
    
    multi1.sort(key = lambda x: x.intensity)
    multi2.sort(key = lambda x: x.intensity)
    
    #multi1 = um.most_sig_peaks(multi1, 5e6)
    #multi2 = um.most_sig_peaks(multi2, 5e6)
    
    #For the model we want high quality matching peaksets so the RT threshold is
    #Set to only 1.5 seconds
    
    pps = ps.align(multi1, multi2,1.5)
    
    #Create a list of peakset objects
    
    peaksets = ps.make_peaksets(pps)
    
    #we want high quality peaksets so we want to validate them by their MS2 spectra
    #Only if the user requires it
    
    if ms2_validation == True:
    
        ms2_validated_peaksets = ps.ms2_comparison(peaksets)
    
        #Extract the RT from the Matched peaksets that are validated by m/z, rt and MS2
        
        multi1_rt, multi2_rt = plot.rt_extract_convert(ms2_validated_peaksets)
        
        #Creates the RT minus list that is needed to build the model
        
        rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
        
    else:
        
        #Extract the RT from the Matched peaksets that are validated by m/z, rt and MS2
        
        multi1_rt, multi2_rt = plot.rt_extract_convert(peaksets)
        
        #Creates the RT minus list that is needed to build the model
        
        rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
    
    #The model requires numpy arrays for its argument, numpy is used here to convert the list of RTs to arrays
    
    X = np.array(multi2_rt).reshape(len(multi2_rt),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    return X, Y

def make_kernel(v, ls):
    '''
    Parameters
    ----------
    variance : Float
    ls : Float
    DESCRIPTION: Makes a kernel object
    Returns
    -------
    GPy RBF kernel object

    '''
    
    return GPy.kern.RBF(input_dim=1, variance= v, lengthscale= ls)

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

def correct_rt(X, Y, filepath_to_match, filepath_to_correct, RT_tolerance):
    
    '''
    Parameters
    ----------
    X: numpy array of input Retention times
    Y: numpy array of rt -rt times
    file_to_correct : file path of picked peaks to correct
    file_to_match: file path of picked peaks to match with corrected file
    RT_tolerance : float (seconds)- the tolerance of RT when matching peaks between file
    DESCRIPTION: This method will find the optimum paramaters of the kernel to be
    used in the GP model, the optimum kernel will produce the lowest number of peaksets-
    which should result in more matched peaksets.
    Returns
    -------
    List of corrected Peaksets
    '''
    
    #list ariable to keep track of optimal paramters
    
    results = []
    
    #Variables to be incremented in the loop
    
    variance = 1
    ls = 10
    
    while variance <10:
    
        while ls < 150:
        
            file_to_match = um.peak_creator(filepath_to_match)
            file_to_correct = um.peak_creator(filepath_to_correct)
            
            #Sort by intensity
            
            file_to_match.sort(key = lambda x: x.intensity)
            file_to_correct.sort(key = lambda x: x.intensity)
            
            #List of times from the file to corrected, needed as an input for the GP predict
            
            all_time = []
            
            for i in file_to_correct:
                
                all_time.append(i.get_rt())
                
            #Convert all time list into a numpy array- type needed for the predict method
                
            all_time = np.array(all_time).reshape(len(all_time),1)    
            
            #Make a kernel and model    
            
            kernel = make_kernel(variance, ls)
            m = make_model(X, Y, kernel)
    
            #The predict method returns 2 arrays of mean and variance, so these 2 variables are needed        
    
            mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
    
            #convert from np array to list- needs to be done so that when adding the predicted shifts to the existing
            #times there isnt a disparity in types
            
            mean = list(mean.flatten())
            
            #Alter the RT of the peaks- this method adds the 2 together
            
            mean = um.correct_rt(file_to_correct, mean)
            
            #match PS again
            
            pseuo = ps.align(file_to_match, file_to_correct, RT_tolerance)
            peak_sets = ps.make_peaksets(pseuo)
            
            #Get the length of the peakset list- lower is better as that means we have more matches
            
            num_of_ps = len(peak_sets)
            
            '''
            Create a tuple to store the length of the peaksets along with
            the value of the varaince and lengthscale variables, that created the
            kernel- that created the model- that made the predictions for the
            corrected RT. Place this in a results list to obtain the optimum params
            '''
            
            tup = (variance, ls, num_of_ps, peak_sets)
            
            results.append(tup)
            
            #Increase lengthscale up until a limit
            
            ls += 2
        
        #Increment the varaince
        
        variance+=1
    
    '''
    sort the list in ascending order of length of peaksets
    The peakset with the lowest length has the best params for correcting RT
    as this indicates there have been more matches
    '''
    results.sort(key=lambda tup: tup[2])
    
    most_optimum = results[0]
    
    #Get each value as its own variable
    
    best_var, best_ls, ps_num, best_ps = most_optimum
    
    #return these variables
    
    return best_var, best_ls, best_ps


def main(filepath_to_match, filepath_to_correct, ms2_validation, mgf_path1, mgf_path2, RT_tolerance):

    X, Y = create_params(filepath_to_match, filepath_to_correct, ms2_validation, mgf_path1, mgf_path2)
    
    #k = make_kernel(50,150)
    
    #m = make_model(X,Y, k)
    
    #m.plot()

    best_var, best_ls, best_ps = correct_rt(X, Y, filepath_to_match, filepath_to_correct, RT_tolerance)    
    
    return best_var, best_ls, best_ps

x,y,z = main('multi 1 ms2.csv','multi 2 ms2.csv',True, "multi1_ms2.MGF","multi2_ms2.MGF",20)

print("var: ", x, "lengthscale: ", y, "peaksets: ", len(z))