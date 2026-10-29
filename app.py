"""ProgLucía · Fundamentos de Computadores, Programación en C y Python (1.º de Ingeniería de Datos e IA).

Arranque:  streamlit run app.py
"""
import streamlit as st

from ui import ejercicios, paginas
from ui.estilo import aplicar_estilo
from ui.herramientas import NAV
from ui.teoria import guardar_en_navegador, leer_del_navegador

st.set_page_config(page_title="ProgLucía", page_icon="🌸", layout="wide")
aplicar_estilo()


def _seguro(func, nombre):
    """Ninguna página deja la app en blanco: si algo falla, lo explica."""
    def envoltura():
        try:
            func()
        except Exception as exc:  # noqa: BLE001
            if type(exc).__name__ in ("RerunException", "StopException", "SwitchPageException"):
                raise
            st.error(f"Algo ha fallado en esta página: {exc}. Revisa lo que has escrito o prueba otro ejemplo.")
            with st.expander("Detalles técnicos"):
                st.exception(exc)
    envoltura.__name__ = nombre
    return envoltura


def _p(func, titulo, icono, url, clave=None, **kw):
    pg = st.Page(_seguro(func, url), title=titulo, icon=icono, url_path=url, **kw)
    NAV[clave or url] = pg
    return pg


paginas_nav = {
    "": [_p(paginas.inicio, "Inicio", "🏠", "inicio", default=True)],
    "Fundamentos de Computadores": [
        _p(lambda: paginas.pagina_teoria("fc"), "Teoría", "📖", "teoria_fc"),
        _p(lambda: ejercicios.pagina_ejercicios("fc"), "Ejercicios", "✍️", "ejercicios_fc"),
        _p(paginas.pagina_herramientas, "Herramientas", "🧪", "herramientas"),
    ],
    "Programación en C": [
        _p(lambda: paginas.pagina_teoria("c"), "Teoría de C", "📖", "teoria_c"),
        _p(lambda: ejercicios.pagina_ejercicios("c"), "Ejercicios de C", "✍️", "ejercicios_c"),
        _p(paginas.pagina_compilador, "Compilador de C", "💻", "compilador"),
    ],
    "Programación en Python": [
        _p(lambda: paginas.pagina_teoria("py"), "Teoría de Python", "📖", "teoria_py"),
        _p(lambda: ejercicios.pagina_ejercicios("py"), "Ejercicios de Python", "✍️", "ejercicios_py"),
        _p(paginas.pagina_interprete, "Intérprete de Python", "🐍", "interprete"),
    ],
    "Estudiar": [
        _p(paginas.pagina_guias, "Guías en PDF", "📚", "guias"),
        _p(paginas.pagina_buscador, "Buscador", "🔎", "buscador"),
        _p(paginas.pagina_erratas, "Erratas", "🛠️", "erratas"),
        _p(paginas.pagina_progreso, "Mi progreso", "💗", "progreso"),
    ],
}

pagina = st.navigation(paginas_nav, expanded=True)
with st.sidebar:
    st.caption("Cada solución está comprobada: los programas se ejecutan de verdad (simulador MIPS, gcc y Python) y "
               "las cuentas con simuladores de caché, pipeline y memoria. ¡Mucho ánimo, Lucía! 💗")
with st.sidebar:
    leer_del_navegador()          # antes de dibujar nada: recupera lo que hiciste en otras sesiones
pagina.run()
with st.sidebar:
    guardar_en_navegador()
