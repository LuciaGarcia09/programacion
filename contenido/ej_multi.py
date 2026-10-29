from itertools import product

from contenido.base import Ejercicio, Hoja, Respuesta
from core.consistencia import intercalaciones, texto_orden

R = Respuesta


def tabla_sc(hilos, columnas, extraer, finales=()):
    """Tabla con las 2^k combinaciones de 0/1: ¿posible con consistencia secuencial? + un orden de ejemplo."""
    res = intercalaciones(hilos, finales)
    vistos = {}
    for clave, orden in res.items():
        vistos.setdefault(extraer(clave), orden)
    t = "| " + " | ".join(columnas) + " | ¿Posible (SC)? | Un orden que lo produce |\n|" + "---|" * (len(columnas) + 2) + "\n"
    for combo in product((0, 1), repeat=len(columnas)):
        if combo in vistos:
            t += "| " + " | ".join(map(str, combo)) + f" | ✅ sí | {texto_orden(hilos, vistos[combo])} |\n"
        else:
            t += "| " + " | ".join(map(str, combo)) + " | ❌ no | — |\n"
    return t


H9 = ["X=1", "print(X)\nprint(Y)", "X=1\nprint(X)"]
T9 = tabla_sc(H9, ["Print(X) [P2]", "Print(Y)", "Print(X) [P3]"], lambda k: (k[1][0], k[1][1], k[2][0]))
H10 = ["A=1\nprint(flag)", "while(flag==0)\nprint(A)", "flag=1\nprint(A)"]
T10 = tabla_sc(H10, ["Print(flag) [P1]", "Print(A) [P2]", "Print(A) [P3]"], lambda k: (k[0][0], k[1][0], k[2][0]))
H11 = ["A=1", "U=A\nB=1", "V=B\nW=A"]
T11 = tabla_sc(H11, ["U", "V", "W"], lambda k: k[-1], ("U", "V", "W"))
H12 = ["X=1\nY=X", "Y=2\nX=3"]
R12 = sorted({k[-1] for k in intercalaciones(H12, ("X", "Y"))})
R12_TXT = ", ".join(f"({x}, {y})" for x, y in R12)

MSI = r"""
<details><summary>📘 Recordatorio del protocolo MSI (pulsa)</summary>

| Estado | Significado |
|---|---|
| **M** (modificado) | solo esta caché tiene el bloque y está **cambiado** respecto a memoria (es la dueña) |
| **S** (compartido) | una o varias cachés lo tienen **limpio** (igual que memoria); solo se puede leer |
| **I** (inválido) | no está (o la copia ya no vale) |

| Evento | Transición y bus |
|---|---|
| Lectura con fallo | I → S · **BusRd** (si otra lo tiene en M, lo vuelca —*flush*— y pasa a S) |
| Escritura con fallo | I → M · **BusRdX** (las demás copias → I; si había una M, la vuelca antes) |
| Escritura sobre S | S → M · **BusUpgr**/invalidación (las demás copias → I) |
| Lectura o escritura sobre M · lectura sobre S | acierto, sin tráfico |
| Otra caché lee un bloque que tengo en M | M → S + flush · Otra caché escribe: M → I + flush; S → I |

💡 Analogía: un documento compartido. S = todos tenéis una fotocopia; para escribir hay que romper las fotocopias de los
demás (invalidar) y quedarte el original (M).
</details>
"""

HOJA = Hoja("multi", "Multiprocesadores: coherencia y consistencia", "fc",
            "Arquitectura de Computadores · Ejercicios de multiprocesadores (J. D. García et al., ARCOS-UC3M)",
            "Protocolo MSI, tráfico de bus, cerrojos test-and-set y LL/SC, modelos de consistencia.", [

Ejercicio("mp-1", "Estados MSI de la variable A",
r"""Dos procesadores con caché privada y post-escritura; todas las entradas inválidas; A vale 255 en memoria.

| Tiempo | Procesador 1 | Procesador 2 |
|---|---|---|
| 1 | lw $t0, A | |
| 2 | | lw $t1, A |
| 3 | sw $zero, A | |
| 4 | | lw $t2, A |

Indique para cada operación el estado y el valor de A en cada caché y en memoria.""" + MSI,
r"""| Tiempo | Estado C1 | Valor C1 | Estado C2 | Valor C2 | Memoria | Qué pasa |
|---|---|---|---|---|---|---|
| 0 | I | — | I | — | 255 | |
| 1 | **S** | 255 | I | — | 255 | P1 falla en lectura: BusRd, la memoria da el dato |
| 2 | S | 255 | **S** | 255 | 255 | P2 falla en lectura: BusRd |
| 3 | **M** | 0 | **I** | — | 255 | P1 escribe sobre S: invalida la copia de P2. Post-escritura: la memoria **no** se actualiza |
| 4 | **S** | 0 | **S** | 0 | **0** | P2 falla; P1 tiene el bloque en M: lo vuelca (flush) a memoria y a P2, y pasa a S |""",
origen="Junio de 2015", respuestas=[R("Valor en memoria al final", 0), R("Valor en memoria tras t = 3", 255)]),

Ejercicio("mp-2", "MSI con tres hilos y un conflicto de líneas",
r"""Protocolo MSI. Hilo 0: `for (i=0;i<16;i++) a[i]=16;` · Hilo 1: `tmp=0; for (i=0;i<16;i++){ a[i]=tmp; tmp+=a[i]; }` ·
Hilo 2: `cnt=0; for (i=0;i<4;i++) cnt+=b[i];`
2 procesadores de 32 bits, caché privada de correspondencia directa, líneas de 16 B, vacías. Hilos 0 y 2 en P0; hilo 1 en
P1. i, tmp, cnt en registros. **El bloque de a[0] y el de b[0] van a la misma línea de caché.**
Transiciones del bloque de a[0] y tráfico de bus: 1) hilo 0 → hilo 1; 2) hilo 1 → hilo 0; 3) hilo 0 → hilo 2 → hilo 1.
4) Fallos de caché de cada procesador en cada escenario.""" + MSI,
r"""Una línea de 16 B guarda 4 enteros: a[0..15] ocupa **4 bloques** y b[0..3], **1 bloque**.

**1) Hilo 0 → hilo 1**

| Código | Transición P0 | Transición P1 | Señales de bus |
|---|---|---|---|
| Hilo 0 | I → M (escribe a[0]) | — (I) | BusRdX |
| Hilo 1 | M → I (vuelca el bloque) | I → M (escribe a[0]; luego lee/escribe con aciertos) | BusRdX + flush de P0 |

**2) Hilo 1 → hilo 0**

| Código | Transición P0 | Transición P1 | Señales de bus |
|---|---|---|---|
| Hilo 1 | — (I) | I → M | BusRdX |
| Hilo 0 | I → M | M → I (vuelca) | BusRdX + flush de P1 |

**3) Hilo 0 → hilo 2 → hilo 1**

| Código | Transición P0 | Transición P1 | Señales de bus |
|---|---|---|---|
| Hilo 0 | I → M | — | BusRdX |
| Hilo 2 | M → I (**reemplazo**: b[0] ocupa su línea; se escribe a memoria) | — | Write-back de a[0..3] + BusRd de b |
| Hilo 1 | — (I) | I → M | BusRdX (lo sirve la memoria) |

**4) Fallos**

| Escenario | Fallos P0 | Fallos P1 |
|---|---|---|
| Hilo 0 → hilo 1 | 4 (los 4 bloques de a) | 4 |
| Hilo 1 → hilo 0 | 4 | 4 |
| Hilo 0 → hilo 2 → hilo 1 | 4 + 1 (b) = **5** | 4 |

En el hilo 1, `tmp += a[i]` lee un dato que acaba de escribir: acierto (el bloque ya está en M).""",
origen="Enero de 2015", respuestas=[R("Fallos de P0 en el escenario 3", 5), R("Fallos de P1 en el escenario 1", 4)]),

Ejercicio("mp-3", "Cachés MSI con etiquetas completas",
r"""Bus con *snooping* y MSI. Cada caché: correspondencia directa, 4 bloques de 2 palabras; la etiqueta es la dirección
completa; palabra menos significativa a la izquierda.

**P0:** B0 I 0x00100700 [0x00000000 0x7FAABB11] · B1 S 0x00100708 [0x00000000 0x00001234] · B2 M 0x00100710
[0x00000000 0x0077AABB] · B3 I 0x00100718 [0x00000000 0x7FAABB11]

**P1:** B0 I 0x00100700 [0x00000000 0x7FAABB11] · B1 M 0x00100728 [0x00000000 0xFF000000] · B2 I 0x00100710
[0x00000000 0xEEEE7777] · B3 S 0x00100718 [0x00000000 0x7FAABB11]

**P2:** B0 S 0x00100720 [0x00000000 0x1111AAAA] · B1 S 0x00100708 [0x00000000 0x00001234] · B2 I 0x00100710
[0x00000000 0x7FAABB11] · B3 I 0x00100718 [0x00001234 0x1111AABB]

Partiendo siempre de la situación inicial: 1) P2: write 0x00100708, 0xFFFFFFFF. 2) P2: read 0x00100708.
3) P2: read 0x00100718. Indique los cambios y, en las lecturas, el valor leído.""" + MSI,
r"""Bloque de 8 bytes → el bloque de una dirección es $(dir / 8) \bmod 4$: …700 → B0, …708 → B1, …710 → B2, …718 → B3,
…720 → B0, …728 → B1. La primera palabra de cada bloque es la de la dirección de la etiqueta y la segunda, la de +4.

**1) P2 escribe 0xFFFFFFFF en 0x00100708.** P2 tiene ese bloque en **S** → acierto de escritura sobre S: se invalidan las
demás copias (BusUpgr). P0 tiene 0x708 en S → I. P1 tiene en B1 otro bloque (0x728) → no cambia.

| Procesador | Bloque | Estado anterior | Estado actual | Etiqueta | Datos |
|---|---|---|---|---|---|
| P2 | B1 | S | **M** | 0x00100708 | **0xFFFFFFFF** 0x00001234 |
| P0 | B1 | S | **I** | 0x00100708 | 0x00000000 0x00001234 |

**2) P2 lee 0x00100708.** Está en S en su B1 → **acierto**, sin cambios. Valor leído: **0x00000000** (primera palabra).

**3) P2 lee 0x00100718.** Su B3 tiene esa etiqueta pero en **I** → fallo de lectura (BusRd). Nadie lo tiene en M (P1 en S)
→ lo sirve la memoria, con el mismo contenido que la copia S de P1.

| Procesador | Bloque | Estado anterior | Estado actual | Etiqueta | Datos |
|---|---|---|---|---|---|
| P2 | B3 | I | **S** | 0x00100718 | 0x00000000 0x7FAABB11 |
| P1 | B3 | S | S | 0x00100718 | 0x00000000 0x7FAABB11 |

Valor leído: **0x00000000**.""",
origen="Enero de 2014", respuestas=[R("2) Valor leído", "00000000", "hex"), R("3) Valor leído", "00000000", "hex")]),

Ejercicio("mp-4", "¿r2 = r4 = 42 en un Intel P6?",
r"""Procesador Intel P6 o posterior; z y t valen 42.
Hilo 1: `mov [_z], 1` · `mov r1, [_z]` · `mov r2, [_t]`. Hilo 2: `mov [_t], 1` · `mov r3, [_t]` · `mov r4, [_z]`.
¿Es posible que al final r2 y r4 valgan ambos 42?""",
r"""**Sí.** El modelo de memoria de x86 (TSO, *total store order*) permite que una **lectura adelante a una escritura
anterior a otra dirección**: cada núcleo tiene un **búfer de escrituras** (store buffer).

1. Hilo 1 deja `z = 1` en su búfer (aún no visible para el otro núcleo); `r1 = [_z]` lee su propio búfer → **r1 = 1**
   (*store forwarding*); `r2 = [_t]` lee memoria → **42**.
2. A la vez, hilo 2 deja `t = 1` en su búfer, `r3 = 1` y `r4 = [_z]` → **42** (la escritura de z sigue en el búfer del hilo 1).
3. Después los búferes se vacían a memoria.

Resultado r1 = r3 = 1 y **r2 = r4 = 42**, imposible con consistencia secuencial pero permitido (y documentado por Intel:
*intra-processor forwarding*). Para evitarlo hay que poner una barrera (`mfence`) entre la escritura y la lectura.""",
origen="Junio de 2014", respuestas=[R("¿Posible? (si/no)", ["si", "sí"], "texto")]),

Ejercicio("mp-5", "¿Qué accesos llevan de un estado a otro?",
r"""MSI con bloques de una palabra («Exclusive» = M).

| Inicial | A | B | C | D |
|---|---|---|---|---|
| P0 | S | M | S | S |
| P1 | I | I | I | S |
| P2 | I | I | S | S |

| Final | A | B | C | D |
|---|---|---|---|---|
| P0 | I | I | I | S |
| P1 | I | I | S | M |
| P2 | M | M | I | S |

Para cada variable, describa los accesos que llevan al estado final (puede no haber solución) y el tráfico de bus.""" + MSI,
r"""**A:** P2 **escribe** A. Como P2 la tiene en I → BusRdX (o *invalidate*); P0 (S) → I. P2 → M.

**B:** P2 **escribe** B. BusRdX; P0 la tiene en M → hace **flush** (la vuelca a memoria / se la pasa a P2) y queda en I. P2 → M.

**C:** hay que acabar con solo P1 en S. Una opción: P1 **lee** C (BusRd, P1: I → S) y P0 y P2 **reemplazan** su copia
(S → I sin tráfico, por acceder a otros datos que van a la misma línea). Otra: P1 escribe C (BusRdX: P0 y P2 → I, P1 → M)…
pero de M a S solo se pasa si **otro** lee, y ese otro quedaría en S. Así que **solo es alcanzable con reemplazos**.

**D:** **imposible.** En MSI, si una caché tiene el bloque en **M**, todas las demás tienen que estar en **I** (si no, habría
copias distintas del mismo dato). El estado final P0 = S, P1 = M, P2 = S no es coherente.""",
origen="Junio de 2014", respuestas=[R("¿D es alcanzable? (si/no)", ["no"], "texto")]),

Ejercicio("mp-6", "Core Duo: estados de a[0] y tiempo del núcleo 2",
r"""Core Duo con MSI en todos los niveles; bloques de 16 B, palabras de 4 B. L1I 16 KB y L1D 32 KB (1 ns, escritura directa);
L2 de 2 MB **compartida** (5 ns, post-escritura); memoria 4 GB (100 ns). a está solo en memoria al principio.

Núcleo 1: `sleep(2 s)` · **T1** · lee a[0..39] · `sleep(3 s)` · **T2** · escribe a[j] = j · **T3**
Núcleo 2: **T0** · lee a[0..39] · `sleep(10 s)` · **T4** · vuelve a leer a[0..39] · **T5**
(T0 < T1 < … < T5; los bucles tardan un tiempo despreciable.)

1. Estado del bloque de a[0] en la L1D del núcleo 1 en T0…T5. 2. Lo mismo en el núcleo 2. 3. Tiempo de acceso a datos del
código del núcleo 2.""" + MSI,
r"""**1. L1D del núcleo 1**

| T0 | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| I | I | S | M | M | S |

En T1 aún no ha leído (el bucle va después de T1). Tras leer → S (en T2). Al escribir → M (las demás copias se invalidan).
En T5 el núcleo 2 ha vuelto a leer → el núcleo 1 pasa a S.

**2. L1D del núcleo 2**

| T0 | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| I | S | S | I | I | S |

Lee al principio (S), la escritura del núcleo 1 lo invalida (I en T3 y T4) y vuelve a leer (S en T5).

**3.** 40 elementos = 10 bloques de 4 palabras.
- **Primer bucle:** cada bloque falla en L1 y en L2 → $1 + 5 + 100 = 106$ ns; las otras 3 palabras aciertan (1 ns):
  $10\cdot106 + 30\cdot1 = 1090$ ns.
- **Segundo bucle:** L1 inválida, pero la L2 compartida tiene los datos nuevos (la L1 del núcleo 1 es de escritura directa)
  → $1 + 5 = 6$ ns por bloque: $10\cdot6 + 30 = 90$ ns.

**Total: 1180 ns** (sin contar los *sleep*).""",
origen="Enero de 2013", respuestas=[R("3) ns", 1180)]),

Ejercicio("mp-7", "Cerrojo con test_and_set y espera de 2 ms",
r"""```c
lock(location) {
    acquired = 0;
    while (!acquired) {
        acquired = test_and_set(location);
        if (!acquired) sleep(2 ms);
    }
}
unlock(location) { location = 0; }
```
P0…P3 ejecutan a la vez `lock; cómputo de 3 ms; unlock`. 1. ¿Cuándo adquiere el cerrojo cada uno, si lo hacen en orden
P0, P1, P2, P3? 2. ¿Es eficiente? 3. Una mejora.""",
r"""**1.** Cada intento fallido duerme 2 ms, así que solo se reintenta en t = 0, 2, 4, 6…

| Procesador | Lo adquiere | Lo suelta | Intentos fallidos |
|---|---|---|---|
| P0 | **0 ms** | 3 ms | — |
| P1 | **4 ms** | 7 ms | 0, 2 |
| P2 | **8 ms** | 11 ms | 0, 2, 4, 6 |
| P3 | **12 ms** | 15 ms | 0, 2, 4, 6, 8, 10 |

**2. No.** El cerrojo queda **libre sin que nadie lo use** 1 ms en cada traspaso (3→4, 7→8, 11→12): 3 ms perdidos de 15.
Además cada `test_and_set` es una **escritura**: aunque falle, invalida el bloque en las demás cachés y genera tráfico.

**3.** Mejoras: **test-and-test-and-set** (girar leyendo la copia local y solo hacer test_and_set cuando se ve libre),
**espera exponencial** (*backoff*) con tiempos menores o aleatorios, usar **LL/SC**, o cerrojos con **cola** (ticket lock,
MCS) que entregan el cerrojo directamente al siguiente en cuanto se libera.""",
origen="Enero de 2013", respuestas=[R("P1 (ms)", 4), R("P2 (ms)", 8), R("P3 (ms)", 12)]),

Ejercicio("mp-8", "lock/unlock con test_and_set y tiempo de bus",
r"""2 procesos en P1 y P2 con bus de 100 Mbps, cachés privadas vacías, MSI. Ambos ejecutan a la vez `lock(l); cómputo de
100 ms; unlock(l)`. 1. Implemente lock y unlock con `test_and_set Registro Dir`. 2. Si un fallo de caché transfiere 8 bytes y
una invalidación 16 bytes, ¿tiempo total (solo fallos, invalidaciones y cómputo)? 3. Diferencia entre test_and_set y LL/SC.""",
r"""**1.** (Versión *test-and-test-and-set*, la buena para cachés)
```mipsasm
lock:   lw    $t0, 0($a0)          # ¿libre? se gira sobre la copia local (sin tráfico)
        bnez  $t0, lock
        test_and_set $t0, 0($a0)   # lee el valor antiguo y escribe 1, atómicamente
        bnez  $t0, lock            # otro se adelantó
        jr    $ra
unlock: sw    $zero, 0($a0)
        jr    $ra
```
**2.** Bus de 100 Mbps: un fallo (8 B = 64 bits) = **0,64 µs**; una invalidación (16 B) = **1,28 µs**. Secuencia:

| Paso | Evento | Coste |
|---|---|---|
| P1 y P2 leen l | 2 fallos (los dos en S) | 1,28 µs |
| P1 test_and_set | invalidación (P1 → M, gana) | 1,28 µs |
| P2 test_and_set | fallo + invalidación (P2 → M, falla) | 1,92 µs |
| P2 gira leyendo | aciertos en su caché | 0 |
| P1 cómputo | | 100 ms |
| P1 unlock | fallo + invalidación | 1,92 µs |
| P2 lee l = 0 | fallo | 0,64 µs |
| P2 test_and_set | invalidación (gana) | 1,28 µs |
| P2 cómputo + unlock (acierto en M) | | 100 ms |

**Total ≈ 200 ms + 8,32 µs ≈ 200,008 ms**: el coste del protocolo es despreciable frente a las secciones críticas, que se
ejecutan **una detrás de otra**.

**3.** `test_and_set` **siempre escribe** (aunque el cerrojo esté cogido), así que cada intento invalida la línea en las demás
cachés → mucho tráfico si muchos giran con él. **LL/SC** separa la lectura (LL, que se queda en caché sin invalidar a nadie)
de la escritura condicional (SC, que solo escribe si nadie ha tocado la dirección): menos tráfico, mejor escalabilidad, y
sirve para construir otras operaciones atómicas (fetch&add, compare&swap).""",
origen="Junio de 2013", respuestas=[R("Fallo de 8 B (µs)", 0.64), R("Invalidación (µs)", 1.28)]),

Ejercicio("mp-9", "Consistencia: X = 1 desde dos procesadores",
r"""Variables compartidas a 0; accesos atómicos. P1: `X=1;` · P2: `Print(X); Print(Y);` · P3: `X=1; Print(X);`
Para cada uno de los 8 resultados (Print(X) de P2, Print(Y), Print(X) de P3), ¿es posible? Si lo es, dé un orden total.
Indique un resultado imposible con consistencia secuencial pero posible con modelos relajados.""",
r"""**Enumerando todas las intercalaciones** (la app las genera todas):

""" + T9 + r"""
Razones: **nadie escribe Y** → Print(Y) siempre es 0; y **P3 lee X después de escribirla él mismo** → siempre ve 1.

**Modelos relajados:** aquí no aparece ningún resultado nuevo. Incluso los modelos relajados garantizan que un procesador ve
sus propias escrituras (orden de programa sobre la misma dirección) y no se pueden inventar valores (Y = 1 nunca). Es un
ejemplo de que relajar la consistencia **no** siempre cambia el resultado.""",
respuestas=[R("¿Cuántos resultados son posibles?", 2)], herramienta="Consistencia"),

Ejercicio("mp-10", "Consistencia con un flag",
r"""Variables a 0. P1: `A=1; Print(flag);` · P2: `while (flag==0); Print(A);` · P3: `flag=1; Print(A);`
Mismas preguntas que el anterior.""",
r"""""" + T10 + r"""
- Si P1 imprime flag = 0, su `A=1` ocurrió **antes** que `flag=1`, y P2 y P3 leen A después de flag=1 → los dos ven A = 1.
  Por eso **(0, x, 0)** y **(0, 0, x)** son imposibles con consistencia secuencial.
- **Con modelos relajados** (por ejemplo TSO de x86, con búfer de escrituras): P1 deja `A=1` en su búfer y lee flag = 0; P3
  deja `flag=1` y lee A = 0 de memoria. Resultado **(0, —, 0)** posible: es el clásico patrón de Dekker. Y con escrituras
  que se reordenan entre sí (PSO) también **(0, 0, x)**.""",
respuestas=[R("¿Cuántos resultados son posibles con SC?", 5)], herramienta="Consistencia"),

Ejercicio("mp-11", "Causalidad: U = A, B = 1, V = B, W = A",
r"""Variables a 0. P1: `A=1;` · P2: `U=A; B=1;` · P3: `V=B; W=A;` Mismas preguntas (resultados de U, V, W).""",
r"""""" + T11 + r"""
El único imposible con SC es **(U, V, W) = (1, 1, 0)**: si P2 vio A = 1 y después escribió B = 1, y P3 vio B = 1, entonces
P3 tendría que ver también A = 1 (**causalidad**).

**Con modelos relajados** (sin atomicidad de escrituras «multi-copia», como POWER o ARM, o si P3 reordena sus dos lecturas)
**(1, 1, 0) sí es posible**: la escritura A = 1 puede haber llegado a P2 pero todavía no a P3.""",
respuestas=[R("¿Cuántos resultados son posibles con SC?", 7)], herramienta="Consistencia"),

Ejercicio("mp-12", "Resultados finales de X e Y",
r"""2 procesadores, variables a 0. P1: `X=1; Y=X;` · P2: `Y=2; X=3;`
¿Qué resultados (X, Y) son posibles con consistencia secuencial? ¿Alguno es posible solo con consistencia relajada?
¿Es posible (3, 0)?""",
r"""**Con consistencia secuencial** (enumerando las 6 intercalaciones): """ + R12_TXT + r""".

- **Solo con consistencia relajada: (1, 2).** Necesita X = 1 al final (X=3 antes que X=1) y Y = 2 al final (Y=2 después
  de Y=X). Con SC, P2 hace Y=2 antes que X=3, así que el orden sería Y=2 → X=3 → X=1 → Y=X, que da Y = 1. Si P2 puede
  **reordenar sus dos escrituras** (X=3 antes que Y=2, como en PSO), sale (1, 2).
- **(3, 0) es imposible** en cualquier modelo: Y se escribe siempre (con 2, o con el valor de X, que ya es 1 o 3), así que no
  puede quedar en 0.""",
respuestas=[R("¿Es posible (3,0)? (si/no)", ["no"], "texto")], herramienta="Consistencia"),
], icono="🤝")
