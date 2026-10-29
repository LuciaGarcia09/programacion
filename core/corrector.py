"""Corrige las respuestas y los programas de la alumna.

- Respuestas numéricas, hexadecimales, binarias o de texto (con tolerancia y sin tildes/mayúsculas).
- Programas MIPS (con el simulador), C (gcc) y Python (subproceso), contra una lista de pruebas.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass

from core import mips


# ======================================================================= respuestas cortas
def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalizar(s: str) -> str:
    return re.sub(r"\s+", " ", _sin_tildes(str(s)).strip().lower())


def leer_numero(t: str) -> float | None:
    """Admite 1.5, 1,5, 2^-24, 2**-24, 3·2^-130, 1.2e-5, 1/3, -∞… (sin eval peligroso)."""
    s = str(t).strip().replace("−", "-").replace(" ", "").replace("·", "*").replace("×", "*").replace("^", "**")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3}){2,}", s):     # 16.777.214 → miles con punto (al menos dos grupos)
        s = s.replace(".", "")
    s = s.replace(",", ".")
    if s.endswith("%"):
        s = s[:-1]
    if not re.fullmatch(r"[0-9eE.+\-*/()]+", s):
        return None
    try:
        v = eval(s, {"__builtins__": {}}, {})           # solo dígitos y operadores
        return float(v)
    except Exception:
        return None


def comprobar(resp, texto: str) -> tuple[bool, str]:
    """Devuelve (correcta, comentario)."""
    if texto is None or str(texto).strip() == "":
        return False, "sin responder"
    t = str(texto).strip()
    if resp.tipo == "num":
        v = leer_numero(t)
        if v is None:
            return False, "no he entendido el número (usa 1,5 · 2^-24 · 1.2e-5 · 3/4)"
        ok_v = float(resp.valor)
        if ok_v == 0:
            ok = abs(v) <= 1e-12
        else:
            ok = abs(v - ok_v) <= max(abs(ok_v) * resp.tolerancia, 1e-12)
        return ok, ""
    if resp.tipo in ("hex", "bin"):
        base = 16 if resp.tipo == "hex" else 2
        s = t.lower().replace(" ", "").replace("_", "")
        s = s[2:] if s.startswith("0x" if base == 16 else "0b") else s
        try:
            v = int(s, base)
        except ValueError:
            return False, f"no es un número en base {base}"
        bueno = int(str(resp.valor).replace(" ", ""), base)
        if v != bueno:
            return False, ""
        if base == 2 and len(s) != len(str(resp.valor).replace(" ", "")):
            return False, f"el valor está bien, pero escribe los {len(str(resp.valor))} bits"
        return True, ""
    aceptadas = resp.valor if isinstance(resp.valor, (list, tuple)) else [resp.valor]
    return normalizar(t) in {normalizar(a) for a in aceptadas}, ""


# ======================================================================= comparación de salidas
_TOK = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?|[a-zñ]+")


def tokens(s: str) -> list[str]:
    return _TOK.findall(_sin_tildes(s.lower()))


def _es_num(t):
    return t[0].isdigit() or (t[0] == "-" and len(t) > 1)


def salida_coincide(esperada: str, obtenida: str, modo="tokens") -> bool:
    """modo 'tokens': los números esperados aparecen seguidos y en orden en la salida (los textos de aviso, como
    «Introduce un número:», se ignoran) y las palabras esperadas aparecen en orden.
    modo 'texto': el texto esperado aparece tal cual (espacios normalizados).
    modo 'sin_espacios': se comparan quitando todos los espacios y saltos de línea."""
    if modo == "texto":
        return re.sub(r"\s+", " ", esperada.strip()) in re.sub(r"\s+", " ", obtenida)
    if modo == "sin_espacios":
        return re.sub(r"\s+", "", esperada) in re.sub(r"\s+", "", obtenida)
    te, to = tokens(esperada), tokens(obtenida)
    ne = [t for t in te if _es_num(t)]
    no = [t for t in to if _es_num(t)]
    if ne:
        fe = [float(x) for x in ne]
        fo = [float(x) for x in no]
        if not any(all(abs(fo[i + k] - fe[k]) <= 1e-6 * max(1, abs(fe[k])) for k in range(len(fe)))
                   for i in range(len(fo) - len(fe) + 1)):
            return False
    pe = [t for t in te if not _es_num(t)]
    po = [t for t in to if not _es_num(t)]
    it = iter(po)
    return all(any(p == q for q in it) for p in pe)


# ======================================================================= ejecución de programas
@dataclass
class ResultadoPrueba:
    ok: bool
    descripcion: str
    entrada: str
    esperado: str
    obtenido: str
    detalle: str = ""


def _resolver(clave, etiquetas):
    if isinstance(clave, int):
        return clave
    m = re.fullmatch(r"\s*([A-Za-z_.$][\w.$]*)\s*(?:\+\s*(\d+))?\s*", str(clave))
    if not m or m.group(1) not in etiquetas:
        raise KeyError(f"no encuentro la etiqueta «{clave}» en tu programa (¿le has cambiado el nombre?)")
    return etiquetas[m.group(1)] + int(m.group(2) or 0)


def _bytes_palabra(v):
    v &= 0xFFFFFFFF
    return [(v >> (8 * j)) & 0xFF for j in range(4)]


def preparar_mips(codigo: str, prog, prueba) -> str:
    fuente = codigo
    main = getattr(prueba, "main", None)
    if main:
        # el main de la alumna se renombra para que mande el main de prueba
        fuente = re.sub(r"(?<![\w$])main(?![\w$])", "_main_tuyo", fuente)
        fuente = fuente + "\n\n# ---- main de prueba añadido por la app ----\n" + main
    if prog.anexo:
        etq = prog.anexo_si_falta
        if not etq or not re.search(rf"(?m)^\s*{re.escape(etq)}\s*:", codigo):
            fuente = fuente + "\n\n# ---- código añadido por la app ----\n" + prog.anexo
    return fuente


def ejecutar_mips(codigo: str, prog, prueba):
    from core.mips import Maquina, ensamblar, ErrorMIPS
    fuente = preparar_mips(codigo, prog, prueba)
    p = ensamblar(fuente)
    mem = {}
    for clave, vals in (prueba.mem_inicial or {}).items():
        base = _resolver(clave, p.etiquetas)
        for k, v in enumerate(vals):
            for j, b in enumerate(_bytes_palabra(v)):
                mem[base + 4 * k + j] = b
    devs = prueba.dispositivos() if callable(prueba.dispositivos) else None
    m = Maquina(p, prueba.entrada, dispositivos=devs, regs_iniciales=prueba.preparar, max_pasos=prueba.max_pasos,
                mem_extra=mem)
    res = m.ejecutar()
    res.dispositivos = devs
    return res


def correr_mips(codigo: str, prog) -> list[ResultadoPrueba]:
    out = []
    for pr in prog.pruebas:
        try:
            res = ejecutar_mips(codigo, prog, pr)
        except mips.ErrorMIPS as exc:
            return [ResultadoPrueba(False, pr.descripcion, pr.entrada, "", "", f"Error al ensamblar: {exc}")]
        except KeyError as exc:
            return [ResultadoPrueba(False, pr.descripcion, pr.entrada, "", "", str(exc).strip('"'))]
        fallos, esperado, obtenido = [], [], []
        if pr.salida is not None:
            esperado.append(pr.salida)
            obtenido.append(res.salida_programa or "(no imprime nada)")
            if not salida_coincide(pr.salida, res.salida_programa, pr.modo):
                fallos.append("la salida no es la esperada")
        for r, v in (pr.regs or {}).items():
            real = res.regs[mips.leer_reg(r)]
            esperado.append(f"{r} = {v}")
            obtenido.append(f"{r} = {real}")
            if real != v:
                pista = ""
                if r == "$v0" and real == 10 and "syscall 10" in res.motivo:
                    pista = " (¡has machacado $v0 con el 10 de la llamada «exit»!)"
                fallos.append(f"{r} vale {real} y debería valer {v}{pista}")
        for clave, vals in (pr.memoria or {}).items():
            try:
                base = _resolver(clave, res.etiquetas)
            except KeyError as exc:
                fallos.append(str(exc).strip('"'))
                continue
            reales = mips.palabras(res, base, len(vals))
            esperado.append(f"{clave} = {vals if len(vals) > 1 else vals[0]}")
            obtenido.append(f"{clave} = {reales if len(vals) > 1 else reales[0]}")
            if reales != list(vals):
                fallos.append(f"la memoria en «{clave}» no es la esperada")
        if pr.verificar:
            fallos += pr.verificar(res.dispositivos or [], res)
        if not res.termino and not (pr.infinito and "se ha parado tras" in res.motivo):
            fallos.append(f"el programa no ha terminado bien: {res.motivo}")
        out.append(ResultadoPrueba(not fallos, pr.descripcion, pr.entrada, "\n".join(esperado), "\n".join(obtenido),
                                   "; ".join(fallos) + (f" · {res.pasos:,} instrucciones".replace(",", ".")
                                                         if not fallos else "")))
    return out


def gcc_disponible() -> str | None:
    return shutil.which("gcc") or shutil.which("cc") or shutil.which("clang")


def compilar_c(codigo: str, extra_flags=()) -> tuple[str | None, str]:
    cc = gcc_disponible()
    if not cc:
        return None, "Este equipo no tiene compilador de C (gcc)."
    d = tempfile.mkdtemp(prefix="proglucia_")
    src, exe = os.path.join(d, "prog.c"), os.path.join(d, "prog")
    with open(src, "w", encoding="utf-8") as f:
        f.write(codigo)
    r = subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-O0", *extra_flags, "-o", exe, src, "-lm"],
                       capture_output=True, text=True, timeout=30)
    msgs = (r.stderr or "").replace(src, "prog.c")
    if r.returncode != 0:
        return None, msgs
    return exe, msgs


def _fuente_c(codigo, pr):
    """Si la prueba trae su propio main, el de la alumna se renombra (-Dmain=…) y se añade el de prueba."""
    if getattr(pr, "main", None):
        return codigo + "\n\n/* ---- main de prueba añadido por la app ---- */\n#undef main\n" + pr.main, ("-Dmain=_main_tuyo",)
    return codigo, ()


def correr_c(codigo: str, prog) -> tuple[list[ResultadoPrueba], str]:
    cache, out, msgs0 = {}, [], ""
    for pr in prog.pruebas:
        fuente, flags = _fuente_c(codigo, pr)
        if fuente not in cache:
            cache[fuente] = compilar_c(fuente, flags)
        exe, msgs = cache[fuente]
        if not msgs0:
            msgs0 = msgs
        if not exe:
            return [ResultadoPrueba(False, "compilación", "", "", "", msgs or "no compila")], msgs
        out += _correr_ejecutable([exe], prog, [pr])
    return out, msgs0


ARRANQUE_PY = """
import builtins as _b, contextlib as _c, io as _io, runpy as _r, sys as _s
_orig = _b.input
_b.input = lambda *a, **k: "7"          # por si tu archivo pide datos al cargarse
with _c.redirect_stdout(_io.StringIO()):
    try:
        _ns = _r.run_path(_s.argv[1], run_name="solucion")
    except SystemExit:
        _ns = {}
_b.input = _orig
globals().update({k: v for k, v in _ns.items() if not k.startswith("__")})
"""


def correr_python(codigo: str, prog) -> list[ResultadoPrueba]:
    d = tempfile.mkdtemp(prefix="proglucia_")
    src = os.path.join(d, "prog.py")
    with open(src, "w", encoding="utf-8") as f:
        f.write(codigo + "\n" + (prog.anexo or ""))
    out = []
    for k, pr in enumerate(prog.pruebas):
        if getattr(pr, "main", None):
            t = os.path.join(d, f"prueba{k}.py")
            with open(t, "w", encoding="utf-8") as f:
                f.write(ARRANQUE_PY + "\n" + pr.main)
            out += _correr_ejecutable([sys.executable, "-I", t, src], prog, [pr])
        else:
            out += _correr_ejecutable([sys.executable, "-I", src], prog, [pr])
    return out


def _correr_ejecutable(cmd, prog, pruebas=None) -> list[ResultadoPrueba]:
    out = []
    for pr in (pruebas if pruebas is not None else prog.pruebas):
        carpeta = tempfile.mkdtemp(prefix="proglucia_run_")       # cada prueba en su carpeta (ficheros)
        for nombre, contenido in (pr.ficheros or {}).items():
            with open(os.path.join(carpeta, nombre), "w", encoding="utf-8") as f:
                f.write(contenido)
        try:
            r = subprocess.run(cmd, input=pr.entrada + ("\n" if pr.entrada and not pr.entrada.endswith("\n") else ""),
                               capture_output=True, text=True, timeout=5, cwd=carpeta)
        except subprocess.TimeoutExpired:
            out.append(ResultadoPrueba(False, pr.descripcion, pr.entrada, pr.salida or "", "",
                                       "tarda demasiado (más de 5 s): ¿un bucle infinito o espera más datos?"))
            continue
        obtenido = r.stdout
        fallos = []
        if r.returncode != 0 and prog.lenguaje == "python":
            err = (r.stderr or "").strip().splitlines()
            from core.diagnostico import explicar_error_ejecucion
            fallos.append("error al ejecutar: " + (explicar_error_ejecucion(err[-1], pr.entrada) if err
                                                   else f"código {r.returncode}"))
        elif r.returncode < 0:
            fallos.append({-11: "violación de segmento (accedes a memoria que no es tuya: ¿un puntero o un índice "
                                 "fuera del array?)", -8: "excepción aritmética (¿divides entre 0?)",
                           -6: "abortado (¿free doble o memoria corrupta?)"}.get(r.returncode,
                                                                                f"señal {-r.returncode}"))
        if pr.salida is not None and not salida_coincide(pr.salida, obtenido, pr.modo):
            fallos.append("la salida no es la esperada")
        if pr.verificar:
            fallos += pr.verificar(obtenido)
        shutil.rmtree(carpeta, ignore_errors=True)
        out.append(ResultadoPrueba(not fallos, pr.descripcion, pr.entrada, pr.salida or "",
                                   obtenido or "(no imprime nada)", "; ".join(fallos)))
    return out


def corregir(codigo: str, prog):
    """Devuelve (lista de ResultadoPrueba, mensajes del compilador)."""
    if prog.lenguaje == "mips":
        return correr_mips(codigo, prog), ""
    if prog.lenguaje == "c":
        return correr_c(codigo, prog)
    from core.diagnostico import diagnosticar
    diag, sintaxis = diagnosticar(codigo)
    if sintaxis:
        return [ResultadoPrueba(False, pr.descripcion, pr.entrada, pr.salida or "", "(no llega a ejecutarse)",
                                "error de sintaxis: mira la explicación de arriba 👆") for pr in prog.pruebas], diag
    return correr_python(codigo, prog), diag
