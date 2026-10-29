from contenido.base import Ejercicio, Hoja, Respuesta

R = Respuesta
VERIF = "\n\n✅ *Comprobado con el simulador de caché de la app (pestaña Herramientas → Caché).*"

HOJA = Hoja("cache", "Jerarquía de memoria y memoria caché", "fc", "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "Accesos de un programa, líneas, conjuntos, tiempo medio de acceso y tasas de acierto de bucles.", [

Ejercicio("cache-1", "Bytes, accesos y fallos de un bucle MIPS",
r"""```mipsasm
        la   $t1, 0x04000
        li   $t2, 0
        li   $t3, 0
        li   $t4, 1000
        li   $t5, 80
bucle:  bgt  $t3, $t4, fin
        lw   $t5, ($t1)
        addi $t2, $t2, $t5
        addi $t1, $t1, 4
        addi $t3, $t3, 1
        addi $t5, $t5, 4
        b    bucle
fin:
```
a) Bytes que ocupa el programa y número de accesos a memoria al ejecutarlo. b) Con una única caché de 8 MB y líneas de
32 bytes, inicialmente vacía, ¿cuántos aciertos y fallos hay?""",
r"""**a) Tamaño:** 12 instrucciones × 4 bytes = **48 bytes**.

**Accesos** = 1 por cada instrucción ejecutada (fetch) + 1 por cada lw/sw.
- $t3 va de 0 a 1000 → el cuerpo (bgt, lw, 3×addi… 7 instrucciones) se ejecuta **1001 veces** (¡bgt sale cuando $t3 > 1000!).
- Instrucciones: $5 + 1001\cdot7 + 1$ (el último bgt que sale) $= 7013$.
- Datos: 1001 lw.

Total: $7013 + 1001 =$ **8014 accesos**.

**b)** La caché es enorme (8 MB): cada bloque solo falla **la primera vez** (fallos «obligatorios»).
- Código: 48 bytes = **2 líneas** de 32 bytes → 2 fallos.
- Datos: 1001 palabras seguidas desde 0x4000 = 4004 bytes → $\lceil4004/32\rceil$ = **126 líneas** → 126 fallos.

**Fallos = 128 · Aciertos = 8014 − 128 = 7886** (tasa de aciertos ≈ 98,4 %).""" + VERIF,
errata="«addi $t2, $t2, $t5» lleva un registro como tercer operando: debería ser «add» (addi necesita un número).",
respuestas=[R("a) Bytes", 48), R("a) Accesos", 8014), R("b) Fallos", 128), R("b) Aciertos", 7886)], herramienta="Caché"),

Ejercicio("cache-2", "Caché de 64 KB y 4 vías",
r"""Computador de 32 bits; caché de 64 KB asociativa por conjuntos de 4 vías, acceso de 4 ns, líneas de 128 bytes; servir un
fallo cuesta 120 ns. a) Nº de líneas. b) Nº de conjuntos. c) Tamaño del bloque que se transfiere en un fallo.
d) Tasa de aciertos para un tiempo medio de acceso de 20 ns.""",
r"""**a)** $\dfrac{2^{16}}{2^7} = 2^9 =$ **512 líneas**. **b)** $512/4 =$ **128 conjuntos**.
**c)** Lo que cabe en una línea: **128 bytes**.

**d)** $T_m = T_a + (1-h)\,T_f$ → $20 = 4 + (1-h)\cdot120$ → $1-h = \dfrac{16}{120} = 0{,}1333$ → **h ≈ 86,7 %**.""",
respuestas=[R("a) Líneas", 512), R("b) Conjuntos", 128), R("c) Bytes por bloque", 128),
            R("d) h (%)", 100 * (1 - 16 / 120), tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("cache-3", "Tiempo medio con escritura inmediata",
r"""Caché de 4 ns, memoria principal de 80 ns, servir un fallo 120 ns, política de **escritura inmediata**. Tasa de aciertos
del 95 % y, de cada 100 accesos, 90 son lecturas. Calcule el tiempo medio de acceso.""",
r"""Lecturas y escrituras se tratan **por separado**:
- **Lecturas** (90 %): fórmula normal → $4 + 0{,}05\cdot120 = 10$ ns.
- **Escrituras** (10 %): con escritura inmediata **toda escritura va a memoria principal** → 80 ns.

$$T_m = 0{,}9\cdot10 + 0{,}1\cdot80 = 9 + 8 = \mathbf{17\ ns}.$$
Moraleja: solo el 10 % son escrituras… y aportan casi la mitad del tiempo. Por eso existe la escritura diferida.""",
respuestas=[R("Tm (ns)", 17)], herramienta="Caché"),

Ejercicio("cache-4", "Tasa de aciertos para 20 ns",
r"""Caché de 16 KB, bloques de 32 bytes (8 palabras), acceso 10 ns; la memoria transfiere un bloque de 8 palabras en 120 ns.
¿Qué tasa de aciertos hace falta para un tiempo medio de 20 ns?""",
r"""$20 = 10 + (1-h)\cdot120$ → $1-h = \dfrac{10}{120} = 0{,}0833$ → **h ≈ 91,7 %**.
(El tamaño de la caché no hace falta para esta pregunta: es un dato «de adorno».)""",
respuestas=[R("h (%)", 100 * (1 - 10 / 120), tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("cache-5", "Caché de dos niveles: cuántos accesos llegan a cada uno",
r"""Caché de 2 niveles: tasa de aciertos de L1 = 90 % y de L2 = 95 %. La aplicación genera un millón de accesos.
a) Accesos a L1. b) Accesos a L2. c) Accesos a memoria principal.""",
r"""Cada nivel solo recibe **los fallos del anterior** (como un embudo):

**a)** L1 recibe todos: **1 000 000**.
**b)** L2 recibe los fallos de L1: $10\,\% \cdot 10^6 =$ **100 000**.
**c)** La MP recibe los fallos de L2: $5\,\% \cdot 100\,000 =$ **5 000**.""",
respuestas=[R("a) L1", 1_000_000), R("b) L2", 100_000), R("c) MP", 5_000)]),

Ejercicio("cache-6", "Sumar dos vectores de float",
r"""Direcciones de 32 bits, memoria por bytes; caché de 4 vías, líneas de 64 bytes, 128 KB; acceso 2 ns, fallo 80 ns.
```c
float v1[10000];
float v2[10000];
for (i = 0; i < 10000; i = i + 1)
    v1[i] = v1[i] + v2[i];
```
a) Memoria direccionable en MB. b) Palabras que caben en la caché. c) Líneas y conjuntos. d) Tasa de aciertos para un
tiempo medio de 10 ns. e) Tasa de aciertos del código (solo datos; i en un registro; caché vacía).""",
r"""**a)** $2^{32}$ B $= 2^{12}\cdot2^{20}$ B = **4096 MB** (4 GB).
**b)** $2^{17}/2^2 = 2^{15} =$ **32 768 palabras**.
**c)** Líneas $2^{17}/2^6 =$ **2048**; conjuntos $2048/4 =$ **512**.
**d)** $10 = 2 + (1-h)\cdot80$ → $1-h = 0{,}1$ → **h = 90 %**.

**e)** Cada vuelta: leer v1[i], leer v2[i], escribir v1[i] → $3\cdot10\,000 = 30\,000$ accesos.
En una línea caben $64/4 = 16$ floats → cada vector ocupa $40\,000/64 = 625$ líneas. Falla el primer acceso a cada línea de
v1 y de v2 (las 4 vías evitan que se echen entre sí): $625 + 625 = 1250$ fallos.
$$h = \frac{30\,000 - 1250}{30\,000} \approx \mathbf{95{,}83\ \%}$$
Comprobación por bloques: cada 16 vueltas hay 48 accesos y 2 fallos → 46/48 ✓.""" + VERIF,
respuestas=[R("a) MB", 4096), R("b) Palabras", 32768), R("c) Líneas", 2048), R("c) Conjuntos", 512),
            R("d) h (%)", 90), R("e) h (%)", 2875 / 30, tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("cache-7", "s = s + a1[i] + a2[i]",
r"""Computador de 32 bits, caché de 512 KB, 4 vías y líneas de 128 bytes.
```c
int a1[200];
int a2[200];
int i, s;
for (i = 0; i < 200; i++) s = s + a1[i] + a2[i];
```
a) Líneas y conjuntos. b) Con la caché vacía y i, s en registros, tasa de aciertos considerando solo los accesos a a1 y a2.""",
r"""**a)** Líneas: $2^{19}/2^7 = 2^{12} =$ **4096**; conjuntos: $4096/4 =$ **1024**.

**b)** 400 lecturas (2 por vuelta). Una línea guarda $128/4 = 32$ enteros → cada vector ocupa $200/32 = 6{,}25$ →
**7 líneas** → 7 fallos por vector (si cada uno empieza al principio de una línea) = **14 fallos**.
$$h = \frac{400-14}{400} = \mathbf{96{,}5\ \%}$$
Si a2 va justo detrás de a1 en memoria (sin alinear), comparten una línea y salen 13 fallos (96,75 %). En el examen,
indica la suposición que haces.""" + VERIF,
respuestas=[R("a) Líneas", 4096), R("a) Conjuntos", 1024), R("b) h (%)", 96.5)], herramienta="Caché"),

Ejercicio("cache-8", "Caché de 256 KB con LRU",
r"""Computador de 32 bits; caché de 256 KB, líneas de 64 bytes, acceso 5 ns, 4 vías, LRU. a) Líneas y conjuntos.
b) Tamaño de los bloques que se transfieren. c) Si traer un bloque cuesta 200 ns, tasa de aciertos para un tiempo medio de 20 ns.""",
r"""**a)** Líneas $2^{18}/2^6 =$ **4096**; conjuntos $4096/4 =$ **1024**. **b)** **64 bytes**.
**c)** $20 = 5 + (1-h)\cdot200$ → $1-h = 0{,}075$ → **h = 92,5 %**.""",
respuestas=[R("a) Líneas", 4096), R("a) Conjuntos", 1024), R("b) Bytes", 64), R("c) h (%)", 92.5)], herramienta="Caché"),

Ejercicio("cache-9", "Estructura de una caché de 2 vías",
r"""Caché de 64 KB para instrucciones o datos, líneas de 64 bytes, acceso 20 ns, penalización por fallo 120 ns, 2 vías.
1) Nº total de líneas. 2) Nº de conjuntos. 3) Líneas por conjunto. 4) Esquema de la estructura. 5) Tiempo en obtener un
dato si hay fallo.""",
r"""1. $2^{16}/2^6 =$ **1024 líneas**. 2. $1024/2 =$ **512 conjuntos**. 3. **2** (= nº de vías).
4. Esquema:

| Conjunto | Vía 0 (V · etiqueta · 64 bytes) | Vía 1 (V · etiqueta · 64 bytes) |
|---|---|---|
| 0 | V · etiq · datos | V · etiq · datos |
| 1 | V · etiq · datos | V · etiq · datos |
| … | … | … |
| 511 | V · etiq · datos | V · etiq · datos |

Con direcciones de 32 bits: **byte 6 bits · conjunto 9 bits · etiqueta 17 bits**.

5. Con fallo hay que traer el bloque y luego servir el dato: $T_a + T_f = 20 + 120 =$ **140 ns**.""",
respuestas=[R("1) Líneas", 1024), R("2) Conjuntos", 512), R("3) Líneas/conjunto", 2), R("5) ns con fallo", 140)],
herramienta="Caché"),

Ejercicio("cache-10", "Fallos de caché de un bucle sin lw/sw",
r"""MIPS de 32 bits; código cargado desde la dirección 0x00000000; caché de 4 vías, 32 KB, líneas de 16 bytes, vacía.
```mipsasm
        li   $t0, 1000
        li   $t1, 0
        li   $t2, 0
bucle:  addi $t1, $t1, 1
        addi $t2, $t2, 4
        beq  $t1, $t0, bucle
```
Calcule el número de fallos y la tasa de aciertos.""",
r"""Con `beq` el bucle se haría una sola vez ($t1 = 1 ≠ 1000 → no salta). Lo que se pretende es repetir hasta que $t1 = 1000,
que es **bne**.

- Solo hay accesos a instrucciones: $3 + 3\cdot1000 = 3003$.
- 6 instrucciones × 4 = 24 bytes → **2 bloques** de 16 bytes (0x00–0x0F y 0x10–0x1F) → **2 fallos** (la primera vez).
- $h = \dfrac{3001}{3003} \approx$ **99,93 %**.

Literalmente con `beq`: se ejecutan 6 instrucciones con 2 fallos → $4/6 \approx 66{,}7\,\%$.""",
errata="Debería ser «bne $t1, $t0, bucle»: con beq el bucle no se repite.",
respuestas=[R("Fallos", 2), R("h (%) con bne", 3001 / 30.03, tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("cache-11", "a[i] = b[i] + c[i] + d[i] en una caché directa",
r"""Computador de 32 bits con una caché de datos de 8 KB, líneas de 64 bytes, **correspondencia directa** y escritura
diferida. Calcule la tasa de fallos global:
```c
double a[1024], b[1024], c[1024], d[1024];   // consecutivos en memoria
for (int i = 0; i < 1024; i++)
    a[i] = b[i] + c[i] + d[i];
```""",
r"""- Cada vector: $1024\cdot8 = 8192$ B = **8 KB = justo el tamaño de la caché**. Como están seguidos, a[i], b[i], c[i] y d[i]
  están separados exactamente 8 KB → **caen en la misma línea** de la caché directa ($línea = bloque \bmod 128$).
- Cada vuelta: leer b[i], c[i], d[i] y escribir a[i]; cada acceso **expulsa** la línea del anterior (y al expulsar a, se
  vuelca porque está modificada).
- Resultado: **todos los accesos fallan** → tasa de fallos = **100 %** (4096 de 4096). Es el caso de «thrashing» o
  conflicto patológico de la correspondencia directa.

💡 Analogía: cuatro personas que solo pueden sentarse en la misma silla: cada vez que una se sienta, levanta a la otra.""" + VERIF,
respuestas=[R("Tasa de fallos (%)", 100)], herramienta="Caché"),

Ejercicio("cache-12", "El mismo bucle con caché totalmente asociativa (LRU)",
r"""Resuelva el ejercicio anterior suponiendo que la caché es **totalmente asociativa** con sustitución LRU.""",
r"""Ahora cualquier bloque puede ir en cualquiera de las 128 líneas: las 4 líneas «en uso» (una de cada vector) caben a la vez.
- Cada línea de 64 bytes guarda 8 doubles → cada línea de cada vector falla solo en su primer acceso.
- Fallos: $4\ \text{vectores}\cdot\dfrac{8192}{64} = 4\cdot128 = 512$ de 4096 accesos.

**Tasa de fallos = 512/4096 = 12,5 %** (1 de cada 8).""" + VERIF,
errata="El enunciado dice «Resuelva el ejercicio 3»; se refiere al ejercicio 11 (el bucle con a, b, c y d).",
respuestas=[R("Tasa de fallos (%)", 12.5)], herramienta="Caché"),

Ejercicio("cache-13", "El mismo bucle con 2 y 4 vías (LRU)",
r"""Resuelva el ejercicio 11 suponiendo que la caché es asociativa por conjuntos de **dos** vías y de **cuatro** vías, con LRU.""",
r"""Los cuatro bloques a[i], b[i], c[i], d[i] siguen yendo **al mismo conjunto** (distan 8 KB).

- **2 vías** (64 conjuntos): compiten 4 bloques por 2 huecos, en orden cíclico b → c → d → a → b… Con LRU siempre se expulsa
  justo el que se va a necesitar → **100 % de fallos**.
- **4 vías** (32 conjuntos): ¡caben los 4! Cada línea falla solo la primera vez → **12,5 %** (como la totalmente asociativa).""" + VERIF,
errata="Igual que el anterior: «ejercicio 3» debe ser «ejercicio 11».",
respuestas=[R("Fallos con 2 vías (%)", 100), R("Fallos con 4 vías (%)", 12.5)], herramienta="Caché"),

Ejercicio("cache-14", "Recorrer una matriz por filas o por columnas",
r"""Computador de 32 bits; caché de datos de 32 KB, líneas de 64 bytes, 2 vías. `int m[512][512]` (se guarda por filas).
Tasa de fallos de: (1) `sum = sum + m[i][j]` (bucle externo i, interno j) y (2) `sum = sum + m[j][i]`.""",
r"""Una línea guarda $64/4 = 16$ enteros. Cada fila mide $512\cdot4 = 2048$ B = 32 líneas. La caché tiene 512 líneas y
256 conjuntos.

**(1) Por filas** (en el orden en que está en memoria): falla 1 de cada 16 accesos →
**tasa de fallos = 1/16 = 6,25 %** (16 384 fallos de 262 144).

**(2) Por columnas** (`m[j][i]`): cada acceso salta 2048 bytes = 32 líneas. Esos saltos solo caen en
$256/32 = 8$ conjuntos distintos → con 2 vías caben 16 líneas, pero cada columna usa 512 líneas distintas. Cuando se vuelve
a la misma línea (siguiente i), ya la han echado → **tasa de fallos = 100 %**.

Moraleja: en C, recorre las matrices **por filas** (bucle interno en el último índice).""" + VERIF,
respuestas=[R("(1) Tasa de fallos (%)", 6.25), R("(2) Tasa de fallos (%)", 100)], herramienta="Caché"),
], icono="🧠")
