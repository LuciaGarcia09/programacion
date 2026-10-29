"""Genera (con el modelo de core.segmentacion) las tablas de dependencias y los cronogramas de las soluciones."""
from __future__ import annotations

from dataclasses import replace

from core.segmentacion import (Config, dependencias, diagrama, flujo_bucle, formula_n, leer_codigo,
                               planificar_latencias)


def deps_md(texto: str, tipos=("RAW", "WAR", "WAW"), bucle=True) -> str:
    cod = leer_codigo(texto)
    ds = [d for d in dependencias(cod, bucle) if d.tipo in tipos]
    orden = {"RAW": 0, "WAR": 1, "WAW": 2}
    ds.sort(key=lambda d: (orden[d.tipo], d.entre_iteraciones, d.destino, d.origen))
    t = "| Tipo | Registro | De (origen) | A (destino) | ¿Entre iteraciones? |\n|---|---|---|---|---|\n"
    for d in ds:
        a = cod[d.origen].texto.split(":")[-1].strip() if ":" in cod[d.origen].texto else cod[d.origen].texto
        b = cod[d.destino].texto.split(":")[-1].strip() if ":" in cod[d.destino].texto else cod[d.destino].texto
        t += (f"| {d.tipo} | `{d.registro}` | I{d.origen + 1}: `{a}` | I{d.destino + 1}: `{b}` | "
              f"{'sí (de una vuelta a la siguiente)' if d.entre_iteraciones else 'no'} |\n")
    return t


def _celdas_md(filas, total, numerar=True):
    ancho = total
    cab = "| Instrucción | " + " | ".join(str(c) for c in range(1, ancho + 1)) + " |\n"
    cab += "|---|" + "---|" * ancho + "\n"
    cuerpo = ""
    for k, f in enumerate(filas, 1):
        txt = f.texto.split(":")[-1].strip() if ":" in f.texto else f.texto
        celdas = [f.celdas.get(c, "") for c in range(1, ancho + 1)]
        cuerpo += f"| {'I' + str(k) + ' ' if numerar else ''}`{txt}` | " + " | ".join(celdas) + " |\n"
    return cab + cuerpo


def _etapas_md(filas):
    t = "| Instrucción | IF | ID | EX | M | WB |\n|---|---|---|---|---|---|\n"
    for f in filas:
        txt = f.texto.split(":")[-1].strip() if ":" in f.texto else f.texto
        c = []
        for e in ("IF", "ID", "EX", "M", "WB"):
            a, b = f.etapas[e]
            c.append(str(a) if a == b else f"{a}–{b}")
        t += f"| `{txt}` | " + " | ".join(c) + " |\n"
    return t


def cronograma(texto: str, cfg: Config, iteraciones=1, flujo=None, tomados=None, max_columnas=34):
    """Devuelve (markdown, total de ciclos, filas)."""
    if flujo is None:
        cod = leer_codigo(texto)
        flujo, tomados, _ = flujo_bucle(cod, iteraciones)
        if iteraciones == 1:
            tomados = [True] * len(tomados)       # la primera vuelta continúa el bucle
    filas, total = diagrama(flujo, cfg, tomados)
    if total <= max_columnas:
        md = _celdas_md(filas, total)
    else:
        md = _etapas_md(filas)
    return md, total, filas


def ciclos_iteracion(texto: str, cfg: Config) -> tuple[int, int]:
    """(ciclos por iteración en régimen estacionario, término independiente) → total(N) = a·N + b."""
    return formula_n(leer_codigo(texto), cfg)


def latencias_md(texto: str, latencia, salto_extra=0, hueco_retardo=False):
    cod = leer_codigo(texto)
    filas, total = planificar_latencias(cod, latencia, salto_extra, hueco_retardo)
    t = "| Ciclo | Instrucción |\n|---|---|\n"
    for c, txt in filas:
        txt2 = txt.split(":")[-1].strip() if ":" in txt else txt
        t += f"| {c} | {'*' + txt2 + '*' if txt2.startswith('detención') else '`' + txt2 + '`'} |\n"
    return t, total


def flujo_con_extras(texto: str, extras: list[dict], vueltas=1):
    """Flujo dinámico de `vueltas` iteraciones con ciclos extra distintos en cada instancia (fallos de caché)."""
    cod = leer_codigo(texto)
    flujo, tomados, _ = flujo_bucle(cod, vueltas)
    flujo = [replace(ins, extra_din=extras[k] if k < len(extras) else {}) for k, ins in enumerate(flujo)]
    return flujo, [True] * len(tomados)
