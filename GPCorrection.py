# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 12:50:15 2020

@author: Don Haughton
"""

'''
What do I need this method to do?

We need to have a set value for the LS then incrememnt that within some limit
Thats then used to make a kernel, then a model
That model makes predictions
the predictions are used to update the peak objects
they are aligned again
#ps and ls recorded
ls incrmeented and repeat 
'''

import GPy
from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import UsefulMethods as um
import numpy as np
import SimilarityCalc as sc

def GP_optimization(filepath_to_match, filepath_to_correct, mgf_path1, mgf_path2, RT_tolerance):

    multi1 = um.peak_creator(filepath_to_match)
    multi2 = um.peak_creator(filepath_to_correct)
    
    
    um.assign_ms2(mgf_path1, multi1)
    um.assign_ms2(mgf_path2, multi2)
    
    #Sort by intensity
    
    multi1.sort(key = lambda x: x.intensity)
    multi2.sort(key = lambda x: x.intensity)
    
    pps = ps.align(multi1, multi2,1.5)
    
    peaksets = ps.make_peaksets(pps)
    
    ms2_validated_peaksets = ps.ms2_comparison(peaksets)
    
    og_score = check_correction_quality(ms2_validated_peaksets)
    
    original_score = np.mean(og_score)

    multi1_rt, multi2_rt = plot.rt_extract_convert(ms2_validated_peaksets)

    rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
        
    #This is needed to make it an array/2d list so it can be used in the guassian
    
    #Imports
    #Create peakset objects and match them
    
    X = np.array(multi2_rt).reshape(len(multi2_rt),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    #variables for var and LS
    
    variance = 1
    ls = 30
    
    #Empty list to store the results
    
    results = []
    
    all_time = []
    
    for i in multi2:
        
        all_time.append(i.rt)
        
    all_time = np.array(all_time).reshape(len(all_time),1)
    
    while ls < 10000:
        
        kernel = GPy.kern.RBF(input_dim=1, variance= variance, lengthscale= ls)
        m = GPy.models.GPRegression(X,Y, kernel = kernel)    
        
        mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
        
        #convert from np array to list
            
        mean = list(mean.flatten())
        #Alter the RT of the peaks
        
        um.correct_rt(multi2, mean)
        
        #match PS again
        
        pseuo = ps.align(multi1, multi2, RT_tolerance)
        peak_sets = ps.make_peaksets(pseuo)
        
        peak_sets = ps.ms2_comparison(peak_sets)
        
        num_of_ps = len(peak_sets)
        
        scores = check_correction_quality(peak_sets)
        
        avg_score = np.mean(scores)
        
        h_or_l = ""
        
        if avg_score > original_score:
            
            h_or_l = "Higher"
            
        else:
            
            h_or_l = "Lower"
        
        tup = (variance, ls, num_of_ps, original_score, avg_score, h_or_l)
        
        results.append(tup)
        
        #Reset the PS list to be corrected
        
        multi2 = um.peak_creator(filepath_to_correct)
        um.assign_ms2(mgf_path2, multi2)
        
        scores = []
        avg_score = 0
        
        ls = (ls/1.2) *1.5
    
    results.sort(key=lambda tup: tup[2])
    
    return results

def check_correction_quality(list_of_peaksets):
    
    scores = []
    
    for sets in list_of_peaksets:
            
        #We're only looking to compare matched peaksets so look for peaksets having >1 peaks making up the peakset
        
        if len(sets.peaks) > 1:
            
            #Empty list to store the spectrum objects that are an attribute of Peak objects
            
            ms2 = []
            
            #Loop over the peak list in peakset
        
            for peak in sets.peaks:
                
                #Not all peak objects have an ms2 attrbute so this checks for those that do
                
                if peak.ms2 != None:
                    
                    #If one is found add it to the ms2 list
                    
                    ms2.append(peak.ms2)
            
            '''
            Of the matched peaks, some may have an ms2 spectrum whilst the others dont, by ensuring
            that the ms list is larger than 1 and there are no null values we can check the similarity
            score of both the spectra
            '''
            
            if len(ms2) > 1 and None not in ms2:
                
                '''
                The function that checks the similarity takes a list of spectrum objects
                As its argument and returns a similarity score
                If this score is above the treshold then the peaks match on m/z,rt and ms2-
                Append that peakset to the list at the beginning of the function
                '''
                
                spectra_similarity = sc.similarity_score(ms2)
                
                scores.append(spectra_similarity)
                
    return scores

resu = GP_optimization('multi 1 ms2.csv','multi 2 ms2.csv', "multi1_ms2.MGF","multi2_ms2.MGF",1.5)

for i in resu:
    
    best_var, best_ls, ps_num, ogs, avgs, h_or_l = i

    print("var: ", best_var, "Lengthscale: ", best_ls, "PS num: " ,ps_num, "OG Score : ", ogs, "Avg Score: ", avgs, "New score higher or lower?: ", h_or_l)