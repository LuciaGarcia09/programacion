"""Cada página y cada herramienta se ejecutan sin errores; los ejemplos de la teoría funcionan."""
import pytest
from streamlit.testing.v1 import AppTest

from contenido.indice import TODOS_TEMAS, HOJAS
from ui.herramientas import HERRAMIENTAS


def correr(codigo, preparar=None, timeout=120):
    at = AppTest.from_string("import sys; sys.path.insert(0, '.')\n" + codigo, default_timeout=timeout)
    at.run()
    if preparar:
        preparar(at)
        at.run()
    return at


def sin_errores(at):
    assert not at.exception, [e.value for e in at.exception]
    errores = [e.value for e in at.error]
    assert not errores, errores


@pytest.mark.parametrize("fn", ["inicio", "pagina_herramientas", "pagina_compilador", "pagina_interprete", "pagina_guias",
                                "pagina_buscador", "pagina_erratas", "pagina_progreso"])
def test_paginas(fn):
    sin_errores(correr(f"from ui import paginas\npaginas.{fn}()"))


@pytest.mark.parametrize("asig", ["fc", "c", "py"])
def test_teoria_y_ejercicios(asig):
    sin_errores(correr(f"from ui import paginas\npaginas.pagina_teoria('{asig}')"))
    sin_errores(correr(f"from ui import ejercicios\nejercicios.pagina_ejercicios('{asig}')"))


@pytest.mark.parametrize("nombre", list(HERRAMIENTAS))
def test_herramientas(nombre):
    sin_errores(correr(f"from ui.herramientas import HERRAMIENTAS\nHERRAMIENTAS[{nombre!r}][0]()"))


TEMAS_SECS = [(t.id, s.id) for t in TODOS_TEMAS for s in t.secciones]


@pytest.mark.parametrize("tid,sid", TEMAS_SECS, ids=[f"{a}-{b}" for a, b in TEMAS_SECS])
def test_cada_seccion_se_muestra(tid, sid):
    cod = (f"import streamlit as st\nfrom contenido.indice import TODOS_TEMAS\nfrom ui.teoria import mostrar_tema\n"
           f"t = next(x for x in TODOS_TEMAS if x.id == {tid!r})\nst.session_state['sec_{tid}'] = {sid!r}\nmostrar_tema(t)")
    sin_errores(correr(cod))


EJS = [e.id for h in HOJAS for e in h.ejercicios]


@pytest.mark.parametrize("eid", EJS)
def test_cada_ejercicio_se_muestra(eid):
    cod = (f"from contenido.indice import HOJAS\nfrom ui.ejercicios import mostrar_ejercicio\n"
           f"e = next(x for h in HOJAS for x in h.ejercicios if x.id == {eid!r})\nmostrar_ejercicio(e)")
    sin_errores(correr(cod))


def test_app_completa_arranca():
    at = AppTest.from_file("../app.py", default_timeout=120)
    at.run()
    sin_errores(at)


def test_corrigeme_mips_desde_la_interfaz():
    from contenido.ej_ensamblador import S2
    cod = ("from contenido.indice import HOJAS\nfrom ui.ejercicios import mostrar_ejercicio\n"
           "e = next(x for h in HOJAS for x in h.ejercicios if x.id == 'ens-2')\nmostrar_ejercicio(e)")
    at = correr(cod)
    at.text_area(key="cod_ens-2").set_value(S2)
    [b for b in at.button if "Corrígeme" in b.label][0].click()
    at.run()
    assert any("Pasa las" in s.value for s in at.success), [s.value for s in at.success]


def test_corrigeme_respuestas():
    cod = ("from contenido.indice import HOJAS\nfrom ui.ejercicios import mostrar_ejercicio\n"
           "e = next(x for h in HOJAS for x in h.ejercicios if x.id == 'repr-2')\nmostrar_ejercicio(e)")
    at = correr(cod)
    for k, v in enumerate(["19", "-9", "-32"]):
        at.text_input(key=f"r_repr-2_{k}").set_value(v)
    at.button[0].click()
    at.run()
    assert any("Todo correcto" in s.value for s in at.success), [s.value for s in at.success]
