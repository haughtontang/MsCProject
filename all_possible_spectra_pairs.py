
import similarity_calc as sc

#Testing the possibility of different combinations

#Set up lists of spectra objects using the file paths

spectra1 = sc.mgf_reader("multi1_ms2.MGF")
spectra2 = sc.mgf_reader("multi2_ms2.MGF")

#Flags to keep track of the low and zero scores as well as the total number of combinations

low_score_count = 0
zero_score_count = 0
total_combinations = 0

#nested loop to compare each value to the other, to get the total number of comps

for i in spectra1:
    
    #make a variable for a single spectrum
    
    spec1 = i
    
    for j in spectra2:
        
        #EMpty list to put the 2 spectra together as the score function takes a list as its argument
        
        pair = []
        
        #make a variable for a single spectrum
        
        spec2 = j
        
        #Append to list
        
        pair.append(spec1)
        pair.append(spec2)
        
        #Calculate their similarity score
        
        score = sc.similarity_score(pair)
        
        #Increment the total combinations
        
        total_combinations += 1
        
        '''
        Check the quality of the scores and increment the necessary flags
        for when a score reaches a certain condition. Return these as prints at the end
        '''
        
        if score < 0.9 and score > 0:
            
            low_score_count +=1
            
        if score == 0:
            
            zero_score_count +=1

#Print the results

print("Total number of combinations: ", total_combinations)            
print("Scores lower than 0.9: ", low_score_count)
print("scores equal to 0: ", zero_score_count)