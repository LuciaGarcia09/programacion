"""Portada, teoría, herramientas, guías en PDF, buscador, erratas y progreso."""
from __future__ import annotations

import os

import streamlit as st

from contenido.indice import HOJAS, TEMAS, TODOS_TEMAS
from ui.estilo import cabecera, caja, tarjeta
from ui.herramientas import HERRAMIENTAS, NAV
from ui.teoria import buscar, mostrar_tema, progreso_tema, _cargar

RAIZ = os.path.dirname(os.path.dirname(__file__))
NOMBRE = {"fc": "Fundamentos de Computadores", "c": "Programación en C", "py": "Programación en Python"}
ICONO = {"fc": "🖥️", "c": "💻", "py": "🐍"}


def _ej_hechos(asig):
    p = _cargar()
    es = [e for h in HOJAS if h.asignatura == asig for e in h.ejercicios]
    return sum(1 for e in es if p.get(f"ej/{e.id}")), len(es)


# =========================================================================== portada
def inicio():
    cabecera("🌸", "ProgLucía", "Tu app para Fundamentos de Computadores, C y Python: teoría con ejemplos que se ejecutan, "
             "todos los ejercicios de tus hojas resueltos paso a paso y un «corrígeme» que prueba tus respuestas y tus "
             "programas.", etiqueta="1.º de Ingeniería de Datos e IA",
             chips=[f"{sum(len(h.ejercicios) for h in HOJAS)} ejercicios resueltos",
                    f"{sum(len(t.secciones) for t in TODOS_TEMAS)} secciones de teoría",
                    f"{len(HERRAMIENTAS)} herramientas", "simulador MIPS · gcc · Python"])
    cols = st.columns(3)
    for col, asig in zip(cols, ["fc", "c", "py"]):
        h, t = _ej_hechos(asig)
        temas = TEMAS[asig]
        teo = sum(progreso_tema(x) for x in temas) / max(1, len(temas))
        with col:
            tarjeta(f"{ICONO[asig]} {NOMBRE[asig]}",
                    f"{len(temas)} temas de teoría · {t} ejercicios<br>Teoría entendida: {teo * 100:.0f} % · "
                    f"ejercicios hechos: {h}/{t}", num=f"{h}/{t}", progreso=(h / t if t else 0), alto=170)
            c1, c2 = st.columns(2)
            if c1.button("📖 Teoría", key=f"go_t_{asig}", width="stretch"):
                st.switch_page(NAV[f"teoria_{asig}"])
            if c2.button("✍️ Ejercicios", key=f"go_e_{asig}", width="stretch", type="primary"):
                st.switch_page(NAV[f"ejercicios_{asig}"])
    st.write("")
    with caja("idea", "Cómo usarla"):
        st.markdown("""
1. **Teoría**: cada sección tiene la idea con una analogía, lo que tienes que saber decir y **ejemplos con ▶ Ejecutar**
   (Python, C y MIPS de verdad). Marca «💗 ya la entiendo» para llevar tu progreso.
2. **Ejercicios**: el enunciado de tus hojas, una **pista**, la **solución paso a paso** y **✔️ Corrígeme**: escribe tu
   resultado o tu programa y la app lo comprueba con varias pruebas (el MIPS en el simulador, el C con gcc y el Python
   ejecutándolo).
3. **Herramientas**: simulador MIPS, codificador de instrucciones, IEEE 754, caché, memoria virtual, segmentación,
   rendimiento, discos y consistencia, más un compilador de C y un intérprete de Python.
4. **Guías**: tus PDF originales (guías, chuletas y hojas) para consultarlos sin salir de la app.""")
    with caja("ojo", "Erratas"):
        st.markdown("Las hojas y diapositivas tienen erratas: en cada ejercicio afectado verás un recuadro 🛠️ y tienes "
                    "la lista completa en **Erratas**. Si en clase os lo explicaron de otra forma, haz caso al profe 💗")


# =========================================================================== teoría
def pagina_teoria(asig: str):
    temas = TEMAS[asig]
    cabecera("📖", f"Teoría · {NOMBRE[asig]}", "Explicada desde cero, con analogías y ejemplos que puedes ejecutar.",
             etiqueta=NOMBRE[asig], chips=[f"{len(temas)} temas", f"{sum(len(t.secciones) for t in temas)} secciones"])
    ids = [t.id for t in temas]
    clave = f"tema_{asig}"
    if st.session_state.get(clave) not in ids:
        st.session_state[clave] = ids[0]
    elegido = st.pills("Tema", ids, key=f"pills_{clave}", default=st.session_state[clave],
                       format_func=lambda i: next(f"{t.numero}. {t.titulo} · {progreso_tema(t) * 100:.0f} %"
                                                  for t in temas if t.id == i), label_visibility="collapsed")
    if elegido and elegido != st.session_state[clave]:
        st.session_state[clave] = elegido
    t = next(x for x in temas if x.id == st.session_state[clave])
    st.markdown(f"## {t.numero}. {t.titulo}")
    st.caption(t.resumen)
    mostrar_tema(t)


# =========================================================================== herramientas
def pagina_herramientas():
    nombres = [n for n, (_, _, a) in HERRAMIENTAS.items() if a == "fc"]
    cabecera("🧪", "Herramientas · Fundamentos de Computadores",
             "Calcula, simula y comprueba: cada herramienta explica el paso a paso.", etiqueta="Computadores",
             chips=[f"{len(nombres)} herramientas"])
    pedido = st.session_state.pop("_herr", None)
    if pedido in nombres:
        st.session_state["herr_sel"] = pedido
        st.session_state.pop("pills_herr", None)
    if st.session_state.get("herr_sel") not in nombres:
        st.session_state["herr_sel"] = nombres[0]
    el = st.pills("Herramienta", nombres, key="pills_herr", default=st.session_state["herr_sel"],
                  format_func=lambda n: f"{HERRAMIENTAS[n][1]} {n}", label_visibility="collapsed")
    if el and el != st.session_state["herr_sel"]:
        st.session_state["herr_sel"] = el
    n = st.session_state["herr_sel"]
    st.markdown(f"### {HERRAMIENTAS[n][1]} {n}")
    HERRAMIENTAS[n][0]()


def pagina_compilador():
    cabecera("💻", "Compilador de C", "Escribe, compila (gcc -Wall -Wextra) y ejecuta; te explica los errores más típicos.",
             etiqueta="Programación en C")
    HERRAMIENTAS["Compilador de C"][0]()


def pagina_interprete():
    cabecera("🐍", "Intérprete de Python", "Ejecuta tus programas con su entrada por teclado y te explica los errores.",
             etiqueta="Programación en Python")
    HERRAMIENTAS["Intérprete de Python"][0]()


# =========================================================================== guías en PDF
GUIAS = [
    ("Guías y chuletas", [("Guia_MIPS_Temas3y4.pdf", "Fundamentos de Computadores · Temas 3 y 4 (MIPS y memoria)"),
                          ("Guia_C.pdf", "Programar en C desde cero (guía rosa)"), ("Chuleta_C.pdf", "Chuleta de C"),
                          ("Guia_Python.pdf", "Programación en Python"),
                          ("Chuleta_Python_tipos.pdf", "Chuleta de Python: tipos y métodos")]),
    ("Hojas de Estructura de Computadores (UC3M)", [
        ("EC_1_Introduccion.pdf", "1 · Introducción"), ("EC_2_Representacion.pdf", "2 · Representación de la información"),
        ("EC_3_Ensamblador.pdf", "3 · Programación en ensamblador"), ("EC_4_Unidad_de_control.pdf", "4 · Unidad de control"),
        ("EC_5_Cache.pdf", "5 · Jerarquía de memoria y caché"), ("EC_5_Memoria_virtual.pdf", "5 · Memoria virtual"),
        ("EC_6_Entrada_salida.pdf", "6 · Sistemas de E/S")]),
    ("Hojas de Arquitectura de Computadores (ARCOS)", [
        ("AC_1_Fundamentos.pdf", "Fundamentos"), ("AC_2_ILP.pdf", "Paralelismo a nivel de instrucción"),
        ("AC_3_Jerarquia_memoria.pdf", "Jerarquía de memoria"), ("AC_4_Multiprocesadores.pdf", "Multiprocesadores")]),
]


def pagina_guias():
    cabecera("📚", "Tus guías y hojas", "Los PDF originales, para leerlos o descargarlos sin salir de la app.",
             etiqueta="Estudiar")
    opciones = [(f, t) for _, lista in GUIAS for f, t in lista]
    grupo = {f: g for g, lista in GUIAS for f, _ in lista}
    f = st.selectbox("Documento", [o[0] for o in opciones], format_func=lambda x: f"{grupo[x]} · {dict(opciones)[x]}",
                     key="guia_sel")
    ruta = os.path.join(RAIZ, "assets", "pdf", f)
    if not os.path.exists(ruta):
        st.error("No encuentro ese PDF.")
        return
    with open(ruta, "rb") as fh:
        datos = fh.read()
    st.download_button("⬇️ Descargar", datos, file_name=f, mime="application/pdf", key="guia_dl")
    try:
        st.pdf(datos, height=800)
    except Exception:  # noqa: BLE001  (st.pdf necesita el extra streamlit[pdf])
        st.info("Para verlo aquí dentro hace falta `pip install streamlit[pdf]`; mientras, descárgalo con el botón.")


# =========================================================================== buscador
def pagina_buscador():
    cabecera("🔎", "Buscador", "Busca en toda la teoría y en todos los ejercicios.", etiqueta="Estudiar")
    q = st.text_input("¿Qué buscas?", placeholder="malloc, little endian, LRU, comprensión, $ra…", key="busca_q")
    if len(q.strip()) < 2:
        return
    res = buscar(TODOS_TEMAS, q)
    st.markdown(f"**Teoría** · {len(res)} resultados")
    for _, t, s, frag in res[:25]:
        asig = next(a for a, ts in TEMAS.items() if t in ts)
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"{ICONO[asig]} **{t.titulo} → {s.titulo}**  \n<span class='mini'>…{frag}…</span>",
                    unsafe_allow_html=True)
        if c2.button("Abrir", key=f"bt_{t.id}_{s.id}"):
            st.session_state[f"tema_{asig}"] = t.id
            st.session_state.pop(f"pills_tema_{asig}", None)
            st.session_state[f"sec_{t.id}"] = s.id
            st.session_state.pop(f"pills_{t.id}", None)
            st.switch_page(NAV[f"teoria_{asig}"])
    from ui.teoria import _norm
    palabras = _norm(q).split()
    ejs = [(h, e) for h in HOJAS for e in h.ejercicios
           if all(w in _norm(e.titulo + " " + e.enunciado + " " + e.solucion) for w in palabras)]
    st.markdown(f"**Ejercicios** · {len(ejs)} resultados")
    for h, e in ejs[:30]:
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"{h.icono} **{h.titulo} → {e.titulo}**")
        if c2.button("Abrir", key=f"be_{e.id}"):
            st.session_state["_ir_a_ejercicio"] = e.id
            st.switch_page(NAV[f"ejercicios_{h.asignatura}"])


# =========================================================================== erratas
def pagina_erratas():
    cabecera("🛠️", "Erratas", "Todo lo que estaba mal (o confuso) en hojas y diapositivas, ya corregido en la app.",
             etiqueta="Estudiar")
    filas = [(h, e) for h in HOJAS for e in h.ejercicios if e.errata]
    st.markdown(f"#### En los enunciados de los ejercicios ({len(filas)})")
    for h, e in filas:
        with caja("errata", f"{h.titulo} · {e.titulo}"):
            st.markdown(e.errata)
    st.markdown("#### En la teoría")
    for t in TODOS_TEMAS:
        for s in t.secciones:
            for b in s.bloques:
                if b[0] == "errata":
                    with caja("errata", f"{t.titulo} · {b[1] or s.titulo}"):
                        st.markdown(b[2])


# =========================================================================== progreso
def pagina_progreso():
    cabecera("💗", "Mi progreso", "Lo que ya entiendes y los ejercicios que dominas.", etiqueta="Estudiar")
    p = _cargar()
    for asig in ["fc", "c", "py"]:
        st.markdown(f"### {ICONO[asig]} {NOMBRE[asig]}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Teoría**")
            for t in TEMAS[asig]:
                st.progress(progreso_tema(t), text=f"{t.numero}. {t.titulo}")
        with c2:
            st.markdown("**Ejercicios**")
            for h in [h for h in HOJAS if h.asignatura == asig]:
                n = sum(1 for e in h.ejercicios if p.get(f"ej/{e.id}"))
                st.progress(n / len(h.ejercicios), text=f"{h.icono} {h.titulo}: {n}/{len(h.ejercicios)}")
    st.divider()
    if st.button("🗑️ Borrar todo mi progreso", key="borrar_prog"):
        st.session_state["confirmar_borrar"] = True
    if st.session_state.get("confirmar_borrar"):
        st.warning("¿Seguro? Se borra todo lo marcado.")
        if st.button("Sí, borrar", key="borrar_si", type="primary"):
            from ui.teoria import _guardar
            st.session_state.progreso = {}
            _guardar()
            st.session_state["confirmar_borrar"] = False
            st.rerun()
