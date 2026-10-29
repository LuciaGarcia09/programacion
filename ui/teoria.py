"""Renderizado de la teoría, progreso guardado y buscador."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import re
import unicodedata

import streamlit as st

from ui.estilo import caja, ICONOS

RUTA_PROGRESO = os.environ.get("PROGLUCIA_PROGRESO") or os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                                    "progreso.json")


# ======================================================================== modelo
@dataclass
class Seccion:
    id: str
    titulo: str
    referencia: str                 # «apartados 1–5» o «§2.1 de los apuntes»
    bloques: list                   # (tipo, titulo, markdown)
    herramienta: str | None = None  # nombre de la pestaña donde practicarlo


@dataclass
class Tema:
    id: str
    asignatura: str
    numero: int
    titulo: str
    resumen: str
    secciones: list[Seccion] = field(default_factory=list)


def S(id_, titulo, referencia, bloques, herramienta=None):
    return Seccion(id_, titulo, referencia, bloques, herramienta)


# ======================================================================== progreso
def _cargar():
    if "progreso" not in st.session_state:
        try:
            with open(RUTA_PROGRESO, encoding="utf-8") as f:
                st.session_state.progreso = json.load(f)
        except Exception:  # noqa: BLE001
            st.session_state.progreso = {}
    return st.session_state.progreso


def _guardar():
    try:
        with open(RUTA_PROGRESO, "w", encoding="utf-8") as f:
            json.dump(st.session_state.progreso, f, ensure_ascii=False, indent=1)
    except Exception:  # noqa: BLE001
        pass  # (si no se puede escribir, el progreso dura lo que dure la sesión)


# El servidor de Streamlit Cloud se reinicia (y borra progreso.json) cada vez que se actualiza la app,
# así que el progreso se guarda también en el navegador (localStorage), que sí dura entre sesiones.
_JS_ALMACEN = """
export default function(component) {
    const { data, setStateValue } = component;
    const CLAVE = "proglucia_progreso";
    let guardado = "{}";
    try { guardado = window.localStorage.getItem(CLAVE) || "{}"; } catch (e) {}
    if (data && data.modo === "leer") {
        setStateValue("guardado", guardado);
    } else if (data && data.modo === "escribir" && data.progreso && data.progreso !== guardado) {
        try { window.localStorage.setItem(CLAVE, data.progreso); } catch (e) {}
    }
}
"""
_almacen = []


def fusionar(guardado: dict) -> int:
    """Añade al progreso lo marcado en otra sesión (nunca desmarca nada). Devuelve cuántas marcas nuevas.
    Debe llamarse ANTES de dibujar los interruptores (al principio de la página)."""
    p = _cargar()
    nuevas = 0
    for k, v in (guardado or {}).items():
        if v and not p.get(k):
            p[k] = v
            nuevas += 1
    if nuevas:
        _guardar()
    for k, v in p.items():                # los interruptores muestran lo recuperado
        st.session_state["tg_ej_" + k[3:] if k.startswith("ej/") else "tg_" + k] = bool(v)
    return nuevas


def _componente():
    import streamlit.components.v2 as v2
    if not _almacen:
        _almacen.append(v2.component("proglucia_almacen", js=_JS_ALMACEN))
    return _almacen[0]


def leer_del_navegador():
    """Al principio de cada carga: recupera (una vez por sesión) el progreso guardado en este navegador."""
    if st.session_state.get("_almacen_listo"):
        return
    try:
        res = _componente()(key="almacen_leer", data={"modo": "leer"}, on_guardado_change=lambda: None)
        valor = getattr(res, "guardado", None)
    except Exception:  # noqa: BLE001  (sin navegador: tests)
        return
    if valor is not None:
        try:
            fusionar(json.loads(valor))
        except (ValueError, AttributeError):
            pass
        st.session_state["_almacen_listo"] = True


def guardar_en_navegador():
    """Al final de cada carga: copia el progreso al navegador (cuando ya se ha leído lo anterior)."""
    if not st.session_state.get("_almacen_listo"):
        return
    try:
        _componente()(key="almacen_escribir", data={"modo": "escribir",
                                                    "progreso": json.dumps(_cargar(), sort_keys=True)})
    except Exception:  # noqa: BLE001
        pass


def progreso_tema(tema: Tema) -> float:
    p = _cargar()
    if not tema.secciones:
        return 0.0
    return sum(1 for s in tema.secciones if p.get(f"{tema.id}/{s.id}")) / len(tema.secciones)


def marcar(clave: str, valor: bool):
    p = _cargar()
    p[clave] = valor
    _guardar()


# ======================================================================== renderizado
_n_bloque = [0]


def _bloque(tipo, titulo, md, extra=()):
    if tipo in ("py", "c", "mips"):
        from ui.codigo import bloque_ejecutable
        _n_bloque[0] += 1
        entrada = extra[0] if extra else ""
        disp = extra[1] if len(extra) > 1 else None
        bloque_ejecutable(tipo, titulo, md, entrada, disp, clave=f"{st.session_state.get('_tema_actual', '')}_{_n_bloque[0]}")
        return
    if tipo == "demo":
        with st.expander("🔍 Demostración" + (f" · {titulo}" if titulo else ""), expanded=False):
            st.markdown(md)
        return
    if tipo == "latex":
        st.latex(md)
        return
    if tipo == "texto":
        st.markdown(md)
        return
    with caja(tipo, titulo):
        st.markdown(md)


def mostrar_tema(tema: Tema, herramientas: list[str] | None = None):
    """Muestra el índice de secciones y la sección elegida."""
    p = _cargar()
    if not tema.secciones:
        st.info("La teoría de este tema está en camino.")
        return
    clave = f"sec_{tema.id}"
    ids = [s.id for s in tema.secciones]
    if st.session_state.get(clave) not in ids:
        st.session_state[clave] = ids[0]
    etiquetas = {s.id: ("✅ " if p.get(f"{tema.id}/{s.id}") else "") + s.titulo for s in tema.secciones}
    hecho = progreso_tema(tema)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"**Índice del tema** · {len(tema.secciones)} secciones")
    with c2:
        st.progress(hecho, text=f"{hecho * 100:.0f} % entendido")
    elegido = st.pills("Sección", ids, format_func=lambda i: etiquetas[i], key=f"pills_{tema.id}",
                       default=st.session_state[clave], label_visibility="collapsed")
    if elegido and elegido != st.session_state[clave]:
        st.session_state[clave] = elegido
    sec = next(s for s in tema.secciones if s.id == st.session_state[clave])
    st.session_state["_tema_actual"] = f"{tema.id}_{sec.id}"
    _n_bloque[0] = 0
    st.markdown(f"### {sec.titulo}")
    st.caption(f"📎 {sec.referencia}")
    for b in sec.bloques:
        if len(b) == 2:
            tipo, titulo, md, extra = b[0], None, b[1], ()
        else:
            tipo, titulo, md, extra = b[0], b[1], b[2], tuple(b[3:])
        _bloque(tipo, titulo, md, extra)
    if sec.herramienta:
        from ui.herramientas import boton_herramienta
        boton_herramienta(sec.herramienta, f"h_{tema.id}_{sec.id}")
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    i = ids.index(sec.id)
    with c1:
        if i > 0 and st.button("← Anterior", key=f"ant_{tema.id}_{sec.id}", width="stretch"):
            st.session_state[clave] = ids[i - 1]
            st.session_state.pop(f"pills_{tema.id}", None)
            st.rerun()
    with c2:
        k = f"{tema.id}/{sec.id}"
        if f"tg_{k}" not in st.session_state:
            st.session_state[f"tg_{k}"] = bool(p.get(k))
        st.toggle("💗 Esta sección ya la entiendo", key=f"tg_{k}",
                  on_change=lambda: marcar(k, st.session_state[f"tg_{k}"]))
    with c3:
        if i < len(ids) - 1 and st.button("Siguiente →", key=f"sig_{tema.id}_{sec.id}", width="stretch", type="primary"):
            st.session_state[clave] = ids[i + 1]
            st.session_state.pop(f"pills_{tema.id}", None)
            st.rerun()


# ======================================================================== buscador
def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def buscar(temas: list[Tema], consulta: str, maximo: int = 40):
    q = _norm(consulta).strip()
    if len(q) < 2:
        return []
    palabras = q.split()
    res = []
    for t in temas:
        for s in t.secciones:
            texto_sec = " ".join([s.titulo, s.referencia] + [" ".join(str(x) for x in b[1:3] if x) for b in s.bloques])
            crudo = re.sub(r"\s+", " ", texto_sec)
            n = _norm(crudo)
            if all(w in n for w in palabras):
                puntos = sum(n.count(w) for w in palabras) + (5 if all(w in _norm(s.titulo) for w in palabras) else 0)
                i = n.find(palabras[0])
                frag = crudo[max(0, i - 80): i + 160]
                res.append((puntos, t, s, frag))
    res.sort(key=lambda r: -r[0])
    return res[:maximo]
