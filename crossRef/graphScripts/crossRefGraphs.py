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

def getLogLinks(page_url, years):
	base_url = "https://android.googlesource.com"
	page = requests.get(base_url + page_url)
	soup = BeautifulSoup(page.content, 'html.parser')
	logLink = soup.find("div", class_="u-sha1 u-monospace BlobSha1")
	logLink = logLink.find("a", text=re.compile(r'log'))
	logLink = logLink.get("href")
	
	# Now get all log update links
	page = requests.get(base_url + logLink)
	soup = BeautifulSoup(page.content, 'html.parser')
	updateLinksList = soup.ol.find_all("li")
	updateLinks = soup.ol.li

	logLinks = []
	linkTag = updateLinks.find_all("a")
	timeStamp = updateLinks.find("span", class_="CommitLog-time")
	timeStamp = timeStamp.text
	timeSplit = timeStamp.split(" ")
	if ("months" in timeSplit[2]) or (("years" in timeSplit[2]) and int(timeSplit[1]) <= years):
		logLinks.append(linkTag[1].get("href"))

	for i in range(1, len(updateLinksList)):
		updateLinks = updateLinks.next_sibling
		linkTag = updateLinks.find_all("a")
		timeStamp = updateLinks.find("span", class_="CommitLog-time")
		timeStamp = timeStamp.text
		timeSplit = timeStamp.split(" ")
		if ("months" in timeSplit[2]) or (("years" in timeSplit[2])  and int(timeSplit[1]) <= years):
			logLinks.append(linkTag[1].get("href"))
	
	return logLinks
	

def getTestFiles(page_url):
	base_page = requests.get(page_url)
	soup_files = BeautifulSoup(base_page.content, 'html.parser')
	files_link_list = soup_files.ol.find_all('li')
	files_link_obj = soup_files.ol.li
	fileLinks = [files_link_obj.a.get("href")]
	for i in range(len(files_link_list) - 1):
		files_link_obj = files_link_obj.next_sibling
		fileLinks.append(files_link_obj.a.get("href"))

	fileNames = []
	for j in range(len(fileLinks)):
		fileStr = fileLinks[j].split("/")
		fileNames.append(fileStr[-1])

	return fileLinks, fileNames


def getFilesFromUpdatePage(page_url):
	base_url = "https://android.googlesource.com"
	if base_url not in page_url:
		page = requests.get(base_url + page_url)
	else:
		page = requests.get(page_url)
	soup = BeautifulSoup(page.content, 'html.parser')
	file_name_raw = (soup.ul.get_text()).split("[")
	file_name_list = []
	
	for i in range(len(file_name_raw) - 1):
		split_str = file_name_raw[i].split("/")
		file_name_list.append(split_str[-1])

	file_name_list = [i for i in file_name_list if not (']' in i)]

	return file_name_list


def getFileRefsFromBulletin(soup):
	allFileRefs = []
	result = soup.find('h3', id="framework")
	if result is None:
		result = soup.find('h3', id="framework-01")
	if result is None:
		return
	table = result.find_next('table')
	aosp_ver_idx = -1
	table_rows = table.findAll('tr')
	for i in range(1, len(table_rows)):
		columns = table_rows[i].findAll('td')
		fileRefs = []
		if columns[1].a != None:
			if columns[1].a.get("href") != "#asterisk":
				curCVE = columns[0].text
				fileRefs = getFilesFromUpdatePage(columns[1].a.get("href"))
				# Append overall list
				allFileRefs.append((curCVE, fileRefs))

	return allFileRefs


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--url",
	    type=str,
	    required=True,
	    help=
	    "Specify the url for the patch to have files downloaded for.")
	parser.add_argument(
		"--years",
		type=int,
		required=True,
		help=
		"Number of years back from the present that you want to search through.")
	args = parser.parse_args()
	test_page_url = args.url

	# Get test file links and names
	
	testFileLinks, testFileNames = getTestFiles(test_page_url)

	# Get log links for each test file
	testLogLinks = []
	print("\nRetrieving Log Links for " + str(len(testFileLinks)) + " total elements.")
	for i in range(len(testFileLinks)):
		print("Getting Log Links for element #" + str(i))
		nextLinks = getLogLinks(testFileLinks[i], args.years)
		for item in nextLinks:
			testLogLinks.append((testFileNames[i], item))

	# Retrieve all files that the log update links list
	logFiles = []
	print("\nRetrieving files listed in Log Updates for " + str(len(testLogLinks)) + " total links.")
	for i in range(len(testLogLinks)):
		nextFiles = getFilesFromUpdatePage(testLogLinks[i][1])
		for j in range(len(nextFiles)):
			logFiles.append((testLogLinks[i][0], nextFiles[j]))

	# Retrieve list of all other files over the given time period from framework security bulletin posts
	curYear = int(datetime.datetime.now().date().strftime("%Y"))

	securityBulletinFiles = []
	for i in range(args.years):
		testYear = curYear - i
		for j in range(11, -1, -1):
			if j < 9:
				jter = "0" + str(j + 1)
			else:
				jter = str(j + 1)
			url = "https://source.android.com/security/bulletin/{}-{}-01".format(testYear, jter)
			print("Retrieving Security Bulletin File Names from " + str(testYear) + "-" + str(jter) + "-01")
			page = requests.get(url)
			soup = BeautifulSoup(page.content, 'html.parser')
			returnFiles = getFileRefsFromBulletin(soup)
			if returnFiles != None:
				for k in range(len(returnFiles)):
					for x in range(len(returnFiles[k][1])):
						securityBulletinFiles.append((returnFiles[k][0], returnFiles[k][1][x]))

	crossRefFiles = []
	for i in range(len(logFiles)):
		for j in range(len(securityBulletinFiles)):
			if logFiles[i][1] == securityBulletinFiles[j][1]:
				cve = re.sub(r"[\n\t\s]*", "", securityBulletinFiles[j][0])
				refFileName = re.sub(r"[\n\t\s]*", "", logFiles[i][1])
				testFileName = re.sub(r"[\n\t\s]*", "", logFiles[i][0])
				cve = re.sub(r"[\t\n\s]*", "", securityBulletinFiles[j][0])
				refFile = re.sub(r"[\t\n\s]*", "", logFiles[i][1])
				testFile = re.sub(r"[\t\n\s]*", "", logFiles[i][0])
				crossRefFiles.append((cve, refFile, testFile))

	crossRefsSort = list(set(crossRefFiles))
	crossRefsSort.sort(key=lambda y: y[0])

	print("\n\n")	
	fileToWrite = open("crossRefOut.txt", "w")
	outputStr = "{0:<20}{1:<40}{2:<50}".format("CVE Reference", "Cross Referenced File", "Test File")
	print(outputStr)
	fileToWrite.write(outputStr)
	for crossRef in crossRefsSort:
		outputStr = "{0:<20}{1:<40}{2:<50}".format(crossRef[0], crossRef[1], crossRef[2])
		print(outputStr)
		fileToWrite.write(outputStr)

	fileToWrite.close()


def printFreqFig(values, descriptor, filename):
	# Check to make sure you can plot it with the current number of legend colors
	colors = ["orange", "blue", "green", "purple", "red", "brown", "pink", "olive", "cyan", "silver", "black"]
	legendList = list(list(zip(*values))[1])
	legendLabels = list(set(legendList))
	if len(legendLabels) > len(colors):
		colorsNec = len(legendLabels) - len(colors)
		print(str(colorsNec) + " more legend colors are necessary to plot this graph.")
		exit(1)

	plotVals = [None] * len(legendLabels)
	for i in range(len(legendLabels)):
		plotVals[i] = []
	for i in range(len(values)):
		for j in range(len(legendLabels)):
			if values[i][1] == legendLabels[j]:
				plotVals[j].append(values[i][0])

	allFiles = []
	for i in range(len(plotVals)):
		plotVals[i] = [item for items, c in Counter(plotVals[i]).most_common() for item in [items] * c]
		for item in plotVals[i]:
			allFiles.append(item)

	allFiles = [item for items, c in Counter(allFiles).most_common() for item in [items] * c]

	numBinsGraph = len(list(set(allFiles)))
	figWidth = round((numBinsGraph/3)/10)*10
	fig = plt.figure(figsize=(figWidth,6)).gca()
	fig.yaxis.set_major_locator(MaxNLocator(integer=True))
	N, bins, patches = plt.hist(plotVals, numBinsGraph, ec="k", color=colors[:len(legendLabels)], histtype="barstacked", align="mid")
	xticks =[(bins[idx+1] + value)/2 for idx, value in enumerate(bins[:-1])]
	plt.xticks(xticks, fontsize=8, rotation='vertical')
	plt.ylabel("Frequency")
	plt.title(descriptor)
	handles = [Rectangle((0,0), 1, 1, color=c, ec="k") for c in colors]
	plt.legend(handles[:len(legendLabels)], legendLabels)
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

	crossRefsGraph = []
	for line in readLines:
		splitStr = line.split()
		crossRefsGraph.append((splitStr[1], splitStr[2]))

	legendList = list(list(zip(*crossRefsGraph))[1])
	legendLabels = list(set(legendList))
	numTypes = [0] * len(legendLabels)
	for i in range(len(crossRefsGraph)):
		for j in range(len(legendLabels)):
			if crossRefsGraph[i][1] == legendLabels[j]:
				numTypes[j] = numTypes[j] + 1

	# Sort here
	crossRefsGraph = tuple(crossRefsGraph)
	#crossRefsGraph = [item for items, c in Counter(crossRefsGraph).most_common() for item in [items] * c]
	#crossRefsGraph = tuple(crossRefsGraph)

	#printFreqFig(np.array(testCrossRefsGraph), "Frequency of Security Related Files Referenced in Update Logs for Permission Tests", "freqGraphs/permTestCrossRefsGraph.png")



	#printFreqFig(crossRefsGraph, "Frequency of Security Related Files Referenced in Update Logs for Permission Tests", "freqGraphs/permTestCrossRefsGraph.png")

	printFreqFig(crossRefsGraph, "Frequency of Security Related Files Referenced in Update Logs for Platform Test Files", "freqGraphs/allTestCrossRefsGraph.png")



if __name__ == '__main__':
	createGraph()
