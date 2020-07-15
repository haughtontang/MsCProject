# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 12:32:20 2020

@author: Don Haughton
"""
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Peak as p
from PeakTools import Plotter as plot
#test = um.peak_creator("D:/Users/donha/Documents/MastersProject/Practice Python/reduced_multi_1_full.csv", "")
p1 = um.peak_creator('multi 1 ms2.csv', "multi1_ms2.MGF")
p2 = um.peak_creator('multi 2 ms2.csv', "multi2_ms2.MGF")

#p1 = p.peak_storage(f1)
#p2 = p.peak_storage(f2)

#Can sort peaks this way using pythons inbuilt functions

p1.sort(key=lambda x: x.intensity, reverse=True)
p2.sort(key=lambda x: x.intensity, reverse=True)

#p1 = um.most_sig_peaks(p1, 5e6)
#p2 = um.most_sig_peaks(p2, 5e6)

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
    rt_buffer = 0.5
    
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

pps = ps.align(p1,p2, 1.5)
print("pseudo peakset length = ", len(pps))
ps = ps.make_peaksets(pps)
print("peakset length = ",len(ps))

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
                
                rt = peak.get_rt() * 60
                
                rt1.append(rt)
            
            #Same as ove but for if it came from a different file    
            
            else:
                
                rt = peak.get_rt() * 60
                
                rt2.append(rt)
        
        #Return 2 lists of rt in seconds        
        
        return rt1, rt2
                       
#rt1, rt2 = plot.rt_extract_convert(ps)

#print(len(rt1),len(rt2))
        
#diff = plot.rt_minus_rt_plot(rt1, rt2)

#plot(rt1,diff,"","","",False)

#02/07- dont need to worry about anchors for now

'''

import MakeAnchors as ma

mz_anch = ma.filter_mz(ps, 5e7)

rt_anch = ma.filter_rt(mz_anch)

print("mz anchors = {} and rt anchors = {}".format(len(mz_anch), len(rt_anch)))

rt1, rt2 = plot.rt_extract_convert(rt_anch)

print(len(rt1),len(rt2))
'''

#Testing the ms2 mtaching

import SimilarityCalc as sc

#spectra_matches = sc.similarity_score("multi1_ms2.MGF","multi2_ms2.MGF")

#This method finds peaksets that have >1 peak in them and then checks if they have ms2 and then calculates the similarity

def ms2_comparison(peakset_list):
    
    ms2_comp = []
    
    for ps in peakset_list:
        
        if len(ps.peaks) > 1:
            
            ms2 = []
        
            for peak in ps.peaks:
                
                if peak.ms2 != None:
                    
                    ms2.append(peak.ms2)
                    
            if len(ms2) > 1 and None not in ms2:
                
                spectra_similarity = sc.similarity_score(ms2)
                
                if spectra_similarity > 0.9:
                    
                    ms2_comp.append(ps)
                    
    return ms2_comp
            
            

def assign_ms2(peakset_list, spectra_list):
    '''
    Parameters
    ----------
    peakset_list : List of peakset objects
    spectra_list : List of spectra objects
    DESCRIPTION: Each peak from the file has a unique id, the same is true for ms spectra.
    Using these unique ids, this method will loop over the peaks in peakset and
    the spectra objects in the spectra list, find the matching ids- put the peakset object
    and that spectrum object in a tuple, then append it to a list

    Returns
    -------
    List of tuples corresponding to peakset objects and thier ms2 spectra.

    '''
    
    #make an empty list, match peaksets to their spectra, if they have it
    
    peaksets_and_ms2 = []
    
    '''
    Find out which file amongst the peaks in peakset contains more peaks
    This will be required later when assigning ms2 spectea- as the ids of the largest spectrum
    list (corresponding to the largest picked peak file) is used to assign spectrum objects to 
    peaksets
    '''
    
    largest_file, smallest_file = um.find_largest_file(peakset_list)
    
    '''
    loop over the list of peakset objects
    This will require a nested loop as each peakset object has a list attribute
    which contains the peaks associated with that peakset
    '''
    
    for ps in peakset_list:
        
        for peak in ps.peaks:
            
            '''
            there are bound to be repeated values in the ids in peakset since
            We're getting the peaks from more than 2 files
            the id in spectra list at the first index is equal to that of the largest
            mfg file- which is paired with the largest picked peak file. So for them to match, the peak
            must have that file name and match an id from the spectra list
            '''
            #Get the peak id in peakset
            
            peak_id = peak.get_id()
            
            #get the file that the peak originated from
             
            original_file = peak.get_file()
            
            for ms2 in spectra_list:
                
                #The id of the largest mfg file is at the 0th index
                
                if ms2[0] == peak_id and original_file == largest_file:
                    
                    #Make a tuple to append to the list
                    
                    together = (ps, ms2)
                    
                    peaksets_and_ms2.append(together)
    
    #Length of list should equal the length of the spectra file
                    
    return peaksets_and_ms2                    

            
#tog = assign_ms2(ps, spectra_matches)

#Now that peaksets are matched to thier ms2, loop through and compare peaks based on ms2

def ms2_matching(combined):
    '''
    Parameters
    ----------
    combined : a list of tuples containing peakset objects and their ms2 spectra
    DESCRIPTION: This will filter through the tuple list and find peaksets that
    Have very highly scoring similarity scores- the cut off value for this has been
    set at 0.99 similarity
    Returns
    -------
    A list of peakset objects that have very high similarity score
    '''
    
    #Empty list to return at the end
    
    highly_likely_matches = []
    
    #Get the largest and smallest file names
    
    #First need to get a list of peaksets
    
    peaksets = []
    
    for row in combined:
        
        ps = row[0]
        
        peaksets.append(ps)
    
    largest, smallest = um.find_largest_file(peaksets)
    
    #Loop over the list of tuples

    for row in combined:
        
        #Store the information in the tuples as seperate variables

        ps = row[0]
        
        ms2 = row[1]
        
        peak_list = ps.peaks
        
        '''
        We want to validate peaksets that have greater that have >1 peak, as these are likely to
        Be the same metabolite across different files, so we only want to run the ms2 validation
        on peaks that meet this criteria
        '''
        
        if len(peak_list) > 1:
            
            #Look over the multi peak peaksets
            
            for peak in peak_list:
                
                #Get the file the peak originated from
                
                file = peak.get_file()
                
                '''
                The spectra matches are themsleves tuples, in which they have a list of ids of the
                smaller mfg file that are compared to the largest mfg file. This is done for each id of the 
                larger mfg file and each comparison makes up one tuple in the list
                
                The checker boolean bellow is checking if the id of the specific peak in the peakset list
                is one of the peaks that was compared to when making spectra comparisons. In the previous align method
                The spectra and peakset objects were matched by the ids of the largest file. In this step they're
                matched by the id of the smaller file
                
                This is only one step, as the id of the larger file may coincidentally also match an id of a spectra
                that was compared the peaks file name must also be equal to that of the smaller file. That is why
                the file names were generated earlier
                '''
                
                #File list is at the second index in the spectra matches tuple
                
                checker = peak.get_id() in ms2[1]
                
                #An average score of all the comparisons made is at the third tuple
                
                score = ms2[2]
                
                '''
                To be considered a likely match the peak must originate from the smallest file,
                have been a peak that had an ms2 spectra that was compared against the larger mfg file
                and have a similarity score > .98
                
                '''
                
                if file == smallest and checker == True and score > .98:
                    
                    #If its a match, append it to the list

                    highly_likely_matches.append(ps)
    
    #A list containing the peaks that are likely to have matched bt m/z, rt and ms2 spectra matching                 
    
    return highly_likely_matches

ms2_validated_peaksets = ms2_comparison(ps)

#Result = 43. It actually works. Keep in mind that this for the full file- no intensity filter applied.

#print(len(test))


rt1, rt2 = plot.rt_extract_convert(ms2_validated_peaksets)

print(len(rt1),len(rt2))
        
diff = plot.rt_minus_rt_plot(rt1, rt2)

#Checking the maximum rt difference

diff.sort(key=float, reverse=True)

#print(diff)

#plot(rt1,diff,"RT difference for peaks matched by m/z, rt and MS2 spectra","","",False)

#spectra = sc.mgf_reader("multi1_ms2.MGF")






            
   
        
