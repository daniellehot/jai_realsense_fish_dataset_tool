import numpy as np
from pyemd import emd_with_flow
import random as rnd
import matplotlib.pyplot as plt
import pandas as pd

class SampleData:
    def __init__(self, id):
        self.id = id
        no_of_samples = rnd.randint(1000, 1500)
        noise = np.random.uniform(0.01, 5, no_of_samples)
        perfect_data = np.ones(no_of_samples) * rnd.randint(1, 50)
        
        self.data = np.add(perfect_data, noise)
        self.freq, self.bins = np.histogram(self.data, bins=6, density=True)
        self.mean = np.mean(self.data)
        self.std = np.std(self.data)
        self.range = np.max(self.data) - np.min(self.data)

        self.plot_color = (np.random.random(), np.random.random(), np.random.random()) 
        self.plot_label = "data_" + str(id)

        self.emd_values = []

    def compute_histogram(self):  
        self.fig, self.ax = plt.subplots()
        self.ax.hist(self.data, bins=6, alpha=0.5, density=True, color=self.plot_color, label = self.plot_label)
        self.ax.set_xticks(np.around(self.bins, 2))
        self.ax.grid(axis='x')
        

def compute_distance_matrix(locations, show = False):
    distance_matrix = np.eye(len(locations))
    for i in range(len(locations)):
        for j in range(len(locations)):
            distance_matrix[i, j] = np.abs(locations[i] - locations[j])
    if show:
        locations = np.around(locations, 2)
        print(pd.DataFrame(distance_matrix.round(1), index=np.arange(1, len(locations)+1), columns=np.arange(1, len(locations)+1)))
    return distance_matrix.astype(np.float64)

def compute_emd(hist_1, hist_2, distance_matrix):
    hist_1 = hist_1.astype(np.float64)
    hist_2 = hist_2.astype(np.float64)
    emd_value, flow = emd_with_flow(hist_1, hist_2, distance_matrix)
    print("Flow:\n", pd.DataFrame(flow, index=np.arange(1, len(hist_1)+1), columns=np.arange(1, len(hist_1)+1)))
    return emd_value

if __name__=="__main__":
    data_entries = []
    data_locations = []
    for i in range(6):
        data_entries.append(SampleData(i+1))
        data_locations.append(data_entries[i].mean)
    
    distance_matrix = compute_distance_matrix(data_locations, show = True)

    fig, axs = plt.subplots(len(data_entries))
    for i in range(len(data_entries)):
        for j in range(len(data_entries)):
            emd_val = compute_emd(data_entries[i].freq, data_entries[j].freq, distance_matrix)
            data_entries[i].emd_values.append(emd_val)
            #print(emd_val)
            #axs[i].hist(data_entries[i].data, bins=6, alpha=0.5, density=True, color=data_entries[0].plot_color, label = data_entries[0].plot_label)
            #axs[i].hist(data_entries[i].data, bins=6, alpha=0.5, density=True, color=data_entries[i].plot_color, label = data_entries[i].plot_label)
            #xs[i].set_title(emd_val)

    for entry in data_entries:
        print(np.around(entry.emd_values, 2))

    print(pd.DataFrame(distance_matrix.round(1), index=np.arange(1, len(data_entries)+1), columns=np.arange(1, len(data_entries)+1)))
    #fig.legend()
    #fig.tight_layout()
    
    #fig_e, ax_e = plt.subplots()
    #ax_e.errorbar([0], np.mean(data_entries[0].emd_values), yerr=np.std(data_entries[0].emd_values),  fmt='o')


    #plt.show()

        #emd_val = compute_emd(data_entries[1].freq, data_entries[1].freq, distance_matrix)
        #print(emd_val)

    #fig, ax = plt.subplots()
    #for entry in data_entries:
    #    ax.hist(entry.data, bins=10, alpha=0.5, density=True, color=entry.plot_color, label = entry.plot_label)

    #fig.legend()
    #fig.tight_layout()
    #plt.show()