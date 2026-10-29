from contenido.base import Ejercicio, Hoja, Respuesta
from contenido.pipe_util import ciclos_iteracion, cronograma, deps_md, flujo_con_extras
from core.segmentacion import Config, diagrama, leer_codigo, flujo_bucle

R = Respuesta
LEYENDA = ("\n\n*Cómo leer el cronograma:* cada fila es una instrucción y cada columna un ciclo; «—» es un ciclo en que "
           "la instrucción está **detenida** (esperando un dato o a que quede libre la etapa siguiente). *Generado con el "
           "modelo de pipeline de la app (Herramientas → Segmentación), donde puedes cambiar las condiciones.*")


def asm(c):
    return "\n```mipsasm\n" + c.strip("\n") + "\n```\n"


# ======================================================================= 1. latencias adicionales (jun 2015)
E1 = """\
bucle: ldc1  $f0, ($t0)
       ldc1  $f2, ($t1)
       add.d $f4, $f0, $f2
       mul.d $f4, $f4, $f6
       sdc1  $f4, ($t2)
       addi  $t0, $t0, 8
       addi  $t1, $t1, 8
       subi  $t3, $t3, 1
       bnez  $t3, bucle
       addi  $t2, $t2, 8"""

E1_TABLA = """| Ciclo | Instrucción | Por qué |
|---|---|---|
| 1 | `ldc1 $f0, ($t0)` | |
| 2 | `ldc1 $f2, ($t1)` | |
| 3–4 | *2 detenciones* | add.d necesita $f2: ldc1 tiene latencia adicional +2 |
| 5 | `add.d $f4, $f0, $f2` | |
| 6–9 | *4 detenciones* | mul.d necesita $f4: add.d +4 |
| 10 | `mul.d $f4, $f4, $f6` | |
| 11–16 | *6 detenciones* | sdc1 necesita $f4: mul.d +6 |
| 17 | `sdc1 $f4, ($t2)` | |
| 18 | `addi $t0, $t0, 8` | |
| 19 | `addi $t1, $t1, 8` | |
| 20 | `subi $t3, $t3, 1` | |
| 21 | `bnez $t3, bucle` | subi tiene latencia +0: sin espera |
| 22 | `addi $t2, $t2, 8` | hueco de retardo (*delay slot*): se ejecuta siempre |"""

E1_PLAN = """\
bucle: ldc1  $f0, 0($t0)
       ldc1  $f2, 0($t1)
       addi  $t0, $t0, 8        # adelantadas: no dependen de nada
       addi  $t1, $t1, 8
       add.d $f4, $f0, $f2      # ciclo 5: $f2 ya está (2 + 1 + 2)
       subi  $t3, $t3, 1
       # 3 detenciones (ciclos 7–9)
       mul.d $f4, $f4, $f6      # ciclo 10
       addi  $t2, $t2, 8
       bnez  $t3, bucle         # ciclo 12
       # 4 detenciones (ciclos 13–16)
       sdc1  $f4, -8($t2)       # ciclo 17, en el hueco de retardo ($t2 ya avanzó: −8)"""

E1_DES = """\
bucle: ldc1  $f0, 0($t0)        # 1
       ldc1  $f2, 0($t1)        # 2
       ldc1  $f8, 8($t0)        # 3
       ldc1  $f10, 8($t1)       # 4
       ldc1  $f12, 16($t0)      # 5
       ldc1  $f14, 16($t1)      # 6
       ldc1  $f16, 24($t0)      # 7
       ldc1  $f18, 24($t1)      # 8
       add.d $f4, $f0, $f2      # 9
       add.d $f20, $f8, $f10    # 10
       add.d $f22, $f12, $f14   # 11
       add.d $f24, $f16, $f18   # 12  ($f18 listo en 8 + 3 = 11 ✓)
       addi  $t0, $t0, 32       # 13  (rellena el hueco: mul.d no puede ir antes del 14)
       mul.d $f4, $f4, $f6      # 14  (9 + 5)
       mul.d $f20, $f20, $f6    # 15
       mul.d $f22, $f22, $f6    # 16
       mul.d $f24, $f24, $f6    # 17
       addi  $t1, $t1, 32       # 18
       subi  $t3, $t3, 4        # 19
       addi  $t2, $t2, 32       # 20
       sdc1  $f4, -32($t2)      # 21  (14 + 7 ✓)
       sdc1  $f20, -24($t2)     # 22
       sdc1  $f22, -16($t2)     # 23
       bnez  $t3, bucle         # 24
       sdc1  $f24, -8($t2)      # 25  hueco de retardo (17 + 7 = 24 ✓)"""

# ======================================================================= 2. cachés + pipeline (ene 2015)
E2 = """\
bucle: lw   $r2, 0($r0)
       addi $r3, $r2, 20
       sw   $r3, 0($r1)
       addi $r0, $r0, 4
       addi $r1, $r1, 4
       bnez $r2, bucle"""
# acierto L1 = 4 ciclos; fallo L1 + acierto L2 = 4 + 14; fallo en ambos = 4 + 14 + 80
_F1, _F2 = flujo_con_extras(E2, [{"IF": 97, "M": 97}, {"IF": 3}, {"IF": 3, "M": 97}, {"IF": 3}, {"IF": 3}, {"IF": 97}]), None
_I1_FILAS, _I1_TOTAL = diagrama(_F1[0], Config(), _F1[1])
_I2 = flujo_con_extras(E2, [{"IF": 3, "M": 3}, {"IF": 3}, {"IF": 3, "M": 3}, {"IF": 3}, {"IF": 3}, {"IF": 3}])
_I2_FILAS, _I2_TOTAL = diagrama(_I2[0], Config(), _I2[1])


def _tabla_etapas(filas, desplaz=0):
    t = "| Instrucción | IF | ID | EX | M | WB |\n|---|---|---|---|---|---|\n"
    for f in filas:
        txt = f.texto.split(":")[-1].strip()
        c = []
        for e in ("IF", "ID", "EX", "M", "WB"):
            a, b = f.etapas[e]
            a, b = a + desplaz, b + desplaz
            c.append(str(a) if a == b else f"{a}–{b}")
        t += f"| `{txt}` | " + " | ".join(c) + " |\n"
    return t


# ======================================================================= 3 y 4. cronogramas (oct 2014)
E3 = """\
bucle: lw    $f0, 0($r1)
       lw    $f2, 0($r2)
       mul.f $f4, $f0, $f2
       add.d $f6, $f6, $f4
       addi  $r1, $r1, 4
       addi  $r2, $r2, 4
       sub   $r3, $r3, 1
       bnez  $r3, bucle"""
E4 = """\
bucle: lw    $f0, 0($r1)
       lw    $f2, 0($r2)
       sub.f $f4, $f0, $f2
       mul.d $f4, $f4, $f4
       add.d $f6, $f6, $f4
       addi  $r1, $r1, 4
       addi  $r2, $r2, 4
       sub   $r3, $r3, 1
       bnez  $r3, bucle"""
SIN_FW = Config(forwarding=False, salto="vaciado", salto_resuelto_en="EX")
CON_FW_T = Config(forwarding=True, salto="tomado", salto_resuelto_en="EX")


def _cron_y_formula(cod, cfg):
    md, tot, _ = cronograma(cod, cfg)
    a, b = ciclos_iteracion(cod, cfg)
    return md, tot, a, b


E3_A = _cron_y_formula(E3, SIN_FW)
E3_B = _cron_y_formula(E3, CON_FW_T)
E4_A = _cron_y_formula(E4, SIN_FW)
E4_B = _cron_y_formula(E4, CON_FW_T)

# ======================================================================= 6. memoria de 2 ciclos (ene 2014)
E6 = """\
i0: lw   $r4, 0($r1)
    lw   $r5, 0($r2)
    add  $r4, $r4, $r5
    sw   $r4, 0($r3)
    addi $r1, $r1, 4
    addi $r2, $r2, 4
    addi $r3, $r3, 4
    bne  $r3, $r0, i0"""
CFG6 = Config(forwarding=False, salto="vaciado", salto_resuelto_en="EX",
              extra={("load", "M"): 1, ("store", "M"): 1, ("branch", "EX"): 1})
E6_DES = """\
i0: lw   $r4, 0($r1)
    lw   $r5, 0($r2)
    lw   $r6, 4($r1)
    lw   $r7, 4($r2)
    lw   $r8, 8($r1)
    lw   $r9, 8($r2)
    lw   $r10, 12($r1)
    lw   $r11, 12($r2)
    add  $r4, $r4, $r5
    add  $r6, $r6, $r7
    add  $r8, $r8, $r9
    add  $r10, $r10, $r11
    sw   $r4, 0($r3)
    sw   $r6, 4($r3)
    sw   $r8, 8($r3)
    sw   $r10, 12($r3)
    addi $r1, $r1, 16
    addi $r2, $r2, 16
    addi $r3, $r3, 16
    bne  $r3, $r0, i0"""
E6_A = _cron_y_formula(E6, CFG6)
E6_D = _cron_y_formula(E6_DES, CFG6)
E6_T1000 = E6_A[2] * 1000 + E6_A[3]
E6_T250 = E6_D[2] * 250 + E6_D[3]

# ======================================================================= 7. (oct 2013)
E7 = """\
i0: lw   $r3, 0($r0)
    lw   $r1, 0($r3)
    addi $r1, $r1, 1
    sub  $r4, $r3, $r2
    sw   $r1, 0($r3)
    bnz  $r4, i0"""
CFG7 = Config(forwarding=False, salto="vaciado", salto_resuelto_en="EX",
              extra={("load", "M"): 2, ("store", "M"): 2, ("branch", "EX"): 1})
CFG7T = Config(forwarding=False, salto="tomado", salto_resuelto_en="EX",
               extra={("load", "M"): 2, ("store", "M"): 2, ("branch", "EX"): 1})
E7_A = _cron_y_formula(E7, CFG7)
E7_B = _cron_y_formula(E7, CFG7T)

# ======================================================================= 8. (oct 2013)
E8 = """\
Loop: LD   R4, 0(R1)
      DIV  R2, R2, R4
      ADD  R1, R1, #1
      SUB  R5, R5, #1
      SD   R4, 0(R5)
      SUB  R6, R1, R5
      BNEZ R6, Loop"""
CFG8 = Config(forwarding=False, salto="vaciado", salto_resuelto_en="EX", extra={("load", "M"): 1})
E8_A = _cron_y_formula(E8, CFG8)
_f8, _t8, _ = flujo_bucle(leer_codigo(E8), 4)
E8_TOTAL4 = diagrama(_f8, CFG8, _t8)[1]

# ======================================================================= 9. (oct 2013)
E9 = """\
Bucle: LD  R4, 0(R2)
       LD  R5, 0(R3)
       ADD R6, R4, R5
       SD  R6, 0(R3)
       BNZ R6, Bucle"""
CFG9 = Config(forwarding=True, salto="vaciado", salto_resuelto_en="EX", extra={("load", "M"): 2, ("store", "M"): 2})
E9_A = _cron_y_formula(E9, CFG9)

# ======================================================================= 11. (ene 2013)
E11 = """\
      ADDI  R3, R3, 1
Loop: LD    R4, 0(16)
      MULT  R5, R4, R4
      ADD   R5, R3, R5
      SD    R5, 0(16)
      DADDI R3, R4, 1
      DADDI R1, R1, 1
      BNE   R1, R2, Loop"""
CFG11 = Config(forwarding=True, salto="no_tomado", salto_resuelto_en="EX",
               extra={("load", "WB"): 1, ("store", "ID"): 1, ("mult", "EX"): 1, ("add", "EX"): 1})
E11_A = _cron_y_formula(E11, CFG11)
E11_TOT = E11_A[2] * 999 + E11_A[3]

# ======================================================================= 12. (jun 2012)
E12 = """\
Bucle: LD   R4, 0(R2)
       LD   R5, 0(R3)
       ADD  R6, R4, R5
       SD   R6, 0(R3)
       ADD  R6, R6, R4
       ADDI R3, R3, #8
       SUB  R20, R4, R3
       BNZ  R20, Bucle"""
CFG12 = Config(forwarding=False, banco_partido=True, salto="vaciado", salto_resuelto_en="EX", extra_if=1,
               extra={("load", "M"): 1, ("store", "M"): 1})
E12_A = _cron_y_formula(E12, CFG12)


def _md(t):
    return t[0]


HOJA = Hoja("ilp", "Paralelismo a nivel de instrucción", "fc",
            "Arquitectura de Computadores · Ejercicios de ILP (J. D. García et al., ARCOS-UC3M)",
            "Dependencias, detenciones, cronogramas con y sin forwarding, planificación y desenrollado de bucles.", [

Ejercicio("ilp-1", "Latencias adicionales, planificación y desenrollado ×4",
r"""Procesador segmentado tipo MIPS con bancos de registros enteros y de coma flotante (dobles: $f0, $f2…$f30). Se puede
iniciar una instrucción por ciclo salvo detenciones por dependencias de datos. Latencias **adicionales** (solo si hay
dependencia): ldc1 +2, sdc1 +2, add.d +4, mul.d +6, addi +0, subi +0, bnez +1. `bnez` usa **salto retardado con un hueco**.""" +
asm(E1) + r"""
Inicialmente $t0 = 0x00100000, $t1 = 0x00140000, $t2 = 0x00180000, $t3 = 0x100.
1. Dependencias RAW. 2. Detenciones y ciclos por iteración. 3. Planifique el bucle. 4. Desenróllelo para procesar 4
posiciones por iteración (con registros reales) y calcule el speedup.""",
r"""**1. Dependencias RAW**

""" + deps_md(E1, ("RAW",)) + r"""
**2. Detenciones** (una instrucción por ciclo; si usa un resultado, espera la latencia adicional del productor):

""" + E1_TABLA + r"""

**22 ciclos por iteración** (10 instrucciones + 12 detenciones). Con $t3 = 0x100 = 256 iteraciones → 5632 ciclos.

**3. Planificación:** adelantamos los `addi` (que no dependen de nada) para rellenar huecos y metemos el `sdc1` en el hueco
de retardo, corrigiendo su desplazamiento porque $t2 ya se ha incrementado:""" + asm(E1_PLAN) + r"""
**17 ciclos** por iteración (7 detenciones). Speedup = 22/17 ≈ 1,29.

**4. Desenrollado ×4** (64 iteraciones; registros distintos para cada copia para no crear dependencias falsas):""" +
asm(E1_DES) + r"""
**25 ciclos para 4 elementos y ninguna detención** (6,25 ciclos/elemento frente a 22).
$$\text{Speedup} = \frac{4\cdot22}{25} = \frac{88}{25} = \mathbf{3{,}52}$$
(Total: 64 · 25 = 1600 ciclos frente a 5632.)""",
respuestas=[R("2) Ciclos por iteración", 22), R("3) Ciclos planificado", 17), R("4) Ciclos por iteración desenrollada", 25),
            R("4) Speedup", 3.52)], herramienta="Segmentación"),

Ejercicio("ilp-2", "Cachés L1/L2 y cronograma con fallos",
r"""Código almacenado desde 0x1000100C (4 bytes por instrucción):""" + asm(E2) + r"""
L1 de datos y L1 de instrucciones: 2 vías, 32 KB; L2 unificada: 8 vías, 1 MB; líneas de 32 bytes. Acierto en L1: 4 ciclos;
acierto en L2: 14 ciclos adicionales; traer un bloque de memoria a L2: 80 ciclos. Post-escritura.
$r0 = 0x00010000, $r1 = 0x00080000. Desde 0x00010000 todos los valores son ≠ 0 hasta 0x000100FC, que vale 0.
1. Tiempo medio de acceso de *otro* programa con 2 accesos a datos por instrucción y tasas de fallo L1I 10 %, L1D 5 %,
L2 2 %. 2. Fallos en L1D, L1I y L2 de este código. 3. Cronograma de la primera iteración (5 etapas, sin forwarding, banco
que escribe y lee en el mismo ciclo, saltos vaciando el pipeline y resueltos en EX, cachés vacías). 4. Segunda iteración.""",
r"""**1.** Penalización desde L1: $14 + 0{,}02\cdot80 = 15{,}6$ ciclos.
- Instrucciones: $4 + 0{,}10\cdot15{,}6 = 5{,}56$ ciclos. Datos: $4 + 0{,}05\cdot15{,}6 = 4{,}78$ ciclos.
- Por instrucción hay 1 acceso a instrucción y 2 a datos:
$$T_m = \frac{1\cdot5{,}56 + 2\cdot4{,}78}{3} = \frac{15{,}12}{3} = \mathbf{5{,}04\ ciclos}.$$

**2. Fallos.** El bucle lee desde 0x10000 hasta encontrar el 0 en 0x100FC → **64 iteraciones**.
- **L1I:** el código ocupa 0x1000100C–0x10001023 → dos líneas (0x10001000–0x1000101F, que tiene las 5 primeras, y
  0x10001020, que tiene `bnez`) → **2 fallos**.
- **L1D:** lecturas 0x10000–0x100FF = 256 B = 8 líneas → 8 fallos; escrituras 0x80000–0x800FF → 8 fallos (con
  post-escritura se trae el bloque al escribir). Los dos vectores caen en el mismo conjunto pero hay 2 vías → **16 fallos**.
- **L2:** recibe todos esos fallos y todos son bloques nuevos → **18 fallos**.

**3. Primera iteración** (todo frío): `lw` falla en IF (4 + 14 + 80 = 98 ciclos) y en M (98); `addi`, `sw`, `addi`,
`addi` aciertan en IF (4 ciclos); `sw` falla en M (98); `bnez` está en otra línea y falla en IF (98). Inicio y fin de cada
etapa:

""" + _tabla_etapas(_I1_FILAS) + f"""
La primera iteración termina en el ciclo **{_I1_TOTAL}**.

**4. Segunda iteración** (todo acierta en L1: 4 ciclos en IF y 4 en M para lw/sw), contando desde su primer ciclo:

""" + _tabla_etapas(_I2_FILAS) + f"""
Dura **{_I2_TOTAL} ciclos**. La dependencia lw → addi (sin forwarding) y bnez → siguiente fetch son las que más frenan.
*(Las cifras exactas dependen de cómo se dibuje el solapamiento; este cronograma sigue el modelo de la app.)*""",
respuestas=[R("1) Tm (ciclos)", 5.04), R("2) Fallos L1I", 2), R("2) Fallos L1D", 16), R("2) Fallos L2", 18)],
herramienta="Segmentación"),

Ejercicio("ilp-3", "Cronograma sin y con forwarding (mul.f)",
asm(E3) + r"""
1. Lista de todas las dependencias (registro, origen, destino, tipo). 2. Cronograma en un MIPS de 5 etapas sin forwarding,
banco que escribe y lee en el mismo ciclo, saltos vaciando el pipeline, memoria de 1 ciclo y salto resuelto en EX.
3. Ciclos para N iteraciones. 4. Cronograma con forwarding completo y predicción «siempre tomado». 5. Ciclos para N.""",
r"""**1. Dependencias**

""" + deps_md(E3) + r"""
**2. Sin forwarding** (un dato solo se puede leer en ID en el mismo ciclo en que el productor hace WB):

""" + E3_A[0] + f"""
**3.** El fetch de la siguiente iteración espera a que `bnez` termine EX. Ciclos para N iteraciones:
**{E3_A[2]}·N + {E3_A[3]}** (una iteración: {E3_A[1]} ciclos).

**4. Con forwarding y predicción «tomado»** (el destino se conoce al final de ID, así que la siguiente iteración se
capta en el ciclo siguiente a ese ID):

""" + E3_B[0] + f"""
**5.** Ciclos para N iteraciones: **{E3_B[2]}·N + {E3_B[3]}**. La única detención que queda es la de load → uso
(el dato de `lw` no existe hasta el final de M).""" + LEYENDA,
respuestas=[R("3) Ciclos por iteración (sin forwarding)", E3_A[2]), R("5) Ciclos por iteración (con forwarding)", E3_B[2])],
herramienta="Segmentación"),

Ejercicio("ilp-4", "Cronograma sin y con forwarding (sub.f + mul.d)",
asm(E4) + r"""
Mismas preguntas y condiciones que el ejercicio anterior.""",
r"""**1. Dependencias**

""" + deps_md(E4) + r"""
**2. Sin forwarding:**

""" + E4_A[0] + f"""
**3.** N iteraciones: **{E4_A[2]}·N + {E4_A[3]}**.

**4. Con forwarding y predicción «tomado»:**

""" + E4_B[0] + f"""
**5.** N iteraciones: **{E4_B[2]}·N + {E4_B[3]}**.""" + LEYENDA,
respuestas=[R("3) Ciclos por iteración (sin forwarding)", E4_A[2]), R("5) Ciclos por iteración (con forwarding)", E4_B[2])],
herramienta="Segmentación"),

Ejercicio("ilp-5", "Tabla de latencias: planificar y desenrollar ×2 y ×4",
r"""Latencias entre instrucciones: ALU FP → otra ALU FP: 6; ALU FP → almacenar doble: 3; cargar doble → ALU FP: 2;
cargar doble → almacenar doble: 0.
```
BUCLE: L.D    F0, 0(R1)
       L.D    F2, 0(R2)
       ADD.D  F4, F0, F2
       S.D    F4, 0(R3)
       DADDUI R1, R1, #-8
       BNE    R1, R4, BUCLE
```
Los arrays tienen 4000 elementos. Ciclos totales: 1) sin modificar; 2) planificando; 3) desenrollando ×2; 4) ×4.""",
r"""Supuestos: una instrucción por ciclo; las latencias que no están en la tabla valen 0; el salto no añade ciclos.
**Latencia L** significa que entre productor y consumidor tiene que haber L ciclos (L detenciones si van seguidos).

**1) Sin modificar:**

| Ciclo | Instrucción |
|---|---|
| 1 | L.D F0 |
| 2 | L.D F2 |
| 3–4 | *detención ×2* (cargar → ALU FP: 2) |
| 5 | ADD.D F4 |
| 6–8 | *detención ×3* (ALU FP → almacenar: 3) |
| 9 | S.D F4 |
| 10 | DADDUI |
| 11 | BNE |

**11 ciclos** × 4000 = **44 000 ciclos**.

**2) Planificado:** subir el DADDUI para rellenar un hueco (y corregir el desplazamiento del S.D si usara R1; aquí usa R3):
`L.D F0 · L.D F2 · DADDUI · (1 det.) · ADD.D · (3 det.) · S.D · BNE` = **10 ciclos** → **40 000 ciclos**.

**3) Desenrollado ×2** (2000 iteraciones):
```
L.D F0,0(R1) · L.D F2,0(R2) · L.D F6,-8(R1) · L.D F8,-8(R2)
ADD.D F4,F0,F2       (ciclo 5)
DADDUI R1,R1,#-16    (6)
ADD.D F10,F6,F8      (7)
(1 det.)             (8)
S.D F4,0(R3)         (9)
(1 det.)             (10)
S.D F10,-8(R3)       (11)
BNE R1,R4,BUCLE      (12)
```
**12 ciclos** cada 2 elementos → **24 000 ciclos**.

**4) Desenrollado ×4** (1000 iteraciones): 8 L.D (1–8), 4 ADD.D (9–12, ninguno espera), DADDUI R1,R1,#-32 (13), 4 S.D
(14–17, cada uno 4 ciclos después de su ADD.D ✓) y BNE (18) → **18 ciclos**, sin detenciones → **18 000 ciclos**.

Speedup frente al original: 44 000 / 18 000 ≈ **2,44**.""",
errata="El bucle solo decrementa R1: R2 y R3 nunca cambian, así que leería y escribiría siempre los mismos elementos. "
       "Faltan «DADDUI R2, R2, #-8» y «DADDUI R3, R3, #-8» (se resuelve con el código tal cual, como pide el enunciado).",
respuestas=[R("1) Ciclos totales", 44000), R("2) Planificado", 40000), R("3) ×2", 24000), R("4) ×4", 18000)],
herramienta="Segmentación"),

Ejercicio("ilp-6", "Memoria de 2 ciclos, saltos lentos y desenrollado ×4",
asm(E6) + r"""
5 etapas sin forwarding. Todo tarda un ciclo por etapa salvo: cargas y almacenamientos, 2 ciclos en M; saltos, 2 ciclos en
EX; sin predicción de saltos. 1. Riesgos RAW con impacto. 2. Cronograma de una iteración. 3. Ciclos por iteración.
4. Desenrolle ×4 (1000 iteraciones). 5. Speedup.""",
r"""**1. Riesgos RAW** (los que detienen el pipeline: productor cerca del consumidor):

""" + deps_md(E6, ("RAW",)) + r"""
Los que de verdad cuestan ciclos son **$r5 (i1 → i2)**, **$r4 (i2 → i3)** y **$r3 (i6 → i7)**; los que vienen de la vuelta
anterior quedan lejos y ya están escritos.

**2. Cronograma** (supuesto: el banco escribe en la 1.ª mitad del ciclo y lee en la 2.ª; sin predicción, la siguiente
instrucción se capta cuando el salto acaba EX):

""" + E6_A[0] + f"""
**3.** En régimen estacionario: **{E6_A[2]} ciclos por iteración** (total para N: {E6_A[2]}·N + {E6_A[3]}).

**4. Desenrollado ×4** (registros distintos para cada copia; los incrementos se hacen una vez, de 16 en 16):""" +
asm(E6_DES) + f"""
Ciclos por iteración desenrollada: **{E6_D[2]}** (4 elementos).

**5.** 1000 iteraciones originales: {E6_A[2]}·1000 + {E6_A[3]} = {E6_T1000} ciclos; 250 desenrolladas:
{E6_D[2]}·250 + {E6_D[3]} = {E6_T250} ciclos →
$$\\text{{Speedup}} = \\frac{{{E6_T1000}}}{{{E6_T250}}} \\approx \\mathbf{{{E6_T1000 / E6_T250:.2f}}}$$""" + LEYENDA,
respuestas=[R("3) Ciclos por iteración", E6_A[2]), R("5) Speedup", E6_T1000 / E6_T250, tolerancia=5e-3)],
herramienta="Segmentación"),

Ejercicio("ilp-7", "Cargas con 2 ciclos extra: sin predicción y con «tomado»",
asm(E7) + r"""
5 etapas sin forwarding. Cargas y almacenamientos: 2 ciclos adicionales en memoria; saltos: 1 ciclo adicional en EX.
1. Riesgos RAW. 2. Cronograma de una iteración. 3. Ciclos por iteración sin predicción. 4. Con predicción «siempre tomado».""",
r"""**1. RAW**

""" + deps_md(E7, ("RAW",)) + r"""
**2–3. Sin predicción** (el siguiente fetch espera al final del EX del salto):

""" + E7_A[0] + f"""
Ciclos por iteración: **{E7_A[2]}**.

**4. Predicción «tomado»** (se capta el destino al acabar el ID del salto): **{E7_B[2]} ciclos por iteración**.""" + LEYENDA,
respuestas=[R("3) Ciclos/iteración sin predicción", E7_A[2]), R("4) Con predicción tomado", E7_B[2])],
herramienta="Segmentación"),

Ejercicio("ilp-8", "RAW y WAW de un bucle con DIV",
asm(E8) + r"""
R1 y R5 contienen las direcciones del primer y último elemento de un array de 9 entradas (R1 = 0x010, R5 = 0x018).
1. Riesgos RAW y WAW. 2. Cronograma en 5 etapas sin forwarding, congelando el pipeline en el salto y con 1 ciclo adicional
en las lecturas de memoria (LD). 3. Ciclos de todo el bucle.""",
r"""**1. RAW y WAW**

""" + deps_md(E8, ("RAW", "WAW")) + r"""
**¿Cuántas vueltas?** R6 = R1 − R5 empieza en 0x10 − 0x18 = −8 y cada vuelta R1 sube 1 y R5 baja 1 → R6 sube 2:
−6, −4, −2, 0 → **4 iteraciones**.

**2. Cronograma de una iteración:**

""" + E8_A[0] + f"""
**3.** {E8_A[2]} ciclos por iteración; las 4 iteraciones completas: **{E8_TOTAL4} ciclos**
(fórmula {E8_A[2]}·N + {E8_A[3]}).""" + LEYENDA,
errata="El enunciado dice «las instrucciones R3 y R5»: son los registros R1 y R5.",
respuestas=[R("Iteraciones", 4), R("3) Ciclos totales", E8_TOTAL4)], herramienta="Segmentación"),

Ejercicio("ilp-9", "Sin segmentar y segmentado con forwarding",
asm(E9) + r"""
1. Ciclos de una iteración en un procesador **no segmentado** (acceso a memoria: 3 ciclos; salto: 1 ciclo).
2. Dependencias RAW. 3. Ciclos de una iteración segmentada en 5 etapas con forwarding y congelación en los saltos.""",
r"""**1. No segmentado:** cada instrucción empieza cuando acaba la anterior: LD (3) + LD (3) + ADD (1) + SD (3) + BNZ (1) =
**11 ciclos** (supuesto: las operaciones de ALU tardan 1 ciclo).

**2. RAW**

""" + deps_md(E9, ("RAW",), bucle=False) + r"""
**3. Segmentado** (memoria de 3 ciclos en M, forwarding, el fetch siguiente espera al EX del salto):

""" + E9_A[0] + f"""
**{E9_A[2]} ciclos por iteración** en régimen estacionario.""" + LEYENDA,
respuestas=[R("1) No segmentado", 11), R("3) Segmentado (ciclos/iteración)", E9_A[2])], herramienta="Segmentación"),

Ejercicio("ilp-10", "Bucles anidados con detenciones estructurales",
r"""Cada instrucción cuesta 1 ciclo más los adicionales de la tabla, y las detenciones ocurren **siempre** (haya o no
dependencia). R1 = 0, R2 = 24, R3 = 16.
```
Loop1: LD    F2, 0(R1)
       ADDD  F2, F0, F2
Loop2: LD    F4, 0(R3)
       MULTD F4, F0, F4
       DIVD  F10, F4, F0
       ADDD  F12, F10, F4
       ADDI  R1, R1, #8
       SUB   R18, R2, R1
       BNZ   R18, Loop2
       SD    F2, 0(R3)
       ADDI  R3, R3, #8
       SUB   R20, R2, R3
       BNZ   R20, Loop1
```
Costes adicionales: LD 3, SD 1, ADD 2, MULTD 4, DIVD 10, ADDI 0, SUB 0, BNZ 1.
1. Ciclos de una iteración del bucle exterior con 30 del interior. 2. Igual desenrollando 3 iteraciones del interior.
3. Compare.""",
r"""Como las detenciones son siempre, cada instrucción cuesta **1 + adicional**:

| Instrucción | Ciclos |
|---|---|
| LD | 4 |
| ADDD | 3 |
| MULTD | 5 |
| DIVD | 11 |
| SD | 2 |
| ADDI, SUB | 1 |
| BNZ | 2 |

**1)** Interior: LD 4 + MULTD 5 + DIVD 11 + ADDD 3 + ADDI 1 + SUB 1 + BNZ 2 = **27 ciclos**.
Exterior (sin el interior): LD 4 + ADDD 3 + SD 2 + ADDI 1 + SUB 1 + BNZ 2 = **13 ciclos**.
$$T = 13 + 30\cdot27 = \mathbf{823\ ciclos}.$$

**2)** Desenrollando 3 veces el interior: 3 × (4 + 5 + 11 + 3) = 69 de trabajo + **una sola vez** ADDI R1,R1,#24 + SUB + BNZ
(1 + 1 + 2) = **73 ciclos** por iteración desenrollada; 30/3 = 10 iteraciones:
$$T = 13 + 10\cdot73 = \mathbf{743\ ciclos}.$$
(Copias con registros distintos, p. ej. F4/F6/F8 y F10/F14/F16, F12/F18/F20, para no crear dependencias falsas.)

**3)** Se ahorran 80 ciclos (speedup 823/743 ≈ **1,11**). Solo se gana la sobrecarga del control del bucle (ADDI, SUB y
BNZ de 20 de las 30 vueltas): como aquí las detenciones son estructurales y ocurren siempre, **reordenar no esconde
latencias**; con detenciones por dependencias, el desenrollado permitiría además intercalar instrucciones independientes.""",
respuestas=[R("1) Ciclos", 823), R("2) Ciclos desenrollado", 743)], herramienta="Segmentación"),

Ejercicio("ilp-11", "Riesgos WAW y cronograma con forwarding",
asm(E11) + r"""
R1 = 1 y R2 = 1000. MIPS de 5 etapas, una instrucción por ciclo y forwarding. Todo tarda un ciclo salvo: SD usa un ciclo
adicional para leer R5 del banco (en ID), LD un ciclo adicional para escribir R4 (en WB), y ADD y MULT un ciclo adicional en
la ALU. Predicción «no tomado». 1. Solo los riesgos WAW y cuándo podrían dar un resultado incorrecto. 2. Cronograma y ciclos
totales.""",
r"""**1. WAW**

""" + deps_md(E11, ("WAW",)) + r"""
En un pipeline **en orden** con una sola etapa de escritura (WB) las escrituras se hacen en el orden del programa, así que
estas WAW **no causan errores**. Serían peligrosas si las instrucciones pudieran **terminar fuera de orden** (unidades
funcionales con latencias distintas, ejecución fuera de orden): por ejemplo, si `MULT R5` (lenta) escribiera R5 **después**
que `ADD R5`, quedaría el valor viejo. Se evitan con renombrado de registros.

**2. Cronograma** de la primera iteración (con el ADDI inicial):

""" + E11_A[0] + f"""
R1 va de 1 a 1000 → **999 iteraciones**. En régimen estacionario: {E11_A[2]} ciclos por iteración (cada salto tomado con
predicción «no tomado» paga la penalización). Total ≈ {E11_A[2]}·999 + {E11_A[3]} = **{E11_TOT} ciclos**.""" + LEYENDA,
errata="«LD R4,0(16)»: el 16 hace de registro base (se interpreta como dirección 0 + R16, o como la dirección 16). No afecta a los riesgos.",
respuestas=[R("Iteraciones", 999), R("Ciclos totales", E11_TOT, tolerancia=1e-3)], herramienta="Segmentación"),

Ejercicio("ilp-12", "Todos los accesos a memoria tardan 2 ciclos",
asm(E12) + r"""
1. Dependencias de datos. 2. Temporización en el pipeline de 5 etapas sin forwarding, pero leyendo y escribiendo el banco en
el mismo ciclo; saltos vaciando el pipeline; todos los accesos a memoria (también el fetch) tardan 2 ciclos.""",
r"""**1. Dependencias**

""" + deps_md(E12) + r"""
**2. Cronograma** (IF y M duran 2 ciclos; salto resuelto en EX):

""" + E12_A[0] + f"""
Una iteración: {E12_A[1]} ciclos; en régimen estacionario **{E12_A[2]} ciclos por iteración**. Al ser el fetch de 2 ciclos,
como mucho se capta una instrucción cada 2 ciclos: el pipeline nunca va a más de la mitad de velocidad.""" + LEYENDA,
respuestas=[R("Ciclos por iteración", E12_A[2])], herramienta="Segmentación"),

Ejercicio("ilp-13", "Tabla de latencias con salto de 1 ciclo: planificar y desenrollar ×2",
r"""```
       DADDUI R3, R1, #40     ; I1
BUCLE: L.D    F0, 0(R1)       ; I2
       L.D    F2, 0(R2)       ; I3
       ADD.D  F4, F0, F2      ; I4
       S.D    F4, 0(R1)       ; I5
       DADDUI R1, R1, #8      ; I6
       DADDUI R2, R2, #8      ; I7
       BLE    R1, R3, BUCLE   ; I8
```
Latencias adicionales: ALU FP → ALU FP 5; ALU FP → cargar/almacenar 4; ALU FP → salto 4; cargar → ALU FP 2; cargar →
cargar 1; almacenar → ALU FP 2. El salto tiene latencia de 1 ciclo y no hay hueco de retardo. 1. Dependencias. 2. Ciclos
totales. 3. Planificación y aceleración. 4. Desenrollado ×2 y aceleración.""",
r"""**1. Dependencias:** RAW F0 (I2 → I4), F2 (I3 → I4), F4 (I4 → I5), R1 (I6 → I8 y a I2, I5, I6 de la siguiente vuelta),
R2 (I7 → I3, I7 siguientes), R3 (I1 → I8). WAR: R1 (I2, I5 → I6), R2 (I3 → I7). WAW entre iteraciones de F0, F2, F4, R1, R2.

**¿Cuántas vueltas?** R3 = R1 + 40 y R1 avanza de 8 en 8 mientras R1 ≤ R3: tras cada vuelta R1 = R1₀ + 8k, se repite si
8k ≤ 40 → **6 iteraciones**.

**2. Sin modificar:**

| Ciclo | Instrucción |
|---|---|
| 1 | I2 L.D F0 |
| 2 | I3 L.D F2 |
| 3–4 | *2 detenciones* (cargar → ALU FP) |
| 5 | I4 ADD.D |
| 6–9 | *4 detenciones* (ALU FP → almacenar) |
| 10 | I5 S.D |
| 11 | I6 DADDUI R1 |
| 12 | I7 DADDUI R2 |
| 13 | I8 BLE |
| 14 | *1 detención* (salto) |

**14 ciclos** por iteración → $1 + 6\cdot14 =$ **85 ciclos** (el 1 es I1).

**3. Planificado:** `L.D F0 · L.D F2 · DADDUI R1 · DADDUI R2 · ADD.D (5) · 4 det. · S.D F4,-8(R1) (10) · BLE (11) · 1 det.`
→ **12 ciclos** → $1 + 6\cdot12 = 73$ → aceleración 85/73 ≈ **1,16**.

**4. Desenrollado ×2** (3 iteraciones):
```
L.D F0,0(R1) (1) · L.D F2,0(R2) (2) · L.D F6,8(R1) (3) · L.D F8,8(R2) (4)
ADD.D F4,F0,F2 (5) · DADDUI R1,R1,#16 (6) · ADD.D F10,F6,F8 (7) · DADDUI R2,R2,#16 (8)
(1 det.) (9) · S.D F4,-16(R1) (10) · (1 det.) (11) · S.D F10,-8(R1) (12) · BLE (13) · (1 det.) (14)
```
**14 ciclos cada 2 elementos** → $1 + 3\cdot14 = 43$ → aceleración 85/43 ≈ **1,98**.""",
respuestas=[R("Iteraciones", 6), R("2) Ciclos totales", 85), R("3) Ciclos planificado", 73), R("4) Ciclos desenrollado", 43)],
herramienta="Segmentación"),
], icono="🚀")
