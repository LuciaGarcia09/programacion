"""Memoria caché: partir una dirección en campos, simular accesos (directa, asociativa, por conjuntos; LRU, FIFO, LFU)
y fórmulas de tiempo medio de acceso. También memoria virtual (traducción de direcciones con tabla de páginas)."""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
import math


def log2_exacto(n: int) -> int:
    k = n.bit_length() - 1
    if 1 << k != n:
        raise ValueError(f"{n} no es una potencia de 2")
    return k


def tam_texto(nbytes: int) -> str:
    for suf, p in (("GB", 30), ("MB", 20), ("KB", 10)):
        if nbytes >= 1 << p and nbytes % (1 << p) == 0:
            return f"{nbytes >> p} {suf} = 2^{log2_exacto(nbytes) if nbytes & (nbytes - 1) == 0 else '?'} B"
    return f"{nbytes} B"


def leer_tam(t: str) -> int:
    t = t.strip().upper().replace(" ", "")
    mult = {"B": 1, "KB": 1 << 10, "K": 1 << 10, "MB": 1 << 20, "M": 1 << 20, "GB": 1 << 30, "G": 1 << 30,
            "TB": 1 << 40}
    for suf in sorted(mult, key=len, reverse=True):
        if t.endswith(suf):
            return int(float(t[: -len(suf)]) * mult[suf])
    return int(t)


@dataclass
class Campos:
    bits_dir: int
    lineas: int
    conjuntos: int
    vias: int
    b_byte: int
    b_indice: int
    b_etiqueta: int
    pasos: list


def campos(bits_dir: int, tam_cache: int, tam_linea: int, vias: int | None) -> Campos:
    """vias = 1 → directa · vias = None → totalmente asociativa."""
    lineas = tam_cache // tam_linea
    pasos = [f"Nº de líneas = tamaño caché / tamaño línea = {tam_texto(tam_cache)} / {tam_linea} B = "
             f"2^{log2_exacto(tam_cache)} / 2^{log2_exacto(tam_linea)} = 2^{log2_exacto(lineas)} = {lineas}"]
    bb = log2_exacto(tam_linea)
    pasos.append(f"Bits de byte (desplazamiento dentro de la línea) = log2({tam_linea}) = {bb}")
    if vias is None or vias == lineas:
        conj, bi = 1, 0
        pasos.append("Totalmente asociativa: no hay campo de línea/conjunto; la etiqueta es el nº de bloque entero.")
        v = lineas
    else:
        v = vias
        conj = lineas // vias
        bi = log2_exacto(conj)
        if vias == 1:
            pasos.append(f"Correspondencia directa: bits de línea = log2({lineas}) = {bi}")
        else:
            pasos.append(f"Nº de conjuntos = líneas / vías = {lineas} / {vias} = {conj} → bits de conjunto = {bi}")
    be = bits_dir - bi - bb
    pasos.append(f"Bits de etiqueta = {bits_dir} − {bi} − {bb} = {be}")
    return Campos(bits_dir, lineas, conj, v, bb, bi, be, pasos)


def partir_direccion(d: int, c: Campos) -> dict:
    b = format(d, f"0{c.bits_dir}b")
    et = b[: c.b_etiqueta]
    ind = b[c.b_etiqueta: c.b_etiqueta + c.b_indice]
    by = b[c.b_etiqueta + c.b_indice:]
    return {"binario": b, "etiqueta": et, "indice": ind, "byte": by,
            "etiqueta_val": int(et, 2) if et else 0, "indice_val": int(ind, 2) if ind else 0, "byte_val": int(by, 2),
            "bloque": d >> c.b_byte}


@dataclass
class Acceso:
    tipo: str
    dir: int
    bloque: int
    conjunto: int
    acierto: bool
    expulsado: int | None
    sucio_expulsado: bool = False


@dataclass
class ResultadoCache:
    accesos: list
    aciertos: int
    fallos: int
    lecturas: int
    escrituras: int
    expulsiones: int
    escrituras_mp: int          # bloques volcados (post-escritura) o palabras escritas (escritura inmediata)
    estado: list                # por conjunto: lista de bloques

    @property
    def total(self):
        return self.aciertos + self.fallos

    @property
    def tasa_aciertos(self):
        return self.aciertos / self.total if self.total else 0.0


class Cache:
    def __init__(self, tam_cache: int, tam_linea: int, vias: int | None = 1, reemplazo="LRU",
                 escritura="post", asignar_en_escritura=True):
        self.lineas = tam_cache // tam_linea
        self.tl = tam_linea
        self.vias = self.lineas if vias is None else vias
        self.nconj = self.lineas // self.vias
        self.reemplazo = reemplazo.upper()
        self.escritura = escritura            # "post" (write-back) o "inmediata" (write-through)
        self.asignar = asignar_en_escritura
        self.conj = [OrderedDict() for _ in range(self.nconj)]   # bloque → [sucio, usos]
        self.aciertos = self.fallos = self.lect = self.escr = self.expul = self.esc_mp = 0
        self.registro: list[Acceso] = []

    def acceder(self, d: int, tipo="R") -> bool:
        blo = d // self.tl
        k = blo % self.nconj
        S = self.conj[k]
        es_w = tipo == "W"
        if es_w:
            self.escr += 1
        else:
            self.lect += 1
        if blo in S:
            self.aciertos += 1
            ent = S[blo]
            ent[1] += 1
            if self.reemplazo == "LRU":
                S.move_to_end(blo)
            if es_w:
                if self.escritura == "post":
                    ent[0] = True
                else:
                    self.esc_mp += 1
            self.registro.append(Acceso(tipo, d, blo, k, True, None))
            return True
        self.fallos += 1
        expulsado, sucio = None, False
        if es_w and not self.asignar:
            self.esc_mp += 1
            self.registro.append(Acceso(tipo, d, blo, k, False, None))
            return False
        if len(S) >= self.vias:
            if self.reemplazo == "LFU":
                victima = min(S, key=lambda b: S[b][1])
            else:                     # LRU y FIFO: el primero del OrderedDict
                victima = next(iter(S))
            sucio = S[victima][0]
            del S[victima]
            expulsado = victima
            self.expul += 1
            if sucio:
                self.esc_mp += 1
        S[blo] = [es_w and self.escritura == "post", 1]
        if es_w and self.escritura != "post":
            self.esc_mp += 1
        self.registro.append(Acceso(tipo, d, blo, k, False, expulsado, sucio))
        return False

    def resultado(self) -> ResultadoCache:
        return ResultadoCache(self.registro, self.aciertos, self.fallos, self.lect, self.escr, self.expul,
                              self.esc_mp, [list(S) for S in self.conj])


def simular(traza, tam_cache, tam_linea, vias=1, reemplazo="LRU", escritura="post", asignar=True) -> ResultadoCache:
    c = Cache(tam_cache, tam_linea, vias, reemplazo, escritura, asignar)
    for t, d in traza:
        c.acceder(d, "W" if t == "W" else "R")
    return c.resultado()


def simular_dos_niveles(traza, l1: dict, l2: dict):
    c1 = Cache(**l1)
    c2 = Cache(**l2)
    for t, d in traza:
        if not c1.acceder(d, t):
            c2.acceder(d, "R")
    return c1.resultado(), c2.resultado()


# ======================================================================= fórmulas
def tiempo_medio(ta, tf, h):
    """Tm = Ta + (1 − h)·Tf   (h en tanto por uno)."""
    return ta + (1 - h) * tf


def tasa_necesaria(tm, ta, tf):
    """Despeja h: 1 − h = (Tm − Ta) / Tf."""
    return 1 - (tm - ta) / tf


# ======================================================================= memoria virtual
@dataclass
class FormatoVirtual:
    bits_dir: int
    bits_pagina: int
    bits_desp: int
    paginas: int
    marcos: int | None
    bits_marco: int | None
    pasos: list


def formato_virtual(bits_dir: int, tam_pagina: int, mem_fisica: int | None = None) -> FormatoVirtual:
    d = log2_exacto(tam_pagina)
    p = bits_dir - d
    pasos = [f"Desplazamiento dentro de la página = log2({tam_texto(tam_pagina)}) = {d} bits",
             f"Nº de página = {bits_dir} − {d} = {p} bits → hasta 2^{p} = {1 << p:,} páginas".replace(",", ".")]
    marcos = bm = None
    if mem_fisica:
        marcos = mem_fisica // tam_pagina
        bm = log2_exacto(marcos)
        pasos.append(f"Marcos de página = memoria física / tamaño de página = {tam_texto(mem_fisica)} / "
                     f"{tam_texto(tam_pagina)} = 2^{bm} = {marcos:,}".replace(",", "."))
        pasos.append(f"Dirección física: {bm} bits de marco + {d} de desplazamiento = {bm + d} bits")
    return FormatoVirtual(bits_dir, p, d, 1 << p, marcos, bm, pasos)


def traducir(dir_virtual: int, tam_pagina: int, tabla: dict[int, int | None], bits_dir=32):
    """tabla: página → marco (None si no está en memoria: fallo de página)."""
    d = log2_exacto(tam_pagina)
    pag, desp = dir_virtual >> d, dir_virtual & (tam_pagina - 1)
    pasos = [f"0x{dir_virtual:08X} = página {pag} (los bits altos) y desplazamiento 0x{desp:X} = {desp} (los {d} bits bajos)"]
    marco = tabla.get(pag)
    if marco is None:
        pasos.append(f"La página {pag} no está en memoria principal → FALLO DE PÁGINA (el S.O. la trae del disco).")
        return None, pasos
    fis = (marco << d) | desp
    pasos.append(f"Tabla de páginas: página {pag} → marco {marco}")
    pasos.append(f"Dirección física = marco × tamaño de página + desplazamiento = {marco} × {tam_pagina} + {desp} = "
                 f"{fis} = 0x{fis:X}")
    return fis, pasos
