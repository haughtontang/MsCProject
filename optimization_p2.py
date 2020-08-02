import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc

def find_best_hypparams(peak1, peak2):
    
    align = ps.align(peak1, peak2,1.5)
    
    peaksets = ps.make_peaksets(align)
    
    anchors = ps.ms2_comparison(peaksets, 0.9)
    
    rt1, rt2 = plot.rt_extract_convert(anchors)
    
    rt_minus = plot.rt_minus_rt_plot(rt1, rt2)
    
    #get the time in peak2
    
    all_time = []
    
    for peak in peak2:
        
        time = peak.get_rt()
        
        time = round(time, 2)
        
        all_time.append(time)
        
    all_time = np.array(all_time).reshape(len(all_time),1)
        
    X = np.array(rt2).reshape(len(rt2),1)
    Y = np.array(rt_minus).reshape(len(rt_minus),1)
    
    #variance values
    
    variance = [1,2.5,5,7.5,10]
    
    initial_ls = 30.0
    
    #get ls values
    
    ls = []
    
    while initial_ls < 10000:
        
        initial_ls = (initial_ls /1.2) * 1.5
        
        ls.append(initial_ls)
        
        
        
    results = []
    
    var1 = peak1
    var2 = peak2
    
    for v in variance:
        
        for leng in ls:
            
            #Make a kernel using these params
            
            #Set up kernel and model objects using Gpy
            
            kernel = GPy.kern.RBF(input_dim=1, variance= v, lengthscale= leng)
            m = GPy.models.GPRegression(X,Y, kernel = kernel)    

            #Store the mean and variance predicitons from the model. The times extracted from the file_to_corect are passed to this function
            
            mean, var = m.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
            
            #convert from np array to list
            
            mean = list(mean.flatten())
            
            #This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model
            
            um.correct_rt(var2, mean)
            
            #Align again
            
            corrected_align = ps.align(var1, var2, 1.5)
            
            corrected_peaksets = ps.make_peaksets(corrected_align)
            
            #get the number
            
            num_corrected = len(corrected_peaksets)
            
            #MS2 numbers
            
            corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)
            
            #get ms2 num
            
            ms2_num = len(corrected_ms2)
            
            #Check the correction quality
            
            corrected_scores = check_correction_quality(corrected_ms2)
            
            low_score_count = 0
            
            zero_score_count = 0
            
            for score in corrected_scores:
                
                if score < 0.9:
                    
                    low_score_count+=1
                    
                if score == 0:
                    
                    zero_score_count+=1
                    
            #record the results
            
            tup = (v, leng, num_corrected, ms2_num, low_score_count, zero_score_count)
            
            results.append(tup)
            
            #reset the peaks
            
            var1 = peak1
            var2 = peak2
            
    #sort the list
    
    results.sort(key=lambda tup: tup[2])
    
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
    
    top_result = results_list[0]
    
    variance, lengthscale, ps, ms2, low, zero = top_result
    
    best_results = []
    
    for res in results_list:
        
        if res[2] == ps:
            
            best_results.append(res)
            
    best_results.sort(key=lambda tup: tup[3])
    
    best = best_results[0]
    
    best_v, best_ls, best_ps, best_ms2, best_low, best_zero = best
            
    #remove results from the best list
    
    for i in best_results:
        
        if i[3] < best_ps or i[4] > best_low or i[5] > best_zero:
            
            best_results.remove(i)
            
    best_var = []
    best_leng = []
    
    for top in best_results:
        
        v, ls, p, m, l, z = top
        
        best_var.append(v)
        best_leng.append(ls)
        
    best_var = sorted(best_var, key=float)
    best_leng = sorted(best_leng, key=float)
   
    print("list of the best :")
    print(list_of_the_best)
    print()
    print("variance list:")
    print(best_var)
    print()
    print("LS list:")
    print(best_ls)
   
    return best_var[0], best_leng[0]
            
p1 = um.peak_creator('multi 1 ms2.csv')
p2 = um.peak_creator('multi 2 ms2.csv')
  
um.assign_ms2("multi1_ms2.MGF", p1) 
um.assign_ms2("multi2_ms2.MGF", p2) 

p1.sort(key = lambda x: x.intensity)
p2.sort(key = lambda x: x.intensity)

normal_align = ps.align(p1,p2,1.5)

normal_ps = ps.make_peaksets(normal_align)

print("Normal ps: ", len(normal_ps))

ms2 = ps.ms2_comparison(normal_ps, 0)

print("Normal ms2: ", len(ms2))

rt1, rt2 = plot.rt_extract_convert(ms2)

rt_minus = plot.rt_minus_rt_plot(rt1, rt2)

X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

resu, variance_val, ls_val = find_best_hypparams(p1, p2)

gp_kern = GPy.kern.RBF(input_dim=1, variance= variance_val, lengthscale= ls_val)
gp_model = GPy.models.GPRegression(X,Y, kernel = gp_kern)    

mean, var = gp_model.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
            
#convert from np array to list

mean = list(mean.flatten())

#This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model

um.correct_rt(p2, mean)

#for time in RT_tolerances:

#Align PS again under normal circumstances

pseuo = ps.align(p1, p2, 1.5)
peak_sets = ps.make_peaksets(pseuo)

ms2_peak_sets = ps.ms2_comparison(peak_sets, 0)

print(variance_val, ls_val)

print("len after cor: ", len(peak_sets))

print("ms2 after cor: ", len(ms2_peak_sets))       

file = []

for i in resu:
    
    best_var, best_ls, rt, ps_num, ms2_num, low, zero = i

    line = "var: ", str(best_var), "Lengthscale: ", str(best_ls), "RT tol: ", str(rt), "PS num: " ,str(ps_num), "MS2 PS: ", str(ms2_num), "Normal Scores < 0.9: ", str(low),"Normal Scores = 0: ", str(zero)
    file.append(line)
    
with open('this time lucky.txt', 'w') as f:
    for item in file:
        line = str(item)
        f.write(line)
        f.write("\n")

