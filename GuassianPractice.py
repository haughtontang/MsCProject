# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:42:58 2020

@author: Don Haughton
"""

import GPy
from PeakTools import PeakSet
from PeakTools import Plotter
import numpy as np

multi1 = PeakSet('reduced_multi_1.csv')
multi2 = PeakSet('reduced_multi_2.csv')

multi1.sort_peaks(8)
multi2.sort_peaks(8)

print(len(multi1.peaks))

multi1.cut_off(5e6, True)
multi2.cut_off(5e6, True)

print(len(multi1.peaks))
print(len(multi2.peaks))

#This method is the step where the repeated values are being generated

multi1.match_peaks(multi2)

print(len(multi1.peaks))
print(len(multi2.peaks))

multi1_rt = Plotter.rt_extract_convert(multi1)
multi2_rt = Plotter.rt_extract_convert(multi2)

rt_minus = Plotter.rt_minus_rt_plot(multi1_rt, multi2_rt)

print(rt_minus[:4])

#Try the GP but for the anchors only

from PeakTools import Anchor

anchor = Anchor('reduced_multi_1.csv')
anchor.sort_peaks(8)

#print(len(anchor.peaks))
anchor.most_sig_peaks(5e6,True)
#print("Anchors v sig", len(anchor.peaks))

anchor.filter_mz(5e7)
#print(len(anchor.peaks))

anchor.filter_rt()
#print(len(anchor.peaks))

anchor2 = Anchor('reduced_multi_2.csv')
anchor2.sort_peaks(8)

#print(len(anchor.peaks))
anchor2.most_sig_peaks(5e6,True)
#print("Anchors v sig", len(anchor.peaks))

anchor2.filter_mz(5e7)
#print(len(anchor.peaks))

anchor2.filter_rt()
#print(len(anchor.peaks))

PeakSet.make_same_size(anchor, anchor2)

anchor1_rt = Plotter.rt_extract_convert(anchor)
print(len(anchor1_rt))
anchor2_rt = Plotter.rt_extract_convert(anchor2)
print(len(anchor2_rt))
anchor_diff = Plotter.rt_minus_rt_plot(anchor2_rt, anchor1_rt)
print(len(anchor_diff))
plot = Plotter(anchor2_rt,anchor_diff,"Anchor RT Difference", "RT Multi 2", "RT Multi 1  minus RT Multi 2", False)

import numpy as np

X = anchor2_rt
Y = anchor_diff

#This is needed to make it an array/2d list so it can be used in the guassian

#Imports
#Create peakset objects and match them

X = np.array(anchor2_rt).reshape(len(anchor2_rt),1)
Y = np.array(anchor_diff).reshape(len(anchor_diff),1)

kernel = GPy.kern.RBF(input_dim=1, variance=1. , lengthscale=1.)

m = GPy.models.GPRegression(X,Y, kernel = kernel)

m.optimize_restarts(num_restarts=8)

m.plot()




