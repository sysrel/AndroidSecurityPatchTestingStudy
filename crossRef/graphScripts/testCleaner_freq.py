import os
import re
from collections import Counter


def main():
	with open("../scrapeData/cleanSecBulFreqTests.txt", "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()
	del readLines[0]

	# atestCVEs will be the unique CVEs containing atest information
	# testCVEs will be all the unique CVEs containing test information

	atestCVEs = []
	testCVEs = []
	for line in readLines:
		splitLine = line.split()
		if "atest" in line or "Atest" in line:
			if splitLine[0] not in atestCVEs:
				atestCVEs.append(splitLine[0])

	for i in range(len(readLines)-1):
		line = readLines[i]
		splitLine = line.split()
		if "CVE-" in line:
			if splitLine[0] not in testCVEs:
				testCVEs.append(splitLine[0])

	print("Number of unique CVEs containing atest information: " + str(len(atestCVEs)))
	print("Number of unique CVEs containing any test information: " + str(len(testCVEs)))

	print("\n")
	print("List of unique CVEs containing atest info")
	for cve in atestCVEs:
		print(cve)

	print("\n")
	print("List of unique CVEs containing any test info")
	for cve in testCVEs:
		print(cve)




if __name__ == '__main__':
	main()
