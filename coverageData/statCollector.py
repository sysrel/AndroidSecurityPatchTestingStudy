import argparse
import os
import re
from os.path import exists


def in_nested_list(my_list, item):
	for items in my_list:
		if item in items:
			return True
	return False

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--version",
		type=int,
		required=True)
	args = parser.parse_args()
	statDirectory = "/home/cdbrant/android_security/coverageData/v" + str(args.version)
	stats = []
	directoryFiles = os.listdir(statDirectory)

	for file in os.listdir(statDirectory):
		fileSplit = file.split("_")
		cvePartA = re.sub("[^0-9]", "", fileSplit[0])
		cvePartB = re.sub("[^0-9]", "", fileSplit[1])
		currStats = []
		if not file.endswith("_missing.txt"):
			cveRef = "CVE-" + cvePartA + "-" + cvePartB
			fileName = "v" + str(args.version) + "/" + file			
			with open(fileName, "r") as fileToRead:
				readLines = fileToRead.readlines()
		
			fileToRead.close()

			missingFileName = file.split(".")
			missingFileName = missingFileName[0]
			missingFileName = "v" + str(args.version) + "/" + missingFileName + "_missing.txt"
			missingReadLines = []
			if exists(missingFileName):
				with open(missingFileName, "r") as fileToRead:
					missingReadLines = fileToRead.readlines()
				
				fileToRead.close()

			perFileStatsSum = []
			perCVEStatsSum = []
			perFileStatsSum.append(["File Name", "Total # of Patch BBs", "# of Covered Patch BBs Entered","# of Covered Patch BBs Exited", "% of Patch BBs Covered"])
			perCVEStatsSum.append(["CVE Reference", "# of Patched Files", "Total # of Patch BBs", "# of Covered Patch BBs Entered", "# of Covered Patch BBs Exited", "% of Patch BBs Covered"])
			
			for line in readLines:
				if "---------" in line:
					continue	
				else:
					splitLine = line.split(":")
					allLineInfo = splitLine[3]
					lineInfo = allLineInfo.split()
					currLineInfo = " ".join(lineInfo)
		
					if currLineInfo not in currStats:
						currStats.append(currLineInfo)
						

			if currStats != []:
				currStats.sort()
				fileList = []
				currFileStatsSum = []
				for line in currStats:
					splitLine = line.split()
					fileInfo = splitLine[0]
					blockInfo = splitLine[1].split("/")
					accessInfo = splitLine[2:]
					accessInfo = " ".join(accessInfo)
					
					if not in_nested_list(fileList, fileInfo):
						if currFileStatsSum != []:
							perFileStatsSum.append(currFileStatsSum)
							currFileStatsSum = []

						fileList.append([fileInfo, blockInfo[0], accessInfo])

						if accessInfo == "Entry":
							currFileStatsSum = [fileInfo, int(blockInfo[1]), int(blockInfo[1]), 1, 0, str((1 / float(blockInfo[1])) * 100) + "%", "0.0%"]
						elif "Exit" in accessInfo:
							currFileStatsSum = [fileInfo, int(blockInfo[1]), int(blockInfo[1]), 0, 1, "0.0%", str((1 / float(blockInfo[1])) * 100) + "%"]
					else:
						if [fileInfo, blockInfo[0], accessInfo] not in fileList: 
							fileList.append([fileInfo, blockInfo[0], accessInfo])

							if accessInfo == "Entry":
								currFileStatsSum[3] = currFileStatsSum[3] + 1
								currFileStatsSum[5] = str((currFileStatsSum[3] / currFileStatsSum[1]) * 100) + "%"
							elif "Exit" in accessInfo:
								if "Exit A" in accessInfo:
									currFileStatsSum[2] = currFileStatsSum[2] + 1
								elif "Exit B" in accessInfo:
									continue
								currFileStatsSum[4] = currFileStatsSum[4] + 1 
								currFileStatsSum[6] = str((currFileStatsSum[4] / currFileStatsSum[2]) * 100) + "%"
					
				perFileStatsSum.append(currFileStatsSum)	

				for missingLine in missingReadLines:
					splitMissingLine = missingLine.split()
					perFileStatsSum.append([splitMissingLine[0], splitMissingLine[1], splitMissingLine[1], 0, 0, "0.0%", "0.0%"])
				
				# Now that file stas have been calculated in a list, calculate CVE stats
				totalNumPatchBBsEntry = 0
				totalNumPatchBBsExit = 0
				totalCoveredEntry = 0
				totalCoveredExit = 0
	
				fileStatsIter = iter(perFileStatsSum)
				next(fileStatsIter)

				for fileStats in fileStatsIter:
					totalNumPatchBBsEntry = totalNumPatchBBsEntry + int(fileStats[1])
					totalNumPatchBBsExit = totalNumPatchBBsExit + int(fileStats[2])
					totalCoveredEntry = totalCoveredEntry + int(fileStats[3])
					totalCoveredExit = totalCoveredExit + int(fileStats[4])

				perCVEStatsSum.append([cveRef, (len(perFileStatsSum)-1), totalNumPatchBBsEntry, totalNumPatchBBsExit, totalCoveredEntry, totalCoveredExit, str(((totalCoveredEntry / totalNumPatchBBsEntry) * 100)) + "%", str(((totalCoveredExit / totalNumPatchBBsExit) * 100)) + "%"])

				stats.append([cveRef, perCVEStatsSum, perFileStatsSum])
			else:
				emptyFileStats = []
				emptyFileStats.append(["File Name", "Total # of Patch BB Entrances", "Total # of Patch BB Exits", "# of Covered Patch BBs Entered","# of Covered Patch BBs Exited", "% of Patch BBs Entered", "% of Patch BBs Exited"])
				emptyCVEStats = []
				emptyCVEStats.append(["CVE Reference", "# of Patched Files", "Total # of Patch BB Entrances", "Total # of Patch BB Exits", "# of Covered Patch BBs Entered", "# of Covered Patch BBs Exited", "% of Patch BBs Entered", "% of Patch BBs Exited"])
				for missingLine in missingReadLines:
					splitMissingLine = missingLine.split()
					emptyFileStats.append([splitMissingLine[0], splitMissingLine[1], splitMissingLine[1], 0, 0, "0.0%", "0.0%"])

				fileStatsIter = iter(emptyFileStats)
				next(fileStatsIter)
			
				totalNumPatchBBs = 0
				for fileStats in fileStatsIter:
					totalNumPatchBBs = totalNumPatchBBs + int(fileStats[1])

				emptyCVEStats.append([cveRef, len(emptyFileStats)-1, totalNumPatchBBs, totalNumPatchBBs, 0, 0, "0.0%", "0.0%"])
				stats.append([cveRef, emptyCVEStats, emptyFileStats])
	
	for cve in stats:
		print("Statistics for " + cve[0] + "\n")
		
		for line in cve[1]:
			print(", ".join(str(e) for e in line)) 

		print("\n")
		
		for line in cve[2]:
			print(", ".join(str(e) for e in line))	
		
		print("\n")


if __name__ == '__main__':
	main()
