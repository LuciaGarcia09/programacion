"""Índice de todas las hojas de ejercicios y de todos los temas de teoría."""
from contenido import (ej_c, ej_cache, ej_ensamblador, ej_es, ej_ilp, ej_intro, ej_jerarquia, ej_multi, ej_python,
                       ej_repr, ej_uc, ej_virtual, t_c, t_fc, t_python)

HOJAS = [ej_intro.HOJA, ej_repr.HOJA, ej_ensamblador.HOJA, ej_uc.HOJA, ej_cache.HOJA, ej_virtual.HOJA, ej_es.HOJA,
         ej_intro.HOJA_ARCOS, ej_ilp.HOJA, ej_jerarquia.HOJA, ej_multi.HOJA,
         ej_c.HOJA,
         ej_python.HOJA_CONTROL, ej_python.HOJA_FUNC, ej_python.HOJA_PROG]

TEMAS = {"fc": t_fc.TEMAS, "c": t_c.TEMAS, "py": t_python.TEMAS}
TODOS_TEMAS = [t for ts in TEMAS.values() for t in ts]
