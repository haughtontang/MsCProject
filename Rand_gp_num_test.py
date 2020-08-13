# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 12:34:15 2020

@author: Don Haughton
"""
from peak_tools import PeakSet as ps
import useful_functions as um
import numpy as np
import optimization

'''
Bellow is a script that sets up peak objects, aligns them and check the the number
of peaksets. After that the preditions of RT drift are made using a random GP number
generator. This is done to determine if the increased number of peaksets that are seen
at the end of a normal correction run are a feature of this particulary dataset or
happen regardless. 
'''

#Set up peak objects

multi1 = um.peak_creator('multi 1 ms2.csv')
multi2 = um.peak_creator('multi 2 ms2.csv')

#Assign ms2 spectra

um.assign_ms2("multi1_ms2.MGF", multi1)
um.assign_ms2("multi2_ms2.MGF", multi2)

#Align the peak objects 

pps = ps.align(multi1, multi2,1.5)

#Create peakset objects from this alignment

peaksets = ps.make_peaksets(pps)

#record how many PS are generated

original_ps = len(peaksets)

#Scan these peaksets and find those that match by their MS2 spectra

anchors = ps.ms2_comparison(peaksets, 0.9)

original_ms2 = len(anchors)

#Extract the RT of the anchors created above

rt1, rt2 = um.rt_extraction(anchors)

#Get the values of RT-RT from the 2 files respectively, this will be used to make the GP model

rt_minus = um.subtract_attributes(rt1, rt2)
    
#Need to make it the list into an numpy array so it can be used in the GP

X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

#Make random gauss predicitons 

from random import gauss

# generate some Gaussian values

fake_predictions = []

mu, sigma = 0, 1

for i in range(len(multi2)):
    
    #Get the values
    
    values = gauss(mu, sigma)

    #Append the values in a list

    fake_predictions.append(values)

#This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model

um.correct_rt(multi2, fake_predictions)

#Align again after correcting RT using the fake predictions

corrected_align = ps.align(multi1, multi2, 1.5)

corrected_peaksets = ps.make_peaksets(corrected_align)

#get the number

num_corrected = len(corrected_peaksets)

#MS2 numbers post correction

corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)

#get ms2 num

ms2_num = len(corrected_ms2)
  
#Counters to check the correction quality after the fake corrections
          
low_score_count = 0

zero_score_count = 0

#Get correction scores for all MS2 spectra aligned and find if there are any of low quality

corrected_scores = optimization.check_correction_quality(corrected_ms2)

#Update the counters depending on the score of the ms2 spectra after correction

for score in corrected_scores:
    
    if score < 0.9:
        
        low_score_count+=1
        
    if score == 0:
        
        zero_score_count+=1
        
#record the results in a tuple to compare before and after correction

tup = (original_ps, original_ms2, num_corrected, ms2_num, low_score_count, zero_score_count)

#Print the results to observe

print(tup)
