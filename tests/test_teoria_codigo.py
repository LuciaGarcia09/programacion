"""Todos los ejemplos ejecutables de la teoría funcionan de verdad."""
import pytest

from contenido.indice import TODOS_TEMAS
from ui.codigo import ejecutar_c, ejecutar_mips, ejecutar_python

BLOQUES = [(t.id, s.id, k, b) for t in TODOS_TEMAS for s in t.secciones for k, b in enumerate(s.bloques)
           if b[0] in ("py", "c", "mips")]
FALLOS_A_PROPOSITO = {"desbordamiento", "overflow"}


@pytest.mark.parametrize("tid,sid,k,b", BLOQUES, ids=[f"{a}-{b}-{c}" for a, b, c, _ in BLOQUES])
def test_ejemplo(tid, sid, k, b):
    tipo, codigo = b[0], b[2]
    entrada = b[3] if len(b) > 3 else ""
    if tipo == "py":
        out, err, rc = ejecutar_python(codigo, entrada)
        assert rc == 0, err
    elif tipo == "c":
        out, err, rc, msgs = ejecutar_c(codigo, entrada)
        assert rc is not None, msgs
        if not any(t in (b[1] or "") for t in ("Encuentra los 3 errores", "sin break", "Intenta cambiarlo")):
            assert "warning" not in msgs, msgs
    else:
        res, err = ejecutar_mips(codigo, entrada, b[4] if len(b) > 4 else None)
        assert err is None, err
        assert res.termino or any(p in res.motivo for p in FALLOS_A_PROPOSITO), res.motivo
