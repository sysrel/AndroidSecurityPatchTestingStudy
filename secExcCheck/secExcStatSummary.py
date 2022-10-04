import argparse
import os
import re
import matplotlib.pyplot as plt

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--version",
		type=int,
		required=True,
		help=
		"AOSP Version Number to summarize stats for.")
	args = parser.parse_args()
	
	if args.version == 9:
		prefix = "pie"
	elif args.version == 10:
		prefix = "android10"
	elif args.version == 11:
		prefix = "android11"
	else:
		print("Invalid version. Please enter 9, 10, or 11.")
		exit(1)	

	throwFile = prefix + "SecExcThrow.txt"
	catchFile = prefix + "SecExcCatch.txt"
	updatedFile = "../allFilesPackages_throughMarch2022.txt"

	with open(throwFile, "r") as fileToRead:
		throwLines = fileToRead.readlines()
	fileToRead.close()

	with open(catchFile, "r") as fileToRead:
		catchLines = fileToRead.readlines()
	fileToRead.close()

	with open(updatedFile, "r") as fileToRead:
		updatedLines = fileToRead.readlines()
	fileToRead.close()

	updatedFiles = []
	for line in updatedLines:
		splitLine = line.split()
		if splitLine[1] != "" and splitLine[1].endswith(".java"):
			if splitLine[1] not in updatedFiles:
				updatedFiles.append(splitLine[1])

	throwFiles = []
	for line in throwLines:
		splitLine = line.split(":")
		splitName = splitLine[0].split("/")
		if splitName[-1] not in throwFiles:
			throwFiles.append(splitName[-1])

	catchFiles = []
	for line in catchLines:
		splitLine = line.split(":")
		splitName = splitLine[0].split("/")
		if splitName[-1] not in catchFiles:
			catchFiles.append(splitName[-1])

	bothFiles = []
	for fileName in throwFiles:
		if fileName in catchFiles:
			bothFiles.append(fileName)

	for line in bothFiles:
		throwFiles.remove(line)
		catchFiles.remove(line)		

	updatedThrowFiles = set(updatedFiles).intersection(set(throwFiles))
	updatedCatchFiles = set(updatedFiles).intersection(set(catchFiles))
	updatedBothFiles = set(updatedFiles).intersection(set(bothFiles))


	print("Total Number of Unique Java Files that throw Security Exceptions: " + str(len(throwFiles)))
	print("Total Number of Unique Java Files that catch Security Exceptions: " + str(len(catchFiles)))
	print("Total Number of Unique Java Files that both throw and catch Security Exceptions: " + str(len(bothFiles)))
	print("\n")
	print("Total Number of Unique Java Files Updated: " + str(len(updatedFiles)))
	print("Total Number of Unique Java Files with any Security Exception functions: " + str(len(throwFiles) + len(catchFiles) + len(bothFiles)))
	print("Total Number of Unique Java Files Upated that contain any Security Exception functions: " + str(len(updatedThrowFiles) + len(updatedCatchFiles) + len(updatedBothFiles)))
	print("Total Number of Unique Java Files Updated that throw Security Exceptions: " + str(len(updatedThrowFiles)))
	print("Total Number of Unique Java Files Updated that catch Security Exceptions: " + str(len(updatedCatchFiles)))
	print("Total Number of Unique Java Files Updated that throw and catch Security Exceptions: " + str(len(updatedBothFiles)))
	print("\n")
	lenTotalFiles = len(throwFiles) + len(catchFiles) + len(bothFiles)
	throwNotUpdated = len(throwFiles) - len(updatedThrowFiles)
	catchNotUpdated = len(catchFiles) - len(updatedCatchFiles)
	bothNotUpdated = len(bothFiles) - len(updatedBothFiles)
	notUpdatedThrowPercentage = (throwNotUpdated / lenTotalFiles) * 100
	notUpdatedCatchPercentage = (catchNotUpdated / lenTotalFiles) * 100
	notUpdatedBothPercentage = (bothNotUpdated / lenTotalFiles) * 100	
	updatedThrowPercentage = (len(updatedThrowFiles) / lenTotalFiles) * 100
	updatedCatchPercentage = (len(updatedCatchFiles) / lenTotalFiles) * 100
	updatedBothPercentage = (len(updatedBothFiles) / lenTotalFiles) * 100
	percentageCheck = notUpdatedThrowPercentage + notUpdatedCatchPercentage + notUpdatedBothPercentage + updatedThrowPercentage + updatedCatchPercentage + updatedBothPercentage
	print("Percentage of updated security exception files that throw: " + str(updatedThrowPercentage) + "%")
	print("Percentage of non-updated security exception files that throw: " + str(notUpdatedThrowPercentage) + "%")
	print("Percentage of updated security exception files that catch: " + str(updatedCatchPercentage) + "%")
	print("Percentage of non-updated security exception files that catch: " + str(notUpdatedCatchPercentage) + "%")
	print("Percentage of updated security exception files that both throw and catch: " + str(updatedBothPercentage) + "%")
	print("Percentage of non-updated security exception files that throw and catch: " + str(notUpdatedBothPercentage) + "%")
	print("Percentage total check: " + str(percentageCheck) + "%")
	print("\n")

	notUpdatedThrowPercentageStr = str(format(notUpdatedThrowPercentage, ".1f")) + "%"
	updatedThrowPercentageStr = str(format(updatedThrowPercentage, ".1f")) + "%"
	notUpdatedCatchPercentageStr = str(format(notUpdatedCatchPercentage, ".1f")) + "%"
	updatedCatchPercentageStr = str(format(updatedCatchPercentage, ".1f")) + "%"
	notUpdatedBothPercentageStr = str(format(notUpdatedBothPercentage, ".1f")) + "%"
	updatedBothPercentageStr = str(format(updatedBothPercentage, ".1f")) + "%"

	pctLabels = [notUpdatedThrowPercentageStr, updatedThrowPercentageStr, notUpdatedCatchPercentageStr, updatedCatchPercentageStr, notUpdatedBothPercentageStr, updatedBothPercentageStr]

	plotData = [notUpdatedThrowPercentage, updatedThrowPercentage, notUpdatedCatchPercentage, updatedCatchPercentage, notUpdatedBothPercentage, updatedBothPercentage]
	plotLabels = ["Throws SE/Not Updated" + " - " + str(pctLabels[0]), "Throws SE/Updated" + " - " + str(pctLabels[1]), "Catch SE/Not Updated" + " - " + str(pctLabels[2]), "Catch SE/Updated" + " - " + str(pctLabels[3]), "T&C SE/Not Updated" + " - " + str(pctLabels[4]), "T&C SE/Updated" + " - " + str(pctLabels[5])]
	titleStr = "Android v" + str(args.version) + " Files Containing Security Exception Functions"	
	fileStr = "secExcChart_v" + str(args.version) + ".png"

	plt.pie(plotData, labels=plotLabels, startangle=90, labeldistance=1.15)
	plt.title(titleStr)
	plt.savefig(fileStr, bbox_inches="tight")



if __name__ == '__main__':
	main()
