# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 12:32:20 2020

@author: Don Haughton
"""
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Peak as p
from PeakTools import Plotter as plot

p1 = um.peak_creator('reduced_multi_1_full.csv')
p2 = um.peak_creator('reduced_multi_2_full.csv')

#p1 = p.peak_storage(f1)
#p2 = p.peak_storage(f2)

#Can sort peaks this way using pythons inbuilt functions

p1.sort(key=lambda x: x.intensity, reverse=True)
p2.sort(key=lambda x: x.intensity, reverse=True)

p1 = um.most_sig_peaks(p1, 5e6)
p2 = um.most_sig_peaks(p2, 5e6)

print(len(p1), len(p2))

count = 0

#26/05 - figure out why there are so many repeated values in this method and why it isnt working

#Its also producing some empty lists so look into why thats happening as well

#In its current state its unable to make peakset objs from the list so sort it out NOW

#Cant figure out the issues with align so simply begin again in this moment

'''
Irresepctive of how many matches/ multi peak peaksets there are the length of
list of lists needs to be 526 as thats the accumulation between the 2 sig peaks lists
'''

'''
Its coming together, so the probelm I was getting:
    
mean requires at least one data point    
    
Its because one list was longer than the other so it was resulting in null values

for this sake that means the longer list has to go first in the entry
So im gonna have to include an if statmenet in the code to account for that

a simple if len(x) > len(y) will do it

'''

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
    
    '''
    #The largest list needs to be the first in the loop or else it'll produce an error when
    calculating the mean mv, rt ect downstream at the peakset creation stage as there will be null values
    '''
    
    if len(peak_obj_list) > len(another_peak_obj_list):
        
        largest = peak_obj_list
        smallest = another_peak_obj_list
        
    else:
        
        largest = another_peak_obj_list
        smallest = peak_obj_list
        
        
    '''
    Lists for those that dont match to be added to
    Unique 1 for those in the largest list and unique 2 for those in the smaller list
    We want them to be in seperate lists as they're not matched so we want to keep them seperate
    '''
    
    peakset = []
    unmatched_file1 = []
    unmatched_file2 = []
    
    
    '''
    30/06 I'm tweeking this method here as I have found it to be faulty
    The maxiumm amount of peaksets that should be found from this is 526- and that 
    should only be happening when no peaks match
    So bellow ive reworked the method
    
    In this state it'll loop over all the peaks in largest and find matches
    If it matches then both peaks from the 2 files are added to peakset, if not
    then only the unique peaks from the largest are appended  if not
    
    Due to the loop structure its impossible to make unique peaksets from both files
    Instead Ive made a seperate nested for loop, this goes over all the peaks in the
    smallest peak list and if that peak isnt in peakset (list ive made in the nested for loops bellow)
    then its added to unmatched_2. From here I'm getting the number of pseudo peaksets to be 370 which sounds
    about right
    
    Only thing to do now is sort out the rt extract and sort as thats a bit off
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
                
                peakset.append(i)
                peakset.append(j)
                list_of_lists.append(peakset)
                peakset = []
 
        #If they dont match    
        
        else:
            
            unmatched_file1.append(i)
            list_of_lists.append(unmatched_file1)
            unmatched_file1 = []
        
        
    double = []            

    for i in list_of_lists:
    
        if len(i) ==2:
    
            double.append(i)
    
   
    for i in smallest:           
        for j in double:
            if i not in j:
                unmatched_file2.append(i)
                list_of_lists.append(unmatched_file2)
                unmatched_file2 = []
            
    #peakset = list(set(peakset))
    #unmatched_file1 = list(set(unmatched_file1))
    #unmatched_file2 = list(set(unmatched_file2))
    
    #list_of_lists.append(peakset)
    #list_of_lists.append(unmatched_file1)
    #list_of_lists.append(unmatched_file2)
    
    return list_of_lists

pps = align(p1,p2)
print(len(pps))
ps = ps.make_peaksets(pps)

'''
EOW note 26/06: Good news is it works, bad news is doesnt work properly, getting way too many results
come back to look at that method another time- im sure it'll just be something to do with the way the loops are
indented. 
From there I want to ahead and:

 test the plots, do the guassian with this new peakset structure, fix the anchor
class to reflect this new class structure and from there move onto ms2 tings
'''

'''
29/06- lets try writing a new method and seeing how it works 
Go step by step and test it to see where im going wrong
'''

def rt_extract_convert(peak_obj_list):
    '''
    Parameters
    ----------
    peak_obj_list : peak or peakset object
    DESCRIPTION: This will loop over the list attribute in the object,#
    extracting the RT values into a sepearate list
    These will be converted to seconds (as mzMINE represent RT in minutes) 
    prior tO being placed into the new list.
    Returns
    -------
    List of RT in seconds
    NOTE: if peakset obj list is provided the number of lists returned
    Will be the number of files that make up the peaksets
    '''
    #Convert these values into seconds since they're currently in minutes
    
    rt_converted = []
    
    #Check if it is a peak or peakset obj list
    
    flag = isinstance(peak_obj_list[0], p)
    
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
        
        #Find out the original file, to do that I need to loop over all the peaksets and find all the unique file names
        
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
        
        peaks = []
        
        #loop over peakset objects
        
        for ps in peak_obj_list:
            
            if len(ps.peaks) < 2:
                
                peak_obj_list.remove(ps)
                
        print("length after removing singlet peaksets", len(peak_obj_list))
        
        for peakset in peak_obj_list:
            
            #loop over peak list attributes that are part of those objects
            
            for peak in peakset.peaks:
                
                #Get the peaks in that list attribute and append it to this list
                
                peaks.append(peak)
        
        #This method produces a lot of repeats so make the list only contain unique peak objects using set()
        
        peaks = list(set(peaks))
        
        #loop over this peak obj list and extract and convert their rt
        
        for peak in peaks:
            
            #Check the original file it came from and append it to a different list to maintain data integrity
            
            if peak.get_file() == names[0]:
                
                rt = peak.get_rt() * 60
                
                rt1.append(rt)
            
            #Same as ove but for if it came from a different file    
            
            else:
                
                rt = peak.get_rt() * 60
                
                rt2.append(rt)
        
        #Return 2 lists of rt in seconds        
        
        return rt1, rt2
                       
rt1, rt2 = rt_extract_convert(ps)

print(len(rt1),len(rt2))
        
diff = plot.rt_minus_rt_plot(rt1, rt2)

#plot(rt1,diff,"","","",False)
            
            
            
   
        
