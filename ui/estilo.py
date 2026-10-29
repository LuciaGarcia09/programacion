"""Sistema de diseño de MatesLucía: colores, tipografía, cabeceras y cajas de teoría."""
from __future__ import annotations

import itertools
from contextlib import contextmanager

import streamlit as st

ROSA = "#e75480"
ROSA_OSC = "#b8336a"
ROSA_CLARO = "#fde7ef"
LILA = "#8e5bd6"
LILA_CLARO = "#f1eafc"
MENTA = "#1fa595"
MENTA_CLARO = "#e3f6f3"
AMARILLO = "#e0a21b"
AMARILLO_CLARO = "#fff7e0"
NARANJA = "#e2711d"
NARANJA_CLARO = "#fff0e4"
ROJO = "#d64545"
ROJO_CLARO = "#fdecec"
TINTA = "#2b1b24"
GRIS = "#8a7f86"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600&family=JetBrains+Mono:wght@400;600&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, p, li, label, input, textarea, button {{
  font-family: 'Nunito', system-ui, -apple-system, 'Segoe UI', sans-serif;
}}
h1, h2, h3, h4 {{ font-family: 'Fredoka', 'Nunito', sans-serif !important; color: {ROSA_OSC}; letter-spacing: .2px; }}
.block-container {{ padding-top: 3.4rem; max-width: 1180px; }}
[data-testid="stAppViewContainer"] {{
  background: radial-gradient(1200px 500px at 100% -10%, #ffe3ef 0%, rgba(255,255,255,0) 60%),
              radial-gradient(900px 400px at -10% 110%, #efe6ff 0%, rgba(255,255,255,0) 60%), #fffafc;
}}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #fff0f6 0%, #fbe3ee 55%, #f3e8ff 100%); }}
[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{ border-color: #f2c4d6; }}
[data-testid="stSidebarNavLink"] span {{ font-weight: 600; }}

/* ---------- cabecera de página ---------- */
.cabecera {{
  background: linear-gradient(120deg, {ROSA} 0%, #f07aa3 45%, {LILA} 100%);
  border-radius: 22px; padding: 22px 26px 18px 26px; color: white; margin: 4px 0 18px 0;
  box-shadow: 0 10px 30px rgba(231,84,128,.25); position: relative; overflow: hidden;
}}
.cabecera:after {{ content: "✿"; position: absolute; right: 22px; top: -10px; font-size: 110px; opacity: .15; }}
.cabecera .tag {{ font-size: .78rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; opacity: .9; }}
.cabecera h1 {{ color: white !important; margin: 2px 0 4px 0; font-size: 2.05rem; }}
.cabecera p {{ margin: 0; font-size: 1.02rem; opacity: .95; }}
.chips {{ margin-top: 10px; }}
.chip {{ display: inline-block; background: rgba(255,255,255,.22); border: 1px solid rgba(255,255,255,.45);
  border-radius: 999px; padding: 2px 11px; margin: 3px 6px 0 0; font-size: .82rem; font-weight: 700; }}

/* ---------- tarjetas de la portada ---------- */
.tarjeta {{ background: white; border: 1px solid #f6cadb; border-radius: 18px; padding: 16px 18px; height: 100%;
  box-shadow: 0 4px 14px rgba(184,51,106,.07); transition: transform .15s ease, box-shadow .15s ease; }}
.tarjeta:hover {{ transform: translateY(-2px); box-shadow: 0 10px 24px rgba(184,51,106,.14); }}
.tarjeta {{ display: flex; flex-direction: column; }}
.tarjeta .barra {{ margin-top: auto; }}
.tarjeta .mini {{ margin-bottom: 10px; }}
.tarjeta h4 {{ margin: 0 0 6px 0; color: {ROSA_OSC}; }}
.tarjeta .num {{ font-family: 'Fredoka'; font-size: 1.9rem; color: {ROSA}; line-height: 1; }}
.mini {{ color: {GRIS}; font-size: .86rem; }}
.barra {{ height: 9px; background: #f7d9e5; border-radius: 99px; overflow: hidden; margin-top: 8px; }}
.barra > div {{ height: 100%; background: linear-gradient(90deg, {ROSA}, {LILA}); border-radius: 99px; }}

/* ---------- cajas de teoría (st.container con key="caja-<tipo>-…") ---------- */
div[class*="st-key-caja-"] {{ border-radius: 16px; padding: 12px 16px 6px 16px; margin: 6px 0 12px 0;
  border: 1px solid transparent; }}
div[class*="st-key-caja-idea"] {{ background: {ROSA_CLARO}; border-left: 6px solid {ROSA}; }}
div[class*="st-key-caja-enunciado"] {{ background: #fff; border: 2px solid #f4a9c4; box-shadow: 0 3px 10px rgba(231,84,128,.08); }}
div[class*="st-key-caja-def"] {{ background: #fff; border: 2px solid #f4a9c4; box-shadow: 0 3px 10px rgba(231,84,128,.08); }}
div[class*="st-key-caja-teo"] {{ background: {LILA_CLARO}; border: 2px solid #c9b2f0; }}
div[class*="st-key-caja-ej"] {{ background: {MENTA_CLARO}; border-left: 6px solid {MENTA}; }}
div[class*="st-key-caja-truco"] {{ background: {AMARILLO_CLARO}; border: 2px dashed {AMARILLO}; }}
div[class*="st-key-caja-ojo"] {{ background: {NARANJA_CLARO}; border-left: 6px solid {NARANJA}; }}
div[class*="st-key-caja-errata"] {{ background: {ROJO_CLARO}; border: 2px solid #f2aaaa; }}
div[class*="st-key-caja-ia"] {{ background: #f4efff; border-left: 6px solid {LILA}; }}
div[class*="st-key-caja-resumen"] {{ background: linear-gradient(135deg, #fff 0%, #fff3f8 100%); border: 2px solid {ROSA}; }}
div[class*="st-key-caja-pasos"] {{ background: #fff; border: 1px solid #ead7e0; }}
.titulo-caja {{ font-family: 'Fredoka'; font-weight: 600; font-size: 1.02rem; margin-bottom: 2px; }}
.t-idea {{ color: {ROSA_OSC}; }} .t-def {{ color: {ROSA_OSC}; }} .t-teo {{ color: {LILA}; }} .t-ej {{ color: {MENTA}; }}
.t-truco {{ color: #a86f00; }} .t-ojo {{ color: {NARANJA}; }} .t-errata {{ color: {ROJO}; }} .t-ia {{ color: {LILA}; }}
.t-resumen {{ color: {ROSA}; }} .t-pasos {{ color: {ROSA_OSC}; }} .t-enunciado {{ color: {ROSA_OSC}; }}
[data-testid="stTextArea"] textarea {{ font-family: 'JetBrains Mono', ui-monospace, 'Cascadia Code', Consolas, monospace !important;
  font-size: .9rem; line-height: 1.45; tab-size: 4; }}

/* ---------- widgets ---------- */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; flex-wrap: wrap; }}
.stTabs [data-baseweb="tab"] {{ background: #fff3f8; border-radius: 12px 12px 0 0; padding: 6px 12px; font-weight: 700; }}
.stTabs [aria-selected="true"] {{ background: #ffe0ec !important; }}
[data-testid="stExpander"] details {{ border-radius: 14px; border-color: #f3cfdd; background: rgba(255,255,255,.7); }}
[data-testid="stMetricValue"] {{ font-family: 'Fredoka'; color: {ROSA_OSC}; }}
.stButton > button, .stFormSubmitButton > button {{ border-radius: 12px; font-weight: 700; }}
.stButton > button[kind="primary"] {{ background: linear-gradient(90deg, {ROSA}, {LILA}); border: none; }}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {{ border-radius: 10px; }}
code {{ color: {ROSA_OSC}; background: #fff0f6; }}
.katex {{ font-size: 1.07em; }}
.sello {{ display:inline-block; padding: 1px 9px; border-radius: 99px; font-weight: 800; font-size: .8rem; }}
.sello-ok {{ background: #dff5ea; color: #1b7a4b; }} .sello-no {{ background: #fde3e3; color: #b42323; }}
footer {{ visibility: hidden; }}
</style>
"""

ICONOS = {
    "idea": ("💡", "La idea"), "def": ("📘", "Definición"), "teo": ("⭐", "Teorema"), "ej": ("✏️", "Ejemplo"),
    "truco": ("🪄", "Truco"), "ojo": ("⚠️", "Cuidado"), "errata": ("🛠️", "Errata de los apuntes"),
    "ia": ("🤖", "En Datos e IA"), "enunciado": ("📝", "Enunciado"), "resumen": ("📌", "Resumen"), "pasos": ("🪜", "Paso a paso"),
}

_contador = itertools.count()


def aplicar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def cabecera(icono: str, titulo: str, subtitulo: str = "", etiqueta: str = "", chips: list[str] | None = None):
    chips_html = "".join(f"<span class='chip'>{c}</span>" for c in (chips or []))
    st.markdown(
        f"<div class='cabecera'><div class='tag'>{etiqueta}</div><h1>{icono} {titulo}</h1>"
        f"<p>{subtitulo}</p><div class='chips'>{chips_html}</div></div>", unsafe_allow_html=True)


@contextmanager
def caja(tipo: str, titulo: str | None = None, clave: str | None = None):
    """Caja de color. Dentro se puede usar cualquier widget y LaTeX ($…$)."""
    ic, nombre = ICONOS.get(tipo, ("•", tipo))
    k = clave or f"caja-{tipo}-{next(_contador)}"
    if not k.startswith("caja-"):
        k = f"caja-{tipo}-{k}"
    with st.container(key=k):
        cab = f"{ic} {nombre}" + (f" · {titulo}" if titulo else "")
        st.markdown(f"<div class='titulo-caja t-{tipo}'>{cab}</div>", unsafe_allow_html=True)
        yield


def texto_caja(tipo: str, md: str, titulo: str | None = None):
    with caja(tipo, titulo):
        st.markdown(md)


def tarjeta(titulo: str, cuerpo: str, num: str | None = None, progreso: float | None = None, alto: int | None = None):
    barra = (f"<div class='barra'><div style='width:{max(0, min(100, progreso * 100)):.0f}%'></div></div>"
             if progreso is not None else "")
    n = f"<div class='num'>{num}</div>" if num else ""
    estilo = f" style='min-height:{alto}px'" if alto else ""
    st.markdown(f"<div class='tarjeta'{estilo}>{n}<h4>{titulo}</h4><div class='mini'>{cuerpo}</div>{barra}</div>",
                unsafe_allow_html=True)
