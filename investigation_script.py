# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:19:43 2020

@author: Don Haughton
"""

import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc
import random
import matplotlib.pyplot as plt
import Investigative_Functions as ivfun

p1 = um.peak_creator('multi 1 ms2.csv')
p2 = um.peak_creator('multi 2 ms2.csv')
  
um.assign_ms2("multi1_ms2.MGF", p1) 
um.assign_ms2("multi2_ms2.MGF", p2) 

p1.sort(key = lambda x: x.intensity)
p2.sort(key = lambda x: x.intensity)

normal_align = ps.align(p1,p2,1.5)

normal_ps = ps.make_peaksets(normal_align)



print("Normal ps: ", len(normal_ps))

ms2 = ps.ms2_comparison(normal_ps, 0)
premz1, premz2 = ivfun.get_mz_plot(ms2)

print("len mz list", len(premz1))

print("Normal ms2: ", len(ms2))

rt1, rt2 = plot.rt_extract_convert(ms2)

rt_minus = plot.rt_minus_rt_plot(rt1, rt2)

X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

all_time = []

for i in p2:
    
    time = i.get_rt()
    all_time.append(time)
    
all_time = np.array(all_time).reshape(len(all_time),1)

gp_kern = GPy.kern.RBF(input_dim=1, variance= 1, lengthscale= 91.56)
gp_model = GPy.models.GPRegression(X,Y, kernel = gp_kern)    

mean, var = gp_model.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)

#convert from np array to list

mean = list(mean.flatten())

#Correct RT using the mean

um.correct_rt(p2, mean)

#Align again

corrected_align = ps.align(p1, p2, 1.5)

corrected_peaksets = ps.make_peaksets(corrected_align)



num_corrected = len(corrected_peaksets)

#MS2 numbers

corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)
postmz1, postmz2 = ivfun.get_mz_plot(corrected_ms2)
print("len mz list", len(postmz1))
#get ms2 num

ms2_num = len(corrected_ms2)

print("Corrected ps: ", len(corrected_peaksets))

print("Corrected ms2: ", len(corrected_ms2))

ivfun.numbers_added(normal_ps, corrected_peaksets)

mz_diff1 = []
mz_diff2 = []

for i in postmz1:
    
    if i not in premz1:
        
        mz_diff1.append(i)
        
for i in postmz2:
    
    if i not in premz2:
        
        mz_diff2.append(i)

print(len(mz_diff1), len(mz_diff2))
        
#diff_minus = plot.rt_minus_rt_plot(mz_diff1, mz_diff2)

#plt.scatter(mz_diff2, diff_minus, c="#5E62F4", alpha=1)
#plt.show() 

tog = ivfun.get_reomoved_ms2_peaks(normal_ps, corrected_peaksets)

ms2_tog = ps.ms2_comparison(tog, 0)

a,b = ivfun.get_mz_plot(ms2_tog)