"""Explica en español, con cariño y con la línea exacta, los errores típicos de un programa en Python."""
from __future__ import annotations

import re

_COND = re.compile(r"^\s*(if|elif|while)\b(.*):\s*(#.*)?$")


def _asignacion_en_condicion(cond: str) -> bool:
    sin_textos = re.sub(r"(\"[^\"]*\"|'[^']*')", "", cond)
    return bool(re.search(r"(?<![=!<>:])=(?!=)", sin_textos))


def _print_sin_comillas(linea: str) -> bool:
    m = re.search(r"\bprint\((.*)\)\s*$", linea)
    if not m:
        return False
    arg = m.group(1).strip()
    if not arg or arg[0] in "\"'" or re.match(r"^[fFrRbB]{1,2}[\"']", arg):
        return False
    if re.match(r"^[fF]\{", arg):
        return True
    # palabras sueltas separadas por espacios, sin comas ni operadores → texto sin comillas
    return bool(re.match(r"^[\wáéíóúñÁÉÍÓÚÑ{}]+(\s+[\wáéíóúñÁÉÍÓÚÑ{}]+)+$", arg))


def revisar_lineas(codigo: str) -> list[str]:
    """Busca en TODAS las líneas los despistes más típicos (Python solo avisa del primero)."""
    avisos = []
    for n, linea in enumerate(codigo.splitlines(), 1):
        m = _COND.match(linea)
        if m and _asignacion_en_condicion(m.group(2)):
            avisos.append(f"**Línea {n}** · `{linea.strip()}` → para **comparar** se usa `==` (doble igual). "
                          "Un solo `=` sirve para **guardar** un valor en una variable. "
                          "Como en la vida real: «x = 5» es *meter 5 en la caja x*; «x == 5» es *preguntar si la caja tiene un 5*.")
        if _print_sin_comillas(linea):
            arg = re.search(r"\bprint\((.*)\)\s*$", linea).group(1).strip()
            f = arg.startswith(("f", "F")) and "{" in arg
            texto = arg[1:] if f else arg
            arreglo = f'print(f"{texto}")' if f or "{" in texto else f'print("{texto}")'
            avisos.append(f"**Línea {n}** · `{linea.strip()}` → el texto tiene que ir **entre comillas**. "
                          f"Así: `{arreglo}`. La `f` va pegada a las comillas y dentro, entre llaves, las variables.")
        if re.match(r"^\s*(if|elif|else|while|for|def)\b[^:#]*$", linea) and not linea.rstrip().endswith(":") \
                and not linea.rstrip().endswith(("(", ",", "\\")):
            avisos.append(f"**Línea {n}** · `{linea.strip()}` → te falta **los dos puntos `:`** al final.")
    return avisos


def _sintaxis(exc: SyntaxError) -> str:
    msg = exc.msg or ""
    linea = (exc.text or "").rstrip("\n")
    donde = f"**Línea {exc.lineno}**" + (f" · `{linea.strip()}`" if linea.strip() else "")
    if isinstance(exc, IndentationError) or "indent" in msg:
        if "expected an indented block" in msg:
            explica = "después de una línea que acaba en `:` (if, for, while, def…) lo de dentro va **sangrado** (4 espacios)."
        elif "unindent does not match" in msg:
            explica = "la sangría no cuadra con las líneas de arriba: usa siempre **4 espacios** por nivel y no mezcles tabuladores."
        else:
            explica = "esta línea tiene **espacios de más** al principio. En Python la sangría manda: solo se sangra lo que va dentro de un bloque."
    elif "'=='" in msg:
        explica = "para comparar se usa `==`; un solo `=` es para guardar un valor."
    elif "forgot a comma" in msg or "invalid syntax" in msg and "print" in linea:
        explica = "Python no entiende lo de dentro del paréntesis. Casi siempre es un **texto sin comillas**: `print(\"hola\")`, o con variables `print(f\"{x} es positivo\")`."
    elif "expected ':'" in msg:
        explica = "falta **`:`** al final de la línea (if, elif, else, for, while y def acaban en dos puntos)."
    elif "unterminated string" in msg or "EOL" in msg:
        explica = "abres unas comillas y **no las cierras**."
    elif "was never closed" in msg or "unmatched" in msg or "does not match" in msg:
        explica = "los **paréntesis/corchetes no cuadran**: cuenta los que abres y los que cierras."
    elif "invalid decimal literal" in msg:
        explica = "hay un número pegado a letras (¿una variable que empieza por número o un texto sin comillas?)."
    else:
        explica = f"Python dice: *{msg}*."
    return f"{donde} → {explica}"


def explicar_error_ejecucion(ultima: str, entrada: str = "") -> str:
    """Traduce la última línea de un error (traceback) a algo comprensible."""
    m = re.match(r"ValueError: invalid literal for int\(\) with base 10: '(.*)'", ultima)
    if m:
        v = m.group(1)
        if re.fullmatch(r"-?\d+[.,]\d*", v.strip()):
            return f"`int()` no acepta decimales como `{v}`: usa **`float(input())`** para admitir números con coma."
        return f"`int()` no puede convertir `{v}` en número entero."
    m = re.match(r"ValueError: could not convert string to float: '(.*)'", ultima)
    if m:
        return f"`float()` no puede convertir `{m.group(1)}` (¿has usado coma decimal? En Python es punto: 2.5)."
    m = re.match(r"NameError: name '(.*)' is not defined", ultima)
    if m:
        return f"usas `{m.group(1)}` pero no existe: ¿la has creado antes?, ¿mayúsculas/minúsculas?, ¿un texto sin comillas?"
    if ultima.startswith("TypeError") and ("concatenate" in ultima or "unsupported operand" in ultima):
        return "mezclas **texto y números** en una operación: convierte con `int()`/`float()` o usa una f-string."
    if ultima.startswith("ZeroDivisionError"):
        return "**divides entre 0**: comprueba antes que el divisor no sea 0."
    if ultima.startswith("EOFError"):
        return "tu programa pide **más `input()`** de los datos que hay en la prueba."
    if ultima.startswith("IndexError"):
        return "accedes a una **posición que no existe** de la lista (recuerda: empiezan en 0 y la última es len-1)."
    if ultima.startswith("RecursionError"):
        return "la recursión **no termina**: falta el caso base o no te acercas a él."
    return ultima


def diagnosticar(codigo: str) -> tuple[str, bool]:
    """(explicación en markdown, hay_error_de_sintaxis)."""
    partes = []
    sintaxis = False
    extra = revisar_lineas(codigo)
    try:
        compile(codigo, "tu programa", "exec")
    except SyntaxError as exc:
        sintaxis = True
        misma = [a for a in extra if a.startswith(f"**Línea {exc.lineno}** ")]
        extra = [a for a in extra if a not in misma]
        partes.append("🚫 **Tu programa no llega a ejecutarse** porque Python no entiende una línea:\n\n- " +
                      (misma[0] if misma else _sintaxis(exc)))
    if extra:
        titulo = "🔎 **Otros despistes que he visto** (corrígelos todos de una vez):" if sintaxis else \
            "🔎 **Ojo con esto:**"
        partes.append(titulo + "\n\n" + "\n".join(f"- {a}" for a in extra))
    return "\n\n".join(partes), sintaxis
