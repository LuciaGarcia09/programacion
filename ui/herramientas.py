"""Herramientas interactivas de Fundamentos de Computadores (y los patios de juego de C y Python)."""
from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from core import cache as CA, mips, representacion as RP, segmentacion as SG
from ui.estilo import caja

NAV = {}            # nombre de página → st.Page (lo rellena app.py)


def boton_herramienta(nombre: str, clave: str):
    if nombre not in HERRAMIENTAS:
        return
    ic = HERRAMIENTAS[nombre][1]
    if st.button(f"{ic} Abrir la herramienta «{nombre}»", key=clave):
        st.session_state["_herr"] = nombre
        if "herramientas" in NAV:
            st.switch_page(NAV["herramientas"])


def _pasos(lista, titulo="Paso a paso"):
    with caja("pasos", titulo):
        st.markdown("\n".join(f"{k}. {p}" for k, p in enumerate(lista, 1)))


# =========================================================================== bases y potencias
def herr_bases():
    st.caption("Convierte entre decimal, binario, octal y hexadecimal, y calcula cuántos bits hacen falta.")
    c1, c2 = st.columns([2, 1])
    with c1:
        txt = st.text_input("Número (decimal, 0b…, 0o…, 0x…)", "0xEAAB591", key="hb_num")
    with c2:
        bits = st.number_input("Bits a mostrar (0 = los justos)", 0, 64, 0, key="hb_bits")
    try:
        n = int(txt.strip().replace("_", ""), 0)
    except ValueError:
        st.error("No entiendo ese número: escribe 123, 0b101, 0o17 o 0x1F.")
        return
    b = format(abs(n), "b") if not bits else format(abs(n), f"0{bits}b")
    st.markdown(f"""
| Base | Valor |
|---|---|
| Decimal | **{n:,}** |
| Binario | `{RP.agrupar(b)}` ({len(b)} bits) |
| Octal | `{oct(n)}` |
| Hexadecimal | `{hex(n).upper().replace('X', 'x')}` |""".replace(",", " "))
    if txt.lower().startswith("0x"):
        trozos = " · ".join(f"{c} = {format(int(c, 16), '04b')}" for c in txt[2:].upper())
        st.info(f"Cada cifra hexadecimal son 4 bits: {trozos}")
    st.divider()
    m = st.number_input("¿Cuántas cosas quieres numerar? (registros, instrucciones…)", 1, 10**12, 60, key="hb_m")
    k = (m - 1).bit_length() if m > 1 else 0
    st.success(f"Hacen falta **⌈log₂ {m}⌉ = {k} bits** (2^{k - 1 if k else 0} = {2 ** (k - 1) if k else 1} < {m} ≤ 2^{k} = {2 ** k}).")
    p = st.slider("Potencia de 2", 0, 64, 20, key="hb_p")
    nombres = [(60, "E"), (50, "P"), (40, "T"), (30, "G"), (20, "M"), (10, "K"), (0, "")]
    for e, nom in nombres:
        if p >= e:
            st.markdown(f"$2^{{{p}}} = 2^{{{p - e}}}\\cdot2^{{{e}}} =$ **{2 ** (p - e)} {nom}** = {2 ** p:,}".replace(",", " "))
            break


# =========================================================================== enteros
def herr_enteros():
    st.caption("Signo-magnitud, complemento a 1, complemento a 2, binario puro y exceso, con el paso a paso.")
    modo = st.radio("Quiero…", ["Representar un número", "Leer un patrón de bits", "Bits para un rango"],
                    horizontal=True, key="he_modo")
    sistemas = {"Complemento a 2": "ca2", "Complemento a 1": "ca1", "Signo-magnitud": "sm", "Binario puro": "binario"}
    if modo == "Representar un número":
        c1, c2, c3 = st.columns(3)
        v = c1.number_input("Número", value=-14, step=1, key="he_v")
        n = c2.number_input("Bits", 1, 64, 5, key="he_n")
        sis = c3.selectbox("Sistema", list(sistemas) + ["Exceso 2^(n−1)"], key="he_s")
        s = sistemas.get(sis, "exceso")
        r = RP.codificar_entero(int(v), s, int(n))
        if r.patron:
            st.success(f"**{r.patron}**  ·  rango con {n} bits: [{r.rango[0]}, {r.rango[1]}]")
        else:
            st.error(r.pasos[0])
        _pasos(r.pasos)
        filas = []
        for nom, ss in sistemas.items():
            e = RP.codificar_entero(int(v), ss, int(n))
            filas.append({"Sistema": nom, "Patrón": e.patron or "no cabe", "Rango": f"[{e.rango[0]}, {e.rango[1]}]"})
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
    elif modo == "Leer un patrón de bits":
        c1, c2 = st.columns(2)
        p = c1.text_input("Patrón", "110111", key="he_p").replace(" ", "")
        sis = c2.selectbox("Sistema", list(sistemas), key="he_s2")
        if not re.fullmatch(r"[01]+", p):
            st.error("Escribe solo ceros y unos.")
            return
        r = RP.decodificar_entero(p, sistemas[sis])
        st.success(f"**{p}** en {sis} vale **{r.valor}**")
        _pasos(r.pasos)
    else:
        c1, c2, c3 = st.columns(3)
        lo = c1.number_input("Mínimo", value=-8191, step=1, key="he_lo")
        hi = c2.number_input("Máximo", value=8191, step=1, key="he_hi")
        sis = c3.selectbox("Sistema", list(sistemas), key="he_s3")
        n, expl = RP.bits_necesarios(sistemas[sis], int(lo), int(hi))
        st.success(f"Hacen falta **{n} bits**")
        st.markdown(expl)


# =========================================================================== IEEE 754
FORMATOS = {"Simple (32 bits: 1 + 8 + 23)": (8, 23), "Media (16 bits: 1 + 5 + 10)": (5, 10),
            "Doble (64 bits: 1 + 11 + 52)": (11, 52)}


def _mostrar_float(f):
    eb, mb = f.e_bits, f.m_bits
    p = f.patron
    st.markdown(f"""
| Signo | Exponente ({eb} bits) | Mantisa ({mb} bits) |
|---|---|---|
| `{p[0]}` | `{p[1:1 + eb]}` = {f.exp_campo} | `{RP.agrupar(p[1 + eb:])}` |""")
    val = "NaN" if f.tipo == "NaN" else ("−∞" if f.tipo == "infinito" and f.signo else "+∞" if f.tipo == "infinito" else f"{f.valor:.10g}")
    st.success(f"**{f.hexa}** · tipo: **{f.tipo}** · valor: **{val}**")


def herr_ieee():
    st.caption("Codifica y decodifica en IEEE 754 (32, 16 y 64 bits) y opera explicando cada paso.")
    fmt = st.selectbox("Formato", list(FORMATOS), key="hi_fmt")
    eb, mb = FORMATOS[fmt]
    t1, t2, t3, t4 = st.tabs(["Número → bits", "Bits / hex → número", "Suma y producto", "Extremos"])
    with t1:
        x = st.text_input("Número (admite 0.1, -3.5, 1e-5, 1/3, inf, nan)", "14", key="hi_x")
        try:
            f = RP.codificar_float(x, eb, mb)
        except Exception as exc:  # noqa: BLE001
            st.error(f"No entiendo «{x}»: {exc}")
            return
        _mostrar_float(f)
        if f.exacto is not None:
            try:
                from fractions import Fraction
                err = abs(Fraction(f.exacto) - Fraction(x.strip()))
                st.caption(f"Valor guardado exacto: {float(f.exacto)!r} · error de representación: {float(err):.3g}")
            except (ValueError, ZeroDivisionError):
                pass
        _pasos(f.pasos)
    with t2:
        h = st.text_input("Patrón en hexadecimal (0x…) o binario", "0xC7B00000", key="hi_h")
        try:
            f = RP.decodificar_float(h, eb, mb)
        except Exception as exc:  # noqa: BLE001
            st.error(f"No entiendo «{h}»: {exc}")
        else:
            _mostrar_float(f)
            _pasos(f.pasos)
    with t3:
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a", value=14.0, key="hi_a", format="%g")
        b = c2.number_input("b", value=3.5, key="hi_b", format="%g")
        op = c3.radio("Operación", ["a + b", "a · b"], key="hi_op")
        fr, pasos = (RP.suma_float if op == "a + b" else RP.producto_float)(a, b, eb, mb)
        _mostrar_float(fr)
        _pasos(pasos)
    with t4:
        ex = RP.extremos(eb, mb)
        filas = [{"Qué": k, "Valor": (f"{float(v):.6g}" if not isinstance(v, int) else str(v))} for k, v in ex.items()]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
        st.caption("Positivos; los negativos son los mismos con el signo a 1.")


# =========================================================================== simulador MIPS
EJEMPLO_MIPS = """.data
v:      .word 3, 7, 1, 9, 5
.text
main:   la   $t0, v
        li   $t1, 5          # n
        li   $t2, 0          # i
        li   $t3, 0          # suma
bucle:  bge  $t2, $t1, fin
        sll  $t4, $t2, 2     # i·4
        add  $t4, $t0, $t4
        lw   $t5, 0($t4)
        add  $t3, $t3, $t5
        addi $t2, $t2, 1
        b    bucle
fin:    move $a0, $t3
        li   $v0, 1          # print_int
        syscall
        li   $v0, 10         # exit
        syscall
"""


def herr_mips():
    st.caption("Ensambla y ejecuta MIPS32 (como MARS): pseudoinstrucciones, syscall, coma flotante, pila y E/S. "
               "Te dice qué registros cambian en cada paso.")
    if "hm_cod" not in st.session_state:
        st.session_state.hm_cod = st.session_state.pop("_mips_precarga", EJEMPLO_MIPS)
    elif "_mips_precarga" in st.session_state:
        st.session_state.hm_cod = st.session_state.pop("_mips_precarga")
    cod = st.text_area("Programa", key="hm_cod", height=360)
    c1, c2, c3 = st.columns([2, 1, 1])
    ent = c1.text_area("Entrada por teclado (una línea por dato)", "", key="hm_ent", height=68)
    pasos = c2.number_input("Pasos a registrar", 0, 2000, 60, key="hm_pasos")
    disp = c3.selectbox("Periférico simulado", ["ninguno", "tensiometro", "microondas", "sensor_piezas", "temperatura",
                                                 "barras", "semaforo", "horno", "agua"], key="hm_disp")
    if st.button("▶ Ensamblar y ejecutar", type="primary", key="hm_run"):
        from ui.codigo import ejecutar_mips
        res, err = ejecutar_mips(cod, ent, None if disp == "ninguno" else disp, historial=int(pasos))
        if err:
            st.error(err)
            return
        st.session_state.hm_res = res
    res = st.session_state.get("hm_res")
    if not res:
        return
    (st.success if res.termino else st.warning)(f"🛑 {res.motivo}")
    st.markdown("**Consola**")
    st.code(res.salida or "(no imprime nada)", language="text")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Instrucciones", res.pasos)
    m2.metric("Accesos (fetch)", res.accesos_instr)
    m3.metric("Accesos a datos", res.accesos_datos)
    m4.metric("Total accesos", res.accesos_instr + res.accesos_datos)
    t1, t2, t3, t4 = st.tabs(["Registros", "Memoria (.data)", "Paso a paso", "Etiquetas"])
    with t1:
        filas = [{"Registro": f"${mips.NOMBRES[k]}", "Nº": k, "Decimal": v, "Hex": f"0x{v & 0xFFFFFFFF:08X}"}
                 for k, v in enumerate(res.regs)]
        filas += [{"Registro": "HI", "Nº": "", "Decimal": res.hi, "Hex": f"0x{res.hi & 0xFFFFFFFF:08X}"},
                  {"Registro": "LO", "Nº": "", "Decimal": res.lo, "Hex": f"0x{res.lo & 0xFFFFFFFF:08X}"}]
        solo = st.toggle("Solo los distintos de 0", True, key="hm_solo")
        df = pd.DataFrame([f for f in filas if not solo or f["Decimal"]])
        st.dataframe(df, hide_index=True, width="stretch")
        fs = [(k, res.fregs[k]) for k in range(32) if res.fregs[k]]
        if fs:
            import struct
            st.caption("Coma flotante: " + " · ".join(
                f"$f{k} = {struct.unpack('<f', struct.pack('<I', v & 0xFFFFFFFF))[0]:g}" for k, v in fs))
    with t2:
        dirs = sorted(d for d in res.memoria if 0x10010000 <= d < 0x10020000)
        if not dirs:
            st.info("No hay datos en el segmento .data.")
        else:
            ini, fin = dirs[0] & ~3, min(dirs[-1], dirs[0] + 4 * 64)
            filas = []
            etq = {v: k for k, v in res.etiquetas.items()}
            for d in range(ini, fin + 1, 4):
                w = mips.palabras(res, d, 1)[0]
                bs = [res.memoria.get(d + j, 0) for j in range(4)]
                filas.append({"Dirección": f"0x{d:08X}", "Etiqueta": etq.get(d, ""), "Palabra (dec)": w,
                              "Hex": f"0x{w & 0xFFFFFFFF:08X}",
                              "Bytes (d, d+1, d+2, d+3)": " ".join(f"{b:02X}" for b in bs),
                              "Texto": "".join(chr(b) if 32 <= b < 127 else "·" for b in bs)})
            st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
            st.caption("Little endian (como MARS en un PC): el byte de la dirección más baja es el menos significativo.")
    with t3:
        if not res.historial:
            st.info("Sube «Pasos a registrar» para ver la traza.")
        else:
            filas = [{"Paso": p, "Línea": l, "Instrucción": t,
                      "Cambios": ", ".join(f"${k} = {v}" for k, v in c.items())} for p, l, t, c in res.historial]
            st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch", height=420)
    with t4:
        st.dataframe(pd.DataFrame([{"Etiqueta": k, "Dirección": f"0x{v:08X}"} for k, v in res.etiquetas.items()]),
                     hide_index=True, width="stretch")


# =========================================================================== codificador
def herr_codificador():
    st.caption("Codifica una instrucción MIPS real en binario (tipos R, I y J) o decodifica una palabra.")
    t1, t2 = st.tabs(["Instrucción → binario", "Hexadecimal → instrucción"])
    with t1:
        linea = st.text_input("Instrucción", "addi $21, $22, -50", key="hc_l")
        try:
            c = mips.codificar(linea)
        except mips.ErrorMIPS as exc:
            st.error(str(exc))
        else:
            st.markdown("| " + " | ".join(n for n, _, _ in c.campos) + " |\n|" + "---|" * len(c.campos) + "\n| " +
                        " | ".join(str(v) for _, v, _ in c.campos) + " |\n| " +
                        " | ".join(f"`{b}`" for _, _, b in c.campos) + " |")
            st.success(f"Tipo **{c.tipo}** · `{RP.agrupar(c.binario)}` = **{c.hexa}**")
            st.markdown(c.explicacion)
    with t2:
        h = st.text_input("Palabra (hex)", "0x012A4020", key="hc_h")
        try:
            st.success(f"**{mips.decodificar(int(h, 16))}**")
        except Exception as exc:  # noqa: BLE001
            st.error(f"No he podido decodificarla: {exc}")


# =========================================================================== caché
def _leer_traza(texto):
    out = []
    for t in re.split(r"[,\n;]+", texto):
        t = t.strip()
        if not t:
            continue
        m = re.fullmatch(r"([RrWwLlEe])?\s*(0x[0-9a-fA-F]+|\d+)", t)
        if not m:
            raise ValueError(f"no entiendo «{t}» (escribe R 0x1000 o W 64)")
        tipo = "W" if (m.group(1) or "R").upper() in ("W", "E") else "R"
        out.append((tipo, int(m.group(2), 0)))
    return out


def herr_cache():
    st.caption("Campos de la dirección, simulación acceso a acceso (directa, asociativa o por conjuntos; LRU, FIFO, LFU) "
               "y tiempo medio de acceso.")
    t1, t2, t3 = st.tabs(["Campos de la dirección", "Simular accesos", "Tiempo medio"])
    with t1:
        c1, c2, c3, c4 = st.columns(4)
        bits = c1.number_input("Bits de dirección", 8, 64, 32, key="hca_b")
        tam = c2.text_input("Tamaño caché", "64 KB", key="hca_t")
        lin = c3.text_input("Tamaño línea", "64 B", key="hca_l")
        vias = c4.selectbox("Correspondencia", ["directa", "2 vías", "4 vías", "8 vías", "16 vías", "totalmente asociativa"],
                            index=2, key="hca_v")
        try:
            T, Lb = CA.leer_tam(tam), CA.leer_tam(lin)
            v = None if vias.startswith("total") else (1 if vias == "directa" else int(vias.split()[0]))
            c = CA.campos(int(bits), T, Lb, v)
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))
            return
        st.markdown(f"| etiqueta | {'línea' if v == 1 else 'conjunto' if c.b_indice else '—'} | byte |\n|---|---|---|\n"
                    f"| **{c.b_etiqueta}** bits | **{c.b_indice}** bits | **{c.b_byte}** bits |")
        _pasos(c.pasos)
        d = st.text_input("Partir una dirección (hex o decimal)", "0x03C300F8", key="hca_d")
        try:
            pr = CA.partir_direccion(int(d, 0), c)
            st.success(f"`{pr['etiqueta']}` | `{pr['indice'] or '—'}` | `{pr['byte']}` → etiqueta {pr['etiqueta_val']}, "
                       f"{'línea' if v == 1 else 'conjunto'} {pr['indice_val']}, byte {pr['byte_val']} (bloque {pr['bloque']})")
        except ValueError:
            st.error("Dirección no válida.")
    with t2:
        c1, c2, c3, c4 = st.columns(4)
        tam = c1.text_input("Tamaño caché", "256 B", key="hcs_t")
        lin = c2.text_input("Tamaño línea", "16 B", key="hcs_l")
        vias = c3.selectbox("Correspondencia", ["directa", "2 vías", "4 vías", "totalmente asociativa"], key="hcs_v")
        reemp = c4.selectbox("Sustitución", ["LRU", "FIFO", "LFU"], key="hcs_r")
        esc = st.radio("Escritura", ["post-escritura (write-back)", "inmediata (write-through)"], horizontal=True, key="hcs_e")
        origen = st.radio("Accesos", ["Escribirlos", "Patrón de un vector", "De un programa MIPS"], horizontal=True,
                          key="hcs_o")
        try:
            if origen == "Escribirlos":
                traza = _leer_traza(st.text_area("Accesos (R/W y dirección; separados por comas o líneas)",
                                                 "R 0, R 4, R 16, R 0, W 64, R 0, R 128, R 4", key="hcs_tr"))
            elif origen == "Patrón de un vector":
                a1, a2, a3, a4 = st.columns(4)
                base = int(a1.text_input("Dirección inicial", "0x1000", key="hcs_vb"), 0)
                n = a2.number_input("Elementos", 1, 100000, 64, key="hcs_vn")
                tam_e = a3.number_input("Bytes por elemento", 1, 64, 4, key="hcs_ve")
                paso = a4.number_input("Paso (en elementos)", 1, 4096, 1, key="hcs_vp")
                traza = [("R", base + k * paso * tam_e) for k in range(int(n))]
            else:
                cod = st.text_area("Programa MIPS (se usan todos sus accesos: instrucciones y datos)", EJEMPLO_MIPS,
                                   height=200, key="hcs_m")
                solo_datos = st.toggle("Solo accesos a datos", False, key="hcs_sd")
                res = mips.ejecutar(cod, max_pasos=200000)
                traza = [(t if t in "RW" else "R", d) for t, d in res.traza if not (solo_datos and t == "I")]
                st.caption(f"{len(traza)} accesos ({res.pasos} instrucciones ejecutadas).")
            T, Lb = CA.leer_tam(tam), CA.leer_tam(lin)
            v = None if vias.startswith("total") else (1 if vias == "directa" else int(vias.split()[0]))
            r = CA.simular(traza, T, Lb, v, reemp, "post" if esc.startswith("post") else "inmediata")
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))
            return
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Accesos", r.total)
        m2.metric("Aciertos", r.aciertos)
        m3.metric("Fallos", r.fallos)
        m4.metric("Tasa de aciertos", f"{r.tasa_aciertos * 100:.2f} %")
        st.caption(f"Escrituras a memoria principal: {r.escrituras_mp} · expulsiones: {r.expulsiones}")
        filas = [{"#": k + 1, "Tipo": a.tipo, "Dirección": f"0x{a.dir:X}", "Bloque": a.bloque, "Conjunto/línea": a.conjunto,
                  "Resultado": "✅ acierto" if a.acierto else "❌ fallo",
                  "Expulsa": "" if a.expulsado is None else f"bloque {a.expulsado}" + (" (sucio → MP)" if a.sucio_expulsado else "")}
                 for k, a in enumerate(r.accesos[:400])]
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch", height=380)
        if len(r.accesos) > 400:
            st.caption(f"(se muestran los 400 primeros de {len(r.accesos)})")
    with t3:
        c1, c2, c3 = st.columns(3)
        ta = c1.number_input("Ta (acceso a caché)", 0.0, value=4.0, key="hct_a")
        tf = c2.number_input("Tf (tratar un fallo)", 0.0, value=120.0, key="hct_f")
        modo = c3.radio("Calcular", ["Tm a partir de h", "h a partir de Tm"], key="hct_m")
        if modo == "Tm a partir de h":
            h = st.slider("h (tasa de aciertos, %)", 0.0, 100.0, 95.0, 0.1, key="hct_h") / 100
            tm = CA.tiempo_medio(ta, tf, h)
            st.success(f"$T_m = T_a + (1-h)\\,T_f = {ta:g} + {1 - h:.4g}\\cdot{tf:g} =$ **{tm:.4g}**")
        else:
            tm = st.number_input("Tm deseado", 0.0, value=20.0, key="hct_tm")
            h = CA.tasa_necesaria(tm, ta, tf)
            st.success(f"$1-h = \\dfrac{{T_m - T_a}}{{T_f}} = \\dfrac{{{tm:g} - {ta:g}}}{{{tf:g}}} = {1 - h:.4g}$ → **h = {h * 100:.3f} %**")


# =========================================================================== memoria virtual
def herr_virtual():
    st.caption("Formato de la dirección virtual y traducción con una tabla de páginas.")
    c1, c2, c3 = st.columns(3)
    bits = c1.number_input("Bits de la dirección virtual", 8, 64, 32, key="hv_b")
    pag = c2.text_input("Tamaño de página", "4 KB", key="hv_p")
    fis = c3.text_input("Memoria física (opcional)", "1 GB", key="hv_f")
    try:
        P = CA.leer_tam(pag)
        F = CA.leer_tam(fis) if fis.strip() else None
        fv = CA.formato_virtual(int(bits), P, F)
    except Exception as exc:  # noqa: BLE001
        st.error(str(exc))
        return
    st.markdown(f"| nº de página | desplazamiento |\n|---|---|\n| **{fv.bits_pagina}** bits | **{fv.bits_desp}** bits |")
    _pasos(fv.pasos)
    st.divider()
    st.markdown("**Traducir una dirección**")
    tabla_txt = st.text_area("Tabla de páginas (página: marco; deja el marco vacío o «-» si no está en memoria)",
                             "0: 20\n1: 6\n2: 4\n3: 8\n4: 1\n5: 3\n6: 5\n7: 7", key="hv_t", height=150)
    d = st.text_input("Dirección virtual", "0x000023F0", key="hv_d")
    tabla = {}
    for l in tabla_txt.splitlines():
        if ":" in l:
            a, b = l.split(":", 1)
            b = b.strip()
            tabla[int(a.strip(), 0)] = None if b in ("", "-") else int(b, 0)
    try:
        r, pasos = CA.traducir(int(d, 0), P, tabla, int(bits))
    except Exception as exc:  # noqa: BLE001
        st.error(str(exc))
        return
    (st.success if r is not None else st.error)(pasos[-1])
    _pasos(pasos)


# =========================================================================== segmentación
EJEMPLO_PIPE = """bucle: lw   $f0, 0($r1)
       lw   $f2, 0($r2)
       mul.f $f4, $f0, $f2
       add.d $f6, $f6, $f4
       addi $r1, $r1, 4
       addi $r2, $r2, 4
       sub  $r3, $r3, 1
       bnez $r3, bucle"""


def herr_pipeline():
    st.caption("Cronograma de un MIPS de 5 etapas (IF ID EX M WB) con o sin forwarding, ciclos extra y saltos; "
               "dependencias RAW/WAR/WAW y ciclos para N iteraciones.")
    cod = st.text_area("Código (con la etiqueta del bucle)", EJEMPLO_PIPE, height=200, key="hp_c")
    c1, c2, c3, c4 = st.columns(4)
    fw = c1.toggle("Forwarding", False, key="hp_fw")
    banco = c2.toggle("Escribir y leer el banco en el mismo ciclo", True, key="hp_bp")
    salto = c3.selectbox("Saltos", ["vaciado", "no_tomado", "tomado", "retardado"],
                         format_func={"vaciado": "vaciar / congelar", "no_tomado": "predecir no tomado",
                                      "tomado": "predecir tomado", "retardado": "salto retardado"}.get, key="hp_s")
    res_en = c4.selectbox("Salto resuelto en", ["EX", "ID"], key="hp_r")
    c1, c2, c3, c4, c5 = st.columns(5)
    xl = c1.number_input("Ciclos extra de lw en M", 0, 200, 0, key="hp_xl")
    xs = c2.number_input("… de sw en M", 0, 200, 0, key="hp_xs")
    xb = c3.number_input("… del salto en EX", 0, 10, 0, key="hp_xb")
    xf = c4.number_input("… de cada IF", 0, 200, 0, key="hp_xf")
    it = c5.number_input("Iteraciones a dibujar", 1, 4, 1, key="hp_it")
    xmul = st.number_input("Ciclos extra de multiplicaciones (mul, mult, mul.d…) en EX", 0, 20, 0, key="hp_xm")
    try:
        codigo = SG.leer_codigo(cod)
    except Exception as exc:  # noqa: BLE001
        st.error(f"No he podido leer el código: {exc}")
        return
    extra = {("load", "M"): xl, ("store", "M"): xs, ("branch", "EX"): xb, ("mul", "EX"): xmul, ("fp_mul", "EX"): xmul}
    cfg = SG.Config(forwarding=fw, banco_partido=banco, salto=salto, salto_resuelto_en=res_en,
                    extra={k: v for k, v in extra.items() if v}, extra_if=xf)
    flujo, tomados, _ = SG.flujo_bucle(codigo, int(it))
    if it == 1:
        tomados = [True] * len(tomados)
    filas, total = SG.diagrama(flujo, cfg, tomados)
    a, b = SG.formula_n(codigo, cfg)
    m1, m2 = st.columns(2)
    m1.metric("Ciclos del cronograma", total)
    m2.metric("Ciclos para N iteraciones", f"{a}·N + {b}")
    tabla = {}
    for k, f in enumerate(filas):
        tabla[f"I{(k % len(codigo)) + 1} {f.texto.split(':')[-1].strip()}" + ("" if it == 1 else f" ({k // len(codigo) + 1})")] = \
            {c: f.celdas.get(c, "") for c in range(1, total + 1)}
    df = pd.DataFrame(tabla).T
    colores = {"IF": "#ffd6e7", "ID": "#e9dcff", "EX": "#d7f5ef", "M": "#fff1c9", "WB": "#ffe3cc", "—": "#f3f3f3"}
    st.dataframe(df.style.map(lambda v: f"background-color: {colores.get(v, 'white')}; text-align: center"),
                 width="stretch", height=min(60 + 36 * len(df), 620))
    st.caption("«—» = detención (esperando un dato o a que quede libre la etapa siguiente).")
    with st.expander("🔗 Dependencias de datos"):
        ds = SG.dependencias(codigo)
        st.dataframe(pd.DataFrame([{"Tipo": d.tipo, "Registro": d.registro, "De": f"I{d.origen + 1}",
                                    "A": f"I{d.destino + 1}", "Entre iteraciones": "sí" if d.entre_iteraciones else ""}
                                   for d in ds]), hide_index=True, width="stretch")


# =========================================================================== rendimiento
def herr_rendimiento():
    st.caption("CPI, MIPS, tiempo de CPU, speedup y ley de Amdahl.")
    t1, t2, t3 = st.tabs(["CPI, MIPS y tiempo", "Amdahl", "Comparar dos máquinas"])
    with t1:
        c1, c2, c3 = st.columns(3)
        f = c1.number_input("Frecuencia (MHz)", 1.0, value=500.0, key="hr_f")
        cpi = c2.number_input("CPI", 0.01, value=25.0, key="hr_cpi")
        n = c3.number_input("Instrucciones del programa", 1, value=5000, key="hr_n")
        mips_ = f / cpi
        t = n * cpi / (f * 1e6)
        st.success(f"MIPS = f / CPI = {f:g} / {cpi:g} = **{mips_:.4g}** millones de instrucciones/s · "
                   f"T = N·CPI/f = **{t * 1e6:.4g} µs**")
    with t2:
        c1, c2 = st.columns(2)
        fr = c1.slider("Fracción que se acelera (%)", 0.0, 100.0, 90.0, 0.5, key="hr_fr") / 100
        s = c2.number_input("Factor de aceleración de esa parte", 1.0, value=10.0, key="hr_s")
        S = 1 / ((1 - fr) + fr / s)
        st.success(f"$S = \\dfrac{{1}}{{(1-f) + f/s}} = \\dfrac{{1}}{{{1 - fr:.4g} + {fr:.4g}/{s:g}}} =$ **{S:.4f}**  ·  "
                   f"límite (s → ∞): {('∞' if fr == 1 else f'{1 / (1 - fr):.4g}')}")
    with t3:
        c1, c2 = st.columns(2)
        with c1:
            fa = st.number_input("A: frecuencia (MHz)", 1.0, value=1000.0, key="hr_fa")
            ca = st.number_input("A: CPI", 0.01, value=8.0, key="hr_ca")
            na = st.number_input("A: instrucciones", 1, value=5000, key="hr_na")
        with c2:
            fb = st.number_input("B: frecuencia (MHz)", 1.0, value=2500.0, key="hr_fb")
            cb = st.number_input("B: CPI", 0.01, value=30.0, key="hr_cb")
            nb = st.number_input("B: instrucciones", 1, value=7000, key="hr_nb")
        ta, tb = na * ca / fa, nb * cb / fb
        gana = "A" if ta < tb else "B"
        st.success(f"T_A = {ta:.4g} µs · T_B = {tb:.4g} µs → **{gana}** es {max(ta, tb) / min(ta, tb):.3f} veces más rápida")


# =========================================================================== discos
def herr_discos():
    st.caption("Tiempo de acceso a un disco: búsqueda + latencia rotacional + transferencia.")
    c1, c2, c3 = st.columns(3)
    rpm = c1.number_input("Velocidad (rpm)", 1, value=15000, key="hd_r")
    seek = c2.number_input("Búsqueda media (ms)", 0.0, value=4.0, key="hd_s")
    spp = c3.number_input("Sectores por pista", 1, value=500, key="hd_p")
    vuelta = 60000 / rpm
    lat = vuelta / 2
    tr = vuelta / spp
    st.markdown(f"Una vuelta: **{vuelta:.4g} ms** · latencia media (media vuelta): **{lat:.4g} ms** · "
                f"leer un sector: **{tr:.4g} ms**")
    st.success(f"Acceso a un sector: {seek:g} + {lat:.4g} + {tr:.4g} = **{seek + lat + tr:.4g} ms**")
    n = st.number_input("Sectores del fichero", 1, value=2500, key="hd_n")
    pistas = -(-n // spp)
    sec = seek + lat + vuelta + (pistas - 1) * (lat + vuelta) if n >= spp else seek + lat + n * tr
    st.info(f"**Secuencial** (pistas contiguas): ≈ {sec:.4g} ms · **Aleatorio**: {n} × {seek + lat + tr:.4g} = "
            f"{n * (seek + lat + tr):.6g} ms")


# =========================================================================== consistencia
def herr_consistencia():
    st.caption("Enumera todas las intercalaciones (consistencia secuencial) de hilos sencillos. "
               "Sentencias: X=1 · Y=X · print(X) · while(flag==0)")
    n = st.number_input("Número de hilos", 1, 4, 3, key="hk_n")
    defecto = ["A=1\nprint(flag)", "while(flag==0)\nprint(A)", "flag=1\nprint(A)", "B=1"]
    cols = st.columns(int(n))
    hilos = [c.text_area(f"P{k + 1}", defecto[k], key=f"hk_{k}", height=130) for k, c in enumerate(cols)]
    fin = st.text_input("Variables cuyo valor final quieres ver (separadas por comas)", "", key="hk_f")
    from core.consistencia import intercalaciones, texto_orden
    try:
        res = intercalaciones(hilos, tuple(v.strip() for v in fin.split(",") if v.strip()))
    except ValueError as exc:
        st.error(str(exc))
        return
    filas = []
    for clave, orden in sorted(res.items()):
        d = {f"P{k + 1} imprime": " ".join(map(str, s)) for k, s in enumerate(clave[:-1])}
        if clave[-1]:
            d["Final"] = ", ".join(f"{v}={x}" for v, x in zip([v.strip() for v in fin.split(",") if v.strip()], clave[-1]))
        d["Un orden que lo produce"] = texto_orden(hilos, orden).replace("`", "")
        filas.append(d)
    st.success(f"{len(filas)} resultados posibles con consistencia secuencial")
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")


# =========================================================================== patios de juego
EJ_C = r"""#include <stdio.h>

int main(void)
{
    int n;
    printf("Dime un numero: ");
    scanf("%d", &n);
    for (int i = 1; i <= n; i++)
        printf("%d al cuadrado es %d\n", i, i * i);
    return 0;
}
"""

EJ_PY = '''def cuadrado(n):
    return n * n

n = int(input("Dime un número: "))
for i in range(1, n + 1):
    print(i, "al cuadrado es", cuadrado(i))
'''


def herr_c():
    st.caption("Compila con gcc -std=c11 -Wall -Wextra y ejecuta. Si no compila, te enseña los mensajes del compilador.")
    from ui.codigo import ejecutar_c
    cod = st.text_area("Programa en C", st.session_state.pop("_c_precarga", EJ_C), height=360, key="hcc_cod")
    ent = st.text_area("Entrada por teclado", "5", height=68, key="hcc_ent")
    if st.button("▶ Compilar y ejecutar", type="primary", key="hcc_run"):
        out, err, rc, msgs = ejecutar_c(cod, ent)
        if msgs.strip():
            (st.error if rc is None else st.warning)("Mensajes del compilador:")
            st.code(msgs, language="text")
            _explicar_gcc(msgs)
        if rc is not None:
            st.code(out or "(no imprime nada)", language="text")
            if err.strip():
                st.error(err)
            st.caption(f"Código de salida: {rc}")


def _explicar_gcc(msgs):
    pistas = [("expected ';'", "Falta un `;` (normalmente al final de la línea anterior a la que señala)."),
              ("undeclared", "Usas una variable o función que no está declarada (¿falta declararla, un `#include` o un prototipo?)."),
              ("implicit declaration", "Llamas a una función antes de declararla: pon su prototipo arriba o el `#include` que la trae."),
              ("undefined reference to `sqrt'", "Falta `-lm` al compilar (aquí ya se añade)."),
              ("format '%d' expects", "El marcador de printf/scanf no coincide con el tipo de la variable."),
              ("format '%f' expects argument of type 'float *'", "Para leer un double con scanf es `%lf`."),
              ("suggest parentheses around assignment", "¿Querías `==`? Con `=` asignas dentro del if."),
              ("is used uninitialized", "Usas una variable sin darle valor (tiene basura)."),
              ("control reaches end of non-void function", "A la función le falta un `return` en algún camino."),
              ("expected declaration or statement at end of input", "Falta cerrar una llave `}`.")]
    for clave, texto in pistas:
        if clave in msgs:
            st.info(f"💡 {texto}")


def herr_python():
    st.caption("Ejecuta tu programa de Python 3. Lo que pongas en la entrada es lo que leerá input().")
    from ui.codigo import ejecutar_python
    cod = st.text_area("Programa en Python", st.session_state.pop("_py_precarga", EJ_PY), height=360, key="hpy_cod")
    ent = st.text_area("Entrada por teclado", "5", height=68, key="hpy_ent")
    if st.button("▶ Ejecutar", type="primary", key="hpy_run"):
        out, err, rc = ejecutar_python(cod, ent)
        st.code(out or "(no imprime nada)", language="text")
        if rc != 0 and err.strip():
            st.error(err.strip().splitlines()[-1])
            with st.expander("Traza completa del error"):
                st.code(err, language="text")
            _explicar_py(err)


def _explicar_py(err):
    pistas = [("IndentationError", "La sangría no cuadra: usa 4 espacios en cada nivel y no mezcles tabuladores."),
              ("NameError", "Usas un nombre que no existe (¿mal escrito? ¿variable sin asignar todavía?)."),
              ("TypeError: can only concatenate str", "Estás sumando texto y número: usa `str(n)` o una coma en print."),
              ("unsupported operand type(s) for +: 'int' and 'str'", "Sumas un número y un texto: ¿olvidaste `int(input())`?"),
              ("ValueError: invalid literal for int()", "`int()` ha recibido algo que no es un número entero."),
              ("IndexError", "Te sales de la lista/cadena: los índices van de 0 a len − 1."),
              ("ZeroDivisionError", "Divides entre 0."),
              ("RecursionError", "La recursión no para: revisa el caso base."),
              ("EOFError", "El programa pide más datos de los que has escrito en la entrada."),
              ("SyntaxError", "Hay algo mal escrito: dos puntos al final de if/for/def, paréntesis o comillas sin cerrar…")]
    for clave, texto in pistas:
        if clave in err:
            st.info(f"💡 {texto}")
            break


HERRAMIENTAS = {
    "Simulador MIPS": (herr_mips, "⚙️", "fc"),
    "Codificador de instrucciones": (herr_codificador, "🔣", "fc"),
    "Bases y potencias": (herr_bases, "🔢", "fc"),
    "Representación de enteros": (herr_enteros, "➕", "fc"),
    "IEEE 754": (herr_ieee, "🌊", "fc"),
    "Caché": (herr_cache, "🧠", "fc"),
    "Memoria virtual": (herr_virtual, "📄", "fc"),
    "Segmentación": (herr_pipeline, "🚀", "fc"),
    "Rendimiento": (herr_rendimiento, "⚡", "fc"),
    "Discos": (herr_discos, "💽", "fc"),
    "Consistencia": (herr_consistencia, "🤝", "fc"),
    "Compilador de C": (herr_c, "💻", "c"),
    "Intérprete de Python": (herr_python, "🐍", "py"),
}
