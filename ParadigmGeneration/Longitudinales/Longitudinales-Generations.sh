if [ -n "$1" ]
then
	numeros=$1
else
	exit 1
fi
for numero in $numeros
do
	python2 "../MGC02-GenerateNetwork-ContextFree.py" $numero "-X"
	python2 "../MGC02-GenerateNetwork-ContextFree.py" $numero "-X" "-Morphomes"
done
echo $numeros
