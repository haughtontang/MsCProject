import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc
import random

def random_ms2(peak_list, mgf_path, mgf_path_otherfile):
              
    #This method is just for testing the optimization thing bellow
    
    #It will randomly assign MS2 spectrum objects to aligned peaksets in attempt to generate false +ves
    
    spectra1 = sc.mgf_reader(mgf_path)
    spectra2 = sc.mgf_reader(mgf_path_otherfile)
    
    id_1 = []
    
    for i in spectra1:
        
        key = i.feature_id
        
        id_1.append(key)
     
    id_2 = []    
     
    for j in spectra2:
        
        key = j.feature_id
        
        id_2.append(key)
        
    lim1 = len(id_1)
    lim2 = len(id_2)
    
    for peak in peak_list:
        
        if peak.get_file() == 'multi 1 ms2.csv':
            
            index = random.randint(0, lim1-1)
            
            new_id = id_1[index]
            
            peak.id = new_id
            
        else:
            
            index2 = random.randint(0, lim2-1)
            
            new_id2 = id_2[index2]
            
            peak.id2 = new_id2
        
def check_correction_quality(list_of_peaksets):
    
    '''
    Parameters
    ----------
    list_of_peaksets : List of peakset objects
    
    DESCRIPTION: Loops through the list and calculate the similarity score of the
    MS2 spectra objects contained in the PS. These scores are then appended to a list
    and returned at the end. 

    Returns
    -------
    scores : List of floats
    '''
    
    scores = []
    
    for sets in list_of_peaksets:
            
        #We're only looking to compare matched peaksets so look for peaksets having >1 peaks making up the peakset
        
        if len(sets.peaks) > 1:
            
            #Empty list to store the spectrum objects that are an attribute of Peak objects
            
            ms2 = []
            
            #Loop over the peak list in peakset
        
            for peak in sets.peaks:
                
                #Not all peak objects have an ms2 attrbute so this checks for those that do
                
                if peak.ms2 != None:
                    
                    #If one is found add it to the ms2 list
                    
                    ms2.append(peak.ms2)
            
            '''
            Of the matched peaks, some may have an ms2 spectrum whilst the others dont, by ensuring
            that the ms list is larger than 1 and there are no null values we can check the similarity
            score of both the spectra
            '''
            
            if len(ms2) > 1:
                
                '''
                The function that checks the similarity takes a list of spectrum objects
                As its argument and returns a similarity score
                If this score is above the treshold then the peaks match on m/z,rt and ms2-
                Append that peakset to the list at the beginning of the function
                '''
                
                spectra_similarity = sc.similarity_score(ms2)
                
                scores.append(spectra_similarity)
                
    return scores
    

def randomize_ms2(mgf_path, mgf_path_otherfile, peakset_list):
    '''
    Parameters
    ----------
    mgf_path : File path to an mgf file corresponding to a picked peak file
    mgf_path_otherfile : mgf file path corresponding to a seperate picked peak file
    peakset_list : List of peakset objects
    
    DESCRIPTION: The function will extract peaksets that have greater than 1
    peak into a seperate list. 2 lists of spectrum objects are created using the 
    file paths. By using a random number generator and looping over the extarcted
    list of peaksets; the function randomly assigns ms2 spectrum objects to the
    peaks contained within the peakset.

    By doing this only on matching peaksets, we are able to increase the rate
    of a false +ve being generated.
    
    Returns
    -------
    The same list of peaksets provided in the argument but with randomized 
    ms2 spectra.
    '''

    spectra1 = sc.mgf_reader(mgf_path)
    spectra2 = sc.mgf_reader(mgf_path_otherfile)
    
    index1 = random.randint(0,len(spectra1))
    index2 = random.randint(0,len(spectra2))
    
    for i in peakset_list:
        
        if len(i.peaks) > 1:
        
            for j in i.peaks:
                
                index1 = random.randint(0,len(spectra1)-1)
                index2 = random.randint(0,len(spectra2)-1)
                
                if j.get_file() =='multi 1 ms2.csv':
        
                    j.ms2 = spectra1[index1]
                    
                else:
                    
                    j.ms2 = spectra2[index2]
                    
    return peakset_list

def check_correction_quality(list_of_peaksets):
    
    '''
    Parameters
    ----------
    list_of_peaksets : List of peakset objects
    
    DESCRIPTION: Loops through the list and calculate the similarity score of the
    MS2 spectra objects contained in the PS. These scores are then appended to a list
    and returned at the end. 

    Returns
    -------
    scores : List of floats
    '''
    
    scores = []
    
    for sets in list_of_peaksets:
            
        #We're only looking to compare matched peaksets so look for peaksets having >1 peaks making up the peakset
        
        if sets.number_of_peaks > 1:
            
            #Empty list to store the spectrum objects that are an attribute of Peak objects
            
            ms2 = []
            
            #Loop over the peak list in peakset
        
            for peak in sets.peaks:
                
                #Not all peak objects have an ms2 attrbute so this checks for those that do
                
                if peak.ms2 != None:
                    
                    #If one is found add it to the ms2 list
                    
                    ms2.append(peak.ms2)
            
            '''
            Of the matched peaks, some may have an ms2 spectrum whilst the others dont, by ensuring
            that the ms list is larger than 1 and there are no null values we can check the similarity
            score of both the spectra
            '''
            
            if len(ms2) > 1:
                
                '''
                The function that checks the similarity takes a list of spectrum objects
                As its argument and returns a similarity score
                If this score is above the treshold then the peaks match on m/z,rt and ms2-
                Append that peakset to the list at the beginning of the function
                '''
                
                spectra_similarity = sc.similarity_score(ms2)
                
                scores.append(spectra_similarity)
                
    return scores



multi1 = um.peak_creator('multi 1 ms2.csv')
multi2 = um.peak_creator('multi 2 ms2.csv')


i = 0

while i < 1000:

    #Sort by intensity

    multi1.sort(key = lambda x: x.intensity)
    multi2.sort(key = lambda x: x.intensity)
    
    random_ms2(multi1,"multi1_ms2.MGF","multi2_ms2.MGF")
    random_ms2(multi2,"multi1_ms2.MGF","multi2_ms2.MGF")
        
    um.assign_ms2("multi1_ms2.MGF", multi1)
    um.assign_ms2("multi2_ms2.MGF", multi2)
    
    pps = ps.align(multi1, multi2,1.5)
    
    #Create peakset objects from this alignment
    
    peaksets = ps.make_peaksets(pps)
    
    ms2_peaksets = ps.ms2_comparison(peaksets, 0)
    
    scores = check_correction_quality(peaksets)
    
    zero_count = 0
    
    low_count = 0
    
    for i in scores:
        
        if i == 0:
            
            zero_count+=1
            
        if i < 0.9:
            
            low_count+=1
    
    print("Random PS num: ", len(peaksets))
    
    print("Random MS2 num: ", len(ms2_peaksets))
    
    print("Low num: ", low_count)
    
    print("Zero num: ", zero_count)
    
    #print(scores)
    
    if zero_count != 0:
        
        break
    
    multi1 = um.peak_creator('multi 1 ms2.csv')
    multi2 = um.peak_creator('multi 2 ms2.csv')
    
    i +=1


'''
#Testing for normal circumstances

multi1 = um.peak_creator('multi 1 ms2.csv')
multi2 = um.peak_creator('multi 2 ms2.csv')

#Sort by intensity

multi1.sort(key = lambda x: x.intensity)
multi2.sort(key = lambda x: x.intensity)

um.assign_ms2("multi1_ms2.MGF", multi1)
um.assign_ms2("multi2_ms2.MGF", multi2)

pps = ps.align(multi1, multi2,1.5)
    
#Create peakset objects from this alignment

peaksets = ps.make_peaksets(pps)

ms2_peaksets = ps.ms2_comparison(peaksets, 0)

print("Normal PS num: ", len(peaksets))

print("Normal MS2 num: ", len(ms2_peaksets))
 
 '''

'''              
peaksets2 = randomize_ms2("multi1_ms2.MGF","multi2_ms2.MGF", peaksets)
        
scores = check_correction_quality(peaksets2)

num_ms2_matches = len(scores)

low = 0
zero = 0
for i in scores:
    
    if i < 0.9:
        
        low +=1
        
    if i ==0:
        
        zero+=1
        
print("Total Random MS2 matches: ", num_ms2_matches)
print("Number of low scores: ", low)
print("Number of zero scores: ", zero)
'''

    

        