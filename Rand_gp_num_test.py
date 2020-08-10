# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 12:34:15 2020

@author: Don Haughton
"""
import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc
import random

def check_correction_quality(list_of_peaksets):
    
    '''
    Parameters
    ----------
    list_of_peaksets : List of peakset objects
    
    DESCRIPTION: Loops through the list and calculate the similarity score of the
    MS2 spectra objects contained in the PS. These scores are then appended to a list
    and returned at the end. 

    Returns
    -------
    scores : List of floats
    '''
    
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

multi1 = um.peak_creator('multi 1 ms2.csv')
multi2 = um.peak_creator('multi 2 ms2.csv')

um.assign_ms2("multi1_ms2.MGF", multi1)
um.assign_ms2("multi2_ms2.MGF", multi2)

#Sort by intensity

multi1.sort(key = lambda x: x.intensity)
multi2.sort(key = lambda x: x.intensity)

#Align the peak objects 

pps = ps.align(multi1, multi2,1.5)

#Create peakset objects from this alignment

peaksets = ps.make_peaksets(pps)

original_ps = len(peaksets)

#Scan these peaksets and find those that match by their MS2 spectra

ms2_validated_peaksets = ps.ms2_comparison(peaksets, 0)

original_ms2 = len(ms2_validated_peaksets)

id_list1 = []
id_list2 = []
for i in ms2_validated_peaksets:

    for j in i.peaks:
        
        if j.file == "multi 1 ms2.csv":
            yup = j.ms2
            
            key = yup.feature_id
            
            id_list1.append(key)
            
        else:
            
            yup = j.ms2
            
            key = yup.feature_id
            
            id_list2.append(key)
   
#Extract the RT of the anchors created above

rt1, rt2 = plot.rt_extract_convert(ms2_validated_peaksets)

#Get the values of RT-RT from the 2 files respectively, this will be used to make the GP model

rt_minus = plot.rt_minus_rt_plot(rt1, rt2)
    
#Need to make it the list into an array so it can be used in the GP

X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

#get the time in peak2
            
X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)


#Make random gauss predicitons 

from random import seed
from random import gauss

# seed random number generator

#seed(1)

# generate some Gaussian values

fake_predictions = []
mu, sigma = 0, 1
for i in range(len(multi2)):
    
    values = random.gauss(mu, sigma)

    fake_predictions.append(values)

#This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model

um.correct_rt(multi2, fake_predictions)

#Align again

corrected_align = ps.align(multi1, multi2, 1.5)

corrected_peaksets = ps.make_peaksets(corrected_align)

#get the number

num_corrected = len(corrected_peaksets)

#MS2 numbers

corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)

#get ms2 num

ms2_num = len(corrected_ms2)
            
low_score_count = 0

zero_score_count = 0

#Get correction scores for all MS2 spectra aligned and find if there are any of low quality

corrected_scores = check_correction_quality(corrected_ms2)

for score in corrected_scores:
    
    if score < 0.9:
        
        low_score_count+=1
        
    if score == 0:
        
        zero_score_count+=1


        
#record the results

tup = (original_ps, original_ms2, num_corrected, ms2_num, low_score_count, zero_score_count)

print(tup)

corrected_id_list1 = []
corrected_id_list2 = []


