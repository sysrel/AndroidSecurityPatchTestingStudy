import argparse
import os
import re
from collections import Counter


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--file",
		type=str,
		required=True,
		help=
		"File name to summarize statistics from.")
	args = parser.parse_args()
	
	with open(args.file, "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()
	del readLines[0]

	cveLines = []
	javaLines = []
	for line in readLines:
		splitLine = line.split()
		if splitLine[0] not in cveLines:
			cveLines.append(splitLine[0])
		if splitLine[1] not in javaLines:
			javaLines.append(splitLine[1])

	print("Number of unique CVEs Java classes are updated over: " + str(len(cveLines)))
	print("Number of unique Java classes updated over the last 6 years: " + str(len(javaLines)))
	print("\n")
	for javaClass in javaLines:
		print(javaClass)

if __name__ == '__main__':
	main()
