"""Analizador sintáctico descendente recursivo.

Hay una función por cada no terminal de grammars/lenguaje.txt, y cada una decide
qué regla aplicar mirando un solo token de anticipación, usando los conjuntos de
predicción. Devuelve el árbol sintáctico como tuplas:

    ('asig',  nombre, expr, linea)
    ('bin',   operador, izq, der, linea)      operador: + - * / %
    ('neg',   expr, linea)
    ('abs',   expr, linea)
    ('func',  nombre, expr, linea)            nombre: sin cos tan
    ('num',   valor, tipo, linea)             tipo: entero | real
    ('var',   nombre, linea)
"""

from lexico import analizar as analizar_lexico

# Conjuntos de predicción usados en las decisiones (calculados con conjuntos.py).
PRED_UNIDAD = {"NUM", "ID", "abre", "barra", "abs", "sin", "cos", "tan"}
PRED_FACT = PRED_UNIDAD | {"menos"}
FUNCIONES = {"sin", "cos", "tan"}
OPERADORES = {"mas": "+", "menos": "-", "por": "*", "entre": "/", "modulo": "%"}


class ErrorSintactico(Exception):
    pass


class Analizador:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------ utilidades
    @property
    def actual(self):
        return self.tokens[self.pos]

    def consumir(self, clase, esperado):
        if self.actual.clase != clase:
            self.error(esperado)
        token = self.actual
        self.pos += 1
        return token

    def error(self, esperado):
        t = self.actual
        encontrado = "fin de la entrada" if t.clase == "$" else f"'{t.lexema}'"
        raise ErrorSintactico(
            f"línea {t.linea}, columna {t.columna}: se esperaba {esperado} y se encontró {encontrado}."
        )

    # ------------------------------------------------------------ prog, sents
    def prog(self):
        """prog -> sents"""
        sentencias = self.sents()
        if self.actual.clase != "$":
            self.error("el inicio de una sentencia")
        return sentencias

    def sents(self):
        """sents -> sent sents | ε"""
        sentencias = []
        while self.actual.clase == "ID":
            sentencias.append(self.sent())
        return sentencias

    def sent(self):
        """sent -> ID asig expr fin"""
        nombre = self.consumir("ID", "un nombre de variable")
        self.consumir("asig", "'='")
        valor = self.expr()
        self.consumir("fin", "';'")
        return ("asig", nombre.lexema, valor, nombre.linea)

    # ------------------------------------------------------------ expresiones
    def expr(self):
        """expr -> term expr_r"""
        return self.expr_r(self.term())

    def expr_r(self, izq):
        """expr_r -> mas term expr_r | menos term expr_r | ε"""
        while self.actual.clase in ("mas", "menos"):
            op = self.actual
            self.pos += 1
            izq = ("bin", OPERADORES[op.clase], izq, self.term(), op.linea)
        return izq

    def term(self):
        """term -> fact term_r"""
        return self.term_r(self.fact())

    def term_r(self, izq):
        """term_r -> por fact term_r | entre fact term_r | modulo fact term_r | ε"""
        while self.actual.clase in ("por", "entre", "modulo"):
            op = self.actual
            self.pos += 1
            izq = ("bin", OPERADORES[op.clase], izq, self.fact(), op.linea)
        return izq

    def fact(self):
        """fact -> menos fact | unidad"""
        if self.actual.clase == "menos":
            op = self.actual
            self.pos += 1
            return ("neg", self.fact(), op.linea)
        return self.unidad()

    def unidad(self):
        """unidad -> NUM | ID | abre expr cierra | barra expr barra | func abre expr cierra"""
        t = self.actual

        if t.clase == "NUM":
            self.pos += 1
            tipo = "real" if "." in t.lexema else "entero"
            valor = float(t.lexema) if tipo == "real" else int(t.lexema)
            return ("num", valor, tipo, t.linea)

        if t.clase == "ID":
            self.pos += 1
            return ("var", t.lexema, t.linea)

        if t.clase == "abre":
            self.pos += 1
            dentro = self.expr()
            self.consumir("cierra", "')'")
            return dentro

        if t.clase == "barra":
            self.pos += 1
            dentro = self.expr()
            self.consumir("barra", "'|' de cierre")
            return ("abs", dentro, t.linea)

        if t.clase in FUNCIONES or t.clase == "abs":
            self.pos += 1
            self.consumir("abre", f"'(' después de {t.lexema}")
            dentro = self.expr()
            self.consumir("cierra", "')'")
            etiqueta = "abs" if t.clase == "abs" else "func"
            return (etiqueta, dentro, t.linea) if etiqueta == "abs" else ("func", t.clase, dentro, t.linea)

        self.error("un número, una variable, '(', '|' o una función")


def analizar(texto):
    """Del texto del programa al árbol sintáctico."""
    return Analizador(analizar_lexico(texto)).prog()
