from contenido.base import Ejercicio, Hoja, Respuesta, Prueba, Programa

R = Respuesta


def asm(codigo: str) -> str:
    return "\n```mipsasm\n" + codigo.strip("\n") + "\n```\n"


# --------------------------------------------------------------------------- soluciones (todas probadas en el simulador)
S1 = """\
.text
main:   li   $t0, 6           # a
        li   $t1, 7           # b
        li   $t2, 3           # c (no se usa en la expresión)
        add  $t3, $t0, $t1    # $t3 = a + b = 13
        mul  $t5, $t3, $t3    # d = (a+b)·(a+b) = 169   → en $t5
"""

S2 = """\
.text
main:   li   $v0, 0           # suma = 0
        li   $t0, 1           # i = 1
        li   $t1, 100         # límite
bucle:  bgt  $t0, $t1, fin    # mientras i <= 100
        add  $v0, $v0, $t0    #   suma += i
        addi $t0, $t0, 1      #   i++
        b    bucle
fin:                          # $v0 = 5050  (no llamamos a exit: machacaría $v0 con el 10)
"""

S3 = """\
.data
a:      .word 10
b:      .word 5
.text
main:   li    $t0 2
        lw    $t1, a
        lw    $t2, b
label1: bgt   $t0, $t1, label2
        addi  $t2, $t2, 2
        addi  $t0, $t0, 1
        b     label1
label2: sw    $t0, a
        sw    $t2, b
"""

S4 = S3.rstrip() + """
        # --- apartado 4: imprimir los resultados
        move $a0, $t0
        li   $v0, 1          # print_int(a)
        syscall
        li   $a0, ' '
        li   $v0, 11         # print_char(' ')
        syscall
        move $a0, $t2
        li   $v0, 1          # print_int(b)
        syscall
        li   $v0, 10         # exit
        syscall
"""

S5 = """\
.data
pideA:  .asciiz "A = "
pideB:  .asciiz "B = "
si:     .asciiz "Si, uno es multiplo del otro\\n"
no:     .asciiz "No, ninguno es multiplo del otro\\n"
.text
main:   la   $a0, pideA
        li   $v0, 4
        syscall
        li   $v0, 5          # read_int → A
        syscall
        move $t0, $v0
        la   $a0, pideB
        li   $v0, 4
        syscall
        li   $v0, 5          # read_int → B
        syscall
        move $t1, $v0

        beqz $t1, probar2    # si B = 0 no se puede dividir entre B
        rem  $t2, $t0, $t1   # A mod B
        beqz $t2, essi       # A es múltiplo de B
probar2: beqz $t0, essi      # 0 es múltiplo de cualquier número
        rem  $t2, $t1, $t0   # B mod A
        beqz $t2, essi       # B es múltiplo de A
        la   $a0, no
        b    imprimir
essi:   la   $a0, si
imprimir: li $v0, 4
        syscall
        li   $v0, 10
        syscall
"""

S6 = """\
.text
main:   li   $v0, 5          # N = read_int()
        syscall
        move $s0, $v0
        li   $t0, 1          # fila = 1
filas:  bgt  $t0, $s0, fin
        li   $t1, 1          # col = 1
cols:   bgt  $t1, $t0, finfila
        move $a0, $t1        # print_int(col)
        li   $v0, 1
        syscall
        li   $a0, ' '        # separador
        li   $v0, 11
        syscall
        addi $t1, $t1, 1
        b    cols
finfila: li  $a0, '\\n'      # salto de línea
        li   $v0, 11
        syscall
        addi $t0, $t0, 1
        b    filas
fin:    li   $v0, 10
        syscall
"""

S7 = """\
.data
a:      .word 0
b:      .word 5
c:      .word 7
.text
main:   lw   $t1, b          # $t1 = b
        lw   $t2, c          # $t2 = c
        add  $t0, $t1, $t2   # b + c
        addi $t0, $t0, 100   # + 100
        sw   $t0, a          # a = b + c + 100
"""

S8 = """\
.text
main:   li   $v0, 5
        syscall
        move $t0, $v0        # primer número
        li   $v0, 5
        syscall
        move $t1, $v0        # segundo número
        move $a0, $t0        # de momento el mayor es el primero
        bge  $t0, $t1, imprime
        move $a0, $t1        # si no, el segundo
imprime: li  $v0, 1
        syscall
        li   $v0, 10
        syscall
"""

S9 = """\
.data
par:    .asciiz "par\\n"
impar:  .asciiz "impar\\n"
.text
main:   li   $v0, 5
        syscall
        andi $t0, $v0, 1     # el bit de menos peso: 0 → par, 1 → impar (vale también para negativos en Ca2)
        la   $a0, par
        beqz $t0, imprime
        la   $a0, impar
imprime: li  $v0, 4
        syscall
        li   $v0, 10
        syscall
"""

S10 = """\
.text
main:   li   $v0, 5          # N (par)
        syscall
        move $t1, $v0
        li   $t2, 0          # suma
        li   $t0, 2          # i = 2
bucle:  bgt  $t0, $t1, fin
        add  $t2, $t2, $t0
        addi $t0, $t0, 2     # i += 2
        b    bucle
fin:    move $a0, $t2
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""

S11 = """\
# sustituir(cadena, viejo, nuevo): $a0 = dirección de la cadena, $a1 = carácter a buscar, $a2 = carácter nuevo
# Es una función hoja (no llama a nadie) y solo usa registros $t: no necesita pila.
.text
sustituir:
bucle:  lb   $t0, 0($a0)          # carácter actual
        beqz $t0, fin             # '\\0' → fin de la cadena
        bne  $t0, $a1, siguiente
        sb   $a2, 0($a0)          # coincide: lo cambiamos
siguiente: addi $a0, $a0, 1       # siguiente byte
        b    bucle
fin:    jr   $ra
"""

M11 = """\
.data
_cad:   .asciiz "hola mundo, otro dia"
.text
main:   la   $a0, _cad
        li   $a1, 'o'
        li   $a2, '0'
        jal  sustituir
        la   $a0, _cad
        li   $v0, 4
        syscall
        li   $v0, 10
        syscall
"""

M11b = M11.replace("'o'", "'z'").replace("'0'", "'Z'")

S12 = """\
.data
a:      .word 5
b:      .word 7
c:      .word 9
.text
main:   lw   $a0, a          # 1.er argumento
        lw   $a1, b          # 2.º argumento
        lw   $a2, c          # 3.er argumento
        jal  func            # $ra ← dirección de vuelta; salta a func
        move $a0, $v0        # el resultado llega en $v0
        li   $v0, 1          # print_int
        syscall
        li   $v0, 10
        syscall
"""

FUNC12 = """\
func:   add  $v0, $a0, $a1   # func de ejemplo de la app: a + b + c
        add  $v0, $v0, $a2
        jr   $ra
"""

S13 = """\
.data
a:      .word 10
b:      .word 5
.align 2
v:      .space 800           # 800 bytes / 4 = 200 enteros
.text
main:   la   $t0, v          # dirección de v[0]
        # b)  v[20] = v[30]
        lw   $t1, 120($t0)   # v[30] está en v + 30·4
        sw   $t1, 80($t0)    # v[20] está en v + 20·4
        # c)  v[10] = b
        lw   $t1, b
        sw   $t1, 40($t0)    # v[10] está en v + 10·4
"""

S14 = """\
.text
# int maximo(int A, int B): función hoja → no necesita pila
maximo: move $v0, $a0            # supongo que el mayor es A
        bgt  $a0, $a1, finmax
        move $v0, $a1            # si no, B
finmax: jr   $ra

# void maximoV(int v1[], int v2[], int v3[], int N): NO es hoja (llama a maximo)
# → guarda $ra y los valores que necesita después de cada llamada en registros $s (que también guarda)
maximoV:
        addi $sp, $sp, -24
        sw   $ra, 20($sp)
        sw   $s0, 16($sp)
        sw   $s1, 12($sp)
        sw   $s2, 8($sp)
        sw   $s3, 4($sp)
        sw   $s4, 0($sp)
        move $s0, $a0            # v1
        move $s1, $a1            # v2
        move $s2, $a2            # v3
        move $s3, $a3            # N
        li   $s4, 0              # i = 0
for:    bge  $s4, $s3, finfor    # i < N
        sll  $t0, $s4, 2         # i·4 (desplazamiento en bytes)
        add  $t1, $s0, $t0
        lw   $a0, 0($t1)         # v1[i]
        add  $t1, $s1, $t0
        lw   $a1, 0($t1)         # v2[i]
        jal  maximo              # $v0 = maximo(v1[i], v2[i])
        sll  $t0, $s4, 2         # ¡$t0 pudo cambiar en la llamada! se recalcula
        add  $t1, $s2, $t0
        sw   $v0, 0($t1)         # v3[i] = …
        addi $s4, $s4, 1         # i++
        b    for
finfor: lw   $ra, 20($sp)
        lw   $s0, 16($sp)
        lw   $s1, 12($sp)
        lw   $s2, 8($sp)
        lw   $s3, 4($sp)
        lw   $s4, 0($sp)
        addi $sp, $sp, 24
        jr   $ra
"""

M14 = """\
.data
_v1:    .word 1, 9, 3, -4, 7
_v2:    .word 5, 2, 3, -1, 0
_v3:    .space 20
.text
main:   li   $s0, 111             # valores «testigo» en $s0 y $s1
        li   $s1, 222
        la   $a0, _v1
        la   $a1, _v2
        la   $a2, _v3
        li   $a3, 5
        jal  maximoV
        li   $t0, 0
        la   $t1, _v3
_imp:   lw   $a0, 0($t1)
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        addi $t1, $t1, 4
        addi $t0, $t0, 1
        blt  $t0, 5, _imp
        move $a0, $s0             # ¿se respetaron los $s?
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        move $a0, $s1
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""

M14b = """\
.text
main:   li   $a0, -3
        li   $a1, 8
        jal  maximo
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        li   $a0, 12
        li   $a1, 12
        jal  maximo
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""

S15 = """\
.data
.align 2
vector: .space 4096              # int vector[1024]  (global → en .data)
.text
main:                            # funcion1
        li   $t0, 0              # i
        la   $t1, vector
        li   $t2, 1024
llenar: bge  $t0, $t2, finll
        sw   $t0, 0($t1)         # vector[i] = i
        addi $t1, $t1, 4
        addi $t0, $t0, 1
        b    llenar
finll:  li   $a0, 1024           # z = suma(1024)
        jal  suma
        move $a0, $v0            # print_int(z)
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall

# int suma(int n): accede directamente al vector global
suma:   li   $v0, 0              # s = 0
        li   $t0, 0              # i = 0
        la   $t1, vector
bsuma:  bge  $t0, $a0, fsuma
        lw   $t2, 0($t1)
        add  $v0, $v0, $t2       # s += vector[i]
        addi $t1, $t1, 4
        addi $t0, $t0, 1
        b    bsuma
fsuma:  jr   $ra
"""

S16 = """\
.text
main:   jal  funcion1
        li   $v0, 10
        syscall

# void funcion1(): el vector es LOCAL → vive en la pila (4096 bytes) y se pasa su dirección a suma
funcion1:
        addi $sp, $sp, -4100     # 4096 del vector + 4 para guardar $ra
        sw   $ra, 4096($sp)
        li   $t0, 0              # i
        move $t1, $sp            # &vector[0] = $sp
llenar: bge  $t0, 1024, finll
        sw   $t0, 0($t1)         # vector[i] = i
        addi $t1, $t1, 4
        addi $t0, $t0, 1
        b    llenar
finll:  move $a0, $sp            # 1.er arg: dirección del vector
        li   $a1, 1024           # 2.º arg: n
        jal  suma
        move $a0, $v0            # print_int(z)
        li   $v0, 1
        syscall
        lw   $ra, 4096($sp)
        addi $sp, $sp, 4100      # liberar el marco
        jr   $ra

# int suma(int vector[], int n): $a0 = dirección, $a1 = n
suma:   li   $v0, 0
        li   $t0, 0
bsuma:  bge  $t0, $a1, fsuma
        lw   $t2, 0($a0)
        add  $v0, $v0, $t2
        addi $a0, $a0, 4
        addi $t0, $t0, 1
        b    bsuma
fsuma:  jr   $ra
"""

S20 = """\
.data
.align 2
vector: .space 1024              # 1024 / 4 = 256 enteros
.text
main:   # b)  vector[8] = 30
        li   $t0, 30
        la   $t1, vector
        sw   $t0, 32($t1)        # 8·4 = 32
        # c)  leer un número y ponerlo en todas las componentes
        li   $v0, 5
        syscall
        la   $t1, vector
        li   $t0, 0              # i
bucle:  bge  $t0, 256, fin
        sw   $v0, 0($t1)
        addi $t1, $t1, 4
        addi $t0, $t0, 1
        b    bucle
fin:    li   $v0, 10
        syscall
"""

S21 = """\
.text
.globl main
main:   li   $a0, 5
        jal  funcion
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
funcion: move $t0, $a0
        li   $t1, 0
bucle:  beq  $t0, 0, fin
        add  $t1, $t1, $t0
        sub  $t0, $t0, 1
        b    bucle
fin:    move $v0, $t1
        jr   $ra
"""

S22 = """\
# int Vocales(char *cadena): $a0 = dirección de la cadena → $v0 = número de 'a'
#   (cadena nula, es decir, puntero 0, o cadena vacía → -1)
.text
Vocales: li  $v0, -1
        beqz $a0, vfin           # puntero nulo
        lb   $t0, 0($a0)
        beqz $t0, vfin           # cadena vacía ""
        li   $v0, 0              # contador
vbucle: lb   $t0, 0($a0)
        beqz $t0, vfin           # '\\0' → fin
        bne  $t0, 'a', vsig
        addi $v0, $v0, 1         # ¡una 'a'!
vsig:   addi $a0, $a0, 1
        b    vbucle
vfin:   jr   $ra
"""

M22_MAIN = """\
.data
cadena: .asciiz "Hola"
.text
.globl main
main:   la   $a0, cadena         # argumento en $a0
        jal  Vocales
        move $a0, $v0            # resultado en $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""


def _main_cad(texto, nulo=False):
    carga = "li   $a0, 0" if nulo else "la   $a0, _c"
    return f""".data
_c:     .asciiz "{texto}"
.text
main:   {carga}
        jal  Vocales
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""


S23 = """\
.text
.globl main
main:   li   $a0, 5
        jal  funcion
        move $a0, $v0
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
funcion: li  $t0, 10
        bgt  $a0, $t0, et1
        li   $t0, 10
        add  $v0, $t0, $a0
        b    et2
et1:    li   $t0, 8
        add  $v0, $t0, $a0
et2:    jr   $ra
"""

S24 = """\
.data
v:      .word 7, 8, 3, 4, 5, 6
.text
.globl main
main:   la   $a0, v              # 1.º: dirección del vector
        li   $a1, 6              # 2.º: número de componentes
        li   $a2, 5              # 3.º: valor a sumar
        jal  SumarValor
        # imprimir las componentes
        la   $t0, v
        li   $t1, 0
imp:    bge  $t1, 6, fin
        lw   $a0, 0($t0)
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        addi $t0, $t0, 4
        addi $t1, $t1, 1
        b    imp
fin:    li   $v0, 10
        syscall

# void SumarValor(int v[], int n, int valor)   — función hoja
SumarValor:
        li   $t0, 0              # i
sv:     bge  $t0, $a1, svfin
        lw   $t1, 0($a0)
        add  $t1, $t1, $a2       # v[i] += valor
        sw   $t1, 0($a0)
        addi $a0, $a0, 4
        addi $t0, $t0, 1
        b    sv
svfin:  jr   $ra
"""

M24 = """\
.data
_w:     .word -1, 0, 100
.text
main:   la   $a0, _w
        li   $a1, 3
        li   $a2, -10
        jal  SumarValor
        la   $t0, _w
        lw   $a0, 0($t0)
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        lw   $a0, 4($t0)
        li   $v0, 1
        syscall
        li   $a0, ' '
        li   $v0, 11
        syscall
        lw   $a0, 8($t0)
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""

S30 = """\
# float funcion(float A[], int N, float x):  $a0 = A, $a1 = N, x en $f12  →  resultado en $f0
.text
funcion: li  $t0, 0              # i = 0
fbucle: bge  $t0, $a1, ffin      # i < N
        sll  $t1, $t0, 2         # i·4 (un float ocupa 4 bytes)
        add  $t1, $a0, $t1       # &A[i]
        s.s  $f12, 0($t1)        # A[i] = x
        addi $t0, $t0, 1
        b    fbucle
ffin:   li.s $f0, 0.0            # return 0.0
        jr   $ra
"""

M30 = """\
.data
_A:     .float 1.0, 1.0, 1.0, 1.0, 9.0
_x:     .float 2.5
.text
main:   la   $a0, _A
        li   $a1, 4
        l.s  $f12, _x
        jal  funcion
        mov.s $f12, $f0          # imprimir lo que devuelve
        li   $v0, 2
        syscall
        li   $t0, 0
        la   $t1, _A
_p:     li   $a0, ' '
        li   $v0, 11
        syscall
        l.s  $f12, 0($t1)
        li   $v0, 2
        syscall
        addi $t1, $t1, 4
        addi $t0, $t0, 1
        blt  $t0, 5, _p
        li   $v0, 10
        syscall
"""

S32 = """\
# float Integral(F, a, b, n):  $a0 = dirección de F,  $a1 = a,  $a2 = b  (bits IEEE 754 en registros enteros),
#                              $a3 = n (entero)  →  $v0 = resultado (bits IEEE 754)
# Método de los rectángulos con x_i = a + i·B  (i = 0 … n−1),  B = (b − a) / n
.text
Integral:
        addi $sp, $sp, -28
        sw   $ra, 24($sp)
        sw   $s0, 20($sp)
        sw   $s1, 16($sp)
        sw   $s2, 12($sp)
        s.s  $f20, 8($sp)        # $f20…$f31 se conservan entre llamadas (como los $s)
        s.s  $f22, 4($sp)
        s.s  $f24, 0($sp)

        move $s0, $a0            # dirección de F
        move $s1, $a3            # n
        li   $s2, 0              # i = 0
        mtc1 $a1, $f4            # a
        mtc1 $a2, $f6            # b
        mtc1 $a3, $f8
        cvt.s.w $f8, $f8         # n como float
        sub.s $f20, $f6, $f4     # b − a
        div.s $f20, $f20, $f8    # B = (b − a) / n
        mov.s $f22, $f4          # x = a
        mtc1 $zero, $f24         # suma = 0.0

ibucle: bge  $s2, $s1, ifin
        mfc1 $a0, $f22           # F recibe x en $a0
        jalr $s0                 # llamada a la función cuya dirección está en $s0
        mtc1 $v0, $f10           # F(x) llega en $v0
        mul.s $f10, $f10, $f20   # B · F(x_i)
        add.s $f24, $f24, $f10   # suma += área del rectángulo
        add.s $f22, $f22, $f20   # x += B
        addi $s2, $s2, 1
        b    ibucle

ifin:   mfc1 $v0, $f24           # resultado en $v0
        lw   $ra, 24($sp)
        lw   $s0, 20($sp)
        lw   $s1, 16($sp)
        lw   $s2, 12($sp)
        l.s  $f20, 8($sp)
        l.s  $f22, 4($sp)
        l.s  $f24, 0($sp)
        addi $sp, $sp, 28
        jr   $ra
"""


def _m32(a, b, n, cuerpo):
    return f""".data
_a:     .float {a}
_b:     .float {b}
.text
main:   la   $a0, F
        lw   $a1, _a
        lw   $a2, _b
        li   $a3, {n}
        jal  Integral
        mtc1 $v0, $f12
        li   $v0, 2
        syscall
        li   $v0, 10
        syscall
F:      mtc1 $a0, $f0            # F(x) de la prueba
{cuerpo}        mfc1 $v0, $f0
        jr   $ra
"""


M32a = _m32("0.0", "1.0", 4, "        mul.s $f0, $f0, $f0      # x²\n")
M32b = _m32("1.0", "3.0", 2, "        add.s $f0, $f0, $f0      # 2x\n")

S34 = """\
# struct Datos { int a; char b; int c[4]; }  → a: +0, b: +4 (y 3 bytes de relleno), c: +8 … +23 → 24 bytes
.text
main:   jal  f2
        li   $v0, 10
        syscall

# int f1(struct Datos d): la estructura llega POR VALOR, copiada en la pila por quien llama (en 0($sp) … 23($sp))
f1:     lw   $v0, 16($sp)        # d.c[2] → 8 + 2·4 = 16
        jr   $ra

f2:     addi $sp, $sp, -32       # x (24 bytes) + $ra (4) + relleno (4)
        sw   $ra, 28($sp)
        li   $t0, 9
        sw   $t0, 0($sp)         # x.a = 9
        li   $t0, 'c'
        sb   $t0, 4($sp)         # x.b = 'c'
        sw   $zero, 8($sp)       # x.c[0] = 0
        li   $t0, 1
        sw   $t0, 12($sp)        # x.c[1] = 1
        li   $t0, 2
        sw   $t0, 16($sp)        # x.c[2] = 2
        li   $t0, 3
        sw   $t0, 20($sp)        # x.c[3] = 3
        # paso por valor: se COPIA x en la cima de la pila (24 bytes = 6 palabras)
        addi $sp, $sp, -24
        li   $t1, 0
copia:  add  $t2, $sp, $t1
        lw   $t3, 24($t2)        # palabra de x
        sw   $t3, 0($t2)         # → copia
        addi $t1, $t1, 4
        blt  $t1, 24, copia
        jal  f1                  # k = f1(x)
        addi $sp, $sp, 24        # quitar la copia
        move $a0, $v0            # print_int(k)
        li   $v0, 1
        syscall
        lw   $ra, 28($sp)
        addi $sp, $sp, 32
        jr   $ra
"""

S35 = """\
.text
main:   jal  f2
        li   $v0, 10
        syscall

# int f1(struct Datos *d): llega la DIRECCIÓN en $a0 → d->c[2] está en 16($a0)
f1:     lw   $v0, 16($a0)
        jr   $ra

f2:     addi $sp, $sp, -32       # x (24 bytes) + $ra + relleno
        sw   $ra, 28($sp)
        li   $t0, 9
        sw   $t0, 0($sp)         # x.a = 9
        li   $t0, 'c'
        sb   $t0, 4($sp)         # x.b = 'c'
        sw   $zero, 8($sp)
        li   $t0, 1
        sw   $t0, 12($sp)
        li   $t0, 2
        sw   $t0, 16($sp)
        li   $t0, 3
        sw   $t0, 20($sp)
        move $a0, $sp            # &x
        jal  f1                  # k = f1(&x)
        move $a0, $v0
        li   $v0, 1
        syscall
        lw   $ra, 28($sp)
        addi $sp, $sp, 32
        jr   $ra
"""

S36 = """\
.text
main:   jal  f2
        li   $v0, 10
        syscall

# struct Datos f1(void): devolver una estructura de 24 bytes no cabe en $v0/$v1 →
# quien llama reserva el sitio y pasa su dirección (argumento «oculto») en $a0; f1 la rellena.
f1:     li   $t0, 9
        sw   $t0, 0($a0)         # p.a = 9
        li   $t0, 'c'
        sb   $t0, 4($a0)         # p.b = 'c'
        sw   $zero, 8($a0)       # p.c[0] = 0
        li   $t0, 1
        sw   $t0, 12($a0)
        li   $t0, 2
        sw   $t0, 16($a0)
        li   $t0, 3
        sw   $t0, 20($a0)        # p.c[3] = 3
        move $v0, $a0            # (por convenio, se devuelve también la dirección)
        jr   $ra

f2:     addi $sp, $sp, -32       # x (24 bytes) + $ra + relleno
        sw   $ra, 28($sp)
        move $a0, $sp            # dónde quiero el resultado: en x
        jal  f1                  # x = f1()
        lw   $a0, 20($sp)        # k = x.c[3] → 8 + 3·4 = 20
        li   $v0, 1
        syscall
        lw   $ra, 28($sp)
        addi $sp, $sp, 32
        jr   $ra
"""

P = Prueba
MIPS = "mips"

HOJA = Hoja("ensamblador", "Programación en ensamblador (MIPS32)", "fc",
            "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "36 ejercicios: programas, funciones y pila, vectores, cadenas, coma flotante, estructuras y formatos de instrucción.", [

Ejercicio("ens-1", "d = (a+b)·(a+b)",
r"""Dada la expresión `int a = 6; int b = 7; int c = 3; int d; d = (a+b) * (a+b);` escriba un fragmento en ensamblador
del MIPS 32 que la evalúe. El resultado ha de almacenarse en el registro **$t5**.""",
r"""Cargamos los valores con `li` (cargar inmediato), sumamos una vez y multiplicamos el resultado por sí mismo (no hace
falta sumar dos veces). `mul` es una pseudoinstrucción de 3 operandos: el ensamblador la traduce a `mult` + `mflo`.""" + asm(S1) +
"Al final **$t5 = 13 · 13 = 169**.",
pista="Calcula a+b una sola vez en un registro temporal.",
programa=Programa(MIPS, [P(regs={"$t5": 169}, descripcion="a=6, b=7 → $t5 = 169")], solucion=S1),
respuestas=[R("Valor final de $t5", 169)], herramienta="Simulador MIPS"),

Ejercicio("ens-2", "Suma de los 100 primeros naturales",
r"""Escriba un programa en ensamblador del MIPS 32 que calcule la suma de los 100 primeros números naturales.
El programa debe dejar el resultado en el registro **$v0**.""",
r"""Es el bucle `for (i = 1; i <= 100; i++) suma += i;` con la suma directamente en $v0.

💡 **Trampa típica:** si terminas con `li $v0, 10 / syscall` (exit) **machacas $v0** con el 10. Por eso el programa
termina sin más (el simulador para al llegar al final del código).""" + asm(S2) +
"Resultado: $v0 = 1 + 2 + … + 100 = 100·101/2 = **5050** (Gauss lo hizo de cabeza 😉).",
pista="Bucle con contador de 1 a 100. ¡No llames a exit con $v0!",
programa=Programa(MIPS, [P(regs={"$v0": 5050}, descripcion="$v0 = 5050")], solucion=S2),
respuestas=[R("$v0", 5050)], herramienta="Simulador MIPS"),

Ejercicio("ens-3", "Traza de un bucle con lw / sw",
r"""Dado el fragmento:""" + asm(S3.replace("main:   ", "        ")) +
r"""Indique el valor de **$t0, $t1, $t2** y de las posiciones de memoria **a** y **b** al final de la ejecución.""",
r"""Al empezar: $t0 = 2, $t1 = a = 10, $t2 = b = 5. El bucle se repite **mientras $t0 ≤ 10** (sale con `bgt` cuando $t0 > $t1):

| Vuelta | $t0 antes | $t2 después |
|---|---|---|
| 1 | 2 | 7 |
| 2 | 3 | 9 |
| … | … | … |
| 9 | 10 | 23 |

Son $10 - 2 + 1 = 9$ vueltas: $t2 = 5 + 9\cdot2 = 23$ y $t0 termina en 11. Luego se guardan en memoria.

**Final:** $t0 = 11 · $t1 = 10 · $t2 = 23 · a = 11 · b = 23.""",
pista="Cuenta cuántas veces se cumple $t0 ≤ 10 empezando en 2.",
programa=Programa(MIPS, [P(regs={"$t0": 11, "$t1": 10, "$t2": 23}, memoria={"a": [11], "b": [23]},
                           descripcion="registros y memoria finales")], solucion=S3),
respuestas=[R("$t0", 11), R("$t1", 10), R("$t2", 23), R("a", 11), R("b", 23)], herramienta="Simulador MIPS"),

Ejercicio("ens-4", "Imprimir el resultado",
r"""Modifique el programa anterior para imprimir el resultado por pantalla.""",
r"""Para imprimir un entero: **$a0 ← valor, $v0 ← 1, syscall**. Para un carácter (el espacio que separa): $v0 ← 11.""" + asm(S4) +
"Imprime `11 23`.",
programa=Programa(MIPS, [P(salida="11 23", descripcion="imprime a y b")], solucion=S4, plantilla=S3),
herramienta="Simulador MIPS"),

Ejercicio("ens-5", "¿Uno es múltiplo del otro?",
r"""Escriba un programa que lea dos números enteros A y B e indique si uno de ellos es múltiplo del otro.""",
r"""**Idea:** A es múltiplo de B si el resto de A/B es 0 (y al revés). `rem` (pseudoinstrucción) da el resto.

⚠️ **Casos límite:** no se puede dividir entre 0. El 0 es múltiplo de cualquier número (0 = 0·B), así que si A = 0 la
respuesta es «sí»; y si B = 0 solo hay que mirar si B es múltiplo de A (lo es: 0 = 0·A).

La app comprueba la palabra **Si** / **No** en lo que imprimes (con o sin tilde).""" + asm(S5),
pista="Usa rem $t2, $t0, $t1 y compara con 0. Cuidado con dividir entre 0.",
programa=Programa(MIPS, [P("12\n4", "si", descripcion="A=12, B=4"), P("4\n12", "si", descripcion="A=4, B=12"),
                         P("7\n3", "no", descripcion="A=7, B=3"), P("-9\n3", "si", descripcion="A=−9, B=3"),
                         P("0\n5", "si", descripcion="A=0, B=5")], solucion=S5),
herramienta="Simulador MIPS"),

Ejercicio("ens-6", "Triángulo 1, 12, 123…",
r"""Escriba un programa que lea un número N y muestre por pantalla:
```
1
12
123
1234
…
1 2 3 4 5 … N
```""",
r"""Dos bucles anidados: la **fila** va de 1 a N, y en cada fila la **columna** va de 1 a fila. Usamos $s0 para N
(no lo toca ninguna syscall). Separamos con espacio para que se lea bien cuando N ≥ 10 (si no, «1112» sería ambiguo);
la app acepta las dos formas.""" + asm(S6),
pista="Bucle externo i = 1..N; bucle interno j = 1..i imprimiendo j; salto de línea al acabar cada fila.",
programa=Programa(MIPS, [P("4", "1\n1 2\n1 2 3\n1 2 3 4", descripcion="N = 4", modo="sin_espacios"),
                         P("1", "1", descripcion="N = 1", modo="sin_espacios")], solucion=S6),
herramienta="Simulador MIPS"),

Ejercicio("ens-7", "a = b + c + 100",
r"""Indique la secuencia de instrucciones del MIPS para ejecutar la sentencia de C `a = b + c + 100;` (a, b y c son int).""",
r"""Las variables globales viven en memoria (.data). MIPS es **load/store**: hay que traerlas a registros (`lw`), operar y
volver a guardar (`sw`). El 100 cabe en el inmediato de 16 bits de `addi`.

Para probarlo, usa la plantilla (b = 5, c = 7): debe quedar **a = 112**.""" + asm(S7),
programa=Programa(MIPS, [P(memoria={"a": [112]}, descripcion="b=5, c=7 → a = 112")], solucion=S7,
                  plantilla=".data\na:      .word 0\nb:      .word 5\nc:      .word 7\n.text\nmain:\n        # tu código aquí\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-8", "Imprimir el mayor de dos números",
r"""Escriba un programa en ensamblador que lea dos números enteros e imprima el mayor de ellos.""",
r"""Suponemos que el mayor es el primero y, si no lo es, lo cambiamos: así solo hace falta un salto.""" + asm(S8),
programa=Programa(MIPS, [P("3\n8", "8", descripcion="3 y 8"), P("9\n-2", "9", descripcion="9 y −2"),
                         P("5\n5", "5", descripcion="5 y 5"), P("-7\n-3", "-3", descripcion="−7 y −3")], solucion=S8),
herramienta="Simulador MIPS"),

Ejercicio("ens-9", "¿Par o impar?",
r"""Escriba un programa en ensamblador del MIPS que lea un número e indique si es par o impar.""",
r"""El **bit de menos peso** dice la paridad: `andi $t0, $v0, 1` lo aísla (0 → par, 1 → impar). Funciona también con
negativos en complemento a 2 (−3 = …11101, acaba en 1). Con `rem` también vale, pero ojo: −3 rem 2 = −1 (no 1).""" + asm(S9),
programa=Programa(MIPS, [P("7", "impar", descripcion="7"), P("10", "par", descripcion="10"),
                         P("-3", "impar", descripcion="−3"), P("0", "par", descripcion="0")], solucion=S9),
herramienta="Simulador MIPS"),

Ejercicio("ens-10", "2 + 4 + 6 + … + N",
r"""Escriba un programa que lea un número N par y calcule la suma 2 + 4 + 6 + … + N. Asuma que siempre se introduce un
número par. El programa imprimirá el resultado.""",
r"""Como el anterior de los 100 naturales, pero el contador avanza de 2 en 2.
Comprobación: $2+4+\dots+N = 2(1+2+\dots+\tfrac N2) = \tfrac N2\left(\tfrac N2+1\right)$. Para N = 10: 5·6 = 30.""" + asm(S10),
programa=Programa(MIPS, [P("10", "30", descripcion="N = 10"), P("2", "2", descripcion="N = 2"),
                         P("100", "2550", descripcion="N = 100")], solucion=S10),
herramienta="Simulador MIPS"),

Ejercicio("ens-11", "Función que sustituye un carácter en una cadena",
r"""Escriba una función que reciba tres argumentos: la dirección de comienzo de una cadena de caracteres, el código ASCII
de un carácter y el de otro. La función debe sustituir en la cadena todas las ocurrencias del carácter del segundo
argumento por el del tercero.

*En la app:* llama a tu función **sustituir**. Escribe solo la función: la app añade un main que la llama.""",
r"""**Convenio:** argumentos en **$a0, $a1, $a2**. Recorremos la cadena byte a byte (`lb`) hasta el `'\0'` y, si el carácter
coincide, escribimos el nuevo con `sb`. Como no llama a ninguna otra función (es **hoja**) y solo usa $t, no necesita pila.""" +
asm(S11) + "Con «hola mundo, otro dia» cambiando 'o' por '0' queda «h0la mund0, 0tr0 dia».",
pista="lb para leer el carácter, sb para escribirlo, y avanzar la dirección de 1 en 1 (son bytes).",
programa=Programa(MIPS, [P(salida="h0la mund0, 0tr0 dia", main=M11, modo="texto", descripcion="'o' → '0'"),
                         P(salida="hola mundo, otro dia", main=M11b, modo="texto", descripcion="carácter que no aparece")],
                  solucion=S11, plantilla="sustituir:\n        # $a0 = cadena, $a1 = carácter viejo, $a2 = nuevo\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-12", "Llamar a func(a, b, c) e imprimir el resultado",
r"""Considere una función `func` que recibe tres enteros y devuelve un entero, y el segmento de datos:
```
.data
a: .word 5
b: .word 7
c: .word 9
```
Indique el código necesario para llamar a la función pasando los valores de a, b y c e imprimir el valor que devuelve.

*En la app:* no hace falta escribir `func`; se añade una de ejemplo que devuelve a + b + c (= 21).""",
r"""**Convenio de paso de parámetros:** los 4 primeros argumentos van en **$a0–$a3**, la llamada es **`jal`** (guarda la
vuelta en $ra) y el resultado llega en **$v0**.""" + asm(S12),
programa=Programa(MIPS, [P(salida="21", descripcion="func de ejemplo: a + b + c")], solucion=S12, anexo=FUNC12,
                  anexo_si_falta="func", plantilla=".data\na:      .word 5\nb:      .word 7\nc:      .word 9\n.text\nmain:\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-13", "Vector de 800 bytes: v[20] = v[30] y v[10] = b",
r"""Dado:
```
.data
a: .word 10
b: .word 5
.align 2
v: .space 800
```
Si v es un array de enteros: a) número de elementos; b) instrucciones para `v[20] = v[30];` c) instrucciones para `v[10] = b;`""",
r"""**a)** Cada entero ocupa 4 bytes → $800/4 =$ **200 elementos**. (`.align 2` asegura que v empieza en múltiplo de $2^2=4$.)

**b) y c)** La dirección de `v[i]` es **v + 4·i**: v[30] → +120, v[20] → +80, v[10] → +40.""" + asm(S13) +
"*En la app:* se rellena v[30] = 77 antes de ejecutar y se comprueba que v[20] = 77 y v[10] = 5.",
programa=Programa(MIPS, [P(mem_inicial={"v+120": [77]}, memoria={"v+80": [77], "v+40": [5]},
                           descripcion="v[30] = 77 → v[20] = 77, v[10] = b = 5")], solucion=S13,
                  plantilla=".data\na:      .word 10\nb:      .word 5\n.align 2\nv:      .space 800\n.text\nmain:\n"),
respuestas=[R("a) Número de elementos", 200)], herramienta="Simulador MIPS"),

Ejercicio("ens-14", "maximo y maximoV (funciones que llaman a funciones)",
r"""Escriba en MIPS la función `int maximo(int A, int B)` que devuelve el mayor. Usándola, implemente
```c
void maximoV(int v1[], int v2[], int v3[], int N) {
    int i;
    for (i = 0; i < N; i++)
        v3[i] = maximo(v1[i], v2[i]);
}
```
siguiendo el convenio de paso de parámetros.

*En la app:* escribe las dos funciones (sin main): la app las prueba con su propio main y comprueba además que tus
registros $s0 y $s1 se conservan.""",
r"""**maximo** es una función **hoja**: no llama a nadie, así que no necesita guardar nada.

**maximoV** **no es hoja**: al hacer `jal maximo` se machaca **$ra**, y tras la llamada los $t y $a pueden haber
cambiado. Por eso:
1. Guarda **$ra** en la pila.
2. Copia v1, v2, v3, N e i en registros **$s** (que se conservan entre llamadas)… y como el convenio obliga a devolver
   los $s como estaban, **también los guarda** en la pila y los restaura al final.

💡 Analogía: la pila es como dejar un post-it con «por dónde iba» antes de atender una llamada de teléfono.""" + asm(S14),
pista="maximoV llama a otra función: guarda $ra y usa registros $s (guardándolos antes).",
programa=Programa(MIPS, [P(salida="5 9 3 -1 7 111 222", main=M14, descripcion="v1 = 1 9 3 −4 7, v2 = 5 2 3 −1 0 (+ $s intactos)"),
                         P(salida="8 12", main=M14b, descripcion="maximo(−3, 8) y maximo(12, 12)")], solucion=S14,
                  plantilla="maximo:\n        jr   $ra\n\nmaximoV:\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-15", "Vector global y función suma",
r"""Escriba en MIPS un programa equivalente:
```c
int vector[1024];   // variable global
int funcion1() {
    int z, i;
    for (i = 0; i < 1024; i++) vector[i] = i;
    z = suma(1024);
    print_int(z);
}
int suma(int n) {
    int s = 0, i;
    for (i = 0; i < n; i++) s = s + vector[i];
    return s;
}
```""",
r"""Una variable **global** va en **.data** (`.space 4096`: 1024 enteros × 4 bytes) y cualquier función la usa por su
etiqueta. `suma` es hoja; `funcion1` hace de main.""" + asm(S15) +
"Imprime $0 + 1 + \\dots + 1023 = 1023\\cdot1024/2 =$ **523 776**.",
programa=Programa(MIPS, [P(salida="523776", descripcion="imprime 523776")], solucion=S15),
herramienta="Simulador MIPS"),

Ejercicio("ens-16", "Vector local (en la pila) pasado como argumento",
r"""Igual que el anterior, pero ahora el vector es **local** a `funcion1` y se pasa a `int suma(int vector[], int n)`.""",
r"""Una variable **local** vive en el **marco de pila** de la función: `funcion1` reserva 4096 bytes moviendo $sp
(más 4 para guardar $ra, porque llama a `suma`). En C, pasar un array es pasar **su dirección**: $a0 = $sp.

⚠️ Al acabar hay que **devolver la pila tal como estaba** (`addi $sp, $sp, 4100`).""" + asm(S16) +
"Imprime **523 776**, igual que antes, pero ahora sin variables globales.",
programa=Programa(MIPS, [P(salida="523776", descripcion="imprime 523776")], solucion=S16),
herramienta="Simulador MIPS"),

Ejercicio("ens-17", "Formato de «sumar R1, R2, dirección»",
r"""Computador de 32 bits con 140 instrucciones máquina y 64 registros. La instrucción `sumar R1, R2, dirección` suma R1 y
R2 y deja el resultado en la posición de memoria *dirección*. a) Proponga un formato. b) Escriba un fragmento MIPS equivalente.""",
r"""**a)** Código de operación: $\lceil\log_2 140\rceil =$ **8 bits** ($2^7 = 128 < 140$). Cada registro: $\log_2 64 =$ **6 bits**.
La dirección es de **32 bits** (computador de 32 bits). Total: $8 + 6 + 6 + 32 = 52 > 32$ → **no cabe en una palabra**:
ocupa **2 palabras**.

| Palabra 1 | | | | Palabra 2 |
|---|---|---|---|---|
| CO (8) | R1 (6) | R2 (6) | sin usar (12) | dirección (32) |

**b)**""" + asm("add  $t0, $t1, $t2     # R1 + R2\nsw   $t0, direccion     # se guarda en memoria"),
respuestas=[R("Bits del código de operación", 8), R("Bits por registro", 6), R("Palabras que ocupa", 2)]),

Ejercicio("ens-18", "Formato de ADDV R1, R2, M (16 bits)",
r"""Computador de 16 bits, direccionamiento por bytes, 60 instrucciones y 8 registros. Indique el formato de
`ADDV R1, R2, M` (R1 y R2 registros, M dirección de memoria).""",
r"""- CO: $\lceil\log_2 60\rceil =$ **6 bits**. Registros: $\log_2 8 =$ **3 bits** cada uno.
- M: dirección de **16 bits**.
- Total $6 + 3 + 3 + 16 = 28$ bits > 16 → **2 palabras** (32 bits):

| Palabra 1 (16 bits) | | | | Palabra 2 (16 bits) |
|---|---|---|---|---|
| CO (6) | R1 (3) | R2 (3) | sin usar (4) | M (16) |""",
respuestas=[R("Bits de CO", 6), R("Bits por registro", 3), R("Palabras", 2)]),

Ejercicio("ens-19", "SWAPM dir1, dir2",
r"""Computador de 32 bits, direccionamiento por bytes, 64 instrucciones y 128 registros. `SWAPM dir1, dir2` intercambia el
contenido de dos posiciones de memoria. a) Espacio direccionable. b) Formato. c) Fragmento MIPS equivalente.
d) Si se fuerza a que ocupe una palabra, ¿qué rango de direcciones se podría usar (binario puro)?""",
r"""**a)** Direcciones de 32 bits → $2^{32}$ bytes = **4 GB**.

**b)** CO: $\log_2 64 = 6$ bits; dos direcciones de 32 bits → $6 + 32 + 32 = 70$ bits → **3 palabras** (96 bits):
palabra 1 = CO (6) + 26 sin usar; palabra 2 = dir1; palabra 3 = dir2. (Los 128 registros no intervienen.)

**c)**""" + asm("lw   $t0, dir1\nlw   $t1, dir2\nsw   $t0, dir2\nsw   $t1, dir1") + r"""
**d)** En una palabra: $32 - 6 = 26$ bits para las dos direcciones → **13 bits** cada una → de **0 a $2^{13}-1 = 8191$**.""",
respuestas=[R("a) GB direccionables", 4), R("b) Palabras", 3), R("d) Dirección máxima", 8191)]),

Ejercicio("ens-20", "Vector de 1024 bytes",
r"""Dado:
```
.data
.align 2
vector: .space 1024     # vector de enteros de 32 bits
```
a) Número de componentes. b) Instrucciones para `vector[8] = 30;` c) Fragmento que lea un entero y lo asigne a **todas**
las componentes.""",
r"""**a)** $1024/4 =$ **256** componentes.

**b)** vector[8] está en vector + 8·4 = vector + 32.

**c)** Bucle de 256 vueltas guardando el número leído (que llega en $v0).""" + asm(S20),
errata="El enunciado pone «.data:» con dos puntos; la directiva es «.data» (sin ellos).",
programa=Programa(MIPS, [P("7", memoria={"vector": [7] * 256}, descripcion="entrada 7 → las 256 componentes valen 7"),
                         P("-1", memoria={"vector": [-1] * 256}, descripcion="entrada −1")], solucion=S20,
                  plantilla=".data\n.align 2\nvector: .space 1024\n.text\nmain:\n"),
respuestas=[R("a) Componentes", 256)], herramienta="Simulador MIPS"),

Ejercicio("ens-21", "¿Qué imprime? (suma 5+4+3+2+1)",
r"""Dado el programa:""" + asm(S21.replace("sub  $t0", "sub, $t0")) + r"""
a) ¿Qué valor se imprime? b) Si el valor de $a0 se representa en **complemento a uno**, ¿qué rango de números podría
pasarse a la función?""",
r"""**a)** `funcion` hace $t1 = $t0 + ($t0 − 1) + … + 1 bajando $t0 hasta 0: con $a0 = 5 → 5 + 4 + 3 + 2 + 1 = **15**.
Se imprime **15**.

**b)** Con 32 bits en Ca1 el rango es $[-(2^{31}-1),\,2^{31}-1]$ = **[−2 147 483 647, 2 147 483 647]**.
(Aunque la función solo tiene sentido con n ≥ 0: con un negativo, $t0 nunca llega a 0 bajando… daría la vuelta.)""",
errata="En el enunciado aparece «sub, $t0, $t0, 1» con una coma de más tras «sub».",
programa=Programa(MIPS, [P(salida="15", descripcion="imprime 15")], solucion=S21),
respuestas=[R("a) Valor impreso", 15), R("b) Máximo en Ca1", 2**31 - 1)], herramienta="Simulador MIPS"),

Ejercicio("ens-22", "Función Vocales: contar las 'a'",
r"""La función `Vocales` recibe la dirección de inicio de una cadena y calcula cuántas veces aparece 'a' (minúscula).
Con la cadena nula devuelve −1; si no hay ninguna 'a', 0. a) Prográmela. b) ¿En qué registro se pasa el argumento y en
cuál se recoge el resultado? c) Complete el main para contar las 'a' de "Hola" e imprimirlo.

*En la app:* escribe la función `Vocales`; se prueba con varias cadenas y con el puntero nulo (0).""",
r"""**b)** Argumento en **$a0** (la dirección), resultado en **$v0**.

**a)** Se recorre la cadena con `lb` hasta el '\0'. «Cadena nula» se interpreta como **puntero nulo** ($a0 = 0); la
solución también devuelve −1 con la cadena vacía "" por si tu profe lo entiende así.""" + asm(S22) +
"**c)**" + asm(M22_MAIN) + "Imprime **1** (la 'a' final de «Hola»; la «H» no cuenta).",
programa=Programa(MIPS, [P(salida="1", main=_main_cad("Hola"), descripcion="«Hola» → 1"),
                         P(salida="3", main=_main_cad("banana"), descripcion="«banana» → 3"),
                         P(salida="0", main=_main_cad("xyz A"), descripcion="«xyz A» → 0 (la A mayúscula no cuenta)"),
                         P(salida="-1", main=_main_cad("", nulo=True), descripcion="puntero nulo → −1")],
                  solucion=S22, plantilla="Vocales:\n        # $a0 = dirección de la cadena → $v0 = nº de 'a'\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-23", "¿Qué imprime? (bgt con 5 y 10)",
r"""Indique el valor que se imprime:""" + asm(S23),
r"""Con $a0 = 5: `bgt $a0, $t0, et1` pregunta si 5 > 10 → **no**, así que no salta. Se ejecuta `li $t0, 10` y
`add $v0, $t0, $a0` = 10 + 5 = 15, y `b et2` vuelve. Se imprime **15**.""",
programa=Programa(MIPS, [P(salida="15", descripcion="imprime 15")], solucion=S23),
respuestas=[R("Valor impreso", 15)], herramienta="Simulador MIPS"),

Ejercicio("ens-24", "SumarValor: sumar un valor a todo un vector",
r"""`SumarValor` recibe: la dirección de inicio de un vector de enteros, el número de componentes y un valor entero, y suma
el valor a todas las componentes. a) ¿En qué registros van los parámetros? b) Prográmela. c) Con
`v: .word 7, 8, 3, 4, 5, 6` escriba el main que le sume 5 e imprima todas las componentes.""",
r"""**a)** $a0 = dirección del vector, $a1 = número de componentes, $a2 = valor.

**b) y c)**""" + asm(S24) + "Imprime **12 13 8 9 10 11**.",
programa=Programa(MIPS, [P(salida="12 13 8 9 10 11", descripcion="tu programa completo (main + función)"),
                         P(salida="-11 -10 90", main=M24, descripcion="tu SumarValor con otro vector y −10")],
                  solucion=S24, plantilla=".data\nv:      .word 7, 8, 3, 4, 5, 6\n.text\n.globl main\nmain:\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-25", "Formato de beqz $t1, $t2, dirección",
r"""Computador de 32 bits con 48 registros y 200 instrucciones. Indique el formato de la instrucción hipotética
`beqz $t1, $t2, dirección` (dos registros y una dirección de memoria).""",
r"""- CO: $\lceil\log_2 200\rceil =$ **8 bits**. Registros: $\lceil\log_2 48\rceil =$ **6 bits** cada uno.
- Quedan $32 - 8 - 6 - 6 = 12$ bits: no cabe una dirección de 32 bits. Dos opciones válidas:
  1. **Dos palabras**: CO (8) | R1 (6) | R2 (6) | sin usar (12) — y la dirección completa (32) en la segunda palabra.
  2. **Una palabra** con direccionamiento **relativo al PC**: los 12 bits son un desplazamiento en Ca2
     (de −2048 a 2047 instrucciones/bytes desde el PC). Así lo hace MIPS con `beq`.""",
respuestas=[R("Bits de CO", 8), R("Bits por registro", 6)]),

Ejercicio("ens-26", "Direccionamiento relativo a registro base",
r"""Indique una instrucción del MIPS con direccionamiento **relativo a registro base**. ¿En qué consiste?""",
r"""Por ejemplo **`lw $t0, 8($t1)`** (o `sw`, `lb`, `sb`…).

La dirección efectiva se calcula como **contenido del registro base + desplazamiento** de la instrucción:
$DE = \$t1 + 8$. Es ideal para estructuras y vectores: el registro apunta al principio y el desplazamiento elige el campo.

💡 Analogía: «la casa que está 8 portales más allá de la de mi amiga ($t1)».""",
respuestas=[]),

Ejercicio("ens-27", "Diseñar el juego de instrucciones (115 instrucciones, 64 registros)",
r"""Computador de 32 bits, direccionamiento por bytes, 64 registros, 115 instrucciones, modelo registro-registro. Tipos:
transferencias registro–memoria (direccionamiento directo y relativo a registro base), aritmético-lógicas, bifurcación
incondicional a una dirección y bifurcaciones condicionales (condición en un registro, salto relativo al PC).
a) Diseñe los formatos (todas en una palabra). b) Desplazamiento máximo del relativo a registro base (Ca2).
c) Rango de direcciones del salto incondicional (binario natural). d) ¿RISC o CISC?""",
r"""CO: $\lceil\log_2 115\rceil =$ **7 bits**. Registro: **6 bits**.

**a)** Formatos de 32 bits:

| Tipo | Campos |
|---|---|
| Carga/almacenamiento directo | CO (7) · R (6) · dirección (19) |
| Carga/almacenamiento relativo a base | CO (7) · R (6) · Rbase (6) · desplazamiento (13) |
| Aritmético-lógica (reg-reg) | CO (7) · Rd (6) · Rs (6) · Rt (6) · sin usar (7) |
| Salto incondicional | CO (7) · dirección (25) |
| Salto condicional | CO (7) · R (6) · desplazamiento respecto al PC (19) |

**b)** 13 bits en Ca2 → máximo **$2^{12}-1 = 4095$** (mínimo −4096).

**c)** 25 bits en binario natural → de **0 a $2^{25}-1 = 33\,554\,431$**.

**d)** **RISC**: todas las instrucciones miden lo mismo (una palabra), hay pocos formatos y modos de direccionamiento, y
solo las cargas/almacenamientos tocan memoria (modelo registro-registro).""",
respuestas=[R("Bits de CO", 7), R("b) Desplazamiento máximo", 4095), R("c) Dirección máxima", 2**25 - 1),
            R("d) RISC o CISC", ["risc"], "texto")]),

Ejercicio("ens-28", "CPU de 16 bits: formatos, ocupación y traza",
r"""CPU de 16 bits, memoria por bytes, 16 registros y 180 instrucciones, entre ellas `LOADI R, inm`, `STORE R, dir`,
`ADDI R1, R2, inm`, `ADD R1, R2` (R1 ← R1 + R2) y `BNEZ R, dir`. Direcciones e inmediatos son enteros de 16 bits. Programa:
```
      LOADI R1, 0
      LOADI R2, 3
      LOADI R3, 1
ETI:  ADD   R1, R3
      ADDI  R3, R3, 2
      ADDI  R2, R2, -1
      BNEZ  R2, ETI
      STORE R3, 500
```
a) Formato posible. b) Si se carga en la posición 1000, ¿cuántas palabras ocupa y qué contienen? c) ¿Qué hace y qué
valen R1, R2 y R3 al final?""",
r"""**a)** CO: $\lceil\log_2 180\rceil =$ **8 bits**; registro: **4 bits**; la palabra es de **16 bits**.

| Instrucción | Palabra 1 | Palabra 2 | Palabras |
|---|---|---|---|
| LOADI R, inm | CO (8) · R (4) · sin usar (4) | inm (16) | 2 |
| STORE R, dir | CO (8) · R (4) · sin usar (4) | dir (16) | 2 |
| ADDI R1, R2, inm | CO (8) · R1 (4) · R2 (4) | inm (16) | 2 |
| ADD R1, R2 | CO (8) · R1 (4) · R2 (4) | — | 1 |
| BNEZ R, dir | CO (8) · R (4) · sin usar (4) | dir (16) | 2 |

**b)** $3\cdot2 + 1 + 2\cdot2 + 2 + 2 =$ **15 palabras** (30 bytes, de la 1000 a la 1029). Eligiendo, por ejemplo,
LOADI = 00000001, STORE = 00000010, ADDI = 00000011, ADD = 00000100 y BNEZ = 00000101 (los bits sin usar a 0):

| Dir. | Contenido | |
|---|---|---|
| 1000 | 00000001 0001 0000 | LOADI R1 |
| 1002 | 0000000000000000 | 0 |
| 1004 | 00000001 0010 0000 | LOADI R2 |
| 1006 | 0000000000000011 | 3 |
| 1008 | 00000001 0011 0000 | LOADI R3 |
| 1010 | 0000000000000001 | 1 |
| 1012 | 00000100 0001 0011 | ETI: ADD R1, R3 |
| 1014 | 00000011 0011 0011 | ADDI R3, R3 |
| 1016 | 0000000000000010 | 2 |
| 1018 | 00000011 0010 0010 | ADDI R2, R2 |
| 1020 | 1111111111111111 | −1 (Ca2) |
| 1022 | 00000101 0010 0000 | BNEZ R2 |
| 1024 | 0000001111110100 | ETI = 1012 |
| 1026 | 00000010 0011 0000 | STORE R3 |
| 1028 | 0000000111110100 | 500 |

**c)** Suma los 3 primeros impares (R2 cuenta 3 vueltas y R3 va tomando 1, 3, 5):

| Vuelta | R1 | R3 | R2 |
|---|---|---|---|
| 1 | 1 | 3 | 2 |
| 2 | 4 | 5 | 1 |
| 3 | 9 | 7 | 0 |

**R1 = 9, R2 = 0, R3 = 7**, y en la posición 500 se guarda **R3 = 7** (¡ojo, no R1!).""",
respuestas=[R("b) Palabras", 15), R("R1", 9), R("R2", 0), R("R3", 7)]),

Ejercicio("ens-29", "Computador de 64 bits: modos de direccionamiento y formatos",
r"""Computador de 64 bits, memoria por bytes, 256 registros y 190 instrucciones. Instrucciones: `LOAD Reg, direccion`,
`STORE Reg1, (Reg2)` y `BEQZ Reg1, direccion`. a) Modos de direccionamiento de cada una. b) Formato (una palabra).
c) Valor máximo de la dirección en LOAD y BEQZ.""",
r"""**a)**
- `LOAD Reg, direccion`: **directo a registro** (Reg) y **directo/absoluto a memoria** (direccion).
- `STORE Reg1, (Reg2)`: directo a registro (Reg1) e **indirecto a registro** ((Reg2): la dirección está en Reg2).
- `BEQZ Reg1, direccion`: directo a registro y **directo/absoluto** para el destino del salto.

**b)** CO: $\lceil\log_2 190\rceil =$ **8 bits**; registro: $\log_2 256 =$ **8 bits**; palabra de 64 bits:
- LOAD: CO (8) · Reg (8) · dirección (**48**)
- STORE: CO (8) · Reg1 (8) · Reg2 (8) · sin usar (40)
- BEQZ: CO (8) · Reg1 (8) · dirección (**48**)

**c)** 48 bits → máximo **$2^{48}-1$** (≈ 2,8·10¹⁴, 256 TB direccionables).""",
errata="El enunciado describe STORE como «almacena en el registro Reg1 el dato de la posición de Reg2»: eso sería una "
       "carga. Un STORE guarda Reg1 en la posición de memoria cuya dirección está en Reg2 (los modos no cambian).",
respuestas=[R("Bits de dirección", 48), R("Dirección máxima", 2**48 - 1)]),

Ejercicio("ens-30", "Función con un vector de float",
r"""Escriba en ensamblador, con el convenio de paso de parámetros, la función:
```c
float funcion(float A[], int N, float x) {
    int i;
    for (i = 0; i < N; i = i + 1) A[i] = x;
    return 0.0;
}
```
*En la app:* llámala **funcion**. El main de prueba imprime lo que devuelves y el vector.""",
r"""**Convenio con coma flotante:** los enteros y direcciones van en $a0–$a3 (A → $a0, N → $a1); el float **x llega en
$f12** (registro del coprocesador 1) y el resultado float se devuelve en **$f0**. Se guarda con `s.s` (*store single*).""" +
asm(S30),
programa=Programa(MIPS, [P(salida="0.0 2.5 2.5 2.5 2.5 9.0", main=M30,
                           descripcion="A = [1,1,1,1,9], N = 4, x = 2,5 → devuelve 0.0 y A = [2,5 ×4, 9]")],
                  solucion=S30, plantilla="funcion:\n        # $a0 = A, $a1 = N, $f12 = x  → $f0\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-31", "Formato para una CPU de 16 bits con 6 registros",
r"""CPU de 16 bits, 6 registros, 64 KB de espacio de direcciones, memoria por bytes (3 ciclos por lectura/escritura) y una
ALU con 20 operaciones. Con código de operación de longitud fija, diseñe el formato para al menos: a) 40 instrucciones
aritmético-lógicas registro-registro; b) 5 de direccionamiento absoluto; c) 5 relativas a registro base con desplazamiento
máximo de 128 bytes; d) 2 de direccionamiento indirecto absoluto.""",
r"""- Instrucciones: $40 + 5 + 5 + 2 = 52$ → CO de **6 bits** ($2^6 = 64 \ge 52$).
- Registros: 6 → **3 bits**. Direcciones: 64 KB = $2^{16}$ → **16 bits**. Palabra: 16 bits.

| Tipo | Palabra 1 (16 bits) | Palabra 2 |
|---|---|---|
| a) Reg-reg | CO (6) · Rd (3) · Rs1 (3) · Rs2 (3) · 1 sin usar | — |
| b) Absoluto | CO (6) · R (3) · 7 sin usar | dirección (16) |
| c) Relativo a base | CO (6) · R (3) · Rbase (3) · 4 sin usar | desplazamiento |
| d) Indirecto absoluto | CO (6) · R (3) · 7 sin usar | dirección del puntero (16) |

c) Un desplazamiento de hasta 128 necesita **8 bits** (sin signo: 0–255; con 7 solo se llega a 127). En la primera palabra
solo quedan 4 bits, así que va en una segunda palabra (o habría que reducir campos).

Las reg-reg caben en **una palabra**; el resto necesitan **dos**.""",
respuestas=[R("Bits de CO", 6), R("Bits por registro", 3), R("Bits de dirección", 16)]),

Ejercicio("ens-32", "Integral por rectángulos (coprocesador y punteros a función)",
r"""Función **Integral** que aproxima $\int_a^b F(x)\,dx \approx \sum_{i} B\cdot F(x_i)$ con $n$ rectángulos de base
$B = (b-a)/n$. Argumentos: **$a0** = dirección del código de F, **$a1** = a, **$a2** = b, **$a3** = n. Devuelve el
resultado en **$v0**. Todos los valores son reales IEEE 754 (salvo n). F recibe su parámetro en $a0 y devuelve en $v0.

*En la app:* se toma $x_i = a + i\cdot B$ (extremo izquierdo, $i = 0\ldots n-1$) y se prueba con $F(x) = x^2$ en
$[0,1]$ con $n = 4$, y con $F(x) = 2x$ en $[1,3]$ con $n = 2$.""",
r"""**Claves:**
1. Los floats llegan **en registros enteros** ($a1, $a2) → hay que pasarlos al coprocesador con **`mtc1`**, y al revés
   con **`mfc1`** para llamar a F y devolver el resultado.
2. n es entero → `mtc1` + **`cvt.s.w`** para convertirlo a float antes de dividir.
3. Se llama a F con **`jalr $s0`** (salto a la dirección guardada en un registro).
4. Integral **no es hoja**: guarda $ra, los $s que usa y los registros FP «salvados» ($f20, $f22, $f24) donde tiene B, x
   y la suma, porque F puede machacar los temporales.""" + asm(S32) + r"""
**Comprobación** ($x^2$ en [0,1], n = 4, B = 0,25): $0{,}25\,(0 + 0{,}0625 + 0{,}25 + 0{,}5625) = 0{,}21875$
(el valor exacto es 1/3: con más rectángulos se acerca). Para $2x$ en [1,3] con n = 2: $1\cdot(2 + 4) = 6$.""",
pista="mtc1/mfc1 para mover bits entre $a/$v y $f; cvt.s.w para convertir n; jalr para llamar a F.",
programa=Programa(MIPS, [P(salida="0.21875", main=M32a, descripcion="x² en [0,1], n = 4"),
                         P(salida="6.0", main=M32b, descripcion="2x en [1,3], n = 2")], solucion=S32,
                  plantilla="Integral:\n        # $a0 = F, $a1 = a, $a2 = b, $a3 = n  → $v0\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("ens-33", "Decodificar y ejecutar código máquina",
r"""Computador de 32 bits (memoria por bytes, 32 registros R0–R31) con el juego de instrucciones de la tabla
(CO en los bits 31–26, R1 en 25–21, R2 en 20–16 y *desp/numero* de 16 bits en Ca2):

| Instrucción | Significado | CO |
|---|---|---|
| add R1, R2 | R1 ← R1 + R2 | 000000 |
| sub R1, R2 | R1 ← R1 − R2 | 000001 |
| AND R1, R2 | R1 ← R1 and R2 | 000010 |
| OR R1, R2 | R1 ← R1 or R2 | 000011 |
| lw R1, (R2) | R1 ← MP[R2] | 000100 |
| sw R1, (R2) | MP[R2] ← R1 | 000101 |
| b desp | PC ← PC + desp | 100000 |
| j R2 | PC ← R2 | 100001 |
| beq R1, R2, desp | si R1 == R2: PC ← PC + desp | 100010 |
| bneq R1, R2, desp | si R1 ≠ R2: PC ← PC + desp | 100011 |
| bgt R1, R2, desp | si R1 > R2: PC ← PC + desp | 100100 |
| blt R1, R2, desp | si R1 < R2: PC ← PC + desp | 100101 |
| li R1, numero | R1 ← numero | 110101 |

Programa (PC = 0x00000010):
```
0x10  11010100100000000000000000000001
0x14  11010100001000000000000000000000
0x18  11010100010000000000000000001010
0x1C  11010100011000000000000000000000
0x20  10010000001000100000000000001100
0x24  00000000001001000000000000000000
0x28  00000000011001000000000000000000
0x2C  10000000000000001111111111110000
0x30  11010100001000000000000010000000
0x34  00010100011000010000000000000000
0x80  00000000000000000000000000000000
0x84  00000000000000000000000000000000
```
a) Obtenga el programa ensamblador. b) Ejecútelo hasta que PC = 0x38. c) Contenido de los registros modificados y de
las posiciones 0x80 y 0x84.""",
r"""**a)** Se trocea cada palabra en CO (6) | R1 (5) | R2 (5) | 16 bits:

| Dir. | CO | R1 | R2 | 16 bits | Instrucción |
|---|---|---|---|---|---|
| 0x10 | 110101 | 00100 | — | 1 | `li R4, 1` |
| 0x14 | 110101 | 00001 | — | 0 | `li R1, 0` |
| 0x18 | 110101 | 00010 | — | 10 | `li R2, 10` |
| 0x1C | 110101 | 00011 | — | 0 | `li R3, 0` |
| 0x20 | 100100 | 00001 | 00010 | 12 | `bgt R1, R2, 12` → a 0x30 |
| 0x24 | 000000 | 00001 | 00100 | — | `add R1, R4` (R1++) |
| 0x28 | 000000 | 00011 | 00100 | — | `add R3, R4` (R3++) |
| 0x2C | 100000 | — | — | −16 | `b −16` → a 0x20 |
| 0x30 | 110101 | 00001 | — | 128 | `li R1, 0x80` |
| 0x34 | 000101 | 00011 | 00001 | — | `sw R3, (R1)` |

¿Desde dónde se cuenta el desplazamiento? Cuando se ejecuta una instrucción el PC **ya apunta a la siguiente**:
bgt en 0x20 → 0x24 + 12 = **0x30** (justo después del bucle) y b en 0x2C → 0x30 − 16 = **0x20** (vuelve a la
comparación). Las dos cuentas encajan, lo que confirma la interpretación. 1111111111110000 en Ca2 es −16.

**b)** Es un bucle `for (R1 = 0; R1 <= 10; R1++) R3++;` → da **11 vueltas** (R1 = 0 … 10). Al salir, R1 = 11; luego
`li R1, 0x80` y `sw R3, (R1)` guarda R3 en la dirección 0x80, y el PC pasa a 0x38.

**c)** **R1 = 0x80 = 128, R2 = 10, R3 = 11, R4 = 1**; MP[0x80] = **11** y MP[0x84] = **0** (no cambia).""",
respuestas=[R("R1 (decimal)", 128), R("R2", 10), R("R3", 11), R("R4", 1), R("MP[0x80]", 11), R("MP[0x84]", 0)],
herramienta="Codificador de instrucciones"),

Ejercicio("ens-34", "Estructura pasada por valor",
r"""Escriba en MIPS:
```c
struct Datos { int a; char b; int c[4]; };
int f1(struct Datos d) { int k; k = d.c[2]; return k; }
void f2(void) {
    struct Datos x; int k;
    x.a = 9; x.b = 'c'; x.c[0] = 0; x.c[1] = 1; x.c[2] = 2; x.c[3] = 3;
    k = f1(x);
    print_int(k);
}
```""",
r"""**1. Disposición en memoria** (alineación: cada int empieza en múltiplo de 4):

| Campo | Desplazamiento |
|---|---|
| a | 0 |
| b | 4 (+ 3 bytes de relleno) |
| c[0] … c[3] | 8, 12, 16, 20 |

Total **24 bytes**. `d.c[2]` está en el desplazamiento $8 + 2\cdot4 = 16$.

**2. Paso por valor:** la función recibe **una copia**. Una estructura de 24 bytes no cabe en $a0–$a3, así que quien
llama **copia la estructura en la pila** y f1 la lee de ahí (si f1 la modificase, x no cambiaría).""" + asm(S34) +
"Imprime **2**.",
programa=Programa(MIPS, [P(salida="2", descripcion="imprime 2")], solucion=S34),
errata="En el código C aparece «sturct» en lugar de «struct».", herramienta="Simulador MIPS"),

Ejercicio("ens-35", "Estructura pasada por referencia (puntero)",
r"""Igual que el anterior, pero ahora `int f1(struct Datos *d) { return d->c[2]; }` y se llama con `k = f1(&x);`""",
r"""Ahora solo viaja **la dirección** de x ($a0 = $sp, donde está x). `d->c[2]` es `lw $v0, 16($a0)`: direccionamiento
relativo a registro base. Mucho más barato que copiar 24 bytes.""" + asm(S35) + "Imprime **2**.",
programa=Programa(MIPS, [P(salida="2", descripcion="imprime 2")], solucion=S35, ), herramienta="Simulador MIPS"),

Ejercicio("ens-36", "Función que devuelve una estructura",
r"""Ahora `struct Datos f1(void)` rellena una estructura local p (a = 9, b = 'c', c = {0,1,2,3}) y la **devuelve**;
f2 hace `x = f1(); k = x.c[3]; print_int(k);`""",
r"""Una estructura de 24 bytes **no cabe en $v0–$v1**. La solución habitual (la que usan los compiladores): quien llama
**reserva el espacio** (x, en su pila) y pasa su dirección como **argumento oculto** en $a0; f1 escribe ahí los campos.
`x.c[3]` está en el desplazamiento $8 + 3\cdot4 = 20$.""" + asm(S36) + "Imprime **3**.",
programa=Programa(MIPS, [P(salida="3", descripcion="imprime 3")], solucion=S36), herramienta="Simulador MIPS"),
], icono="⚙️")
