# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 09:18:29 2020

@author: Don Haughton
"""

import GPy
from peak_tools import PeakSet as ps
import useful_functions as um
import numpy as np
import part_correct as gpc
import investigative_functions as invfun
import matplotlib.pyplot as plt
'''
Take 2 paths of picked peaks as its argument and convert the information in these files into
peak objects
'''

def create_peak_objects(filepath, mgf_path):
    
    peaks = um.peak_creator(filepath)
    um.assign_ms2(mgf_path, peaks)
    
    return peaks

#dealing with list of peaks so ignore
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
'''
def incoming_peaks(real_time_run):
    
    #Should be dealing with list of peaks, will leave whats bellow commented out in case Needed later
    
    list_of_live_runs = []
    
    #Not sure of an appropriate value for this, can revist later on. 
    
    limit = 50
    
    while len(list_of_live_runs) < limit:
        
        list_of_live_runs.append(real_time_run)
        
'''
'''
The way that peak_creator is set up this wont work, maybe need to create a similar
but realted method that does the exact same thing but without the file reader

'''
#Create peaks from this list
'''
list_of_peaks = um.peak_creator(real_time_run)
  
#The file paths may also have to be arguments to this function
  
first_file = first_run_peaks(filepath, mfg_path)
  
#sort these based on intensity
  
first_file.sort(key = lambda x: x.intensity, reverse = True)
list_of_peaks.sort(key = lambda x: x.intensity, reverse = True)
  
#perform alignment
  
ps = alignment(first_file, list_of_peaks)
return ps
'''
#Seperate alignment method to clean up the incoming_peaks function and later functions
  
def alignment(first_run_peaks, incoming_peaks, RT_tol):
    
    pseudo_peaksets = ps.align(first_run_peaks, incoming_peaks, RT_tol)
    
    peaksets = ps.make_peaksets(pseudo_peaksets)
    
    return peaksets

def create_model(peakset_list, variance, lengthscale):
    
    anchors = ps.ms2_comparison(peakset_list, 0.9)
    r1,r2 = um.rt_extraction(anchors)
    minus = um.subtract_attributes(r1,r2)
    first_run_rt, incoming_rt = um.rt_extraction(anchors)
    #plt.scatter(r1, minus, c="#5E62F4", alpha=1)
    #plt.show() 
   #
    
    #print("RT numbers : ", first_run_rt,incoming_rt)
    
    #Get the values of RT-RT from the 2 files respectively, this will be used to make the GP model

    rt_minus = um.subtract_attributes(first_run_rt, incoming_rt)
    
    #print("RT minus numbers : ", rt_minus)
        
    #Need to make it the list into an array so it can be used in the GP
    
    X = np.array(incoming_rt).reshape(len(incoming_rt),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    kernel = GPy.kern.RBF(input_dim=1, variance= variance, lengthscale= lengthscale)
    model = GPy.models.GPRegression(X,Y, kernel = kernel)   
    
    return model

def create_optimized_gp_model(peaksets):
    
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
    
    return gpc.find_best_hyperparameters(peaksets)

def add_peak(first_file, peakset_list, peak, RT_tol):
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
     
     #instead of those arguments pass it the first file and then the peakset list
     
     first_file_name = ""
     
     for i in first_file:
         
         first_file_name = i.get_file()
         
         break
     
     second = []   
     
     for i in peakset_list:
         
         for j in i.get_peaks():
             
             if j.get_file() != first_file_name:
                 
                 second.append(j)
     
     if len(peak) == 1:   
     
         #Convert from list to peak
    
         peak = peak[0]
         
         second.append(peak)
         
     #else it'll be a plist of splits so add this to the second variable
     
     else:
         
         for i in peak:
             
             second.append(i)
     
     added = alignment(first_file, second, RT_tol)
     
     return added
     '''
     #Convert the peak into a list to be used in the alignment method of peakset
          
     for peakset in peakset_list:
         
         if peakset.number_of_peaks <2:
             
             potential_match = peakset.get_peaks()
             
             new_match = alignment(peak, potential_match,RT_tol)
             
             if
             
     return peakset
     '''
#This could be set up as a recursive method?
    
def correct_rt(GP_model, peak_list):
    
    rt = []
    
    for peak in peak_list:
        
        rt.append(peak.get_rt())
    
    #Convert this variable into a numpy array before passing to the model
    
    rt = np.array(rt).reshape(len(rt),1)
    
    #Get mean and variance for the current rt based on the model
    
    mean, var = GP_model.predict(rt, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
    
    mean = list(mean.flatten())
            
    #This method corrects the RT by adding the predictions (mean) produced by the model
    
    um.correct_rt(peak_list, mean)
    
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
 
#Make a main method that can be easily called and performs everything, takes file paths are arguments

# def split_list(list_of_peaks, num_splits):
    
#     length = len(list_of_peaks)
    
#     original_length = len(list_of_peaks)
    
#     index_ranges = []
    
#     counter = 0
      
#     length = length // num_splits
    
#     index_ranges.append(length)
    
#     devison = False
#     while devision != True:
        
#         if sum(index_ranges)!= original_length:
        

            
            

def real_time_correction(first_run_fp, first_run_mgf, live_run, live_run_mgf, RT_tol, peak_batch):

    #Make peak objects

    first_run = create_peak_objects(first_run_fp, first_run_mgf)
    
    live_peaks = create_peak_objects(live_run, live_run_mgf)
    
    initial = []
    
    for i in live_peaks:
        
        initial.append(i)
        
        live_peaks.remove(i)
        
        if len(initial) >= 150:
            
            break
    
    #get the length of live peaks after getting the starting peaks

    half_len = len(live_peaks)    
    
    #correct using these initial numbers
    
    peaksets = alignment(first_run, initial, RT_tol)
    
    anchors = ps.ms2_comparison(peaksets, 0.9)
    
    print("anchors: ", len(anchors))
    
    r1,r2 = um.rt_extraction(anchors)
    
    minus = um.subtract_attributes(r1,r2)
    
    #The anchors and peaksets are all fine here- something beyond this point is getting muddled nad
    #messing up the order of anchors and peaks so the numbers are all jacked
    
    print("len after initial alignment with 150 peaks ", len(peaksets))
    
    #Find the optimal optimization parameters
        
    var, ls = create_optimized_gp_model(peaksets)
    
    X = np.array(r2).reshape(len(r2),1)
    Y = np.array(minus).reshape(len(minus),1)
    
    kernel = GPy.kern.RBF(input_dim=1, variance= var, lengthscale= ls)
    model = GPy.models.GPRegression(X,Y, kernel = kernel)   
    
    #Create the model
    #plt.scatter(X, Y, c="#5E62F4", alpha=1)
    #plt.show() 
   
    #model = create_model(peaksets, var, ls)
    
    #model.plot()
    
    #Correct RT
    
    correct_rt(model, initial)
    
    corrected_peaksets = alignment(first_run, initial, RT_tol)
    
    #get anchor num
    
    anchors = ps.ms2_comparison(peaksets, 0.9)
    
    anch_num = len(anchors)
    
    print("Number of anchors: ", anch_num)
    
    #simulate RT by doing it peak by peak
    
    count = 0

    limit = peak_batch
    
    list_of_splits = []
    
    while len(live_peaks) > 0:
        print("live_peaks = ", len(live_peaks))
        split = []
        
        if len(live_peaks) < limit:
                
            limit = len(live_peaks)
        
        for i in range(0, limit):

            split.append(live_peaks[i])
            
        for i in split:
            
            live_peaks.remove(i)
            
        print("split = ", len(split))
            
        # for p in live_peaks:
            
        #     if p in split:
                
        #         live_peaks.remove(p)
                
        list_of_splits.append(split)
    '''
    for i in live_peaks:
        
        print("length of live_peak at the start: ", len(live_peaks))
        
        if len(live_peaks) < limit:
                
                limit = len(live_peaks)
                
        split = []
       
        while len(split) < limit:
            
            split.append(i)
            
        #remove split for live_peaks
        print("length of split: ", len(split))
        for p in live_peaks:
            
            if p in split:
                
                live_peaks.remove(p)
        
        print("length of live_peak at the end: ", len(live_peaks))
        
        list_of_splits.append(split)    
    '''    
    for j in list_of_splits:
        
        #convert to list
        
        count +=1
        
        #peak = []
        
        #peak.append(j)
        
        correct_rt(model, j)
        
        #add peak isnt doing anything, it resets the ps list to 1. Not working properly
        
        corrected_peaksets = add_peak(first_run, corrected_peaksets, j,RT_tol)
        
        print("len after adding peak ", len(corrected_peaksets))
        
        check_anchor = ps.ms2_comparison(corrected_peaksets, 0.9)
        
        if len(check_anchor) > len(anchors):
            
            print("New anchor found- updating model")
            
            #update the model
             
            r1,r2 = um.rt_extraction(check_anchor)
             
            minus = um.subtract_attributes(r1,r2)
            
            X = np.array(r2).reshape(len(r2),1)
            Y = np.array(minus).reshape(len(minus),1)
            
            kernel = GPy.kern.RBF(input_dim=1, variance= var, lengthscale= ls)
            model = GPy.models.GPRegression(X,Y, kernel = kernel)   
            
            #reset anch_num for next iteration
            
            anchors = check_anchor
            
        #Rejig the var and ls halfway through
        
        # if count == (len(list_of_splits) // 2):
            
        #     print("Halway point- reassigning optimal hyperparameters")
            
        #     var, ls = create_optimized_gp_model(corrected_peaksets)
            
        #     model.plot()
                
    print("len after ", peak_batch, " peak split correction ", len(corrected_peaksets))
    
    ms2_peaksets = ps.ms2_comparison(corrected_peaksets, 0)
    
    print("len after ", peak_batch, " peak split correction ", len(ms2_peaksets))
          
        
real_time_correction('multi 1 ms2.csv', "multi1_ms2.MGF",'multi 2 ms2.csv',"multi2_ms2.MGF",1.5, 500)    
    