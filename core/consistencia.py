"""Enumera TODAS las intercalaciones posibles (consistencia secuencial) de unos hilos muy sencillos.

Sentencias admitidas (una por línea): `X=1`, `Y=X`, `U=A`, `print(X)`, `while(flag==0);`
Cada sentencia es atómica. Devuelve, para cada resultado posible, un orden total de ejemplo.
"""
from __future__ import annotations

import re


def _paso(s: str):
    s = s.strip().rstrip(";").replace(" ", "")
    m = re.fullmatch(r"(?:print|Print)\((\w+)\)", s)
    if m:
        v = m.group(1)
        return ("print", v, None)
    m = re.fullmatch(r"while\((\w+)==(-?\d+)\)", s)
    if m:
        return ("espera", m.group(1), int(m.group(2)))
    m = re.fullmatch(r"(\w+)=(-?\d+|\w+)", s)
    if m:
        dst, src = m.groups()
        return ("asig", dst, int(src) if re.fullmatch(r"-?\d+", src) else src)
    raise ValueError(f"no entiendo «{s}»")


def leer(hilos: list[str]):
    return [[_paso(l) for l in h.strip().split("\n") if l.strip()] for h in hilos]


def intercalaciones(hilos_txt: list[str], finales: tuple = (), max_res=100000):
    """Devuelve {resultado: orden de ejemplo}. resultado = (salidas de cada hilo..., valores finales)."""
    hilos = leer(hilos_txt)
    res = {}

    def dfs(pcs, mem, salidas, orden):
        if len(res) > max_res:
            return
        acabado = True
        for h, prog in enumerate(hilos):
            pc = pcs[h]
            if pc >= len(prog):
                continue
            acabado = False
            tipo, a, b = prog[pc]
            if tipo == "espera" and mem.get(a, 0) == b:
                continue            # bloqueado: el bucle seguiría girando
            m2, s2 = mem, salidas
            if tipo == "print":
                s2 = list(salidas)
                s2[h] = s2[h] + (mem.get(a, 0),)
            elif tipo == "asig":
                m2 = dict(mem)
                m2[a] = b if isinstance(b, int) else mem.get(b, 0)
            p2 = list(pcs)
            p2[h] += 1
            dfs(tuple(p2), m2, s2, orden + [(h, pc)])
        if acabado:
            clave = tuple(salidas) + (tuple(mem.get(v, 0) for v in finales),)
            if clave not in res:
                res[clave] = orden

    dfs(tuple(0 for _ in hilos), {}, [() for _ in hilos], [])
    return res


def texto_orden(hilos_txt, orden):
    lineas = [[l.strip() for l in h.strip().split("\n") if l.strip()] for h in hilos_txt]
    return " → ".join(f"P{h + 1}: `{lineas[h][pc]}`" for h, pc in orden)
