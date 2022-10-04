from bs4 import BeautifulSoup
import argparse
import os
import requests
import re
import datetime
import numpy as np

def extract_package(package_url):
	page_package = requests.get(package_url)
	soup_package = BeautifulSoup(page_package.content, 'html.parser')
	package_span = soup_package.find("span", string=re.compile("package"))
	package_container = package_span.parent
	package_str_raw = package_container.get_text()

	split_str = package_str_raw.split(" ")
	package_str_raw = split_str[1]
	package_str_raw = package_str_raw[:-1]
	package_split_str = package_str_raw.split(".")
	package_name = ""

	for name in package_split_str:
		if name != "com":
			package_name = package_name + "/" + name
	
	return package_name

def extract_class(class_url, class_index):
	base_url = "https://android.googlesource.com"
	page_class = requests.get(class_url)
	soup_class = BeautifulSoup(page_class.content, 'html.parser')
	class_link_list = soup_class.ul.find_all('a')
	class_link_list = class_link_list[0::2]
	class_names_raw = (soup_class.ul.get_text()).split("[")
	del class_names_raw[-1]

	class_names_list = []
	for class_name in class_names_raw:
		split_str = class_name.split("/")
		class_names_list.append(split_str[-1])

	package_url = base_url + class_link_list[class_index].get('href')
	package_name = extract_package(package_url)

	return package_name, class_names_list[class_index];


def getFilesFromUpdatePage(page_url):
	base_url = "https://android.googlesource.com"
	if base_url not in page_url:
		page = requests.get(base_url + page_url)
	else:
		page = requests.get(page_url)
	soup = BeautifulSoup(page.content, 'html.parser')
	file_link_list_raw = soup.ul.find_all('a')
	file_link_list_raw = file_link_list_raw[0::2]
	file_name_raw = (soup.ul.get_text()).split("[")
	file_name_list = []
	file_link_list = []	
	
	for i in range(len(file_name_raw) - 1):
		split_str = file_name_raw[i].split("/")
		fileExt = split_str[-1].split(".")
		if fileExt[-1] == "java":
			file_name_list.append(split_str[-1])
			file_link_list.append(file_link_list_raw[i].get("href"))

	package_name_list = []
	for i in range(len(file_link_list)):
		package_url = base_url + file_link_list[i]
		package_name_list.append(extract_package(package_url))


	return file_name_list, package_name_list


def getFileRefsFromBulletin(soup):
	allFileRefs = []
	cveSum = 0
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
				cveSum = cveSum + 1
				fileRefs, package_info = getFilesFromUpdatePage(columns[1].a.get("href"))
				# Append overall list
				allFileRefs.append((curCVE, fileRefs, package_info))

	return [allFileRefs, cveSum]


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--years",
		type=int,
		required=True,
		help=
		"Number of years back from the present that you want to search through.")
	parser.add_argument(
		"--outFile",
		type=str,
		required=True,
		help=
		"File name to print results out to.")
	args = parser.parse_args()

	# Retrieve list of all other files over the given time period from framework security bulletin posts
	curYear = int(datetime.datetime.now().date().strftime("%Y"))

	securityBulletinFiles = []
	cveSum = 0
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
			print(returnFiles)
			if returnFiles != None:
				cveNum = returnFiles[-1]
				returnFiles = returnFiles[0]
				cveSum = cveSum + cveNum
				for k in range(len(returnFiles)):
					for x in range(len(returnFiles[k][1])):
						securityBulletinFiles.append((returnFiles[k][0], returnFiles[k][1][x], returnFiles[k][2][x]))

	print("Number of total CVEs across the given time: " + str(cveSum))
	print("\n\n")
	fileToWrite = open(args.outFile, "w")
	outputStr = "{0:<20}{1:<50}{2:<50}".format("CVE Ref", "Class Name", "Package Name")
	fileToWrite.write(outputStr + "\n")
	for fileRef in securityBulletinFiles:
		cve = re.sub(r"[\t\n\s]*", "", fileRef[0])
		fileName = re.sub(r"[\t\n\s]*", "", fileRef[1])
		packageName = re.sub(r"[\t\n\s]*", "", fileRef[2])
		outputStr = "{0:<20}{1:<50}{2:<50}".format(cve, fileName, packageName)
		print(outputStr)
		fileToWrite.write(outputStr + "\n")

	fileToWrite.close()





if __name__ == '__main__':
	main()
