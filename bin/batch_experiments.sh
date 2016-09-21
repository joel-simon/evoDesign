#!/bin/bash
trap "exit" INT
for shape in loops dots checkerboard circles E O R Y X stripes
do
	pypy main.py -o "out/${1}/${shape}" -c 1 -e shapes -s $shape -p 200 -g 200
done

declare sum_fitness=0
for shape in E O R Y X stripes loops dots checkerboard circles
do
	fitness=$(grep fitness "./out/${1}/${shape}/genome.txt" | cut -f 2 -d " ")
	echo -ne $fitness
	echo -ne '\t'
	sum_fitness=$(python -c "print($fitness + $sum_fitness)")
done

echo ''
python -c "print($sum_fitness / 10.0)"

