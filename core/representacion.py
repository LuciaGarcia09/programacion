"""Representación de la información: enteros (binario, Ca2, Ca1, signo-magnitud, exceso) y coma flotante
(IEEE 754 de 32 y 64 bits y formatos «a medida», p. ej. 16 bits con 5 de exponente y 10 de mantisa).

Todo con los pasos explicados, como se hace en el examen.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
import struct


# ======================================================================= bases
def a_binario(n: int, bits: int | None = None) -> str:
    s = bin(n)[2:]
    return s.zfill(bits) if bits else s


def hex_a_bin(h: str) -> tuple[str, list[tuple[str, str]]]:
    h = h.strip().upper().removeprefix("0X")
    pasos = [(c, format(int(c, 16), "04b")) for c in h]
    return " ".join(b for _, b in pasos), pasos


def bin_a_hex(b: str) -> str:
    b = b.replace(" ", "")
    b = b.zfill((len(b) + 3) // 4 * 4)
    return "".join(format(int(b[i:i + 4], 2), "X") for i in range(0, len(b), 4))


def agrupar(b: str, n: int = 4) -> str:
    b = b.replace(" ", "")
    r = len(b) % n
    trozos = ([b[:r]] if r else []) + [b[i:i + n] for i in range(r, len(b), n)]
    return " ".join(trozos)


# ======================================================================= enteros con signo
@dataclass
class Entero:
    sistema: str
    bits: int
    patron: str
    valor: int | None
    pasos: list[str]
    rango: tuple[int, int]


def rango(sistema: str, n: int) -> tuple[int, int]:
    if sistema == "ca2":
        return -(1 << (n - 1)), (1 << (n - 1)) - 1
    if sistema in ("ca1", "sm"):
        return -((1 << (n - 1)) - 1), (1 << (n - 1)) - 1
    if sistema == "binario":
        return 0, (1 << n) - 1
    if sistema.startswith("exceso"):
        e = int(sistema[6:]) if len(sistema) > 6 else (1 << (n - 1)) - 1
        return -e, (1 << n) - 1 - e
    raise ValueError(sistema)


NOMBRE_SIS = {"ca2": "complemento a 2", "ca1": "complemento a 1", "sm": "signo-magnitud", "binario": "binario natural"}


def bits_necesarios(sistema: str, minimo: int, maximo: int) -> tuple[int, str]:
    n = 1
    while True:
        lo, hi = rango(sistema, n)
        if lo <= minimo and maximo <= hi:
            return n, f"Con {n} bits en {NOMBRE_SIS.get(sistema, sistema)} el rango es [{lo}, {hi}], que contiene [{minimo}, {maximo}]" + (
                f"; con {n - 1} bits sería [{rango(sistema, n - 1)[0]}, {rango(sistema, n - 1)[1]}] y no llega." if n > 1 else ".")
        n += 1


def codificar_entero(valor: int, sistema: str, n: int) -> Entero:
    lo, hi = rango(sistema, n)
    pasos = []
    if not lo <= valor <= hi:
        return Entero(sistema, n, "", valor, [f"{valor} no se puede representar: con {n} bits en "
                                               f"{NOMBRE_SIS.get(sistema, sistema)} el rango es [{lo}, {hi}]."], (lo, hi))
    if sistema == "binario":
        p = a_binario(valor, n)
        pasos.append(f"{valor} en binario con {n} bits: {p}")
    elif sistema == "sm":
        mag = a_binario(abs(valor), n - 1)
        p = ("1" if valor < 0 else "0") + mag
        pasos += [f"Bit de signo: {'1 (negativo)' if valor < 0 else '0 (positivo)'}",
                  f"Magnitud |{valor}| = {abs(valor)} en {n - 1} bits: {mag}", f"Resultado: {p}"]
    elif sistema == "ca1":
        pos = a_binario(abs(valor), n)
        if valor >= 0:
            p = pos
            pasos.append(f"Positivo: igual que en binario: {p}")
        else:
            p = "".join("1" if c == "0" else "0" for c in pos)
            pasos += [f"+{abs(valor)} en {n} bits: {pos}", f"Negativo: se invierten todos los bits → {p}"]
    elif sistema == "ca2":
        if valor >= 0:
            p = a_binario(valor, n)
            pasos.append(f"Positivo: igual que en binario: {p}")
        else:
            pos = a_binario(abs(valor), n) if abs(valor) < (1 << n) else None
            if pos is None or abs(valor) == (1 << (n - 1)):
                p = a_binario((1 << n) + valor, n)
                pasos += [f"{valor} es el menor número representable con {n} bits (−2^{n - 1}).",
                          f"2^{n} + ({valor}) = {(1 << n) + valor} → {p}"]
                if pos is not None:
                    pasos.insert(0, f"(+{abs(valor)} no cabe en {n} bits con signo, pero su Ca2 sí: )")
            else:
                inv = "".join("1" if c == "0" else "0" for c in pos)
                p = a_binario(int(inv, 2) + 1, n)
                pasos += [f"+{abs(valor)} en {n} bits: {pos}", f"Se invierten los bits: {inv}", f"Se suma 1: {p}",
                          f"(Atajo: 2^{n} − {abs(valor)} = {(1 << n) + valor} → {p})"]
    else:
        e = -lo
        p = a_binario(valor + e, n)
        pasos.append(f"Exceso {e}: se guarda {valor} + {e} = {valor + e} en binario: {p}")
    return Entero(sistema, n, p, valor, pasos, (lo, hi))


def decodificar_entero(patron: str, sistema: str) -> Entero:
    b = patron.replace(" ", "")
    n = len(b)
    u = int(b, 2)
    pasos = []
    if sistema == "binario":
        v = u
        pasos.append(f"Binario natural: {v}")
    elif sistema == "sm":
        mag = int(b[1:], 2) if n > 1 else 0
        v = -mag if b[0] == "1" else mag
        pasos += [f"Signo {b[0]} ({'negativo' if b[0] == '1' else 'positivo'}), magnitud {b[1:]} = {mag}", f"Valor: {v}"]
    elif sistema == "ca1":
        if b[0] == "0":
            v = u
            pasos.append(f"Empieza por 0 → positivo: {v}")
        else:
            inv = "".join("1" if c == "0" else "0" for c in b)
            v = -int(inv, 2)
            pasos += ["Empieza por 1 → negativo.", f"Se invierten los bits: {inv} = {int(inv, 2)}", f"Valor: {v}"]
    elif sistema == "ca2":
        if b[0] == "0":
            v = u
            pasos.append(f"Empieza por 0 → positivo: {b} = {v}")
        else:
            v = u - (1 << n)
            inv = "".join("1" if c == "0" else "0" for c in b)
            pasos += ["Empieza por 1 → negativo.",
                      f"Método 1: se invierte y se suma 1: {inv} + 1 = {int(inv, 2) + 1} → valor −{int(inv, 2) + 1}",
                      f"Método 2: el bit de mayor peso vale −2^{n - 1} = {-(1 << (n - 1))}: "
                      f"{-(1 << (n - 1))} + {u - (1 << (n - 1))} = {v}"]
    else:
        e = -rango(sistema, n)[0]
        v = u - e
        pasos.append(f"Exceso {e}: {u} − {e} = {v}")
    return Entero(sistema, n, b, v, pasos, rango(sistema, n))


# ======================================================================= coma flotante
@dataclass
class Flotante:
    e_bits: int
    m_bits: int
    signo: int
    exp_campo: int
    mant_campo: int
    tipo: str              # normal, desnormalizado, cero, infinito, NaN
    valor: float | None
    exacto: Fraction | None
    pasos: list[str]

    @property
    def sesgo(self):
        return (1 << (self.e_bits - 1)) - 1

    @property
    def patron(self) -> str:
        return (str(self.signo) + format(self.exp_campo, f"0{self.e_bits}b") + format(self.mant_campo, f"0{self.m_bits}b"))

    @property
    def hexa(self) -> str:
        n = 1 + self.e_bits + self.m_bits
        return "0x" + format(int(self.patron, 2), f"0{(n + 3) // 4}X")


def _binario_fraccion(x: Fraction, maxbits=80) -> str:
    ent = math.floor(x)
    f = x - ent
    out = []
    for _ in range(maxbits):
        if f == 0:
            break
        f *= 2
        out.append("1" if f >= 1 else "0")
        if f >= 1:
            f -= 1
    return bin(ent)[2:] + ("," + "".join(out) if out else "")


def codificar_float(x: float | str, e_bits=8, m_bits=23) -> Flotante:
    """Codifica x en el formato IEEE (1, e_bits, m_bits) con redondeo al par más cercano."""
    sesgo = (1 << (e_bits - 1)) - 1
    pasos = []
    if isinstance(x, str):
        xs = x.strip().replace(",", ".")
        if xs.lower() in ("inf", "+inf", "infinito"):
            return Flotante(e_bits, m_bits, 0, (1 << e_bits) - 1, 0, "infinito", math.inf, None, ["+∞: exponente todo a 1 y mantisa 0."])
        if xs.lower() in ("-inf", "-infinito"):
            return Flotante(e_bits, m_bits, 1, (1 << e_bits) - 1, 0, "infinito", -math.inf, None, ["−∞: signo 1, exponente todo a 1 y mantisa 0."])
        X = Fraction(xs)
    else:
        X = Fraction(x)
    s = 1 if X < 0 else 0
    A = abs(X)
    pasos.append(f"Signo: {'negativo → S = 1' if s else 'positivo → S = 0'}.")
    if A == 0:
        return Flotante(e_bits, m_bits, s, 0, 0, "cero", 0.0, Fraction(0), pasos + ["El cero: exponente y mantisa a 0."])
    pasos.append(f"{float(A):g} en binario: {_binario_fraccion(A, m_bits + 12)}" + ("…" if A.denominator & (A.denominator - 1) else ""))
    E = math.floor(math.log2(A))
    while Fraction(2) ** E > A:
        E -= 1
    while Fraction(2) ** (E + 1) <= A:
        E += 1
    emin = 1 - sesgo
    if E < emin:
        # desnormalizado
        q = A / Fraction(2) ** emin * (1 << m_bits)
        mant = _redondeo_par(q)
        pasos.append(f"Es menor que 2^{emin} (el menor normalizado): se representa desnormalizado, "
                     f"0,mantisa × 2^{emin}, con exponente 000…0.")
        if mant >= (1 << m_bits):
            mant -= 1 << m_bits
            ecampo = 1
            tipo = "normal"
        else:
            ecampo = 0
            tipo = "desnormalizado" if mant else "cero"
    else:
        q = (A / Fraction(2) ** E - 1) * (1 << m_bits)
        mant = _redondeo_par(q)
        if mant == (1 << m_bits):
            mant = 0
            E += 1
        pasos.append(f"Normalizado: 1,{format(mant, f'0{m_bits}b').rstrip('0') or '0'} × 2^{E}")
        ecampo = E + sesgo
        if ecampo >= (1 << e_bits) - 1:
            return Flotante(e_bits, m_bits, s, (1 << e_bits) - 1, 0, "infinito", -math.inf if s else math.inf, None,
                            pasos + [f"El exponente {E} es demasiado grande: desbordamiento → {'−' if s else '+'}∞."])
        pasos.append(f"Exponente en exceso {sesgo}: {E} + {sesgo} = {ecampo} = {format(ecampo, f'0{e_bits}b')}")
        tipo = "normal"
    pasos.append(f"Mantisa (sin el 1 implícito, {m_bits} bits): {format(mant, f'0{m_bits}b')}")
    f = Flotante(e_bits, m_bits, s, ecampo, mant, tipo, None, None, pasos)
    d = decodificar_float(f.patron, e_bits, m_bits)
    f.valor, f.exacto = d.valor, d.exacto
    if d.exacto is not None and d.exacto != X:
        err = abs(d.exacto - X)
        pasos.append(f"No es exacto: se guarda {float(d.exacto):.10g}; error = {float(err):.4g} "
                     f"(relativo {float(err / A):.3g}).")
    else:
        pasos.append("La representación es exacta.")
    pasos.append(f"Resultado: {agrupar(f.patron)} = {f.hexa}")
    return f


def _redondeo_par(q: Fraction) -> int:
    fl = math.floor(q)
    r = q - fl
    if r > Fraction(1, 2) or (r == Fraction(1, 2) and fl % 2 == 1):
        return fl + 1
    return fl


def decodificar_float(patron: str | int, e_bits=8, m_bits=23) -> Flotante:
    n = 1 + e_bits + m_bits
    if isinstance(patron, int):
        b = format(patron, f"0{n}b")
    else:
        t = patron.strip().replace(" ", "")
        if t.lower().startswith("0x"):
            b = format(int(t, 16), f"0{n}b")
        else:
            b = t
    if len(b) != n:
        raise ValueError(f"Hacen falta {n} bits y hay {len(b)}.")
    s, ec, mc = int(b[0]), int(b[1:1 + e_bits], 2), int(b[1 + e_bits:], 2)
    sesgo = (1 << (e_bits - 1)) - 1
    pasos = [f"Se separan los campos: S = {b[0]} · exponente = {b[1:1 + e_bits]} ({ec}) · mantisa = {b[1 + e_bits:]}"]
    sg = -1 if s else 1
    if ec == (1 << e_bits) - 1:
        if mc == 0:
            pasos.append(f"Exponente todo a 1 y mantisa 0 → {'−' if s else '+'}∞.")
            return Flotante(e_bits, m_bits, s, ec, mc, "infinito", sg * math.inf, None, pasos)
        pasos.append("Exponente todo a 1 y mantisa distinta de 0 → NaN (Not a Number).")
        return Flotante(e_bits, m_bits, s, ec, mc, "NaN", math.nan, None, pasos)
    if ec == 0:
        if mc == 0:
            pasos.append(f"Exponente y mantisa a 0 → {'−' if s else '+'}0.")
            return Flotante(e_bits, m_bits, s, ec, mc, "cero", -0.0 if s else 0.0, Fraction(0), pasos)
        v = Fraction(mc, 1 << m_bits) * Fraction(2) ** (1 - sesgo)
        pasos.append(f"Exponente 0 y mantisa ≠ 0 → desnormalizado: (−1)^{s} × 0,{b[1 + e_bits:].rstrip('0')} × 2^{1 - sesgo}")
        pasos.append(f"= {'−' if s else ''}{mc}/2^{m_bits} × 2^{1 - sesgo} = {'−' if s else ''}{_fmt_exacto(v)}")
        return Flotante(e_bits, m_bits, s, ec, mc, "desnormalizado", float(sg * v), sg * v, pasos)
    E = ec - sesgo
    v = (1 + Fraction(mc, 1 << m_bits)) * Fraction(2) ** E
    pasos.append(f"Normalizado: exponente real = {ec} − {sesgo} = {E}")
    pasos.append(f"Valor = (−1)^{s} × 1,{b[1 + e_bits:].rstrip('0') or '0'} × 2^{E} = {'−' if s else ''}{_fmt_exacto(v)}")
    return Flotante(e_bits, m_bits, s, ec, mc, "normal", float(sg * v), sg * v, pasos)


def _fmt_exacto(v: Fraction) -> str:
    if v.denominator == 1:
        return str(v.numerator)
    f = float(v)
    if v.denominator & (v.denominator - 1) == 0 and v.denominator <= 2 ** 30:
        return f"{f:.12g}".rstrip("0") if "e" not in f"{f:.12g}" else f"{f:.6e}"
    return f"{f:.7e}"


def extremos(e_bits=8, m_bits=23) -> dict:
    sesgo = (1 << (e_bits - 1)) - 1
    emin, emax = 1 - sesgo, (1 << e_bits) - 2 - sesgo
    return {
        "sesgo": sesgo,
        "menor desnormalizado": Fraction(1, 1 << m_bits) * Fraction(2) ** emin,
        "mayor desnormalizado": Fraction((1 << m_bits) - 1, 1 << m_bits) * Fraction(2) ** emin,
        "menor normalizado": Fraction(2) ** emin,
        "mayor normalizado": (2 - Fraction(1, 1 << m_bits)) * Fraction(2) ** emax,
        "exponente mínimo": emin, "exponente máximo": emax,
        "nº desnormalizados (por signo)": (1 << m_bits) - 1,
    }


def contar_entre(a: float, b: float, e_bits=8, m_bits=23) -> int:
    """Cuántos números representables hay en [a, b) (a, b ≥ 0)."""
    def clave(x):  # patrón de x redondeado hacia abajo (positivo)
        f = codificar_float(Fraction(x), e_bits, m_bits)
        return int(f.patron, 2)
    return clave(b) - clave(a)


def float32_hex(x: float) -> str:
    return "0x" + struct.pack(">f", x).hex().upper()


def suma_float(a: float, b: float, e_bits=8, m_bits=23) -> tuple[Flotante, list[str]]:
    """Suma en coma flotante explicada (alinear exponentes, sumar mantisas, normalizar, redondear)."""
    fa, fb = codificar_float(a, e_bits, m_bits), codificar_float(b, e_bits, m_bits)
    pasos = []
    sesgo = (1 << (e_bits - 1)) - 1
    Ea, Eb = fa.exp_campo - sesgo, fb.exp_campo - sesgo
    Ma = (1 << m_bits) | fa.mant_campo
    Mb = (1 << m_bits) | fb.mant_campo
    pasos.append(f"a = 1,{format(fa.mant_campo, f'0{m_bits}b').rstrip('0') or '0'} × 2^{Ea}   b = 1,"
                 f"{format(fb.mant_campo, f'0{m_bits}b').rstrip('0') or '0'} × 2^{Eb}")
    if Ea < Eb:
        Ea, Eb, Ma, Mb = Eb, Ea, Mb, Ma
    d = Ea - Eb
    pasos.append(f"1) Se igualan exponentes: el menor se desplaza {d} posiciones a la derecha → los dos × 2^{Ea}.")
    sa = -1 if (fa.signo if Ea == fa.exp_campo - sesgo else fb.signo) else 1
    r = Fraction(a) + Fraction(b)
    pasos.append(f"2) Se suman las mantisas (con su signo).")
    fr = codificar_float(r, e_bits, m_bits)
    E = fr.exp_campo - sesgo
    pasos.append(f"3) Se normaliza el resultado: 1,{format(fr.mant_campo, f'0{m_bits}b').rstrip('0') or '0'} × 2^{E}")
    pasos.append(f"4) Resultado: {agrupar(fr.patron)} = {fr.hexa} = {fr.valor:g}")
    return fr, pasos


def producto_float(a: float, b: float, e_bits=8, m_bits=23) -> tuple[Flotante, list[str]]:
    fa, fb = codificar_float(a, e_bits, m_bits), codificar_float(b, e_bits, m_bits)
    sesgo = (1 << (e_bits - 1)) - 1
    Ea, Eb = fa.exp_campo - sesgo, fb.exp_campo - sesgo
    pasos = [f"1) Signo: {fa.signo} XOR {fb.signo} = {fa.signo ^ fb.signo}",
             f"2) Exponentes: se suman los reales {Ea} + {Eb} = {Ea + Eb} (en exceso: {fa.exp_campo} + {fb.exp_campo} − {sesgo} = {Ea + Eb + sesgo})",
             "3) Se multiplican las mantisas (con el 1 implícito) y se normaliza si hace falta."]
    fr = codificar_float(Fraction(a) * Fraction(b), e_bits, m_bits)
    E = fr.exp_campo - sesgo
    pasos.append(f"4) Resultado: 1,{format(fr.mant_campo, f'0{m_bits}b').rstrip('0') or '0'} × 2^{E} = {agrupar(fr.patron)} = {fr.hexa} = {fr.valor:g}")
    return fr, pasos
