from bs4 import BeautifulSoup
import argparse
import os
import requests
import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from collections import Counter
from itertools import chain

def printFreqFig(values, descriptor, filename):
	values = [d for d in values if values.count(d) > 1]
	numBinsGraph = len(list(set(values)))
	figWidth = round((numBinsGraph/3)/10)*10
	fig = plt.figure(figsize=(figWidth,6)).gca()
	fig.yaxis.set_major_locator(MaxNLocator(integer=True))
	N, bins, patches = plt.hist(values, numBinsGraph, ec="k", align="mid")
	xticks =[(bins[idx+1] + value)/2 for idx, value in enumerate(bins[:-1])]
	plt.xticks(xticks, fontsize=8, rotation='vertical')
	plt.ylabel("Frequency")
	plt.title(descriptor)
	plt.savefig(filename, bbox_inches="tight")


def createGraph():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--file",
	    type=str,
	    required=True)
	args = parser.parse_args()
	fileName = args.file

	with open(fileName, "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()
	del readLines[0]

	updateFreqGraph = []
	for line in readLines:
		if ".cpp" in line or ".xml" in line or ".h" in line or ".txt" in line or ".c" in line or ".bp" in line or ".mk" in line or ".patch" in line or ".version" in line:
			continue
		else:
			splitStr = line.split()
			updateFreqGraph.append(splitStr[1])

	# Sort here
	updateFreqGraph = [item for items, c in Counter(updateFreqGraph).most_common() for item in [items] * c]

	printFreqFig(updateFreqGraph, "Frequency of Updates to Files Listed in Frameworks Security Bulletins", "freqGraphs/updateFreq_6years.png")


if __name__ == '__main__':
	createGraph()
