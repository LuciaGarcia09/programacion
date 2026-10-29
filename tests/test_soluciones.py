"""Cada solución de referencia debe pasar sus propias pruebas y cada respuesta debe aceptarse a sí misma."""
import importlib
import pkgutil

import pytest

import contenido
from contenido.base import Hoja
from core.corrector import corregir, comprobar


def hojas():
    out = []
    for m in pkgutil.iter_modules(contenido.__path__):
        if m.name.startswith("ej_"):
            mod = importlib.import_module(f"contenido.{m.name}")
            out += [v for v in vars(mod).values() if isinstance(v, Hoja)]
    return out


EJ = [(h.id, e) for h in hojas() for e in h.ejercicios]


@pytest.mark.parametrize("hid,e", EJ, ids=[e.id for _, e in EJ])
def test_programa(hid, e):
    if not e.programa or not e.programa.solucion:
        pytest.skip("sin programa")
    res, msgs = corregir(e.programa.solucion, e.programa)
    malos = [(r.descripcion, r.detalle, r.obtenido) for r in res if not r.ok]
    assert not malos, malos


@pytest.mark.parametrize("hid,e", EJ, ids=[e.id for _, e in EJ])
def test_respuestas(hid, e):
    for r in e.respuestas:
        v = r.valor[0] if isinstance(r.valor, list) else r.valor
        assert comprobar(r, str(v))[0], (r.etiqueta, v)


def test_ids_unicos():
    ids = [e.id for _, e in EJ]
    assert len(ids) == len(set(ids))
