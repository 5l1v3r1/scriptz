#!/bin/bash
#Description: copy specified files to $filename.bak. Abort if destination file exists
USAGE="$(basename $0) FILES
	FILES	copy specified files to .bak files"

if [ "$1" = "" -o "$1" = "-h" ]
	then echo "USAGE: $usage"
	exit 1
fi

for file in "$@"; do
	cp -pnv "$file" $file.bak
done