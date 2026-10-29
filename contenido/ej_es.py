from contenido.base import Ejercicio, Hoja, Respuesta, Prueba, Programa
from contenido.ej_ensamblador import asm
from core import dispositivos as D

R = Respuesta
P = Prueba
MIPS = "mips"


def _imp(*regs):
    """Código que imprime registros separados por espacios."""
    out = []
    for k, r in enumerate(regs):
        if k:
            out += ["        li   $a0, ' '", "        li   $v0, 11", "        syscall"]
        out += [f"        move $a0, {r}", "        li   $v0, 1", "        syscall"]
    return "\n".join(out) + "\n        li   $v0, 10\n        syscall\n"


# ------------------------------------------------------------------ 3. sensor de piezas
S3 = """\
# void LeerMedidas(int *largo):  $a0 = dirección donde dejar el largo
#   → $v0 = alto, $v1 = ancho  (solo hay dos registros de resultado: el tercero se devuelve por memoria)
.text
LeerMedidas:
        li   $t0, 2
        sw   $t0, 0x104          # registro de control ← 2: ¡mide!
espera: lw   $t0, 0x100          # registro de estado
        beqz $t0, espera         # 0 → aún no hay medida (espera activa)
        lw   $v0, 0x108          # alto
        lw   $v1, 0x10C          # ancho
        lw   $t1, 0x110          # largo
        sw   $t1, 0($a0)
        jr   $ra
"""
M3 = """\
.data
_largo: .word 0
.text
main:   la   $a0, _largo
        jal  LeerMedidas
        move $s0, $v0
        move $s1, $v1
        lw   $s2, _largo
""" + _imp("$s0", "$s1", "$s2")

# ------------------------------------------------------------------ 4. sensor de temperatura
S4 = """\
.text
# void InicializarSensor(void)
InicializarSensor:
        li   $t0, 2
        sw   $t0, 0x104          # control ← 2: inicializar
ini:    lw   $t0, 0x100
        li   $t1, 1
        bne  $t0, $t1, ini       # esperar a que el estado valga 1
        jr   $ra

# LeerTemperatura(void) → $v0 = temperatura, $v1 = código (0 bien, −1 error)
LeerTemperatura:
lee:    lw   $t0, 0x100          # estado
        beqz $t0, lee            # 0: aún no hay lectura
        li   $t1, -1
        beq  $t0, $t1, error
        lw   $v0, 0x108          # 1: la temperatura está en el registro de datos
        li   $v1, 0
        jr   $ra
error:  li   $v0, 0
        li   $v1, -1
        jr   $ra
"""
M4 = """\
.text
main:   jal  InicializarSensor
        jal  LeerTemperatura
        move $s0, $v0
        move $s1, $v1
""" + _imp("$s0", "$s1")

# ------------------------------------------------------------------ 5. lector de códigos de barras
S5 = """\
.text
main:   li   $t0, 111
        sw   $t0, 0x1004         # control ← 111: inicializar el lector
bucle:  lw   $t0, 0x1008         # estado
        beqz $t0, bucle          # 0: no hay código nuevo
        lw   $t1, 0x1000         # leer el código
        sw   $t1, 0xA0000000     # guardarlo en memoria
        b    bucle               # para siempre
"""


def _v5(devs, res):
    d = devs[0]
    f = []
    if not d.iniciado:
        f.append("no se ha inicializado el lector (escribir 111 en 0x1004)")
    if d.leidos != [11, 22, 33]:
        f.append(f"se han leído los códigos {d.leidos} y debían ser [11, 22, 33]")
    from core.mips import palabras
    if palabras(res, 0xA0000000, 1)[0] != 33:
        f.append("en 0xA0000000 no está el último código leído (33)")
    return f


# ------------------------------------------------------------------ 6. semáforo (mapa separado)
S6 = """\
.eqv CUENTA  1000
.eqv EMPEZAR 1004
.eqv FIN     1008
.eqv COLOR   1012
.text
main:
ciclo:  li   $a0, 4              # 100 (rojo)
        li   $a1, 90
        jal  fase
        li   $a0, 1              # 001 (verde)
        li   $a1, 90
        jal  fase
        li   $a0, 2              # 010 (ámbar)
        li   $a1, 20
        jal  fase
        b    ciclo               # el semáforo no se para nunca

# fase(color, segundos): enciende un color y espera a que acabe la cuenta atrás
fase:   out  $a0, COLOR
        out  $a1, CUENTA
        li   $t0, 1
        out  $t0, EMPEZAR
espera: in   $t0, FIN
        beqz $t0, espera
        jr   $ra
"""

COLORES = {4: "rojo", 100: "rojo", 2: "ámbar", 10: "ámbar", 1: "verde"}


def _v6(devs, res):
    fases = [(COLORES.get(c, f"¿{c}?"), s) for c, s in devs[0].fases[:4]]
    bueno = [("rojo", 90), ("verde", 90), ("ámbar", 20), ("rojo", 90)]
    if fases != bueno:
        return [f"secuencia de fases {fases}; debía ser {bueno}"]
    return []


# ------------------------------------------------------------------ 8. horno con alarma (mapa separado)
EQV8 = """\
.eqv ST_REG_CONTROL 0x100
.eqv ST_REG_DATOS   0x104
.eqv ST_REG_ESTADO  0x108
.eqv A_REG_CONTROL  0x200
.eqv A_REG_ESTADO   0x204
"""
S8 = EQV8 + """\
.text
main:   li   $t0, 0
        out  $t0, ST_REG_CONTROL     # inicializar el sensor
ini:    in   $t0, ST_REG_ESTADO
        beqz $t0, ini                # ocupado (0) → esperar
bucle:  li   $t0, 1
        out  $t0, ST_REG_CONTROL     # pedir una medida
esp:    in   $t0, ST_REG_ESTADO
        beqz $t0, esp
        in   $t1, ST_REG_DATOS       # temperatura
        li   $t2, 100
        bgt  $t1, $t2, alarma_on
        out  $zero, A_REG_CONTROL    # ≤ 100 → alarma desactivada
        b    bucle
alarma_on:
        li   $t3, 1
        out  $t3, A_REG_CONTROL      # > 100 → alarma activada
        b    bucle
"""


def _v8(devs, res):
    d = devs[0]
    f = []
    if not d.inicializado:
        f.append("no se ha inicializado el sensor (escribir 0 en ST_REG_CONTROL)")
    esperado = [(80, 0), (120, 1), (130, 1), (90, 0), (101, 1), (99, 0)]
    if d.medidas[:6] != esperado:
        f.append(f"(temperatura, alarma) = {d.medidas[:6]}; debía ser {esperado}")
    return f


# ------------------------------------------------------------------ 10. sensor de nivel de agua
EQV10 = """\
.eqv R_CONTROL_Px 0x300
.eqv R_ESTADO_Px  0x304
.eqv R_DATOS_Px   0x308
.eqv ON           1
.eqv OFF          0
.eqv MIDIENDO     0
.eqv NUEVO        1
.eqv ERROR        2
.eqv M_CODIGO     0x10010000
.eqv M_ALMACEN    0x10010100
.eqv PROBLEMAS    -1
.eqv TODO_OK      1
"""
S10 = EQV10 + """\
.text
main:   li   $t0, ON
        out  $t0, R_CONTROL_Px       # 1. activar el sensor
        li   $t1, 0                  # medidas guardadas
        li   $t2, M_ALMACEN          # siguiente posición libre
        li   $t5, NUEVO
        li   $t6, ERROR
bucle:  beq  $t1, 100, todo_ok       # ¿ya hay 100?
espera: in   $t0, R_ESTADO_Px
        beq  $t0, $t6, problemas     # 3. error → abandonar
        bne  $t0, $t5, espera        # MIDIENDO → seguir esperando
        in   $t3, R_DATOS_Px         # 2. NUEVO → leer…
        sw   $t3, 0($t2)             #    …y guardar
        addi $t2, $t2, 4
        addi $t1, $t1, 1
        b    bucle
todo_ok: li  $t0, TODO_OK            # 4. completadas
        sw   $t0, M_CODIGO
        b    fin
problemas: li $t0, PROBLEMAS
        sw   $t0, M_CODIGO
fin:    li   $t0, OFF
        out  $t0, R_CONTROL_Px       # (buena costumbre: desactivarlo)
        li   $v0, 10
        syscall
"""

# ------------------------------------------------------------------ 11. microondas
S11 = """\
# int Controlador_Horno(int segundos, int potencia):  $a0 = segundos, $a1 = potencia → $v0
.text
Controlador_Horno:
        li   $v0, -1
        blt  $a1, 100, fin_h         # potencia fuera de [100, 1000] → −1 sin tocar el horno
        bgt  $a1, 1000, fin_h
        sw   $a0, 1000($zero)        # segundos de la cuenta atrás
        sw   $a1, 1012($zero)        # potencia
        li   $t0, 1
        sw   $t0, 1016($zero)        # encender
        sw   $t0, 1004($zero)        # empezar la cuenta atrás
esp_h:  lw   $t0, 1008($zero)
        beqz $t0, esp_h              # esperar a que llegue a 0
        sw   $zero, 1016($zero)      # apagar
        li   $v0, 0
fin_h:  jr   $ra
"""
M11_MAIN = """\
.text
main:   li   $a0, 90                 # segundos
        li   $a1, 800                # potencia
        jal  Controlador_Horno
        move $a0, $v0                # imprimir el resultado
        li   $v0, 1
        syscall
        li   $v0, 10
        syscall
"""


def _m11(seg, pot):
    return M11_MAIN.replace("90 ", f"{seg} ").replace("800 ", f"{pot} ")


def _v11(seg, pot, valido):
    def v(devs, res):
        d = devs[0]
        if not valido:
            return [] if not any(t == "W" for t, _, _ in d.log) else ["con una potencia no válida no se debe tocar el horno"]
        f = []
        if d.segundos != seg:
            f.append(f"en el registro 1000 hay {d.segundos} s y debían ser {seg}")
        if d.potencia != pot:
            f.append(f"en el registro 1012 hay potencia {d.potencia} y debía ser {pot}")
        if 1 not in d.escrituras(1016):
            f.append("el horno no se ha encendido (1 en 1016)")
        if d.encendido != 0 or not d.apagado_tras_fin:
            f.append("el horno no se ha apagado al acabar la cuenta atrás (0 en 1016)")
        return f
    return v


# ------------------------------------------------------------------ 12. tensiómetro
S12 = """\
# Controlador_tension(void) → $v0 = sistólica, $v1 = diastólica
.text
Controlador_tension:
        li   $t0, 1
        sw   $t0, 1000($zero)        # empezar la medida
esp_t:  lw   $t0, 1004($zero)
        beqz $t0, esp_t              # 0: midiendo
        lw   $v0, 1008($zero)        # sistólica
        lw   $v1, 1012($zero)        # diastólica
        jr   $ra
"""
M12 = """\
.text
main:   jal  Controlador_tension
        move $s0, $v0
        move $s1, $v1
""" + _imp("$s0", "$s1")


HOJA = Hoja("es", "Sistemas de entrada/salida", "fc", "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "Discos, E/S programada con mapa común (lw/sw) y separado (in/out), periféricos simulados y sobrecarga.", [

Ejercicio("es-1", "Leer un fichero: secuencial o aleatorio",
r"""Disco con búsqueda media de 4 ms, 15 000 rpm, sectores de 512 bytes y 500 sectores por pista. Se lee un fichero de
2500 sectores (1,22 MB). Estime el tiempo: 1) almacenado de forma secuencial (5 pistas consecutivas); 2) con los sectores
distribuidos aleatoriamente.""",
r"""**Datos derivados:**
- Una vuelta: $\dfrac{60}{15\,000}$ s = **4 ms** → latencia rotacional media (media vuelta) = **2 ms**.
- Leer un sector: $4\text{ ms}/500 =$ **0,008 ms**; leer una pista entera: 4 ms.

**1) Secuencial:** primera pista: búsqueda + latencia + leer la pista $= 4 + 2 + 4 = 10$ ms. Las otras 4 pistas son
contiguas (sin búsqueda) pero cada una tiene su latencia: $4\cdot(2 + 4) = 24$ ms.
$$T = 10 + 24 = \mathbf{34\ ms}$$

**2) Aleatorio:** cada sector paga búsqueda + latencia + transferencia:
$$T = 2500\cdot(4 + 2 + 0{,}008) = 2500\cdot6{,}008 = \mathbf{15\,020\ ms \approx 15\ s}$$
¡Unas 440 veces más lento! Por eso los sistemas de ficheros intentan guardar los ficheros contiguos.""",
respuestas=[R("1) ms", 34), R("2) ms", 15020)], herramienta="Discos"),

Ejercicio("es-2", "Tiempo medio de acceso a un sector",
r"""Disco con 600 sectores por pista, 7200 rpm y búsqueda media de 2 ms. Tiempo medio de acceso a un sector.""",
r"""- Vuelta: $60/7200$ s = 8,333 ms → latencia media = **4,167 ms**.
- Transferencia de un sector: $8{,}333/600 =$ **0,0139 ms**.
$$T = 2 + 4{,}167 + 0{,}014 \approx \mathbf{6{,}18\ ms}$$""",
respuestas=[R("ms", 2 + 30000 / 7200 + 60000 / 7200 / 600, tolerancia=2e-3)], herramienta="Discos"),

Ejercicio("es-3", "LeerMedidas: un sensor de piezas con mapa común",
r"""MIPS32 con **mapa de E/S común**. Sensor con registros de 32 bits: datos 1 (0x108, alto), datos 2 (0x112, ancho),
datos 3 (0x116, largo), control (0x104: escribir 0x2 pide una medida) y estado (0x100: 0 sin medida, 1 medida disponible).
Escriba **LeerMedidas**, que devuelve el alto, el ancho y el largo, siguiendo estrictamente el convenio de paso de parámetros.

*En la app:* el sensor simulado usa las direcciones 0x108, **0x10C** y **0x110** (ver la errata). La función recibe en $a0
la dirección donde dejar el largo.""",
r"""**Mapa común** = los registros del periférico se leen y escriben como si fueran memoria, con `lw`/`sw`.
**E/S programada con espera activa**: pedir la medida y preguntar el estado una y otra vez hasta que valga 1.

**El problema de los tres resultados:** el convenio solo tiene **dos** registros de resultado ($v0 y $v1). El tercero se
devuelve **por memoria**: quien llama pasa en $a0 la dirección donde quiere el largo (como un puntero en C:
`int LeerMedidas(int *ancho, int *largo)`… aquí usamos $v0, $v1 y uno por memoria).""" + asm(S3),
errata="0x112 y 0x116 no son múltiplos de 4: un lw a esas direcciones daría error de alineación en MIPS. "
       "Los registros de 32 bits que siguen a 0x108 son 0x10C y 0x110.",
programa=Programa(MIPS, [P(salida="10 20 30", main=M3, dispositivos=lambda: [D.SensorPiezas(10, 20, 30)],
                           descripcion="alto 10, ancho 20, largo 30"),
                         P(salida="7 1 250", main=M3, dispositivos=lambda: [D.SensorPiezas(7, 1, 250, espera=6)],
                           descripcion="otra pieza, sensor más lento")], solucion=S3,
                  plantilla="LeerMedidas:\n        # $a0 = dirección para el largo → $v0 = alto, $v1 = ancho\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-4", "InicializarSensor y LeerTemperatura",
r"""MIPS32 con mapa común. Sensor: datos (0x108, temperatura), control (0x104: 0x2 inicializa; inicializado cuando el
estado vale 1) y estado (0x100: 0 sin lectura, 1 lectura disponible, −1 error). Escriba **InicializarSensor** (sin
argumentos ni resultado; vuelve cuando el sensor está inicializado) y **LeerTemperatura** (devuelve el valor y un código:
0 si bien, −1 si error).""",
r"""Dos resultados → **$v0** (temperatura) y **$v1** (código). Ninguna función llama a otras: son hoja, sin pila.""" + asm(S4) +
"La app prueba con 25 °C (debe imprimir `25 0`) y con un sensor averiado (`0 -1`; el valor da igual).",
errata="En el enunciado la función se llama «InicialiarSensor» (falta una «z»); aquí se usa InicializarSensor.",
programa=Programa(MIPS, [P(salida="25 0", main=M4, dispositivos=lambda: [D.SensorTemperatura(25)], descripcion="25 °C"),
                         P(salida="-1", main=M4, dispositivos=lambda: [D.SensorTemperatura(25, error=True)],
                           descripcion="sensor con error → código −1")], solucion=S4,
                  plantilla="InicializarSensor:\n        jr   $ra\n\nLeerTemperatura:\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-5", "Lector de códigos de barras",
r"""Controlador con: datos (0x1000, código leído), control (0x1004: escribir 111 lo inicializa) y estado (0x1008: 0 sin
lectura, 1 hay código). Con mapa común y MIPS32, programe: inicializar el lector y, indefinidamente, leer códigos;
cada código nuevo se guarda en la posición **0xA0000000**.""",
r"""Un bucle infinito de E/S programada: preguntar el estado; si hay código, leerlo y guardarlo.""" + asm(S5) + r"""
*En la app:* el programa no termina nunca (es lo que se pide), así que se para tras unas miles de instrucciones y se
comprueba que leyó los códigos 11, 22 y 33 en orden y que en 0xA0000000 quedó el último.""",
programa=Programa(MIPS, [P(dispositivos=lambda: [D.LectorBarras()], verificar=_v5, infinito=True, max_pasos=4000,
                           descripcion="códigos 11, 22, 33")], solucion=S5),
herramienta="Simulador MIPS"),

Ejercicio("es-6", "Controlador de un semáforo (mapa separado)",
r"""CPU MIPS32 con **mapa de E/S separado** (instrucciones `in`/`out`). Cronómetro: registro 1000 = segundos de cuenta
atrás; 1004 = escribir 1 para empezar; 1008 = vale 1 cuando la cuenta llega a 0 (0 mientras cuenta). Semáforo: registro
1012 = color (100 rojo, 010 amarillo, 001 verde). Empieza en rojo; rojo y verde duran 90 s y amarillo 20 s.""",
r"""Como cada fase hace lo mismo (poner color, programar los segundos, arrancar y esperar), se escribe una **función**
`fase(color, segundos)` y el programa la llama en bucle: rojo → verde → ámbar → rojo…
Los colores son patrones de bits: 100₂ = 4, 010₂ = 2, 001₂ = 1 (la app también acepta 100, 10 y 1 en decimal).""" + asm(S6),
programa=Programa(MIPS, [P(dispositivos=lambda: [D.Semaforo()], verificar=_v6, infinito=True, max_pasos=3000,
                           descripcion="rojo 90 → verde 90 → ámbar 20 → rojo 90")], solucion=S6,
                  plantilla=".eqv CUENTA  1000\n.eqv EMPEZAR 1004\n.eqv FIN     1008\n.eqv COLOR   1012\n.text\nmain:\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-7", "Sobrecarga de consultar el ratón",
r"""Un ratón debe consultarse al menos 30 veces por segundo. La rutina tarda 2000 ciclos y el procesador va a 2,7 GHz.
¿Qué porcentaje del tiempo dedica a esa rutina?""",
r"""Ciclos por segundo dedicados: $30\cdot2000 = 60\,000$. Ciclos disponibles: $2{,}7\cdot10^9$.
$$\text{sobrecarga} = \frac{60\,000}{2{,}7\cdot10^9} = 2{,}22\cdot10^{-5} = \mathbf{0{,}00222\ \%}$$
Despreciable: el ratón es un dispositivo muy lento comparado con la CPU.""",
respuestas=[R("Sobrecarga (%)", 60000 / 2.7e9 * 100, tolerancia=2e-3)]),

Ejercicio("es-8", "Horno con sensor de temperatura y alarma",
r"""Sensor de temperatura con ST_REG_CONTROL (0 inicializa, 1 pide una lectura), ST_REG_DATOS (temperatura) y
ST_REG_ESTADO (1 listo, 0 ocupado). Alarma con A_REG_CONTROL (1 activa, 0 desactiva) y A_REG_ESTADO. Mapa separado con
`in`/`out`. Programa que lea continuamente la temperatura: por encima de 100 °C, alarma activada; por debajo, desactivada.

*En la app:* las direcciones simbólicas se definen con `.eqv` (como en MARS): usa la plantilla.""",
r"""1. Inicializar el sensor y esperar a que esté listo.
2. Bucle infinito: pedir una lectura, esperar «listo», leer el dato y escribir 1 o 0 en la alarma.""" + asm(S8) + r"""
El simulador entrega 80, 120, 130, 90, 101 y 99 °C y comprueba el estado de la alarma tras cada una.""",
programa=Programa(MIPS, [P(dispositivos=lambda: [D.HornoAlarma()], verificar=_v8, infinito=True, max_pasos=3000,
                           descripcion="80, 120, 130, 90, 101, 99 °C")], solucion=S8, plantilla=EQV8 + ".text\nmain:\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-9", "Disco el doble de rápido y CPU un 50 % más rápida",
r"""Un programa tarda 1 hora: 20 % acceso a disco y 80 % procesamiento. Con un disco que tarda la mitad, ¿qué fracción se
dedica al disco? Y si además el procesador es un 50 % más rápido?""",
r"""Minutos: disco 12, CPU 48.
- **Disco nuevo:** disco 6 min, total 54 → $6/54 =$ **11,1 %**.
- **Además CPU 1,5 veces más rápida:** CPU $48/1{,}5 = 32$ min, total 38 → $6/38 =$ **15,8 %**.

Al acelerar la CPU, el disco vuelve a pesar más: es la ley de Amdahl en acción (lo que no mejoras acaba mandando).""",
respuestas=[R("Fracción de disco (%) con disco nuevo", 600 / 54, tolerancia=1e-3),
            R("… y con CPU más rápida (%)", 600 / 38, tolerancia=1e-3)], herramienta="Rendimiento"),

Ejercicio("es-10", "Driver de un sensor de nivel de agua",
r"""Mapa separado con `in rdest, dirección` y `out rsrc, dirección`. Sensor Px con R_CONTROL_Px, R_ESTADO_Px y R_DATOS_Px
(32 bits). Comandos ON y OFF. Estado: MIDIENDO, NUEVO o ERROR (al leer el dato pasa de NUEVO a MIDIENDO).
a) Driver por E/S programada: activar el sensor; guardar cada medida nueva en la siguiente posición desde M_ALMACEN hasta
completar 100; si hay un error, parar y escribir PROBLEMAS en M_CODIGO; si se completan, escribir TODO_OK en M_CODIGO.
b) Inconvenientes de la E/S programada y cómo se haría por interrupciones.""",
r"""**a)** Los nombres simbólicos se declaran con `.eqv` (sus valores dan igual; la plantilla trae unos).""" + asm(S10) + r"""
**b)** Con **E/S programada** la CPU se pasa todo el tiempo en el bucle de espera preguntando el estado (**espera activa**):
el nivel del agua cambia muy de vez en cuando, así que casi todos los ciclos se desperdician y no puede hacer otra cosa.

Con **E/S por interrupciones**, el sensor activa una interrupción cuando hay una medida NUEVA o un ERROR. La rutina de
tratamiento lee el dato, lo guarda en M_ALMACEN + 4·k, incrementa k y, si k = 100 (o hay error), escribe el código y
desactiva el sensor. Mientras tanto la CPU ejecuta otros programas: **solo trabaja cuando hay algo que hacer**.""",
errata="En la tabla de registros pone «32 its»: son 32 bits.",
programa=Programa(MIPS, [P(dispositivos=lambda: [D.SensorAgua(100)], descripcion="100 medidas sin errores",
                           memoria={0x10010000: [1], 0x10010100: [1000 + 7 * k for k in range(100)]}),
                         P(dispositivos=lambda: [D.SensorAgua(100, error_en=5)], descripcion="error tras 5 medidas",
                           memoria={0x10010000: [-1], 0x10010100: [1000 + 7 * k for k in range(5)]})],
                  solucion=S10, plantilla=EQV10 + ".text\nmain:\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-11", "Controlador de un microondas",
r"""Mapa común. Registros: 1000 = segundos de cuenta atrás; 1004 = 1 inicia la cuenta; 1008 = vale 1 al llegar a 0;
1012 = potencia (Ca2); 1016 = 1 enciende con esa potencia, 0 apaga. Función **Controlador_Horno(segundos, potencia)**:
programa el horno, lo enciende y lo apaga al acabar; devuelve 0, o −1 si la potencia es menor de 100 o mayor de 1000 (en
ese caso no toca el horno). a) Registros de parámetros y resultado. b) Llamada con 800 W y 90 s, imprimiendo el resultado.
c) Código de la función.""",
r"""**a)** $a0 = segundos, $a1 = potencia; resultado en **$v0**.

**b)**""" + asm(M11_MAIN) + "**c)**" + asm(S11) + r"""
En mapa común se accede a una dirección absoluta pequeña con `sw $t0, 1000($zero)` (registro base = $zero).""",
errata="Pone «menor de 100 y mayor de 1000», que es imposible a la vez: es «menor de 100 o mayor de 1000».",
programa=Programa(MIPS, [P(salida="0", main=_m11(90, 800), dispositivos=lambda: [D.Microondas()],
                           verificar=_v11(90, 800, True), descripcion="90 s a 800 W"),
                         P(salida="-1", main=_m11(30, 50), dispositivos=lambda: [D.Microondas()],
                           verificar=_v11(30, 50, False), descripcion="potencia 50 → −1"),
                         P(salida="-1", main=_m11(30, 1500), dispositivos=lambda: [D.Microondas()],
                           verificar=_v11(30, 1500, False), descripcion="potencia 1500 → −1"),
                         P(salida="0", main=_m11(5, 1000), dispositivos=lambda: [D.Microondas()],
                           verificar=_v11(5, 1000, True), descripcion="límite: 1000 W")], solucion=S11,
                  plantilla="Controlador_Horno:\n        # $a0 = segundos, $a1 = potencia → $v0\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-12", "Controlador de un tensiómetro",
r"""Mapa común. Registros: 1000 = escribir 1 empieza la medida; 1004 = 1 cuando termina (0 mientras mide);
1008 = sistólica; 1012 = diastólica. Función **Controlador_tension** sin parámetros que devuelva las dos tensiones.""",
r"""Dos resultados → **$v0** (sistólica) y **$v1** (diastólica).""" + asm(S12),
programa=Programa(MIPS, [P(salida="120 80", main=M12, dispositivos=lambda: [D.Tensiometro(120, 80)], descripcion="120/80"),
                         P(salida="135 92", main=M12, dispositivos=lambda: [D.Tensiometro(135, 92, espera=8)],
                           descripcion="135/92, medida lenta")], solucion=S12,
                  plantilla="Controlador_tension:\n        # → $v0 = sistólica, $v1 = diastólica\n\n        jr   $ra\n"),
herramienta="Simulador MIPS"),

Ejercicio("es-13", "Elegir disco para un servidor de películas",
r"""| | Disco A | Disco B |
|---|---|---|
| Platos | 16 | 32 |
| Superficies por plato | 2 | 2 |
| Pistas por superficie | 512 000 | 256 000 |
| Sectores por pista | 64 | 64 |
| Bytes por sector | 512 | 512 |
| rpm | 5400 | 7200 |
| Búsqueda media | 1 ms | 3 ms |
| Coste | 0,01 €/MB | 0,02 €/MB |

a) Capacidad en MB de cada disco. b) Disco A: tiempo medio para leer una película de 4096 MB guardada de forma secuencial.
c) ¿Cuál es más económico? d) Disco A leyendo la película sector a sector de forma aleatoria.""",
r"""**a)** Capacidad = platos × superficies × pistas × sectores × bytes:
- A: $16\cdot2\cdot512\,000\cdot64\cdot512 = 536\,870\,912\,000$ B = **512 000 MB**
- B: $32\cdot2\cdot256\,000\cdot64\cdot512$ = lo mismo = **512 000 MB** (dividiendo entre $2^{20}$).

**b)** Disco A: una vuelta = $60/5400$ s = 11,11 ms (latencia media 5,56 ms). Una pista = $64\cdot512$ = 32 KB.
Película: $4096\text{ MB}/32\text{ KB} = 131\,072$ pistas. Secuencial (una búsqueda y una latencia, y luego leer seguido):
$$T = 1 + 5{,}56 + 131\,072\cdot11{,}11\text{ ms} \approx 1\,456\,362\text{ ms} \approx \mathbf{1456\ s\ (24{,}3\ min)}.$$

**c)** A: $512\,000\cdot0{,}01 =$ **5120 €**; B: $512\,000\cdot0{,}02 =$ 10 240 € → **A** es más económico (misma capacidad, la mitad de precio).

**d)** Sectores: $4096\text{ MB}/512\text{ B} = 8\,388\,608$. Cada uno: búsqueda + latencia + transferencia
$= 1 + 5{,}556 + 11{,}11/64 = 6{,}729$ ms →
$$T = 8\,388\,608\cdot6{,}729\text{ ms} \approx 56\,448\text{ s} \approx \mathbf{15{,}7\ horas}.$$""",
respuestas=[R("a) MB de A", 512000), R("a) MB de B", 512000), R("b) segundos", 1456.362, tolerancia=2e-3),
            R("c) Más económico", ["a", "disco a"], "texto"), R("d) horas", 15.68, tolerancia=3e-3)], herramienta="Discos"),
], icono="🔌")
