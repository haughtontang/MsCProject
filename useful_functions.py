# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 16:58:41 2020

@author: Don Haughton
"""

import csv
from peak_tools import Peak
import similarity_calc as sc

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
    List of peak objects
    '''
    
    file = open(file_path, newline = '')

    #The reader is part of the csv library but it stores this as an object, need to do more to extract the data in the file
    
    reader = csv.reader(file)
    
    #Skips the text headers
    
    next(reader)
    
    #Empty list for storing the peak data
    
    peaks = []
    
    #Loop over all the rows in the files, sroting the relevant information in variables to append to my empty list above
    
    for row in reader:
        
        #row = [id, m/z, rt, peak height]
        
        #Now that I know the types and the data lets format it
        
        key = int(row[0])
        mz = float(row[1])
        rt = float(row[2])
        height =  float(row[3])
        
        #mzmine2 deals with RT in minutes so this will Convert RT to seconds
        
        rt = rt *60
        
        #Now that its properly formatted as the proper type, convert
        #to peak object and put it into a list
        
        peaks.append(Peak(key, mz, rt, height, file_path, None))
        
    return peaks

def assign_ms2(mgf_file_path, peak_list):
    
    '''
    Parameters
    ----------
    mgf_file_path : File path to an mgf file
    peak_list: list of peak objects
    
    DESCRIPTION: Creates spectrum objects from the MGF file, it will then loop
    through the peak object list and if the ID of the specrum object matches
    the Peak objects ID; that spectrum object is assiged as the Peaks ms2 attribute
    
    Returns
    -------
    None.

    '''

    #Create a list of spectra objects- representing an MS2 specrum
    
    spectra = sc.mgf_reader(mgf_file_path)
    
    #Match the spectra objects to peak objects by their ID- if a match is found
    #alter the ms2 attribute in peak to be equal to the spectra object
    
    for peak in peak_list:
        
        #Get the id of the peak
        
        key = peak.get_id()
        
        '''
        Loop over all ms2 spectra in the mgf file (stored in this spectra list)
        and check if there are any matches
        '''
        for ms2 in spectra:
            
            #Get the ID of the ms2 spectra
            
            ms2_id = ms2.feature_id
            
            #If the IDs match then alter the ms2 attrbiute of the peak object from none to equal the spectra object it matches
            
            if key == ms2_id:
                
                peak.set_ms2(ms2)

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
                
                intesnity = row.get_intensity()
                
                if intesnity >= value:
                    
                    #Only stores the peaks that reach the condition of intensity
                    
                    sig_peaks.append(row)
            
            #Return updated list of sig peaks    
            
            return sig_peaks
        
        #If the list given isnt a Peak obj list then it must be a Peakset, requires a slight alteration when grabbing intensity
        
        else:
            
            for ps in peak_obj_list:
                
                #store the intensity as a variable
                
                intesnity = ps.get_intensity()
                
                if intesnity >= value:
                    
                    #Only stores the peaks that reach the condition of intensity
                    
                    sig_peaks.append(ps)
            
            #Return updated list of sig peaks    
            
            return sig_peaks
        
#Function to extract the RT from the OBJECTS
     
def rt_extraction(peak_obj_list):

    '''
    Parameters
    ----------
    peak_obj_list : peak or peakset object
    DESCRIPTION: This will loop over the list attribute in the object,
    extracting the RT values into a sepearate list. Can work with peak objects,
    in which case it returns all times. If the object is a peakset it will only
    return the RTs for those peaksets that MATCH i.e are aligned
    Returns
    -------
    List of RT in seconds
    NOTE: if peakset obj list is provided the number of lists returned
    Will be the number of files that make up the peaksets
    '''

    rt_converted = []
    
    first_item = None
    
    for i in peak_obj_list:
        
        first_item = i
        
        break
    
    #Check if it is a peak or peakset obj list
    
    flag = isinstance(first_item, Peak)
    
    #if it is an instance of peak then only the get_rt method has to be called
    
    if flag:
    
        for i in peak_obj_list:
            
            #get rt as seperate variable
            
            rt_convert = i.get_rt()
            
            #Add this converted time to a list
        
            rt_converted.append(rt_convert)
        
        #return the list of conversions    
        
        return rt_converted
    
    #If it isnt a peak then it must be a peakset, needs slight alteration when grabbing rt
    
    else:
        
        #Find out the original file, to do that; loop over all the peaksets and find all the unique file names
        
        names =[]
        
        for peakset in peak_obj_list:
            
            #loop over lists in peakset
            
            for peak in peakset.get_peaks():
                
                name = peak.get_file()
                
            names.append(name)
            
        #make the names list only contain unique names
        
        names = list(set(names))
        
        names.sort()
        
        '''
        in the case of the multi beers we're working with 2 files so make 2 rt lists to append to
        these will be returned at the end once they've been populated'
        '''
        
        rt1 = []
        rt2 = []
        
        '''
        Since peaksets are dealing with lists of lists it can get complicated quite quikcly
        Instead, this for loop bellow will extract all the peak objects in peakset and
        store them as a 1D list as thats easier to manipulate
        '''
        
        #Variable to store peaksets that dont contain only a single peak
        
        matched = []
        
        #List variable for the eventual 1d list of peaks in peakset
        
        peaks = []

        #if the peakset obj has more than one peak, append it to the matched list
        
        for ps in peak_obj_list:
            
            if ps.number_of_peaks != 1:
                
                matched.append(ps)
                
        #for all the peaks in the matched list, loop over those and extract individual peaks
    
        for peakset in matched:
            
            #loop over peak list attributes that are part of those objects
            
            for peak in peakset.get_peaks():
                
                #Get the peaks in that list attribute and append it to this list
                
                peaks.append(peak)
            
        #now that we have a 1d list of peaks in peakset, get their retnetion times
        
        for peak in peaks:
            
            #Check the original file it came from and append it to a different list to maintain data integrity
            
            if peak.get_file() == names[0]:
                
                rt = peak.get_rt() 
                
                rt1.append(rt)
            
            #Same as ove but for if it came from a different file    
            
            else:
                
                rt = peak.get_rt() 
                
                rt2.append(rt)
        
        #Return 2 lists of rt in seconds        
        
        return rt1, rt2

''' 
This method takes the rt in one file and subtracts it from the rt in another
Useful for visualising differences between attributes.
'''

def subtract_attributes(attr_1, attr_2):
    '''
    Parameters
    ----------
    attr_1 : list of attribute values from a picked peak file
    attr_2 : list of attribute values from a picked peak file
    DESCRIPTION: Takes the values from the first list provided and subtracts
    them from the values in the second list provided (they're subtracted at the same index)
    Returns
    -------
    a list of floats containing the attribute differences between the 2 files

    '''
    
    #Variable to store the differences
    
    difference = []
    
    '''
    By zipping the lists together it means you only require 1 for loop to go through
    and subtract the values
    '''
    
    zip_obj = zip(attr_1, attr_2)
    
    for i, j in zip_obj:
        
        #i and j represent the first attribute values in attr 1 and 2 respectively
        
        #simply append the subtraction value to the empty list created earlier
        

        difference.append(i - j)
    
    #Return the list of differences    
    
    return difference
        
def correct_rt(peak_obj_list, list_of_corrections):
    '''
    Parameters
    ----------
    peak_obj_list : list of retention times from a picked peak file
    list_of_corrections : list of predicted RT drift from a GPR
    DESCRIPTION: Updates the RT values in the peak objeycts from peak_obj_list
    based on the corrections
    -------
    Returns
    None
    '''
    
    '''
    By zipping the lists together it means you only require 1 for loop to go through
    and subtract the values
    '''
    
    zip_obj = zip(peak_obj_list, list_of_corrections)
    
    for i, j in zip_obj:
        
        #Get the retention time of the object and ammend it using the prediction
        
        new_rt = i.get_rt() + j

        i.set_rt(new_rt)
    
def find_largest_file(peakset_list):
    
    '''
    Parameters
    ----------
    peakset_list : list of peakset objects
    DESCRIPTION: Loops through the peakset object list, exctracts the unique
    file names from where the peaks originated from and returns the
    file name of the largest and smallest file names

    Returns
    -------
    largest and smallest file name- In THAT order

    '''
    
    '''
    Find out which file amongst the peaks in peakset contains more peaks
    This will be required later when assigning ms2 spectea- as the ids of the largest spectrum
    list (corresponding to the largest picked peak file) is used to assign spectrum objects to 
    peaksets
    
    The for loop bellow will extract all files that the peaks originated from
    '''
    
    file_list = []
    
    for ps in peakset_list:
        for peak in ps.peaks:
            
            file = peak.get_file()
            file_list.append(file)
    
    file_list = list(set(file_list))
    
    #Now it will find out which file is larger
    
    #Count variables to track the number of peaks per file
    
    file_1_count = 0
    file_2_count = 0
    
    for ps in peakset_list:
        for peak in ps.peaks:
            
            file = peak.get_file
            
            if file == file_list[0]:
                
                file_1_count +=1
                
            else:
                
                file_2_count +=1
                
    #Determine which is larger and asign variable based on this
    
    if file_1_count > file_2_count:
        
        largest_file = file_list[0]
        smallest_file = file_list[1]
        
    else:
        
        largest_file = file_list[1]
        smallest_file = file_list[0]
        
    return largest_file, smallest_file
