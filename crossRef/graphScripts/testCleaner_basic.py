import os
import re
from collections import Counter


def main():
	with open("../scrapeData/secBulletinTestInfo.txt", "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()

	# atestCVEs will be the unique CVEs containing atest information
	# testCVEs will be all the unique CVEs containing test information

	toRemove = [".xml ", ".java ", ".cpp ", ".h ", "CVE Reference", ".c ", ".bp ", ".version ", ".patch ", ".version ", ".aidl ", ".mk ", "No Test Info in Desc.", ".proto ", "None", "none", ".cc ", "N/A", ".js ", "Tested on a device"]
	newReadLines = []
	removedLines = []
	
	for line in readLines:
		if not any(item in line for item in toRemove):
			appendLine = line.strip()
			if appendLine != "":
				newReadLines.append(appendLine)
		else:
			removedLines.append(line)

	atestCVEs = []
	atestLines = []
	testCVEs = []
	adbCVEs = []
	adbLines = []
	manualCVEs = []
	manualLines = []
	buildCVEs = []
	buildLines = []
	pocCVEs = []
	pocLines = []
	tradefedLines = []
	tradefedCVEs = []

	readLines = newReadLines
	buildKeys = [" m ", " builds ", " compile", " Compile", " compiles ", " builds"]

	for line in readLines:
		splitLine = line.split()
		if "atest" in line or "Atest" in line:
			atestLines.append(line)
			if splitLine[0] not in atestCVEs and splitLine[0] not in testCVEs:
				atestCVEs.append(splitLine[0])
				testCVEs.append(splitLine[0])
		elif "manual" in line or "Manual" in line:
			manualLines.append(line)
			if splitLine[0] not in manualCVEs and splitLine[0] not in testCVEs:
				manualCVEs.append(splitLine[0])
				testCVEs.append(splitLine[0])
		elif any(item in line for item in buildKeys):
			buildLines.append(line)
			if splitLine[0] not in buildCVEs and splitLine[0] not in testCVEs:
				buildCVEs.append(splitLine[0])
				testCVEs.append(splitLine[0])
		elif " PoC " in line or " POC " in line or " poc" in line:
			pocLines.append(line)
			if splitLine[0] not in pocCVEs and splitLine[0] not in testCVEs:
				pocCVEs.append(splitLine[0])
				testCVEs.append(splitLine[0])
		elif "run cts" in line or "cts-tradefed" in line or "tradefed" in line:
			tradefedLines.append(line)
			if splitLine[0] not in tradefedCVEs and splitLine[0] not in testCVEs:
				tradefedCVEs.append(splitLine[0])
				testCVEs.append(splitLine[0])

		if splitLine[0] not in testCVEs:
			testCVEs.append(splitLine[0])

	uncategorized = []
	for line in readLines:
		if line not in atestLines and line not in manualLines and line not in buildLines and line not in pocLines and line not in tradefedLines:
			uncategorized.append(line)
	print("List of atest categorized lines")
	for line in atestLines:
		print(line)

	print("\nList of manually tested categorized lines")
	for line in manualLines:
		print(line)

	print("\nList of PoC categorized lines")
	for line in pocLines:
		print(line)
	
	print("\nList of make/build categorized lines")
	for line in buildLines:
		print(line)

	print("\nList of tradefed categorized lines")
	for line in tradefedLines:
		print(line)

	print("Number of unique CVEs containing atest information: " + str(len(atestCVEs)))
	print("Number of unique CVEs that just state to test manually: " + str(len(manualCVEs)))
	print("Number of unique CVEs in the PoC category: " + str(len(pocCVEs)))
	print("Number of unique CVEs in the 'make/build' category: " + str(len(buildCVEs)))
	print("Number of unique CVEs in the tradefed category: " + str(len(tradefedCVEs)))
	print("Number of unique CVEs containing any test information: " + str(len(testCVEs)))

	print("\n")
	print("List of lines that contain uncategorized test information, total num: " + str(len(uncategorized)))
	for line in uncategorized:
		print(line)


if __name__ == '__main__':
	main()
