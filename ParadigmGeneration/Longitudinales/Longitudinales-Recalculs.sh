#! /bin/bash

if [ -n "$1" ]
then
	numeros=$1
else
	numeros="50 51"
fi

if [ -n "$2" ]
then
	paradigmes=$2
else
	paradigmes="-X -X-Morphomes"
fi

if [ -n "$3" ]
then
	etapes=$3
else
	etapes="-Swim1 -Swim2"
fi



for numero in $numeros
do
	for paradigme in $paradigmes
	do
		for etape in $etapes
		do
			python2 ./EvaluationParadigmes-Recalcul.py $numero $paradigme $etape
		done
	done
done