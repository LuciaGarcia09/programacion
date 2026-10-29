from contenido.base import Ejercicio, Hoja, Respuesta

R = Respuesta
VERIF = "\n\n✅ *Tasas comprobadas con el simulador de caché de la app.*"

HOJA = Hoja("jerarquia", "Jerarquía de memoria: optimizaciones", "fc",
            "Arquitectura de Computadores · Ejercicios de jerarquía de memoria (J. D. García et al., ARCOS-UC3M)",
            "CPI con fallos, fusión de arrays y de bucles, conflictos, cachés multinivel y escritura.", [

Ejercicio("jer-1", "Speedup de no tener fallos de caché",
r"""CPI = 1 cuando todos los accesos aciertan. Los load/store son el 25 % de las instrucciones; penalización por fallo 50 ciclos;
tasa de fallos 5 %; todas las instrucciones están en caché. Speedup del caso sin fallos frente al caso con fallos.""",
r"""Ciclos de espera por instrucción = accesos a datos por instrucción × tasa de fallos × penalización:
$$CPI_{real} = 1 + 0{,}25\cdot0{,}05\cdot50 = 1 + 0{,}625 = 1{,}625$$
$$S = \frac{CPI_{real}}{CPI_{ideal}} = \frac{1{,}625}{1} = \mathbf{1{,}625}$$
Una caché perfecta haría el programa un 62,5 % más rápido.""",
origen="Junio de 2015", respuestas=[R("Speedup", 1.625)], herramienta="Caché"),

Ejercicio("jer-2", "Fusión de arrays (x, y, z, vx, vy, vz)",
r"""```c
const unsigned int max = 1024 * 1024;
double x[max], y[max], z[max], vx[max], vy[max], vz[max];
void actualiza_posiciones(double dt) {
    for (unsigned int i = 0; i < max; ++i) {
        x[i] = vx[i] * dt + x[i];
        y[i] = vy[i] * dt + y[i];
        z[i] = vz[i] * dt + z[i];
    }
}
```
L1: 4 vías, 32 KB, líneas de 64 B. L2: 8 vías, 1 MB, líneas de 64 B. LRU, cachés vacías. Arrays consecutivos, el primero en
múltiplo de 1024; dt e i en registros. 1. Tasas de acierto de L1, L2 y global. 2. Aplique fusión de arrays. 3. Repita
los cálculos. 4. Con acierto en L1 = 4 ciclos, en L2 = 14 y traer de memoria a L2 = 80, tiempo medio de acceso en cada caso.""",
r"""**1. Código original.** Cada array mide $2^{20}\cdot8 = 8$ MB, múltiplo del tamaño de L1 y de L2 → **x[i], y[i], z[i],
vx[i], vy[i] y vz[i] caen siempre en el mismo conjunto**. Por iteración: 9 accesos (leer vx, leer x, escribir x, y lo mismo
con y y z) sobre **6 líneas distintas**.

- **L1 (4 vías):** 6 líneas compitiendo por 4 huecos en orden cíclico → con LRU se expulsa justo la que se va a necesitar.
  Las 6 lecturas fallan siempre; solo aciertan las 3 escrituras (justo después de leer el mismo dato).
  **$h_{L1} = 3/9 = 33{,}3\,\%$**.
- **L2 (8 vías):** sí caben las 6 líneas. Recibe 6 accesos por iteración y cada línea (8 doubles) falla solo la primera vez:
  **$h_{L2} = 42/48 = 87{,}5\,\%$**.
- **Global:** van a memoria 6 de cada $9\cdot8 = 72$ accesos → **$h = 91{,}7\,\%$**.

**2. Fusión de arrays:**
```c
struct cuerpo { double x, y, z, vx, vy, vz; };    // 48 bytes
struct cuerpo c[max];
for (unsigned int i = 0; i < max; ++i) {
    c[i].x = c[i].vx * dt + c[i].x;
    c[i].y = c[i].vy * dt + c[i].y;
    c[i].z = c[i].vz * dt + c[i].z;
}
```
**3.** Ahora se recorre la memoria seguida: 4 estructuras = 192 B = 3 líneas para 36 accesos → 3 fallos.
- **$h_{L1} = 33/36 = 91{,}7\,\%$**.
- **L2:** todo lo que le llega son bloques nuevos → **$h_{L2} = 0\,\%$**.
- **Global:** 3 de 36 van a memoria → **91,7 %** (los mismos fallos «obligatorios», pero ya no hay conflictos en L1).

**4.** $T_m = 4 + m_{L1}\cdot(14 + m_{L2}\cdot80)$:
- Original: $4 + \tfrac23\,(14 + 0{,}125\cdot80) = 4 + \tfrac23\cdot24 =$ **20 ciclos**.
- Fusionado: $4 + \tfrac1{12}\,(14 + 80) =$ **11,83 ciclos** (1,69 veces más rápido).""" + VERIF,
origen="Octubre de 2014",
respuestas=[R("1) h L1 (%)", 100 / 3, tolerancia=1e-3), R("1) h L2 (%)", 87.5), R("1) h global (%)", 1100 / 12, tolerancia=1e-3),
            R("3) h L1 (%)", 1100 / 12, tolerancia=1e-3), R("4) Tm original", 20), R("4) Tm fusionado", 4 + 94 / 12, tolerancia=1e-3)],
herramienta="Caché"),

Ejercicio("jer-3", "Fusión de bucles… que empeora",
r"""Mismas variables y cachés que el anterior, pero la función tiene **tres bucles** separados (uno para x, otro para y, otro
para z). 1. Tasas de acierto de L1, L2 y global. 2. Aplique fusión de bucles. 3. Repita. 4. Tiempo medio con L1 = 4,
L2 = 16 y memoria = 80 ciclos.""",
r"""**1. Tres bucles:** cada bucle solo usa **2 arrays** (p. ej. vx y x), que caben en el conjunto de 4 vías.
Cada 8 iteraciones: 24 accesos, 2 fallos → **$h_{L1} = 22/24 = 91{,}7\,\%$**; a L2 llegan solo bloques nuevos →
**$h_{L2} = 0\,\%$**; global **91,7 %**.

**2. Fusión de bucles:** un solo `for` con las tres sentencias… ¡que es justo el código del ejercicio anterior!

**3.** Por tanto, $h_{L1} = 33{,}3\,\%$, $h_{L2} = 87{,}5\,\%$, global 91,7 %.

**4.**
- Tres bucles: $4 + \tfrac1{12}(16 + 80) =$ **12 ciclos**.
- Fusionado: $4 + \tfrac23(16 + 0{,}125\cdot80) = 4 + \tfrac23\cdot26 =$ **21,33 ciclos**.

⚠️ **Moraleja:** la fusión de bucles mejora la localidad temporal, pero aquí junta 6 flujos que caen en el **mismo conjunto**
de una caché de 4 vías y provoca fallos por **conflicto**. Ninguna optimización es buena siempre: hay que mirar las direcciones.""" + VERIF,
origen="Octubre de 2014",
respuestas=[R("1) h L1 (%)", 1100 / 12, tolerancia=1e-3), R("3) h L1 (%)", 100 / 3, tolerancia=1e-3), R("4) Tm separados", 12),
            R("4) Tm fusionado", 4 + 2 / 3 * 26, tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("jer-4", "Array de estructuras: fusión de bucles y arrays paralelos",
r"""```c
struct particula { double x, y; double ax, ay; double vx, vy; double masa; double carga; };
void mueve(particula p[], int n, double t) {
    for (int i = 0; i < n; ++i) p[i].x += p[i].vx * t + 0.5 * p[i].ax * t * t;
    for (int i = 0; i < n; ++i) p[i].y += p[i].vy * t + 0.5 * p[i].ay * t * t;
}
```
1000 partículas; L1 de datos de 32 KB, 4 vías, bloques de 64 B, vacía; p alineado a 64; n, t, i en registros.
1. Fallos. 2. Tasa de fallos. 3. Con fusión de bucles. 4. Con arrays paralelos sin fusión. 5. ¿Conviene fusionar en 4?""",
r"""Cada partícula = 8 doubles = **64 B = una línea**. El array mide 64 000 B > 32 KB: no cabe entero.

**1–2.** Cada bucle hace 4 accesos por partícula (leer vx, ax, x y escribir x) y falla 1 vez (la línea de esa partícula).
El segundo bucle vuelve a fallar en todas porque al acabar el primero solo quedan las últimas 512 líneas.
**Fallos = 1000 + 1000 = 2000** de 8000 accesos → **tasa de fallos 25 %**.

**3. Fusión de bucles:**
```c
for (int i = 0; i < n; ++i) {
    p[i].x += p[i].vx * t + 0.5 * p[i].ax * t * t;
    p[i].y += p[i].vy * t + 0.5 * p[i].ay * t * t;
}
```
8 accesos por partícula y 1 fallo → **1000 fallos, 12,5 %**.

**4. Arrays paralelos** (`double x[1000], y[1000], ax[1000], …`), sin fusionar: el primer bucle usa x, vx, ax; en una línea
caben 8 doubles → 3 fallos cada 8 partículas (32 accesos): $3\cdot125 = 375$ fallos; el segundo, con y, vy, ay, otros 375.
**750 fallos de 8000 → 9,375 %**. Ya no se traen a la caché masa, carga… que no se usan.

**5.** Fusionar los bucles con arrays paralelos **no reduce los fallos** (sigue habiendo 750: cada línea útil se trae una
vez), aunque sí ahorra la sobrecarga de un bucle. Tampoco perjudica: son 6 flujos, que no caen todos en el mismo conjunto.""" + VERIF,
origen="Octubre de 2013",
respuestas=[R("1) Fallos", 2000), R("2) Tasa (%)", 25), R("3) Tasa (%)", 12.5), R("4) Tasa (%)", 9.375)], herramienta="Caché"),

Ejercicio("jer-5", "Matriz v[64][1024] y vector b",
r"""```c
for (i = 0; i < 64; i++)
    for (j = 0; j < 1024; j = j + 2)
        v[i][j] = v[i][j] * v[i][j+1] + b[i];
```
Caché de 256 KB totalmente asociativa con LRU, bloques de 64 B, palabras de 8 B; v (64 × 1024) y b (64) de reales de 8 B
por filas; índices en registros; caché vacía. 1. Fallos. 2. Tasa de fallos. 3. ¿Hay reemplazos de líneas ya cargadas?
4. ¿Mejoraría el intercambio de bucles?""",
r"""**1.** Accesos por iteración: leer v[i][j], v[i][j+1], b[i] y escribir v[i][j] → $64\cdot512\cdot4 = 131\,072$.
- v: cada línea (8 doubles) se usa en 4 iteraciones seguidas → falla 1 vez: $64\cdot1024/8 = 8192$ fallos.
- b: 64 doubles = 8 líneas → 8 fallos.
**Total: 8200 fallos.**

**2.** $8200/131\,072 \approx$ **6,26 %**.

**3.** Sí hay reemplazos: v ocupa 512 KB y la caché 256 KB (4096 líneas), así que en la segunda mitad se expulsan líneas.
Pero con LRU se van las líneas de v **que ya no se volverán a usar**; las de b se usan continuamente y siempre están entre
las más recientes. Los reemplazos no generan fallos extra.

**4. No.** El código ya recorre v **por filas** (en el orden en que está en memoria). Intercambiar los bucles (j fuera, i
dentro) saltaría 8 KB en cada acceso y empeoraría la localidad espacial.""" + VERIF,
origen="Octubre de 2013",
respuestas=[R("1) Fallos", 8200), R("2) Tasa (%)", 8200 / 131072 * 100, tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("jer-6", "Optimizar a[] y b[] y tiempo con L1 y L2",
r"""```c
int a[100]; int b[100];
for (i = 0; i < 100; i++) a[i] = a[i] + 5;
for (i = 0; i < 100; i++) {
    if (i > 90) c = c + 1;
    else        b[i] = a[i] * 3;
}
```
1. Optimizaciones de caché del compilador y código reescrito. 2. Con líneas de 32 B y caché vacía, tasa de fallos del
programa optimizado (solo fallos forzosos de a y b). 3. L1 y L2 unificadas, ciclo 1 ns, CPI = 1,3; L1: fallos 10 %,
penalización 10 ns; L2: aciertos 95 %, penalización 80 ns; acceso a L1 1 ns. Tiempo de un programa con CI instrucciones
con un 50 % de lecturas/escrituras.""",
r"""**1.** **Fusión de bucles** (a[i] se usa en los dos: se aprovecha mientras está en caché) y, ya puestos, **división del
bucle** para quitar el `if`:
```c
for (i = 0; i <= 90; i++) {
    a[i] = a[i] + 5;
    b[i] = a[i] * 3;       // a[i] ya está en un registro / en caché
}
for (i = 91; i < 100; i++) a[i] = a[i] + 5;
c = c + 9;                 // las 9 vueltas con i > 90
```

**2.** Una línea de 32 B guarda 8 int.
- a: 100 elementos → $\lceil100/8\rceil = 13$ líneas → 13 fallos.
- b: se escriben b[0..90] = 91 elementos → 12 líneas → 12 fallos.
- Accesos (contando que el compilador reutiliza a[i] en un registro): leer y escribir a (200) + escribir b (91) = 291.
**Tasa de fallos = 25/291 ≈ 8,6 %**.

**3.** Accesos por instrucción: 1 (fetch) + 0,5 (datos) = 1,5. Penalización media por acceso:
$0{,}10\cdot(10 + 0{,}05\cdot80) = 0{,}1\cdot14 = 1{,}4$ ns (el acceso a L1 ya está dentro del CPI).
$$T = CI\cdot(1{,}3 + 1{,}5\cdot1{,}4)\text{ ns} = \mathbf{3{,}4\cdot CI\ ns}.$$""",
origen="Octubre de 2013",
respuestas=[R("2) Fallos", 25), R("3) ns por instrucción", 3.4)], herramienta="Caché"),

Ejercicio("jer-7", "a = b + c y d = b − c: fusión de bucles",
r"""```c
double a[256][256], b[256][256], c[256][256], d[256][256];
for (int i = 0; i < 256; ++i) for (int j = 0; j < 256; ++j) a[i][j] = b[i][j] + c[i][j];
for (int i = 0; i < 256; ++i) for (int j = 0; j < 256; ++j) d[i][j] = b[i][j] - c[i][j];
```
L1 totalmente asociativa de 16 KB, LRU, líneas de 64 B; un fallo de L1 cuesta 16 ciclos (L2 siempre acierta); los fallos de
escritura van a un búfer de escritura sin esperas. 1. Tasa de aciertos. 2. Tiempo de acceso (acierto en L1 = 1 ciclo).
3. Transformación del compilador. 4. Nueva tasa y tiempo.""",
r"""Cada matriz mide 512 KB y en una línea caben 8 doubles.

**1.** Por cada 8 elementos de un bucle: leer 8 de b (1 fallo), 8 de c (1 fallo) y escribir 8 de a (las escrituras van al
búfer: **no se asignan en caché**, cuentan como fallo pero sin espera). El segundo bucle no aprovecha nada del primero (b y c
no caben en 16 KB).
$$h = \frac{14}{24} = \mathbf{58{,}3\,\%}$$

**2.** Solo cuestan los fallos de **lectura**: 2 de cada 24 accesos.
$$T_m = 1 + \frac{2}{24}\cdot16 = \mathbf{2{,}33\ ciclos}$$

**3. Fusión de bucles:**
```c
for (int i = 0; i < 256; ++i)
    for (int j = 0; j < 256; ++j) {
        a[i][j] = b[i][j] + c[i][j];
        d[i][j] = b[i][j] - c[i][j];
    }
```
**4.** Cada 8 elementos: 32 lecturas (b y c dos veces) con 2 fallos y 16 escrituras al búfer:
$h = 30/48 =$ **62,5 %** y $T_m = 1 + \tfrac{2}{48}\cdot16 =$ **1,67 ciclos**. Los fallos de lectura bajan a la mitad
(de 32 768 a 16 384).""" + VERIF,
origen="Junio de 2011",
respuestas=[R("1) h (%)", 175 / 3, tolerancia=1e-3), R("2) Tm (ciclos)", 7 / 3, tolerancia=1e-3), R("4) h (%)", 62.5),
            R("4) Tm (ciclos)", 5 / 3, tolerancia=1e-3)], herramienta="Caché"),

Ejercicio("jer-8", "Escritura inmediata vs post-escritura y caché multibanco",
r"""| Memoria | Tiempo de acceso (ns) | Tasa de aciertos |
|---|---|---|
| L1 | 2 | 0,8 |
| L2 | 8 | 0,9 |
| RAM | 100 | 1 |

1. Si el 100 % de los accesos son escrituras, tiempo medio con (a) escritura inmediata y (b) post-escritura en L1 y L2.
2. Considerando L1 + L2 como una única caché, tiempo medio y tasa de aciertos globales.
3. Con `for (i = 0; i < 1000; i = i + 32) a[i] = a[i+8] + a[i+16];` (elementos de 8 B, bloques de 64 B), efecto de una caché
multibanco con 4 bancos en el tiempo de cada acceso y en el ancho de banda.""",
r"""**1. (a) Escritura inmediata** (*write-through*): cada escritura se propaga a todos los niveles hasta la RAM, así que
(sin búfer de escritura) cuesta siempre lo de todos: $2 + 8 + 100 =$ **110 ns**.

**(b) Post-escritura** (*write-back*): se escribe en el nivel donde está el bloque; solo se baja de nivel en los fallos:
$$T = 2 + 0{,}2\cdot\left(8 + 0{,}1\cdot100\right) = 2 + 0{,}2\cdot18 = \mathbf{5{,}6\ ns}$$
(sin contar el volcado de bloques sucios al reemplazar).

**2. Caché global:** falla solo si fallan las dos: $1 - 0{,}2\cdot0{,}1 = 0{,}98$ → **h = 98 %**.
Tiempo medio del sistema: el mismo **5,6 ns** ($2 + 0{,}2\cdot8 + 0{,}02\cdot100$). El tiempo medio de un *acierto* de esa
caché global es $\dfrac{0{,}8\cdot2 + 0{,}18\cdot10}{0{,}98} \approx 3{,}47$ ns.

**3.** Cada iteración toca a[i], a[i+8] y a[i+16]: desplazamientos de 0, 64 y 128 bytes → **tres bloques consecutivos**
distintos. Con 4 bancos entrelazados (bloque k → banco k mod 4) caen en **bancos 0, 1 y 2**: se pueden servir **a la vez**.
- **Tiempo de cada acceso:** no cambia (cada banco tarda lo mismo).
- **Ancho de banda:** hasta **3 veces mayor** para este código (el banco 3 nunca se usa porque a[i+24] no se lee).""",
origen="Mayo de 2011",
respuestas=[R("1a) ns", 110), R("1b) ns", 5.6), R("2) h global (%)", 98)], herramienta="Caché"),
], icono="🏗️")
