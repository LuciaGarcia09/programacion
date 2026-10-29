from contenido.base import Ejercicio, Hoja, Respuesta

R = Respuesta

HOJA = Hoja("repr", "Representación de la información", "fc", "Estructura de Computadores (F. García Carballeira et al., UC3M)",
            "Complemento a 2 y a 1, signo-magnitud, IEEE 754 (32 y 16 bits), sumas y productos en coma flotante.", [

Ejercicio("repr-1", "Rango en Ca2 → tamaño de registro y memoria",
r"""Un computador dispone de un ancho de palabra que le permite representar números en complemento a dos en el rango
$[-2^{22},\,2^{22}-1]$. a) ¿Cuál es el número de bits de los registros? b) ¿Cuántos KB de memoria puede direccionar como mucho?""",
r"""**a)** Con $n$ bits en Ca2 el rango es $[-2^{n-1},\,2^{n-1}-1]$. Aquí $n-1 = 22$ → **$n = 23$ bits**.

**b)** Si las direcciones tienen también 23 bits (mismo ancho de palabra) y se direcciona por bytes:
$2^{23}$ B $= 2^{13}$ KB $=$ **8192 KB** (= 8 MB).""",
pista="Rango Ca2 con n bits: [−2^(n−1), 2^(n−1)−1].",
respuestas=[R("a) bits", 23), R("b) KB", 8192)], herramienta="Representación de enteros"),

Ejercicio("repr-2", "Ca2 de 6 bits a decimal",
r"""Los siguientes números están en complemento a dos con 6 bits. Indique su valor decimal: a) 010011 b) 110111 c) 100000""",
r"""**Truco del peso negativo:** en Ca2 el bit de la izquierda pesa $-2^{n-1}$ (aquí $-32$) y el resto pesa como siempre.

| Número | Cálculo | Valor |
|---|---|---|
| a) 010011 | $16+2+1$ | **19** |
| b) 110111 | $-32+16+4+2+1$ | **−9** |
| c) 100000 | $-32$ | **−32** (el más negativo; no tiene positivo «pareja») |

Comprobación de b) por el método clásico: empieza por 1 → negativo; invertir 001000 y sumar 1 → 001001 = 9 → −9.""",
pista="El bit de más peso vale −32.",
respuestas=[R("a)", 19), R("b)", -9), R("c)", -32)], herramienta="Representación de enteros"),

Ejercicio("repr-3", "Bits para el rango −8191…8191",
r"""Se desea representar enteros en el rango −8191…8191. ¿Cuántos bits hacen falta a) en complemento a uno? b) en signo-magnitud?""",
r"""Ca1 y signo-magnitud tienen el **mismo rango simétrico** con $n$ bits: $[-(2^{n-1}-1),\,2^{n-1}-1]$ (los dos tienen un «doble cero»).

$8191 = 2^{13}-1$ → $n-1 = 13$ → **a) 14 bits** y **b) 14 bits**. (Con 13 bits solo llegaríamos a ±4095.)""",
pista="8191 = 2^13 − 1",
respuestas=[R("a) Ca1", 14), R("b) SM", 14)], herramienta="Representación de enteros"),

Ejercicio("repr-4", "Representar con 5 bits",
r"""Indique la representación razonada de: a) −16 en Ca2 con 5 bits; b) −16 en Ca1 con 5 bits; c) +13 en signo-magnitud
con 5 bits; d) −14 en Ca2 con 5 bits.""",
r"""**a) 10000.** Rango Ca2 de 5 bits: $[-16, 15]$, así que −16 cabe justo: es el patrón con solo el bit de signo, $-2^4$.

**b) No se puede.** Rango Ca1 de 5 bits: $[-15, 15]$. ¡Ojo, es la trampa del ejercicio!

**c) 01101.** Signo 0 (positivo) y magnitud 13 = 1101 en 4 bits.

**d) 10010.** $+14 = 01110$ → invertir: $10001$ → sumar 1: **$10010$**.
(Comprobación: $-16 + 2 = -14$ ✓.)""",
pista="Mira primero el rango de cada representación con 5 bits.",
respuestas=[R("a)", "10000", "bin"), R("b) ¿se puede? (si/no)", ["no"], "texto"), R("c)", "01101", "bin"), R("d)", "10010", "bin")],
herramienta="Representación de enteros"),

Ejercicio("repr-5", "14 y 3,5 en IEEE 754 simple",
r"""Represente en el estándar IEEE 754 de simple precisión los números **14** y **3,5**.""",
r"""Receta: **1)** pasar a binario, **2)** normalizar $1{,}xxx\cdot2^E$, **3)** exponente con exceso 127, **4)** mantisa sin el 1 implícito.

**14:**
1. $14 = 1110_2$
2. $1110 = 1{,}110\cdot2^3$
3. Exponente: $3 + 127 = 130 = 1000\,0010$
4. Mantisa: $110\,0000\ldots0$ (23 bits)

`0 10000010 11000000000000000000000` → **0x41600000**

**3,5:**
1. $3{,}5 = 11{,}1_2$
2. $1{,}11\cdot2^1$
3. Exponente: $1 + 127 = 128 = 1000\,0000$
4. Mantisa: $1100\ldots0$

`0 10000000 11000000000000000000000` → **0x40600000**""",
pista="14 = 1,11·2³ y 3,5 = 1,11·2¹: tienen la misma mantisa.",
respuestas=[R("14 en hex", "41600000", "hex"), R("3,5 en hex", "40600000", "hex")], herramienta="IEEE 754"),

Ejercicio("repr-6", "Precisión del float en 32 y 64 bits",
r"""a) ¿Dónde tiene más precisión una variable *float*, en un computador de 32 bits o en uno de 64 bits?
b) ¿Se puede almacenar de forma exacta cualquier entero de 32 bits en Ca2 en un *float*?""",
r"""**a) En los dos igual.** Un `float` es IEEE 754 de simple precisión (32 bits: 1 + 8 + 23) en cualquier máquina; lo que
cambia con el «computador de 64 bits» es el tamaño de los registros enteros y las direcciones, no el formato del `float`.

**b) No.** Un float tiene 23 bits de mantisa + 1 implícito = **24 bits significativos**. Un entero de 32 bits puede
necesitar hasta 31 bits significativos. El primer entero que no cabe es $2^{24}+1 = 16\,777\,217$: en binario es un 1, 23
ceros y otro 1 (25 bits) → al guardarlo se redondea a 16 777 216.

💡 Analogía: es como apuntar un número de teléfono con solo 7 cifras de espacio: los números largos pierden las últimas.""",
pista="¿Cuántos bits significativos tiene la mantisa de un float?",
respuestas=[R("Primer entero positivo no representable exactamente", 2**24 + 1)], herramienta="IEEE 754"),

Ejercicio("repr-7", "Suma 14 + 3,5 en IEEE 754",
r"""Realice la suma de los números anteriores (14 y 3,5) representados en IEEE 754.""",
r"""1. **Igualar exponentes** (se desplaza la mantisa del número pequeño): $14 = 1{,}110\cdot2^3$,
   $3{,}5 = 1{,}11\cdot2^1 = 0{,}0111\cdot2^3$.
2. **Sumar mantisas:** $1{,}1100 + 0{,}0111 = 10{,}0011$.
3. **Normalizar:** $10{,}0011\cdot2^3 = 1{,}00011\cdot2^4$.
4. **Empaquetar:** exponente $4 + 127 = 131 = 1000\,0011$; mantisa $00011\,0\ldots0$.

`0 10000011 00011000000000000000000` → **0x418C0000** $= 17{,}5$ ✓""",
pista="Lleva el 3,5 a exponente 3 desplazando la mantisa dos posiciones a la derecha.",
respuestas=[R("Resultado en hex", "418C0000", "hex")], herramienta="IEEE 754"),

Ejercicio("repr-8", "Producto 14 · 3,5 en IEEE 754",
r"""Realice el producto de los números anteriores representados en IEEE 754.""",
r"""1. **Signo:** $0\oplus0 = 0$.
2. **Exponentes se suman** (quitando un exceso): $130 + 128 - 127 = 131$ (es decir, $3 + 1 = 4$).
3. **Mantisas se multiplican:** $1{,}11\times1{,}11 = 11{,}0001$.
4. **Normalizar:** $11{,}0001\cdot2^4 = 1{,}10001\cdot2^5$ → exponente $5+127 = 132 = 1000\,0100$.

`0 10000100 10001000000000000000000` → **0x42440000** $= 49$ ✓""",
pista="Al sumar dos exponentes con exceso, el exceso aparece dos veces: réstalo una vez.",
respuestas=[R("Resultado en hex", "42440000", "hex")], herramienta="IEEE 754"),

Ejercicio("repr-9", "Formato de 16 bits: extremos",
r"""Coma flotante de 16 bits tipo IEEE 754: 1 de signo, 5 de exponente y 10 de mantisa. a) Menor y mayor número no
normalizado. b) Menor y mayor normalizado.""",
r"""Exceso $= 2^{5-1}-1 = 15$. Exponentes normales: 1…30 → $E\in[-14, 15]$. Los no normalizados usan exponente 00000 y
valen $0{,}m\cdot2^{-14}$.

**a) No normalizados (positivos):**
- Menor: `0 00000 0000000001` $= 2^{-10}\cdot2^{-14} = 2^{-24}\approx\mathbf{5{,}96\cdot10^{-8}}$
- Mayor: `0 00000 1111111111` $= (1-2^{-10})\cdot2^{-14}\approx\mathbf{6{,}0976\cdot10^{-5}}$

**b) Normalizados (positivos):**
- Menor: `0 00001 0000000000` $= 2^{-14}\approx\mathbf{6{,}1035\cdot10^{-5}}$
- Mayor: `0 11110 1111111111` $= (2-2^{-10})\cdot2^{15} = \mathbf{65\,504}$

(Los negativos son los mismos con el signo a 1.)""",
pista="Exceso 15; exponente 00000 → no normalizado con 2^−14; 11111 reservado para ∞/NaN.",
respuestas=[R("Menor no normalizado", 2**-24, tolerancia=1e-3), R("Mayor no normalizado", (1 - 2**-10) * 2**-14, tolerancia=1e-3),
            R("Menor normalizado", 2**-14, tolerancia=1e-3), R("Mayor normalizado", 65504)], herramienta="IEEE 754"),

Ejercicio("repr-10", "14 y 3,5 en 16 bits",
r"""Represente 14 y 3,5 en la coma flotante de 16 bits anterior (1 + 5 + 10).""",
r"""Mismo método, pero con exceso 15 y 10 bits de mantisa.

- **14** $= 1{,}11\cdot2^3$ → exponente $3+15 = 18 = 10010$ → `0 10010 1100000000` = `0100 1011 0000 0000` → **0x4B00**
- **3,5** $= 1{,}11\cdot2^1$ → exponente $1+15 = 16 = 10000$ → `0 10000 1100000000` = `0100 0011 0000 0000` → **0x4300**""",
respuestas=[R("14", "4B00", "hex"), R("3,5", "4300", "hex")], herramienta="IEEE 754"),

Ejercicio("repr-11", "Hexadecimal IEEE 754 a decimal",
r"""Valor decimal de estos números en IEEE 754 de 32 bits: a) 0xFF800000 b) 0x7F804000 c) 0xC7B00000 d) 0x00180000""",
r"""Separa siempre **signo (1) | exponente (8) | mantisa (23)**:

**a) 0xFF800000** = `1 11111111 000…0`: exponente todo unos y mantisa 0 → **−∞**.

**b) 0x7F804000** = `0 11111111 000000001000…0`: exponente todo unos y mantisa ≠ 0 → **NaN**.

**c) 0xC7B00000** = `1 10001111 0110000…0`: exponente $143-127 = 16$, mantisa $1{,}011_2 = 1{,}375$ →
$-1{,}375\cdot2^{16} = $ **−90 112**.

**d) 0x00180000** = `0 00000000 0011000…0`: exponente 0 → **no normalizado**: $0{,}0011_2\cdot2^{-126} = 3\cdot2^{-4}\cdot2^{-126} =
3\cdot2^{-130}\approx$ **$2{,}2041\cdot10^{-39}$**.""",
pista="Exponente 11111111 → ∞ o NaN; 00000000 → cero o no normalizado (sin 1 implícito, exponente −126).",
respuestas=[R("a)", ["-inf", "−inf", "-infinito", "menos infinito", "−∞", "-∞"], "texto"), R("b)", ["nan"], "texto"),
            R("c)", -90112), R("d)", 3 * 2**-130, tolerancia=1e-4)], herramienta="IEEE 754"),

Ejercicio("repr-12", "Suma con 3 dígitos: con y sin guarda",
r"""Sume $8{,}76\times10^{1}$ a $1{,}47\times10^{2}$ suponiendo que solo hay 3 dígitos para la mantisa, primero con dígitos de
guarda y redondeo y después sin ellos.""",
r"""Igualamos al exponente mayor: $8{,}76\times10^1 = 0{,}876\times10^2$.

**Con guarda y redondeo** (la ALU guarda los dígitos que «se salen» mientras opera):
$0{,}876 + 1{,}470 = 2{,}346$ → redondear a 3 dígitos → **$2{,}35\times10^2$**.

**Sin ellos** (el dígito que se sale al desplazar se pierde): $0{,}87 + 1{,}47 =$ **$2{,}34\times10^2$**.

El resultado exacto es $234{,}6$: con dígitos de guarda el error es 0,4; sin ellos, 0,6.""",
errata="El enunciado original pone «8,76 x 10 a 1,47 x 102»: se perdieron los superíndices; es 8,76·10¹ y 1,47·10².",
respuestas=[R("Con guarda (×10²)", 2.35), R("Sin guarda (×10²)", 2.34)]),

Ejercicio("repr-13", "Error de 0,1 en 16 y 32 bits",
r"""¿Qué error se comete al representar 0,1 con el formato de 16 bits frente a usar 32 bits?""",
r"""$0{,}1 = 0{,}000110011001100\ldots_2$ (periódico: ¡0,1 no tiene representación exacta en binario!) $= 1{,}100110011\ldots\cdot2^{-4}$.

- **16 bits** (10 bits de mantisa, redondeo al más cercano): `0 01011 1001100110` = 0x2E66 =
  $0{,}0999755859375$ → error $\approx$ **$2{,}44\cdot10^{-5}$**.
- **32 bits** (23 bits): 0x3DCCCCCD $= 0{,}100000001490116\ldots$ → error $\approx$ **$1{,}49\cdot10^{-9}$**.

Con 13 bits más de mantisa, el error es unas $2^{13}\approx 8000$ veces menor (de hecho ~16 000 por cómo cae el redondeo).""",
respuestas=[R("Error con 16 bits", 2.44140625e-05, tolerancia=1e-2), R("Error con 32 bits", 1.4901161e-09, tolerancia=1e-2)],
herramienta="IEEE 754"),

Ejercicio("repr-14", "0x7F800000 y 0x40E00000",
r"""Valor decimal de estos números IEEE 754 de 32 bits: a) 0x7F800000 b) 0x40E00000""",
r"""**a)** `0 11111111 000…0` → exponente todo unos, mantisa 0, signo + → **+∞**.

**b)** `0 10000001 11000…0` → exponente $129-127 = 2$, mantisa $1{,}11_2 = 1{,}75$ → $1{,}75\cdot4 =$ **7**.""",
respuestas=[R("a)", ["inf", "+inf", "infinito", "+infinito", "∞", "+∞"], "texto"), R("b)", 7)], herramienta="IEEE 754"),

Ejercicio("repr-15", "¿Cuántos no normalizados hay?",
r"""¿Cuántos números no normalizados se pueden representar en el estándar IEEE 754 de 32 bits?""",
r"""Un no normalizado tiene exponente `00000000` y mantisa **distinta de 0** (mantisa 0 es el cero).
Mantisas posibles: $2^{23}-1$; y dos signos:
$$2\cdot(2^{23}-1) = \mathbf{16\,777\,214}.$$""",
respuestas=[R("Cantidad", 2 * (2**23 - 1))], herramienta="IEEE 754"),

Ejercicio("repr-16", "Floats entre 1 y 2, y entre 3 y 4",
r"""Calcule el número de valores en coma flotante de 32 bits entre 1 y 2, y entre 3 y 4.""",
r"""**Entre 1 y 2** (intervalo $[1,2)$): todos tienen exponente 0 y la mantisa recorre sus $2^{23}$ valores →
**$2^{23} = 8\,388\,608$**.

**Entre 3 y 4** ($[3,4)$): exponente 1, y la mantisa tiene que empezar por 1 ($1{,}1xxx\cdot2^1$) → quedan 22 bits libres →
**$2^{22} = 4\,194\,304$**.

💡 Los floats son como una regla cuyas marcas se separan cada vez más: cada «octava» $[2^k, 2^{k+1})$ tiene los mismos
$2^{23}$ valores, así que $[3,4)$, que es media octava, tiene la mitad. (Si se cuenta también el extremo 2 o 4, súmale 1.)""",
respuestas=[R("Entre 1 y 2", 2**23), R("Entre 3 y 4", 2**22)], herramienta="IEEE 754"),

Ejercicio("repr-17", "Más Ca2 de 6 bits",
r"""En complemento a dos con 6 bits, indique el valor decimal de: a) 010011 b) 100111""",
r"""a) $16+2+1 =$ **19**. b) $-32+4+2+1 =$ **−25**.""",
respuestas=[R("a)", 19), R("b)", -25)], herramienta="Representación de enteros"),

Ejercicio("repr-18", "0x00200000",
r"""Valor decimal de 0x00200000 en IEEE 754 de 32 bits.""",
r"""`0 00000000 01000000000000000000000` → exponente 0 y mantisa ≠ 0 → **no normalizado**:
$0{,}01_2\cdot2^{-126} = 2^{-2}\cdot2^{-126} = 2^{-128}\approx$ **$2{,}9387\cdot10^{-39}$**.""",
respuestas=[R("Valor", 2**-128, tolerancia=1e-4)], herramienta="IEEE 754"),

Ejercicio("repr-19", "0xBE800000",
r"""Valor decimal de 0xBE800000 en IEEE 754 de simple precisión.""",
r"""`1 01111101 000…0` → signo −, exponente $125-127 = -2$, mantisa 1,0 → $-1\cdot2^{-2} =$ **−0,25**.""",
respuestas=[R("Valor", -0.25)], herramienta="IEEE 754"),

Ejercicio("repr-20", "Mayor negativo y 0xFFF00000",
r"""a) Valor decimal del **mayor número negativo** representable en IEEE 754 simple. b) Valor de 0xFFF00000.""",
r"""**a)** La frase es ambigua, así que conviene dar las dos lecturas:
- «Mayor» en **magnitud** (el más negativo): `1 11111110 111…1` $= -(2-2^{-23})\cdot2^{127}\approx$ **$-3{,}4028\cdot10^{38}$**.
- «Mayor» en el sentido de **más cercano a cero**: `1 00000000 000…01` $= -2^{-149}\approx -1{,}4\cdot10^{-45}$ (no normalizado).

En el examen, escribe la que pidan y aclara la interpretación: así no te la pueden tumbar.

**b)** `1 11111111 1110000…0`: exponente todo unos y mantisa ≠ 0 → **NaN** (Not a Number).""",
respuestas=[R("a) el más negativo", -(2 - 2**-23) * 2**127, tolerancia=1e-6), R("b)", ["nan"], "texto")], herramienta="IEEE 754"),
], icono="🔢")
