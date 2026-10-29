"""Páginas de ejercicios: enunciado, «corrígeme» (respuestas y programas) y solución paso a paso."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from contenido.indice import HOJAS
from core.corrector import comprobar, corregir
from ui.estilo import cabecera, caja
from ui.teoria import _cargar, marcar

NOMBRE = {"fc": "Fundamentos de Computadores", "c": "Programación en C", "py": "Programación en Python"}
LENG = {"mips": "MIPS", "c": "C", "python": "Python"}


def hecho(eid: str) -> bool:
    return bool(_cargar().get(f"ej/{eid}"))


def marcar_hecho(eid: str, valor: bool = True):
    marcar(f"ej/{eid}", valor)
    st.session_state[f"tg_ej_{eid}"] = valor          # el interruptor de abajo aún no se ha dibujado


def progreso_hoja(h) -> float:
    return sum(hecho(e.id) for e in h.ejercicios) / max(1, len(h.ejercicios))


def _corregir_respuestas(e):
    with st.form(f"f_{e.id}"):
        st.markdown("**Escribe tus resultados** (admite `1,5`, `2^-24`, `3/4`, `1.2e-5`, hexadecimal `0x…`):")
        valores = []
        cols = st.columns(min(3, len(e.respuestas)))
        for k, r in enumerate(e.respuestas):
            with cols[k % len(cols)]:
                valores.append(st.text_input(r.etiqueta, key=f"r_{e.id}_{k}"))
        enviar = st.form_submit_button("✔️ Corrígeme", type="primary")
    if enviar:
        bien = 0
        for r, v in zip(e.respuestas, valores):
            ok, com = comprobar(r, v)
            bien += ok
            if ok:
                st.success(f"**{r.etiqueta}**: {v} ✓ ¡bien!")
            else:
                st.error(f"**{r.etiqueta}**: {v or '—'} ✗ {com}".strip())
        if bien == len(e.respuestas):
            st.balloons()
            st.success("💗 ¡Todo correcto! Ejercicio marcado como hecho.")
            marcar_hecho(e.id)
        else:
            st.info(f"{bien} de {len(e.respuestas)} bien. Mira la pista o la solución paso a paso y vuelve a intentarlo 💪")


def _corregir_programa(e):
    p = e.programa
    leng = LENG[p.lenguaje]
    clave = f"cod_{e.id}"
    if clave not in st.session_state:
        st.session_state[clave] = p.plantilla
    usa_main = any(getattr(pr, "main", None) for pr in p.pruebas)
    if p.lenguaje == "mips" and usa_main:
        st.caption("🧩 Escribe tu función: la app añade su propio `main` de prueba (si escribes un main tuyo, se ignora "
                   "en esas pruebas).")
    elif p.lenguaje == "c" and usa_main:
        st.caption("🧩 La app prueba tus funciones con su propio `main` (el tuyo se renombra solo).")
    elif p.lenguaje == "python" and usa_main:
        st.caption("🧩 La app importa tus funciones y las llama directamente (además de ejecutar tu programa).")
    codigo = st.text_area(f"Tu programa en {leng}", key=clave, height=340)
    c1, c2, c3 = st.columns(3)
    corr = c1.button("✔️ Corrígeme", type="primary", key=f"corr_{e.id}", width="stretch")
    ver = c2.button("👀 Probar la solución en la herramienta", key=f"ver_{e.id}", width="stretch")
    c3.button("↺ Volver a la plantilla", key=f"pl_{e.id}", width="stretch",
              on_click=lambda: st.session_state.update({clave: p.plantilla}))
    if ver:
        from ui.herramientas import NAV
        if p.lenguaje == "mips":
            principal = next((pr.main for pr in p.pruebas if getattr(pr, "main", None)), None)
            st.session_state["_mips_precarga"] = p.solucion + ("\n\n# ---- main de prueba ----\n" + principal if principal else "") + \
                ("\n" + p.anexo if p.anexo else "")
            st.session_state["_herr"] = "Simulador MIPS"
            st.switch_page(NAV["herramientas"])
        elif p.lenguaje == "c":
            st.session_state["_c_precarga"] = p.solucion
            st.switch_page(NAV["compilador"])
        else:
            st.session_state["_py_precarga"] = p.solucion
            st.switch_page(NAV["interprete"])
    if corr:
        if not codigo.strip():
            st.warning("Escribe tu programa antes de corregirlo 😉")
            return
        with st.spinner("Probando tu programa…"):
            try:
                res, msgs = corregir(codigo, p)
            except Exception as exc:  # noqa: BLE001
                st.error(f"No he podido probarlo: {exc}")
                return
        if msgs and msgs.strip() and p.lenguaje == "python":
            with caja("errata", "Qué falla y cómo arreglarlo"):
                st.markdown(msgs)
        elif msgs and msgs.strip():
            with st.expander("⚠️ Avisos del compilador", expanded=not any(r.ok for r in res)):
                st.code(msgs, language="text")
        errores = sorted({r.detalle for r in res if not r.ok and r.detalle.startswith("error al ejecutar")})
        if errores and p.lenguaje == "python":
            with caja("truco", "Por qué se para tu programa"):
                st.markdown("\n".join(f"- {d.removeprefix('error al ejecutar: ')}" for d in errores))
        filas = []
        for r in res:
            filas.append({"": "✅" if r.ok else "❌", "Prueba": r.descripcion, "Entrada": r.entrada.replace("\n", " ⏎ "),
                          "Se esperaba": r.esperado, "Tu programa": r.obtenido.strip()[:300], "Comentario": r.detalle})
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
        buenas = sum(r.ok for r in res)
        if buenas == len(res) and res:
            st.balloons()
            st.success(f"💗 ¡Pasa las {len(res)} pruebas! Ejercicio marcado como hecho.")
            marcar_hecho(e.id)
        else:
            st.warning(f"Pasa {buenas} de {len(res)} pruebas. Mira la columna «Comentario»: dice qué falla.")


def mostrar_ejercicio(e):
    with caja("enunciado", e.titulo):
        st.markdown(e.enunciado)
    if e.origen:
        st.caption(f"📎 {e.origen}")
    if e.errata:
        with caja("errata"):
            st.markdown(e.errata)
    nombres = []
    if e.respuestas or e.programa:
        nombres.append("✍️ Corrígeme")
    if e.pista:
        nombres.append("💡 Pista")
    nombres.append("✅ Solución paso a paso")
    tabs = st.tabs(nombres, key=f"tabs_ej_{e.id}", on_change="rerun")
    k = 0
    if e.respuestas or e.programa:
        if tabs[k].open:
            with tabs[k]:
                if e.programa:
                    _corregir_programa(e)
                if e.respuestas:
                    if e.programa:
                        st.divider()
                    _corregir_respuestas(e)
        k += 1
    if e.pista:
        if tabs[k].open:
            with tabs[k]:
                with caja("truco", "Pista"):
                    st.markdown(e.pista)
        k += 1
    if tabs[k].open:
        with tabs[k]:
            st.markdown(e.solucion)
            if e.herramienta:
                from ui.herramientas import boton_herramienta
                boton_herramienta(e.herramienta, f"hb_{e.id}")
    st.divider()
    k = f"tg_ej_{e.id}"
    if k not in st.session_state:
        st.session_state[k] = hecho(e.id)
    st.toggle("💗 Este ejercicio ya lo domino", key=k, on_change=lambda: marcar(f"ej/{e.id}", st.session_state[k]))


def pagina_ejercicios(asig: str):
    hojas = [h for h in HOJAS if h.asignatura == asig]
    total = sum(len(h.ejercicios) for h in hojas)
    hechos = sum(hecho(e.id) for h in hojas for e in h.ejercicios)
    cabecera("✍️", f"Ejercicios · {NOMBRE[asig]}", "Todos los ejercicios de tus hojas, resueltos paso a paso y con "
             "corrección automática.", etiqueta=NOMBRE[asig],
             chips=[f"{len(hojas)} hojas", f"{total} ejercicios", f"{hechos} hechos"])
    ids = [h.id for h in hojas]
    clave = f"hoja_{asig}"
    pedido = st.session_state.pop("_ir_a_ejercicio", None)
    if pedido:
        for h in hojas:
            if any(e.id == pedido for e in h.ejercicios):
                st.session_state[clave] = h.id
                st.session_state[f"ej_{h.id}"] = pedido
                st.session_state.pop(f"pills_{clave}", None)
    if st.session_state.get(clave) not in ids:
        st.session_state[clave] = ids[0]
    elegido = st.pills("Hoja", ids, key=f"pills_{clave}", default=st.session_state[clave],
                       format_func=lambda i: next(f"{h.icono} {h.titulo} · {progreso_hoja(h) * 100:.0f} %"
                                                  for h in hojas if h.id == i), label_visibility="collapsed")
    if elegido and elegido != st.session_state[clave]:
        st.session_state[clave] = elegido
    h = next(x for x in hojas if x.id == st.session_state[clave])
    st.markdown(f"### {h.icono} {h.titulo}")
    st.caption(f"📚 {h.fuente} · {h.descripcion}")
    st.progress(progreso_hoja(h), text=f"{sum(hecho(e.id) for e in h.ejercicios)} de {len(h.ejercicios)} hechos")
    eids = [e.id for e in h.ejercicios]
    ck = f"ej_{h.id}"
    if st.session_state.get(ck) not in eids:
        st.session_state[ck] = eids[0]
    titulos = {e.id: ("✅ " if hecho(e.id) else "") + f"{k}. {e.titulo}" for k, e in enumerate(h.ejercicios, 1)}
    c1, c2, c3 = st.columns([1, 6, 1])
    i = eids.index(st.session_state[ck])

    def _mover(paso):                       # callback: corre antes de dibujar el selector
        st.session_state[ck] = eids[eids.index(st.session_state[ck]) + paso]

    c1.button("←", key=f"prev_{h.id}", disabled=i == 0, width="stretch", on_click=_mover, args=(-1,))
    with c2:
        st.selectbox("Ejercicio", eids, key=ck, format_func=titulos.get, label_visibility="collapsed")
    c3.button("→", key=f"next_{h.id}", disabled=i == len(eids) - 1, width="stretch", on_click=_mover, args=(1,))
    e = next(x for x in h.ejercicios if x.id == st.session_state[ck])
    mostrar_ejercicio(e)
