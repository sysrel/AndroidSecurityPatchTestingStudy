import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--file",
		type=str,
		required=True,
		help="Specify the file to create a table from it's data.")
	args = parser.parse_args()
	fileName = args.file

	with open(fileName, "r") as fileToRead:
		readLines = fileToRead.readlines()

	switch = 0
	bugIDs = []
	cveIDs = []
	for line in readLines:	
		if len(line.split()) == 3:
			bugIDs.append(line.split())
		elif len(line.split()) == 2:
			cveIDs.append(line.split())

	bugIDs.insert(0, ["Test File Info", "Cross Referenced Bug ID", "Corresponding CVE"])
	cveIDs.insert(0, ["Test File Info", "Cross Referenced CVE"])

	fig, ax = plt.subplots()
	table = ax.table(cellText=bugIDs, loc='center')
	table.set_fontsize(14)
	table.scale(1,2)	
	ax.axis('off')
	plt.savefig("bugIDsOut.png")
	
	fig, ax = plt.subplots()
	table = ax.table(cellText=cveIDs, loc='center')
	table.set_fontsize(14)
	table.scale(1,2)
	ax.axis('off')
	plt.savefig("cveIDsOut.png")


if __name__ == '__main__':
	main()
