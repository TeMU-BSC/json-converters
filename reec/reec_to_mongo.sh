#!/bin/bash

for filename in ../REEC_EN_ES-Original/*.json; do
	echo "$filename"
	if  mongoimport --db Reec --collection articles $filename; then
		echo "$filename success"
		echo "$filename" >> ../logs/success.txt
	else
		echo "$filename  error"
		echo "$filename" >> ../logs/error.txt
	fi
done
