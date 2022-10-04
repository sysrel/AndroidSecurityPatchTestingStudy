from bs4 import BeautifulSoup
import argparse
import os
import requests
import re
import datetime
import numpy as np
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


def getInfoFromUpdatePage(page_url):
	base_url = "https://android.googlesource.com"
	# Might need to add a sleep delay	
	if base_url not in page_url:
		page = requests.get(base_url + page_url)
	else:
		page = requests.get(page_url)
	soup = BeautifulSoup(page.content, 'html.parser')

	file_name_list = []
	testFileName = ""
	if soup.ul != None:
		file_name_raw = (soup.ul.get_text()).split("[")
		file_name_list = []
	
		for i in range(len(file_name_raw) - 1):
			split_str = file_name_raw[i].split("/")
			file_name_list.append(split_str[-1])

		file_name_list = [i for i in file_name_list if not (']' in i)]

	commitMessage = soup.find("pre", class_="u-pre u-monospace MetadataMessage")

	bugIDs = []
	cveIDs = []
	testInfo = []
	containRevert = False
	if commitMessage != None:
		commitMessage = commitMessage.text
		splitMessage = commitMessage.split()
		if "revert" in splitMessage or "Revert" in splitMessage:
			containRevert = True
		elif "Fix" in splitMessage:
			idx = splitMessage.index("Fix")
			if "CVE" in splitMessage[idx+1]:
				containRevert = True
		elif "fix" in splitMessage:
			idx = splitMessage.index("fix")
			if "CVE" in splitMessage[idx+1]:
				containRevert = True
		
		for i in range(len(splitMessage)):
			if splitMessage[i] == "Bug:":
				bugIDs.append(splitMessage[i+1])
			elif "bug:" in splitMessage[i]:
				splitWord = splitMessage[i].split(":")
				if splitWord[-1] != None and splitWord[-1] != "bug":
					bugIDs.append(splitWord[-1])
			elif splitMessage[i] == "Test:" or splitMessage[i] == "Test":
				testString = []
				idx = i + 1
				curString = splitMessage[idx]
				testString.append(curString)
				while curString != "Merged-In:" and curString != "Change-Id:" and "bug:" not in curString and curString != "Bug:" and curString != "Test:" and (idx + 1) != len(splitMessage):
					idx = idx + 1
					curString = splitMessage[idx]
					testString.append(curString)
				if (idx + 1) != len(splitMessage):
					del testString[-1]
				testInfo.append(" ".join(testString))
				i = idx
			elif "CVE" in splitMessage[i]:
				cveIDs.append(splitMessage[i])

	if cveIDs == []:
		cveToPrint = "No CVEs in Desc."
	else:
		cveToPrint = cveIDs
	if bugIDs == []:
		bugToPrint = "No Bug IDs in Desc."
	else:
		bugToPrint = bugIDs
	if testInfo == []:
		testInfoToPrint = "No Test Info in Desc."
	else:
		testInfoToPrint = testInfo
	if containRevert:
		revertToPrint = commitMessage
	else:
		revertToPrint = "No Reversion"
	
	return [file_name_list, testInfoToPrint, bugToPrint, cveToPrint, revertToPrint]


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
					allFileRefs.append([curCVE, fileRefs[0], fileRefs[1], fileRefs[2], fileRefs[3], fileRefs[4]])
	
	return allFileRefs


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--url",
	    type=str,
	    required=False,
	    help=
	    "Specify the url for the files to check references for. (If Necessary)")
	parser.add_argument(
		"--years",
		type=int,
		required=True,
		help=
		"Number of years back from the present that you want to search through.")
	args = parser.parse_args()
	test_page_url = args.url

	# ALL OF THIS BELOW HERE WILL NEED TO BE CHANGED
	curYear = int(datetime.datetime.now().date().strftime("%Y"))

	securityBulletinFiles = []
	cveFiles = []
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
					# [CVE Reference, [Updated Files], [Testing Info], [Bug IDs], [Add'l CVEs Listed]]
					securityBulletinFiles.append([first, returnFiles[i][1], returnFiles[i][2], returnFiles[i][3], returnFiles[i][4], returnFiles[i][5]])
					for j in range(len(returnFiles[i][1])):
						line = returnFiles[i][1][j]
						if ".cpp"in line or ".xml" in line or ".h" in line or ".txt" in line or ".c" in line or ".bp" in line or ".mk" in line or ".patch" in line or ".version" in line:
							continue
						else:
							cveFiles.append(returnFiles[i][1][j])


	revertedFiles = []
	for fileInfo in securityBulletinFiles:
		if fileInfo[5] != "No Reversion":
			revertedFiles.append(fileInfo)
		 
    
	fileToWrite = open("scrapeData/revertCommits.txt", "w")
	print("\n\n")
	outputStr = "{0:<25}{1:<50}".format("CVE Reference", "Commit Description")
	print(outputStr)
	fileToWrite.write(outputStr + "\n")
	for testInfo in revertedFiles:
		outputStr = "{0:<25}{1:<50}".format(testInfo[0], testInfo[5])
		print(outputStr)
		fileToWrite.write(outputStr + "\n")

	fileToWrite.close()
			


if __name__ == '__main__':
	main()
