import argparse
import csv
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from collections import Counter

def printFig(values, descriptor, filename):
	unique_vals = list(set(values))
	freq_vals = []
	for i in range(len(unique_vals)):
		freq_vals.append(values.count(unique_vals[i]))
	figWidth = round((len(unique_vals)/3)/10)*10
	fig = plt.figure(figsize=(figWidth,6)).gca()
	fig.yaxis.set_major_locator(MaxNLocator(integer=True)) 
	N, bins, patches = plt.hist(values, len(unique_vals), ec="k", align="mid")
	xticks = [(bins[idx+1] + value)/2 for idx, value in enumerate(bins[:-1])]
	plt.xticks(xticks, fontsize=8, rotation='vertical')
	plt.ylabel("Instances")
	plt.title("Instances of Unique " + descriptor)
	plt.savefig(filename, bbox_inches="tight")

	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--file",
	    type=str,
	    required=True
	)
	args = parser.parse_args()
	fileName = args.file

	with open(fileName, "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()
	del readLines[0]

	data = []
	for line in readLines:
		splitStr = line.split()
		data.append((splitStr[0], splitStr[1], splitStr[2]))

	currCVE = data[0][0]
	currClasses = []
	currPackages = []
	packages_pairs = []
	classes_pairs = []
	packages_all = []
	classes_all = []
	for i in range(1, len(data)):
		classes_all.append(data[i][1])
		packages_all.append(data[i][2])
		if data[i][0] == currCVE:
			currClasses.append(data[i][1])
			currPackages.append(data[i][2]) 
		else:
			classCombos = list(combinations(list(set(currClasses)), 2))
			packageCombos = list(combinations(list(set(currPackages)), 2))
			for combo in classCombos:
				classes_pairs.append(combo[0] + " & " + combo[1])
			for combo in packageCombos:
				packages_pairs.append(combo[0] + " & " + combo[1])
			currCVE = data[i][0]
			currClasses = []
			currPackages = []
	
	# Sort by frequency
	packages_all = [item for items, c in Counter(packages_all).most_common() for item in [items] * c]
	packages_all = [d for d in packages_all if packages_all.count(d) > 1]
	classes_all = [item for items, c in Counter(classes_all).most_common() for item in [items] * c]
	classes_all = [d for d in classes_all if classes_all.count(d) > 1]
	packages_pairs = [item for items, c in Counter(packages_pairs).most_common() for item in [items] * c]
	classes_pairs = [item for items, c in Counter(classes_pairs).most_common() for item in [items] * c]

	#packages_pairs_list = []
	#for i in range(len(packages_pairs)):
	#	packages_pairs_list.append(list(packages_pairs[i]))

	#classes_pairs_list = []
	#for i in range(len(classes_pairs)):
	#	classes_pairs_list.append(list(classes_pairs[i]))

	#packages_pairs = packages_pairs_list
	#classes_pairs = classes_pairs_list

	while(" " in packages_all):
		packages_all.remove(" ")
	
	while("/android/server/slice" in packages_all):
		packages_all.remove("/android/server/slice")

	# Call the figure prints
	printFig(packages_all, "Packages", "packages.png")
	printFig(classes_all, "Classes", "classes.png")
	printFig(packages_pairs, "Pairs of Packages", "package_pairs.png")
	printFig(classes_pairs, "Pairs of Classes", "class_pairs.png")


if __name__ == '__main__':
	main()
