from contenido.base import Ejercicio, Hoja, Respuesta

PROG_EJ3 = """\
Dir. | Binario            | Significado
-----|--------------------|------------------------------------------
  0  | 001 00 00000000000 | R0 ← 0            (suma = 0)
  1  | 001 01 00000000010 | R1 ← 2            (incremento)
  2  | 001 10 00000000010 | R2 ← 2            (par actual)
  3  | 001 11 00000010110 | R3 ← 22           (límite: el primer par que ya NO se suma)
  4  | 101 10 11 000001000 | si R2 == R3 salta a 8 (fin)
  5  | 000 00 00 10 0000000 | R0 ← R0 + R2     (suma += par)
  6  | 000 10 10 01 0000000 | R2 ← R2 + R1     (siguiente par)
  7  | 100 0000000000100  | salta a 4         (repetir)
  8  | 011 00 00001100100 | MEM[100] ← R0     (guardar el resultado)
  9  | 100 0000000001001  | salta a 9         (se queda aquí: fin)"""

HOJA = Hoja("intro", "Introducción a los computadores", "fc", "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "Ancho de palabra, registros, direcciones, bases y un programa en un computador inventado.", [

Ejercicio("intro-1", "Computador de 20 bits con 60 registros",
r"""Considere un hipotético computador de 20 bits (ancho de palabra = 20 bits) con 60 registros que direcciona la memoria
por bytes. a) ¿Cuántos bits se emplean para las direcciones de memoria? b) ¿Cuál es el tamaño de los registros?
c) ¿Cuántos bits se almacenan en cada posición de memoria? d) ¿Cuántas posiciones de memoria se pueden direccionar?
Exprese el resultado en KB. e) ¿Cuántos bits se necesitan para identificar a los registros?""",
r"""**a) 20 bits.** En un computador de *n* bits, palabra, registros, bus de datos y direcciones tienen *n* bits (es lo que
se supone salvo que digan otra cosa).

**b) 20 bits.** Un registro guarda una palabra.

**c) 8 bits.** «Direcciona por bytes» significa que cada dirección corresponde a una posición de 1 byte.

**d)** Con 20 bits de dirección hay $2^{20}$ direcciones distintas → $2^{20}$ posiciones de 1 byte
$= 2^{20}$ B $= 2^{10}$ KB $=$ **1024 KB** (= 1 MB).

**e) 6 bits.** Hay que dar un número distinto a cada uno de los 60 registros: $2^5 = 32 < 60 \le 64 = 2^6$ →
$\lceil\log_2 60\rceil = 6$.""",
pista="Pregunta clave: ¿qué cosa mide lo mismo que la palabra? Para los registros, busca la menor potencia de 2 ≥ 60.",
respuestas=[Respuesta("a) bits de dirección", 20), Respuesta("b) bits por registro", 20),
            Respuesta("c) bits por posición", 8), Respuesta("d) KB direccionables", 1024), Respuesta("e) bits para el nº de registro", 6)],
herramienta="Bases y potencias"),

Ejercicio("intro-2", "Hexadecimal a binario",
r"""Convierta a binario el siguiente número hexadecimal: **EAAB591**.""",
r"""Cada cifra hexadecimal son exactamente **4 bits** ($16 = 2^4$), así que se traduce cifra a cifra:

| E | A | A | B | 5 | 9 | 1 |
|---|---|---|---|---|---|---|
| 1110 | 1010 | 1010 | 1011 | 0101 | 1001 | 0001 |

$\text{EAAB591}_{16} = \mathbf{1110\,1010\,1010\,1011\,0101\,1001\,0001}_2$ (28 bits; en decimal, 246 068 625).""",
pista="Tabla de 0–F en 4 bits: A=1010, B=1011, E=1110…",
respuestas=[Respuesta("binario", "1110101010101011010110010001", "bin")], herramienta="Bases y potencias"),

Ejercicio("intro-3", "Programa en un computador inventado: suma de los 10 primeros pares",
r"""Computador hipotético: posición de memoria de 16 bits, instrucciones de 16 bits, código de operación de 3 bits y
4 registros (R0 = 00, R1 = 01, R2 = 10, R3 = 11). Instrucciones:

| Instrucción | Descripción |
|---|---|
| `000 01 00 10 XXXXXXX` | Suma el registro 00 con el 10 y deja el resultado en 01 |
| `001 01 00000000101` | Almacena en el registro 01 el valor 00000000101 |
| `010 01 00000001001` | Almacena en el registro 01 el valor de la posición de memoria 00000001001 |
| `011 01 00000001001` | Almacena en la posición de memoria 00000001001 el contenido del registro 01 |
| `100 0000000001001` | Salta a la instrucción de la posición 0000000001001 |
| `101 01 00 000001001` | Si el registro 01 es igual al 00, salta a la instrucción de la posición 000001001 |

Escriba un programa que calcule la suma de los 10 primeros números pares: 2 + 4 + 6 + … + 20.""",
r"""**1. Deducir los formatos** (mirando los ejemplos):

| Cód. | Instrucción | Campos |
|---|---|---|
| 000 | suma | op(3) · Rdestino(2) · Rfuente1(2) · Rfuente2(2) · relleno(7) |
| 001 | cargar inmediato | op(3) · R(2) · valor(11) |
| 010 | cargar de memoria | op(3) · R(2) · dirección(11) |
| 011 | guardar en memoria | op(3) · R(2) · dirección(11) |
| 100 | salto | op(3) · dirección(13) |
| 101 | salto si iguales | op(3) · R1(2) · R2(2) · dirección(9) |

**2. Algoritmo** (con solo 4 registros): suma = 0; incremento = 2; par = 2; límite = 22.
Mientras par ≠ límite: suma += par; par += incremento. Al salir, guardamos la suma en memoria.
(No hay «menor que», solo «igual»: por eso se compara con 22, el primer par que ya no se suma.)

**3. Programa** (una instrucción por posición de memoria, empezando en la 0):
```
""" + PROG_EJ3 + r"""
```
Al terminar, **R0 = 110 = 2 + 4 + … + 20** (comprobado simulando la máquina instrucción a instrucción) y se guarda en
la posición 100. Como no hay instrucción de parar, se acaba con un salto a sí misma.""",
pista="Primero deduce qué significa cada campo mirando los ejemplos. Solo hay «saltar si son iguales»: ¿con qué número comparas?",
respuestas=[Respuesta("resultado de la suma", 110)], herramienta="Simulador MIPS"),
], icono="🖥️")


HOJA_ARCOS = Hoja("arcos-fund", "Fundamentos: rendimiento, potencia y fiabilidad", "fc",
                  "Arquitectura de Computadores · Ejercicios de Fundamentos (J. D. García et al., ARCOS-UC3M)",
                  "Ley de Amdahl, CPI y frecuencia, potencia dinámica, fiabilidad y disponibilidad.", [

Ejercicio("af-1", "Speedup de 10 con Amdahl", r"""Una aplicación procesa una imagen de muy alta resolución: una fracción es
paralelizable y otra debe ejecutarse secuencialmente. No hay límite al número de procesos. Se desea un **speedup global
de 10**. Exprese la fracción de código que debe ser paralelizable en función del grado de paralelismo *p*.""",
r"""**Ley de Amdahl** con una fracción $f$ que se acelera $p$ veces (los $p$ procesos) y $1-f$ que no:
$$S=\frac{1}{(1-f)+\dfrac fp}.$$
Imponemos $S = 10$:
$$\frac1{10}=1-f+\frac fp\;\Rightarrow\;f\left(1-\frac1p\right)=\frac9{10}\;\Rightarrow\;\boxed{f=\frac{0{,}9\,p}{p-1}}.$$

**Interpretación:** como $f\le1$, hace falta $0{,}9p\le p-1$, es decir **$p\ge10$**. Con $p = 10$ habría que paralelizar
el 100 %; con $p = 20$, $f = 18/19 \approx 94{,}7\%$; y cuando $p\to\infty$, $f\to0{,}9$: **como mínimo el 90 % del código
tiene que ser paralelizable** (el 10 % secuencial limita el speedup a 10 por muchos procesadores que haya).""",
pista="Plantea Amdahl con S = 10 y despeja f.", origen="Examen de junio de 2015",
respuestas=[Respuesta("f con p = 20 (en tanto por uno)", 18 / 19, tolerancia=1e-3)], herramienta="Rendimiento"),

Ejercicio("af-2", "Migrar una aplicación financiera: alternativas A y B", r"""Un computador de un solo núcleo ejecuta una aplicación
que dedica el **90 %** del tiempo a cálculo y el **10 %** a esperar E/S de disco. Del tiempo de cálculo, el **75 %** son
operaciones en coma flotante (12 CPI de media) y el **25 %** otras instrucciones (4 CPI). Las alternativas no mejoran la E/S:

- **A**: un núcleo, reloj un 50 % más alto, las de coma flotante necesitan un 10 % más de ciclos y el resto un 25 % más.
- **B**: cuatro núcleos, reloj un 50 % más bajo, las de coma flotante necesitan un 20 % menos de ciclos y el resto los mismos.

1. Aceleración global en el caso A. 2. Aceleración global en el caso B si el cálculo es totalmente paralelizable y la E/S no.""",
r"""Tomamos el tiempo original como 1 y lo repartimos (los porcentajes ya son **de tiempo**, así que los CPI 12 y 4 no hacen falta):

| Parte | Tiempo original |
|---|---|
| Coma flotante | $0{,}9\cdot0{,}75 = 0{,}675$ |
| Otras instrucciones | $0{,}9\cdot0{,}25 = 0{,}225$ |
| E/S | $0{,}1$ |

Para la parte de CPU, $T = \dfrac{N\cdot CPI}{f}$: cambiar el CPI multiplica el tiempo y cambiar la frecuencia lo divide.

**1) Alternativa A** ($f\times1{,}5$):
- Coma flotante: $0{,}675\cdot\dfrac{1{,}10}{1{,}5}=0{,}495$
- Otras: $0{,}225\cdot\dfrac{1{,}25}{1{,}5}=0{,}1875$
- E/S: $0{,}1$ → total $0{,}7825$.

$$S_A=\frac1{0{,}7825}\approx\mathbf{1{,}28}\ \text{(acelera un 28 %)}.$$

**2) Alternativa B** ($f\times0{,}5$, 4 núcleos):
- Coma flotante en un núcleo: $0{,}675\cdot\dfrac{0{,}8}{0{,}5}=1{,}08$; otras: $0{,}225\cdot\dfrac1{0{,}5}=0{,}45$
- Cálculo repartido entre 4 núcleos: $(1{,}08+0{,}45)/4=0{,}3825$
- E/S: $0{,}1$ → total $0{,}4825$.

$$S_B=\frac1{0{,}4825}\approx\mathbf{2{,}07}.$$
La B es mejor pese a tener un reloj más lento, porque reparte el 90 % del trabajo entre 4 núcleos.""",
pista="Normaliza el tiempo original a 1 y trocéalo. Tiempo de CPU ∝ CPI / frecuencia.", origen="Examen de enero de 2014",
respuestas=[Respuesta("Speedup A", 1 / 0.7825, tolerancia=2e-3), Respuesta("Speedup B", 1 / 0.4825, tolerancia=2e-3)],
herramienta="Rendimiento"),

Ejercicio("af-3", "Nueva máquina: +25 % de CPI y el doble de frecuencia", r"""Una aplicación pasa el **80 %** del tiempo ejecutando
instrucciones y el **20 %** esperando al disco. Del tiempo de ejecución, el 20 % es en coma flotante (8 CPI) y el 80 % el
resto (6 CPI). La nueva máquina necesita un **25 % más de CPI** en todas las instrucciones, pero su **frecuencia es el doble**.
¿Cuál será la aceleración global?""",
r"""Todas las instrucciones empeoran igual (×1,25 de CPI), así que el reparto entre coma flotante y resto no influye.

- Parte de CPU: $0{,}8\cdot\dfrac{1{,}25}{2}=0{,}5$
- Disco (no cambia): $0{,}2$

$$T_{nuevo}=0{,}7\quad\Rightarrow\quad S=\frac1{0{,}7}\approx\mathbf{1{,}43}.$$""",
pista="Si todos los CPI suben lo mismo, el reparto 20/80 da igual.", origen="Examen de octubre de 2013",
respuestas=[Respuesta("Aceleración", 1 / 0.7, tolerancia=2e-3)], herramienta="Rendimiento"),

Ejercicio("af-4", "Reducir la potencia dinámica", r"""Un procesador consume una potencia dinámica *P*. Dos alternativas:
1) bajar el voltaje a la mitad manteniendo la frecuencia; 2) bajar la frecuencia a la mitad manteniendo el voltaje.
Razone cuál reduce más la potencia y cuantifique la reducción.""",
r"""La potencia dinámica es $P = \alpha\,C\,V^2 f$ (o $\tfrac12 C V^2 f$; la constante da igual).

1. **Voltaje a la mitad:** $P' = C\left(\tfrac V2\right)^2 f = \tfrac14\,CV^2f = \mathbf{0{,}25\,P}$ → se reduce un **75 %**.
2. **Frecuencia a la mitad:** $P' = CV^2\tfrac f2 = \mathbf{0{,}5\,P}$ → se reduce un **50 %**.

Gana **bajar el voltaje**, porque la potencia depende del **cuadrado** del voltaje y solo linealmente de la frecuencia.
(Además, bajar la frecuencia hace que el programa tarde el doble: la energía total apenas cambia.)""",
pista="P ∝ C·V²·f", origen="Examen de octubre de 2013",
respuestas=[Respuesta("Reducción (%) bajando el voltaje", 75), Respuesta("Reducción (%) bajando la frecuencia", 50)]),

Ejercicio("af-5", "Fiabilidad y disponibilidad", r"""Un computador funciona de forma continuada y sin errores hasta t = 20 meses.
1. Defina la **fiabilidad**. ¿Cuál es para t = 0, t = 24 y t = 30 meses?
2. Defina la **disponibilidad**. Si durante los dos años de uso tiene dos averías con tiempos de reparación de 3,85 y
4,15 días, ¿cuál es su disponibilidad?""",
r"""**1. Fiabilidad** $R(t)$: probabilidad de que el sistema funcione **sin fallos desde 0 hasta t** (mide el tiempo hasta el
primer fallo). Este equipo funciona seguro hasta los 20 meses y entonces falla, así que:
$R(0)=\mathbf 1$ · $R(24)=\mathbf 0$ · $R(30)=\mathbf 0$ (a los 24 y a los 30 meses ya ha fallado).

**2. Disponibilidad:** fracción del tiempo en que el sistema **está funcionando** (dando servicio):
$$A=\frac{\text{tiempo funcionando}}{\text{tiempo total}}=\frac{MTTF}{MTTF+MTTR}.$$
Dos años = 730 días; reparaciones: $3{,}85+4{,}15=8$ días →
$$A=\frac{730-8}{730}=\frac{722}{730}\approx\mathbf{98{,}9\,\%}.$$
(Con la otra fórmula: MTTR = 4 días, MTTF = 722/2 = 361 días → 361/365 = 98,9 %.)

💡 Fiabilidad y disponibilidad no son lo mismo: un sistema puede fallar a menudo pero repararse en segundos (poco fiable y
muy disponible).""",
pista="Fiabilidad: ¿llega vivo hasta t sin fallar? Disponibilidad: ¿qué fracción del tiempo está en marcha?",
origen="Examen de enero de 2013",
respuestas=[Respuesta("R(0)", 1), Respuesta("R(24)", 0), Respuesta("Disponibilidad (%)", 722 / 730 * 100, tolerancia=1e-3)]),
], icono="⚡")
