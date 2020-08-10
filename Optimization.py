import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc

def find_best_hyperparameters(filepath_to_match, filepath_to_correct, mgf_path1, mgf_path2):
    '''
    Parameters
    ----------
    filepath_to_match : File path to picked peak file
    filepath_to_correct : File path to another picked peak file
    mgf_path1 : file path to the corresponding mfg file of the first picked peak file
    mgf_path2 : file path to the corresponding mfg file of the second picked peak file
    
    DESCRIPTION: assesses various variance and length scale values and return the optimum
    kernel parameters based on the number of peaksets generated post correction, and the
    quality of their ms2 similairty scores
    
    Returns
    -------
    best_var : Float: best variance value
    best_ls : Float: best ls value
    '''
    
    #variance values
    
    variance = [1,2.5,5,7.5,10]
    
    #get ls values
    
    ls = []
    
    #Start at 30 as lower values dont optimize well
    
    initial_ls = 30.0
    
    ls.append(initial_ls)
    
    '''
    A more extreme range of ls values was explored udring testing
    however above the 150 the mean line will flatten- such a result also
    isnt optimizing anything so this range was chosen
    '''
    
    while initial_ls < 150:
        
        initial_ls = (initial_ls /1.2) * 1.5
        
        #The floats this produces can be quite long so to keep things neater the value is rounded
        
        initial_ls = round(initial_ls, 2)
        
        ls.append(initial_ls)
        
    #Appended recorded results
        
    results = []
    
    #Nested loop bellow will test every variance value against eveery ls value to find the best results
    
    for v in variance:
        
        for leng in ls:
            
            #Creating the Peak objects and assigning their MS2 spectra

            peak1 = um.peak_creator(filepath_to_match)
            peak2 = um.peak_creator(filepath_to_correct)
            
            um.assign_ms2(mgf_path1, peak1)
            um.assign_ms2(mgf_path2, peak2)
            
            #Sort by intensity
            
            peak1.sort(key = lambda x: x.intensity)
            peak2.sort(key = lambda x: x.intensity)
            
            #Align and make peaksets
            
            align = ps.align(peak1, peak2,1.5)
            
            peaksets = ps.make_peaksets(align)
            
            #Create anchors
            
            anchors = ps.ms2_comparison(peaksets, 0.9)
            
            #Extract RT values from the peaks
            
            rt1, rt2 = plot.rt_extract_convert(anchors)
            
            rt_minus = plot.rt_minus_rt_plot(rt1, rt2)
            
            #get the time in peak2
            
            all_time = []
            
            for peak in peak2:
                
                time = peak.get_rt()
                
                all_time.append(time)
            
            #Convert to numpy arrays    
            
            all_time = np.array(all_time).reshape(len(all_time),1)
            X = np.array(rt2).reshape(len(rt2),1)
            Y = np.array(rt_minus).reshape(len(rt_minus),1)
            
            #Make a kernel using these params
            
            #Set up kernel and model objects using Gpy
            
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
            
            #get the number of peaksets
            
            num_corrected = len(corrected_peaksets)
            
            #MS2 numbers- threshold has to be set to -1 so that negative 0 scoring spectra can be detected
            
            corrected_ms2 = ps.ms2_comparison(corrected_peaksets, -1)
            
            #get ms2 num
            
            ms2_num = len(corrected_ms2)
            
            #Counter flags to track the correction quality
            
            low_score_count = 0
            
            zero_score_count = 0
            
            #Get correction scores for all MS2 spectra aligned and find if there are any of low quality
            
            corrected_scores = check_correction_quality(corrected_ms2)
            
            #Loop over the scores and count the low scoring and zero scoring pairs
            
            for score in corrected_scores:
                
                if score < 0.9:
                    
                    low_score_count+=1
                    
                if score == 0:
                    
                    zero_score_count+=1
                    
            #record the results
            
            tup = (v, leng, num_corrected, ms2_num, low_score_count, zero_score_count)
            
            results.append(tup)
            
    #sort the list
    
    results.sort(key=lambda tup: tup[2])

    #Based on MS2 correction quality this function will get the best var and ls values

    best_var, best_ls = picking_best_results(results)
    
    return best_var, best_ls 
            
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
            
            if len(ms2) > 1 and None not in ms2:
                
                '''
                The function that checks the similarity takes a list of spectrum objects
                As its argument and returns a similarity score
                If this score is above the treshold then the peaks match on m/z,rt and ms2-
                Append that peakset to the list at the beginning of the function
                '''
                
                spectra_similarity = sc.similarity_score(ms2)
                
                scores.append(spectra_similarity)
                
    return scores

def picking_best_results(results_list):
    '''
    Parameters
    ----------
    results_list : List of tuples
    
    DESCRIPTION: THis function is a helper function designed to be used in
    conjunction with the find_best_hyperparameters function above. It takes the list of results
    generated in the function and sorts them based on the number of peaksets generated
    and finds the best parameters best on the ms2 quality of the corrected peaksets
    Returns
    -------
    Float: variance value
    Float: length scale value
    '''
    
    #Get the best results of the data
    
    top_result = results_list[0]
    
    #unpack best results
    
    variance, lengthscale, ps, ms2, low, zero = top_result
    
    best_results = []
    
    #Make a list of best results based on number of ps generated
    
    for res in results_list:
        
        #If its equal to the best result or within 10 peaks of it
        
        peak_range = ps + 10
        
        boolean_check = res[2] <= ps and res[2] <= peak_range
        
        if res[2] == ps or boolean_check == True:
            
            best_results.append(res)
    
    #sort this list on the number of ms2 peaksets generated        
    
    best_results.sort(key=lambda tup: tup[3])

    #Take the best result of this list

    best = best_results[0]
    
    #Unpack it
    
    best_v, best_ls, best_ps, best_ms2, best_low, best_zero = best
            
    #remove results from the best list
    
    for i in best_results:
        
        if i[3] < best_ps or i[4] > best_low or i[5] > best_zero:
            
            best_results.remove(i)
         
    best_var = []
    best_leng = []
    
    #Get the best var and ls values if the list of the best is >1
    
    for top in best_results:
        
        #inpack the values in the tuple
        
        v, ls, p, m, l, z = top
        
        best_var.append(v)
        best_leng.append(ls)
    
    #Sort the list and return the highest results of the the var and ls    
    
    best_var.sort(key=float, reverse = True)
    best_leng.sort(key=float)

    return best_var[0], best_leng[0]
