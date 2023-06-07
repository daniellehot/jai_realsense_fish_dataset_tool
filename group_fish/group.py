import random as rnd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import os

FISH_CATALOG = {
    "cod": 102,
    "haddock": 119,
    "*hake": 52,
    "*other": 29,
    "whiting": 103,
    "*horse mack": 58
}

COLORS = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'yellow', 'cyan', 'silver']
BAR_COLORS = COLORS[:len(list(FISH_CATALOG.keys()))]

NUMBER_OF_GROUPS = 25
GROUP_MIN = 14
GROUP_MAX = 24

class GroupGenerator():
    def __init__(self):
        self.available_fish = self.get_all_fish()
        self.used_fish = []
        self.groups = []

    def draw_global_distribution(self):
        species = FISH_CATALOG.keys()
        #x_pos = np.arange(len(species))
        sizes =np.asarray(list(FISH_CATALOG.values()))
        sizes = sizes/sizes.sum(axis=0) * 100
        
        fig, ax = plt.subplots()
        ax.set_xlabel("Species")
        ax.set_ylabel("Percentage")
        ax.bar(species, sizes, align='center', alpha=0.5, color = BAR_COLORS)
        plt.savefig("global_distribution.png")
    
    def draw_distribution_across_groups(self, species, color):
        fig, ax = plt.subplots()
        sizes = []
        for group in self.groups:
            number_of_instances = group.count(species)
            sizes.append(number_of_instances/len(group)*100)

        fig, ax = plt.subplots()
        fig.set_figwidth(12)
        ax.bar(np.arange(1, len(self.groups)+1), sizes, align='center', alpha = 0.5, color = color)
        ax.set_title(species + ' distribution')
        ax.set_xlabel("Group")
        ax.set_ylabel("Percentage")
        ax.set_xticks(np.arange(1, NUMBER_OF_GROUPS+1))
        plt.savefig(species + ".png") 

    def draw_distribution_across_groups_one_figure(self):
        fig, axs = plt.subplots(len(list(FISH_CATALOG.keys())))
        fig.set_figheight(28)
        fig.set_figwidth(22)

        for species in FISH_CATALOG.keys():
            sizes = []
            for group in self.groups:
                number_of_instances = group.count(species)
                sizes.append(number_of_instances/len(group)*100)
            ax_idx = list(FISH_CATALOG.keys()).index(species)
            ax_color = COLORS[list(FISH_CATALOG.keys()).index(species)]
            axs[ax_idx].bar(np.arange(1, len(self.groups)+1), sizes, align='center', alpha = 0.5, label = species, color = ax_color)
            axs[ax_idx].set_title(species + ' distribution')
            #axs[ax_idx].set_xlabel("Group")
            axs[ax_idx].set_ylabel("Percentage")
            axs[ax_idx].set_xticks(np.arange(1, NUMBER_OF_GROUPS+1))
        #fig.legend(loc = "upper left")
        plt.savefig("distribution_across_groups.png")
        
    def draw_group_distribution(self, group):
        species = FISH_CATALOG.keys()
        sizes = []
        for fish in species:
            number_of_instances = group.count(fish)
            sizes.append(number_of_instances/len(group)*100)
        bar_labels = species
        bar_colors = COLORS[:len(species)]
        
        fig, ax = plt.subplots()
        ax.bar(species, sizes, align='center', alpha = 0.5, label = bar_labels, color = bar_colors)
        plt.savefig("group.png")

    def draw_group_distributions(self):
        #group_distributions = []
        fig, ax = plt.subplots()
        fig.set_figheight(10)
        fig.set_figwidth(16)
        ax.set_xlabel("Group")
        ax.set_ylabel("Distribution")
        for group in self.groups:
            #group_distribution = []
            distribution_sum = 0
            for species in FISH_CATALOG.keys():
                number_of_instances = group.count(species)
                size = number_of_instances/len(group)*100
                ax_color = COLORS[list(FISH_CATALOG.keys()).index(species)]
                ax.bar(self.groups.index(group)+1, size, bottom=distribution_sum, align="center", alpha=0.5, label = species, color = ax_color)
                ax.set_xticks(np.arange(1, NUMBER_OF_GROUPS+1))
                distribution_sum += size
        ax.legend(list(FISH_CATALOG.keys()), loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=6)
        plt.savefig("group_distributions.png")
      
    def get_all_fish(self):
        all_fish = []
        for species in FISH_CATALOG.keys():
            for i in range(FISH_CATALOG[species]):
                all_fish.append(species)
        rnd.shuffle(all_fish)
        return all_fish
    
    def reset(self):
        print("Made {}/{} groups. Resetting".format(len(self.groups), NUMBER_OF_GROUPS))
        self.available_fish = self.get_all_fish()
        self.used_fish = []
        self.groups = []
    
    def get_group(self):
        number_of_fish = rnd.randint(GROUP_MIN, GROUP_MAX)
 
        # There is enough fish to create a new group -> Create a new group
        if number_of_fish <= len(self.available_fish):
            group = []
            #print("Number of fish {} Number of groups {}".format(len(self.available_fish), len(self.groups)))
            for i in range(number_of_fish):
                rnd_fish = rnd.choice(self.available_fish)
                group.append(rnd_fish)
                self.available_fish.remove(rnd_fish)
                self.used_fish.append(rnd_fish)
            self.groups.append(group)

        # There is not enough fish to create a new group, but we have 25 groups already
        elif number_of_fish > len(self.available_fish) and len(self.groups) == NUMBER_OF_GROUPS:
            number_of_fish = len(self.available_fish)
            for i in range(number_of_fish):
                rnd_fish = rnd.choice(self.available_fish)
                rnd.choice(self.groups).append(rnd_fish)
                self.available_fish.remove(rnd_fish)
                self.used_fish.append(rnd_fish)

        # There is less fish than required to create a new group and there are more or less groups than the target
        elif number_of_fish > len(self.available_fish) and len(self.groups) != NUMBER_OF_GROUPS:
            self.reset()


    def write_groups(self):
        filename = "groups.txt"
        if os.path.exists(filename):
            os.remove(filename)
            
        for idx, group in enumerate(self.groups):
            group.sort()
            counter = Counter(group)
            string_to_write = 'Group No. {} Number of fish {}'.format(idx + 1, len(group))  
            for fish in FISH_CATALOG.keys():
                fish_count = ' {} {}'.format(fish, counter[fish])
                string_to_write += fish_count
            string_to_write += "\n"
            
            with open(filename, "a") as f:
                f.write(string_to_write)

if __name__=="__main__":
    generator = GroupGenerator()

    while len(generator.available_fish):
        generator.get_group()

    print("Number of groups", len(generator.groups))
    for group in generator.groups: 
        group.sort()
        print("Group No.", generator.groups.index(group)+1, "Number of fish", len(group), group)
    print("===========================")

    generator.write_groups()

    #generator.draw_group_distribution(generator.groups[2])
    generator.draw_group_distributions()

    generator.draw_global_distribution()
    generator.draw_distribution_across_groups_one_figure()
    for species in FISH_CATALOG.keys():
        color_idx = list(FISH_CATALOG.keys()).index(species)
        generator.draw_distribution_across_groups(species, COLORS[color_idx])
        