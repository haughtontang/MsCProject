# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:42:58 2020

@author: Don Haughton
"""

import GPy
from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import UsefulMethods as um
import SimilarityCalc as sc
import numpy as np

#Import and make peaks

multi1 = um.peak_creator('multi 1 ms2.csv')
multi2 = um.peak_creator('multi 2 ms2.csv')

um.assign_ms2("multi1_ms2.MGF", multi1)
um.assign_ms2("multi2_ms2.MGF", multi2)

all_time = []

for i in multi2:
    
    all_time.append(i.rt)

#Sort by intensity

multi1.sort(key = lambda x: x.intensity)
multi2.sort(key = lambda x: x.intensity)

#Get the most sig peaks

#multi1 = um.most_sig_peaks(multi1, 5e6)
#multi2 = um.most_sig_peaks(multi2, 5e6)

pps = ps.align(multi1, multi2,1.5)

peaksets = ps.make_peaksets(pps)

ms2_validated_peaksets = ps.ms2_comparison(peaksets, 0.9)

multi1_rt, multi2_rt = plot.rt_extract_convert(ms2_validated_peaksets)

rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)

#print(rt_minus[:20])
'''
#Try the GP but for the anchors only

import MakeAnchors as ma

a1 = ma.filter_mz(ps, 5e7)

a1 = ma.filter_rt(a1)

multi1_rt, multi2_rt = plot.rt_extract_convert(a1)

rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
'''
import numpy as np

X = multi2_rt
Y = rt_minus

#This is needed to make it an array/2d list so it can be used in the guassian

#Imports
#Create peakset objects and match them

X = np.array(multi2_rt).reshape(len(multi2_rt),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)
kernel = GPy.kern.RBF(input_dim=1, variance= 5, lengthscale= 91.56)
m = GPy.models.GPRegression(X,Y, kernel = kernel) 
m.plot()
#variables for var and LS

variance = 1
ls = 30

#Empty list to store the results

results = []


while variance <2:
    
    while ls < 80:
        
        multi1 = um.peak_creator('multi 1 ms2.csv')
        multi2 = um.peak_creator('multi 2 ms2.csv')
        um.assign_ms2("multi1_ms2.MGF", multi1)
        um.assign_ms2("multi2_ms2.MGF", multi2)
        
        all_time = []
        
        for i in multi2:
            
            all_time.append(i.rt)
        
        #Sort by intensity
        
        multi1.sort(key = lambda x: x.intensity)
        multi2.sort(key = lambda x: x.intensity)
        
        kernel = GPy.kern.RBF(input_dim=1, variance= variance, lengthscale= ls)
        m = GPy.models.GPRegression(X,Y, kernel = kernel)    

        all_time = np.array(all_time).reshape(len(all_time),1)

        mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)

        #convert from np array to list
        
        mean = list(mean.flatten())
        #Alter the RT of the peaks
        
        um.correct_rt(multi2, mean)
        
        #match PS again
        
        pseuo = ps.align(multi1, multi2, 1)
        peak_sets = ps.make_peaksets(pseuo)
        
        num_of_ps = len(peak_sets)
        
        tup = (variance, ls, num_of_ps)
        
        results.append(tup)
        
        ls = (ls/1.2) *1.5
        
    variance+=1
    
    
#sort it

results.sort(key=lambda tup: tup[2])

for i in results:
    
    print(i)


head = results[0]


    
best_var, best_ls, ps_num = head

print("var: ", best_var, "Lengthscale: ", best_ls, "PS num: " ,ps_num)


'''
k = GPy.kern.RBF(input_dim=1, variance= 1, lengthscale= 700)
m = GPy.models.GPRegression(X,Y, kernel = k)    
m.plot()
all_time = []
        
for i in multi2:
    
    all_time.append(i.rt)
    
all_time = np.array(all_time).reshape(len(all_time),1)
mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
mean = list(mean.flatten())
#Alter the RT of the peaks

um.correct_rt(multi2, mean)

#match PS again

pseuo = ps.align(multi1, multi2, 1)
peak_sets = ps.make_peaksets(pseuo)

num_of_ps = len(peak_sets)
print(num_of_ps)
'''
'''        
#Make the model

m = GPy.models.GPRegression(X,Y, kernel = kernel)

#Convert all the times in from file2 into a numpy array so itll work in the predict function

all_time = np.array(all_time).reshape(len(all_time),1)

#returns mean and variance so need two variables for that

mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)

#printed to test and it works

print(len(mean))
print(len(var))
#Ruining gp so comment out for now

#m.optimize_restarts(num_restarts=8)

#m.plot()

#print(kernel)
print(m)
'''




