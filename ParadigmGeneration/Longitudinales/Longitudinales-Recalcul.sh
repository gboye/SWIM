if [ -n "$1" ]
then
	numeros=$1
else
	exit 1
fi
for numero in $numeros
do
	pwd
	python2 "/Users/gilles/Github/SWIM/ParadigmGeneration/Longitudinales/EvaluationParadigmes-Recalcul.py" $numero "-X" "-X" "-Swim1"
	python2 "/Users/gilles/Github/SWIM/ParadigmGeneration/Longitudinales/EvaluationParadigmes-Recalcul.py" $numero "-X" "-X" "-Swim2"
	python2 "/Users/gilles/Github/SWIM/ParadigmGeneration/Longitudinales/EvaluationParadigmes-Recalcul.py" $numero "-X" "-X-Morphomes" "-Swim1"
	python2 "/Users/gilles/Github/SWIM/ParadigmGeneration/Longitudinales/EvaluationParadigmes-Recalcul.py" $numero "-X" "-X-Morphomes" "-Swim2"
done
echo $numeros
