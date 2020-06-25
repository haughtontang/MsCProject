# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:24:53 2020

@author: Don Haughton
"""

import statistics

class Peak(object):
    
    def __init__(self, key, mz, rt, intensity, file):
        
        '''
        Parameters
        ----------
        key: int
        mz: float
        rt: float
        intensity: float
        file: string
        DESCRIPTION: This constructor will create peak objects- which are defined by the 3 
        arguments passed to the constrcutor
        -------
        '''
        self.id = key
        self.mz = mz
        self.rt = rt
        self.intensity = intensity
        self.file = file
    
    #Getters to be used to get specific access to the peak objects attributes
    
    def get_id (self):
        
        return self.id
    
    def get_mz(self):
        
        return self.mz
    
    def get_rt(self):
        
        return self.rt
    
    def get_intensity(self):
        
        return self.intensity
    
    def get_file(self):
        
        return self.file      
       
class PeakSet(object):
    
    def __init__(self, peak_list):
        
        '''
        Parameters
        ----------
        peak_list: list of peak objects that have similar mz and rt
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
    
    def align(peak_obj_list, another_peak_obj_list):
        
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
        rt_buffer = 0.08
        
        '''
        loop over every peak in the first list, comparing it to every peak in the 
        second list, if they fall within an acceptable range- dictated by the upper
        and lower tolerances set by the buffers, then its used to created a new peakset list
        
        once the first peak in the first file has been comapred to all peaks in the second file
        the next peak is checked and this process continues until all peaks have been compared
        and peakset lists are created.
        
        in the list bellow, i and j both represent peaks
        '''
        for i in peak_obj_list:
            
            #peakset list
        
            peakset = []
            
            #mz tolerances
            
            upper_mz_tolerance = i.get_mz() + mz_buffer
            lower_mz_tolerance = i.get_mz() - mz_buffer
            
            #rt tolerances
            
            upper_rt_tolerance = i.get_rt() + rt_buffer
            lower_rt_tolerance = i.get_rt() - rt_buffer
            
            #If there are no matches it will always contain itself so add it to peakset list NOW
            
            peakset.append(i)
            
            for j in another_peak_obj_list:
                
                
                
                #Get the mz and rt to compare to the peak in the first list
                
                mz = j.get_mz()
                rt = j.get_rt()
                
                #Make some boolean variables comparing the mz and rt to the tolerances 
                
                mz_comp = mz >= lower_mz_tolerance and mz <= upper_mz_tolerance
                rt_comp = rt >= lower_rt_tolerance and rt <= upper_rt_tolerance
                
                #If both comp variables are true then it'll add it to the peakset list
                
                if mz_comp == True and rt_comp == True:
                    
                    peakset.append(j)
            
            #Previously I had this inside the if statement but it was producing very large results- not sure if
            #It makes sense having it here but it does give a nice number- will investigate later
            
            list_of_lists.append(peakset)
                
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

    def find_peaksets(peakset_list, another_peakset_list, return_unmatched):
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
                
                #use getter to extraxt mz from peak object and store this in seperate variable with the buffer
                
                upper_diff = j.get_mz() + buffer
                lower_diff = j.get_mz() - buffer
                
                #If they fall within this range then its a match, append them to the lists
                
                if i.get_mz() <= upper_diff and i.get_mz() >= lower_diff:
                    
                    '''
                    Make Peakset objects, since they match the boolean will be True
                    '''
                    
                    new_peakset = PeakSet(i, True)
                    new_peakset2 = PeakSet(j, True)
                    
                    #Store these objects in lists to be returned at the end
                    
                    matched_first.append(new_peakset)
                    matched_second.append(new_peakset2)
                    
                    #Store the information from the peak file so they can be compared to find unmatched peaksets
                    
                    unmatched_comp_first.append(i)
                    
                    unmatched_comp_second.append(j)
        
        #If the boolean is false dont calculate unqiue peaks
                    
        if return_unmatched == False:            
            
            #These remove repeats and make same size methods are just work arounds for the probelm
            
            PeakSet.remove_repeate(matched_first)
            PeakSet.remove_repeate(matched_second)
            PeakSet.make_same_size(matched_first, matched_second)
            
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
                    
                    unique_peakset1 = PeakSet(i, False)
                    
                    #Place peakset object into a list
                    
                    unique.append(unique_peakset1)
            
            #Process is repeated but for the secon file provided and its matched peaks        
            
            print("length of unique after the first file is", len(unique))
            
            for j in another_peakset_list:
                 
                
                if j not in unmatched_comp_second:
                    
                    #Create peakset object
                                    
                    unique_peakset2 = PeakSet(j, False)
                    
                    #Place peakset object into the unique list
                                        
                    unique.append(unique_peakset2)      
            
            
            
            #These remove repeats and make same size methods are just work arounds for the probelm
            
            PeakSet.remove_repeate(matched_first)
            PeakSet.remove_repeate(matched_second)
            PeakSet.make_same_size(matched_first, matched_second)
            
            #Return all 3 lists
            
            return matched_first, matched_second, unique
     
        
    def match_peaks_rt_step(peakset_list, another_peak_set_obj):
        '''
        Parameters
        ----------
        peakset_list : list of peakset objects that have been matched for m/z from a file
        another_peak_set_obj : list of peakset objects that have been matched for m/z from a different file
        DESCRIPTION: Compare the matched peaks in the 2 lists, if the matched peaks have an rt difference
        > or < 0.08 they're removed from the list
        List of matched peaks after being filtered for RT
        Returns
        -------
        2 lists of peakset objects that have been matched by RT
        '''
    
        #Buffer value for the RT in minutes
        
        buffer = 0.08
        
        #Empty lists that will contain peaksets matched by rt at the end
        
        rt_match1 = []
        rt_match2 = []
        
        '''
        Zip object makes it easier to compare the matched peaks to each other as we want to compare the
        peakset lists by theri indeces i.e. comparing the rt of peakset in peakset_list[0] to 
        the rt of peakset in another_peakset_list[0] and so on
        '''
        
        zip_obj = zip(peakset_list, another_peak_set_obj)
        
        for i, j in zip_obj:
            
            #The limits of if they're matched are defined by the upper limit and lower limit
            
            '''
            These are generated by  taking the rt of the current peakset object
            and adding/subtracting the the buffer value
            '''
            
            upper_limit = j.peak.rt + buffer
            lower_limit = j.peak.rt - buffer
            
            #If the peaksets RT is between these 2 values then they peaks match by m/z as well as rt, so they're added to the list
            
            if i.peak.rt <= upper_limit and i.peak.rt >= lower_limit:
                
                #Adding matched peakset objects to the list
                
                rt_match1.append(i)
                rt_match2.append(j)
        
        #Return these populated lists  
        
        return rt_match1, rt_match2  
        
import matplotlib.pyplot as plt

class Plotter:
    
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
        self : peak, peakset or anchor object
        DESCRIPTION: This will loop over the list attribute in the object,#
        extracting the RT values into a sepearate list
        These will be converted to seconds (as mzMINE represent RT in minutes) 
        prior tO being placed into the new list.
        Returns
        -------
        List of RT in seconds
        '''
        #Convert these values into seconds since they're currently in minutes
        
        rt_converted = []
        
        #Check if it is a peak or peakset obj list
        
        flag = isinstance(peak_obj_list[0], Peak)
        
        #if it is an instance of peak then only the get_rt method has to be called
        
        if flag:
        
            for i in peak_obj_list:
                
                #converting from minutes to seconds so multiply by 60
                
                rt_convert = i.get_rt() *60
                
                #Add this converted time to a list
            
                rt_converted.append(rt_convert)
            
            #return the list of conversions    
            
            return rt_converted
        
        #If it isnt a peak then it must be a peakset, needs slight alteration when grabbing rt
        
        else:
            
            for i in peak_obj_list:
                
                #since its a peakset we need to get the peak before being able to get the rt
                
                rt_convert = i.get_peak().get_rt() *60
            
                #Add this converted time to a list
            
                rt_converted.append(rt_convert)
             
            #return the list of conversions       
             
            return rt_converted
    
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