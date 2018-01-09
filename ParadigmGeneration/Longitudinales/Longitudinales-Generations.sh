if [ -n "$1" ]
then 
	numeros=$1
else
	numeros='00 01 02 03'
fi
for numero in $numeros
do
	echo "../MGC02-GenerateNetwork-ContextFree.py $numero -X"
	echo "../MGC02-GenerateNetwork-ContextFree.py $numero -X -Morphomes"
done