# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:24:53 2020

@author: Don Haughton
"""

import statistics

'''
Class bellow is a representation of a peak
The function in the useful_functions.py files is used
to create objects of this class. Throughout the program
the vast majoirt of functions are built to accept list of peak
objects or peakset objects
'''

class Peak(object):
    
    def __init__(self, key, mz, rt, intensity, file, ms2):
        
        '''
        Parameters
        ----------
        key: int
        mz: float
        rt: float
        intensity: float
        file: string
        ms2: spectrum object
        DESCRIPTION: This constructor will create peak objects- which are defined by the 6 
        arguments passed to the constrcutor
        -------
        '''
        self.id = key
        self.mz = mz
        self.rt = rt
        self.intensity = intensity
        self.file = file
        self.ms2 = ms2
    
    #Getters to be used to get specific access to the peak objects attributes
    
    def get_id(self):
        
        return self.id
    
    def get_mz(self):
        
        return self.mz
    
    def get_rt(self):
        
        return self.rt
    
    #This is the only setter required, use during the RT correction stage and ONLY used there
    
    def set_rt(self, rt):
        
        self.rt = rt
    
    def get_intensity(self):
        
        return self.intensity
    
    def get_file(self):
        
        return self.file

    def get_ms2(self):
        
        return self.ms2  

import SimilarityCalc as sc        

'''
Peaksets are generated during the alignment of peaks
during the alignmnet the peak objects are converted to peaksets
'''

class PeakSet(object):
    
    def __init__(self, peak_list):
        
        '''
        Parameters
        ----------
        peak_list: list of peak objects 
        DESCRIPTION: This constructor will create peakset objects- which are defined 
        by the arguments passed to the constructor
        -------
        '''
       
        self.mz = PeakSet.avg_mz(peak_list)
        self.rt = PeakSet.avg_rt(peak_list)
        self.intensity = PeakSet.avg_intensity(peak_list)
        self.number_of_peaks = len(peak_list)
        self.peaks = peak_list
      
    '''    
    A peakset needs to have an mz, rt..ect value same as a peak
    These are calculated by taking the average of said values that make up the
    peakset
    '''    
    def avg_mz(peak_list):
        
        #empty variable to be used to calculate the average
        
        mz_list = []
        
        #loop over the peaks in the list and extract the mz values
        
        for peak in peak_list:
            
            mz = peak.get_mz()
            
            mz_list.append(mz)
        
        #Calculate the mean from this list and return it
        
        average_mz = statistics.mean(mz_list)
        
        return average_mz
    
    def avg_rt(peak_list):
        
        #empty variable to be used to calculate the average
        
        rt_list = []
        
        #loop over the peaks in the list and extract the mz values
        
        for peak in peak_list:
            
            rt = peak.get_rt()
            
            rt_list.append(rt)
        
        #Calculate the mean from this list and return it
        
        average_rt = statistics.mean(rt_list)
        
        return average_rt
    
    def avg_intensity(peak_list):
        
        #empty variable to be used to calculate the average
        
        intensity_list = []
        
        #loop over the peaks in the list and extract the mz values
        
        for peak in peak_list:
            
            intensity = peak.get_intensity()
            
            intensity_list.append(intensity)
        
        #Calculate the mean from this list and return it
        
        average_intensity = statistics.mean(intensity_list)
        
        return average_intensity
    
    #getter for peaks as they are often accessed
    
    def get_peaks(self):
        
        return self.peaks
    
    #Align the peaks into lists of peaks that have similar mz and rt
    
    def align(peak_obj_list, another_peak_obj_list, rt_tol):
            
        '''
        Parameters
        ----------
        NOTE: Both lists should be sorted by intensity in reverse order
        peak_obj_list : List of peak objects from a file
        another_peak_obj_list : List of peak objects from another file
        rt_tol: float- RT tolerance between peaks in seconds
        Description: This method will form pseudo peaksets by matching the peaks
        between the 2 files into a list and appending said list to another list
        This list of lists can then be used to create peakset objects
        Returns
        -------
        List of peakset lists
        '''
        
        #Empty list to contain peakset lists
        
        list_of_lists = []
        
        '''
        m/z differences between peaks that originate from the same metabolite will have a
        tight difference between the 2. This means that the buffer for m/z must be tight
        or else the risk of false positives is evelvated. RT is set by the user as this
        tolerance can be more variable
        '''
    
        mz_buffer = 0.00015
        rt_buffer = rt_tol
        
        '''
        #The largest list needs to be the first in the loop or else it'll produce an error when
        calculating the mean mv, rt ect downstream at the peakset creation stage as there will be null values
        The conditionals bellow will find the largest list amongst the arguments provided
        '''
    
        if len(peak_obj_list) > len(another_peak_obj_list):
            
            largest = peak_obj_list
            smallest = another_peak_obj_list
            
        else:
            
            largest = another_peak_obj_list
            smallest = peak_obj_list
            
            
        '''
        Empty list variables to append to in the loops bellow
        '''
        
        matched_large = []
        matched_small = []
        unmatched_large = []
        unmatched_small = []
         
        '''
        loop over every peak in the first list, comparing it to every peak in the 
        second list, if they fall within an acceptable range- dictated by the upper
        and lower tolerances set by the buffers, then its used to created a new peakset list
        
        once the first peak in the first file has been comapred to all peaks in the second file
        the next peak is checked and this process continues until all peaks have been compared
        and peakset lists are created.
        
        in the list bellow, i and j both represent peaks
        '''
        
        for i in largest:
            
            #Get the mz and rt to compare to the peak in the first list
            
            mz = i.get_mz()
            rt = i.get_rt()
            
            for j in smallest:
                
                #mz tolerances
            
                upper_mz_tolerance = j.get_mz() + mz_buffer
                lower_mz_tolerance = j.get_mz() - mz_buffer
                
                #rt tolerances
                
                upper_rt_tolerance = j.get_rt() + rt_buffer
                lower_rt_tolerance = j.get_rt() - rt_buffer
                
                #boolean variables comparing the mz and rt of all peaks in smallest to the tolerances in largest
                
                mz_comp = mz >= lower_mz_tolerance and mz <= upper_mz_tolerance
                rt_comp = rt >= lower_rt_tolerance and rt <= upper_rt_tolerance
                
                #If both comp variables are true then it'll add it to the peakset list
                
                if mz_comp == True and rt_comp == True:
                    
                    matched_large.append(i)
                    matched_small.append(j)
        
        #Use the list of matched peaks to find the ones that didnt match            
        
        for i in largest:
            
            #If it isn't in the matched list then it must be unmatched
            
            if i not in matched_large:
                
                #Append it to the unmatched list
                
                unmatched_large.append(i)
        
        #Use the list of matched peaks to find the ones that didnt match                    
        
        for i in smallest:
            
            #If it isn't in the matched list then it must be unmatched
            
            if i not in matched_small:
                
                #Append it to the unmatched list
                
                unmatched_small.append(i)
    
        '''
        If the peaks match then they make up one peakset
        The argument for a peakset is a list of peaks so the matched large and matched small
        lists need to be combined together, the loop bellow will achieve this
        '''
    
        #Empty merged list variable to append to
    
        merged = []
        
        for i in range(0, len(matched_large)):
            
            #Use the indexes to append them together, ie so the peak that are matched are in the list together
            
            merged.append(matched_large[i])
            merged.append(matched_small[i])
            
            #Add this list to the list of lists- representing pseudo peaksets
            
            list_of_lists.append(merged)
            
            #Close the list so no more can be added to it until the next iteration
            
            merged = []
        
        '''    
        Similar to above, we want to add the single peak peaksets to list of lists
        so we need to then make each individual peak a list and then add it to the
        pseudo peakset list
        '''
        
        #Empty unmatched list variable to append to
        
        unmatched = []
        
        for i in unmatched_large:
            
            #Add to unmacthed, making it a list containing one peak
            
            unmatched.append(i)
            
            #Add to pseudo peak lists
            
            list_of_lists.append(unmatched)
            
             #Close the list so no more can be added to it until the next iteration
            
            unmatched = []
            
        #Same as above but for the other unmacthed list
            
        for i in unmatched_small:
            
             #Add to unmacthed, making it a list containing one peak
            
            unmatched.append(i)
            
             #Add to pseudo peak lists
            
            list_of_lists.append(unmatched)
            
            #Close the list so no more can be added to it until the next iteration
            
            unmatched = []
            
        #Return the list of lists- representing pseudo peaksets
    
        return list_of_lists
    
    def make_peaksets(list_of_pseudo_peaksets):
        '''
        Parameters
        ----------
        list_of_pseudo_peaksets : output from the align method
        DESCRIPTION: loops through the list of lists provided and creates
        peakset objects from this. Each index in the list of lists is a list itself
        containing peaks- in the case of the test data there will either be one or two peaks
        This function will take each index and convert it to a peakset object
        Returns
        -------
        List of peakset objects
        '''
  
        #Empty list variable to return at the end

        peakset_list = []

        for i in list_of_pseudo_peaksets:

            #each index in this list will be a list of peaks, this is the only argument we
            #need to make peakset objs, the peakset init method does the rest              
            
            ps = PeakSet(i)
            
            peakset_list.append(ps)
            
        return peakset_list
    
    #Find ms2 spectra in a list of peaksets and compare
    
    def ms2_comparison(peakset_list, similarity_tol):
        
        '''
        Parameters
        ----------
        peakset_list : List of Peakset objects
        similarity_tol: Float that cant be greater than 1.0
        DESCRIPTION: Loops over the list of peaks in peaksets- find peaksets that
        match and that have ms2 spectra. Once they are found a method is called to check
        the similarity score between the 2. If it is above the similarity_tol it
        is appended to a list. This list will represent peaksets that have been aligned based on their
        m/z, rt and ms2
        Returns
        -------
        ms2_comp : A seperate list containing only matching peaksets that both have
        an ms2 spectrum object with a similairty score above a certain threshold
        '''
        
        #Empty list of comparisons to be returned
        
        ms2_comp = []
        
        #Loop over peaksets
        
        for ps in peakset_list:
            
            #We're only looking to compare matched peaksets so look for peaksets having >1 peaks making up the peakset
            
            if ps.number_of_peaks > 1:
                
                #Empty list to store the spectrum objects that are an attribute of Peak objects
                
                ms2 = []
                
                #Loop over the peak list in peakset
            
                for peak in ps.get_peaks():
                    
                    #Not all peak objects have an ms2 attrbute so this checks for those that do
                    
                    if peak.get_ms2() != None:
                        
                        #If one is found add it to the ms2 list
                        
                        ms2.append(peak.ms2)
                
                '''
                Of the matched peaks, some may have an ms2 spectrum whilst the others dont, by ensuring
                that the ms list is larger than 1 and there are no null values we can check the similarity
                score of both the spectra
                '''
                
                if len(ms2) > 1 and None not in ms2:
                    
                    '''
                    The function that checks the similarity takes a list of spectrum objects
                    As its argument and returns a similarity score
                    If this score is above the treshold then the peaks match on m/z,rt and ms2-
                    Append that peakset to the list at the beginning of the function
                    '''
                    
                    spectra_similarity = sc.similarity_score(ms2)
                    
                    if spectra_similarity > similarity_tol:
                        
                        ms2_comp.append(ps)
                        
        return ms2_comp
