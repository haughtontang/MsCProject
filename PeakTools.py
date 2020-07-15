# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:24:53 2020

@author: Don Haughton
"""

import statistics

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
        DESCRIPTION: This constructor will create peak objects- which are defined by the 3 
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
    
    def set_rt(self, rt):
        
        self.rt = rt
    
    def get_intensity(self):
        
        return self.intensity
    
    def get_file(self):
        
        return self.file

    def get_ms2(self):
        
        return self.ms2  


import UsefulMethods as um
import SimilarityCalc as sc        

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
    These are calculated by taking the average ofsaid values that make up the
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
    
    #Align the peaks into lists of peaks that have similar mz and rt
    
    def align(peak_obj_list, another_peak_obj_list, rt_tol):
            
        '''
        Parameters
        ----------
        NOTE: Both lists should be sorted by intensity in reverse order
        peak_obj_list : List of peak objects from a file
        another_peak_obj_list : List of peak objects from another file
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
        These 2 buffer variables constitiue the avg differences between mz and
        rt respectively, these were caluclated by taking the mean of the top 10
        most intense peaks in the file
        '''
    
        mz_buffer = 0.00015
        rt_buffer = rt_tol #0.025
        
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
        peakset objects from this
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
    
    def ms2_comparison(peakset_list):
        
        '''
        Parameters
        ----------
        peakset_list : List of Peakset objects
        DESCRIPTION: Loops over the list of peaks in peaksets- find peaksets that
        match and that have ms2 spectra. Once they are found a method is called to check
        the similarity score between the 2. If it is above a certain score threshold it
        is appended to a list. This list will represent peaksets that have been aligned based on their
        m/z, rt and ms2
        Returns
        -------
        ms2_comp : A List of aligned peaksets
        '''
        
        #Empty list of comparisons to be returned
        
        ms2_comp = []
        
        #Loop over peaksets
        
        for ps in peakset_list:
            
            #We're only looking to compare matched peaksets so look for peaksets having >1 peaks making up the peakset
            
            if len(ps.peaks) > 1:
                
                #Empty list to store the spectrum objects that are an attribute of Peak objects
                
                ms2 = []
                
                #Loop over the peak list in peakset
            
                for peak in ps.peaks:
                    
                    #Not all peak objects have an ms2 attrbute so this checks for those that do
                    
                    if peak.ms2 != None:
                        
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
                    
                    if spectra_similarity > 0.9:
                        
                        ms2_comp.append(ps)
                        
        return ms2_comp
   
          
import matplotlib.pyplot as plt

class Plotter(object):
    
    def __init__(self, x, y, title, xtitle, ytitle, show_lobf):
        
        '''
        Parameters
        ----------
        x : list of values to be plotted
        y : list of values to be plotted
        title: title for the plot
        xtitle: x-axis title
        ytitle: y-axis title
        show_lobf: boolean: if true a line of best fit will be plotted with the plot
        DESCRIPTION: uses the 2 variables to produce a scatter plot
        Returns
        -------
        Scatter plot
        '''
        #Variables for plot

        colors = [[0,0,0]]
        
        #Get line of best fit
        
        self.a,self.b = 0.0, 0.0
    
        # Plot
        
        plt.scatter(x, y, c=colors, alpha=1)
        
        #Calls the best_fit function to plot the line of best fit if true
        
        if show_lobf == True:
        
            yfit = [self.a + self.b * xi for xi in x]
            plt.plot(x, yfit)
        
        #Assigning the arguments to the plot    
        
        plt.title(title)
        plt.xlabel(xtitle)
        plt.ylabel(ytitle)
        plt.show()
        
        
    def best_fit(self,x, y):
        '''
        Parameters
        ----------
        X : list
        Y : a different list
        DESCRIPION: takes 2 list variables that are passed in the arguments
        and calculates the paramaters necessary to plot the line of best fit
        Returns
        -------
        The mx and c values that would be in the 
        y= mx+c equation (straight line equation)
        '''
    
        xbar = sum(x)/len(x)
        ybar = sum(y)/len(y)
        n = len(x) # or len(y)
    
        numer = sum([xi*yi for xi,yi in zip(x, y)]) - n * xbar * ybar
        denum = sum([xi**2 for xi in x]) - n * xbar**2
    
        b = numer / denum
        a = ybar - b * xbar
    
        print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))
        
        self.a = a
        self.b = b
        
    #Function to extract the RT from the OBJECTS and convert them into seconds
     
    def rt_extract_convert(peak_obj_list):
    
        '''
        Parameters
        ----------
        peak_obj_list : peak or peakset object
        DESCRIPTION: This will loop over the list attribute in the object,
        extracting the RT values into a sepearate list
        These will be converted to seconds (as mzMINE represent RT in minutes) 
        prior to being placed into the new list.
        Returns
        -------
        List of RT in seconds
        NOTE: if peakset obj list is provided the number of lists returned
        Will be the number of files that make up the peaksets
        '''
        #Convert these values into seconds since they're currently in minutes
        
        rt_converted = []
        
        #Check if it is a peak or peakset obj list
        
        flag = isinstance(peak_obj_list[0], Peak)
        
        #if it is an instance of peak then only the get_rt method has to be called
        
        if flag:
        
            for i in peak_obj_list:
                
                #converting from minutes to seconds so multiply by 60
                
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
                
                for peak in peakset.peaks:
                    
                    name = peak.get_file()
                    
                names.append(name)
                
            #make the names list only contain unique names
            
            names = list(set(names))
            
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
                
                for peak in peakset.peaks:
                    
                    #Get the peaks in that list attribute and append it to this list
                    
                    peaks.append(peak)
                
            #now that we have a 1d list of peaks in peakset, convert them into seconds
            
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
    Needed for plotting the guassian     
    This method takes the rt in one file and subtracts it from the rt in another
    '''
    
    def rt_minus_rt_plot(rt_list_1, rt_list_2):
        '''
        Parameters
        ----------
        rt_list_1 : list of retention times from a picked peak file
        rt_list_2 : list of retention times from a different picked peak file
        DESCRIPTION: Takes the values from the first list provided and subtracts
        them from the values in the second list provided (they're subtracted at the same index)
        Returns
        -------
        a list of floats containing the rt differences between the 2 files

        '''
        
        #Variable to store the differences
        
        difference = []
        
        '''
        By zipping the lists together it means you only require 1 for loop to go through
        and subtract the values
        '''
        
        zip_obj = zip(rt_list_1, rt_list_2)
        
        for i, j in zip_obj:
            
            #i and j represent the first rt values in rt_list_1 and 2 respectively
            
            #simply append the subtraction value to the empty list created earlier
            

            difference.append(i - j)
        
        #Return the list of differences    
        
        return difference