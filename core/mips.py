"""Simulador de MIPS32 (estilo MARS/SPIM) para la asignatura de Fundamentos de Computadores.

- Ensambla .data / .text con etiquetas, directivas (.word .half .byte .space .ascii .asciiz .align .float .double .globl)
  e instrucciones reales y pseudoinstrucciones (li, la, move, mul, div/rem de 3 operandos, b, beqz, bgt…, not, neg…).
- Acepta los operandos separados por comas o por espacios (como en las diapositivas: «li $t0 2»).
- Memoria little endian (como MARS en un PC). Segmentos: texto 0x00400000, datos 0x10010000, pila 0x7FFFEFFC.
- syscall: 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 17.
- E/S: mapa común (lw/sw a direcciones de dispositivo) o separado (in/out) mediante dispositivos simulados.
- Cuenta instrucciones ejecutadas y accesos a memoria (fetch + datos) y guarda la traza de direcciones para
  poder alimentar un simulador de caché.

Cada línea de ensamblador ocupa una palabra (4 bytes), también las pseudoinstrucciones: es el convenio de la
asignatura para contar instrucciones, bytes y accesos. `expansion()` dice en cuántas instrucciones reales se traduce.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
import struct

TEXT_BASE = 0x00400000
DATA_BASE = 0x10010000
STACK_TOP = 0x7FFFEFFC
GP_INIT = 0x10008000

NOMBRES = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3",
           "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
           "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7",
           "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]
NUM_REG = {n: i for i, n in enumerate(NOMBRES)}
NUM_REG["s8"] = 30
MASK = 0xFFFFFFFF


class ErrorMIPS(Exception):
    def __init__(self, msg, linea=None):
        super().__init__(msg if linea is None else f"Línea {linea}: {msg}")
        self.linea = linea


def s32(v):
    v &= MASK
    return v - (1 << 32) if v & 0x80000000 else v


def u32(v):
    return v & MASK


@dataclass
class Instr:
    op: str
    args: list
    linea: int
    texto: str
    dir: int = 0


@dataclass
class Programa:
    instrucciones: list
    etiquetas: dict
    datos: dict            # dirección → byte
    fin_datos: int
    lineas_fuente: list
    avisos: list = field(default_factory=list)


# ======================================================================= lectura
_RE_COM = re.compile(r"#.*$")


def _quitar_comentario(l: str) -> str:
    # respeta las # dentro de comillas
    out, dentro, q = [], False, ""
    i = 0
    while i < len(l):
        c = l[i]
        if dentro:
            out.append(c)
            if c == "\\" and i + 1 < len(l):
                out.append(l[i + 1])
                i += 2
                continue
            if c == q:
                dentro = False
        else:
            if c in "\"'":
                dentro, q = True, c
                out.append(c)
            elif c == "#":
                break
            else:
                out.append(c)
        i += 1
    return "".join(out)


def _tokens_operandos(s: str) -> list[str]:
    """Separa operandos por comas o espacios, respetando cadenas y paréntesis."""
    toks, cur, dentro, q, par = [], [], False, "", 0
    for c in s:
        if dentro:
            cur.append(c)
            if c == q:
                dentro = False
            continue
        if c in "\"'":
            dentro, q = True, c
            cur.append(c)
        elif c == "(":
            par += 1
            cur.append(c)
        elif c == ")":
            par -= 1
            cur.append(c)
        elif (c in ", \t") and par == 0:
            if cur:
                toks.append("".join(cur))
                cur = []
        else:
            cur.append(c)
    if cur:
        toks.append("".join(cur))
    # unir «4 ($t0)» → «4($t0)»
    out = []
    for t in toks:
        if t.startswith("(") and out and not out[-1].startswith("$") and re.fullmatch(r"[-+]?\w+", out[-1] or ""):
            out[-1] = out[-1] + t
        else:
            out.append(t)
    return out


def _escape(s: str) -> str:
    return (s.replace("\\n", "\n").replace("\\t", "\t").replace("\\0", "\0").replace('\\"', '"')
            .replace("\\\\", "\\"))


def leer_reg(t: str, linea=None) -> int:
    t = t.strip()
    if not t.startswith("$"):
        raise ErrorMIPS(f"se esperaba un registro y hay «{t}»", linea)
    n = t[1:].lower()
    if n.isdigit():
        k = int(n)
        if 0 <= k < 32:
            return k
    if n in NUM_REG:
        return NUM_REG[n]
    raise ErrorMIPS(f"registro desconocido «{t}»", linea)


def leer_freg(t: str, linea=None) -> int:
    t = t.strip().lower()
    m = re.fullmatch(r"\$f(\d+)", t)
    if not m or not 0 <= int(m.group(1)) < 32:
        raise ErrorMIPS(f"se esperaba un registro de coma flotante ($f0…$f31) y hay «{t}»", linea)
    return int(m.group(1))


def _num(t: str):
    t = t.strip()
    if re.fullmatch(r"'(\\.|.)'", t):
        return ord(_escape(t[1:-1]))
    neg = t.startswith("-")
    tt = t[1:] if t[:1] in "+-" else t
    if re.fullmatch(r"0[xX][0-9a-fA-F]+", tt):
        v = int(tt, 16)
    elif re.fullmatch(r"0[bB][01]+", tt):
        v = int(tt, 2)
    elif re.fullmatch(r"\d+", tt):
        v = int(tt)
    else:
        return None
    return -v if neg else v


# ======================================================================= ensamblador
DIRECTIVAS_DATOS = {".word", ".half", ".byte", ".space", ".ascii", ".asciiz", ".align", ".float", ".double"}


def ensamblar(fuente: str) -> Programa:
    lineas = fuente.replace("\r\n", "\n").split("\n")
    # .eqv NOMBRE valor  (constantes simbólicas, como en MARS): se sustituyen como texto
    eqv = {}
    for k, l in enumerate(lineas):
        m = re.match(r"^\s*\.eqv\s+([A-Za-z_]\w*)\s*,?\s*(.+?)\s*(#.*)?$", l)
        if m:
            eqv[m.group(1)] = m.group(2)
            lineas[k] = ""
    if eqv:
        patron = re.compile(r"(?<![\w$.])(" + "|".join(sorted(map(re.escape, eqv), key=len, reverse=True)) + r")(?!\w)")
        lineas = [patron.sub(lambda mm: eqv[mm.group(1)], l) if '"' not in l else l for l in lineas]
    seg = ".text"
    instrs: list[Instr] = []
    etiquetas: dict[str, int] = {}
    datos: dict[int, int] = {}
    pend_word: list[tuple[int, str, int]] = []      # (dir, etiqueta, línea) en .word etiqueta
    dato = DATA_BASE
    pc = TEXT_BASE
    avisos = []

    def alinear(n):
        nonlocal dato
        m = 1 << n
        if dato % m:
            dato += m - dato % m

    for nl, cruda in enumerate(lineas, 1):
        l = _quitar_comentario(cruda).strip()
        if not l:
            continue
        # etiquetas (puede haber varias en la misma línea)
        while True:
            m = re.match(r"^([A-Za-z_.$][\w.$]*)\s*:\s*(.*)$", l)
            if not m or m.group(1).startswith(".") and m.group(1) in DIRECTIVAS_DATOS | {".text", ".data", ".globl"}:
                break
            nombre = m.group(1)
            if nombre in etiquetas:
                raise ErrorMIPS(f"la etiqueta «{nombre}» está repetida", nl)
            if seg == ".data":
                # el dato que sigue fija la alineación (como MARS con .word)
                resto = m.group(2).strip()
                d = resto.split()[0] if resto else ""
                if d in (".word", ".float"):
                    alinear(2)
                elif d == ".half":
                    alinear(1)
                elif d == ".double":
                    alinear(3)
                etiquetas[nombre] = dato
            else:
                etiquetas[nombre] = pc
            l = m.group(2).strip()
        if not l:
            continue
        partes = l.split(None, 1)
        cab = partes[0]
        resto = partes[1] if len(partes) > 1 else ""
        low = cab.lower()
        if low in (".data", ".data:"):
            seg = ".data"
            if resto.strip():
                v = _num(resto.strip())
                if v is not None:
                    dato = v
            continue
        if low in (".text", ".text:"):
            seg = ".text"
            continue
        if low in (".globl", ".global", ".extern", ".kdata", ".ktext", ".set", ".ent", ".end"):
            continue
        if low.startswith("."):
            if seg != ".data":
                if low in DIRECTIVAS_DATOS:
                    raise ErrorMIPS(f"la directiva {low} solo puede ir en .data", nl)
                continue
            ops = _tokens_operandos(resto) if low not in (".ascii", ".asciiz") else []
            if low == ".align":
                alinear(int(_num(ops[0])))
            elif low == ".space":
                n = _num(ops[0])
                if n is None or n < 0:
                    raise ErrorMIPS(".space necesita un número de bytes", nl)
                for k in range(n):
                    datos[dato + k] = 0
                dato += n
            elif low in (".ascii", ".asciiz"):
                m2 = re.match(r'^"((?:\\.|[^"\\])*)"\s*$', resto.strip())
                if not m2:
                    raise ErrorMIPS(f"{low} necesita una cadena entre comillas dobles", nl)
                s = _escape(m2.group(1)) + ("\0" if low == ".asciiz" else "")
                for ch in s.encode("latin-1", errors="replace"):
                    datos[dato] = ch
                    dato += 1
            elif low in (".word", ".half", ".byte"):
                tam = {".word": 4, ".half": 2, ".byte": 1}[low]
                alinear({4: 2, 2: 1, 1: 0}[tam])
                for o in ops:
                    rep = 1
                    if ":" in o:            # .word 0:10  (MARS: valor:repeticiones)
                        o, r = o.split(":")
                        rep = int(_num(r))
                    for _ in range(rep):
                        v = _num(o)
                        if v is None:
                            if tam != 4:
                                raise ErrorMIPS(f"valor no válido «{o}»", nl)
                            pend_word.append((dato, o, nl))
                            v = 0
                        v &= (1 << (8 * tam)) - 1
                        for k in range(tam):
                            datos[dato + k] = (v >> (8 * k)) & 0xFF
                        dato += tam
            elif low in (".float", ".double"):
                tam = 4 if low == ".float" else 8
                alinear(2 if tam == 4 else 3)
                for o in ops:
                    b = struct.pack("<f" if tam == 4 else "<d", float(o))
                    for k, by in enumerate(b):
                        datos[dato + k] = by
                    dato += tam
            continue
        if seg == ".data":
            raise ErrorMIPS(f"«{cab}» no es una directiva de datos: ¿falta .text antes de las instrucciones?", nl)
        op = low
        args = _tokens_operandos(resto)
        if args and args[0] == "" :
            args = args[1:]
        instrs.append(Instr(op, args, nl, cruda.strip(), pc))
        pc += 4
    for d, et, nl in pend_word:
        if et not in etiquetas:
            raise ErrorMIPS(f"etiqueta desconocida «{et}»", nl)
        v = etiquetas[et]
        for k in range(4):
            datos[d + k] = (v >> (8 * k)) & 0xFF
    prog = Programa(instrs, etiquetas, datos, dato, lineas, avisos)
    for ins in instrs:
        _validar(ins, prog)
    return prog


# operandos esperados (r = registro, i = inmediato, l = etiqueta/dirección, m = memoria, f = reg. FP, x = reg o inm)
FORMAS = {
    "add": "rrx", "addu": "rrx", "sub": "rrx", "subu": "rrx", "and": "rrx", "or": "rrx", "xor": "rrx", "nor": "rrr",
    "slt": "rrx", "sltu": "rrx", "sllv": "rrr", "srlv": "rrr", "srav": "rrr",
    "addi": "rri", "addiu": "rri", "andi": "rri", "ori": "rri", "xori": "rri", "slti": "rri", "sltiu": "rri",
    "sll": "rri", "srl": "rri", "sra": "rri", "lui": "ri",
    "mult": "rr", "multu": "rr", "mfhi": "r", "mflo": "r", "mthi": "r", "mtlo": "r",
    "li": "ri", "la": "rl", "move": "rr", "not": "rr", "neg": "rr", "negu": "rr", "abs": "rr",
    "mul": "rrx", "mulo": "rrx", "rem": "rrx", "remu": "rrx", "divu": "rr*",
    "div": "rr*",
    "seq": "rrx", "sne": "rrx", "sge": "rrx", "sgt": "rrx", "sle": "rrx", "sgeu": "rrx", "sgtu": "rrx", "sleu": "rrx",
    "lw": "rm", "lh": "rm", "lhu": "rm", "lb": "rm", "lbu": "rm", "sw": "rm", "sh": "rm", "sb": "rm",
    "beq": "rxl", "bne": "rxl", "bgt": "rxl", "bge": "rxl", "blt": "rxl", "ble": "rxl",
    "bgtu": "rxl", "bgeu": "rxl", "bltu": "rxl", "bleu": "rxl",
    "beqz": "rl", "bnez": "rl", "bgez": "rl", "bgtz": "rl", "blez": "rl", "bltz": "rl", "bgezal": "rl", "bltzal": "rl",
    "b": "l", "j": "l", "jal": "l", "jr": "r", "jalr": "r*",
    "syscall": "", "nop": "", "break": "*",
    "in": "ri", "out": "ri",
    # coma flotante
    "lwc1": "fm", "swc1": "fm", "l.s": "fm", "s.s": "fm", "l.d": "fm", "s.d": "fm", "ldc1": "fm", "sdc1": "fm",
    "li.s": "f*", "li.d": "f*",
    "add.s": "fff", "sub.s": "fff", "mul.s": "fff", "div.s": "fff",
    "add.d": "fff", "sub.d": "fff", "mul.d": "fff", "div.d": "fff",
    "mov.s": "ff", "mov.d": "ff", "neg.s": "ff", "neg.d": "ff", "abs.s": "ff", "abs.d": "ff", "sqrt.s": "ff", "sqrt.d": "ff",
    "cvt.s.w": "ff", "cvt.w.s": "ff", "cvt.d.w": "ff", "cvt.w.d": "ff", "cvt.d.s": "ff", "cvt.s.d": "ff",
    "trunc.w.s": "ff", "trunc.w.d": "ff",
    "mtc1": "rf", "mfc1": "rf",
    "c.eq.s": "ff", "c.lt.s": "ff", "c.le.s": "ff", "c.eq.d": "ff", "c.lt.d": "ff", "c.le.d": "ff",
    "bc1t": "l", "bc1f": "l",
}

PSEUDO = {"li", "la", "move", "not", "neg", "negu", "abs", "mul", "mulo", "rem", "remu", "seq", "sne", "sge", "sgt",
          "sle", "sgeu", "sgtu", "sleu", "bgt", "bge", "blt", "ble", "bgtu", "bgeu", "bltu", "bleu", "beqz", "bnez", "b",
          "nop", "li.s", "li.d", "l.s", "s.s", "l.d", "s.d"}


def _validar(ins: Instr, prog: Programa):
    if ins.op not in FORMAS:
        raise ErrorMIPS(f"instrucción desconocida «{ins.op}»", ins.linea)
    f = FORMAS[ins.op]
    a = ins.args
    if f.endswith("*"):
        base = f[:-1]
        if len(a) < len(base):
            raise ErrorMIPS(f"{ins.op} necesita al menos {len(base)} operandos", ins.linea)
    elif len(a) != len(f):
        raise ErrorMIPS(f"{ins.op} necesita {len(f)} operando(s) ({_desc(f)}) y tiene {len(a)}: «{ins.texto}»", ins.linea)
    for tipo, arg in zip(f.rstrip("*"), a):
        if tipo == "r":
            leer_reg(arg, ins.linea)
        elif tipo == "f":
            leer_freg(arg, ins.linea)
        elif tipo == "i":
            if _num(arg) is None:
                if arg.startswith("$"):
                    raise ErrorMIPS(f"«{ins.op}» necesita un número inmediato y le has dado el registro {arg} "
                                    f"(¿querías «{ins.op[:-1] if ins.op.endswith('i') else ins.op}» sin la i?)", ins.linea)
                if arg not in prog.etiquetas:
                    raise ErrorMIPS(f"valor inmediato no válido «{arg}»", ins.linea)
        elif tipo == "x":
            if not arg.startswith("$") and _num(arg) is None:
                raise ErrorMIPS(f"operando no válido «{arg}»", ins.linea)
        elif tipo == "l":
            if arg not in prog.etiquetas and _num(arg) is None:
                raise ErrorMIPS(f"etiqueta desconocida «{arg}»", ins.linea)


def _desc(f):
    return ", ".join({"r": "registro", "i": "inmediato", "l": "etiqueta", "m": "dirección", "f": "registro FP",
                      "x": "registro o inmediato"}[c] for c in f)


def expansion(ins: Instr, prog: Programa | None = None) -> int:
    """Número de instrucciones máquina reales en que se traduce (aproximado, como MARS)."""
    op, a = ins.op, ins.args
    if op == "li":
        v = _num(a[1])
        return 1 if v is not None and -32768 <= v <= 65535 else 2
    if op == "la":
        return 2
    if op in ("mul", "rem", "remu", "seq", "sne", "sge", "sgt", "sle") and len(a) == 3:
        return 2 if a[2].startswith("$") or op != "mul" else 2
    if op in ("bgt", "bge", "blt", "ble", "bgtu", "bgeu", "bltu", "bleu"):
        return 2
    if op == "div" and len(a) == 3:
        return 2
    if op in ("lw", "sw", "lb", "lbu", "sb", "lh", "lhu", "sh") and not re.search(r"\(\$\w+\)$", a[1]):
        return 2
    return 1


# ======================================================================= dispositivos de E/S
class Dispositivo:
    """Dispositivo de E/S simulado: lectura y escritura de registros por dirección."""
    def leer(self, dir_: int) -> int | None:
        return None

    def escribir(self, dir_: int, valor: int) -> bool:
        return False


@dataclass
class Resultado:
    salida: str           # lo que se vería en la consola (incluye el eco de lo tecleado)
    regs: list
    hi: int
    lo: int
    fregs: list
    memoria: dict
    pasos: int
    accesos_instr: int
    accesos_datos: int
    lecturas: int
    escrituras: int
    traza: list           # (tipo 'I'/'R'/'W', dirección)
    termino: bool
    motivo: str
    pc_final: int
    historial: list       # (paso, línea, texto, cambios)
    etiquetas: dict
    salida_programa: str = ""     # solo lo que imprime el programa


class Maquina:
    def __init__(self, prog: Programa, entrada: list[str] | str | None = None, dispositivos=None, max_pasos=2_000_000,
                 registrar_historial=0, regs_iniciales: dict | None = None, little_endian=True, mem_extra=None):
        self.p = prog
        self.R = [0] * 32
        self.F = [0] * 32      # bits crudos de los registros FP
        self.fcc = False
        self.hi = self.lo = 0
        self.mem: dict[int, int] = dict(prog.datos)
        if mem_extra:
            self.mem.update(mem_extra)
        self.R[29] = STACK_TOP
        self.R[28] = GP_INIT
        if regs_iniciales:
            for k, v in regs_iniciales.items():
                self.R[leer_reg(k) if isinstance(k, str) else k] = u32(v)
        self.pc = TEXT_BASE if "main" not in prog.etiquetas else prog.etiquetas["main"]
        if isinstance(entrada, str):
            entrada = entrada.split("\n")
        self.entrada = list(entrada or [])
        self.salida: list[str] = []
        self.salida_prog: list[str] = []
        self.dispositivos = dispositivos or []
        self.puertos: dict[int, int] = {}
        self.max_pasos = max_pasos
        self.pasos = 0
        self.acc_i = self.acc_d = self.lect = self.escr = 0
        self.traza = []
        self.hist_n = registrar_historial
        self.historial = []
        self.le = little_endian
        self.idx = {ins.dir: k for k, ins in enumerate(prog.instrucciones)}

    # ---- memoria
    def _dev_leer(self, d):
        for dev in self.dispositivos:
            v = dev.leer(d)
            if v is not None:
                return u32(v)
        return None

    def leer_mem(self, d, tam, linea):
        if d % tam:
            raise ErrorMIPS(f"acceso no alineado: dirección 0x{d:08X} no es múltiplo de {tam}", linea)
        v = self._dev_leer(d)
        if v is not None:
            return v & ((1 << (8 * tam)) - 1)
        bs = [self.mem.get(d + k, 0) for k in range(tam)]
        if not self.le:
            bs = bs[::-1]
        return sum(b << (8 * k) for k, b in enumerate(bs))

    def escribir_mem(self, d, tam, v, linea):
        if d % tam:
            raise ErrorMIPS(f"acceso no alineado: dirección 0x{d:08X} no es múltiplo de {tam}", linea)
        for dev in self.dispositivos:
            if dev.escribir(d, u32(v)):
                return
        bs = [(v >> (8 * k)) & 0xFF for k in range(tam)]
        if not self.le:
            bs = bs[::-1]
        for k in range(tam):
            self.mem[d + k] = bs[k]

    def palabra(self, d):
        return self.leer_mem(d, 4, None)

    def cadena(self, d, maximo=10000):
        out = []
        while len(out) < maximo:
            b = self.mem.get(d, 0)
            if b == 0:
                break
            out.append(chr(b))
            d += 1
        return "".join(out)

    # ---- operandos
    def _val(self, t, linea):
        if t.startswith("$"):
            return self.R[leer_reg(t, linea)]
        v = _num(t)
        if v is None:
            if t in self.p.etiquetas:
                return self.p.etiquetas[t]
            raise ErrorMIPS(f"operando no válido «{t}»", linea)
        return u32(v)

    def _dir(self, t, linea):
        """Dirección de un operando de memoria: n, etiq, ($r), n($r), etiq($r), etiq+n, etiq+n($r)."""
        t = t.strip()
        m = re.fullmatch(r"(.*?)\((\$\w+)\)", t)
        base = 0
        if m:
            base = self.R[leer_reg(m.group(2), linea)]
            t = m.group(1).strip()
        if not t:
            return u32(base)
        m2 = re.fullmatch(r"([A-Za-z_.$][\w.$]*)\s*([+-]\s*\w+)?", t)
        if m2 and m2.group(1) in self.p.etiquetas:
            off = _num(m2.group(2).replace(" ", "")) if m2.group(2) else 0
            return u32(self.p.etiquetas[m2.group(1)] + off + base)
        v = _num(t)
        if v is None:
            raise ErrorMIPS(f"dirección no válida «{t}»", linea)
        return u32(v + base)

    def _destino(self, t, linea):
        if t in self.p.etiquetas:
            return self.p.etiquetas[t]
        v = _num(t)
        if v is None:
            raise ErrorMIPS(f"etiqueta desconocida «{t}»", linea)
        return u32(v)

    def _f(self, k, doble=False):
        if doble:
            bits = self.F[k] | (self.F[k + 1] << 32)
            return struct.unpack("<d", struct.pack("<Q", bits))[0]
        return struct.unpack("<f", struct.pack("<I", self.F[k]))[0]

    def _setf(self, k, v, doble=False):
        if doble:
            bits = struct.unpack("<Q", struct.pack("<d", v))[0]
            self.F[k] = bits & MASK
            self.F[k + 1] = bits >> 32
        else:
            self.F[k] = struct.unpack("<I", struct.pack("<f", v))[0]

    # ---- ejecución
    def ejecutar(self) -> Resultado:
        motivo, termino = "", False
        try:
            while True:
                if self.pasos >= self.max_pasos:
                    motivo = f"se ha parado tras {self.max_pasos:,} instrucciones (¿bucle infinito?)".replace(",", ".")
                    break
                if self.pc not in self.idx:
                    if self.pc == 0 or self.pc == TEXT_BASE + 4 * len(self.p.instrucciones):
                        termino = True
                        motivo = "el programa ha llegado al final del código"
                    else:
                        motivo = f"el PC (0x{self.pc:08X}) no apunta a ninguna instrucción"
                    break
                ins = self.p.instrucciones[self.idx[self.pc]]
                antes = list(self.R) if self.hist_n and len(self.historial) < self.hist_n else None
                self.acc_i += 1
                self.traza.append(("I", self.pc))
                self.pasos += 1
                fin = self._paso(ins)
                if antes is not None:
                    cambios = {NOMBRES[k]: s32(self.R[k]) for k in range(32) if self.R[k] != antes[k]}
                    self.historial.append((self.pasos, ins.linea, ins.texto, cambios))
                if fin:
                    termino = True
                    motivo = "fin del programa (syscall 10)"
                    break
        except ErrorMIPS as exc:
            motivo = str(exc)
        except _SinEntrada:
            motivo = "el programa pide un dato por teclado y no quedan datos de entrada"
        return Resultado("".join(self.salida), [s32(r) for r in self.R], s32(self.hi), s32(self.lo), list(self.F),
                         self.mem, self.pasos, self.acc_i, self.acc_d, self.lect, self.escr, self.traza, termino,
                         motivo, self.pc, self.historial, dict(self.p.etiquetas), "".join(self.salida_prog))

    def _set(self, r, v):
        if r != 0:
            self.R[r] = u32(v)

    def _paso(self, ins: Instr):
        op, a, L = ins.op, ins.args, ins.linea
        R = self.R
        sig = self.pc + 4
        g = lambda k: leer_reg(a[k], L)  # noqa: E731
        v = lambda k: self._val(a[k], L)  # noqa: E731
        # ---------------- aritméticas
        if op in ("add", "addi"):
            x, y = s32(R[g(1)]), s32(v(2))
            r = x + y
            if not -(1 << 31) <= r < (1 << 31):
                raise ErrorMIPS(f"desbordamiento (overflow) aritmético en «{ins.texto}»: {x} + {y} no cabe en 32 bits "
                                f"con signo (usa addu/addiu si es intencionado)", L)
            self._set(g(0), r)
        elif op in ("addu", "addiu"):
            self._set(g(0), R[g(1)] + v(2))
        elif op == "sub":
            x, y = s32(R[g(1)]), s32(v(2))
            r = x - y
            if not -(1 << 31) <= r < (1 << 31):
                raise ErrorMIPS(f"desbordamiento (overflow) en «{ins.texto}»", L)
            self._set(g(0), r)
        elif op == "subu":
            self._set(g(0), R[g(1)] - v(2))
        elif op in ("mul", "mulo"):
            p_ = s32(R[g(1)]) * s32(v(2))
            self.hi, self.lo = u32(p_ >> 32), u32(p_)
            self._set(g(0), p_)
        elif op in ("mult", "multu"):
            x, y = (s32(R[g(0)]), s32(R[g(1)])) if op == "mult" else (R[g(0)], R[g(1)])
            p_ = x * y
            self.hi, self.lo = u32(p_ >> 32), u32(p_)
        elif op in ("div", "divu"):
            if len(a) == 3:
                x, y = s32(R[g(1)]), s32(v(2))
                if y == 0:
                    raise ErrorMIPS("división entre cero", L)
                q = int(x / y)
                self.lo, self.hi = u32(q), u32(x - q * y)
                self._set(g(0), q)
            else:
                x, y = (s32(R[g(0)]), s32(R[g(1)])) if op == "div" else (R[g(0)], R[g(1)])
                if y == 0:
                    raise ErrorMIPS("división entre cero", L)
                q = int(x / y)
                self.lo, self.hi = u32(q), u32(x - q * y)
        elif op in ("rem", "remu"):
            x, y = s32(R[g(1)]), s32(v(2))
            if y == 0:
                raise ErrorMIPS("división entre cero", L)
            q = int(x / y)
            self._set(g(0), x - q * y)
        elif op == "mfhi":
            self._set(g(0), self.hi)
        elif op == "mflo":
            self._set(g(0), self.lo)
        elif op == "mthi":
            self.hi = R[g(0)]
        elif op == "mtlo":
            self.lo = R[g(0)]
        # ---------------- lógicas
        elif op in ("and", "andi"):
            self._set(g(0), R[g(1)] & (v(2) & (0xFFFF if op == "andi" else MASK)))
        elif op in ("or", "ori"):
            self._set(g(0), R[g(1)] | (v(2) & (0xFFFF if op == "ori" else MASK)))
        elif op in ("xor", "xori"):
            self._set(g(0), R[g(1)] ^ (v(2) & (0xFFFF if op == "xori" else MASK)))
        elif op == "nor":
            self._set(g(0), ~(R[g(1)] | R[g(2)]))
        elif op == "not":
            self._set(g(0), ~R[g(1)])
        elif op in ("neg", "negu"):
            self._set(g(0), -s32(R[g(1)]))
        elif op == "abs":
            self._set(g(0), abs(s32(R[g(1)])))
        elif op == "sll":
            self._set(g(0), R[g(1)] << (v(2) & 31))
        elif op == "srl":
            self._set(g(0), R[g(1)] >> (v(2) & 31))
        elif op == "sra":
            self._set(g(0), s32(R[g(1)]) >> (v(2) & 31))
        elif op == "sllv":
            self._set(g(0), R[g(1)] << (R[g(2)] & 31))
        elif op == "srlv":
            self._set(g(0), R[g(1)] >> (R[g(2)] & 31))
        elif op == "srav":
            self._set(g(0), s32(R[g(1)]) >> (R[g(2)] & 31))
        elif op == "lui":
            self._set(g(0), (v(1) & 0xFFFF) << 16)
        # ---------------- comparaciones
        elif op in ("slt", "slti"):
            self._set(g(0), int(s32(R[g(1)]) < s32(v(2))))
        elif op in ("sltu", "sltiu"):
            self._set(g(0), int(R[g(1)] < u32(v(2))))
        elif op in ("seq", "sne", "sge", "sgt", "sle", "sgeu", "sgtu", "sleu"):
            if op.endswith("u"):
                x, y = R[g(1)], u32(v(2))
            else:
                x, y = s32(R[g(1)]), s32(v(2))
            r = {"seq": x == y, "sne": x != y, "sge": x >= y, "sgt": x > y, "sle": x <= y,
                 "sgeu": x >= y, "sgtu": x > y, "sleu": x <= y}[op]
            self._set(g(0), int(r))
        # ---------------- movimiento
        elif op == "li":
            self._set(g(0), v(1))
        elif op == "la":
            self._set(g(0), self._dir(a[1], L))
        elif op == "move":
            self._set(g(0), R[g(1)])
        # ---------------- memoria
        elif op in ("lw", "lh", "lhu", "lb", "lbu"):
            d = self._dir(a[1], L)
            tam = {"lw": 4, "lh": 2, "lhu": 2, "lb": 1, "lbu": 1}[op]
            x = self.leer_mem(d, tam, L)
            if op in ("lh", "lb") and x & (1 << (8 * tam - 1)):
                x -= 1 << (8 * tam)
            self._set(g(0), x)
            self.acc_d += 1
            self.lect += 1
            self.traza.append(("R", d))
        elif op in ("sw", "sh", "sb"):
            d = self._dir(a[1], L)
            tam = {"sw": 4, "sh": 2, "sb": 1}[op]
            self.escribir_mem(d, tam, R[g(0)] & ((1 << (8 * tam)) - 1), L)
            self.acc_d += 1
            self.escr += 1
            self.traza.append(("W", d))
        # ---------------- saltos
        elif op in ("beq", "bne", "bgt", "bge", "blt", "ble", "bgtu", "bgeu", "bltu", "bleu"):
            if op.endswith("u") and op not in ("beq",):
                x, y = R[g(0)], u32(v(1))
            else:
                x, y = s32(R[g(0)]), s32(v(1))
            c = {"beq": x == y, "bne": x != y, "bgt": x > y, "bge": x >= y, "blt": x < y, "ble": x <= y,
                 "bgtu": x > y, "bgeu": x >= y, "bltu": x < y, "bleu": x <= y}[op]
            if c:
                sig = self._destino(a[2], L)
        elif op in ("beqz", "bnez", "bgez", "bgtz", "blez", "bltz", "bgezal", "bltzal"):
            x = s32(R[g(0)])
            c = {"beqz": x == 0, "bnez": x != 0, "bgez": x >= 0, "bgtz": x > 0, "blez": x <= 0, "bltz": x < 0,
                 "bgezal": x >= 0, "bltzal": x < 0}[op]
            if op.endswith("al"):
                self._set(31, self.pc + 4)
            if c:
                sig = self._destino(a[1], L)
        elif op in ("b", "j"):
            sig = self._destino(a[0], L)
        elif op == "jal":
            self._set(31, self.pc + 4)
            sig = self._destino(a[0], L)
        elif op == "jr":
            sig = R[g(0)]
        elif op == "jalr":
            dest = R[g(0)] if len(a) == 1 else R[g(1)]
            self._set(31 if len(a) == 1 else g(0), self.pc + 4)
            sig = dest
        elif op == "nop":
            pass
        elif op == "break":
            raise ErrorMIPS("instrucción break: ejecución detenida", L)
        # ---------------- E/S con mapa separado
        elif op == "in":
            port = v(1)
            val = None
            for dev in self.dispositivos:
                val = dev.leer(port)
                if val is not None:
                    break
            self._set(g(0), self.puertos.get(port, 0) if val is None else val)
        elif op == "out":
            port = v(1)
            ok = False
            for dev in self.dispositivos:
                ok = dev.escribir(port, R[g(0)]) or ok
            if not ok:
                self.puertos[port] = R[g(0)]
        # ---------------- syscall
        elif op == "syscall":
            return self._syscall(L)
        # ---------------- coma flotante
        elif op in ("lwc1", "l.s", "swc1", "s.s", "l.d", "s.d", "ldc1", "sdc1"):
            fr = leer_freg(a[0], L)
            d = self._dir(a[1], L)
            self.acc_d += 1
            if op in ("lwc1", "l.s"):
                self.F[fr] = self.leer_mem(d, 4, L)
                self.lect += 1
                self.traza.append(("R", d))
            elif op in ("swc1", "s.s"):
                self.escribir_mem(d, 4, self.F[fr], L)
                self.escr += 1
                self.traza.append(("W", d))
            elif op in ("l.d", "ldc1"):
                self.F[fr] = self.leer_mem(d, 4, L)
                self.F[fr + 1] = self.leer_mem(d + 4, 4, L)
                self.lect += 1
                self.traza.append(("R", d))
            else:
                self.escribir_mem(d, 4, self.F[fr], L)
                self.escribir_mem(d + 4, 4, self.F[fr + 1], L)
                self.escr += 1
                self.traza.append(("W", d))
        elif op in ("li.s", "li.d"):
            self._setf(leer_freg(a[0], L), float(a[1]), op == "li.d")
        elif op[:-2] in ("add", "sub", "mul", "div") and op[-2:] in (".s", ".d"):
            dbl = op.endswith(".d")
            x, y = self._f(leer_freg(a[1], L), dbl), self._f(leer_freg(a[2], L), dbl)
            if op.startswith("div") and y == 0:
                r = float("inf") if x > 0 else float("-inf") if x < 0 else float("nan")
            else:
                r = {"add": x + y, "sub": x - y, "mul": x * y, "div": x / y if y else 0}[op[:-2]]
            self._setf(leer_freg(a[0], L), r, dbl)
        elif op in ("mov.s", "mov.d", "neg.s", "neg.d", "abs.s", "abs.d", "sqrt.s", "sqrt.d"):
            dbl = op.endswith(".d")
            x = self._f(leer_freg(a[1], L), dbl)
            r = {"mov": x, "neg": -x, "abs": abs(x), "sqrt": x ** 0.5 if x >= 0 else float("nan")}[op[:-2]]
            self._setf(leer_freg(a[0], L), r, dbl)
        elif op in ("cvt.s.w", "cvt.d.w"):
            n = s32(self.F[leer_freg(a[1], L)])
            self._setf(leer_freg(a[0], L), float(n), op == "cvt.d.w")
        elif op in ("cvt.w.s", "cvt.w.d", "trunc.w.s", "trunc.w.d"):
            x = self._f(leer_freg(a[1], L), op.endswith(".d"))
            self.F[leer_freg(a[0], L)] = u32(int(round(x)) if op.startswith("cvt") else int(x))
        elif op == "cvt.d.s":
            self._setf(leer_freg(a[0], L), self._f(leer_freg(a[1], L)), True)
        elif op == "cvt.s.d":
            self._setf(leer_freg(a[0], L), self._f(leer_freg(a[1], L), True))
        elif op == "mtc1":
            self.F[leer_freg(a[1], L)] = R[g(0)]
        elif op == "mfc1":
            self._set(g(0), self.F[leer_freg(a[1], L)])
        elif op.startswith("c."):
            dbl = op.endswith(".d")
            x, y = self._f(leer_freg(a[0], L), dbl), self._f(leer_freg(a[1], L), dbl)
            self.fcc = {"eq": x == y, "lt": x < y, "le": x <= y}[op.split(".")[1]]
        elif op == "bc1t":
            if self.fcc:
                sig = self._destino(a[0], L)
        elif op == "bc1f":
            if not self.fcc:
                sig = self._destino(a[0], L)
        else:
            raise ErrorMIPS(f"instrucción no implementada «{op}»", L)
        self.pc = u32(sig)
        return False

    def _leer_linea(self):
        if not self.entrada:
            raise _SinEntrada()
        return self.entrada.pop(0)

    def _out(self, t):
        self.salida.append(t)
        self.salida_prog.append(t)

    def _syscall(self, L):
        cod = s32(self.R[2])
        a0 = self.R[4]
        if cod == 1:
            self._out(str(s32(a0)))
        elif cod == 2:
            self._out(_fmt_float(self._f(12)))
        elif cod == 3:
            self._out(_fmt_float(self._f(12, True)))
        elif cod == 4:
            self._out(self.cadena(a0))
        elif cod == 5:
            t = self._leer_linea().strip()
            try:
                self.R[2] = u32(int(t))
            except ValueError as exc:
                raise ErrorMIPS(f"la entrada «{t}» no es un entero", L) from exc
            self.salida.append(t + "\n")
        elif cod in (6, 7):
            t = self._leer_linea().strip()
            self._setf(0, float(t), cod == 7)
            self.salida.append(t + "\n")
        elif cod == 8:
            t = self._leer_linea()
            n = s32(self.R[5])
            s = (t + "\n")[: max(0, n - 1)]
            for k, ch in enumerate(s.encode("latin-1", "replace")):
                self.mem[a0 + k] = ch
            self.mem[a0 + len(s)] = 0
            self.salida.append(t + "\n")
        elif cod in (10, 17):
            self.pc += 4
            return True
        elif cod == 11:
            self._out(chr(a0 & 0xFF))
        elif cod == 12:
            t = self._leer_linea()
            self.R[2] = ord(t[0]) if t else 10
            self.salida.append((t[:1] if t else "") + "\n")
        else:
            raise ErrorMIPS(f"código de syscall no soportado: {cod}", L)
        self.pc += 4
        return False


class _SinEntrada(Exception):
    pass


def _fmt_float(x):
    if x == int(x) and abs(x) < 1e16:
        return f"{x:.1f}"
    return repr(float(f"{x:.7g}"))


def ejecutar(fuente: str, entrada=None, **kw) -> Resultado:
    return Maquina(ensamblar(fuente), entrada, **kw).ejecutar()


def palabras(res: Resultado, desde: int, n: int, little=True) -> list[int]:
    out = []
    for k in range(n):
        bs = [res.memoria.get(desde + 4 * k + j, 0) for j in range(4)]
        if not little:
            bs = bs[::-1]
        out.append(s32(sum(b << (8 * j) for j, b in enumerate(bs))))
    return out


# ======================================================================= codificación binaria (formatos R, I, J)
OPCODES = {"addi": 8, "addiu": 9, "slti": 10, "sltiu": 11, "andi": 12, "ori": 13, "xori": 14, "lui": 15,
           "lw": 35, "lb": 32, "lbu": 36, "lh": 33, "lhu": 37, "sw": 43, "sb": 40, "sh": 41,
           "beq": 4, "bne": 5, "blez": 6, "bgtz": 7, "j": 2, "jal": 3}
FUNCT = {"add": 32, "addu": 33, "sub": 34, "subu": 35, "and": 36, "or": 37, "xor": 38, "nor": 39, "slt": 42,
         "sltu": 43, "sll": 0, "srl": 2, "sra": 3, "sllv": 4, "srlv": 6, "srav": 7, "jr": 8, "jalr": 9,
         "mult": 24, "multu": 25, "div": 26, "divu": 27, "mfhi": 16, "mflo": 18, "syscall": 12, "break": 13}


@dataclass
class Codificacion:
    tipo: str
    campos: list          # (nombre, valor, bits)
    binario: str
    hexa: str
    explicacion: str


def codificar(linea: str, pc: int = TEXT_BASE, etiquetas: dict | None = None) -> Codificacion:
    """Codifica en binario una instrucción real del MIPS (tipos R, I y J)."""
    l = _quitar_comentario(linea).strip()
    partes = l.split(None, 1)
    op = partes[0].lower()
    a = _tokens_operandos(partes[1]) if len(partes) > 1 else []
    et = etiquetas or {}

    def num(t):
        v = _num(t)
        if v is None:
            if t in et:
                return et[t]
            raise ErrorMIPS(f"«{t}» no es un número")
        return v

    def campos_bin(cs):
        return " ".join(format(v & ((1 << b) - 1), f"0{b}b") for _, v, b in cs)

    if op in FUNCT and op not in ("jr", "jalr", "mult", "multu", "div", "divu", "mfhi", "mflo", "syscall", "break",
                                  "sll", "srl", "sra"):
        rd, rs, rt = leer_reg(a[0]), leer_reg(a[1]), leer_reg(a[2])
        if op in ("sllv", "srlv", "srav"):
            rs, rt = rt, rs
        cs = [("op", 0, 6), ("rs", rs, 5), ("rt", rt, 5), ("rd", rd, 5), ("shamt", 0, 5), ("funct", FUNCT[op], 6)]
        exp = f"Tipo R: op = 0 y la operación va en funct = {FUNCT[op]}. rd = {rd} (destino), rs = {rs}, rt = {rt}."
        tipo = "R"
    elif op in ("sll", "srl", "sra"):
        rd, rt, sh = leer_reg(a[0]), leer_reg(a[1]), num(a[2])
        cs = [("op", 0, 6), ("rs", 0, 5), ("rt", rt, 5), ("rd", rd, 5), ("shamt", sh, 5), ("funct", FUNCT[op], 6)]
        exp = f"Tipo R de desplazamiento: rs no se usa (0), rt = {rt} es el registro que se desplaza, shamt = {sh}."
        tipo = "R"
    elif op in ("jr",):
        rs = leer_reg(a[0])
        cs = [("op", 0, 6), ("rs", rs, 5), ("rt", 0, 5), ("rd", 0, 5), ("shamt", 0, 5), ("funct", 8, 6)]
        exp = f"jr es tipo R con funct = 8; el registro va en rs = {rs}."
        tipo = "R"
    elif op in ("mult", "multu", "div", "divu"):
        rs, rt = leer_reg(a[0]), leer_reg(a[1])
        cs = [("op", 0, 6), ("rs", rs, 5), ("rt", rt, 5), ("rd", 0, 5), ("shamt", 0, 5), ("funct", FUNCT[op], 6)]
        exp = f"{op} deja el resultado en HI/LO, por eso rd = 0."
        tipo = "R"
    elif op in ("mfhi", "mflo"):
        rd = leer_reg(a[0])
        cs = [("op", 0, 6), ("rs", 0, 5), ("rt", 0, 5), ("rd", rd, 5), ("shamt", 0, 5), ("funct", FUNCT[op], 6)]
        exp = f"{op}: solo se usa rd = {rd}."
        tipo = "R"
    elif op == "syscall":
        cs = [("op", 0, 6), ("código", 0, 20), ("funct", 12, 6)]
        exp = "syscall: op = 0, funct = 12."
        tipo = "R"
    elif op in ("addi", "addiu", "slti", "sltiu", "andi", "ori", "xori"):
        rt, rs, imm = leer_reg(a[0]), leer_reg(a[1]), num(a[2])
        if not -32768 <= imm <= 65535:
            raise ErrorMIPS(f"el inmediato {imm} no cabe en 16 bits: el ensamblador usaría lui + ori con $at")
        cs = [("op", OPCODES[op], 6), ("rs", rs, 5), ("rt", rt, 5), ("inmediato", imm, 16)]
        exp = (f"Tipo I: op = {OPCODES[op]}. ¡Ojo al orden! En ensamblador el destino va primero, pero en binario "
               f"va rs = {rs} (fuente) y después rt = {rt} (destino). Inmediato {imm} en 16 bits"
               + (" en complemento a 2." if imm < 0 else "."))
        tipo = "I"
    elif op == "lui":
        rt, imm = leer_reg(a[0]), num(a[1])
        cs = [("op", 15, 6), ("rs", 0, 5), ("rt", rt, 5), ("inmediato", imm, 16)]
        exp = "lui: tipo I con rs = 0."
        tipo = "I"
    elif op in ("lw", "lb", "lbu", "lh", "lhu", "sw", "sb", "sh"):
        rt = leer_reg(a[0])
        m = re.fullmatch(r"(.*?)\((\$\w+)\)", a[1].strip())
        if not m:
            raise ErrorMIPS("para codificarla usa la forma desplazamiento($registro)")
        off = num(m.group(1)) if m.group(1).strip() else 0
        rs = leer_reg(m.group(2))
        cs = [("op", OPCODES[op], 6), ("rs", rs, 5), ("rt", rt, 5), ("desplazamiento", off, 16)]
        exp = f"Tipo I: base rs = {rs}, registro de datos rt = {rt}, desplazamiento {off} (con signo)."
        tipo = "I"
    elif op in ("beq", "bne"):
        rs, rt = leer_reg(a[0]), leer_reg(a[1])
        dest = num(a[2])
        if a[2] in et:
            off = (dest - (pc + 4)) // 4
            exp_d = f"desplazamiento = (destino − (PC + 4)) / 4 = (0x{dest:X} − 0x{pc + 4:X}) / 4 = {off}"
        else:
            off = dest
            exp_d = f"desplazamiento = {off} instrucciones"
        cs = [("op", OPCODES[op], 6), ("rs", rs, 5), ("rt", rt, 5), ("desplazamiento", off, 16)]
        exp = f"Tipo I relativo a PC: {exp_d}, en complemento a 2."
        tipo = "I"
    elif op in ("blez", "bgtz"):
        rs = leer_reg(a[0])
        dest = num(a[1])
        off = (dest - (pc + 4)) // 4 if a[1] in et else dest
        cs = [("op", OPCODES[op], 6), ("rs", rs, 5), ("rt", 0, 5), ("desplazamiento", off, 16)]
        exp = "Tipo I relativo a PC."
        tipo = "I"
    elif op in ("j", "jal"):
        dest = num(a[0])
        campo = (dest >> 2) & ((1 << 26) - 1)
        cs = [("op", OPCODES[op], 6), ("dirección/4", campo, 26)]
        exp = (f"Tipo J: se guarda la dirección dividida entre 4 (en palabras): 0x{dest:X} / 4 = 0x{campo:X}. "
               "Al saltar se multiplica por 4 y se completa con los 4 bits altos del PC.")
        tipo = "J"
    else:
        raise ErrorMIPS(f"«{op}» es una pseudoinstrucción o no está en la tabla: no tiene una única codificación")
    b = "".join(format(v & ((1 << n) - 1), f"0{n}b") for _, v, n in cs)
    return Codificacion(tipo, cs, campos_bin(cs), f"0x{int(b, 2):08X}", exp)


def decodificar(palabra: int) -> str:
    """Instrucción en ensamblador a partir de su código máquina (tipos R, I y J más comunes)."""
    op = (palabra >> 26) & 63
    rs, rt, rd = (palabra >> 21) & 31, (palabra >> 16) & 31, (palabra >> 11) & 31
    sh, fn, imm = (palabra >> 6) & 31, palabra & 63, palabra & 0xFFFF
    simm = imm - 0x10000 if imm & 0x8000 else imm
    n = lambda k: "$" + NOMBRES[k]  # noqa: E731
    if op == 0:
        inv = {v: k for k, v in FUNCT.items()}
        f = inv.get(fn)
        if f in ("sll", "srl", "sra"):
            return f"{f} {n(rd)}, {n(rt)}, {sh}"
        if f == "jr":
            return f"jr {n(rs)}"
        if f in ("mult", "multu", "div", "divu"):
            return f"{f} {n(rs)}, {n(rt)}"
        if f in ("mfhi", "mflo"):
            return f"{f} {n(rd)}"
        if f == "syscall":
            return "syscall"
        if f:
            return f"{f} {n(rd)}, {n(rs)}, {n(rt)}"
        return f"(funct {fn} desconocida)"
    inv = {v: k for k, v in OPCODES.items()}
    o = inv.get(op)
    if o in ("j", "jal"):
        return f"{o} 0x{(palabra & 0x3FFFFFF) << 2:08X}"
    if o in ("lw", "lb", "lbu", "lh", "lhu", "sw", "sb", "sh"):
        return f"{o} {n(rt)}, {simm}({n(rs)})"
    if o in ("beq", "bne"):
        return f"{o} {n(rs)}, {n(rt)}, {simm}"
    if o == "lui":
        return f"lui {n(rt)}, 0x{imm:X}"
    if o:
        return f"{o} {n(rt)}, {n(rs)}, {simm if o in ('addi', 'addiu', 'slti') else imm}"
    return f"(código de operación {op} desconocido)"
