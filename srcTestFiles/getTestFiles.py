from bs4 import BeautifulSoup
import argparse
import os
import requests
import base64

def getFiles(page_url, dirList):
	base_url = "https://android.googlesource.com"
	base_filePath = "/home/cdbrant/android_security/srcTestFiles/"
	base_page = requests.get(page_url)
	soup_files = BeautifulSoup(base_page.content, 'html.parser')
	files_link_list = soup_files.ul.find_all('a')
	files_link_list = files_link_list[0::2]
	files_names_raw = (soup_files.ul.get_text()).split("[")
	del files_names_raw[-1]

	file_names_list = []
	for file_name in files_names_raw:
		split_str = file_name.split("/")
		file_names_list.append(split_str[-1])

	for i in range(len(files_link_list)):
		file_url = base_url + files_link_list[i].get('href') + "?format=TEXT"
		response = requests.get(file_url)
		data = response.text
		fileData = base64.b64decode(data)
		for j in range(len(dirList)):
			totalFilePath = base_filePath + "v" + dirList[j] + "/" + file_names_list[i]
			fileToWrite = open(totalFilePath, "wb")
			fileToWrite.write(fileData)
			fileToWrite.close()


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--url",
	    type=str,
	    required=True,
	    help=
	    "Specify the url for the patch to have files downloaded for."
	)
	parser.add_argument("--versions",
	                    nargs='+',
	                    help="Version(s) that are affected by this update.")
	args = parser.parse_args()
	page_url = args.url
	dirList = args.versions
	getFiles(page_url, dirList)

if __name__ == '__main__':
	main()
