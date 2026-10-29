"""Teoría de Fundamentos / Estructura de Computadores (guía «Temas 3 y 4» + resto de temas de las hojas)."""
from ui.teoria import Tema, S

T0 = Tema("fc0", "Fundamentos de Computadores", 0, "Introducción y representación de la información",
          "Palabra, registros y direcciones; bases; enteros en signo-magnitud, Ca1 y Ca2; coma flotante IEEE 754.", [

S("palabra", "0.1 Computador de n bits", "Hoja «Introducción» · Estructura de Computadores", [
    ("def", "Lo que mide lo mismo que la palabra", r"""
En un computador de **n bits**, salvo que digan otra cosa: palabra = registros = bus de datos = **direcciones** = n bits.
- Con **k bits de dirección** hay $2^k$ direcciones. Si se direcciona **por bytes**, cada dirección es 1 byte →
  $2^k$ bytes de memoria. ($2^{10}$ = K, $2^{20}$ = M, $2^{30}$ = G: $2^{26} = 2^6\cdot2^{20}$ = 64 M.)
- Para numerar **m** cosas (registros, instrucciones) hacen falta $\lceil\log_2 m\rceil$ bits."""),
    ("truco", "Hexadecimal ↔ binario", r"""Cada cifra hexadecimal son **4 bits** exactos (A = 1010, B = 1011, C = 1100, D = 1101, E = 1110, F = 1111): se traduce cifra a cifra."""),
], "Bases y potencias"),

S("enteros", "0.2 Enteros: signo-magnitud, Ca1 y Ca2", "Hoja «Representación de la información»", [
    ("def", "Las tres representaciones con n bits", r"""
| | Cómo se hace el negativo | Rango | Ceros |
|---|---|---|---|
| **Signo-magnitud** | bit de signo + magnitud | $[-(2^{n-1}-1),\ 2^{n-1}-1]$ | dos (+0 y −0) |
| **Ca1** | invertir todos los bits | $[-(2^{n-1}-1),\ 2^{n-1}-1]$ | dos |
| **Ca2** | invertir y **sumar 1** | $[-2^{n-1},\ 2^{n-1}-1]$ | uno |

Ejemplo con 8 bits: +5 = 00000101 → SM: 10000101 · Ca1: 11111010 · Ca2: 11111011."""),
    ("truco", "El peso negativo del Ca2", r"""En Ca2 el bit de más peso **vale $-2^{n-1}$** y el resto como siempre: $110111_{Ca2} = -32 + 16 + 4 + 2 + 1 = -9$. Por eso el más negativo (100…0) no tiene «pareja» positiva."""),
    ("idea", "El cuentakilómetros", r"""En Ca2 los números son un círculo: si al mayor positivo (0111…1) le sumas 1, «das la vuelta» al más negativo (1000…0). Es el **desbordamiento** (overflow): `add` en MIPS lo avisa con una excepción; `addu` no."""),
], "Representación de enteros"),

S("ieee", "0.3 Coma flotante IEEE 754", "Hoja «Representación de la información»", [
    ("def", "Simple precisión (32 bits)", r"""
| Signo (1) | Exponente (8, exceso 127) | Mantisa (23, sin el 1 implícito) |
|---|---|---|

Valor normalizado: $(-1)^s\cdot1{,}m\cdot2^{E-127}$. Doble: 1 + 11 (exceso 1023) + 52. Media (16 bits): 1 + 5 (exceso 15) + 10.

| Exponente | Mantisa | Significa |
|---|---|---|
| 00000000 | 0 | **±0** |
| 00000000 | ≠ 0 | **no normalizado**: $0{,}m\cdot2^{-126}$ |
| 1…254 | cualquiera | normalizado |
| 11111111 | 0 | **±∞** |
| 11111111 | ≠ 0 | **NaN** |"""),
    ("pasos", "Pasar un número a IEEE 754", r"""
1. Pasar a binario: $14 = 1110$. 2. Normalizar: $1{,}110\cdot2^3$. 3. Exponente + 127: $130 = 10000010$.
4. Mantisa sin el 1: $110\,0\ldots0$. → `0 10000010 11000…0` = **0x41600000**."""),
    ("pasos", "Sumar y multiplicar", r"""
**Suma**: igualar exponentes (desplazar la mantisa del pequeño) → sumar mantisas → normalizar → redondear.
**Producto**: signos con XOR → exponentes se **suman** (restando un exceso) → mantisas se multiplican → normalizar.
Los **dígitos de guarda y redondeo** guardan los bits que se salen al desplazar: el resultado es más exacto."""),
    ("ojo", "Precisión", r"""Un float tiene **24 bits significativos**: no todos los enteros de 32 bits caben exactos (el primero que falla es $2^{24}+1$). Y 0,1 no es exacto en binario (periódico): por eso `0.1 + 0.2 != 0.3` en Python y en C."""),
], "IEEE 754"),
])

T1 = Tema("fc1", "Fundamentos de Computadores", 1, "Ensamblador I: el MIPS 32 y tu primer programa",
          "Instrucción máquina, ISA, CISC y RISC, ciclo de ejecución, registros, mapa de memoria, directivas y syscall.", [

S("isa", "1.1 Instrucciones, ISA, CISC y RISC", "Guía Temas 3 y 4 · cap. 1", [
    ("idea", "El cuaderno de cocina", r"""En unas páginas está la receta (**instrucciones**) y en otras los ingredientes (**datos**): todo con el mismo bolígrafo y en el mismo cuaderno (**la memoria**). La CPU es la cocinera que lee la receta línea a línea, y el **PC** es su marcapáginas."""),
    ("def", "Instrucción máquina e ISA", r"""
**Instrucción máquina**: operación elemental que el procesador ejecuta directamente (código de operación + operandos:
registros, memoria o inmediato). Hace una tarea sencilla, con un número fijo de operandos, y es **autocontenida**.
**ISA** (juego de instrucciones): la frontera hardware/software. Se define por sus instrucciones, formatos, registros,
modos de direccionamiento y tipos de datos. Ejemplos: x86, MIPS, ARM, Power."""),
    ("def", "CISC frente a RISC", r"""
| | CISC (x86) | RISC (MIPS, ARM) |
|---|---|---|
| Instrucciones | muchas, complejas, de longitud variable | pocas, simples, **todas de una palabra** |
| Operandos | pueden operar sobre memoria | registros; a memoria solo con **load/store** |
| Unidad de control | compleja | sencilla y rápida |

RISC nace de observar que **el 20 % de las instrucciones ocupa el 80 % del tiempo**."""),
    ("def", "Ciclo de ejecución y fetch", r"""Lectura (fetch) → decodificación → ejecución → vuelta a empezar. Fetch: `MAR ← PC` · lectura · `MBR ← Memoria` · `PC ← PC + 4` · `RI ← MBR`."""),
]),

S("mips", "1.2 El MIPS 32: registros y memoria", "Guía Temas 3 y 4 · cap. 2", [
    ("def", "El banco de registros (convenio)", r"""
| Nombre | Nº | Uso |
|---|---|---|
| `$zero` | 0 | siempre 0 |
| `$at` | 1 | reservado al ensamblador (pseudoinstrucciones) |
| `$v0, $v1` | 2–3 | resultados |
| `$a0–$a3` | 4–7 | argumentos |
| `$t0–$t7`, `$t8, $t9` | 8–15, 24–25 | temporales (**no** se conservan) |
| `$s0–$s7` | 16–23 | guardados (**sí** se conservan) |
| `$k0, $k1` | 26–27 | sistema operativo |
| `$gp $sp $fp $ra` | 28–31 | puntero global, de pila, de marco y dirección de retorno |

Truco: t0 = 8, s0 = 16, y los cuatro últimos 28–31. Además: **HI y LO** (mult/div), coprocesador 0 (excepciones) y
coprocesador 1 (FPU, `$f0…$f31`). Direcciones de 32 bits → 4 GB."""),
    ("idea", "Encimera y despensa", r"""Los registros son la **encimera**: 32 huecos, a mano y rapidísimos. La memoria es la **despensa**: enorme, pero hay que ir a por las cosas (`lw`) y devolverlas (`sw`). La ALU solo trabaja con lo que hay en la encimera."""),
    ("def", "Mapa de memoria de un proceso", r"""De abajo arriba: **texto** (código, desde 0x00400000, donde apunta el PC) → **datos** (`.data`, desde 0x10010000; `$gp`) → espacio libre → **pila** (arriba, crece **hacia abajo**; `$sp`)."""),
]),

S("hola", "1.3 Tu primer programa: directivas y syscall", "Guía Temas 3 y 4 · cap. 2", [
    ("mips", "Hola mundo", """.data
msg_hola: .asciiz "hola mundo\\n"
.text
.globl main
main:   li   $v0, 4          # código 4 = imprimir cadena
        la   $a0, msg_hola   # $a0 = dirección de la cadena
        syscall
        li   $v0, 10         # exit
        syscall"""),
    ("def", "Piezas de un programa", r"""**Directiva** (empieza por `.`: orden para el ensamblador, no genera instrucciones) · **etiqueta** (acaba en `:`; es una dirección) · **instrucción** · **comentario** (`#`)."""),
    ("def", "Directivas", r"""`.data` / `.text` · `.globl main` · `.asciiz "…"` (con 0 final) · `.ascii` (sin él) · `.byte` · `.half` (16 bits) · `.word` (32 bits) · `.space n` (n bytes) · `.align n` (alinea a múltiplo de $2^n$) · `.float` / `.double`."""),
    ("def", "Llamadas al sistema", r"""
Se pone el **código en $v0**, los argumentos en `$a0` (y `$a1`) y `syscall`; si devuelve algo, llega en `$v0`.

| $v0 | Servicio | Argumentos / resultado |
|---|---|---|
| 1 | imprimir entero | $a0 |
| 2 / 3 | imprimir float / double | $f12 |
| 4 | imprimir cadena | $a0 = dirección |
| 5 | leer entero | → $v0 |
| 6 / 7 | leer float / double | → $f0 |
| 8 | leer cadena | $a0 = búfer, $a1 = longitud |
| 10 | terminar | — |
| 11 | imprimir carácter | $a0 |
| 12 | leer carácter | → $v0 |"""),
    ("mips", "Leer un número e imprimir su doble", """.text
main:   li   $v0, 5          # leer entero
        syscall
        add  $a0, $v0, $v0   # 2 · número
        li   $v0, 1          # imprimir entero
        syscall
        li   $v0, 10
        syscall""", "21"),
    ("def", "Pseudoinstrucciones", r"""
Se escriben pero no existen en la máquina: el ensamblador las traduce. `li $v0, 4` → `ori $v0, $zero, 4` ·
`move $t1, $t2` → `addu $t1, $zero, $t2` · `li $t1, 0x00800010` → `lui $t1, 0x0080` + `ori $t1, $t1, 0x0010` (un
inmediato de 32 bits no cabe en 16). *Convenio de la asignatura para contar bytes: cada línea = una palabra.*"""),
], "Simulador MIPS"),
])

T2 = Tema("fc2", "Fundamentos de Computadores", 2, "Ensamblador II: registros y memoria",
          "Aritméticas, HI/LO, overflow, lógicas y máscaras, desplazamientos, comparaciones, lw/lb/lbu/sw, endianness y vectores.", [

S("aritmeticas", "2.1 Aritméticas, HI/LO y overflow", "Guía Temas 3 y 4 · cap. 3", [
    ("truco", "Cómo leer una instrucción", r"""El **primer operando es el destino**: `add $t0, $t1, $t2` es $t0 ← $t1 + $t2. Si acaba en **i** (`addi`, `andi`, `slti`) el último es un inmediato; si acaba en **u**, es sin signo (sin aviso de overflow)."""),
    ("mips", "i = −(a·(b − 10) + c)", """.text
main:   li   $t1, 5          # a
        li   $t2, 7          # b
        li   $t3, 8          # c
        addi $t4, $t2, -10   # b - 10 = -3
        mul  $t4, $t4, $t1   # -15
        add  $t4, $t4, $t3   # -7
        sub  $t4, $zero, $t4 # 7   (0 - x = -x)
        move $a0, $t4
        li   $v0, 1
        syscall"""),
    ("mips", "mult y div de verdad: HI y LO", """.text
main:   li   $s0, 17
        li   $s1, 5
        div  $s0, $s1        # LO = cociente, HI = resto
        mflo $t0             # 3
        mfhi $t1             # 2
        move $a0, $t0
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        move $a0, $t1
        li   $v0, 1
        syscall"""),
    ("truco", "LO-cociente", r"""Las dos con «o»: **LO = cociente**, HI = el resto que «sobra arriba». `mult` deja los 64 bits del producto en HI (alta) y LO (baja). `mul`, `div` y `rem` de tres operandos son pseudoinstrucciones."""),
    ("mips", "add avisa del overflow, addu no", """.text
main:   li   $t0, 0x7FFFFFFF  # el mayor positivo en Ca2
        li   $t1, 1
        addu $t2, $t0, $t1    # 0x80000000: da la vuelta en silencio
        move $a0, $t2
        li   $v0, 1
        syscall
        add  $t3, $t0, $t1    # ¡excepción de desbordamiento!"""),
]),

S("logicas", "2.2 Lógicas, máscaras, desplazamientos y comparaciones", "Guía Temas 3 y 4 · cap. 3", [
    ("def", "Bit a bit", r"""`and` (1 si los dos) · `or` (1 si alguno) · `xor` (1 si distintos) · `nor` · `not` (pseudo: `nor $t0, $t1, $zero`). Con inmediato `andi ori xori`: **el inmediato se extiende con ceros**."""),
    ("truco", "Las tres máscaras", r"""**AND** con máscara → pone a 0 donde la máscara tiene 0 (selecciona; como una cartulina con agujeros). **OR** → pone a 1 donde tiene 1. **XOR** → invierte donde tiene 1. `and` con 0x007FFFFF se queda con los 23 bits bajos (¡la mantisa de un float!)."""),
    ("def", "Desplazamientos", r"""`sll` (izquierda, entran ceros: **×2ⁿ**) · `srl` (derecha lógico: ÷2ⁿ sin signo) · `sra` (derecha aritmético: copia el signo, ÷2ⁿ con signo). −16 con `sra 2` → −4 ✓; con `srl 2` → 1 073 741 820 ✗."""),
    ("def", "Comparaciones (set if…)", r"""`slt $t0, $t1, $t2` → 1 si $t1 < $t2 · `slti` · y las pseudo `seq sne sge sgt sle`. Dejan un **1 o un 0** en el destino."""),
    ("mips", "Pruébalo", """.text
main:   li   $t0, 5
        li   $t1, 8
        and  $t2, $t1, $t0      # 0101 & 1000 = 0
        li   $t3, -16
        sra  $t4, $t3, 2        # -4
        srl  $t5, $t3, 2        # 1073741820
        sll  $t6, $t0, 2        # 20
        slt  $t7, $t0, $t1      # 1
        move $a0, $t2
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        move $a0, $t4
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        move $a0, $t5
        li   $v0, 1
        syscall"""),
]),

S("memoria", "2.3 La memoria: lw, lb, lbu, sw, sb y la", "Guía Temas 3 y 4 · cap. 4", [
    ("def", "Carga y almacenamiento", r"""
MIPS es RISC: la ALU no toca la memoria; solo **load** (`lw lh lhu lb lbu`) y **store** (`sw sh sb`). **`la` no accede a
memoria**: carga la dirección. Formas de la dirección: `0x0F000002` · `etiqueta` · `($t1)` · `80($t1)` · `vec+8` ·
`vec($t1)`."""),
    ("ojo", "lb frente a lbu", r"""`lb` **extiende el signo** (copia el bit 7 en los 24 de arriba); `lbu` rellena con ceros. La ñ (164 = 10100100) con `lb` queda en −92 ✗: **para caracteres, `lbu`**."""),
    ("def", "Big endian y little endian", r"""**Big**: en la dirección más baja va el byte **más** significativo (como 2026-10-21). **Little**: el **menos** significativo (21-10-2026). MIPS es bi-endian; el simulador (en un PC) es little endian: `.byte 0x00, 0x11, 0x22, 0x33` leído con `lw` da 0x33221100."""),
    ("mips", "¿Qué endian es esta máquina?", """.data
b1:     .byte 0x00, 0x11, 0x22, 0x33
.text
main:   lw   $t0, b1         # little endian → 0x33221100
        lbu  $t1, b1+3       # 0x33
        move $a0, $t0
        li   $v0, 1
        syscall"""),
    ("def", "Alineación", r"""Un dato de K bytes está alineado si su dirección D cumple **D mod K = 0**: palabras en múltiplos de 4, dobles en múltiplos de 8. El ensamblador lo hace solo (o con `.align 2`); acceder sin alinear da error en MIPS."""),
    ("def", "Vectores y cadenas", r"""**dirección de v[j] = inicio + j · tamaño** (×4 para int: `sll $t4, $t2, 2`). Una cadena es un vector de bytes acabado en 0 (`.asciiz`) y se recorre con `lbu` de 1 en 1."""),
    ("mips", "Longitud de una cadena (strlen)", """.data
cad:    .asciiz "hola"
.text
main:   la   $t0, cad
        li   $t1, 0
bucle:  lbu  $t2, 0($t0)
        beqz $t2, fin
        addi $t1, $t1, 1
        addi $t0, $t0, 1
        b    bucle
fin:    move $a0, $t1
        li   $v0, 1
        syscall"""),
], "Simulador MIPS"),
])

T3 = Tema("fc3", "Fundamentos de Computadores", 3, "Ensamblador III: control de flujo",
          "Saltos condicionales e incondicionales, slt + bne, y plantillas para traducir if, if-else, while, for y switch.", [

S("saltos", "3.1 Saltos", "Guía Temas 3 y 4 · cap. 5", [
    ("def", "Condicionales", r"""
Reales: `beq`, `bne` (comparan dos registros) y `bgez bgtz blez bltz` (con 0). Pseudo: `beqz bnez bgt bge blt ble`.
Nombres: b = branch · eq = igual · ne = distinto · gt mayor · ge mayor o igual · lt menor · le menor o igual · z = con cero.
Todas las condiciones se construyen con **slt + bne + $0**: `slt $1, $16, $17` / `bne $1, $0, Menor` (así traduce el
ensamblador `blt`, usando `$at`)."""),
    ("def", "Incondicionales", r"""`j etiqueta` (absoluto) · `b etiqueta` (relativo al PC) · `jr $t0` (a la dirección del registro) · `jal` (salta y guarda la vuelta en `$ra`)."""),
]),

S("plantillas", "3.2 Traducir C a ensamblador", "Guía Temas 3 y 4 · cap. 5", [
    ("truco", "El truco de oro", r"""En ensamblador se pone **la condición al revés**: en vez de «si se cumple, haz esto» se escribe «si NO se cumple, sáltate esto». Por eso `if (i == j)` suele ser un `bne`."""),
    ("mips", "if-else (con su j Exit)", """.text
main:   li   $s0, 7          # x
        li   $s1, 9          # y
        bge  $s0, $s1, Else  # condición al revés: si x >= y → else
        move $s0, $s1        # x = y
        j    Exit            # ¡sin esto ejecutaría también el else!
Else:   li   $s1, 0          # y = 0
Exit:   move $a0, $s0
        li   $v0, 1
        syscall"""),
    ("mips", "for: sumar un vector", """.data
v:      .word 3, 7, 1, 9, 5
n:      .word 5
.text
main:   la   $t0, v
        lw   $t1, n
        li   $t2, 0          # i
        li   $t3, 0          # suma
bucle:  bge  $t2, $t1, fin   # si i >= n, salir
        sll  $t4, $t2, 2     # i·4
        add  $t4, $t0, $t4   # &v[i]
        lw   $t5, 0($t4)
        add  $t3, $t3, $t5
        addi $t2, $t2, 1
        b    bucle
fin:    move $a0, $t3
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall"""),
    ("mips", "switch con tabla de saltos y jr", """.data
Tabla:  .word L0, L1, L2
.text
main:   li   $s1, 10         # g
        li   $s2, 4          # h
        li   $s3, 1          # i
        li   $s4, 2          # j
        li   $s5, 2          # k  (prueba 0, 1 y 2)
        sll  $t1, $s5, 2     # k·4
        lw   $t0, Tabla($t1) # Tabla[k]
        jr   $t0
L0:     add  $s0, $s3, $s4   # f = i + j
        j    Salir
L1:     add  $s0, $s1, $s2   # f = g + h
        j    Salir
L2:     sub  $s0, $s1, $s2   # f = g - h
Salir:  move $a0, $s0
        li   $v0, 1
        syscall"""),
    ("resumen", "Plantillas", r"""**if** → condición al revés + saltar el bloque · **if-else** → además un `j Exit` · **while/for** → etiqueta arriba, condición de salida, cuerpo, `b` arriba · **switch** → tabla de direcciones + `jr`."""),
], "Simulador MIPS"),
])

T4 = Tema("fc4", "Fundamentos de Computadores", 4, "Formatos de instrucción y modos de direccionamiento",
          "Campos, tipos R, I y J, codificar en binario, diseñar formatos, modos de direccionamiento y relativo al PC.", [

S("formatos", "4.1 Formatos R, I y J", "Guía Temas 3 y 4 · cap. 6", [
    ("def", "Los tres formatos", r"""
| Tipo | Campos | Para |
|---|---|---|
| **R** | op (6) · rs (5) · rt (5) · rd (5) · shamt (5) · funct (6) | aritmético-lógicas entre registros |
| **I** | op (6) · rs (5) · rt (5) · inmediato (16) | inmediatos, lw/sw, saltos condicionales |
| **J** | op (6) · dirección (26) | `j`, `jal` |

5 bits por registro porque $2^5 = 32$. En tipo R, op = 0 y la operación va en **funct** (add = 32, sub = 34, and = 36,
or = 37, slt = 42…)."""),
    ("ej", "Codificar", r"""
- `add $8, $9, $10`: op 0 · rs 9 · rt 10 · rd 8 · shamt 0 · funct 32 → `000000 01001 01010 01000 00000 100000` = **0x012A4020**.
- `addi $21, $22, −50`: op 8 · rs 22 · rt 21 · −50 en Ca2 (16 bits) = 1111111111001110 → **0x22D5FFCE**."""),
    ("ojo", "El orden", r"""En ensamblador se escribe el destino primero (`add rd, rs, rt`), pero **en binario el orden es op, rs, rt, rd**."""),
    ("pasos", "Receta para diseñar un formato", r"""1) La palabra marca el tamaño de la instrucción. 2) CO = $\lceil\log_2(\text{nº instrucciones})\rceil$. 3) Registro = $\lceil\log_2(\text{nº registros})\rceil$. 4) Dirección = ancho de las direcciones. 5) Suma: si sobra, relleno; si no cabe, varias palabras."""),
], "Codificador de instrucciones"),

S("modos", "4.2 Modos de direccionamiento", "Guía Temas 3 y 4 · cap. 7", [
    ("idea", "Encontrar un regalo", r"""**Inmediato**: te lo dan en la mano. **Directo**: «está en el cajón 5». **Indirecto**: «en el cajón 5 hay una nota que dice en qué cajón está». **Relativo**: «3 cajones a la derecha del que te diga tu hermana»."""),
    ("def", "Los modos", r"""
| Modo | Ejemplo | Dónde está el operando |
|---|---|---|
| Implícito | `beqz $a0, etiq` | no escrito (el 0) |
| Inmediato | `li $a0, 0x4f51` | en la instrucción |
| Directo a registro | `move $a0, $a1` | en el registro |
| Directo a memoria | `lw $t0, 0xFFF0` | en esa dirección |
| Indirecto de registro | `lw $a0, ($a1)` | en la dirección que guarda $a1 |
| Indirecto a memoria | `LD R1, [DIR]` (no en MIPS) | en la dirección guardada en DIR |
| Relativo a registro base | `lw $a0, 12($t1)` | en $t1 + 12 (estructuras, pila) |
| Relativo a registro índice | `lw $a0, dir($t1)` | en dir + $t1 (vectores) |
| Relativo al PC | `beqz $a0, etiq` | PC + desplazamiento (reubicable) |
| Relativo a pila | `lw $t0, 8($sp)` | en $sp + 8 |"""),
    ("def", "Relativo al PC", r"""
Al ejecutarse una instrucción **el PC ya apunta a la siguiente**:
$$\text{desplazamiento} = \frac{\text{destino} - (\text{dirección del salto} + 4)}{4}$$
`j` guarda la dirección (en palabras); `b`/`beq` un desplazamiento en Ca2 → el código es **reubicable** (como decir «tres
casas más adelante» en vez de una dirección postal)."""),
]),
])

T5 = Tema("fc5", "Fundamentos de Computadores", 5, "Subrutinas, pila y ciclo de instrucción",
          "jal y jr, el convenio de registros, llamadas anidadas, push/pop, marcos de pila y las 4 fases del MIPS.", [

S("subrutinas", "5.1 jal, jr y el convenio", "Guía Temas 3 y 4 · cap. 8", [
    ("idea", "La nota al pie", r"""`jal` pone el marcapáginas (guarda la vuelta en **$ra**) y salta; `jr $ra` vuelve al marcapáginas."""),
    ("def", "Convenio", r"""Argumentos en **$a0–$a3**; resultados en **$v0–$v1**; `$t` se pueden machacar; los **`$s` hay que dejarlos como estaban** (si los usas, guárdalos); floats: argumento en `$f12`, resultado en `$f0`."""),
    ("mips", "Una subrutina que suma", """.text
.globl main
main:   li   $a0, 7
        li   $a1, 5
        jal  suma
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
suma:   add  $v0, $a0, $a1
        jr   $ra"""),
]),

S("pila", "5.2 La pila y las llamadas anidadas", "Guía Temas 3 y 4 · cap. 8", [
    ("ojo", "El problema", r"""Si A llama a B y B llama a C, el `jal C` **machaca $ra** y B ya no sabe volver a A. Solución: guardar $ra en la **pila** (LIFO, `$sp` apunta a la cima y crece hacia abajo)."""),
    ("def", "push y pop", r"""Push: `addi $sp, $sp, -4` · `sw $ra, 0($sp)`. Pop: `lw $ra, 0($sp)` · `addi $sp, $sp, 4`. **Regla**: si una subrutina hace un `jal`, guarda $ra (y los $s que use) al principio y los recupera antes del `jr $ra`. Las **hoja** (no llaman a nadie) no lo necesitan."""),
    ("mips", "doble_suma llama a suma", """.text
main:   li   $a0, 7
        li   $a1, 5
        jal  doble_suma      # $v0 = 24
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
doble_suma:
        addi $sp, $sp, -4    # push $ra
        sw   $ra, 0($sp)
        jal  suma            # pisa $ra
        add  $v0, $v0, $v0
        lw   $ra, 0($sp)     # pop $ra
        addi $sp, $sp, 4
        jr   $ra
suma:   add  $v0, $a0, $a1
        jr   $ra"""),
    ("def", "Variables locales y paso de estructuras", r"""Las variables **locales** viven en el marco de pila (`addi $sp, $sp, -tamaño`). Un vector local se pasa por su dirección (`move $a0, $sp`). Una estructura por **valor** se copia en la pila; por **referencia** se pasa su dirección; para **devolverla**, quien llama reserva el sitio y pasa su dirección (ejercicios 16 y 34–36)."""),
], "Simulador MIPS"),

S("ciclo", "5.3 Ciclo de instrucción del MIPS", "Guía Temas 3 y 4 · cap. 9", [
    ("def", "Las 4 fases", r"""
1. **Fetch**: IR ← Mem[PC]; PC ← PC + 4.
2. **Decodificación y lectura de registros**: A ← rs, B ← rt; se calcula TARGET por si es un salto.
3. **Ejecución**: tipo R → ALUout = A op B · lw/sw → ALUout = A + IR[15-0] (con signo) · salto → PC ← destino (y
   termina) · beq → si A − B = 0, PC ← TARGET (y termina).
4. **Escritura**: tipo R → rd ← ALUout · sw → Mem[ALUout] ← B · lw → rt ← Mem[ALUout].

Los saltos acaban en la fase 3; aritméticas, lw y sw necesitan la 4."""),
    ("ojo", "Errores que cuestan puntos", r"""Olvidar el ×4 en los vectores · `lb` con caracteres · confundir `la` con `lw` · olvidar el `j Exit` · `jal` sin guardar $ra · contar el desplazamiento de un `beq` desde la propia instrucción · escribir los campos en el orden del ensamblador."""),
]),
])

T6 = Tema("fc6", "Fundamentos de Computadores", 6, "Unidad de control, WepSIM y rendimiento",
          "El procesador elemental WepSIM, operaciones elementales y señales, fetch, interrupciones, CPI, MIPS y Amdahl.", [

S("wepsim", "6.1 El procesador elemental WepSIM", "Hoja «Unidad de control y diseño del procesador»", [
    ("idea", "Una cocina con cintas transportadoras", r"""El **bus interno** es una cinta por la que solo puede viajar **una cosa a la vez**. Las señales **T** (triestados) ponen algo encima de la cinta; las señales **C** (y LC) mandan a un registro que coja lo que pasa. La **unidad de control** es la jefa de cocina que, en cada ciclo de reloj, decide qué señales activar."""),
    ("def", "Registros y señales", r"""
| Elemento | Señales |
|---|---|
| MAR (dirección de memoria) | C0 carga · Ta lo pone en el bus de direcciones |
| MBR (dato de memoria) | C1 carga, M1 elige origen (1 = memoria, 0 = bus) · T1 → bus · Td → bus de datos |
| PC | C2 carga, M2 (1 = PC + 4, 0 = bus) · T2 → bus |
| IR | C3 carga · T3 (SELEC: Size, Offset, SE) → bus |
| RT1, RT2 / RT3 | C4, C5 / C6 cargan · T4, T5 / T7 → bus |
| Banco de registros | RA, RB eligen lectura (T9, T10 → bus) · RC + LC escriben |
| ALU | MA (0 banco, 1 RT1) · MB (00 banco, 01 RT2, 10 = 4, 11 = 1) · Cop · T6 → bus |
| SR (estado C V N Z) | SelP, M7, C7 · T8 → bus |
| Memoria | R / W, BW = 11 (palabra) |"""),
    ("pasos", "Fetch (memoria de 1 ciclo)", r"""
| Ciclo | Operación elemental | Señales |
|---|---|---|
| 1 | MAR ← PC | T2, C0 |
| 2 | MBR ← MP[MAR], PC ← PC + 4 | Ta, R, BW = 11, M1, C1, M2, C2 |
| 3 | IR ← MBR | T1, C3 |
| 4 | Decodificación | salto a la rutina de la instrucción |

Con memoria de 2 ciclos la lectura dura un ciclo más (Ta, R, BW se mantienen y en el segundo se carga MBR)."""),
    ("ej", "add R1, R2, R3 y lw R1, (R2)", r"""
- `add R1, R2, R3`: **R1 ← R2 + R3** → RA = R2, RB = R3, MA = 0, MB = 00, Cop = ADD, T6, RC = R1, LC, SelP, M7, C7 (¡un ciclo!).
- `lw R1, (R2)`: MAR ← R2 (RA = R2, T9, C0) → MBR ← MP[MAR] (Ta, R, BW, M1, C1) → R1 ← MBR (T1, RC = R1, LC)."""),
    ("def", "Interrupciones", r"""Una **interrupción** pide a la CPU que suspenda el programa para atender un periférico (o un error: excepción). En el **ciclo de reconocimiento** la UC guarda **PC y SR** en la pila, deshabilita las interrupciones y carga en el PC la dirección de la rutina de tratamiento (vectorizada o fija). La rutina acaba con un `reti` que lo restaura."""),
]),

S("rendimiento", "6.2 Rendimiento: CPI, MIPS y Amdahl", "Hojas «Unidad de control» y «Fundamentos» (ARCOS)", [
    ("def", "Fórmulas", r"""
$$T_{CPU} = \frac{N_{instr}\cdot CPI}{f}\qquad MIPS = \frac{f}{CPI\cdot10^6}\qquad S = \frac{T_{antes}}{T_{después}}$$
«A es un 50 % más rápido que B» ⇔ $T_B / T_A = 1{,}5$. MIPS no sirve para comparar máquinas con distinto repertorio."""),
    ("def", "Ley de Amdahl", r"""Si una fracción $f$ del tiempo se acelera $s$ veces: $$S = \frac{1}{(1-f) + \dfrac fs}\quad\xrightarrow{s\to\infty}\quad\frac1{1-f}$$ Lo que no mejoras acaba mandando: con un 10 % secuencial, el speedup nunca pasa de 10."""),
    ("def", "Potencia, fiabilidad y disponibilidad", r"""
- Potencia dinámica $P \propto C\,V^2 f$: bajar el voltaje compensa mucho más que bajar la frecuencia.
- **Fiabilidad** R(t): probabilidad de funcionar sin fallar de 0 a t (MTTF).
- **Disponibilidad**: fracción del tiempo en servicio $= \dfrac{MTTF}{MTTF + MTTR}$."""),
], "Rendimiento"),
])

T7 = Tema("fc7", "Fundamentos de Computadores", 7, "Jerarquía de memoria y memoria caché",
          "Tipos de memoria, contar accesos, la jerarquía, proximidad, acierto/fallo, tiempo medio y organización de la caché.", [

S("jerarquia", "7.1 Tipos de memoria y jerarquía", "Guía Temas 3 y 4 · cap. 13–14", [
    ("def", "Características", r"""Permanencia (volátil o no) · operaciones (RAM lectura/escritura, ROM solo lectura) · modo de acceso (secuencial como una cinta, **aleatorio** como una playlist) · tiempo de acceso · ancho de banda · capacidad y coste. Registros ~1 ns · RAM 40–100 ns · disco ms. ⚠️ b = bit, B = byte; en discos y redes, potencias de 10."""),
    ("pasos", "Contar accesos a memoria", r"""**1 por instrucción ejecutada (fetch) + 1 por cada lw/sw ejecutado.** Cuenta: antes del bucle + instrucciones del bucle × vueltas + la comparación que sale + lo de después. Ejemplo: suma de 0 a 999 → 3 + 4·1000 + 1 + 1 = **4005**."""),
    ("idea", "Los libros", r"""Mesa (registros), biblioteca de la facultad (caché), biblioteca de Florida (DRAM). Cuando vas a la biblioteca no traes una hoja: **traes el libro entero** (el bloque) por si lo vuelves a usar."""),
    ("def", "Memoria principal", r"""**SRAM** (biestables, sin refresco, rápida y cara → cachés) frente a **DRAM** (condensador, necesita **refresco**, barata → memoria principal; FPM, EDO, SDRAM, DDR). ROM, PROM, EPROM, EEPROM, Flash (no volátiles)."""),
]),

S("cache", "7.2 La caché: acierto, fallo y tiempo medio", "Guía Temas 3 y 4 · cap. 15", [
    ("def", "Proximidad (localidad)", r"""**Temporal**: lo que usas ahora lo volverás a usar pronto (bucles). **Espacial**: usarás lo que está cerca (vectores, código seguido). Por eso la caché funciona."""),
    ("def", "Tiempo medio de acceso", r"""$$T_m = h\cdot T_a + (1-h)(T_a + T_f) = T_a + (1-h)\,T_f\qquad\Rightarrow\qquad 1-h = \frac{T_m - T_a}{T_f}$$ h en **tanto por uno**. Con escritura inmediata, las escrituras cuestan lo de la memoria principal (separa lecturas y escrituras). Varios niveles: L1 recibe todo, L2 los fallos de L1…"""),
]),

S("organizacion", "7.3 Organización: directa, asociativa y por conjuntos", "Guía Temas 3 y 4 · cap. 16", [
    ("def", "Campos de la dirección", r"""
| Correspondencia | Campos | Dónde va el bloque B |
|---|---|---|
| **Directa** | etiqueta · línea · byte | línea B mod nº líneas |
| **Totalmente asociativa** | etiqueta · byte | cualquiera |
| **Por conjuntos (k vías)** | etiqueta · conjunto · byte | conjunto B mod nº conjuntos |

Byte = $\log_2$(línea) · líneas = caché / línea · conjuntos = líneas / vías · etiqueta = lo que sobra."""),
    ("def", "Sustitución y escritura", r"""**Sustitución**: FIFO, **LRU** (el usado hace más tiempo), LFU, aleatoria. **Escritura inmediata** (write-through: siempre a memoria, coherente pero lenta) o **diferida / post-escritura** (write-back: solo al expulsar un bloque modificado, con bit de sucio). Asignación en escritura (write-allocate) o no."""),
    ("ojo", "Fallos típicos", r"""KB son potencias de 2 (64 KB = $2^{16}$, no 64 000) · usar líneas en vez de conjuntos en el campo central · poner h en % dentro de la fórmula · olvidar el acceso extra de cada lw/sw o la última comparación del bucle."""),
    ("idea", "Thrashing", r"""Dos vectores a la misma distancia que el tamaño de la caché caen en la **misma línea** de una caché directa: se echan el uno al otro en cada acceso (100 % de fallos). Más vías (asociatividad) lo arregla: mira los ejercicios 11–13 de caché."""),
], "Caché"),
])

T8 = Tema("fc8", "Fundamentos de Computadores", 8, "Memoria virtual",
          "Páginas y marcos, formato de la dirección, tabla de páginas, traducción, fallos de página y TLB.", [

S("idea", "8.1 Qué es la memoria virtual", "Hoja «Memoria virtual»", [
    ("idea", "Libros, estantería y almacén", r"""Cada programa cree tener **toda la memoria para él** (espacio virtual de $2^{n}$ bytes). En realidad solo tiene en la **estantería** (memoria física) las **páginas** que usa; el resto está en el **almacén** (el disco, zona de *swap*). La tabla de páginas es el **catálogo** que dice en qué hueco (**marco**) está cada libro."""),
    ("def", "Formato de la dirección", r"""
Con páginas de $2^d$ bytes: **dirección virtual = nº de página | desplazamiento (d bits)**.
- Nº de páginas = $2^{n-d}$ · nº de marcos = memoria física / tamaño de página.
- **Dirección física = marco | desplazamiento** (el desplazamiento se copia tal cual).
- Lo que se transfiere en un fallo de página es **una página entera**."""),
    ("def", "Entrada de la tabla de páginas", r"""Bit de **presencia/válido** · **nº de marco** (o bloque de swap) · bit de **modificado** · bit de **referencia** · bits de **protección**. Tamaño de la tabla de un nivel = nº de páginas × tamaño de entrada (con 32 bits y páginas de 4 KB: $2^{20}\cdot4$ B = 4 MB por proceso → tablas multinivel)."""),
    ("pasos", "Traducir una dirección", r"""1) Separa página y desplazamiento (con páginas de $16^k$ bytes basta con cortar dígitos hexadecimales). 2) Mira la tabla: si presencia = 0 → **fallo de página** (el SO trae la página del disco). 3) Dirección física = marco × tamaño + desplazamiento."""),
    ("def", "TLB", r"""Una **caché de traducciones** (pocas entradas, muy rápida). Acierto en TLB: TLB + acceso al dato. Fallo: TLB + tabla en memoria + (si hay fallo de página) disco + dato."""),
], "Memoria virtual"),
])

T9 = Tema("fc9", "Fundamentos de Computadores", 9, "Entrada/salida",
          "Módulos de E/S, mapas común y separado, E/S programada, interrupciones, DMA y discos.", [

S("es", "9.1 Módulos y técnicas de E/S", "Hoja «Sistemas de E/S»", [
    ("def", "Módulo (controlador) de E/S", r"""Cada periférico se maneja a través de **registros**: de **datos**, de **control** (órdenes) y de **estado** (¿listo? ¿error?)."""),
    ("def", "Mapa común frente a separado", r"""**Común** (memory-mapped): los registros tienen direcciones de memoria y se usan con `lw`/`sw` (`lw $t0, 0x100`). **Separado**: espacio de puertos aparte con instrucciones especiales **`in`/`out`** (`in $t0, 1008`)."""),
    ("def", "Técnicas", r"""
| Técnica | Cómo | Pega |
|---|---|---|
| **E/S programada** | la CPU pregunta el estado en un bucle (**espera activa**) | desperdicia la CPU |
| **Por interrupciones** | el periférico avisa cuando está listo; la CPU hace otras cosas | una interrupción por dato |
| **DMA** | un controlador mueve bloques a memoria sin la CPU y avisa al final | coherencia con la caché |"""),
    ("mips", "E/S programada con un dispositivo simulado (tensiómetro)", """.text
main:   li   $t0, 1
        sw   $t0, 1000($zero)     # empezar la medida
esp:    lw   $t0, 1004($zero)     # ¿terminó?
        beqz $t0, esp             # espera activa
        lw   $a0, 1008($zero)     # sistólica
        li   $v0, 1
        syscall""", "", "tensiometro"),
    ("def", "Sobrecarga", r"""% de tiempo = (consultas por segundo × ciclos por consulta) / frecuencia. Ej.: ratón 30 veces/s × 2000 ciclos a 2,7 GHz = 0,0022 %."""),
]),

S("discos", "9.2 Discos", "Hoja «Sistemas de E/S»", [
    ("def", "Tiempo de acceso a un sector", r"""
$$T = T_{búsqueda} + T_{latencia} + T_{transferencia}$$
- Latencia rotacional media = **media vuelta** = $\dfrac{1}{2}\cdot\dfrac{60}{rpm}$ s.
- Transferencia de un sector = $\dfrac{T_{vuelta}}{\text{sectores por pista}}$.
- Capacidad = platos × superficies × pistas × sectores × bytes.
- **Secuencial** (pistas seguidas): una búsqueda y luego latencia + vuelta por pista. **Aleatorio**: cada sector paga todo."""),
], "Discos"),
])

T10 = Tema("fc10", "Fundamentos de Computadores", 10, "Segmentación y paralelismo a nivel de instrucción",
           "Pipeline de 5 etapas, riesgos estructurales, de datos y de control, forwarding, saltos, planificación y desenrollado.", [

S("pipeline", "10.1 El pipeline de 5 etapas", "Hoja «Paralelismo a nivel de instrucción» (ARCOS)", [
    ("idea", "La lavandería", r"""Lavar, secar, planchar y doblar: mientras una colada se seca, la siguiente ya se lava. Cada prenda tarda lo mismo, pero **sale una colada por etapa**. En el procesador: **IF** (captar) · **ID** (decodificar y leer registros) · **EX** (ALU) · **M** (memoria) · **WB** (escribir el registro)."""),
    ("def", "Riesgos", r"""
- **Estructurales**: dos instrucciones quieren el mismo recurso (una sola memoria para IF y M).
- **De datos**: **RAW** (leer después de escribir: el único real en un pipeline en orden), **WAR** y **WAW** (falsas, por
  reutilizar registros; importan con ejecución fuera de orden → renombrado).
- **De control**: los saltos (no se sabe qué captar hasta resolverlos)."""),
    ("def", "Soluciones", r"""
- **Detenciones** (burbujas). Sin forwarding, el consumidor lee en ID en el mismo ciclo del WB del productor (banco que
  escribe en la 1.ª mitad y lee en la 2.ª).
- **Forwarding** (anticipación): el resultado pasa de EX/M al siguiente sin esperar a WB; solo queda la detención
  **load → uso**.
- Saltos: vaciar/congelar el pipeline, predecir no tomado, predecir tomado, **salto retardado** (hueco que se ejecuta siempre)."""),
    ("def", "Modelo de latencias (Hennessy-Patterson)", r"""Una instrucción por ciclo; si una usa el resultado de otra, espera la **latencia** de la tabla. **Planificar** = reordenar instrucciones independientes para rellenar huecos. **Desenrollar** = varias iteraciones por vuelta (con registros distintos): menos control del bucle y más instrucciones para intercalar."""),
], "Segmentación"),
])

T11 = Tema("fc11", "Fundamentos de Computadores", 11, "Multiprocesadores: coherencia y consistencia",
           "Protocolo MSI con snooping, tráfico de bus, cerrojos con test-and-set y LL/SC, modelos de consistencia.", [

S("coherencia", "11.1 Coherencia de caché: MSI", "Hoja «Multiprocesadores» (ARCOS)", [
    ("idea", "El documento compartido", r"""Cada procesador tiene su copia (caché). **S** = todos tenéis una fotocopia; para escribir hay que **romper las fotocopias de los demás** (invalidar) y quedarte el original (**M**). **I** = no tienes copia válida."""),
    ("def", "Transiciones", r"""
| Evento | Transición | Bus |
|---|---|---|
| Lectura con fallo | I → S | BusRd (si otra la tiene en M, *flush* y pasa a S) |
| Escritura con fallo | I → M | BusRdX (las demás → I) |
| Escritura sobre S | S → M | BusUpgr / invalidación |
| Otra lee mi bloque M | M → S | flush |
| Otra escribe | M o S → I | (flush si estaba en M) |

**Invariante**: si una caché lo tiene en M, todas las demás están en I."""),
]),

S("sincro", "11.2 Sincronización y consistencia", "Hoja «Multiprocesadores» (ARCOS)", [
    ("def", "Cerrojos", r"""**test-and-set** lee y escribe 1 atómicamente (siempre escribe → invalidaciones). Mejor **test-and-test-and-set** (girar leyendo la copia local) o **LL/SC** (load-linked / store-conditional: solo escribe si nadie tocó la dirección)."""),
    ("def", "Consistencia secuencial", r"""El resultado es el de **alguna intercalación** de las instrucciones de todos los hilos **respetando el orden de cada programa**. Los modelos **relajados** (TSO en x86, PSO, débiles en ARM/POWER) permiten reordenar (p. ej. una lectura adelanta a una escritura gracias al *store buffer*): salen resultados imposibles con SC salvo que se usen **barreras** (`mfence`)."""),
], "Consistencia"),
])

T12 = Tema("fc12", "Fundamentos de Computadores", 12, "Chuletas y erratas (Temas 3 y 4)",
           "Las instrucciones marcadas, las fórmulas de memoria en una página y lo que estaba mal en las diapositivas.", [

S("chuleta3", "12.1 Chuleta de instrucciones MIPS", "Guía Temas 3 y 4 · cap. 11", [
    ("resumen", "Las imprescindibles", r"""
| Grupo | Instrucciones |
|---|---|
| Carga | `lw lb lbu lh lhu` · `la` (dirección) · `lui` · `li` |
| Almacenamiento | `sw sb sh` |
| Aritméticas | `add addi addu addiu sub subu` · `mult multu div divu` + `mfhi mflo` · pseudo `mul div rem` |
| Lógicas | `and andi or ori xor xori nor` · pseudo `not` |
| Desplazamientos | `sll srl sra sllv srlv srav` |
| Comparación | `slt slti sltu` · pseudo `seq sne sge sgt sle` |
| Saltos | `beq bne bgez bgtz blez bltz` · pseudo `beqz bnez bgt bge blt ble b` · `j jal jr jalr` |
| Coma flotante | `l.s s.s add.s sub.s mul.s div.s mov.s mtc1 mfc1 cvt.s.w cvt.w.s c.lt.s bc1t` |
| Sistema | `syscall` |"""),
]),

S("chuleta4", "12.2 Chuleta de memoria", "Guía Temas 3 y 4 · cap. 18", [
    ("resumen", "Todas las fórmulas", r"""
| Qué | Cómo |
|---|---|
| Accesos de un programa | 1 por instrucción ejecutada + 1 por cada lw/sw |
| Tasa de aciertos | aciertos / accesos |
| Tiempo medio | $T_a + (1-h)T_f$ · despejar: $1-h = (T_m - T_a)/T_f$ |
| Bloques de MP | tamaño MP / tamaño bloque |
| Líneas · conjuntos | caché / línea · líneas / vías |
| Bits de byte · línea · conjunto | $\log_2$(línea) · $\log_2$(líneas) · $\log_2$(conjuntos) |
| Etiqueta | bits de dirección − el resto |
| Línea / conjunto de B | B mod nº líneas / B mod nº conjuntos |
| Potencias | $2^{10}$ = 1 K · $2^{16}$ = 64 K · $2^{20}$ = 1 M · $2^{30}$ = 1 G · $2^{32}$ = 4 G |"""),
]),

S("erratas", "12.3 Erratas corregidas de los Temas 3 y 4", "Guía Temas 3 y 4 · cap. 12 y 18.2", [
    ("errata", "Tema 3", r"""
| Dónde | Pone | Correcto |
|---|---|---|
| T3 (I) · Lógicas | `ori $0 $t1 80` | `ori $t0, $t1, 80` (no se escribe en $0) |
| T3 (I) · Comparación | `sneq` | `sne` |
| T3 (II) · Arquitectura | «direcciones de 2 bits» | 32 bits (4 GB) |
| T3 (II) · Hola mundo | `msg_holra` | `msg_hola` |
| T3 (II) · Direccionamiento | `lbu $a0 0x0FFEE0000` | `lbu $a0, 0xFFEE0000` |
| T3 (II) · Alineamiento | `w1. .word 10` | `w1: .word 10` |
| T3 (II) · Ejercicio V[5] | `lw $t1, 20` | `li $t1, 20` |
| T3 (II) · Endianness | número de 33 bits | 0x1B000000 (32 bits) |
| T3 (III) · Vectores | `la $t0 16` | `li $t0, 16` |
| Libro · Tabla 12.10 | BEQ «bifurcar sin igual» · MULTU «multiplicar signo» | si igual · sin signo |
| Libro · Salto | `if (1 == j)` | `if (i == j)` |
| Libro · While | `mult $9,$19,$10 # 1*4` · `add $19,419,$20` | `mul $9, $19, $10` · `add $19, $19, $20` |
| Libro · Switch | `mult $9, $19, $21` | `mul $9, $21, $10` y definir `Tabla: .word L0, L1, L2` |
| Libro · Vectores | `lw $8, Inicio($16)` con $16 = i | solo si $16 = i·4 (si no, `sll` antes) |
| Libro · Subrutinas | pila hacia arriba | `addi $sp,$sp,-4` antes y `+4` después |
| Libro · jal | «$31 se llama contador de programa» | $31 es $ra; el PC es otro |"""),
    ("errata", "Tema 4", r"""
| Dónde | Pone | Correcto |
|---|---|---|
| T4 (I) · diap. 14 y 17 | bucle con `bgt` | `bge` (con bgt daría 1001 vueltas) |
| T4 (I) · diap. 26 | «25.6 billones» | 25,6 mil millones (billion inglés) |
| T4 (II) · diap. 4 | `mult $t2 $t0 4` | `mul $t2, $t0, 4` |
| T4 (II) · diap. 18 | 480480 ns = 480.480 ms | 480 480 ns ≈ 0,48 ms |
| T4 (II) · diap. 43 | `addi $t3, $t3, $t4` | `add` |
| T4 (II) · diap. 54 | «= 16 ns ⇒ h > 0.9916» | h ≈ 0,9917 para 5 ns; h > 0,95 para 10 ns |
| T4 (II) · diap. 62 | $2^{26}$ B = 64 megabloques | $2^{26}$ bloques |
| T4 (II) · diap. 63-64 | dirección 0x00000064 | 64 decimal = 0x40 |
| T4 (II) · diap. 99/104 | 64 KB con líneas de 8 B: «$2^{14}$ líneas» | $2^{13}$ líneas; campos 16 · 13 · 3 |
| T4 (II) · diap. 117 | 64 KB, 4 vías: «$2^{12}$ conjuntos» | $2^{11}$; campos 18 · 11 · 3 |
| T4 (II) · diap. 132 | `beq $t1, $t0, bucle` | `bne` |"""),
]),
])

TEMAS = [T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12]
