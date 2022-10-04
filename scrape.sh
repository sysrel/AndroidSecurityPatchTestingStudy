#!/bin/bash

rm -r -f bulletinData
mkdir bulletinData

for i in 2020 2019 2018 2017
do
	for j in 01 02 03 04 05 06 07 08 09 10 11 12
	do
		YEAR_STR="${i}-${j}-01"
		mkdir bulletinData/$YEAR_STR
		echo " "
		echo $YEAR_STR
		python3 android_scraper.py --patch-level $YEAR_STR --out-dir bulletinData/$YEAR_STR
	done
done
