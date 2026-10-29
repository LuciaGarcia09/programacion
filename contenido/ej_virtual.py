from contenido.base import Ejercicio, Hoja, Respuesta

R = Respuesta

CAMPOS_ENTRADA = r"""| Campo | Para qué sirve |
|---|---|
| **Bit de presencia (válido)** | 1 si la página está en memoria principal; 0 → al acceder hay **fallo de página** |
| **Nº de marco** (o bloque de swap) | dónde está la página en memoria física (o en el disco, si no está presente) |
| **Bit de modificado (sucio)** | 1 si se ha escrito: al expulsarla hay que copiarla al disco |
| **Bit de referencia (acceso)** | se activa al usarla; lo usa el algoritmo de reemplazo (LRU aproximado, reloj…) |
| **Bits de protección** | permisos: lectura / escritura / ejecución, usuario o núcleo |"""

HOJA = Hoja("virtual", "Memoria virtual", "fc", "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "Formato de la dirección virtual, tablas de páginas, traducción a dirección física, fallos de página y TLB.", [

Ejercicio("vm-1", "Páginas de 8 KB y 1 GB de memoria",
r"""Computador de 32 bits con memoria virtual, páginas de 8 KB y 1 GB de memoria principal. a) Formato de la dirección
virtual. b) Número máximo de páginas. c) ¿Qué es un marco de página? d) Número de marcos. e) Tamaño del bloque que se
transfiere entre disco y memoria en un fallo de página.""",
r"""**a)** Desplazamiento: $8\text{ KB} = 2^{13}$ → **13 bits**. Página: $32 - 13 =$ **19 bits**.

| nº de página (19 bits) | desplazamiento (13 bits) |
|---|---|

**b)** $2^{19} =$ **524 288 páginas**.

**c)** Un **marco** es un hueco de la memoria física del tamaño de una página, donde se puede colocar una página.
💡 Analogía: las páginas son libros y los marcos, los huecos de la estantería (la memoria física); el resto de libros está
en el almacén (el disco).

**d)** $\dfrac{2^{30}}{2^{13}} = 2^{17} =$ **131 072 marcos**.

**e)** Se transfiere **una página entera: 8 KB**.""",
respuestas=[R("Bits de página", 19), R("Bits de desplazamiento", 13), R("b) Páginas", 2**19), R("d) Marcos", 2**17),
            R("e) KB transferidos", 8)], herramienta="Memoria virtual"),

Ejercicio("vm-2", "Computador de 20 bits con páginas de 1 KB",
r"""Computador de 20 bits con memoria virtual paginada, páginas de 1 KB y 256 KB de memoria física. a) Formato de la
dirección virtual. b) Nº máximo de entradas de la tabla de páginas (un nivel). c) Nº de marcos. d) Campos de una
entrada de la tabla de páginas y para qué sirven.""",
r"""**a)** Desplazamiento $\log_2 1024 =$ **10 bits**; página $20 - 10 =$ **10 bits**.

**b)** Una entrada por página: $2^{10} =$ **1024 entradas**.

**c)** $256\text{ KB}/1\text{ KB} =$ **256 marcos** (el nº de marco necesita 8 bits).

**d)**
""" + CAMPOS_ENTRADA,
respuestas=[R("Bits de página", 10), R("Bits de desplazamiento", 10), R("b) Entradas", 1024), R("c) Marcos", 256)],
herramienta="Memoria virtual"),

Ejercicio("vm-3", "Tamaño de la tabla y traducción de 0x000023F0",
r"""Direcciones virtuales de 32 bits y páginas de 4 KB. a) Formato de la dirección. b) Con una tabla de un nivel y
entradas de 32 bits, tamaño máximo de la tabla en bytes. c) Con la tabla de páginas (página → marco)
0→20, 1→6, 2→4, 3→8, 4→1, 5→3, 6→5, 7→7, ¿qué dirección física corresponde a la virtual **0x000023F0**?""",
r"""**a)** Desplazamiento $\log_2 4096 =$ **12 bits**; página **20 bits**.

**b)** $2^{20}$ entradas × 4 bytes $= 2^{22}$ B = **4 MB** (¡por cada proceso! Por eso existen las tablas multinivel).

**c)** Con páginas de 4 KB, los **3 últimos dígitos hexadecimales** (12 bits) son el desplazamiento:
- 0x000023F0 → página **0x00002 = 2**, desplazamiento **0x3F0**.
- Tabla: página 2 → marco **4**.
- Dirección física = marco | desplazamiento = **0x000043F0** (= 4·4096 + 1008 = 17 392).

💡 Truco: con páginas de $16^k$ bytes, solo cambias los dígitos de la página y copias tal cual los del desplazamiento.""",
respuestas=[R("b) Bytes de la tabla", 2**22), R("c) Dirección física", "43F0", "hex")], herramienta="Memoria virtual"),

Ejercicio("vm-4", "Tabla con bits de presencia: traducir 0x0000608A",
r"""Páginas de 8 KB, espacio virtual de $2^{32}$ bytes y $2^{23}$ bytes de memoria física. Tabla del programa:

| Página | Presencia | Modificado | Marco / bloque de swap |
|---|---|---|---|
| 0 | 1 | 0 | 1 |
| 1 | 0 | 0 | 7 |
| 2 | 1 | 1 | 9 |
| 3 | 1 | 0 | 14 |
| 4 | 1 | 0 | 8 |
| 5 | 1 | 1 | 3 |
| 6 | 0 | 0 | 25 |
| 7 | 0 | 1 | 16 |
| 8 | 0 | 0 | 23 |
| 9 | 1 | 0 | 78 |

a) Formato de la dirección virtual. b) Dirección física de la virtual **0x0000608A**. c) Tamaño del espacio virtual de
este programa. d) Memoria principal en MB.""",
r"""**a)** Desplazamiento **13 bits** (8 KB); página $32 - 13 =$ **19 bits**.

**b)** Con 13 bits de desplazamiento no se puede cortar por dígitos hex, así que hacemos la división:
$0\text{x}608\text{A} = 24\,714 = 3\cdot8192 + 138$ → **página 3, desplazamiento 138 (0x8A)**.
Página 3: presencia = 1 → está en el **marco 14**.
$$DF = 14\cdot8192 + 138 = 114\,826 = \mathbf{0x1C08A}$$
(En binario: el marco 14 = 1110 delante de los 13 bits del desplazamiento.)

**c)** La tabla tiene 10 entradas → 10 páginas × 8 KB = **80 KB**.

**d)** $2^{23}$ B = **8 MB** (1024 marcos de 8 KB).""",
respuestas=[R("b) Dirección física", "1C08A", "hex"), R("c) KB", 80), R("d) MB", 8)], herramienta="Memoria virtual"),

Ejercicio("vm-5", "Páginas de 2 KB con 32 bits",
r"""Procesador con direcciones virtuales de 32 bits y páginas de 2 KB. Formato de la dirección virtual y número máximo de
páginas de un programa.""",
r"""Desplazamiento $\log_2 2048 =$ **11 bits**; página $32 - 11 =$ **21 bits** → hasta $2^{21} =$ **2 097 152 páginas**.""",
respuestas=[R("Bits de página", 21), R("Bits de desplazamiento", 11), R("Páginas", 2**21)], herramienta="Memoria virtual"),

Ejercicio("vm-6", "Computador de 18 bits con páginas de 4 KB",
r"""Computador de 18 bits, memoria virtual paginada, páginas de 4 KB y 512 KB de memoria física. a) Formato de la
dirección virtual. b) Nº máximo de entradas de la tabla (un nivel). c) Nº de marcos. d) Campos de una entrada.""",
r"""**a)** Desplazamiento **12 bits**; página $18 - 12 =$ **6 bits**.

**b)** $2^6 =$ **64 entradas**.

**c)** $512\text{ KB}/4\text{ KB} =$ **128 marcos**.
⚠️ Curiosidad: ¡la memoria física (512 KB) es mayor que el espacio virtual de un proceso ($2^{18}$ = 256 KB)! Tiene sentido si
hay varios procesos a la vez.

**d)**
""" + CAMPOS_ENTRADA,
respuestas=[R("Bits de página", 6), R("Bits de desplazamiento", 12), R("b) Entradas", 64), R("c) Marcos", 128)],
herramienta="Memoria virtual"),

Ejercicio("vm-7", "Direcciones de 16 bits y páginas de 2 KB",
r"""Direcciones de 16 bits y páginas de 2 KB. ¿Tamaño de la memoria virtual? ¿Cuántas páginas? ¿Tamaño del marco? Con
8 KB de memoria física, ¿cuántos marcos? ¿Cuántos bits seleccionan la entrada de la tabla (un nivel)? ¿Para qué se usan
los demás? ¿Cuántas entradas tiene la tabla?""",
r"""- Memoria virtual: $2^{16}$ B = **64 KB**.
- Páginas: $64/2 =$ **32**.
- Marco: igual que la página, **2 KB**.
- Marcos: $8/2 =$ **4**.
- Bits para la entrada: $\log_2 32 =$ **5 bits** (los de más peso).
- Los otros **11 bits** son el **desplazamiento** dentro de la página (se copian tal cual a la dirección física).
- Entradas: **32** (una por página).""",
respuestas=[R("KB de memoria virtual", 64), R("Páginas", 32), R("KB por marco", 2), R("Marcos", 4),
            R("Bits de la entrada", 5), R("Entradas", 32)], herramienta="Memoria virtual"),

Ejercicio("vm-8", "Página y desplazamiento de 0x20018004",
r"""Páginas de 8 KB y memoria direccionada por bytes. Dada la dirección virtual **0x20018004**, indique el tamaño de la
dirección virtual, el número de página y el desplazamiento.""",
r"""La dirección tiene 8 dígitos hex → **32 bits**. Desplazamiento: **13 bits** → página: 19 bits.

$0\text{x}20018004 = 0010\,0000\,0000\,0001\,100|0\,0000\,0000\,0100$:
- Desplazamiento (13 bits bajos): $0\,0000\,0000\,0100$ = **4**.
- Página (19 bits altos): $0010\,0000\,0000\,0001\,100 = $ **0x1000C = 65 548**.

Comprobación: $65\,548\cdot8192 + 4 = 536\,969\,220 = $ 0x20018004 ✓.""",
respuestas=[R("Página (decimal)", 65548), R("Desplazamiento", 4)], herramienta="Memoria virtual"),

Ejercicio("vm-9", "256 Kpáginas de 8 KB",
r"""Espacio virtual de 256 Kpáginas de 8 KB y memoria física de 128 MB. ¿Cuántos bits tiene la dirección virtual?""",
r"""Páginas: $256\text{ K} = 2^{18}$ → 18 bits. Desplazamiento: $2^{13}$ → 13 bits.
Total: $18 + 13 =$ **31 bits** (la memoria física es un dato de adorno: serviría para la dirección física, de 27 bits).""",
respuestas=[R("Bits", 31)], herramienta="Memoria virtual"),

Ejercicio("vm-10", "Fallos de página de un bucle",
r"""Direcciones virtuales de 32 bits y páginas de 8 KB. 1) Formato. 2) Máximo de entradas de una tabla de un nivel.
3) Con
```c
int a[1000000];
for (j = 1; j < 890000; j++)
    a[j] = a[j-1] + 1;
```
sin ninguna página en memoria y con datos e instrucciones en páginas distintas, nº **mínimo** de fallos de página.""",
r"""**1)** Página 19 bits | desplazamiento 13 bits. **2)** $2^{19} = 524\,288$ (una entrada por página posible).

**3)** El bucle toca de **a[0] a a[889 999]**: bytes 0 … 3 559 999 (cada int ocupa 4).
Una página guarda $8192/4 = 2048$ enteros → $\lceil 890\,000/2048\rceil = 435$ páginas de datos (si a empieza al principio
de una página, que es el caso mínimo). El código cabe en **1 página**.

**Mínimo = 435 + 1 = 436 fallos de página** (j está en un registro).""",
respuestas=[R("2) Entradas", 2**19), R("3) Fallos de página", 436)], herramienta="Memoria virtual"),

Ejercicio("vm-11", "Paginación con TLB: formato, tamaño de la tabla y tiempos",
r"""512 páginas de 8 KB, memoria por bytes, 1 MB de memoria física, sin caché pero con TLB, tabla de páginas de un nivel.
Disco 12 ms, memoria 40 ns, TLB 20 ns. a) Formato de las direcciones virtuales y tamaño del espacio virtual.
b) Tamaño en bits de la tabla con 3 bits de control por entrada. c) Tiempo de acceso máximo y mínimo a un dato.""",
r"""**a)** Página: $\log_2 512 = 9$ bits; desplazamiento: 13 bits → **22 bits**; espacio virtual $2^{22}$ B = **4 MB**.

**b)** Marcos: $1\text{ MB}/8\text{ KB} = 128$ → 7 bits de marco. Cada entrada = 7 + 3 = 10 bits.
Tabla: $512\cdot10 =$ **5120 bits** (640 bytes).

**c)**
- **Mínimo** (acierto en la TLB): TLB + acceso al dato = $20 + 40 =$ **60 ns**.
- **Máximo** (fallo de TLB y fallo de página): TLB (20 ns) + leer la tabla en memoria (40 ns) + traer la página del disco
  (12 ms) + acceso al dato (40 ns) = $12\text{ ms} + 100\text{ ns} \approx$ **12,0001 ms**.

💡 La TLB es una caché de traducciones: ahorra ir a la tabla de páginas (que está en memoria) en cada acceso.""",
respuestas=[R("a) Bits", 22), R("a) MB", 4), R("b) Bits de la tabla", 5120), R("c) Mínimo (ns)", 60),
            R("c) Máximo (ns)", 12_000_100, tolerancia=1e-4)], herramienta="Memoria virtual"),
], icono="📄")
