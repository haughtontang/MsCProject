# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 17:22:27 2020

@author: Don Haughton
"""

import csv
from operator import itemgetter

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
        #row = [m/z, rt, peak height]
        
        #Now that I know the types and the data lets format it
        
        mz = float(row[0])
        rt = float(row[1])
        height =  float(row[2])
        
        #Now that its properly formatted as the proper type put it into a list
        
        peaks.append([mz, rt, height])
    
    #Use Pythons built in sorted function to sort by height, m/z and then rt
    
    sorted_peaks = sorted(peaks, key = itemgetter(2), reverse = True)
    
    return sorted_peaks

class Peak:
    
    def __init__(self, mz, rt, intesity):
        
        '''
        Parameters
        ----------
        mz: float
        rt: float
        intensity: float
        DESCRIPTION: This constructor will create peak objects- which are defined by the 3 
        arguments passed to the constrcutor
        -------
        '''
        
        self.mz = mz
        self.rt = rt
        self.intesity = intesity
    
    '''
    First argument is usually self but for the way I want to do it self cant be in the 
    argument list, not sure if thats allowed/convention, may have to have it outside of
    the class
    '''
    
    def peak_storage(list_of_peaks_from_file):
        
        '''
        Parameters
        ----------
        list_of_peaks_from_file :List of peaks from .csv files- should be a list created
        from the peak_creator function
        DESCRIPTION: Filters through the list provided and extarcts the necessary
        information needed to create peak objects
        
        Returns
        -------
        List of peak objects
        '''
        
        #EMpty variable to be returned at the end
        
        peak_obj_list = []
        
        #A loop to cycle through the list provided and use its information to create peak objects
        #A row will have 3 sets of information, m/z, rt and intesnity
        
        for row in list_of_peaks_from_file:
            
            #store m/z
            
            mz = row[0]
            
            #store rt
            
            rt = row[1]
            
            #store height
            
            height = row[2]
            
            #Create a new peak object
            
            new_peak = Peak(mz, rt, height)
            
            #Add that peak object into the list
            
            peak_obj_list.append(new_peak)
            
        return peak_obj_list
    
    #Getters to be used to get specific access to the peak objects attributes
    
    def get_mz(self):
        
        return self.mz
    
    def get_rt(self):
        
        return self.mz
    
    def get_intensity(self):
        
        return self.intesity
            
       
class PeakSet(Peak):
    
    def __init__(self, mz, rt, height,matched):
        
        '''
        Parameters
        ----------
        mz: float
        rt: float
        intensity: float
        matched: boolean
        DESCRIPTION: This constructor will create peak objects- which are defined by the 3 
        arguments passed to the constrcutor
        -------
        '''
        
        super().__init__(mz, rt, height)
        self.mz = mz
        self.rt = rt
        self.height = height
        self.matched = matched
        
    def get_mz(self):
        
        return self.mz
        
    def get_rt(self):
        
        return self.rt
        
    def get_height(self):
        
        return self.height
        
    def is_matched(self):
        
        return self.matched
        
    def peakset_storage(list_of_peaksets):
        
        super().peak_storage(list_of_peaksets)
    
        
    #Found problem so can remove these methods
    
    '''
    This is far from ideal but having to have this method to filter through and remove
    repeated values in a list as the match_peaks method bellow keeps producing duplicates
    I cant figure out why this is, so this method will remove any repeated values
    
    May also be a good idea to have a method returning a boolean to say if there are any lists with
    repeated values in them
    '''
    
    def remove_repeate(peak_list):
        
        '''
        Parameters
        ----------
        Self : peakset object
        DESCRIPTION: This function alters the list atribute of the object that is
        passed to it. It filters through the list and removes repeated values,
        Leaving only unique values in the list
        '''
        #Empty list to store those that are not repeats
        
        unique_values = [] 
        
        #The not in part of the nested for loop ensures that we only get unique values in the list
        
        for i in peak_list: 
            if i not in unique_values: 
                unique_values.append(i)
        
        #Reassign the value of the list attribute to the list produced in the function        
        
        return unique_values
        
    '''
    If an intensity cut off is provdied for the peak lists it can produce differing
    numbers between the matched peaks
    
    So I'm gonna have to write a new function bellow to make the 2 the same size
    '''
    
    def make_same_size(peak_list,another_peak_list):
        
        '''
        Parameters
        ----------
        Self : peakset object
        another_peak_set_obj: a second peakset object
        DESCRIPTION: The matching function isn't perfect, as a result it can sometimes produce 
        peak lists that are of different lengths between the 2 lists. This function will reduce the size of
        the larger list to match the size of the samller one
        '''
        
        #This method is called in another method regardless, so this conditional will 
        #Only activate if the resultant peakset lists are a different lenth
        
        if len(peak_list) != len(another_peak_list):
            
            #First conditional matches the length to the second peak object if its the samller one
            
            if len(peak_list) > len(another_peak_list):
                
                #Variable to store the length of the list, this will be the desired size we want
                
                value = len(another_peak_list)
                
                #Empty list variable to append
                
                same_size = []
                
                for i in peak_list:
                
                    same_size.append(i)
                
                    #When the list is the same length as the smaller list, break out of the loop
                
                    if len(same_size) == value:
                        break
                    
                #Make the peakset list attribute equal to the new variable
                #so they will be the same size as the other objects list attribute    
                    
                return same_size
             
            #The steps in the else condition bellow are exactly the same as above but for if the 
            #the other peak objects list attribute is larger
             
            else:
                
                value = len(peak_list)
                
                same_size = []
                
                for i in another_peak_list:
                
                    same_size.append(i)
                
                    if len(same_size) == value:
                        break
                    
                return same_size
    
    #I think this method is broken in the sense that when matching peaks, it is
    #Including the same peak multiple times, need to debug
    #Comment made on 18/06

    def find_peaksets(peakset_list,another_peakset_list, return_unmatched):
        '''
        Parameters
        ----------
        peakset_list : list of peaks from a file
        peak_set_obj2 : list of peaks from a different file
        return_unmatched: Boolean, if true the unmatched peaksets will also be returned
        DESCRIPTION: This function loops through both peak lists attributes 
        and finds peaks that are the same on the basis of their m/z.
        Returns
        -------
        2 lists of matched peakset objects, one per file provided.
        
        If return_unmatched is True 3 lists will be returned, matched from first
        list in the argument, matched from second list in argument and unique peakset
        objects from both files respectively. 
        '''
        
        '''
        How are we defining that the peaks in the 2 files are the same?
        On average the m/z of the same peak in 2 filles differs by ~0.000143
        For RT the average difference (minutes) is 0.04
        '''
        
        #Buffer value for the mz
        
        buffer = 0.00015
        
        #A place to store the matched peakset object in both the files
        
        matched_first = []
        matched_second = []
        
        #Storing information to check for unique peaks
        
        unmatched_comp_first = []
        unmatched_comp_second = []
        
        #Store unique peaksets
        
        unique = []
        
        '''
        A nested for loop to goes through and check all values in the peak list 
        Comparing it to that of the other list. Since we want m/z to be very similar check this first,
        Then for whatever is left check the RT to filter further
        ''' 
        
        for i in peakset_list:
            for j in another_peakset_list:
                
                #The m/z value is stored at the 0th index in the files
                
                upper_diff = j[0] + buffer
                lower_diff = j[0] - buffer
                
                #If they fall within this range then its a match, append them to the lists
                
                if i[0] <= upper_diff and i[0] >= lower_diff:
                    
                    '''
                    Make Peakset objects, since they match the boolean will be True
                    mz is at the 0th index, rt the 1st and height is at the 2nd
                    '''
                    
                    new_peakset = PeakSet(i[0], i[1], i[2], True)
                    new_peakset2 = PeakSet(j[0], j[1], j[2], True)
                    
                    #Store these objects in lists to be returned at the end
                    
                    matched_first.append(new_peakset)
                    matched_second.append(new_peakset2)
                    
                    #Store the information from the peak file so they can be compared to find unmatched peaksets
                    
                    unmatched_comp_first.append(i)
                    
                    unmatched_comp_second.append(j)
        
        #If the boolean is false dont calculate unqiue peaks
                    
        if return_unmatched == False:            
        
            return matched_first, matched_second
        
        #If it is True then calculate unique peaksets
        
        else:
            
            '''
            The unqie peaksets are calculated by looping over the lists that contain information
            from the file that correspond to matched peak sets i.e their m/z, rt and height
            These are not objects yet though 
            
            So these loops simply check to see if i (which represents a peak in the .csv file)
            is not in the list that corresponds to peaks that match- if it isn't the information
            from i is used to create new peakset objects, these objects are then placed into
            a list
            '''
            
            #This little section of code definietly works as it should,
            #This means that the odd numbers must defineitly be coming from
            #Repeated values in the unmatched_comp lists
            
            for i in peakset_list:
                
                if i not in unmatched_comp_first:
                    
                    #Create peakset object
                    
                    unique_peakset1 = PeakSet(i[0],i[1],i[2], False)
                    
                    #Place peakset object into a list
                    
                    unique.append(unique_peakset1)
            
            #Process is repeated but for the secon file provided and its matched peaks        
            
            print("length of unique after the first file is", len(unique))
            
            for j in another_peakset_list:
                 
                
                if j not in unmatched_comp_second:
                    
                    #Create peakset object
                                    
                    unique_peakset2 = PeakSet(j[0],j[1],j[2], False)
                    
                    #Place peakset object into the unique list
                                        
                    unique.append(unique_peakset2)      
            
            #Return all 3 lists        
            print("length of unique after the first and second  file is", len(unique))
            return matched_first, matched_second, unique
     
        
    '''                
    I dont know if this step is entirely necessary to be honest, may not be worth fixing
    Though I have figured out that the primary probelm is in the buffer value, its way too high
    So thats why the number of peaks is too high, need a better way to compare them
    '''
    
    def match_peaks_rt_step(self, another_peak_set_obj):
        '''
        Parameters
        ----------
        peak_set_obj1 : Peak list after going through the m/z matching step
        peak_set_obj2 : Peak list after going through the m/z matching step
        DESCRIPTION: Does the same as the match_peaks function excpet this one will filter by RT and not m/z
        THis is seen as an extra step to double check we have the same peaks
        Returns
        List of matched peaks after being filtered for RT
        '''
    
        #Buffer value for the RT
        
        buffer = 0.04
        
        #A place to store the matched peaks in both the files
        
        matched_first = []
        matched_second = []
        
        for i in self.peaks:
            for j in another_peak_set_obj.peaks:
                
                #RT is at the third index in the file
                
                upper_diff = j[2] + buffer
                lower_diff = j[2] - buffer
                
                if i[2] <= upper_diff and i[2] >= lower_diff:
                    
                    matched_first.append(i)
                    matched_second.append(j)
                    
        #Update the objects lists to reflect what is matched
        
        self.peaks = matched_first
        another_peak_set_obj.peaks = matched_second  
        
        
#Test the above transformed classes before transferring to proper File to store peak classes 
        
 
file = peak_creator("reduced_multi_1_full.csv")

file2 = peak_creator("reduced_multi_2_full.csv")

print("Peaks from multi 1", len(file))
print("Peaks from multi 2", len(file2))

matched1, matched2, unique = PeakSet.find_peaksets(file, file2, True)  

print("Peaks from macthed 1", len(matched1))
print("Peaks from macthed 2", len(matched2))  
print("Peaks from unique", len(unique))  

import UsefulMethods

sig1 = UsefulMethods.most_sig_peaks(matched1, 5e6)
sig2 = UsefulMethods.most_sig_peaks(matched2, 5e6)

print("Peaks from sig1", len(sig1))
print("Peaks from sig2", len(sig2)) 

#For some reason its saying peakset doesnt have attribute height, even though it does, so it wont sort
#RT and mz work though so thats good

sig1 = UsefulMethods.sort_peaks(sig1, "mz", False)

for i in sig1[:6]:
    
    print(i.get_mz())
#print("There are repeated values in the macthed list 1", UsefulMethods.find_repeats(matched1))
#print("There are repeated values in the macthed list 2", UsefulMethods.find_repeats(matched2))



'''
End of work note (18/06)

classes seem to be all working fine, just need to srot the issue of why there are repeats
in the matching peaks class, almost certain its something to do with the biffer value
and getting more than intended in there

tested the methods in Useful methods file and all working as expected as well

need to contine on to try and see if the plotter will owrk with these new classes
and then from there transform that anchor class into a set of methods
'''

