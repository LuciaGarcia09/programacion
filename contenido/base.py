"""Modelos de datos de la teoría y de las hojas de ejercicios."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Respuesta:
    """Una respuesta que la app puede corregir sola."""
    etiqueta: str
    valor: object                 # número, texto o lista de textos aceptados
    tipo: str = "num"             # num | texto | hex | bin
    tolerancia: float = 1e-6      # relativa para 'num'


@dataclass
class Prueba:
    entrada: str = ""             # lo que se teclea (una línea por dato)
    salida: str | None = None     # lo que debe imprimir (ver corrector.salida_coincide)
    regs: dict | None = None      # registros que deben valer algo al terminar (MIPS): {"$v0": 5050}
    memoria: dict | None = None   # {"etiqueta" o "etiqueta+desp": [palabras]}
    descripcion: str = ""
    preparar: dict | None = None  # registros iniciales (MIPS)
    dispositivos: object = None   # función que crea los dispositivos simulados (E/S)
    main: str | None = None       # main de prueba (MIPS): sustituye al main de la alumna
    mem_inicial: dict | None = None   # memoria que se rellena antes de ejecutar
    modo: str = "tokens"          # tokens | texto | sin_espacios
    infinito: bool = False        # el programa no termina nunca (bucle de E/S): se para tras max_pasos
    max_pasos: int = 3_000_000
    verificar: object = None      # MIPS: función(dispositivos, resultado); C/Python: función(salida) → lista de fallos
    ficheros: dict | None = None  # ficheros que existen antes de ejecutar (C/Python): {"nombre": "contenido"}


@dataclass
class Programa:
    lenguaje: str                 # mips | c | python
    pruebas: list
    plantilla: str = ""
    solucion: str = ""            # código de referencia (se ejecuta en los tests)
    anexo: str | None = None      # código que la app añade (p. ej. una función ya hecha)
    anexo_si_falta: str | None = None   # …solo si la alumna no ha definido esta etiqueta


@dataclass
class Ejercicio:
    id: str
    titulo: str
    enunciado: str
    solucion: str
    pista: str = ""
    errata: str | None = None
    respuestas: list = field(default_factory=list)
    programa: Programa | None = None
    herramienta: str | None = None
    origen: str = ""
    tema: str = ""


@dataclass
class Hoja:
    id: str
    titulo: str
    asignatura: str               # fc | c | py
    fuente: str
    descripcion: str
    ejercicios: list
    icono: str = "📝"
