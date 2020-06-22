# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 14:11:31 2020

@author: Don Haughton

Several classes that have differing functionality;
The main purpose of these classes are to convert picked peak files into corresponding objects
depending on their purpose i.e Peak, peakset ect

From there the objects can be manipulated to eventually visualise the differenece in RT 
(Or other paramteres depending on your prefference) to help solve the probelm of RT alignment
"""

#These imports are necessary for reading .csv files and sorting by specific indecies

import csv
from operator import itemgetter

class Peak:
    
    #Constructor for creating objects that will contain a list of peaks
    
    def __init__ (self, file_path):
        
        '''
        Parameters
        ----------
        file_path: the file path to a file of picked peaks, expected format is .csv
        DESCRIPTION: This constructor will parse through the file and create a list attribute
        where each index in the list represents all the information that correspond to a single peak
        i.e m/z, rt, hegiht ect...
        -------
        '''
        
        file = open(file_path, newline = '')

        #The reader is part of the csv library but it stores this as an obkect, need to do more to extract the data in the file
        
        reader = csv.reader(file)
        
        #Skips the names of the columns in the file
        
        next(reader)
        
        #Empty list for storing the peak data
        
        self.peaks = []
        
        #Loop over all the rows in the files, sroting the relevant information in variables to append to my empty list above
        
        for row in reader:
            #row = [id, m/z, rt, row number, peak status, rt start, rt end, rt duration, peak height, peak area, data points]
            
            #Now that I know the types and the data lets format it
            
            peak_id = int(row[0])
            mz = float(row[1])
            rt = float(row[2])
            row_number = int(row[3])
            status = str(row[4])
            rt_start = float(row[5])
            rt_end = float(row[6])
            rt_duration = float(row[7])
            height =  float(row[8])
            area = float(row[9])
            data_point = int(row[10])
            
            #Now that its properly formatted as the proper type put it into a list
            
            self.peaks.append([peak_id, mz, rt, row_number, status, rt_start, rt_end, rt_duration, height, area, data_point])

    #Sort peak object in descending of index passed to the argument
    
    def sort_peaks(self, column_to_sort_by):
        
        '''
        Parameters
        ----------
        column_to_sort_by: The index of the column you wish to sort by in the object
        DESCRIPTION: The function will sort the peak list attribute of the peak object by the 
        Index that is passed to the argument.
        -------
        '''
        
        self.peaks = sorted(self.peaks, key = itemgetter(column_to_sort_by), reverse = True)
        
    #Next a function for extracting the most intesne peaks
    
    def most_sig_peaks(self, value, alter_object):
        
        '''
        Parameters
        ----------
        value: int/double- the cut off intensity value
        alter_object: boolean, if true it will alter the peak list attribute of the object,
        if false, it returns a new list
        DESCRIPTION: The function will loop through the provided peak list and remove any peaks that are 
        bellow the intensity value that is provided in the argument. 
        -------
        '''
        
        #New variable to be returned at the end
        
        sig_peaks = []
        
        for i in self.peaks:
            
            #intensity(height) is at the 8th index
            
            intesnity = i[8]
            
            if intesnity >= value:
                
                #Only stores the peaks that reach the condition of intensity
                
                sig_peaks.append(i)
        
        #Changes the peak list attribute of the object to be equal to the the newly created sig peaks list
        
        if alter_object == True:
        
            self.peaks = sig_peaks
            
        else:
            
            return sig_peaks
                
    def get_mz(self):
        '''
        Parameters
        ----------
        self : a peak object
        DESCRIPTION: extracts the m/z values from the object that is passed to it and creats a new list
        variable containing those values
        RETURNS
        -------
        A list of those extracted m/z values
        '''
        
        #New variable to be returned at the end
        
        ordered_mz = []
    
        for i in self.peaks:
            
            #m/z is at the second index
            
            #A single index in the peak list contains multiple values (m/z, rt, height) so the second index is needed
            
            mz = i[1]
            
            ordered_mz.append(mz)
            
        return ordered_mz

    def get_rt(self):
        '''
        Parameters
        ----------
        self : a peak object
        DESCRIPTION: extracts the rt values from the object that is passed to it
    
        Returns
        -------
        Another list of just rt values corresponding to the rt values in the peak list attribute of peak
        '''
        
        #New variable to be returned at the end
        
        ordered_rt = []
    
        for i in self.peaks:
            
             #rt is at the third index
            
             #A single index in the peak list contains multiple values (m/z, rt, height) so the second index is needed
            
            rt = i[2]
            
            ordered_rt.append(rt)
            
        return ordered_rt
    
#The stats package will be needed for calculating the mean for a aprticular function
    
import statistics

#Anchor isn't that different from a peak bar the methods that change the attributes

class Anchor(Peak):
    
    #Constructor, exactly the same as a peak, only the methods will differ
    
    def __init__(self, file_path):
        
        '''
        Parameters
        ----------
        file_path: the file path to a file of picked peaks, expected format is .csv
        DESCRIPTION: This constructor will parse through the file and create a list attribute
        where each index in the list represents all the information that correspond to a single peak
        i.e m/z, rt, hegiht ect...
        -------
        '''
        
        super().__init__(file_path)
        
    def filter_mz(self, sig_val):
        
        '''
        Parameters
        ----------
        self : Anchor object 
        sig_val: To establish an acceptable m/z range we want to get the average m/z value from 
        Some very sig peaks, to get these you need to input what intesnity cut off you want to
        use to get the most intese peaks
        DESCRIPTION: filters through the list that is passed and removes
        Values from it that dont satisfy the criteria
        In this case that is those m/z values for peaks that are higher or lower
        Than the average of the very significant peaks with a 10% buffer either way    
        '''
        
        #Get a list of peaks that are very significant
       
        very_sig_peaks = Peak.most_sig_peaks(self, sig_val, False)
        
        #Empty list variable to be populated with them/z values for the very sig peaks in the list above
        
        mz_list = []
        
        #Get the mz values for these very sig peaks
        
        for i in very_sig_peaks:
            mz = i[1]
            mz_list.append(mz)
        
        #Calculate the avg of these m/z values and then allow a buffer of +/- 10% of that average
        
        average_mz = statistics.mean(mz_list)
        
        #These represent the upper and lower ranges of the buffers, each one being the mean + 10% of the bean and - 10% of the mean respectively
        
        comparible_up = (average_mz /100 * 10) + average_mz 
        comparible_down = average_mz - (average_mz /100 * 10) 
       
        #Go through the list passd to the function and remove any values that dont fall within the upper and lower buffers
        
        for i in self.peaks:
            
            #Looking to compare m/z which is at the second index
            
            row_to_be_checked = i[1]
            
            #If the m/z value doesnt fall between the upper and lower tolerances it is removed
            
            if row_to_be_checked > comparible_up or row_to_be_checked < comparible_down:
                    
                self.peaks.remove(i)
            
                
    def filter_rt(self):
        '''
        Parameters
        ----------
        self : Anchor object 
        DESCRIPTION: filters through the attribute list of the obejct that is passed and removes
        Values from it that dont satisfy the criteria
        In this case that is those rt values for peaks that are higher or lower
        Than the most significant peaks rt value with a 15% buffer either way
        '''
        
        #Get a list of rt values from the peak list passed to the function
        
        rt_list = Peak.get_rt(self)
        
        #Upper and lower values to compare the whole list against
        
        #Take the RT of the most intesne peak and allow a +/- 15% buffer
        
        comparible_up = rt_list[0] + (rt_list[0]/100 * 15)
        comparible_down = rt_list[0] - (rt_list[0]/100 * 15)
    
        for i in self.peaks:
            
            row_to_be_checked = i[2]
            
            #Remove peaks from the list that fall outside of this range
            
            if row_to_be_checked > comparible_up or row_to_be_checked < comparible_down:
                
                    self.peaks.remove(i)
    
    '''
    From this point down to the start of the peakset class I belive are empty/useless methods
    
    So lets leave them un commented for now as to not waste my time
    '''
    
    def find_same_anchors(self,first_anchor_obj, second_anchor_obj):
        '''
        Parameters
        ----------
        first_anchor_obj : list of filtered peaks (filtered for m/z and rt)
        second_anchor_obj : list of filtered peaks (filtered for m/z and rt)
        DESCRIPTION: This will loop through both of the filtered anchors provided and find
        Any anchors that are the same
        Since there are naturally occuring differences each time for the same feature a buffer of 0.00005 is allowed
        Returns
        -------
        2 lists that have the same anchors between each file
        '''
    
        buffer = 0.00015
        #Create list variable for storing the same anchors
        
        common_anchors_1 = []
        common_anchors_2 = []
        
        for i in first_anchor_obj.peaks:
            for j in first_anchor_obj.peaks:
                
                #Set the acceptable range
                
                upper_difference_range = j[1] + buffer
                lower_difference_range = j[1] - buffer
                
                if i[1] == j[1] or i[1] <= upper_difference_range and i[1] >= lower_difference_range:
                    common_anchors_1.append(i)
                    common_anchors_2.append(j)
    
        return common_anchors_1, common_anchors_2
    
    #Now I want to make a function that'll append the list of both anchors, filtering out any repeats between the 2 lists
        
    def anchors_combined(self,anchors_list1, anchors_list2):
        '''
        Parameters
        ----------
        anchors_list1 : anchor list
        anchors_list2 : anchor list
        DESCRIPTION: Intended to be used after anchor lists have been compiled, from there
        it will filter through the lists and combine them into one. In the process it'll look for
        The same peaks within the new list and remove them'
        Returns
        -------
        List of combined peaks with doublers removed
    
        '''
        
        #Empty variable to be filled and returned at the end
        
        anchors_complete = []
        
        #Loops to fill the list above with the values from both lists in the argument
        
        for i in anchors_list1:
            anchors_complete.append(i)
            
        for j in anchors_list2:
            anchors_complete.append(j)
    
        #Loop to go through and check for the same peaks
            
        #repeats = find_same_anchors(anchors_list1, anchors_list2)
        
        #Counter variable to itterate in the loop
    
        counter = 0
    
        for row in anchors_complete:
            
            #The m/z is at the second index so create a  variable to check it
            
            mz_comparison = row[1]
            
            #Another loop to go through the list of repeats created above
            
            #for value in repeats:
                
                #If the m/z value in repeats is found in the complete anchor list then it is removed 
                
                #if mz_comparison == value:
                    
                    #anchors_complete.pop(counter)
            
            #Itterate counter so that the appropriate list index is deleted 
            
            counter +=1
            
        return anchors_complete        
    
class PeakSet(Peak):
    
    def __init__(self, file_path):
        
        '''
        Parameters
        ----------
        file_path: the file path to a file of picked peaks, expected format is .csv
        DESCRIPTION: This constructor will parse through the file and create a list attribute
        where each index in the list represents all the information that correspond to a single peak
        i.e m/z, rt, hegiht ect...
        -------
        '''
        
        super().__init__(file_path)
        
    #Works exactly the same way as the most_sig_peaks function in the peak class
    
    def cut_off(self, value, alter_object):
        
        '''
        Parameters
        ----------
        value: int/double- the cut off intensity value
        alter_object: boolean, if true it will alter the peak list attribute of the object,
        if false, it returns a new list
        DESCRIPTION: The function will loop through the provided peak list and remove any peaks that are 
        bellow the intensity value that is provided in the argument. 
        -------
        '''
        
        super().most_sig_peaks(value, alter_object)
        
        
    '''
    This is far from ideal but having to have this method to filter through and remove
    repeated values in a list as the match_peaks method bellow keeps producing duplicates
    I cant figure out why this is, so this method will remove any repeated values
    
    May also be a good idea to have a method returning a boolean to say if there are any lists with
    repeated values in them
    '''
    
    def remove_repeate(self):
        
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
        
        for i in self.peaks: 
            if i not in unique_values: 
                unique_values.append(i)
        
        #Reassign the value of the list attribute to the list produced in the function        
        
        self.peaks = unique_values
        
    '''
    The buffer value in match_peaks seems to be too generous and because of this it allows
    For differing values between the 2 files, it may be entirely possible that its just that one
    file has more of the same metabolite than the other but then again im not sure if thats possible
    
    So I'm gonna have to write a new function bellow to make the 2 the same size
    '''
    
    def make_same_size(self,another_peak_set_obj):
        
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
        
        if len(self.peaks) != len(another_peak_set_obj.peaks):
            
            #First conditional matches the length to the second peak object if its the samller one
            
            if len(self.peaks) > len(another_peak_set_obj.peaks):
                
                #Variable to store the length of the list, this will be the desired size we want
                
                value = len(another_peak_set_obj.peaks)
                
                #Empty list variable to append
                
                same_size = []
                
                for i in self.peaks:
                
                    same_size.append(i)
                
                    #When the list is the same length as the smaller list, break out of the loop
                
                    if len(same_size) == value:
                        break
                    
                #Make the peakset list attribute equal to the new variable
                #so they will be the same size as the other objects list attribute    
                    
                self.peaks = same_size
             
            #The steps in the else condition bellow are exactly the same as above but for if the 
            #the other peak objects list attribute is larger
             
            else:
                
                value = len(self.peaks)
                
                same_size = []
                
                for i in another_peak_set_obj.peaks:
                
                    same_size.append(i)
                
                    if len(same_size) == value:
                        break
                another_peak_set_obj.peaks = same_size
                

    def match_peaks(self, another_peak_set_obj):
        '''
        Parameters
        ----------
        self : Peak set object
        peak_set_obj2 : Another peak set object to compare to the first
        DESCRIPTION: This function loops through both peak lists attributes 
        and finds peaks that are the same on the basis of their m/z.
      
        '''
        
        '''
        How are we defining that the peaks in the 2 files are the same?
        On average the m/z of the same peak in 2 filles differs by ~0.000143
        For RT the average difference is 0.04
        '''
        
        #Buffer value for the mz
        
        buffer = 0.00015
        
        #A place to store the matched peaks in both the files
        
        matched_first = []
        matched_second = []
        
        '''
        A nested for loop to goes through and check all values in the peak list 
        Comparing it to that of the other list. Since we want m/z to be very similar check this first,
        Then for whatever is left check the RT to filter further
        ''' 
        
        for i in self.peaks:
            for j in another_peak_set_obj.peaks:
                
                #The m/z value is stored at the second index in the files
                
                upper_diff = j[1] + buffer
                lower_diff = j[1] - buffer
                
                #If they fall within this range then its a match, append them to the lists
                
                if i[1] <= upper_diff and i[1] >= lower_diff:
                    
                    matched_first.append(i)
                    matched_second.append(j)
        
        #Update the objects lists to reflect what is matched
        
        self.peaks = matched_first
        another_peak_set_obj.peaks = matched_second
        
        #The step above is producing repeated values in the list so this method will remove those
        
        self.remove_repeate()
        another_peak_set_obj.remove_repeate()
        
        #Make them the same
        
        self.make_same_size(another_peak_set_obj)
    
    #I dont feel like this step is entirely necessary to be honest, may not be worth fixing
    #Though I have figured out that the primary probelm is in the buffer value, its way too high
    #So thats why I'm getting so many damn peaks
    
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
     
    def rt_extract_convert(self):
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
        #Function laready exists from earlier to get rt so use it here
        
        new_rt = Peak.get_rt(self)
        
        #Convert these values into seconds since they're currently in minutes
        
        rt_converted = []
        
        for i in new_rt:
                      
            rt_convert = i *60
        
            rt_converted.append(rt_convert)
            
        return rt_converted
    
            
    def rt_minus_rt_plot(rt_list_1, rt_list_2):
        
        difference = []
        
        zip_obj = zip(rt_list_1, rt_list_2)
        
        for i, j in zip_obj:
            
            difference.append(i - j)
            
        return difference
           
           
           
           
           
    
           
    