import numpy as np
from pyemd import emd_with_flow, emd_samples
import pandas as pd

def generate_signatures(freq1, bins1, freq2, bins2, normalize):
    if normalize:
        freq1 = freq1/sum(freq1)
        freq2 = freq2/sum(freq2)
    #all_freq = list(np.concatenate((freq1, freq2)))
    all_bins = list(np.concatenate((bins1, bins2)))
    distribution1_sig = np.concatenate((freq1, np.zeros(len(bins2))))
    distribution2_sig = np.concatenate((np.zeros(len(bins1)), freq2))

    return all_bins, distribution1_sig, distribution2_sig

def generate_ordered_signatures(freq1, bins1, freq2, bins2, normalize):
    if normalize:
        freq1 = freq1/sum(freq1)*100
        freq2 = freq2/sum(freq2)*100
    hist1_dict = dict(zip(bins1, freq1))
    hist2_dict = dict(zip(bins2, freq2))
    #all_freq = list(np.concatenate((freq1, freq2)))
    all_bins = list(np.concatenate((bins1, bins2)))
    all_bins.sort()
    print(all_bins)
    
    distribution1_sig = []
    distribution2_sig = []
    for bin in all_bins:
        distribution1_sig.append(hist1_dict.get(bin, 0))
        distribution2_sig.append(hist2_dict.get(bin, 0))
    print(distribution1_sig)
    print(distribution2_sig)

    #distribution1_sig = np.concatenate((freq1, np.zeros(len(bins2))))
    #distribution2_sig = np.concatenate((np.zeros(len(bins1)), freq2))

    return all_bins, distribution1_sig, distribution2_sig

def compute_dist_matrix(positions):
    dist_matrix = np.eye(len(positions))
    for i in range(len(positions)):
        for j in range(len(positions)):
            dist_matrix[i, j] = np.abs(positions[i]-positions[j])
    return dist_matrix

def calculate_emd(signature_1, signature_2, distance_matrix):
    first_signature = np.array(signature_1, dtype=np.double)
    second_signature = np.array(signature_2, dtype=np.double)
    distances = np.array(distance_matrix, dtype=np.double)
    emd, flow = emd_with_flow(first_signature, second_signature, distances)
    flow = np.array(flow)
    return emd, flow

data1 = [10, 20, 30]
data1_freq, data1_bins = np.histogram(data1, bins=3, density=True)
data1_bins = 0.5 * (data1_bins[1:] + data1_bins[:-1])

data2 = [10, 10, 20, 20, 30]
#data2 = [100, 200, 300]
print(data2)
#data2 = [5, 11, 14, 21, 38]
data2_freq, data2_bins = np.histogram(data2, bins=3, density=True)
data2_bins = 0.5 * (data2_bins[1:] + data2_bins[:-1])

#positions, sig1, sig2 = generate_ordered_signatures(data1_freq, data1_bins, data2_freq, data2_bins, normalize=True)


positions, sig1, sig2 = generate_signatures(data1_freq, data1_bins, data2_freq, data2_bins, normalize=False)
for position, freq in zip(positions, sig1):
    print("SIG1 Position:", np.around(position, 2), "Mass:", np.around(freq, 2))
print("===========")
for position, freq in zip(positions, sig2):
    print("SIG2 Position:", np.around(position, 2), "Mass:", np.around(freq, 2))

dist = compute_dist_matrix(positions)
print("Distance matrix")
print(pd.DataFrame(dist.round(1), index=np.around(positions, 1), columns=np.around(positions, 1)))
print("===========")

emd, flow = calculate_emd(sig1, sig2, dist)
print("EMD: {0:.2f}".format(emd))
print("Flow:\n", pd.DataFrame(flow.round(2), index=positions, columns=positions))


#emd, flow = calculate_emd(sig2, sig1, dist)
#print("EMD: {0:.2f}".format(emd))
#print("Flow:\n", pd.DataFrame(flow, index=positions, columns=positions))