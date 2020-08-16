
import GPy
from peak_tools import PeakSet as ps
import useful_functions as um
import numpy as np
import optimization_for_realtime as gpc
import investigative_functions as invfun

'''
Take 2 paths of picked peaks as its argument and convert the information in these files into
peak objects
'''

def create_peak_objects(filepath, mgf_path):
    '''
    Parameters
    ----------
    filepath : String: file path to a picked peak file
    mgf_path : String: file path to the corresponding MGF file for a picked peak file
    DESCRIPTION: Makes peak objects from the files provided
    Returns
    -------
    peaks : List of peak objects

    '''
    
    peaks = um.peak_creator(filepath)
    um.assign_ms2(mgf_path, peaks)
    
    return peaks

#Seperate alignment method to clean up the incoming_peaks function and later functions
  
def alignment(first_run_peaks, incoming_peaks, RT_tol):
    '''
    Parameters
    ----------
    first_run_peaks : A list of peak objects
    incoming_peaks : A list of different peak objects
    RT_tol : double- RT tolerance for alignment quality
    Description: This method will form pseudo peaksets by matching the peaks
    between the 2 files into a list and appending said list to another list
    This list of lists can then be used to create peakset objects
    Returns
    -------
    List of peakset lists
    '''
    
    pseudo_peaksets = ps.align(first_run_peaks, incoming_peaks, RT_tol)
    
    peaksets = ps.make_peaksets(pseudo_peaksets)
    
    return peaksets

def create_optimized_gp_model(peaksets):
    
    '''
    Parameters
    ----------
    peaksets: list of peakset objects
    
    DESCRIPTION: assesses various variance and length scale values and return the optimum
    kernel parameters based on the number of peaksets generated post correction and the
    quality of their ms2 similarity scores
    
    Returns
    -------
    best_var : Float: best variance value
    best_ls : Float: best ls value
    '''
    
    return gpc.find_best_hyperparameters(peaksets)

def add_peak(first_file, peakset_list, peak, RT_tol):
     '''
     Parameters
     ----------
     first_file: list of peak objects that originated from the COMPLETE file
     peakset_list: list of peakset objects
     peak : list of peak_objects
     RT_tol: float- tolerance for alignment. This value should be the same as the RT tolerance
     used in the original alignment
     DESCRIPTION: Takes a list of peaks and looks for a matching peak in the list of peaksets
     provided in the argument. If no match is found- the peak is added in as a new peakset

     Returns
     -------
     List of updated peaksets
     '''
     
     #get the file name for the first file
     
     first_file_name = ""
     
     for i in first_file:
         
         first_file_name = i.get_file()
         
         break
     
     #extract all the peaks in the live run from the peakset list   
     
     second = []   
     
     for i in peakset_list:
         
         for j in i.get_peaks():
             
             #Use the file name to determine the origin of the peak
             
             if j.get_file() != first_file_name:
                 
                 second.append(j)
     
    #Loop through the peaks in the peak list provided and add them to the list of extracted peaks

     for i in peak:
        
         second.append(i)
     
     #Perform the alignment again with the added corrected peaks from the live run   
     
     added = alignment(first_file, second, RT_tol)
     
     #return the updated peaksets with the added peaks
     
     return added


    
def correct_rt(GP_model, peak_list):
    '''
    Parameters
    ----------
    GP_model: Gpy model object
    peak_list : list of peak objects- the ones being corrected
    DESCRIPTION: Updates the RT values in the peak objects by predicting the drift
    using the RT model
    -------
    Returns
    None
    '''
    
    #empty list to store the RT values

    rt = []
    
    #Loop through and get the RT value
    
    for peak in peak_list:
        
        rt.append(peak.get_rt())
    
    #Convert this variable into a numpy array before passing to the model
    
    rt = np.array(rt).reshape(len(rt),1)
    
    #pass the RT list to the model provided to make predictions on the RT drift
    
    mean, var = GP_model.predict(rt, full_cov=False, Y_metadata=None, kern=None, likelihood=None, include_likelihood=True)
    
    #convert to list
    
    mean = list(mean.flatten())
            
    #This method corrects the RT by adding the predictions (mean) produced by the model
    
    um.correct_rt(peak_list, mean)
    
    
def real_time_correction(first_run_fp, first_run_mgf, live_run, live_run_mgf, RT_tol, peak_batch):
    '''
    Parameters
    ----------
    first_run_fp : String- file path to the first file
    first_run_mgf : String- file path to the first file's corresponding mgf file
    live_run : String- file path to the second file.
    live_run_mgf : String- file path to the second file's corresponding mgf file
    RT_tol : double- tolerance of retention time when aligning peaks
    peak_batch : int- how many peaks per batch of correction e.g. 10 would corrected live_run peaks
    10 at a time

    DESCRIPTION: This method creates a list of peak objects using the file paths created
    An initial chunk of peaks are then taken from the live_run peaks to perform an initial alignment
    The peaksets generated from this are then used to create anchors that will be used to create a GP
    model. The optimal kernel parameters for this model are found before creating the model. The initial 
    alignmnet is then corrected. From there the live_run peaks are split into groups- size dictated by the
    peak_batch parameter. These batches are then corrected in sequence within a loop. If an anchor
    is found within this correction the model is updated. The process will continue until all peaks
    have been corrected in live_run, after correction they are added to the initial peakset object
    and either form a pair with an existing peak or go in as a singlet peakset if no match is found
    
    Returns
    -------
    None.

    '''

    #Make peak objects

    first_run = create_peak_objects(first_run_fp, first_run_mgf)
    
    live_peaks = create_peak_objects(live_run, live_run_mgf)

    #Perform a normal alignment that wouldn't be done under real-time for comparison later
    
    normal = alignment(first_run, live_peaks, RT_tol)

    #Get an initial number of peaksets for a primary alignment to get some anchors to make the model
    
    initial = []
    
    for i in live_peaks:
        
        initial.append(i)
        
        #Remove so we aren't using these later for real-time correction
        
        live_peaks.remove(i)
        
        #For this dataset I chose 150 as this gave a good starting number of anchors, at
        #lower number, not enough anchors were generated to make a good model
        
        if len(initial) >= 150:
            
            break
    
    #correct using these initial numbers
    
    peaksets = alignment(first_run, initial, RT_tol)
    
    #make anchors from these peaksets
    
    anchors = ps.ms2_comparison(peaksets, 0.9)
    
    #extarct the RT from the anchors and find the differences between them
    
    r1,r2 = um.rt_extraction(anchors)
    
    minus = um.subtract_attributes(r1,r2)
    
    print("Number of peaksets after initial alignment with 150 peaks ", len(peaksets))
    
    #Find the optimal optimization parameters for the kernel based on the initial peaksets
        
    var, ls = create_optimized_gp_model(peaksets)
    
    #Converts the RT in live_peaks and the differences into numpy arrays
    
    X = np.array(r2).reshape(len(r2),1)
    Y = np.array(minus).reshape(len(minus),1)
    
    #make a kernel and model
    
    kernel = GPy.kern.RBF(input_dim=1, variance= var, lengthscale= ls)
    model = GPy.models.GPRegression(X,Y, kernel = kernel)   
    
    #Correct RT using the model and RT from the initial peaks
    
    correct_rt(model, initial)
    
    #Performs the alignment again
    
    corrected_peaksets = alignment(first_run, initial, RT_tol)
    
    #remake the anchors from this correction
    
    anchors = ps.ms2_comparison(peaksets, 0.9)
    
    #split live peaks into batches based on the batch number provided
    
    limit = peak_batch
    
    #list of these splits to be used later in a for loop
    
    list_of_splits = []
    
    '''
    after the batch number of peaks has been extracted into a separate list
    they are removed from live peaks. This process will be repeated until 
    there are no peaks left in live peaks- as dictated by the while loop
    '''
    
    while len(live_peaks) > 0:
        
        #List of splits per iteration
        
        split = []
        
        '''
        the split won't always be perfect- this is a special condition to ensure the loop can continue
        In a case where there aren't enough peaks left to satisfy the batch number the limit is changed
        '''
        
        if len(live_peaks) < limit:
                
            limit = len(live_peaks)
        
        #Go through live peaks and get the peaks into split
        
        for i in range(0, limit):

            split.append(live_peaks[i])
        
        #similarly go through and remove the peaks that were added to split
        
        for i in split:
            
            live_peaks.remove(i)
            
        #Add the splits to the list of splits
            
        list_of_splits.append(split)
 
    
    for peak_list in list_of_splits:
        
        #Corret the retention times of the peaks
        
        correct_rt(model, peak_list)
        
        #updated the peakset objects with the new peaks
        
        corrected_peaksets = add_peak(first_run, corrected_peaksets, peak_list, RT_tol)
        
        if len(peak_list) == 1:
            
            print("Number of peaksets after adding peak: ", len(corrected_peaksets))
        
        else:
        
            print("len after adding peaks", len(corrected_peaksets))
        
        #Find out if new anchors were found
        
        check_anchor = ps.ms2_comparison(corrected_peaksets, 0.9)
        
        #if there are new anchors found then the model is updated
        
        if len(check_anchor) > len(anchors):
            
            print("New anchor found- updating model")
            
            #update the model
            
            #get the retention time
            
            r1,r2 = um.rt_extraction(check_anchor)
             
            minus = um.subtract_attributes(r1,r2)
            
            #remake the numpy arrays of RT in live_peaks and the difference in RT
            
            X = np.array(r2).reshape(len(r2),1)
            Y = np.array(minus).reshape(len(minus),1)
            
            #Model updated
            
            model = GPy.models.GPRegression(X,Y, kernel = kernel)   
            
            #reset anchors to equal the new anchors, that way this condition won't be continually
            #triggered when a cascade of new anchors are found that are greater than the original
            
            anchors = check_anchor
                        
    print("Number of peaksets after", peak_batch, "peak split correction:", len(corrected_peaksets))
    
    ms2_peaksets = ps.ms2_comparison(corrected_peaksets, 0)
    
    print("Number of peaksets after",peak_batch,"peak split correction", len(ms2_peaksets))
    
    '''
    Contrast this real-time correction to a standard correction and improve its quality by
    determining if any ms2 peaksets can be added
    '''
    #compare the end result of corrected to normal to find any missed ms2 peaksets
    
    updated = invfun.get_reomoved_ms2_peaks(normal, corrected_peaksets)
    
    #get the updated number of ms2 peaksets from the above function
    
    updated_ms2 = ps.ms2_comparison(updated, 0)
    
    print("Number of MS2 peaksets after ms2 recovery: {} and number of ms2 peaksets after recovery: {}".format(len(updated), len(updated_ms2)))
           
real_time_correction('multi 1 ms2.csv', "multi1_ms2.MGF",'multi 2 ms2.csv',"multi2_ms2.MGF",1.5, 50)    
    