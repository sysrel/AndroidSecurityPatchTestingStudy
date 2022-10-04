import os
import re
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--file",
		type=str,
		required=True,
		help=
		"File Name to read through.")
	args = parser.parse_args()

	with open(args.file, "r") as fileToRead:
		readLines = fileToRead.readlines()

	fileToRead.close()

	uniqueCVEs = []
	for line in readLines:
		splitLine = line.split()
		if splitLine != []:
			if splitLine[0] not in uniqueCVEs and "CVE-" in splitLine[0]:
				uniqueCVEs.append(splitLine[0])

	uniqueCVEs.sort()
	print(len(uniqueCVEs))


if __name__ == '__main__':
	main()
