# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 16:58:41 2020

@author: Don Haughton
"""

import csv
from PeakTools import Peak

def peak_creator (file_path):
    
    '''
    Parameters
    ----------
    file_path: a path to a .csv file of picked peaks
    DESCRIPTION:
    This function will use the file path provided to open the file
    Convert the types to the appropriate type
    From there is will then sort the newly created list from the file
    This list will be sorted by peak height i.e. intensity
    Returns
    -------
    List of peaks from file
    '''
    file = open(file_path, newline = '')

    #The reader is part of the csv library but it stores this as an obkect, need to do more to extract the data in the file
    
    reader = csv.reader(file)
    
    #Skips the text headers
    
    next(reader)
    
    #Empty list for storing the peak data
    
    peaks = []
    
    #Loop over all the rows in the files, sroting the relevant information in variables to append to my empty list above
    
    for row in reader:
        #row = [id, m/z, rt, row number, peak status, rt start, rt end, rt duration, peak height, peak area, data points]
        
        #Now that I know the types and the data lets format it
        
        key = int(row[0])
        mz = float(row[1])
        rt = float(row[2])
        height =  float(row[3])
        
        #Now that its properly formatted as the proper type put it into a list
        
        peaks.append(Peak(key, mz, rt, height, file_path))
        
    return peaks


def most_sig_peaks(peak_obj_list, value):
        
        '''
        Parameters
        ----------
        peak_obj_list: list of peak objects
        value: int/double- the cut off intensity value
        DESCRIPTION: The function will loop through the provided peak list and remove any peaks that are 
        bellow the intensity value that is provided in the argument. 
        -------
        '''
        
        #New variable to be returned at the end
        
        sig_peaks = []
        
        #variable for checking the instance of the argument
        
        flag = isinstance(peak_obj_list[0], Peak)
        
        #Check if the given list is a Peak or peakset object list
        
        if flag:
        
            for row in peak_obj_list:
                
                #intensity(height) is at the 8th index
                
                intesnity = row.get_intensity()
                
                if intesnity >= value:
                    
                    #Only stores the peaks that reach the condition of intensity
                    
                    sig_peaks.append(row)
            
            #Return updated list of sig peaks    
            
            return sig_peaks
        
        #If the list given isnt a Peak obk list then it must be a Peakset, requires a slight alteration when grabbing intensity
        
        else:
            
            for ps in peak_obj_list:
                
                #store the intensity as a variable
                
                intesnity = ps.intensity
                
                if intesnity >= value:
                    
                    #Only stores the peaks that reach the condition of intensity
                    
                    sig_peaks.append(ps)
            
            #Return updated list of sig peaks    
            
            return sig_peaks
