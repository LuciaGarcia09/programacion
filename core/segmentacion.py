"""Segmentación (pipeline) MIPS de 5 etapas y paralelismo a nivel de instrucción.

Dos modelos, los mismos que usan los ejercicios:

1. `diagrama()`: pipeline IF-ID-EX-MEM-WB ciclo a ciclo, con o sin forwarding, banco de registros que escribe en la
   1ª mitad del ciclo y lee en la 2ª, ciclos extra por etapa (memoria lenta, multiplicación…), y tratamiento de saltos
   (vaciado/congelación, predicción no tomado, predicción tomado, hueco de retardo).
2. `planificar_latencias()`: el modelo de las tablas de «latencia entre instrucciones» (Hennessy-Patterson): una
   instrucción por ciclo y, si una usa el resultado de otra, tiene que esperar esa latencia.

Además `dependencias()` lista todas las dependencias RAW, WAR y WAW (también entre iteraciones).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re

ETAPAS = ["IF", "ID", "EX", "M", "WB"]


# ======================================================================= lectura del código
@dataclass
class Ins:
    texto: str
    op: str
    dest: str | None
    fuentes: list
    clase: str                 # alu, load, store, branch, jump, fp_add, fp_mul, fp_div, mul, div, nop
    etiqueta: str | None = None
    destino_salto: str | None = None
    lee_en_mem: str | None = None   # registro que un store necesita en MEM (el dato)
    idx: int = 0
    extra_din: dict = field(default_factory=dict)   # ciclos extra solo de esta ejecución (p. ej. un fallo de caché)


_REG = r"\$?(?:[rR]\d+|[fF]\d+|zero|at|v[01]|a[0-3]|t[0-9]|s[0-7]|k[01]|gp|sp|fp|ra|\d+)"


def _norm_reg(t: str) -> str | None:
    t = t.strip().rstrip(",")
    m = re.fullmatch(r"\$?([A-Za-z]*)(\d*)", t)
    if not m:
        return None
    t = t.lstrip("$").lower()
    if t in ("zero", "r0", "0"):
        return None            # el registro 0 nunca crea dependencias
    return t


def _clase(op: str) -> str:
    o = op.lower()
    if o in ("lw", "lb", "lbu", "lh", "lhu", "ld", "l.d", "l.s", "ldc1", "lwc1"):
        return "load"
    if o in ("sw", "sb", "sh", "sd", "s.d", "s.s", "sdc1", "swc1"):
        return "store"
    if o in ("beq", "bne", "bnez", "beqz", "bnz", "bgez", "bgtz", "blez", "bltz", "ble", "blt", "bge", "bgt",
             "bc1t", "bc1f"):
        return "branch"
    if o in ("j", "jal", "jr", "b"):
        return "jump"
    if o in ("add.d", "sub.d", "add.s", "sub.s", "addd", "subd", "sub.f", "add.f"):
        return "fp_add"
    if o in ("mul.d", "mul.s", "multd", "mul.f", "mult.d"):
        return "fp_mul"
    if o in ("div.d", "div.s", "divd", "div.f"):
        return "fp_div"
    if o in ("mul", "mult", "multu"):
        return "mul"
    if o in ("div", "divu"):
        return "div"
    if o == "nop":
        return "nop"
    return "alu"


def leer_codigo(texto: str) -> list[Ins]:
    out = []
    etiq_pend = None
    for linea in texto.strip().split("\n"):
        l = re.sub(r"[#;].*$", "", linea).strip()
        if not l:
            continue
        m = re.match(r"^(\w+)\s*:\s*(.*)$", l)
        if m:
            etiq_pend = m.group(1)
            l = m.group(2).strip()
            if not l:
                continue
        m = re.match(r"^(i\d+)\s*:\s*(.*)$", l)
        partes = l.split(None, 1)
        op = partes[0]
        args = [a.strip() for a in re.split(r"[,\s]+", partes[1].strip())] if len(partes) > 1 else []
        args = [a for a in args if a]
        c = _clase(op)
        dest, fuentes, lee_mem, salto = None, [], None, None
        def regs_en(s):
            return [x for x in (_norm_reg(r) for r in re.findall(_REG, s)) if x]
        if c == "load":
            dest = _norm_reg(args[0])
            mm = re.search(r"\((.+?)\)", " ".join(args[1:]))
            fuentes = [r for r in ([_norm_reg(mm.group(1))] if mm else []) if r]
        elif c == "store":
            mm = re.search(r"\((.+?)\)", " ".join(args[1:]))
            base = [r for r in ([_norm_reg(mm.group(1))] if mm else []) if r]
            dato = _norm_reg(args[0])
            fuentes = base + ([dato] if dato else [])
            lee_mem = dato
        elif c == "branch":
            regs = [a for a in args[:-1]]
            fuentes = [r for r in (_norm_reg(x) for x in regs) if r and not re.fullmatch(r"#?-?\d+", x if False else r)]
            fuentes = [r for r in fuentes if not r.lstrip("-").isdigit()]
            salto = args[-1] if args else None
        elif c == "jump":
            salto = args[-1] if args else None
            if op.lower() == "jr":
                fuentes = [r for r in [_norm_reg(args[0])] if r]
                salto = None
        elif c == "nop":
            pass
        else:
            if op.lower() in ("mult", "multu", "div", "divu") and len(args) == 2:
                dest = "hilo"
                fuentes = [r for r in (_norm_reg(a) for a in args) if r]
            else:
                dest = _norm_reg(args[0]) if args else None
                fuentes = [r for r in (_norm_reg(a) for a in args[1:] if not re.fullmatch(r"#?-?(0x)?[0-9a-fA-F]+", a))
                           if r and not r.isdigit()]
        out.append(Ins(linea.strip(), op.lower(), dest, fuentes, c, etiq_pend, salto, lee_mem, len(out)))
        etiq_pend = None
    return out


# ======================================================================= dependencias
@dataclass
class Dependencia:
    tipo: str
    registro: str
    origen: int
    destino: int
    entre_iteraciones: bool = False


def dependencias(codigo: list[Ins], bucle=True) -> list[Dependencia]:
    out = []
    n = len(codigo)
    # dentro de la misma iteración
    for j in range(n):
        for i in range(j):
            a, b = codigo[i], codigo[j]
            entre = [codigo[k] for k in range(i + 1, j)]
            if a.dest and a.dest in b.fuentes and not any(k.dest == a.dest for k in entre):
                out.append(Dependencia("RAW", a.dest, i, j))
            if b.dest and b.dest in a.fuentes and not any(k.dest == b.dest for k in entre):
                out.append(Dependencia("WAR", b.dest, i, j))
            if a.dest and a.dest == b.dest and not any(k.dest == a.dest for k in entre):
                out.append(Dependencia("WAW", a.dest, i, j))
    if bucle:
        ini = next((k for k, x in enumerate(codigo) if x.etiqueta), 0)
        cuerpo = list(range(ini, n))
        for jj, j in enumerate(cuerpo):
            for i in cuerpo[jj:]:
                a, b = codigo[i], codigo[j]       # a (iteración k) → b (iteración k+1)
                despues = [codigo[k] for k in cuerpo if k > i]
                antes = [codigo[k] for k in cuerpo if k < j]
                bloquea = lambda r: any(x.dest == r for x in despues + antes)  # noqa: E731
                if a.dest and a.dest in b.fuentes and not bloquea(a.dest):
                    out.append(Dependencia("RAW", a.dest, i, j, True))
                if b.dest and b.dest in a.fuentes and i > j and not any(x.dest == b.dest for x in despues + antes):
                    out.append(Dependencia("WAR", b.dest, i, j, True))
                if a.dest and a.dest == b.dest and i >= j and not bloquea(a.dest):
                    out.append(Dependencia("WAW", a.dest, i, j, True))
    return out


# ======================================================================= modelo de latencias (Hennessy)
def planificar_latencias(codigo: list[Ins], latencia, salto_extra=0, hueco_retardo=False):
    """latencia(productor, consumidor) → ciclos de espera si el consumidor usa el resultado del productor.
    Devuelve [(ciclo de emisión, instrucción o 'detención')] para una iteración y el nº de ciclos."""
    filas = []
    emitido = {}
    ciclo = 0
    for k, ins in enumerate(codigo):
        t = ciclo + 1
        for p in range(k):
            prod = codigo[p]
            if prod.dest and prod.dest in ins.fuentes:
                # el último productor de ese registro antes de k
                if any(codigo[q].dest == prod.dest for q in range(p + 1, k)):
                    continue
                t = max(t, emitido[p] + 1 + latencia(prod, ins))
        for c in range(ciclo + 1, t):
            filas.append((c, "detención"))
        emitido[k] = t
        filas.append((t, ins.texto))
        ciclo = t
        if ins.clase in ("branch", "jump") and salto_extra and not hueco_retardo:
            for c in range(ciclo + 1, ciclo + 1 + salto_extra):
                filas.append((c, "detención (salto)"))
            ciclo += salto_extra
    return filas, ciclo


# ======================================================================= pipeline ciclo a ciclo
@dataclass
class Config:
    forwarding: bool = False
    banco_partido: bool = True          # escribe en la 1ª mitad y lee en la 2ª (ID y WB en el mismo ciclo)
    salto_resuelto_en: str = "EX"       # "ID" o "EX"
    salto: str = "vaciado"              # vaciado | no_tomado | tomado | retardado
    extra: dict = field(default_factory=dict)   # {(clase u op, etapa): ciclos extra}
    extra_if: int = 0                   # ciclos extra de cada fetch (memoria lenta)
    estructural_mem: bool = False       # IF y MEM comparten memoria (no se solapan)


@dataclass
class FilaDiagrama:
    texto: str
    celdas: dict      # ciclo → texto
    etapas: dict      # etapa → (inicio, fin)
    detenciones: list


def _extra(cfg: Config, ins: Ins, etapa: str) -> int:
    e = cfg.extra.get((ins.op, etapa))
    if e is None:
        e = cfg.extra.get((ins.clase, etapa), 0)
    if etapa == "IF":
        e += cfg.extra_if
    return e + ins.extra_din.get(etapa, 0)


def _produce_en(ins: Ins, cfg: Config) -> str:
    return "M" if ins.clase == "load" else "EX"


def diagrama(flujo: list[Ins], cfg: Config, tomados: list[bool] | None = None) -> tuple[list[FilaDiagrama], int]:
    """flujo: instrucciones en orden de ejecución (dinámico). tomados[k]: si el salto k-ésimo del flujo se toma."""
    n = len(flujo)
    ini = [dict() for _ in range(n)]
    fin = [dict() for _ in range(n)]
    det = [[] for _ in range(n)]
    tomados = list(tomados or [])
    salto_k = 0
    min_if = 1
    resultado_listo = {}         # registro → (ciclo a partir del cual se puede usar en EX, en ID)
    escritor = {}                # registro → índice de la última instrucción que lo escribe
    for i, ins in enumerate(flujo):
        # ---------------- IF
        t = max(min_if, (ini[i - 1]["IF"] + 1) if i else 1)
        if i:
            # IF no puede empezar hasta que la anterior deja libre el IF (pasa a ID)
            t = max(t, ini[i - 1]["ID"])
        ini[i]["IF"] = t
        fin[i]["IF"] = t + _extra(cfg, ins, "IF")
        # ---------------- ID
        t = fin[i]["IF"] + 1
        if i:
            t = max(t, ini[i - 1]["EX"])     # la anterior tiene que haber salido de ID
        ini[i]["ID"] = t
        # operandos
        necesita_ex = t + 1 + _extra(cfg, ins, "ID")
        lee_id = ins.clase == "branch" and cfg.salto_resuelto_en == "ID"
        for r in ins.fuentes:
            if r not in escritor:
                continue
            p = escritor[r]
            pr = flujo[p]
            if cfg.forwarding:
                listo = fin[p][_produce_en(pr, cfg)] + 1          # puede usarse en el ciclo siguiente
                if r == ins.lee_en_mem and ins.clase == "store":
                    # el dato del store se necesita en MEM: puede llegar justo a tiempo
                    necesita_mem_min = listo
                    necesita_ex = max(necesita_ex, necesita_mem_min - 1 - _extra(cfg, ins, "EX"))
                    continue
                if lee_id:
                    necesita_ex = max(necesita_ex, listo + 1)
                else:
                    necesita_ex = max(necesita_ex, listo)
            else:
                wb = fin[p]["WB"]
                lectura = wb if cfg.banco_partido else wb + 1   # ciclo en que ID puede leer
                necesita_ex = max(necesita_ex, lectura + 1)
        if i:
            # la anterior tiene que haber dejado libre la etapa EX (si espera para entrar en MEM, sigue ocupándola)
            necesita_ex = max(necesita_ex, fin[i - 1]["EX"] + 1, ini[i - 1]["M"])
        fin[i]["ID"] = necesita_ex - 1
        # ---------------- EX
        ini[i]["EX"] = necesita_ex
        fin[i]["EX"] = necesita_ex + _extra(cfg, ins, "EX")
        # ---------------- MEM
        t = fin[i]["EX"] + 1
        if i:
            t = max(t, fin[i - 1]["M"] + 1, ini[i - 1]["WB"])
        ini[i]["M"] = t
        fin[i]["M"] = t + _extra(cfg, ins, "M")
        # ---------------- WB
        t = fin[i]["M"] + 1
        if i:
            t = max(t, fin[i - 1]["WB"] + 1)
        ini[i]["WB"] = t
        fin[i]["WB"] = t + _extra(cfg, ins, "WB")
        if ins.dest:
            escritor[ins.dest] = i
        # ---------------- efecto de los saltos sobre el siguiente fetch
        if ins.clase in ("branch", "jump"):
            tomado = True if ins.clase == "jump" else (tomados[salto_k] if salto_k < len(tomados) else True)
            if ins.clase == "branch":
                salto_k += 1
            res = fin[i][cfg.salto_resuelto_en if ins.clase == "branch" else "ID"]
            pol = cfg.salto
            if pol == "vaciado":
                min_if = res + 1
            elif pol == "no_tomado":
                if tomado:
                    min_if = res + 1
            elif pol == "tomado":
                if not tomado:
                    min_if = res + 1
                else:
                    min_if = fin[i]["ID"] + 1 if cfg.salto_resuelto_en == "EX" else ini[i]["IF"] + 1
            elif pol == "retardado":
                pass       # la siguiente (hueco) entra normal; el destino tras ella
        elif i and flujo[i - 1].clase in ("branch",) and cfg.salto == "retardado":
            res = fin[i - 1][cfg.salto_resuelto_en]
            min_if = max(min_if, res + 1)
    filas = []
    for i, ins in enumerate(flujo):
        celdas = {}
        dets = []
        for e in ETAPAS:
            trabajo = _extra(cfg, ins, e)
            for c in range(ini[i][e], fin[i][e] + 1):
                if c <= ini[i][e] + trabajo:
                    celdas[c] = e
                else:
                    celdas[c] = "—"          # espera dentro de la etapa (detención)
                    dets.append(c)
        c0, c1 = ini[i]["IF"], fin[i]["WB"]
        for c in range(c0, c1 + 1):
            if c not in celdas:
                celdas[c] = "—"
                dets.append(c)
        filas.append(FilaDiagrama(ins.texto, celdas, {e: (ini[i][e], fin[i][e]) for e in ETAPAS}, sorted(dets)))
    total = fin[-1]["WB"] if n else 0
    return filas, total


def flujo_bucle(codigo: list[Ins], iteraciones: int) -> tuple[list[Ins], list[bool], list[int]]:
    """Construye el flujo dinámico: prólogo (antes de la etiqueta) + cuerpo × iteraciones.
    Devuelve (flujo, tomados, índice de inicio de cada iteración)."""
    ini = next((k for k, x in enumerate(codigo) if x.etiqueta), 0)
    prologo, cuerpo = codigo[:ini], codigo[ini:]
    flujo, tomados, inicios = list(prologo), [], []
    for it in range(iteraciones):
        inicios.append(len(flujo))
        for ins in cuerpo:
            flujo.append(ins)
            if ins.clase == "branch":
                tomados.append(it < iteraciones - 1)
    return flujo, tomados, inicios


def ciclos_por_iteracion(codigo: list[Ins], cfg: Config, iteraciones=4):
    flujo, tomados, inicios = flujo_bucle(codigo, iteraciones)
    filas, total = diagrama(flujo, cfg, tomados)
    starts = [filas[k].etapas["IF"][0] for k in inicios]
    difs = [b - a for a, b in zip(starts, starts[1:])]
    return difs, total, filas


def formula_n(codigo: list[Ins], cfg: Config):
    """Ciclos para N iteraciones = a·N + b (se ajusta con N = 2 y N = 3)."""
    t2 = diagrama(*_fb(codigo, cfg, 2))[1]
    t3 = diagrama(*_fb(codigo, cfg, 3))[1]
    a = t3 - t2
    b = t2 - 2 * a
    return a, b


def _fb(codigo, cfg, n):
    f, t, _ = flujo_bucle(codigo, n)
    return f, cfg, t
