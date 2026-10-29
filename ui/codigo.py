"""Ejecutar trozos de código (Python, C y MIPS) desde la teoría, los ejercicios y los «patios de juego»."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

import streamlit as st

from core import corrector, mips

LENG = {"py": "python", "python": "python", "c": "c", "mips": "mipsasm"}


def ejecutar_python(codigo: str, entrada: str = "", timeout=5):
    d = tempfile.mkdtemp(prefix="proglucia_py_")
    try:
        src = os.path.join(d, "prog.py")
        with open(src, "w", encoding="utf-8") as f:
            f.write(codigo)
        r = subprocess.run([sys.executable, "-I", src], input=entrada, capture_output=True, text=True,
                           timeout=timeout, cwd=d)
        return r.stdout, r.stderr.replace(src, "prog.py"), r.returncode
    except subprocess.TimeoutExpired:
        return "", f"⏳ Tarda más de {timeout} s: ¿un bucle infinito o espera más datos de los que has escrito?", -1
    finally:
        shutil.rmtree(d, ignore_errors=True)


def ejecutar_c(codigo: str, entrada: str = "", timeout=5):
    exe, msgs = corrector.compilar_c(codigo)
    if not exe:
        return "", msgs or "No compila.", None, msgs
    d = os.path.dirname(exe)
    try:
        r = subprocess.run([exe], input=entrada, capture_output=True, text=True, timeout=timeout, cwd=d)
        err = r.stderr
        if r.returncode < 0:
            err += {-11: "\n💥 Violación de segmento: accedes a memoria que no es tuya (¿índice fuera del vector o "
                         "puntero sin inicializar?)", -8: "\n💥 Excepción aritmética (¿divides entre 0?)",
                    -6: "\n💥 Abortado (¿free doble o memoria corrupta?)"}.get(r.returncode, f"\nSeñal {-r.returncode}")
        return r.stdout, err, r.returncode, msgs
    except subprocess.TimeoutExpired:
        return "", f"⏳ Tarda más de {timeout} s: ¿un bucle infinito o espera más datos?", -1, msgs
    finally:
        shutil.rmtree(d, ignore_errors=True)


def dispositivos_por_nombre(nombre):
    from core import dispositivos as D
    return {"tensiometro": lambda: [D.Tensiometro()], "microondas": lambda: [D.Microondas()],
            "sensor_piezas": lambda: [D.SensorPiezas()], "temperatura": lambda: [D.SensorTemperatura()],
            "barras": lambda: [D.LectorBarras()], "semaforo": lambda: [D.Semaforo()],
            "horno": lambda: [D.HornoAlarma()], "agua": lambda: [D.SensorAgua()]}.get(nombre)


def ejecutar_mips(codigo: str, entrada: str = "", dispositivo=None, max_pasos=200_000, historial=0):
    try:
        prog = mips.ensamblar(codigo)
    except mips.ErrorMIPS as exc:
        return None, f"Error al ensamblar: {exc}"
    devs = None
    if dispositivo:
        f = dispositivos_por_nombre(dispositivo) if isinstance(dispositivo, str) else dispositivo
        devs = f() if f else None
    res = mips.Maquina(prog, entrada, dispositivos=devs, max_pasos=max_pasos, registrar_historial=historial).ejecutar()
    return res, None


def consola(texto: str, vacio="(no imprime nada)"):
    st.code(texto if texto else vacio, language="text")


def bloque_ejecutable(lenguaje: str, titulo: str | None, codigo: str, entrada: str = "", dispositivo=None,
                      clave: str = ""):
    """Muestra el código y un botón ▶ que lo ejecuta (con la entrada indicada, editable)."""
    with st.container(border=True):
        cab = {"py": "🐍 Python", "c": "💻 C", "mips": "⚙️ MIPS"}[lenguaje]
        st.markdown(f"**{cab}{' · ' + titulo if titulo else ''}**")
        st.code(codigo, language=LENG[lenguaje], line_numbers=lenguaje != "py" or codigo.count("\n") > 6)
        c1, c2 = st.columns([1, 3])
        k = f"run_{clave}"
        with c2:
            ent = st.text_input("Entrada (lo que se teclea; usa \\n para varias líneas)", entrada.replace("\n", "\\n"),
                                key=f"ent_{clave}", label_visibility="collapsed",
                                placeholder="Entrada por teclado (opcional, \\n separa líneas)") if (entrada or lenguaje != "mips") else ""
        with c1:
            pulsado = st.button("▶ Ejecutar", key=k, width="stretch")
        if pulsado:
            ent = (ent or "").replace("\\n", "\n")
            if lenguaje == "py":
                out, err, rc = ejecutar_python(codigo, ent)
                consola(out)
                if err.strip():
                    st.error(err.strip().splitlines()[-1] if rc != 0 else err)
            elif lenguaje == "c":
                out, err, rc, msgs = ejecutar_c(codigo, ent)
                if msgs and msgs.strip():
                    with st.expander("⚠️ Avisos del compilador (gcc -Wall -Wextra)", expanded=rc is None):
                        st.code(msgs, language="text")
                if rc is not None:
                    consola(out)
                    if err.strip():
                        st.error(err.strip())
            else:
                res, err = ejecutar_mips(codigo, ent, dispositivo)
                if err:
                    st.error(err)
                else:
                    consola(res.salida)
                    st.caption(f"🛑 {res.motivo} · {res.pasos} instrucciones ejecutadas · "
                               f"{res.accesos_instr + res.accesos_datos} accesos a memoria")
                    usados = {mips.NOMBRES[k]: v for k, v in enumerate(res.regs)
                              if v and mips.NOMBRES[k] not in ("sp", "gp")}
                    if usados:
                        st.caption("Registros ≠ 0: " + " · ".join(f"${n} = {v}" for n, v in usados.items()))


def editor(etiqueta: str, valor: str, clave: str, alto: int = 300):
    return st.text_area(etiqueta, valor, height=alto, key=clave)
