from bs4 import BeautifulSoup
import argparse
import csv
import os
import requests
import re
import calendar


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

def extract_types(type_url):
	type_str = ""
	page_type = requests.get(type_url)
	soup_type = BeautifulSoup(page_type.content, 'html.parser')
	file_name_raw = (soup_type.ul.get_text()).split("[")
	file_name_list = []
	file_name_list.append((file_name_raw[0].split("."))[1])
	for i in range(1, len(file_name_raw) - 1):
		split_str = file_name_raw[i].split("]")
		file_type_str = split_str[1].split(".")
		file_name_list.append(file_type_str[1])

	type_names = []

	for split_str in file_name_list:
		if split_str == "java" or split_str == "aidl":
			type_names.append("java")
		elif split_str == "cpp" or split_str == "xml":
			type_names.append("native")

	return type_names


def extract_native(native_url, url_index):
	page_native = requests.get(native_url)
	soup_native = BeautifulSoup(page_native.content, 'html.parser')
	file_name_raw = (soup_native.ul.get_text()).split("[")
	file_name_list = []
	file_name_list.append(file_name_raw[0])
	for i in range(1, len(file_name_raw) - 1):
		split_str = file_name_raw[i].split("]")
		file_name_list.append(split_str[1])	

	file_names_list = []
	for item in file_name_list:
		split_str = item.split("/")
		file_names_list.append(split_str[-1])

	return file_names_list[url_index]


def extract_section(soup, _id, out_dir, year, month):
	result = soup.find('h3', id=_id)
	if result is None:
		return
	table = result.find_next('table')
	output_rows = []
	x = 0
	aosp_ver_idx = -1
	for table_row in table.findAll('tr'):
		if x == 0:
			columns = table_row.findAll('th')
		else:
			columns = table_row.findAll('td')
		output_row = []
		y = 0
		urls = []
		ignore_row = False
		for column in columns:
			if x == 0:
				if y == 1 or column.text == 'References':
					output_row.append('Reference ID(s)')
				else:
					output_row.append(column.text.strip())
			else:
				for url in column.findAll('a'):
					href = url.get('href')
					if href is not None:
						urls.append(href)
				text = column.text.strip().split(
				    '\n')[0] if '\n' in column.text else column.text
				output_row.append(text.strip())
			y += 1
		if x == 0:
			output_row.append('Reference URLs')
			output_row.append('Package')
			output_row.append('Class(es)')
			output_row.append('Native')
			output_row.append('Month')
			output_row.append('Year')
			x = 1
		else:
			output_row.append(';'.join(urls))
			types = []
			package_string = ""
			class_string = ""
			native_string = ""
			
			if len(urls) != 0:
				if urls[0] == "#asterisk":
					continue
				else:
					types = extract_types(urls[0])

					for i in range(len(types)):
						if types[i] == "java":
							package_info, class_info = extract_class(urls[0], i)

							if package_string == "":
								package_string = package_info
							else:
								package_string = package_string + " & " + package_info

							if class_string == "":
								class_string = class_info
							else:
								class_string = class_string + " & " + class_info 
						
						elif types[i] == "native": 
							native_info = extract_native(urls[0], i)
							
							if native_string == "":
								native_string = native_info
							else:
								native_string = native_string + " & " + native_info				


					output_row.append(package_string)
					output_row.append(class_string)
					output_row.append(native_string) 
					output_row.append(calendar.month_name[int(month)])
					output_row.append(year)
			else:
				output_row.append(" ")
				output_row.append(" ")
				output_row.append(" ")
				output_row.append(calendar.month_name[int(month)])
				output_row.append(year)
		if not ignore_row:
			output_rows.append(output_row)
	
	fname = _id + '.csv'
	if out_dir is not None:
		if not os.path.isdir(out_dir):
			os.mkdir(out_dir)
		fname = out_dir + '/' + _id + '.csv'
	with open(fname, 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerows(output_rows)


def dump_urls(out_dir):
	_out_dir = '.' if out_dir is None else out_dir
	files = [
	    os.path.join(_out_dir, f) for f in os.listdir(_out_dir)
	    if os.path.isfile(os.path.join(_out_dir, f)) and f != 'all_patches'
	]
	urls = []
	for fname in files:
		with open(fname, 'r') as csvfile:
			reader = csv.reader(csvfile)
			x = 0
			idx = -1
			for row in reader:
				if x == 0:
					for col_idx in range(len(row)):
						if row[col_idx] == "Reference URLs":
							idx = col_idx
							break
					x += 1
				else:
					if idx == -1:
						print("Failed to find URLs column!")
						return
					if len(row) <= idx:
						continue
					urls += row[idx].split(';')
	with open(os.path.join(_out_dir, 'all_patches'), 'w') as all_patches:
		for url in sorted(set(urls)):
			all_patches.write(url + '\n')


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
	    "--patch-level",
	    type=str,
	    required=True,
	    help=
	    "Specify the patch you want to scrape (Example: 2021-01-01, 2020-10-05, 2019-09, etc)"
	)
	parser.add_argument("--out-dir",
	                    type=str,
	                    help="Directory in which files must be placed")
	args = parser.parse_args()
	level_parts = args.patch_level.split('-')
	url = 'https://source.android.com/security/bulletin/{}-{}-01'.format(
	    level_parts[0], level_parts[1])
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	extract_section(soup, 'framework', args.out_dir, level_parts[0], level_parts[1])
	dump_urls(args.out_dir)


if __name__ == '__main__':
	main()
