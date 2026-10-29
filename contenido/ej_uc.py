from contenido.base import Ejercicio, Hoja, Respuesta

R = Respuesta

LEYENDA = r"""
<details><summary>📘 Chuleta de señales de WepSIM (pulsa para verla)</summary>

| Señal | Qué hace |
|---|---|
| **T2** · **C0** | PC → bus interno · cargar MAR desde el bus |
| **Ta** | MAR → bus de direcciones (para leer/escribir memoria) |
| **R** / **W** · **BW = 11** | leer / escribir memoria · tamaño palabra (4 bytes) |
| **M1 = 1** · **C1** | MBR toma el dato de la memoria (M1 = 0: del bus interno) · cargar MBR |
| **Td** | MBR → bus de datos (para escribir en memoria) |
| **T1** | MBR → bus interno |
| **M2 = 1** · **C2** | PC ← PC + 4 (M2 = 0: PC ← bus interno) · cargar PC |
| **C3** | cargar IR desde el bus |
| **T3** + Size, Offset, SE | un trozo del IR (Size bits desde el bit Offset, con extensión de signo si SE = 1) → bus |
| **RA**, **RB** · **T9**, **T10** | registros que salen por las puertas A y B del banco · A → bus, B → bus |
| **RC** + **LC** | escribir el registro RC del banco con lo que haya en el bus |
| **C4**/**C5** · **T4**/**T5** | cargar RT1/RT2 desde el bus · RT1/RT2 → bus |
| **MA** | entrada A de la ALU: 0 = puerta A del banco, 1 = RT1 |
| **MB** | entrada B de la ALU: 00 = puerta B, 01 = RT2, 10 = constante 4, 11 = constante 1 |
| **Cop** · **T6** · **C6**/**T7** | operación de la ALU · resultado → bus · cargar RT3 / RT3 → bus |
| **SelP**, **M7**, **C7** · **T8** | actualizar los bits de estado (C V N Z) en SR · SR → bus |

**Fetch** (memoria de 1 ciclo): `MAR ← PC` (T2, C0) → `MBR ← MP[MAR], PC ← PC + 4` (Ta, R, BW = 11, M1, C1, M2, C2)
→ `IR ← MBR` (T1, C3) → decodificar. Con memoria de 2 ciclos, la lectura repite (Ta, R, BW) un ciclo más.

💡 **Regla de oro:** en un mismo ciclo **solo puede haber una cosa encima del bus interno** (una sola señal T que lo
use), pero se pueden cargar varios registros a la vez desde él y usar los buses externos en paralelo.
</details>
"""


def tabla(filas):
    t = "| Ciclo | Operación elemental | Señales activas |\n|---|---|---|\n"
    return t + "\n".join(f"| {k} | {op} | {s} |" for k, (op, s) in enumerate(filas, 1)) + "\n"


FETCH1 = [("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4", "Ta, R, BW = 11, M1, C1, M2, C2"),
          ("IR ← MBR", "T1, C3"), ("Decodificación", "C ← 0 (salto a la rutina de la instrucción)")]
FETCH2 = [("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4 (1.er ciclo de memoria)", "Ta, R, BW = 11, M2, C2"),
          ("MBR ← MP[MAR] (2.º ciclo)", "Ta, R, BW = 11, M1, C1"), ("IR ← MBR", "T1, C3"), ("Decodificación", "—")]

HOJA = Hoja("uc", "Unidad de control y procesador (WepSIM)", "fc", "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "Operaciones elementales y señales de control en WepSIM, MIPS y CPI, interrupciones.", [

Ejercicio("uc-1", "lw R1, (R2) y rendimiento a 500 MHz",
r"""Procesador de 32 bits a **500 MHz** con la estructura WepSIM; memoria por bytes con **2 ciclos** por lectura o escritura.
a) Operaciones elementales de `lw R1, (R2)`. b) Si el CPI medio es 25, ¿cuántas instrucciones ejecuta por segundo?""" + LEYENDA,
r"""**a)** Fetch (memoria de 2 ciclos) y luego la ejecución:

""" + tabla(FETCH2 + [("MAR ← R2", "RA = R2, T9, C0"), ("MBR ← MP[MAR] (1.er ciclo)", "Ta, R, BW = 11"),
                      ("MBR ← MP[MAR] (2.º ciclo)", "Ta, R, BW = 11, M1, C1"), ("R1 ← MBR", "T1, RC = R1, LC")]) + r"""
(y vuelta al fetch). `(R2)` es **indirecto a registro**: la dirección está en R2.

**b)** $\dfrac{f}{CPI} = \dfrac{500\cdot10^6}{25} = 20\cdot10^6$ → **20 millones de instrucciones por segundo (20 MIPS)**.""",
respuestas=[R("b) instrucciones/s", 20e6)], herramienta="Rendimiento"),

Ejercicio("uc-2", "MIPS de dos computadores",
r"""A: 1 GHz y CPI = 8. B: 2,5 GHz y CPI = 30. a) ¿Qué representa MIPS? b) Calcúlelo para A y B. c) Un programa en C
compila a 5000 instrucciones en A y a 7000 en B. ¿En qué máquina se ejecuta antes (cada instrucción una vez)?""",
r"""**a)** **MIPS = millones de instrucciones por segundo**: $MIPS = \dfrac{f}{CPI\cdot10^6}$. Mide la velocidad a la que se
ejecutan instrucciones (no sirve para comparar máquinas con repertorios distintos: una instrucción no hace lo mismo en todas).

**b)** $MIPS_A = \dfrac{1000}{8} =$ **125** · $MIPS_B = \dfrac{2500}{30} \approx$ **83,3**.

**c)** $T = \dfrac{N\cdot CPI}{f}$:
- A: $\dfrac{5000\cdot8}{10^9} = 40\ \mu s$
- B: $\dfrac{7000\cdot30}{2{,}5\cdot10^9} = 84\ \mu s$

Se ejecuta antes en **A** (2,1 veces más rápido), aunque su reloj sea más lento.""",
respuestas=[R("MIPS de A", 125), R("MIPS de B", 2500 / 30, tolerancia=1e-3), R("Tiempo en A (µs)", 40),
            R("Tiempo en B (µs)", 84), R("¿Más rápida? (A/B)", ["a"], "texto")], herramienta="Rendimiento"),

Ejercicio("uc-3", "Duplicar los MIPS sin tocar el reloj",
r"""Computador a 0,5 GHz con CPI = 10. a) ¿Qué es MIPS? b) Calcúlelo. c) ¿Qué habría que hacer para obtener el doble de MIPS
manteniendo la frecuencia?""",
r"""**a)** Millones de instrucciones por segundo.

**b)** $MIPS = \dfrac{500}{10} =$ **50**.

**c)** Como $MIPS = f/CPI$, con la misma $f$ hay que **reducir el CPI a la mitad: CPI = 5** (instrucciones con menos
ciclos: memoria más rápida, unidad de control con menos ciclos por instrucción, segmentación…).""",
respuestas=[R("b) MIPS", 50), R("c) CPI necesario", 5)], herramienta="Rendimiento"),

Ejercicio("uc-4", "CPI a 1 GHz y 200 MIPS",
r"""Procesador de 32 bits a 1 GHz (estructura WepSIM, memoria de 2 ciclos) que ejecuta **200 MIPS**. ¿CPI medio?""",
r"""$CPI = \dfrac{f}{MIPS\cdot10^6} = \dfrac{1000}{200} =$ **5 ciclos por instrucción**.""",
respuestas=[R("CPI", 5)], herramienta="Rendimiento"),

Ejercicio("uc-5", "CPI a 1,6 GHz y 850 MIPS",
r"""Procesador a 1,6 GHz y 850 MIPS. Calcule el CPI.""",
r"""$CPI = \dfrac{1600}{850} \approx$ **1,88**.""",
respuestas=[R("CPI", 1600 / 850, tolerancia=2e-3)], herramienta="Rendimiento"),

Ejercicio("uc-6", "¿Qué instrucción hacen estas señales?",
r"""Señales activas en cada ciclo (sin el fetch; el resto a 0):
- C1: T3, C0, Size = 10000, Offset = 00000
- C2: R, Ta, BW = 11
- C3: R, Ta, BW = 11, M1, C1
- C4: RC = 00010, T1, LC

a) Operaciones elementales de cada ciclo. b) ¿A qué instrucción máquina corresponden?""" + LEYENDA,
r"""**a)**

| Ciclo | Señales | Operación elemental |
|---|---|---|
| C1 | T3 con Size = 16, Offset = 0 · C0 | **MAR ← IR(15:0)** (los 16 bits bajos de la instrucción) |
| C2 | R, Ta, BW = 11 | **MBR ← MP[MAR]**, primer ciclo de lectura |
| C3 | R, Ta, BW = 11, M1, C1 | segundo ciclo: el dato llega y **se carga en MBR** |
| C4 | T1, RC = 2, LC | **R2 ← MBR** |

**b)** Carga en R2 una palabra de memoria cuya dirección va en la propia instrucción → **`lw R2, dir`**
(direccionamiento **directo/absoluto**, con dir de 16 bits). La memoria tarda 2 ciclos.""",
respuestas=[R("Registro destino (número)", 2)]),

Ejercicio("uc-7", "SWAP R1, dir (dos palabras)",
r"""Indique las operaciones elementales de `SWAP R1, dir` (ocupa dos palabras: CO + Reg en la primera, dir en la segunda),
que intercambia el registro con la posición de memoria dir.""" + LEYENDA,
r"""Tras el fetch, el PC ya apunta a la **segunda palabra** (dir). Hay que leerla, leer el dato, y cruzar los valores
usando **RT1** como «vaso auxiliar» (como al intercambiar dos vasos de agua con un tercero).

""" + tabla([("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4", "Ta, R, BW = 11, M1, C1, M2, C2"),
             ("MAR ← MBR (dir)", "T1, C0"), ("MBR ← MP[MAR]", "Ta, R, BW = 11, M1, C1"),
             ("RT1 ← MBR (dato de memoria)", "T1, C4"), ("MBR ← R1", "RA = R1, T9, C1 (M1 = 0)"),
             ("MP[MAR] ← MBR, R1 ← RT1", "Ta, Td, W, BW = 11 · T4, RC = R1, LC")]) + r"""
El último ciclo combina dos cosas porque no chocan: la escritura usa los buses **externos** y `R1 ← RT1` el **interno**.
(Si la memoria tarda más de un ciclo, cada acceso se alarga.)"""),

Ejercicio("uc-8", "sw $t1, 80($t2)",
r"""Computador de 32 bits (WepSIM), 32 registros, memoria de 2 ciclos. a) Modos de direccionamiento de `sw $t1, 80($t2)`.
b) Operaciones elementales y señales.""" + LEYENDA,
r"""**a)** `$t1`: **directo a registro** (el dato está en el registro). `80($t2)`: **relativo a registro base**
(dirección = $t2 + 80).

**b)** Tras el fetch y la decodificación ($t1 = registro 9, $t2 = registro 10):

""" + tabla([("RT2 ← IR(15:0) = 80 (con signo)", "T3, Size = 10000, Offset = 00000, SE = 1, C5"),
             ("MAR ← $t2 + RT2", "RA = 01010, MA = 0, MB = 01, Cop = ADD, T6, C0"),
             ("MBR ← $t1", "RA = 01001, T9, C1 (M1 = 0)"),
             ("MP[MAR] ← MBR (1.er ciclo)", "Ta, Td, W, BW = 11"), ("MP[MAR] ← MBR (2.º ciclo)", "Ta, Td, W, BW = 11")]) +
"\nY se vuelve al fetch. El desplazamiento se extiende con signo porque podría ser negativo (p. ej. `-4($sp)`)."),

Ejercicio("uc-9", "ADD R1, dirección (registro + memoria)",
r"""Computador de 32 bits (WepSIM), 32 registros, memoria de 2 ciclos, 100 instrucciones; `ADD R1, dirección` hace
R1 ← R1 + MP[dirección], con dirección de 32 bits. a) Formato. b) Operaciones elementales y señales.""" + LEYENDA,
r"""**a)** CO: $\lceil\log_2 100\rceil = 7$ bits; registro: 5 bits; dirección: 32 bits → $7+5+32 = 44$ → **2 palabras**:
palabra 1 = CO (7) | R1 (5) | 20 sin usar; palabra 2 = dirección.

**b)** Tras el fetch:

""" + tabla([("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4", "Ta, R, BW = 11, M2, C2"),
             ("(2.º ciclo de lectura)", "Ta, R, BW = 11, M1, C1"), ("MAR ← MBR", "T1, C0"),
             ("MBR ← MP[MAR]", "Ta, R, BW = 11"), ("(2.º ciclo de lectura)", "Ta, R, BW = 11, M1, C1"),
             ("RT2 ← MBR", "T1, C5"),
             ("R1 ← R1 + RT2", "RA = R1, MA = 0, MB = 01, Cop = ADD, T6, RC = R1, LC, SelP = 11, M7, C7")]),
respuestas=[R("Bits de CO", 7), R("Palabras", 2)]),

Ejercicio("uc-10", "¿Cuánto más rápido?",
r"""A ejecuta un programa en 10 s y B en 15 s. ¿Qué afirmación es cierta? a) A es un 50 % más rápido que B.
b) A es un 33 % más rápido que B.""",
r"""«Más rápido» se mide con el **speedup** = cociente de tiempos: $S = \dfrac{T_B}{T_A} = \dfrac{15}{10} = 1{,}5$ → A es
**un 50 % más rápido** → **a)**.

El 33 % sale de otra cuenta: A tarda un 33 % **menos tiempo** que B ($5/15$), que no es lo mismo que ser un 33 % más rápido.""",
errata="El enunciado dice «más rápido que C» en el apartado b); debe ser «que B».",
respuestas=[R("Afirmación cierta", ["a", "a)"], "texto")], herramienta="Rendimiento"),

Ejercicio("uc-11", "Señales sueltas, addi y addm R1, (R2)",
r"""Procesador WepSIM con 32 registros, 1 ciclo para decodificar y memoria de 1 ciclo; juego de instrucciones MIPS32.
a) Señales para **PC ← R7**. b) ¿Qué hace un ciclo con **T1 y C5**? c) Operaciones y señales (con fetch) de
**addi $t0, $t1, 10**. d) Señales para **RT1 ← R2**. e) Operaciones y señales (con fetch) de **addm R1, (R2)**
(R1 ← R1 + MP[R2]).""" + LEYENDA,
r"""**a)** RA = 00111, **T9** (R7 al bus), **M2 = 0**, **C2** (el PC se carga desde el bus).

**b)** T1 pone MBR en el bus y C5 carga RT2: **RT2 ← MBR**.

**c)** addi $t0, $t1, 10 ($t0 = 8, $t1 = 9):

""" + tabla(FETCH1 + [("RT2 ← IR(15:0) = 10 (con signo)", "T3, Size = 10000, Offset = 00000, SE = 1, C5"),
                      ("$t0 ← $t1 + RT2", "RA = 01001, MA = 0, MB = 01, Cop = ADD, T6, RC = 01000, LC, SelP = 11, M7, C7")]) + r"""
**d)** RA = 00010, **T9**, **C4**.

**e)** addm R1, (R2):

""" + tabla(FETCH1 + [("MAR ← R2", "RA = R2, T9, C0"), ("MBR ← MP[MAR]", "Ta, R, BW = 11, M1, C1"),
                      ("RT2 ← MBR", "T1, C5"),
                      ("R1 ← R1 + RT2", "RA = R1, MA = 0, MB = 01, Cop = ADD, T6, RC = R1, LC, SelP = 11, M7, C7")])),

Ejercicio("uc-12", "swap R1, dir: formato, modos y microoperaciones",
r"""WepSIM de 32 bits, 32 registros, memoria de 1 ciclo, 98 instrucciones, 1 ciclo de decodificación.
`swap R1, dir` intercambia R1 con MP[dir]; dir debe poder ser cualquier dirección válida.
a) Formato. b) Modos de direccionamiento de R1 y dir. c) Operaciones elementales y señales, con fetch.""" + LEYENDA,
r"""**a)** CO: $\lceil\log_2 98\rceil = 7$ bits; R1: 5 bits; dir: **32 bits** (cualquier dirección) → **2 palabras**:
palabra 1 = CO (7) | R1 (5) | 20 sin usar; palabra 2 = dir.

**b)** R1: **directo a registro**; dir: **directo (absoluto) a memoria**.

**c)**

""" + tabla(FETCH1 + [("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4", "Ta, R, BW = 11, M1, C1, M2, C2"),
                      ("MAR ← MBR (dir)", "T1, C0"), ("MBR ← MP[MAR]", "Ta, R, BW = 11, M1, C1"),
                      ("RT1 ← MBR", "T1, C4"), ("MBR ← R1", "RA = R1, T9, C1 (M1 = 0)"),
                      ("MP[MAR] ← MBR, R1 ← RT1", "Ta, Td, W, BW = 11 · T4, RC = R1, LC")]) +
"\nY vuelta al fetch. Total: 4 ciclos de fetch + 7 de ejecución = **11 ciclos**.",
respuestas=[R("Bits de CO", 7), R("Palabras", 2), R("Ciclos totales (con fetch)", 11)]),

Ejercicio("uc-13", "Interrupciones: qué son y ciclo de reconocimiento",
r"""WepSIM de 32 bits, memoria de 1 ciclo, 1 ciclo de decodificación, puntero de pila = registro 29, R0 cableado a 0.
a) ¿Qué es una interrupción y por qué se produce? Dos ejemplos. b) ¿Qué hace la unidad de control durante el ciclo de
reconocimiento? Indique las operaciones y señales, sabiendo que la dirección de la rutina de tratamiento está en la
posición de memoria 0.""" + LEYENDA,
r"""**a)** Una **interrupción** es una señal (normalmente de un periférico) que pide al procesador que **suspenda el programa
en curso** para ejecutar una **rutina de tratamiento**, y después lo reanude como si nada. Sirve para no tener que estar
preguntando continuamente a los dispositivos (espera activa).
Ejemplos: se pulsa una tecla, un disco termina una transferencia (DMA), vence el temporizador del sistema operativo,
llega un paquete por la red. (Las **excepciones**, como dividir entre 0 o un desbordamiento, se tratan igual pero las
provoca el propio programa.)

💡 Analogía: estás estudiando y suena el timbre: marcas la página (guardas PC y SR), abres (rutina) y vuelves a la página.

**b)** Al final de una instrucción, si INT está activa y las interrupciones habilitadas, la UC: **1)** guarda el PC y el
registro de estado en la pila, **2)** deshabilita las interrupciones y **3)** carga en el PC la dirección de la rutina.

""" + tabla([("MBR ← PC", "T2, C1 (M1 = 0)"),
             ("MAR ← R29 − 4, R29 ← R29 − 4", "RA = 11101, MA = 0, MB = 10, Cop = SUB, T6, C0, RC = 11101, LC"),
             ("MP[MAR] ← MBR (apila el PC)", "Ta, Td, W, BW = 11"),
             ("MBR ← SR", "T8, C1"),
             ("MAR ← R29 − 4, R29 ← R29 − 4", "RA = 11101, MA = 0, MB = 10, Cop = SUB, T6, C0, RC = 11101, LC"),
             ("MP[MAR] ← MBR (apila SR)", "Ta, Td, W, BW = 11"),
             ("MAR ← R0 (= 0), INTA, se deshabilitan las interrupciones (bit I de SR a 0)", "RA = 00000, T9, C0, INTA"),
             ("MBR ← MP[0]", "Ta, R, BW = 11, M1, C1"),
             ("PC ← MBR (dirección de la rutina)", "T1, M2 = 0, C2")]) +
"\nLa rutina terminará con una instrucción de retorno (tipo `reti`) que desapila SR y PC en orden inverso."),

Ejercicio("uc-14", "reset N, dir: poner a 0 N palabras",
r"""Procesador WepSIM con memoria por bytes; puntero de pila = registro 29 y R0 cableado a 0. `reset N, dir` ocupa dos
palabras: N en los 16 bits bajos de la primera y dir en la segunda. Pone a 0 las N palabras a partir de dir. Si N ≤ 0,
no hace nada. Indique operaciones elementales y señales.""" + LEYENDA,
r"""**Idea:** leer dir (segunda palabra), comprobar N ≤ 0, calcular la dirección final $dir + 4N$ y recorrer con un bucle
del microprograma, saltando según los bits de estado (como un `while` hecho con señales).

Truco: N ≤ 0 ⇔ N − 1 < 0, así que basta mirar el bit **N** del resultado de `RT1 − 1`. Truco 2: las entradas de la ALU
son A (banco o RT1) y B (banco, RT2, 4 o 1), así que dejamos la dirección que avanza en **RT1** (lado A, para sumarle 4)
y la dirección final en **RT2** (lado B, para comparar).

""" + tabla([("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4 (MBR = dir)", "Ta, R, BW = 11, M1, C1, M2, C2"),
             ("RT2 ← MBR (dir)", "T1, C5"),
             ("RT1 ← IR(15:0) (N con signo)", "T3, Size = 10000, Offset = 00000, SE = 1, C4"),
             ("SR ← flags(RT1 − 1)", "MA = 1, MB = 11, Cop = SUB, SelP = 11, M7, C7"),
             ("si N = 1 (es decir, N ≤ 0) → saltar al fetch", "salto condicional del microprograma"),
             ("RT1 ← RT1 · 4", "MA = 1, MB = 10, Cop = MUL, T6, C4"),
             ("RT2 ← RT1 + RT2 (dirección final = dir + 4N)", "MA = 1, MB = 01, Cop = ADD, T6, C5"),
             ("RT1 ← MBR (dirección actual = dir)", "T1, C4"),
             ("MBR ← R0 (= 0)", "RA = 00000, T9, C1 (M1 = 0)"),
             ("**bucle:** MAR ← RT1", "T4, C0"),
             ("MP[MAR] ← MBR, RT1 ← RT1 + 4", "Ta, Td, W, BW = 11 · MA = 1, MB = 10, Cop = ADD, T6, C4"),
             ("SR ← flags(RT1 − RT2)", "MA = 1, MB = 01, Cop = SUB, SelP = 11, M7, C7"),
             ("si Z = 0 → saltar a «bucle»; si no → fetch", "salto condicional del microprograma")]) + r"""
La dir se lee **antes** de comprobar N: aunque no se haga nada, el PC tiene que saltarse la segunda palabra (si no, ¡se
ejecutaría dir como si fuera una instrucción!).""",
errata="El enunciado lista «dir, dir + 4, …, dir + N*4», que son N + 1 direcciones. Las N palabras son dir … dir + (N − 1)·4."),

Ejercicio("uc-15", "PUSHREGS R1, R2, R3",
r"""`PUSHREGS R1, R2, R3` ocupa una palabra y apila R1, luego R2 y luego R3, actualizando el puntero de pila (registro 29).
La ALU puede sumar 4 al operando A. Indique las operaciones elementales.""" + LEYENDA,
r"""Convenio MIPS: la pila crece hacia **direcciones bajas** y $sp apunta a la cima → apilar = **restar 4 y escribir**.
Por cada registro: preparar el dato en MBR, bajar el puntero (y usarlo como dirección) y escribir.

""" + tabla([("MBR ← R1", "RA = R1, T9, C1"),
             ("MAR ← R29 − 4, R29 ← R29 − 4", "RA = 29, MA = 0, MB = 10, Cop = SUB, T6, C0, RC = 29, LC"),
             ("MP[MAR] ← MBR", "Ta, Td, W, BW = 11"),
             ("MBR ← R2", "RA = R2, T9, C1"),
             ("MAR ← R29 − 4, R29 ← R29 − 4", "ídem"),
             ("MP[MAR] ← MBR", "Ta, Td, W, BW = 11"),
             ("MBR ← R3", "RA = R3, T9, C1"),
             ("MAR ← R29 − 4, R29 ← R29 − 4", "ídem"),
             ("MP[MAR] ← MBR", "Ta, Td, W, BW = 11")]) + r"""
R3 queda en la cima. Con la operación «A + 4» del enunciado se haría igual si la pila creciera hacia direcciones altas
(MAR ← R29 + 4, R29 ← R29 + 4). En la práctica, el ciclo «MBR ← R2» puede hacerse a la vez que la escritura anterior
solo si la memoria ya ha capturado el dato; por seguridad se dejan separados."""),

Ejercicio("uc-16", "adds R1, R2: resultado en la cima de la pila",
r"""`adds R1, R2` suma R1 y R2 y deja el resultado en la cima de la pila (haciendo hueco). R1 es el registro 1, R2 el 2 y el
puntero de pila el **16**. Indique operaciones elementales y señales.""" + LEYENDA,
tabla([("MBR ← R1 + R2", "RA = 00001, RB = 00010, MA = 0, MB = 00, Cop = ADD, T6, C1 (M1 = 0), SelP = 11, M7, C7"),
       ("MAR ← R16 − 4, R16 ← R16 − 4", "RA = 10000, MA = 0, MB = 10, Cop = SUB, T6, C0, RC = 10000, LC"),
       ("MP[MAR] ← MBR", "Ta, Td, W, BW = 11")]) +
"\nTres ciclos (más el fetch). La suma va directamente de la ALU al MBR por el bus interno, sin pasar por ningún registro."),

Ejercicio("uc-17", "addm R1, dir (no hace nada si dir = 0)",
r"""`addm R1, dir`: si dir = 0 no hace nada; si no, R1 ← R1 + MP[dir]. a) Formato. b) Operaciones elementales sin el fetch.""" + LEYENDA,
r"""**a)** En un computador de 32 bits con dirección completa: **2 palabras** → palabra 1 = CO | R1 | sin usar;
palabra 2 = dir (32 bits). (Si se aceptan direcciones de 16 bits, cabría en una palabra: CO | R1 | dir.)

**b)**

""" + tabla([("MAR ← PC", "T2, C0"), ("MBR ← MP[MAR], PC ← PC + 4", "Ta, R, BW = 11, M1, C1, M2, C2"),
             ("RT1 ← MBR (dir)", "T1, C4"),
             ("MAR ← RT1 y SR ← flags(RT1 − R0)", "T4, C0 · MA = 1, RB = 00000, MB = 00, Cop = SUB, SelP = 11, M7, C7"),
             ("si Z = 1 → fetch (dir = 0, no se hace nada)", "salto condicional del microprograma"),
             ("MBR ← MP[MAR]", "Ta, R, BW = 11, M1, C1"), ("RT2 ← MBR", "T1, C5"),
             ("R1 ← R1 + RT2", "RA = R1, MA = 0, MB = 01, Cop = ADD, T6, RC = R1, LC, SelP = 11, M7, C7")]) +
"\nLa comparación con 0 se hace restando R0 (cableado a 0) para que la ALU active el bit **Z** si dir vale 0."),
], icono="🎛️")
