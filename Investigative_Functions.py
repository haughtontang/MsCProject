# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 13:15:29 2020

@author: Don Haughton
"""

from peak_tools import PeakSet as ps
import useful_functions as um
import matplotlib.pyplot as plt
import similarity_calc as sc


def get_matched(peakset):
    '''
    Parameters
    ----------
    peakset : list of peakset objects
    DESCRIPTION: Will take the list given and look exclusviely for peaksets
    that contain more than 1 peak and return a list of peaksets meeting this
    condition. 

    Returns
    -------
    matched : list of peakset objects with >1 peaks

    '''
    
    matched = []
    
    for i in peakset:
        
        if i.number_of_peaks >1:
            
            matched.append(i)

    return matched

def get_names(peaksets):
    '''
    Parameters
    ----------
    peaksets : list of peakset objects
    
    DESCRIPTION: loops through the list of peaks in the peakset
    objects and gets the file names that the peaks originated from

    Returns
    -------
    List of sorted file names for all files used to create the peaksets

    '''
    
    names =[]
        
    for peakset in peaksets:
        
        #loop over lists in peakset
        
        for peak in peakset.get_peaks():
            
            name = peak.get_file()
            
            names.append(name)
        
    #make the names list only contain unique names
    
    names = list(set(names))
    
    #Sort so the first file is first in the list
    
    names.sort()
    
    return names

def get_matched_ids(peaksets):
    '''
    Parameters
    ----------
    peaksets : list of peakset objects
    DESCRIPTION: loops over the peaks in the peaksets that have > 1 peaks and
    extracts the ids from those peaks into 2 lists
    Returns
    -------
    id_list1 : list of ids from file 1
    id_list2 : list of ids from file 2

    '''
    
    #Get matched peaksets only
    
    matched = get_matched(peaksets)
    
    #Empty lists to append to
    
    id_list1 = []
    id_list2 = []
    
    #Need to get the names of the files so that the ID from the appropriate 
    #file can go to the proper list
    
    names = get_names(peaksets)
    
    #Loop over the matched peaksets
    
    for i in matched:

         for j in i.get_peaks():

             #use the file name at the first index

             if j.file == names[0]:

                 key = j.get_id()
                
                 id_list1.append(key)
             
             #if its not equal then it must have come from the other file, append there   
             
             else:
                
                 key = j.get_id()
                
                 id_list2.append(key)
    
    #return the ID lists             
    
    return id_list1, id_list2

def get_ids(peaksets):
    '''
    Parameters
    ----------
    peaksets : list of peakset objects
    DESCRIPTION: loops over the peaks in the peaksets and
    extracts the ids from those peaks into 2 lists
    Returns
    -------
    id_list1 : list of ids from file 1
    id_list2 : list of ids from file 2
    '''
    
    id_list1 = []
    id_list2 = []
    
    #Need to get the names of the files so that the ID from the appropriate 
    #file can go to the proper list
    
    names = get_names(peaksets)
    
    #Loop over the matched peaksets
    
    for i in peaksets:

         for j in i.get_peaks():

             #use the file name at the first index

             if j.file == names[0]:

                 key = j.get_id()
                
                 id_list1.append(key)
             
             #if its not equal then it must have come from the other file, append there   
             
             else:
                
                 key = j.get_id()
                
                 id_list2.append(key)
    
    #return the ID lists             
    
    return id_list1, id_list2
 
    
def numbers_added(peaksets, corrected_peaksets):
   '''
   Parameters
   ----------
   peaksets : list of peakset objects pre correction
   corrected_peaksets : list of peakset objects post correction
   DESCRIPTION: By using the IDs of the peaksets before and after correction
   and looking at what is missing/added we can determine which peaksets were added
   which were not previously
   Returns
   -------
   None.

   '''
    
   #Since IDs and file names uniquely identify peaks within a peakset, use those to tell the difference
    
   #Pre correction
    
   id_list1, id_list2 = get_matched_ids(peaksets)
   
   #post correction
   
   corrected_id_list1, corrected_id_list2 =  get_matched_ids(corrected_peaksets)
           
   #Find the differences between the lists
    
   differences_file1 = []
   
   '''
   If the ID of a peak in corrected peakset is not in the 
   ID list of the peaks pre correction then it has been newly added and appended
   to the differences list. These lists are dealing with peaks exclusively from file 1
   '''
   
   for i in corrected_id_list1:
        
       if i not in id_list1:
            
           differences_file1.append(i)
            
   differences_file2 = []
   
   #Exact same as a above except these are done for the differences between file 2 pre and post correction
   
   for i in corrected_id_list2:
        
       if i not in id_list2:
            
           differences_file2.append(i)
                
   print("There are %s newly created peakset pairs that weren't present before correction" % len(differences_file1)) 
   
   #Using length of the lists we can also determine how many peaksets were removed
   
   number_removed = len(corrected_peaksets) - (len(peaksets) - len(differences_file1))

   print("There were %s peaksets removed from the original list after correction" % number_removed)
   
   #get numbers for ms2
   
   #Make seperate peakset lists for both conditions but this time only consisting of 
   #Peaksets that have matching ms2
   
   pre_ms2 = ps.ms2_comparison(peaksets,0)
   
   post_ms2 = ps.ms2_comparison(corrected_peaksets,0)

   #get the ids of these specific ms2 peaks that make up the peakset

   id_list1, id_list2 = get_matched_ids(pre_ms2)
     
   corrected_id_list1, corrected_id_list2 =  get_matched_ids(post_ms2)
   
   #Just as above, find the discrepencies between their ID numbers to find out 
   #How many were added and how many were removed
             
   differences_file1 = []
   
   '''
   If the ID of a peak in corrected peakset is not in the 
   ID list of the peaks pre correction then it has been newly added and appended
   to the differences list. These lists are dealing with peaks exclusively from file 1
   '''
   
   for i in corrected_id_list1:
        
       if i not in id_list1:
            
           differences_file1.append(i)
   
   #Same as above but for the second file        
   
   differences_file2 = []
    
   for i in corrected_id_list2:
        
       if i not in id_list2:
            
           differences_file2.append(i)
           
  
   print("There are %s newly created MS2 peakset pairs that weren't present before correction" % len(differences_file1)) 
   
   #get the differences by looking at the different numbers in the list
   
   number_removed = (len(pre_ms2) + len(differences_file1)) - len(post_ms2)

   print("There were %s MS2 peaksets removed from the original list after correction" % number_removed)
     
def plot_removed_ms2_ps_mz_diff(peaksets, id_list1, id_list2, corrected_id_list1, corrected_id_list2):
   '''
   Parameters
   ----------
   peaksets : list of peakset objects.
   id_list1 : list of IDs from the first file of peaks that make up the given peakset objects pre correction
   id_list2 : list of IDs from the second file of peaks that make up the given peakset objects pre correction
   corrected_id_list1 : list of IDs from the first file of peaks that make up the given peakset objects post correction
   corrected_id_list2 : list of IDs from the second file of peaks that make up the given peakset objects post correction

   DESCRIPTION: Similar to the methods used in numbers_added() it identifies the ids of the
   ms2 peaksets that were removed and uses these to recover the peak objects corresponding to
   the id in peaksets. The differnece in the m/z of these peaks is then plottet
   as a scatter plot, which is returned at the end of this function. 

   Returns
   -------
   None.

   '''
   
   #Get the peaks that were removed during correction
   
   removed1 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file1
   
   for i in id_list1:
       
       if i not in corrected_id_list1:
           
           removed1.append(i)
           
   removed2 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
   for i in id_list2:
       
       if i not in corrected_id_list2:
           
           removed2.append(i)
   
   #With the ids, I can extract the peaks into seperate lists of peaks by matching the ids in the list 
   
   tog_peaks1 = []
   tog_peaks2 = []
   
   #get the names of the files used
   
   names = get_names(peaksets)
   
   for i in peaksets:
       
       for j in i.get_peaks():
           
           #Use the origin file as well as ID to ensure the 2 files arent mixed, as they will share ID numbers
           
           if j.id in removed1 and j.file == names[0]:
               
               tog_peaks1.append(j)
               
           if j.id in removed2 and j.file == names[1]:
               
               tog_peaks2.append(j)
   
   #Make lists of mz values            
   
   mz1 = []
   mz2 = []
   
   #Loop over the peak lists and extract their mz values
   
   for i in tog_peaks1:
       
       mz1.append(i.get_mz())
       
   for i in tog_peaks2:
       
       mz2.append(i.get_mz())
   
   #plotting the difference between the 2 files will allow us to see if they are bordering the tolerance    
   
   mz_minus = um.subtract_attributes(mz1,mz2)
   
   #plot the results
   
   plt.scatter(mz2, mz_minus, c="#5E62F4", alpha=1)
   plt.show()
  
def plot_added_ms2_ps_mz_diff(peaksets, id_list1, id_list2, corrected_id_list1, corrected_id_list2):
   '''
   Parameters
   ----------
   peaksets : list of peakset objects.
   id_list1 : list of IDs from the first file of peaks that make up the given peakset objects pre correction
   id_list2 : list of IDs from the second file of peaks that make up the given peakset objects pre correction
   corrected_id_list1 : list of IDs from the first file of peaks that make up the given peakset objects post correction
   corrected_id_list2 : list of IDs from the second file of peaks that make up the given peakset objects post correction

   DESCRIPTION: Similar to the methods used in numbers_added() it identifies the ids of the
   ms2 peaksets that were added and uses these to recover the peak objects corresponding to
   the id in peaksets. The differnece in the m/z of these peaks is then plottet
   as a scatter plot, which is returned at the end of this function. 

   Returns
   -------
   None.

   '''
   #Get the peaks that were added during correction
   
   added1 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file1
   
   for i in corrected_id_list1:
       
       if i not in id_list1:
           
           added1.append(i)
              
   added2 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
   for i in corrected_id_list2:
       
       if i not in id_list2:
           
           added2.append(i)
           
   #With the ids, I can extract the peaks into seperate lists of peaks by matching the ids in the list 
   
   tog_peaks1 = []
   tog_peaks2 = []
   
   #get the names of the files used
   
   names = get_names(peaksets)
   
   for i in peaksets:
       
       for j in i.peaks:
           
           #Use the origin file as well as ID to ensure the 2 files arent mixed, as they will share ID numbers
           
           if j.id in added1 and j.file == names[0]:
               
               tog_peaks1.append(j)
               
           if j.id in added2 and j.file == names[1]:
               
               tog_peaks2.append(j)
   
   #Make lists of mz values            
   
   mz1 = []
   mz2 = []
   
   #Loop over the peak lists and extract their mz values
   
   for i in tog_peaks1:
       
       mz1.append(i.get_mz())
       
   for i in tog_peaks2:
       
       mz2.append(i.get_mz())
   
   #plotting the difference between the 2 files will allow us to see if they are bordering the tolerance    
   
   mz_minus = um.subtract_attributes(mz1,mz2)
   
   #Plot the difference
   
   plt.scatter(mz2, mz_minus, c="#5E62F4", alpha=1)
   plt.show() 
   
   
   
def get_mz_plot(peaksets):
    '''
    Parameters
    ----------
    peaksets : list of peakset objects
    DESCRIPTION: extarcts the peaks contained within the peakset,
    takes their mz values and plots the differences between them. This is
    only done for matched peaksets.
    Returns
    -------
    None
    '''
    
    #Dealing with matched only
    
    matched = get_matched(peaksets)
    
    #List of mz values to use
    
    mz1 = []
    
    mz2 = []
    
    #get the names of the files used
   
    names = get_names(peaksets)
    
    #Get the mz values of the peaks inside matched peaks
    
    for i in matched:
        
        for j in i.peaks:
        
            if j.get_file() == names[0]:
           
                mz1.append(j.get_mz())
            
            #If its not equal to that file it must be the other one
            
            else:
           
                mz2.append(j.get_mz())
   
    #plotting the difference between the 2 files will allow us to see if they are bordering the tolerance    
   
    mz_minus = um.subtract_attributes(mz1,mz2)
   
    plt.scatter(mz2, mz_minus, c="#5E62F4", alpha=1)
    plt.show() 

def get_reomoved_ms2_peaks(peaksets, corrected_peakset):
    
   '''
   Parameters
   ----------
   peaksets : list of peakset objects pre correction
   corrected_peakset : list of peakset objects post correction
   DESCRIPTION: By using the ID lists of the peakset provided in the argument
   The MS2 peaks that were removed during correction are found through use of these IDs. 
   From there the MS2 peaks that were removed have their m/z difference reexamined to determine
   if their removal was a mistake. If the difference is within a certain threshold, they are readded
   to the corrected peakset list as a matching peakset.
   Returns
   -------
   final_corrected_peaksets : list of peakset objects with the potential
   to contain added extra MS2 peaksets
   '''
    
   #Convert PS to ms2 ps
   
   ms2 = ps.ms2_comparison(peaksets, 0)
   corrected_ms2 = ps.ms2_comparison(corrected_peakset, 0)
    
   #Get normal id list
    
   id_list1, id_list2 = get_matched_ids(ms2)
    
   #Get corrected ID liss
    
   corrected_id_list1, corrected_id_list2 = get_matched_ids(corrected_ms2)
 
   #Get the peaks that were removed during correction from the first file
   
   removed1 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
   for i in id_list1:
       
       if i not in corrected_id_list1:
           
           removed1.append(i)
   
   #Get the peaks that were removed during correction from the second file        
   
   removed2 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
   for i in id_list2:
       
       if i not in corrected_id_list2:
           
           removed2.append(i)
   
   #With the ids, I can extract the peaks into seperate lists of peaks by matching the ids in the list 
   
   tog_peaks1 = []
   tog_peaks2 = []
   
   #get the names of the files used
   
   names = get_names(peaksets)
   
   for i in ms2:
       
       for j in i.peaks:
           
           #Use the origin file as well as ID to ensure the 2 files arent mixed, as they will share ID numbers
           
           if j.get_id() in removed1 and j.get_file() == names[0]:
               
               tog_peaks1.append(j)
               
           if j.get_id() in removed2 and j.get_file() == names[1]:
               
               tog_peaks2.append(j)
   
   '''
   Match the peakset together in a list in order to convert them
   from peaks to peaksets
   
   This will be required to ensure peaksets arent made from peaks that dont
   match
   '''
   
   recovered_ps = []
    
   for i in range(0, len(tog_peaks1)):
       
       '''
       Match the peaks in both lists at the respective index
       This will ensure that they are the peaks that match, as it'll match their extraction order from
       the list of peaksets and using the same index for the seperate lists ensures they're appended together
       '''
       
       peak_list = [tog_peaks1[i],tog_peaks2[i]]
       
       recovered_ps.append(peak_list)
   
   '''
   To increase the possibility that the removed ms2 peaksets are not false positives
   The mz tolerance has been lowered to what it would normally be during alignment
   
   The loop bellow will take the mz difference of 2 matched peaks and compare this difference
   to the new tolerance. If its greater than or less than the negative of this tolerance
   they will be removed from the list
   '''
   
   for i in recovered_ps:
       
       #List has 2 items per index so split these into seperate peak variables
       
       p1 = i[0]
       p2 = i[1]
       
       #Get the mz valies
       
       mz1 = p1.get_mz()
       mz2 = p2.get_mz()
       
       #Take the difference of the 2
       
       difference = mz1 - mz2
       
       #Imploy stricter tolerances to esnure they're the same
       
       limit = 0.00009
       
       #If its out of this range, delete it
       
       #Use the negative incase we arent dealing with positive numbers all the time
       
       if difference > limit or difference < (limit * -1):
           
           recovered_ps.remove(i)
               
   #convert to peaksets objects
   
   recovered_ps = ps.make_peaksets(recovered_ps)
   
   #now check the similairty score of their MS2 as a final QC
   
   for i in recovered_ps:
       
       #Unpack the peaks in the peakset object
      
        p1 = i.get_peaks()[0]
        p2 = i.get_peaks()[1]
        
        #access the ms2 spectra as part of these peaks
        
        spec1 = p1.get_ms2()
        spec2 = p2.get_ms2()
        
        #Append the spectra to a list
        
        spec_list = []
        spec_list.append(spec1)
        spec_list.append(spec2)
        
        #Get the spectra similarity score
        
        score = sc.similarity_score(spec_list)
        
        #Apply a stricter similarty threshold for these ms2 peaks
        
        if score < 0.97:
            
            #If it is bellow this threshold- remove it
            
            recovered_ps.remove(i)
   
   #To avoid dealing with file name, do it by indivudal peak
   
   #To do this, extract indiviudal peaks from the recovered list
   
   ms2_peaks = []
   
   #Get the indiviudal peaks from the list
   
   for i in recovered_ps:
       
       for j in i.peaks:
           
           ms2_peaks.append(j)
           
   #Remove the peaksets containing these peaks in the corrected list      
   
   for sets in corrected_peakset:
       
       #loop over the peaks in that peakset
       
       for peak in sets.get_peaks():
           
           #Equal to one as in the corrected list they will now be singlet peaksets
           
           if peak in ms2_peaks and sets.number_of_peaks ==1:
               
               #remove that peakset from the list
               
               corrected_peakset.remove(sets)
                          
   #with the singlets remove, can now append the lost MS2 peaksets
   
   final_corrected_peaksets = corrected_peakset + recovered_ps
   
   #Return an updated corrected PS list
   
   return final_corrected_peaksets







