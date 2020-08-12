import GPy
from PeakTools import PeakSet as ps
import UsefulMethods as um
from PeakTools import Plotter as plot
import numpy as np
import SimilarityCalc as sc
import random

def random_ms2(peak_list):
              
    #This method is just for testing the optimization thing bellow
    
    #It will randomly assign MS2 spectrum objects to aligned peaksets in attempt to generate false +ves
    
    random_list = []
    
    limit = len(peak_list)

    for i in range(0, limit):
        
        n = random.randint(0,limit)
        
        random_list.append(n)
    
    for peak in peak_list:
        
        index = random.randint(0, limit-1)
        
        new_id = random_list[index]
        
        peak.id = new_id
        
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

def find_best_hypparams(filepath_to_match, filepath_to_correct, mgf_path1, mgf_path2):
    
    #variance values
    
    variance = [1,2.5,7.5,10]
    
    #get ls values
    
    ls = []
    
    initial_ls = 30.0
    
    ls.append(initial_ls)
    
    while initial_ls < 1000:
        
        initial_ls = (initial_ls /1.2) * 1.5
        
        initial_ls = round(initial_ls, 2)
        
        ls.append(initial_ls)
        
    #Appended recorded results
        
    results = []
    rt_tol = [1.5]
    for v in variance:
        
        for leng in ls:
            
            #print("var", v)
            #print("lengthscale", leng)
            #Extract rt to make rt minus numbers
    
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
            
            anchors = ps.ms2_comparison(peaksets, 0.9)
    
            rt1, rt2 = plot.rt_extract_convert(anchors)
            
            rt_minus = plot.rt_minus_rt_plot(rt1, rt2)
            
            #get the time in peak2
            
            all_time = []
            
            for peak in peak2:
                
                t = peak.get_rt()
                
                all_time.append(t)
            
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
            
            #get the number
            
            num_corrected = len(corrected_peaksets)
            
            #MS2 numbers
            
            corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)
            
            #get ms2 num
            
            ms2_num = len(corrected_ms2)
                        
            low_score_count = 0
            
            zero_score_count = 0
            
            #Get correction scores for all MS2 spectra aligned and find if there are any of low quality
            
            corrected_scores = check_correction_quality(corrected_ms2)
            
            for score in corrected_scores:
                
                if score < 0.9:
                    
                    low_score_count+=1
                    
                if score == 0:
                    
                    zero_score_count+=1

            #reset for random
            
            peak1 = um.peak_creator(filepath_to_match)
            peak2 = um.peak_creator(filepath_to_correct)
            
            #rnadom for the id method
            
            random_ms2(peak1)
            random_ms2(peak2)
            
            um.assign_ms2(mgf_path1, peak1)
            um.assign_ms2(mgf_path2, peak2)
            
            #Sort by intensity
            
            peak1.sort(key = lambda x: x.intensity)
            peak2.sort(key = lambda x: x.intensity)
            
            um.correct_rt(peak2, mean)
            
            #Align again
            
            rand_corrected_align = ps.align(peak1, peak2, 1.5)
            
            rand_corrected_peaksets = ps.make_peaksets(rand_corrected_align)
            
            #randomize by spectra and not ID
            
            #rand_corrected_peaksets = randomize_ms2(mgf_path1, mgf_path2, rand_corrected_peaksets)
            
            #get the number
            
            rand_num_corrected = len(corrected_peaksets)
            
            #MS2 numbers
            
            rand_corrected_ms2 = ps.ms2_comparison(rand_corrected_peaksets, -1)
            
            #get ms2 num
            
            rand_ms2_num = len(rand_corrected_ms2)
                        
            rand_low_score_count = 0
            
            rand_zero_score_count = 0
            
            #Get correction scores for all MS2 spectra aligned and find if there are any of low quality
            
            rand_corrected_scores = check_correction_quality(rand_corrected_ms2)
            
            for score in rand_corrected_scores:
                
                if score < 0.9:
                    
                    rand_low_score_count+=1
                    
                if score == 0:
                    
                    rand_zero_score_count+=1
                    
            #record the results
            
            tup = (v, leng, 1.5, num_corrected, ms2_num, rand_num_corrected, rand_ms2_num, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count)
            
            results.append(tup)
            
    #sort the list
    
    results.sort(key=lambda tup: tup[3])
    
    #print(results)
    
    best_var, best_ls = picking_best_results(results)
    
    return results, best_var, best_ls 
            
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
    
    print("len results", len(results_list))
    
    top_result = results_list[0]
    
    #print(len(top_result))
    
    #unpack best results
    
    v, leng, time, num_corrected, ms2_num, rand_num_corrected, rand_corrected_ms2, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count = top_result
    
    best_results = []
    
    #Make a list of best results based on number of ps generated
    
    for res in results_list:
        
        if res[3] == num_corrected:
            
            best_results.append(res)
    
    #sort this list on the number of ms2 peaksets generated        
    
    best_results.sort(key=lambda tup: tup[4])
    print("len best results", len(best_results))
    best = best_results[0]
    
    v, leng, time, num_corrected, ms2_num, rand_num_corrected, rand_corrected_ms2, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count = best
            
    #remove results from the best list
    '''
    for i in best_results:
        
        if i[3] < best_ps or i[4] > best_low or i[5] > best_zero:
            
            best_results.remove(i)
     '''       
    best_var = []
    best_leng = []
    
    print("list of the best :")
    print(best_results)
    print()
    
    #Get the best var and ls values if the list of the best is >1
    
    for top in best_results:
        
        v, leng, time, num_corrected, ms2_num, rand_num_corrected, rand_corrected_ms2, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count = top
        
        best_var.append(v)
        best_leng.append(leng)
    
    #Sort the list and return the lowest results of the the var and ls    
    
    best_var.sort(key=float, reverse = True)
    best_leng.sort(key=float)
   
    
    print("variance list:")
    print(best_var)
    print()
    print("LS list:")
    print(best_leng)
   
    return best_var[0], best_leng[0]

'''
#Correcting in the script

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


id_list1 = []
id_list2 = []
for i in normal_ps:
    if i.number_of_peaks > 1:
        for j in i.peaks:
            
            if j.file == "multi 1 ms2.csv":
               # yup = j.ms2
                
                key = j.id
                
                id_list1.append(key)
                
            else:
                
                #yup = j.ms2
                
                key = j.id
                
                id_list2.append(key)
                

rt1, rt2 = plot.rt_extract_convert(ms2)

rt_minus = plot.rt_minus_rt_plot(rt1, rt2)

X = np.array(rt2).reshape(len(rt2),1)
Y = np.array(rt_minus).reshape(len(rt_minus),1)

all_time = []

for i in p2:
    
    time = i.get_rt()
    all_time.append(time)
    
all_time = np.array(all_time).reshape(len(all_time),1)
'''
resu, variance_val, ls_val = find_best_hypparams('multi 1 ms2.csv', 'multi 2 ms2.csv',"multi1_ms2.MGF","multi2_ms2.MGF")


print("var=", variance_val, "ls = ", ls_val)
'''
gp_kern = GPy.kern.RBF(input_dim=1, variance= variance_val, lengthscale= ls_val)
gp_model = GPy.models.GPRegression(X,Y, kernel = gp_kern)    

mean, var = gp_model.predict(all_time, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)

#convert from np array to list

mean = list(mean.flatten())

#This method corrects the RT of the file_to_correct by adding the predictions (mean) produced by the model

um.correct_rt(p2, mean)

#Align again

corrected_align = ps.align(p1, p2, 5)

corrected_peaksets = ps.make_peaksets(corrected_align)

#get the number

num_corrected = len(corrected_peaksets)

#MS2 numbers

corrected_ms2 = ps.ms2_comparison(corrected_peaksets, 0)

#get ms2 num

ms2_num = len(corrected_ms2)

print("len after cor: ", num_corrected)

print("ms2 after cor: ", ms2_num)       

corrected_id_list1 = []
corrected_id_list2 = []

for i in corrected_ms2:
    if i.number_of_peaks > 1:
        for j in i.peaks:
           
            if j.file == "multi 1 ms2.csv":
               # yup = j.ms2
                
                key = j.id
                
                corrected_id_list1.append(key)
                
            else:
                
                #yup = j.ms2
                
                key = j.id
                
                corrected_id_list2.append(key)

count = 0
        
for s in id_list1:
    
    if s not in corrected_id_list1:
        
        #print(s)
        count+=1
 
print("numbers removed from ms2 in file1", count)

count = 0
for s in id_list2:
    
    if s not in corrected_id_list2:
        
        #print(s)
        count+=1
        
print("numbers removed from ms2 in file2", count)



'''
file = []
for i in resu:
    
    v, leng, time, num_corrected, ms2_num, rand_num_corrected, rand_corrected_ms2, low_score_count, rand_low_score_count, zero_score_count, rand_zero_score_count = i

    line = "var: ", str(v), "Lengthscale: ", str(leng), "RT Tole", str(time), "PS num: " ,str(num_corrected), "MS2 PS: ", str(ms2_num), "Rand ps num: ", rand_num_corrected, "rand #ms2: ", rand_corrected_ms2 ,"Normal Scores < 0.9: ", str(low_score_count),"rand Scores < 0.9: ", str(rand_low_score_count),"Normal Scores = 0: ", str(zero_score_count),"rand Scores = 0: ", str(rand_zero_score_count)
    file.append(line)
    
with open('Rand ID for ms2 test 3.txt', 'w') as f:
    for item in file:
        line = str(item)
        f.write(line)
        f.write("\n")
