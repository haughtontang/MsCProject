# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 12:50:15 2020

@author: Don Haughton
"""

'''
What do I need this method to do?

We need to have a set value for the LS then incrememnt that within some limit
Thats then used to make a kernel, then a model
That model makes predictions
the predictions are used to update the peak objects
they are aligned again
#ps and ls recorded
ls incrmeented and repeat 
'''

import GPy
from PeakTools import PeakSet as ps
from PeakTools import Plotter as plot
import UsefulMethods as um
import numpy as np
import SimilarityCalc as sc

def GP_optimization(filepath_to_match, filepath_to_correct, mgf_path1, mgf_path2, RT_tolerance):
    
    '''
    Parameters
    ----------
    filepath_to_match : Filepath to a picked peak files
    filepath_to_correct : Filepath to a different picked peak files
    mgf_path1 : Filepath to a file containg ms2 spectra, this path should match the first filepath provided
    mgf_path2 : Filepath to a file containg ms2 spectra, this path should match the second filepath provided
    RT_tolerance : Float- the tollerance of RT in seconds the files are aligned under

    DESCRIPTION: After creating a high quality anchors using the picked peak files provided.
    Thhis function will loop over the GP model, providing various variance and lengthscale values
    to the model. The most optimum value for both of these facotrs are then returned at the end.
    The most optimum is determined by the # of peaksets they produce, the number of matching MS2 peaksets they
    produce and the similarity score of these MS2 spectra.

    Returns
    -------
    var : Float- optimal variance of the GP model
    ls : Float- optimal lengthscale of the GP model
    '''

    #Creating the Peak objects and assigning their MS2 spectra

    multi1 = um.peak_creator(filepath_to_match)
    multi2 = um.peak_creator(filepath_to_correct)
    
    
    um.assign_ms2(mgf_path1, multi1)
    um.assign_ms2(mgf_path2, multi2)
    
    #Sort by intensity
    
    multi1.sort(key = lambda x: x.intensity)
    multi2.sort(key = lambda x: x.intensity)
    
    #Align the peak objects 
    
    pps = ps.align(multi1, multi2,RT_tolerance)
    
    #Create peakset objects from this alignment
    
    peaksets = ps.make_peaksets(pps)
    
    #Scan these peaksets and find those that match by their MS2 spectra
    
    ms2_validated_peaksets = ps.ms2_comparison(peaksets)
    
    #Of these MS2 validated anchors, find the scores of their comparisons and make a rounded average
    #This will be used to compare to the newly corrected peaksets that will be created bellow
    
    og_score = check_correction_quality(ms2_validated_peaksets)
    
    original_score = np.mean(og_score)
    
    original_score = round(original_score, 5)

    #Extract the RT of the anchors created above

    multi1_rt, multi2_rt = plot.rt_extract_convert(ms2_validated_peaksets)

    #Get the values of RT-RT from the 2 files respectively, this will be used to make the GP model

    rt_minus = plot.rt_minus_rt_plot(multi1_rt, multi2_rt)
        
    #Need to make it the list into an array so it can be used in the GP
    
    X = np.array(multi2_rt).reshape(len(multi2_rt),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    #variables for var and LS
    
    variance = [1, 2.5, 5, 7.5, 10]
    
    #Figure is the starting variable for LS, lower numbers dont optimize well so they are avoided
    
    figure = 30
    ls = [figure]
    
    '''
    This loop will increment the lengthscale list to incorporate a lareg range of values
    These are all then stored in the LS list
    '''
    
    while figure < 10000:
        
        figure = (figure / 1.2) * 1.5
        
        #Round the LS figure to 2 decimal places
            
        figure = round(figure, 2)
        
        ls.append(figure)
    
    #Empty list to store the results
    
    results = []
    
    all_time = []
    
    #To correct the RT, a numpy array of times must be passed to the models predict function. 
    #This step bellow achieves this by extracting the time and appending it into a list
    
    for i in multi2:
        
        all_time.append(i.get_rt())
        
    all_time = np.array(all_time).reshape(len(all_time),1)

    '''
    The nexted for loop bellow will compare every varaince to every LS value
    In each step, the model is used to make predictions on the drift of the RT
    These predictions are then used to correct the RT, the peaks are aligned again and
    the number of PS generated is recorded. The number of MS2 validated peaksets is also recorded
    The variance, ls, #ps, #ms2 peaksets, original avergae ms2 score and new avergae ms2 score
    (based on the newly created ms2 validated peaksets) are recorded in a tuple which is stored in a list
    '''

    for i in variance:
        
        for j in ls:
            
            #Set up kernel and model objects using Gpy
            
            kernel = GPy.kern.RBF(input_dim=1, variance= i, lengthscale= j)
            m = GPy.models.GPRegression(X,Y, kernel = kernel)    
            
            #Store the mean and variance predicitons from the model. The times extracted from the file_to_corect are passed to this function
            
            mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
            
            #convert from np array to list
                
            mean = list(mean.flatten())
            
            #This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model
            
            um.correct_rt(multi2, mean)
            
            #Align PS again
            
            pseuo = ps.align(multi1, multi2, RT_tolerance)
            peak_sets = ps.make_peaksets(pseuo)
            
            ms2_peak_sets = ps.ms2_comparison(peak_sets)
            
            #Record the number of PS produced
            
            num_of_ps = len(peak_sets)
            
            num_of_ms2 = len(ms2_peak_sets)
            
            #This method returns a list of similarity scores for the ms2 matched PS produced from corrected RT
            
            scores = check_correction_quality(ms2_peak_sets)
        
            #Create an average of these scores and round the value
        
            avg_score = np.mean(scores)
            
            avg_score = round(avg_score, 5)
            
            #Store the values in a tuple to track the results
            
            tup = (i, j, num_of_ps, num_of_ms2, original_score, avg_score)
            
            #Append this tuple to a list
            
            results.append(tup)
            
            #Reset the PS list to their original state for the next round of corrections
            
            multi2 = um.peak_creator(filepath_to_correct)
            um.assign_ms2(mgf_path2, multi2)

    #Sort the list in ascending order of peaksets

    results.sort(key=lambda tup: tup[2])
    
    '''
    This function bellow will return the most optimum LS and Variance. A sizeable spread of Ls and variance
    values produce the same number of peaksets. This method bellow evaluates which nummbers in this spread prdouce
    the higher number of ms2 peaksets. If different variables still produce the same number of MS2 peaksets then
    the similarity score is used to evaluate the optimum
    '''
    
    var, ls = picking_best_results(results)
    
    return var, ls

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
    results_list : List of tuples created in the GP optimization function
    
    DECRIPTION: This function evaluates which ls and variance values are the most optimum. Different var and ls
    values produced the same number of PS. This function extracts the values in the tuple that have the same
    number of peaksets (the lowest). It then evaluates these extracted values based on which values produce 
    the higher number of ms2 peaksets. If different variables still produce the same number of MS2 peaksets then
    the similarity score is used to evaluate the optimum.

    Returns
    -------
    Variance - float
    Lengthscale - float
    '''
    
    #List should be sorted prior to being past to this functon
    #If thats the case the first item in the list has the lowest #ps
    
    top_result = results_list[0]
    
    #split the tuple into component variables
    
    var, ls, top_result_num_ps, num_ms2, score, avg_score = top_result
    
    #Empty list to return at the end
    
    list_of_the_best = []
    
    #loop over the list provided and extarct the tuples that match the lowest number of peaksets
    
    for result in results_list:
    
        #If the row in the list matches the lowest #ps appened it to the list
        
        if result[2] == top_result_num_ps:
            
            list_of_the_best.append(result)
            
    #Sort this list based on the number of MS2 anchors created from the newly aligned ps
            
    list_of_the_best.sort(key=lambda tup: tup[3], reverse=True)
    
    #split the tuple for the best result of the newly organized list
    
    var, ls, top_result_num_ps, num_ms2, score, avg_score = list_of_the_best[0]
    
    '''
    This list is then loop over again now that its been sorted in descending order of #ms2 matching ps
    If other tuples in this list have fewer #ms2 matching ps or the average similarity score of these ps
    is lower than 0.9 then they are removed from the list
    '''
    
    for i in list_of_the_best:
        
        if i[3] < num_ms2 or i[5] < 0.9:
            
            list_of_the_best.remove(i)
    
    #empty lists to contain the best variance and lengthscale        
    
    best_var = []
    best_ls = []
                
    '''
    The values remianing in the list are looped over once more, the variance and lengthscale
    values are extracted into the lists above 
    '''
    
    for i in list_of_the_best:
        
        var, ls, top_result_num_ps, num_ms2, score, avg_score = i
        
        best_var.append(var)
        best_ls.append(ls)
    
    #These lists are then sorted in descending order, and the top value of each 
    #list is returned at the end of the function
    
    best_var.sort(key=float, reverse=True)
    best_ls.sort(key=float, reverse=True)
    
    return best_var[0], best_ls[0]
    

var, ls = GP_optimization('multi 1 ms2.csv','multi 2 ms2.csv', "multi1_ms2.MGF","multi2_ms2.MGF",1.5)
print(var, ls)

'''
for i in resu:
    
    best_var, best_ls, ps_num, ms2_num, ogs, avgs = i

    print("var: ", best_var, "Lengthscale: ", best_ls, "PS num: " ,ps_num, "MS2 PS: ", ms2_num, "OG Score : ", ogs, "Avg Score: ", avgs)
  '''  
    