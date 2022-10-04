import os
import re
from collections import Counter


def main():
	with open("secBulletinFreqTests.txt", "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()
	del readLines[0]

	atestLines = []
	restLines = []
	for line in readLines:
		splitLine = line.split()
		if "atest" in splitLine or "Atest" in splitLine:
			newLine = splitLine[2:]	
			atestLines.append([splitLine[0], splitLine[1], " ".join(newLine)]) 
		else:
			restLines.append([splitLine[0], splitLine[1], " ".join(splitLine[2:])])


	fileToWrite = open("cleanSecBulFreqTests.txt", "w")
	outputStr = "Atest information listed first, all additional information subsequent"
	print("\n" + outputStr)
	fileToWrite.write(outputStr + "\n")
	outputStr = "{0:<20}{1:<40}{2:<50}".format("CVE Reference", "File Name", "Associated Test Information")
	print(outputStr)
	fileToWrite.write(outputStr + "\n")
	for fileInfo in atestLines:
		outputStr = "{0:<20}{1:<40}{2:<50}".format(fileInfo[0], fileInfo[1], fileInfo[2])
		print(outputStr)
		fileToWrite.write(outputStr + "\n")

	outputStr = "Additional Information Here"
	print("\n" + outputStr)
	fileToWrite.write("\n" + outputStr + "\n")

	for fileInfo in restLines:
		outputStr = "{0:<20}{1:<40}{2:50}".format(fileInfo[0], fileInfo[1], fileInfo[2])
		print(outputStr)
		fileToWrite.write(outputStr + "\n")


	fileToWrite.close()



if __name__ == '__main__':
	main()
