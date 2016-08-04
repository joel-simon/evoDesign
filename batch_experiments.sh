#!/bin/bash
trap "exit" INT
#
for shape in loops dots checkerboard circles E O R Y X stripes
do
	for i in {1..5}
	do
		echo "${shape}${i}"
		pypy main.py -o "out/${shape}/${i}" -c 6 -e shapes -s $shape
	done
done
