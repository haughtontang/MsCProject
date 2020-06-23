# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:24:53 2020

@author: Don Haughton
"""

class Peak(object):
    
    def __init__(self, mz, rt, intensity):
        
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
        self.intensity = intensity
    
    #Getters to be used to get specific access to the peak objects attributes
    
    def get_mz(self):
        
        return self.mz
    
    def get_rt(self):
        
        return self.rt
    
    def get_intensity(self):
        
        return self.intensity
            
       
class PeakSet(object):
    
    def __init__(self, peak, matched):
        
        '''
        Parameters
        ----------
        peak: peak obj
        matched: boolean
        DESCRIPTION: This constructor will create peakset objects- which are defined 
        by the arguments passed to the constructor
        -------
        '''
        
        self.peak = peak
        self.matched = matched
        
    def get_peak(self):
        
        return self.peak
        
    def is_matched(self):
        
        return self.matched
   
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
                
                #The m/z value is stored at the 0th index in the files
                
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
        
        #if it is then do the following
        
        if flag:
        
            for i in peak_obj_list:
                          
                rt_convert = i.get_rt() *60
            
                rt_converted.append(rt_convert)
                
            return rt_converted
        
        #If it isnt a peak then it must be a peakset, needs slight alteration when grabbing rt
        
        else:
            
            for i in peak_obj_list:
                          
                rt_convert = i.get_peak().get_rt() *60
            
                rt_converted.append(rt_convert)
                
            return rt_converted
    
            
    def rt_minus_rt_plot(rt_list_1, rt_list_2):
        
        difference = []
        
        zip_obj = zip(rt_list_1, rt_list_2)
        
        for i, j in zip_obj:
            
            difference.append(i - j)
            
        return difference
