if [ -n "$1" ]
then
	numeros=$1
else
	exit 1
fi
for numero in $numeros
do
	pwd
	python2 "/Users/gilles/Github/SWIM/ParadigmGeneration/MGC01-AnalyzeSample1-ContextFree.py" $numero
	python2 "/Users/gilles/Github/SWIM/ParadigmGeneration/MGC01-AnalyzeSample1-ContextFree.py" $numero "-X-Morphomes"
done
echo $numeros
