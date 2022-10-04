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

	delList = ["Android.mk", "AndroidManifest.xml", "OWNERS", "Android.bp", "AndroidTest.xml", "test-1.json", "test-2.json", "test-3.json", "test-4.json", "test-5.json", "test-6.json", "README.txt", "Utils.java", "Helper.java", "Components.java", "TestUtils.java", "test-7.json", "test-8.json", "test-9.json"]
	updateFreqGraph = []
	for line in testLines:
		splitStr = line.split()
		if len(splitStr) == 2:
			subSplit = splitStr[1].split(".java")
			if subSplit[1] not in delList:
				updateFreqGraph.append(subSplit[1] + ".java")
		else:
			if splitStr[2] not in delList:
				updateFreqGraph.append(splitStr[2])

	# Sort here
	updateFreqGraph = [item for items, c in Counter(updateFreqGraph).most_common() for item in [items] * c]
	updateFreqGraph = [d for d in updateFreqGraph if updateFreqGraph.count(d) > 200]

	fileToWrite = open("fullCrossRefOutSorted.txt", "w")
	for item in updateFreqGraph:
		print(item)
		fileToWrite.write(item + "\n")

	fileToWrite.close()
	
	printFreqFig(updateFreqGraph, "Frequency of Updates to Files Referenced in Test File Logs", "freqGraphs/fullTestCrossRefFreq_5years.png")


if __name__ == '__main__':
	createGraph()
