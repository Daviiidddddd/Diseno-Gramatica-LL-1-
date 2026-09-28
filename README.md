# Gramática LL(1) — lenguaje con aritmética, trigonometría y asignación

**Universidad Sergio Arboleda** · Facultad de Ingeniería en Ciencias de la Computación e IA
**Materia:** Lenguajes de Programación y Traducción
**Estudiante:** David Andrés Castellanos Angulo

📄 **Informe completo:** [`docs/informe_gramatica_ll1.pdf`](docs/informe_gramatica_ll1.pdf)

## Enunciado

Diseñar e implementar una gramática LL(1) para un lenguaje de programación que soporte `+ - * / %` y valor absoluto, las funciones `sin`, `cos`, `tan` y la asignación de variables. Hay que garantizar las fases léxica, sintáctica y semántica, mostrar los conjuntos de PRIMEROS, SIGUIENTES y PREDICCIÓN, y hacer pruebas de implementación.

<img src="docs/img/enunciado.png" width="520">

## El lenguaje

```
# Programa de ejemplo
base = 12;
area = base * 5 / 2;          # 30.0, real porque hay división
resto = 17 % base;            # 5, el módulo solo va entre enteros
desfase = |3 - 10|;           # 7, valor absoluto
razon = sin(0.7853981634) / cos(0.7853981634);
```

- Números enteros y reales, comentarios con `#`, una sentencia por línea terminada en `;`.
- Valor absoluto en dos formas: `abs(x)` y `|x|`.
- `sin`, `cos` y `tan` trabajan en radianes.

## La gramática

```
prog     -> sents
sents    -> sent sents | ε
sent     -> ID asig expr fin

expr     -> term expr_r
expr_r   -> mas term expr_r | menos term expr_r | ε

term     -> fact term_r
term_r   -> por fact term_r | entre fact term_r | modulo fact term_r | ε

fact     -> menos fact | unidad

unidad   -> NUM | ID | abre expr cierra | barra expr barra | func abre expr cierra
func     -> abs | sin | cos | tan
```

Tres decisiones la dejan LL(1):

- **Precedencia con niveles.** `expr` para sumas y restas, `term` para producto, división y módulo, `fact` abajo. Por eso `2 + 3 * 4` da 14.
- **Sin recursión izquierda.** La repetición va a la derecha con `expr_r` y `term_r`, que terminan en ε. La asociatividad por la izquierda se arma en el analizador.
- **Sin prefijos comunes.** Cada alternativa de `unidad` empieza con un token distinto, y las cuatro funciones se agrupan en `func`.

## Conjuntos y verificación LL(1)

```bash
python3 main.py --conjuntos
```

| No terminal | PRIMEROS | SIGUIENTES |
|---|---|---|
| prog | `{ID, ε}` | `{$}` |
| sents | `{ID, ε}` | `{$}` |
| sent | `{ID}` | `{ID, $}` |
| expr | `{ID, menos, NUM, abre, barra, abs, sin, cos, tan}` | `{fin, cierra, barra}` |
| expr_r | `{mas, menos, ε}` | `{fin, cierra, barra}` |
| term | `{ID, menos, NUM, abre, barra, abs, sin, cos, tan}` | `{fin, mas, menos, cierra, barra}` |
| term_r | `{por, entre, modulo, ε}` | `{fin, mas, menos, cierra, barra}` |
| fact | `{ID, menos, NUM, abre, barra, abs, sin, cos, tan}` | `{fin, mas, menos, por, entre, modulo, cierra, barra}` |
| unidad | `{ID, NUM, abre, barra, abs, sin, cos, tan}` | `{fin, mas, menos, por, entre, modulo, cierra, barra}` |
| func | `{abs, sin, cos, tan}` | `{abre}` |

Los conjuntos de PREDICCIÓN de las 24 reglas están en `conjuntos.txt` y en el informe. El programa los compara par por par:

```
¿ES LL(1)? SÍ: las reglas de cada no terminal tienen predicciones disjuntas.
```

## Las tres fases

| Módulo | Fase | Qué hace |
|---|---|---|
| `lexico.py` | léxica | arma los tokens con su línea y columna; detecta símbolos que no pertenecen al lenguaje |
| `sintactico.py` | sintáctica | descenso recursivo, una función por no terminal, decidiendo con los conjuntos de predicción; construye el árbol |
| `semantico.py` | semántica | tabla de símbolos, tipos entero/real, variables asignadas antes de usarse; luego evalúa el programa |

Reglas semánticas: `+ - *` dan entero solo si los dos operandos son enteros, `/` siempre da real, `%` exige enteros de los dos lados, no se divide entre la constante cero, y `sin`, `cos` y `tan` devuelven real.

Cada error sale con su posición:

```
Error léxico: línea 2, columna 7: símbolo no reconocido '@'.
Error sintáctico: línea 3, columna 1: se esperaba ';' y se encontró 'y'.
Error semántico: línea 2: la variable 'y' se usa sin haber sido asignada.
Error semántico: línea 2: el módulo '%' solo se puede usar entre enteros (se recibió real y entero).
```

## Ejecución

```bash
chmod +x run_all.sh
./run_all.sh      # 31 pruebas + conjuntos + ejemplos
```

Por separado:

```bash
python3 main.py ejemplos/demo.lp            # análisis completo y resultados
python3 main.py ejemplos/demo.lp --tokens   # además muestra los tokens
python3 main.py ejemplos/demo.lp --arbol    # además muestra el árbol sintáctico
python3 main.py --conjuntos                 # PRIMEROS, SIGUIENTES, PREDICCIÓN y LL(1)
```

No necesita librerías externas. En Windows se usa `python` en lugar de `python3`.

## Pruebas

31 pruebas automáticas en `test_implementacion.py`:

| Grupo | Pruebas | Qué revisa |
|---|---|---|
| Léxico | 6 | tokens, comentarios, reales, símbolos inválidos |
| Sintáctico | 9 | precedencia, asociatividad, paréntesis, menos unario, errores |
| Semántico | 6 | tipos, variable sin asignar, módulo con reales, división por cero |
| Funciones | 3 | `sin`, `cos`, `tan` y funciones anidadas |
| Gramática | 5 | LL(1), sin recursión izquierda, PRIMEROS, SIGUIENTES y PREDICCIÓN |
| Ejemplos | 2 | los archivos de `ejemplos/` dan el resultado y el error esperados |

## Estructura

```
grammars/lenguaje.txt      la gramática LL(1)
lexico.py                  análisis léxico
sintactico.py              análisis sintáctico (descenso recursivo)
semantico.py               análisis semántico y evaluación
conjuntos.py               PRIMEROS, SIGUIENTES, PREDICCIÓN y verificación LL(1)
main.py                    une las tres fases
test_implementacion.py     31 pruebas automáticas
run_all.sh                 pruebas + conjuntos + ejemplos
ejemplos/                  programas de prueba, incluidos los que fallan a propósito
conjuntos.txt              salida de los conjuntos
docs/                      informe PDF, fuente LaTeX e imágenes
```
