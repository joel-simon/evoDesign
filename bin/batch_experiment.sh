#!/bin/bash
trap "exit" INT
for i in {0..9}; do
	for j in {0..9}; do
		k="$(($i*10 + j))"
		# echo $k
		pypy main.py -o "out/std/${k}" -c 1 -e shapes -s R -p 100 -g 100 &
	done
	# sleep 1
done

echo "done"