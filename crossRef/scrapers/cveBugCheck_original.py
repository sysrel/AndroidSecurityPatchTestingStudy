from bs4 import BeautifulSoup
import argparse
import os
import requests
import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


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


def getInfoFromUpdatePage(page_url):
	base_url = "https://android.googlesource.com"
	if base_url not in page_url:
		page = requests.get(base_url + page_url)
	else:
		page = requests.get(page_url)
	soup = BeautifulSoup(page.content, 'html.parser')

	testFileName = ""
	if soup.ul != None:
		file_name_raw = (soup.ul.get_text()).split("[")
		file_name_list = []
	
		for i in range(len(file_name_raw) - 1):
			split_str = file_name_raw[i].split("/")
			file_name_list.append(split_str[-1])

		file_name_list = [i for i in file_name_list if not (']' in i)]

		for i in range(len(file_name_list)):
			if "Test" in file_name_list[i]:
				testFileName = file_name_list[i]

	commitMessage = soup.find("pre", class_="u-pre u-monospace MetadataMessage")

	bugIDs = []
	cveIDs = []	
	if commitMessage != None:
		commitMessage = commitMessage.text
		splitMessage = commitMessage.split()
		
		for i in range(len(splitMessage)):
			if splitMessage[i] == "Bug:":
				bugIDs.append(splitMessage[i+1])
			elif "CVE" in splitMessage[i]:
				cveIDs.append(splitMessage[i])

	if testFileName == "" and bugIDs == [] and cveIDs == []:
		return None
	else:
		return [testFileName, bugIDs, cveIDs]


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
				fileRefs = getInfoFromUpdatePage(columns[1].a.get("href"))
				# Append overall list
				if fileRefs != None:
					allFileRefs.append([curCVE, fileRefs[0], fileRefs[1], fileRefs[2]])

	return allFileRefs


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--url",
	    type=str,
	    required=True,
	    help=
	    "Specify the url for the files to check references for.")
	parser.add_argument(
		"--years",
		type=int,
		required=True,
		help=
		"Number of years back from the present that you want to search through.")
	args = parser.parse_args()
	test_page_url = args.url

	testFileLinks, testFileNames = getTestFiles(test_page_url)

	newTestFileLinks = []
	newTestFileNames = []
	for i in range(len(testFileLinks)):
		if testFileNames[i] != "":
			newTestFileLinks.append(testFileLinks[i])
			newTestFileNames.append(testFileNames[i])
	
	testFileLinks = newTestFileLinks
	testFileNames = newTestFileNames	


	# Get log links for each test file
	testLogLinks = []
	print("\nRetrieving Log Links for " + str(len(testFileLinks)) + " total elements.")
	for i in range(len(testFileLinks)):
		print("Getting Log Links for element #" + str(i))
		nextLinks = getLogLinks(testFileLinks[i], args.years)
		for item in nextLinks:
			testLogLinks.append((testFileNames[i], item))

	# Retrieve all files that the log update links list
	logInfo = []
	print("\nRetrieving files listed in Log Updates for " + str(len(testLogLinks)) + " total links.")
	for i in range(len(testLogLinks)):
		nextInfo = getInfoFromUpdatePage(testLogLinks[i][1])
		if nextInfo != None:
			infoList = [testLogLinks[i][0], nextInfo[0], nextInfo[1], nextInfo[2]]
			logInfo.append(infoList)

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
				for i in range(len(returnFiles)):
					first = ""
					second = ""
					if returnFiles[i][0] != None and returnFiles[i][0] != "":
						first = re.sub(r"[\t\n\s]*", "", returnFiles[i][0])
					if returnFiles[i][1] != None and returnFiles[i][1] != "":
						second = re.sub(r"[\t\n\s]*", "", returnFiles[i][1])
					securityBulletinFiles.append([first, second, returnFiles[i][2], returnFiles[i][3]])

	bugIDRefInfo = []
	cveRefInfo = []
	for i in range(len(logInfo)):
		for j in range(len(securityBulletinFiles)):
			for k in range(len(logInfo[i][2])):
				for x in range(len(securityBulletinFiles[j][2])):
					if logInfo[i][2][k] == securityBulletinFiles[j][2][x]:
						bugIDRefInfo.append([logInfo[i][0], logInfo[i][2][k], securityBulletinFiles[j][0]])
			for k in range(len(logInfo[i][3])):
				if logInfo[i][3][k] == securityBulletinFiles[j][0]:
					cveRefInfo.append([logInfo[i][0], logInfo[i][3][k]])

	fileToWrite = open("bugRefOut.txt", "w")
	outputStr = "{0:<40}{1:<25}{2:<20}".format("Test File Info", "Cross Referenced Bug ID", "Corresponding CVE")
	print(outputStr)
	fileToWrite.write(outputStr + "\n")
	for bugRef in bugIDRefInfo:
		outputStr = "{0:<40}{1:<25}{2:<20}".format(bugRef[0], bugRef[1], bugRef[2])
		print(outputStr)
		fileToWrite.write(outputStr + "\n")

	print("\n\n")
	fileToWrite.write("\n\n")
	outputStr = "{0:<40}{1:<20}".format("Test File Info", "Cross Referenced CVE")
	print(outputStr)
	fileToWrite.write(outputStr + "\n")
	for cveRef in cveRefInfo:
		outputStr = "{0:<40}{1:<20}".format(cveRef[0], cveRef[1])
		print(outputStr)
		fileToWrite.write(outputStr + "\n")

	fileToWrite.close()




if __name__ == '__main__':
	main()
