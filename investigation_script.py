
#Imports

import GPy
from peak_tools import PeakSet as ps
import useful_functions as um
import numpy as np
import investigative_functions as ivfun

#Set up peak objects

p1 = um.peak_creator('multi 1 ms2.csv')
p2 = um.peak_creator('multi 2 ms2.csv')
  
um.assign_ms2("multi1_ms2.MGF", p1) 
um.assign_ms2("multi2_ms2.MGF", p2) 

#Align pre correction

normal_align = ps.align(p1,p2,1.5)

#make peakset objects and show the number

normal_ps = ps.make_peaksets(normal_align)

print("Normal ps: ", len(normal_ps))

#Get the number of MS2 peaksets

ms2 = ps.ms2_comparison(normal_ps, 0)

#Plot the difference of mz for all matched ps and ms2 ps respectively

#ivfun.get_mz_plot(normal_ps)
#ivfun.get_mz_plot(ms2)

#print how many MS2 peaksets are present

print("Normal ms2: ", len(ms2))

#Get anchors from the peaksets

anchors = ps.ms2_comparison(normal_ps, 0.9)

#Get 2 lists of the retention times of the matched MS2 anchors

rt1, rt2 = um.rt_extraction(anchors)

#Get the times of rt1 minus rt2

rt_minus = um.subtract_attributes(rt1, rt2)

#Make numpy arrays of the retention time that'll feed the 

X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

#Extract all the retention times of the peaks in file 2 to be used in the correction

all_time = um.rt_extraction(p2)
    
all_time = np.array(all_time).reshape(len(all_time),1)

#Set up the kernel and model, the optimal var and ls figure are already known for this data from the optimization function

gp_kern = GPy.kern.RBF(input_dim=1, variance= 1, lengthscale= 91.56)
gp_model = GPy.models.GPRegression(X,Y, kernel = gp_kern)    

#Get the predicted RT drift

mean, var = gp_model.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)

#convert from np array to list

mean = list(mean.flatten())

#Correct RT using the mean

um.correct_rt(p2, mean)

#Align again with corrected times

corrected_align = ps.align(p1, p2, 1.5)

corrected_peaksets = ps.make_peaksets(corrected_align)

#Get the number corrected

num_corrected = len(corrected_peaksets)

#MS2 numbers

corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)
ms2_num = len(corrected_ms2)

#Plot the m/z difference of the corrected and corrected ms2 peaksets respectively

#ivfun.get_mz_plot(corrected_peaksets)
#ivfun.get_mz_plot(corrected_ms2)

print("Corrected ps: ", len(corrected_peaksets))

print("Corrected ms2: ", len(corrected_ms2))

#This function will print a series of statements stating the number of PS lost in the original alignment
#and the numbers gained after the RT correction

#ivfun.numbers_added(normal_ps, corrected_peaksets)

'''
The function bellow will look for ms2 peaksets that were removed during the
correction and reassess them to determine if they can be re-added as matching
peaksets
'''
recovered = ivfun.get_reomoved_ms2_peaks(normal_ps, corrected_peaksets)

#Extracts the ms2 peaksets from the recovered list

ms2_tog = ps.ms2_comparison(recovered, 0)

#Plots the difference between these

#ivfun.get_mz_plot(ms2_tog)