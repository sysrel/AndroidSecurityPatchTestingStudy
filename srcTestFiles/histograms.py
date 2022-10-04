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
#	plt.bar(unique_vals, freq_vals, color='blue', width=0.8)
	plt.hist(values, len(unique_vals))
	plt.xticks(fontsize=8, rotation='vertical')
	plt.ylabel("Instances")
	plt.title("Instances of Unique " + descriptor)
	plt.savefig(filename, bbox_inches="tight")

	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--csv-file",
	    type=str,
	    required=True,
	    help=
	    "Specify the patch you csv file you want to pull from"
	)
	args = parser.parse_args()
	filePath = r'/home/cdbrant/aosp_bulletins/' + args.csv_file
	data = pd.read_csv(filePath)
	lessData = pd.DataFrame(data, columns=['Package', 'Class(es)'])
	lessData = lessData.dropna()
	packages = lessData['Package']
	classes = lessData['Class(es)']
	
	packages_all = []
	packages_pairs = []
	classes_all = []
	classes_pairs = []	

	for i in packages:
		packages_split = i.split(" & ")
		packages_pair_split = list(set(packages_split))
		current_pairs = list(combinations(packages_pair_split, 2))
		for j in packages_split:
			packages_all.append(j)
		for k in current_pairs:
			current_pair = k[0] + " & " + k[1]
			packages_pairs.append(current_pair)

	for i in classes:
		classes_split = i.split(" & ")
		classes_pair_split = list(set(classes_split))
		current_pairs = list(combinations(classes_pair_split, 2))
		for j in classes_split:
			classes_all.append(j)
		for k in current_pairs:
			current_pair = k[0] + " & " + k[1]
			classes_pairs.append(current_pair)

	# Sort by frequency
	packages_all = [item for items, c in Counter(packages_all).most_common() for item in [items] * c]
	classes_all = [item for items, c in Counter(classes_all).most_common() for item in [items] * c]
	packages_pairs = [item for items, c in Counter(packages_pairs).most_common() for item in [items] * c]
	classes_pairs = [item for items, c in Counter(classes_pairs).most_common() for item in [items] * c]

	while(" " in packages_all):
		packages_all.remove(" ")
	
	while("/android/server/slice" in packages_all):
		packages_all.remove("/android/server/slice")

	# Call the figure prints
	printFig(packages_all, "Packages", "graphs/packages.png")
	printFig(classes_all, "Classes", "graphs/classes.png")
	printFig(packages_pairs, "Pairs of Packages", "graphs/package_pairs.png")
	printFig(classes_pairs, "Pairs of Classes", "graphs/class_pairs.png")


if __name__ == '__main__':
	main()
