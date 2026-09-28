#!/usr/bin/env bash
# Pruebas de implementación + conjuntos de la gramática + ejemplos del lenguaje
set -e
cd "$(dirname "$0")"

echo "################ PRUEBAS DE IMPLEMENTACIÓN ################"
python3 -m unittest -v test_implementacion

echo; echo "################ CONJUNTOS Y VERIFICACIÓN LL(1) ################"
python3 conjuntos.py grammars/lenguaje.txt -o conjuntos.txt

echo; echo "################ EJECUCIÓN DEL LENGUAJE ################"
python3 main.py ejemplos/demo.lp

echo "################ MANEJO DE ERRORES ################"
for archivo in ejemplos/error_*.lp; do
    python3 main.py "$archivo" | tail -2 || true
done
