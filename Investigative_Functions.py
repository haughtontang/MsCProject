# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 13:15:29 2020

@author: Don Haughton
"""

from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import matplotlib.pyplot as plt
import SimilarityCalc as sc


def get_matched(peakset):
    
    matched = []
    
    for i in peakset:
        
        if i.number_of_peaks >1:
            
            matched.append(i)
            
    print("Number of peaksets containing 2 peaks = " , len(matched))
    
    return matched

def get_matched_ids(peaksets):
    
    matched = get_matched(peaksets)
    
    id_list1 = []
    id_list2 = []
    
    for i in matched:

         for j in i.peaks:
            
             if j.file == "multi 1 ms2.csv":

                 key = j.id
                
                 id_list1.append(key)
                
             else:
                
                 key = j.id
                
                 id_list2.append(key)
                 
    return id_list1, id_list2

def get_ids(peakset):
    
    id_list1 = []
    id_list2 = []
    
    for i in matched:

         for j in i.peaks:
            
             if j.file == "multi 1 ms2.csv":

                 key = j.id
                
                 id_list1.append(key)
                
             else:
                
                 key = j.id
                
                 id_list2.append(key)
                 
    return id_list1, id_list2
 
    
def numbers_added(peaksets, corrected_peaksets):
    
    #Since IDs and file names uniquely identift peaks within a peakset, use those to tell the difference
    
    #Pre correction
    
   id_list1, id_list2 = get_matched_ids(peaksets)
     
   corrected_id_list1, corrected_id_list2 =  get_matched_ids(corrected_peaksets)
           
   #Find the differences between the lists
    
   differences_file1 = []
    
   for i in corrected_id_list1:
        
       if i not in id_list1:
            
           differences_file1.append(i)
            
   differences_file2 = []
    
   for i in corrected_id_list2:
        
       if i not in id_list2:
            
           differences_file2.append(i)
           
   #plot_added_ms2_ps_mz_diff(peaksets, id_list1, id_list2, corrected_id_list1, corrected_id_list2)
            
   print("There are %s newly created peakset pairs that weren't present before correction" % len(differences_file1)) 


   number_removed = len(corrected_peaksets) - (len(peaksets) - len(differences_file1))

   print("There were %s peaksets removed from the original list after correction" % number_removed)
   
   #get numbers for ms2
   
   pre_ms2 = ps.ms2_comparison(peaksets,0)
   
   post_ms2 = ps.ms2_comparison(corrected_peaksets,0)

   id_list1, id_list2 = get_matched_ids(pre_ms2)
     
   corrected_id_list1, corrected_id_list2 =  get_matched_ids(post_ms2)
                
   differences_file1 = []
    
   for i in corrected_id_list1:
        
       if i not in id_list1:
            
           differences_file1.append(i)
            
   differences_file2 = []
    
   for i in corrected_id_list2:
        
       if i not in id_list2:
            
           differences_file2.append(i)
   #plot_added_ms2_ps_mz_diff(peaksets, id_list1, id_list2, corrected_id_list1, corrected_id_list2)         
   print("There are %s newly created MS2 peakset pairs that weren't present before correction" % len(differences_file1)) 

   number_removed = (len(pre_ms2) + len(differences_file1)) - len(post_ms2)

   print("There were %s MS2 peaksets removed from the original list after correction" % number_removed)
   

  
def plot_removed_ms2_ps_mz_diff(peaksets, id_list1, id_list2, corrected_id_list1, corrected_id_list2):
    
 
   #Get the peaks that were removed during correction
   
   removed1 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
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
   
   for i in peaksets:
       
       for j in i.peaks:
           
           #Use the origin file as well as ID to ensure the 2 files arent mixed, as they will share ID numbers
           
           if j.id in removed1 and j.file == "multi 1 ms2.csv":
               
               tog_peaks1.append(j)
               
           if j.id in removed2 and j.file == "multi 2 ms2.csv":
               
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
   
   mz_minus = plot.rt_minus_rt_plot(mz1,mz2)
   
   plt.scatter(mz2, mz_minus, c="#5E62F4", alpha=1)
   plt.show()
  
def plot_added_ms2_ps_mz_diff(peaksets, id_list1, id_list2, corrected_id_list1, corrected_id_list2):

   #Get the peaks that were added during correction
   
   added1 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
   for i in corrected_id_list1:
       
       if i not in id_list1:
           
           added1.append(i)
           
   print("added", len(added1))        
   added2 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
   for i in corrected_id_list2:
       
       if i not in id_list2:
           
           added2.append(i)
           
   print("added", len(added2))  
   #With the ids, I can extract the peaks into seperate lists of peaks by matching the ids in the list 
   
   tog_peaks1 = []
   tog_peaks2 = []
   
   for i in peaksets:
       
       for j in i.peaks:
           
           #Use the origin file as well as ID to ensure the 2 files arent mixed, as they will share ID numbers
           
           if j.id in added1 and j.file == "multi 1 ms2.csv":
               
               tog_peaks1.append(j)
               
           if j.id in added2 and j.file == "multi 2 ms2.csv":
               
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
   
   mz_minus = plot.rt_minus_rt_plot(mz1,mz2)
   
   plt.scatter(mz2, mz_minus, c="#5E62F4", alpha=1)
   plt.show() 
   
   
   
def get_mz_plot(peaksets):
    
    matched = get_matched(peaksets)
    
    mz1 = []
    
    mz2 = []
    
    for i in matched:
        
        for j in i.peaks:
        
            if j.get_file() == "multi 1 ms2.csv":
           
                mz1.append(j.get_mz())
           
            else:
           
                mz2.append(j.get_mz())
   
    #plotting the difference between the 2 files will allow us to see if they are bordering the tolerance    
   
    mz_minus = plot.rt_minus_rt_plot(mz1,mz2)
   
    plt.scatter(mz2, mz_minus, c="#5E62F4", alpha=1)
    plt.show() 
    
    return mz1, mz2

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
    
   corrected_id_list1, corrected_id_list2 = get_matched_ids(corrected_ms2)
 
   #Get the peaks that were removed during correction
   
   removed1 = []
   
   #Scan the id list and find what doesnt match, these represent the removed ms2 peaks in file2
   
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
   
   for i in ms2:
       
       for j in i.peaks:
           
           #Use the origin file as well as ID to ensure the 2 files arent mixed, as they will share ID numbers
           
           if j.id in removed1 and j.file == "multi 1 ms2.csv":
               
               tog_peaks1.append(j)
               
           if j.id in removed2 and j.file == "multi 2 ms2.csv":
               
               tog_peaks2.append(j)
   
   '''
   Match the peakset together in a list in order to convert them
   from peaks to peaksets
   '''
   
   recovered_ps = []
    
   for i in range(0, len(tog_peaks1)):
       
       #Match the peaks in both lists at the respective index
       
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
       
       #List has 2 items per index so split these into seperate variables
       
       p1 = i[0]
       p2 = i[1]
       
       #Get the mz valies
       
       mz1 = p1.get_mz()
       mz2 = p2.get_mz()
       
       difference = mz1 - mz2
       
       #Imploy stricter tolerances to esnure they're the same
       
       limit = 0.00009
       
       #If its out of this range, delete it
       
       if difference > limit or difference < (limit * -1):
           
           recovered_ps.remove(i)
               
   #convert to peaksets objects
   
   recovered_ps = ps.make_peaksets(recovered_ps)
   
   #now check the similairty score as a final QC
   
   for i in recovered_ps:
       
       #Unpack the peaks in the peakset object
      
        p1 = i.peaks[0]
        p2 = i.peaks[1]
        
        #access the ms2 spectra as part of these peaks
        
        spec1 = p1.ms2
        spec2 = p2.ms2
        
        #Append the spectra to a list
        
        spec_list = []
        spec_list.append(spec1)
        spec_list.append(spec2)
        
        #Get the spectra similarity score
        
        score = sc.similarity_score(spec_list)
        
        #Apply a stricter similarty threshold for these ms2 peaks
        
        if score < 0.97:
            
            #Ifit is bellow this threshold- remove it
            
            recovered_ps.remove(i)
   
   #To avoid dealing with file name, do it by indivudal peak
   
   #To do this, extract indiviudal peaks from the recovered list
   
   ms2_peaks = []
   
   for i in recovered_ps:
       
       for j in i.peaks:
           
           ms2_peaks.append(j)
           
   #Remove the peaksets containing these peaks       
   
   for sets in corrected_peakset:
       
       #loop over the peaks in that peakset
       
       for peak in sets.peaks:
           
           #Equal to one as in the corrected list they will now be singlet peaksets
           
           if peak in ms2_peaks and sets.number_of_peaks ==1:
               
               #remove that peakset from the list
               
               corrected_peakset.remove(sets)
                          
   #with the singlets remove, can now append the lost MS2 peaksets
   
   final_corrected_peaksets = corrected_peakset + recovered_ps
   
   #Return an updated corrected PS list
   
   return final_corrected_peaksets







