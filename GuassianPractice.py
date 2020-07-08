# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:42:58 2020

@author: Don Haughton
"""

import GPy
from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import UsefulMethods as um
import similarity_calc as sc
import numpy as np

#Import and make peaks

multi1 = um.peak_creator('multi 1 ms2.csv')
multi2 = um.peak_creator('multi 2 ms2.csv')

spectra_matches = sc.main("multi1_ms2.MGF","multi2_ms2.MGF")

#Sort by intensity

multi1.sort(key = lambda x: x.intensity)
multi2.sort(key = lambda x: x.intensity)

#Get the most sig peaks

#multi1 = um.most_sig_peaks(multi1, 5e6)
#multi2 = um.most_sig_peaks(multi2, 5e6)

pps = ps.align(multi1, multi2)

peaksets = ps.make_peaksets(pps)

ps_with_ms2 = ps.assign_ms2(peaksets, spectra_matches)

ms2_validated_peaksets = ps.ms2_matching(ps_with_ms2)

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

X = multi1_rt
Y = rt_minus

#This is needed to make it an array/2d list so it can be used in the guassian

#Imports
#Create peakset objects and match them

X = np.array(multi1_rt).reshape(len(multi1_rt),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

#Increase the lengthscale to improve the gp so it can learn something

#100 is probably a bit too high but it does give a much nice shape- will investigate later

kernel = GPy.kern.RBF(input_dim=1, variance=1. , lengthscale=30.)

m = GPy.models.GPRegression(X,Y, kernel = kernel)

#Ruining gp so comment out for now

#m.optimize_restarts(num_restarts=8)

m.plot()




