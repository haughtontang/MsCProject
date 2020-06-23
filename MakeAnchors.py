# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 12:51:09 2020

@author: Don Haughton
"""

'''
This file contains a list of methods
That can be applied to peaks/ peakset objects that will look
for potential anchors amongst them to perfrom RT correction
'''

import UsefulMethods as um
import statistics


def filter_mz(list_of_peak_objs, sig_val):
        
    '''
    Parameters
    ----------
    list_of_peak_objs : A list containing peaks or peaksets
    sig_val: To establish an acceptable m/z range we want to get the average m/z value from 
    Some very sig peaks, to get these you need to input what intesnity cut off you want to
    use to get the most intese peaks
    DESCRIPTION: filters through the list that is passed and removes
    Values from it that dont satisfy the criteria
    In this case that is those m/z values for peaks that are higher or lower
    Than the average of the very significant peaks with a 10% buffer either way  
    Returns
    -------
    List of peak/peakset objects that have similar m/z to the most intense peaks
    '''
    
    #Get a list of peaks that are very significant
   
    very_sig_peaks = um.most_sig_peaks(list_of_peak_objs, sig_val)
    
    #Empty list variable to be populated with them/z values for the very sig peaks in the list above
    
    mz_list = []
    
    #Get the mz values for these very sig peaks
    
    for i in very_sig_peaks:
        mz = i.get_peak().get_mz()
        mz_list.append(mz)
    
    #Calculate the avg of these m/z values and then allow a buffer of +/- 10% of that average
    
    average_mz = statistics.mean(mz_list)
    
    #These represent the upper and lower ranges of the buffers, each one being the mean + 10% of the bean and - 10% of the mean respectively
    
    comparible_up = (average_mz /100 * 10) + average_mz 
    comparible_down = average_mz - (average_mz /100 * 10) 
   
    #Go through the list passd to the function and remove any values that dont fall within the upper and lower buffers
    
    for i in list_of_peak_objs:
        
        #Looking to compare m/z which is at the second index
        
        row_to_be_checked = i.get_peak().get_mz()
        
        #If the m/z value doesnt fall between the upper and lower tolerances it is removed
        
        if row_to_be_checked > comparible_up or row_to_be_checked < comparible_down:
                
            list_of_peak_objs.remove(i)
            
    return list_of_peak_objs
            
                
def filter_rt(list_of_peak_objs):
    
    '''
    Parameters
    ----------
    list_of_peak_objs : A list containing peaks or peaksets
    DESCRIPTION: filters through the attribute list of the obejct that is passed and removes
    Values from it that dont satisfy the criteria
    In this case that is those rt values for peaks that are higher or lower
    Than the most significant peaks rt value with a 15% buffer either way
    Returns
    -------
    List of peak/peakset objects that have similar rt to the most intense peaks
    '''
    
    #Get a list of rt values from the peak list passed to the function
    
    rt_list = []
    
    #Popular rt list
    
    for i in list_of_peak_objs:
        
        rt = i.get_peak().get_rt()
        
        rt_list.append(rt)
    
    #Upper and lower values to compare the whole list against
    
    #Take the RT of the most intesne peak and allow a +/- 15% buffer
    
    comparible_up = rt_list[0] + (rt_list[0]/100 * 15)
    comparible_down = rt_list[0] - (rt_list[0]/100 * 15)

    for i in list_of_peak_objs:
        
        row_to_be_checked = i.get_peak().get_rt()
        
        #Remove peaks from the list that fall outside of this range
        
        if row_to_be_checked > comparible_up or row_to_be_checked < comparible_down:
            
                list_of_peak_objs.remove(i)
                
    return list_of_peak_objs
