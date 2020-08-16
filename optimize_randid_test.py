import GPy
from peak_tools import PeakSet as ps
import useful_functions as um
import numpy as np
import similarity_calc as sc
import random

def random_ms2(peak_list):
    '''
    Parameters
    ----------
    peak_list : List: a list of peak objects BEFORE assigning their MS2 spectra
    DESCRIPTION: Loop loop through the given list and assign that peak a random id
    number between 1 and the length of the list. This ensures that MS2 spectra are
    randomly assigned as they are aligned by matching spectrum IDs to peak ids
    Returns
    -------
    None.

    '''
    #This method is just for testing the optimization function bellow
    
    #It will randomly assign MS2 spectrum objects to aligned peaksets in attempt to generate false +ves
    
    random_list = []
    
    #Get the mximum number for the random generator
    
    limit = len(peak_list)
    
    #Make a list of random numbers
    
    for i in range(0, limit):
        
        n = random.randint(0,limit)
        
        random_list.append(n)
    
    '''
    Loop through the list of peaks given in the argument and using another 
    random num generator, access a random index in the list of random numbers
    and use its value to replace the existing peak ID. At the end, every peak in the list 
    will have a new ID, generated randomly.
    '''
    
    for peak in peak_list:
        
        index = random.randint(0, limit-1)
        
        new_id = random_list[index]
        
        peak.id = new_id

#Another randomization method
        
def randomize_ms2(mgf_path, mgf_path_otherfile, peakset_list):
    '''
    Parameters
    ----------
    mgf_path : String: File path to an mgf file corresponding to a picked peak file
    mgf_path_otherfile : String: mgf file path corresponding to a separate picked peak file
    peakset_list : List of peakset objects
    
    DESCRIPTION: The function will extract peaksets that have greater than 1
    peak into a separate list. 2 lists of spectrum objects are created using the 
    file paths. By using a random number generator and looping over the extracted
    list of peaksets; the function randomly assigns ms2 spectrum objects to the
    peaks contained within the peakset.

    By doing this only on matching peaksets, we can increase the rate
    of a false +ve being generated.
    
    Returns
    -------
    The same list of peaksets provided in the argument but with randomized 
    ms2 spectra.
    '''

    #Create 2 lists of spectra objects using the file paths    

    spectra1 = sc.mgf_reader(mgf_path)
    spectra2 = sc.mgf_reader(mgf_path_otherfile)
    
    #Loop over the list of peaksests
    
    for i in peakset_list:
        
        #Only access those that are matched
        
        if i.number_of_peaks > 1:
        
            #loop over the list of peaks as part of PS    
        
            for j in i.get_peaks():
                
                #Generate a random index to be used
                
                index1 = random.randint(0,len(spectra1)-1)
                index2 = random.randint(0,len(spectra2)-1)
                
                #Ensures that the correct spectra is applied to its pairing file
                
                if j.get_file() =='multi 1 ms2.csv':
        
                    j.set_ms2(spectra1[index1])
                
                #If it doesnt match this condition then it must be from the other file
                #Use the other list for the random re assignment
                
                else:
                    
                     j.set_ms2(spectra2[index2])
                    
    return peakset_list

#Methods bellow mirror those used in optimization.py with slight changes made for testing purposes

def find_best_hypparams(filepath_to_match, filepath_to_correct, mgf_path1, mgf_path2):
    '''
    Parameters
    ----------
    filepath_to_match : File path to picked peak file
    filepath_to_correct : File path to another picked peak file
    mgf_path1 : file path to the corresponding mfg file of the first picked peak file
    mgf_path2 : file path to the corresponding mfg file of the second picked peak file
    
    DESCRIPTION: assesses various variance and length scale values and return the optimum
    kernel parameters based on the number of peaksets generated post correction, and the
    quality of their ms2 similarity scores
    
    An alteration on the original file for the purposes of testing. There is 
    an increased LS range to assess some extreme params. The results list is also returned
    at the end of this method
    
    Returns
    -------
    results: list of tuples
    '''
    
    #variance values
    
    variance = [1,2.5,7.5,10]
    
    #get ls values
    
    ls = []
    
    initial_ls = 30.0
    
    ls.append(initial_ls)
    
    #More extreme range used to assess how this affects correction
    
    while initial_ls < 1000:
        
        #Incrmeentation used to get a good range of values
        
        initial_ls = (initial_ls /1.2) * 1.5
        
        initial_ls = round(initial_ls, 2)
        
        ls.append(initial_ls)
        
    #Appended recorded results
        
    results = []

    #Nested loop bellow will test every variance value against eveery ls value to find the best results

    for v in variance:
        
        for leng in ls:
            
            '''
            As this test is to identify false positives, we want to get the peakset numbers under
            normal conditions and record these as well as those corrected
            
            later these steps will be repeated but with the random tests
            '''

            #Creating the Peak objects and assigning their MS2 spectra

            peak1 = um.peak_creator(filepath_to_match)
            peak2 = um.peak_creator(filepath_to_correct)
            
            um.assign_ms2(mgf_path1, peak1)
            um.assign_ms2(mgf_path2, peak2)
            
            #Align and make peaksets
        
            align = ps.align(peak1, peak2,1.5)
            
            #Make peaksets
            
            peaksets = ps.make_peaksets(align)
            
            #Make anchors
            
            anchors = ps.ms2_comparison(peaksets, 0.9)
    
            #Get the rt list of the anchors
    
            rt1, rt2 = um.rt_extraction(anchors)
            
            #Subtract the 2 attributes
            
            rt_minus = um.subtract_attributes(rt1, rt2)
            
            #get the time in peak2
            
            all_time = um.rt_extraction(peak2)
            
            #Convert to numpy arrays    
            
            all_time = np.array(all_time).reshape(len(all_time),1)
            X = np.array(rt2).reshape(len(rt2),1)
            Y = np.array(rt_minus).reshape(len(rt_minus),1)
            
            #Make a kernel using these params
            
            #Set up kernel and model objects using Gpy
            
            #Variance and lengthscale values from the for loops are used
            
            kernel = GPy.kern.RBF(input_dim=1, variance= v, lengthscale= leng)
            m = GPy.models.GPRegression(X,Y, kernel = kernel)    

            #Store the mean and variance predicitons from the model. The times extracted from the file_to_corect are passed to this function
            
            mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
            
            #convert from np array to list
            
            mean = list(mean.flatten())
            
            #This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model
            
            um.correct_rt(peak2, mean)
            
            #Align again
            
            corrected_align = ps.align(peak1, peak2, 1.5)
            
            corrected_peaksets = ps.make_peaksets(corrected_align)
            
            #get the number of corrected peaksets
            
            num_corrected = len(corrected_peaksets)
            
            #MS2 numbers
            
            corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)
            
            #get ms2 num
            
            ms2_num = len(corrected_ms2)
            
            #Used as counters for the number of low and zero scores generated after correction
            
            low_score_count = 0
            
            zero_score_count = 0
            
            #Get correction scores for all MS2 spectra aligned and find if there are any of low quality
            
            corrected_scores = check_correction_quality(corrected_ms2)
            
            #Loops over the scores generated by the method above and checks the scores
            
            for score in corrected_scores:
                
                if score < 0.9:
                    
                    low_score_count+=1
                    
                if score == 0:
                    
                    zero_score_count+=1

            #reset everything for the randomization test 
            
            peak1 = um.peak_creator(filepath_to_match)
            peak2 = um.peak_creator(filepath_to_correct)
            
            #Uncomment bellow if using the random ID method
            
            #random_ms2(peak1)
            #random_ms2(peak2)
            
            #Assign ms2 spectra
            
            um.assign_ms2(mgf_path1, peak1)
            um.assign_ms2(mgf_path2, peak2)
            
            #We already have the correction predicitons so no need to do that again
            
            um.correct_rt(peak2, mean)
            
            #Align again after the correction of peak2
            
            rand_corrected_align = ps.align(peak1, peak2, 1.5)
            
            rand_corrected_peaksets = ps.make_peaksets(rand_corrected_align)
            
            #uncomment bellow if using the randomize by spectra randomization method
            
            #rand_corrected_peaksets = randomize_ms2(mgf_path1, mgf_path2, rand_corrected_peaksets)
            
            #get the number of corrected using the random method
            
            rand_num_corrected = len(corrected_peaksets)
            
            #MS2 numbers after randomization, the limit bellow is set to -1 to ensure zero scores are 
            #included as this method looks for scores GREATER than the threshold passed to the argument
            
            rand_corrected_ms2 = ps.ms2_comparison(rand_corrected_peaksets, -1)
            
            #append as a seperate variable
            
            rand_ms2_num = len(rand_corrected_ms2)
            
            '''
            Check the correction quality as was done above by getting the similarity scores
            of all ms2 peaksets generated after randomization and finding out how many
            low and zero scores there are
            '''
            
            rand_low_score_count = 0
            
            rand_zero_score_count = 0
            
            #Get correction scores for all MS2 spectra aligned and find if there are any of low quality
            
            rand_corrected_scores = check_correction_quality(rand_corrected_ms2)
            
            for score in rand_corrected_scores:
                
                if score < 0.9:
                    
                    rand_low_score_count+=1
                    
                if score == 0:
                    
                    rand_zero_score_count+=1
                    
            #record the results in a tuple
            
            tup = (v, leng, 1.5, num_corrected, ms2_num, rand_num_corrected, rand_ms2_num, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count)
            
            #Append this to the empty results list at the begining
            
            results.append(tup)
            
    #sort the list in ascending order by number of peaksets generated
    
    results.sort(key=lambda tup: tup[3])
    
    '''
    In this test version, there is no need to sort the list any further as we're not
    returning anything at the end of it, we only want to check the randomization effects
    of ms2 spectra so that step has been omitted. 
    '''

    #Return the results to be written to a file
    
    return results
            
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
            Of the matched peaks, some may have an ms2 spectrum whilst the others don't, by ensuring
            that the ms list is larger than 1 and there are no null values we can check the similarity
            score of both the spectra
            '''
            
            if len(ms2) > 1 and None not in ms2:
                
                '''
                The function that checks the similarity takes a list of spectrum objects
                As its argument and returns a similarity score
                If this score is above the threshold then the peaks match on m/z, rt and ms2-
                Append that peakset to the list at the beginning of the function
                '''
                
                spectra_similarity = sc.similarity_score(ms2)
                
                scores.append(spectra_similarity)
                
    return scores


#Call the function and get the results

resu = find_best_hypparams('multi 1 ms2.csv', 'multi 2 ms2.csv',"multi1_ms2.MGF","multi2_ms2.MGF")

#empty list to append to

file = []

'''
The loop below will go through the list of tuples generated from the function
unpack each tuple into component variables
convert these to strings and given labels so they can be easily written to a file and read
and append these to the file list above
'''

for i in resu:
    
    v, leng, time, num_corrected, ms2_num, rand_num_corrected, rand_corrected_ms2, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count = i

    line = "var: ", str(v), "Lengthscale: ", str(leng), "RT Tole", str(time), "PS num: " ,str(num_corrected), "MS2 PS: ", str(ms2_num), "Rand ps num: ", rand_num_corrected, "rand #ms2: ", rand_corrected_ms2 ,"Normal Scores < 0.9: ", str(low_score_count),"rand Scores < 0.9: ", str(rand_low_score_count),"Normal Scores = 0: ", str(zero_score_count),"rand Scores = 0: ", str(rand_zero_score_count)
    file.append(line)
 
#Write the file list above to file. This is a representation of all parameters
#tested in the find_best_hypparams function    
 
with open('Rand ID for ms2 test 3.txt', 'w') as f:
    for item in file:
        line = str(item)
        f.write(line)
        f.write("\n")
