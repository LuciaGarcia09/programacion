"""Teoría de Python (guía «Programación en Python»), por capítulos."""
from ui.teoria import Tema, S

T1 = Tema("py1", "Python", 1, "Programar y construir software",
          "Qué es programar, la máquina de Von Neumann, lenguajes, compilar o interpretar, paradigmas y calidad.", [

S("ingenieria", "1.1 Ingeniería, programa y algoritmo", "Guía de Python · 1.1–1.2", [
    ("idea", "La habitación china", r"""
El ordenador **no entiende** tus instrucciones: las **ejecuta**, todas y exactamente como están escritas. Como alguien
encerrado con un libro de reglas «si recibes estos símbolos chinos, devuelve estos otros»: desde fuera parece que sabe
chino, pero solo sigue reglas. Si tus reglas no tienen sentido, las sigue igual."""),
    ("def", "Definiciones básicas", r"""
- **Computadora:** máquina de propósito general: *hardware* (lo físico) + *software* (los programas).
- **Programación:** actividad de crear programas.
- **Programa:** lista de instrucciones bien definidas para ser ejecutada en una computadora.
- **Algoritmo:** lista de instrucciones bien definidas para hacer una tarea **en un tiempo finito**."""),
    ("idea", "Receta y cocina", r"""
Un **algoritmo** es la receta (la idea: «bate los huevos, añade harina…»). Un **programa** es esa receta escrita en un
idioma que la cocina entiende (Python, C…). Un mismo algoritmo puede escribirse como muchos programas."""),
]),

S("vonneumann", "1.2 La máquina de Von Neumann y el ciclo de instrucción", "Guía de Python · 1.3–1.4", [
    ("def", "Partes", r"""
| Parte | Para qué sirve |
|---|---|
| Entrada / salida | Comunicarse: teclado, pantalla, sensores, red… |
| **Unidad de control** | Dirige: recoge la siguiente instrucción, la decodifica y manda ejecutarla |
| **ALU** | Calcula: comparar, sumar, restar, mover… |
| **Memoria** | Guarda **a la vez el programa y los datos** |
| Almacenamiento externo | Guardar a largo plazo: discos, la nube… |"""),
    ("pasos", "El ciclo de instrucción", r"""
**1. Recoge** la siguiente instrucción → **2. Decodifica** (¿qué es?) → **3. Ejecuta** (en la ALU) → **4. Almacena** el
resultado → y vuelta a empezar. (Lo verás a fondo, señal a señal, en Fundamentos de Computadores con WepSIM.)"""),
    ("def", "Todo son bits", r"""
| Información | Cómo se codifica |
|---|---|
| Naturales | base 2: $9_{10} = 1001_2$ |
| Enteros | complemento a uno o a dos |
| Reales | IEEE 754 (simple o doble precisión) |
| Booleanos | 0 = falso; distinto de 0 = verdadero |
| Caracteres | antes ASCII; hoy **Unicode** (cada carácter un número) guardado como UTF-8, UTF-16… |
| Imágenes, sonido | cada formato la suya: jpg, png, mp3… |

La **misma secuencia de bits** se interpreta de formas distintas según dónde esté y cómo se codificó."""),
], "Representación de enteros"),

S("lenguajes", "1.3 Lenguajes, compiladores e intérpretes", "Guía de Python · 1.5", [
    ("def", "Niveles", r"""
| Nivel | Ejemplo | Cómo es |
|---|---|---|
| Lenguaje máquina | `1000100111000011` | binario puro: lo que entiende la CPU |
| Ensamblador | `movl %eax %ebx` | nemónicos 1 a 1 con el código máquina |
| Alto nivel | `if hoja == raiz: …` | cercano al lenguaje humano |"""),
    ("idea", "Compilar o interpretar", r"""
**Compilar** (C) = traducir un libro entero antes de publicarlo: cuesta al principio pero luego se lee rapidísimo.
**Interpretar** (Python) = un intérprete simultáneo que traduce frase a frase: más lento, pero puedes cambiar el discurso
sobre la marcha y funciona en cualquier máquina que tenga el intérprete."""),
    ("def", "Traductores y fases", r"""
- **Preprocesador** (alto nivel ampliado → estándar) · **Compilador** (alto nivel → máquina/ensamblador) ·
  **Ensamblador** (ensamblador → máquina) · **Enlazador** (une y reubica trozos para obtener el ejecutable).
- Fases: **análisis léxico** (tokens) → **sintáctico** (árbol) → **semántico** → código intermedio → optimizador →
  generador de código. Con una tabla de símbolos, una de literales y un gestor de errores.
- Errores en **tiempo de compilación** (antes de ejecutar) o en **tiempo de ejecución** (mientras funciona)."""),
    ("idea", "Corregir una redacción", r"""
Léxico = separar palabras. Sintáctico = frases bien construidas («Rápido el come gato» ✗). Semántico = que tengan
sentido («La piedra come felicidad» tiene buena sintaxis pero ✗ semántica)."""),
]),

S("paradigmas", "1.4 Paradigmas de programación", "Guía de Python · 1.6", [
    ("def", "Los paradigmas", r"""
| Paradigma | Idea | Ejemplos |
|---|---|---|
| **Imperativo** | órdenes que cambian el estado; qué calcular y **cómo** | FORTRAN, C, Pascal, Python |
| **Estructurado** | solo secuencia, selección y repetición (+ funciones) | |
| **Orientado a objetos** | lo importante es la información: objeto = datos + operaciones | Smalltalk, C++, Java, Python |
| **Declarativo** | se dice **qué** se quiere, no cómo | SQL, Prolog, expresiones regulares |
| **Funcional** | combinar funciones sin efectos colaterales | LISP, Haskell, Python |
| **Concurrente** | varios procesos a la vez (paralelo o distribuido) | Erlang, Java, ADA |"""),
    ("idea", "Pedir una pizza", r"""
Imperativo: «amasa, extiende, pon tomate, hornea 12 min». Declarativo: «quiero una margarita». Orientado a objetos:
`pizzeria.pedir("margarita")`. **Python es multiparadigma** (imperativo, objetos y funcional)."""),
]),

S("software", "1.5 Construir software y calidad", "Guía de Python · 1.7", [
    ("pasos", "Procesos", r"""
1. **Análisis** — ¿qué hay que hacer? 2. **Especificación** — fijar exactamente qué hará. 3. **Diseño** — ¿cómo?
(algoritmos, módulos, refinamiento progresivo). 4. **Implementación** — escribir el código. 5. **Verificación y prueba** —
tests y depuración. 6. **Mantenimiento** — corregir, mejorar, adaptar."""),
    ("truco", "Cohesión y acoplamiento", r"""
Buen diseño = **alta cohesión** (cada parte hace una sola cosa y bien) y **bajo acoplamiento** (las partes dependen poco
unas de otras). Como un equipo donde cada persona tiene una tarea clara."""),
    ("def", "Criterios de calidad", r"""
Básicos: **corrección** (hace lo que debe), **robustez** (aguanta lo inesperado: letras donde pide un número),
**fiabilidad** (con datos normales no se equivoca), **eficiencia** (memoria y tiempo). Otros: extensibilidad,
reutilización, verificabilidad, compatibilidad, facilidad de uso, reparabilidad, portabilidad, funcionalidad, oportunidad,
integridad, economía."""),
]),
])

T2 = Tema("py2", "Python", 2, "Primeros pasos: input, print y la calculadora",
          "Qué es Python, cómo se ejecuta, el hola mundo, leer y escribir, y Python como calculadora.", [

S("que", "2.1 ¿Qué es Python?", "Guía de Python · 2.1–2.2", [
    ("def", "Características", r"""
Lenguaje de **alto nivel e interpretado**, **multiparadigma**, con **tipado dinámico** (no declaras el tipo: lo da el
valor) y multiplataforma. Lo creó **Guido van Rossum** en 1989 (el nombre viene de los **Monty Python**). Es de la
Python Software Foundation, con licencia libre. La implementación oficial es CPython."""),
    ("ojo", "Versiones", r"""Usa siempre **Python 3**. Si ves `print "hola"` sin paréntesis en internet, es Python 2 (abandonado)."""),
    ("def", "Cómo ejecutarlo", r"""
`python fichero.py` · `python -c "comandos"` · `python` (intérprete interactivo, el de `>>>`) · IPython · VS Code,
Spyder, Jupyter · en la web: Colab… Lee de la **entrada estándar** (teclado) y escribe en la **salida estándar** (pantalla)."""),
]),

S("io", "2.2 input() y print()", "Guía de Python · 2.3", [
    ("py", "Hola mundo con entrada", "nombre = input()\nprint(\"Hola \" + nombre + \".\")", "Lucía"),
    ("ojo", "input() SIEMPRE devuelve texto", r"""
`input()` lee una línea entera y la devuelve como **str**. Si quieres un número, conviértelo: `int(input())`,
`float(input("Altura: "))`. Si no, `"5" + 1` da `TypeError`."""),
    ("py", "Convertir lo leído", "entrada = input()          # el usuario escribe 5\nprint(type(entrada))       # <class 'str'>\nnumero = int(entrada)\nprint(type(numero), numero * 2)", "5"),
    ("def", "print()", r"""
Admite varios argumentos y los separa con un espacio; al terminar salta de línea. `sep=` cambia el separador y `end=` lo
que se escribe al final. Para pegar texto y números con `+` hay que pasar el número a `str()`."""),
    ("py", "sep y end", 'numero = 5\nprint("El número leído ha sido: " + str(numero))\nprint("El número leído ha sido:", numero)\nprint("a", "b", "c", sep="-", end="!\\n")'),
]),

S("calculadora", "2.3 Python como calculadora", "Guía de Python · 2.4", [
    ("py", "Precedencia y asociatividad", "print(2 + 3 - 4 + 4 * 5)\nprint(((2 + 3) - 4) + (4*5))\nprint(2 + (3 - (4 + (4*5))))\nprint(8 ** 5 ** 4 == 8 ** (5 ** 4))   # ** se agrupa de derecha a izquierda\nprint((8 ** 5) ** 4)"),
    ("py", "Bases, / y booleanos", "print(16 == 0b10000 and 16 == 0o20 and 16 == 0x10)\nprint(10 / 3)      # / siempre da un real\nprint(int(10 / 3))\nprint(True and (False or not False))"),
    ("ojo", "Los reales no son exactos", r"""
`0.1 + 0.2` da `0.30000000000000004`: los reales se guardan en binario (IEEE 754) con precisión limitada. **No compares
reales con `==`**: usa un margen (`abs(a - b) < 1e-9`)."""),
    ("py", "Compruébalo", "print(0.1 + 0.2)\nprint(0.1 + 0.2 == 0.3)\nprint(abs((0.1 + 0.2) - 0.3) < 1e-9)"),
], "IEEE 754"),
])

T3 = Tema("py3", "Python", 3, "Los ladrillos del lenguaje",
          "Análisis léxico, identificadores, literales, tipos, objetos y variables, operadores, cadenas y expresiones.", [

S("lexico", "3.1 Cómo lee Python tu programa", "Guía de Python · 3.1–3.2", [
    ("def", "Líneas, comentarios e indentación", r"""
- **Línea física** = lo que ves; **línea lógica** = una sentencia. Para partir una lógica en varias físicas: `\` al final (o
  dentro de paréntesis/corchetes/llaves, sin nada).
- **Comentarios**: de `#` al final de la línea.
- **Indentación**: los espacios al principio **agrupan las sentencias en bloques** (en C se usan llaves). Usa siempre
  **4 espacios** y no mezcles tabuladores."""),
    ("idea", "La indentación es el esquema de tus apuntes", r"""
Lo que está más metido a la derecha «pertenece» al título de encima. En Python no es estética: si te equivocas de
sangría, **cambia el significado** del programa (o da error)."""),
    ("def", "Identificadores", r"""
Nombres de variables, funciones… No empiezan por dígito, sin espacios ni signos, distinguen mayúsculas (`nota`, `Nota` y
`NOTA` son distintos) y no pueden ser palabras reservadas (`if`, `for`, `def`, `True`, `None`…). Válidos: `nota_final`,
`_x`, `suma2`. No válidos: `2suma`, `mi nota`, `for`, `nota-final`. Estilo recomendado: **snake_case**."""),
]),

S("literales", "3.2 Literales y tipos", "Guía de Python · 3.3–3.4", [
    ("def", "Literales", r"""
- **Cadenas**: `'hola'`, `"hola"`, y largas entre **tres comillas** (pueden ocupar varias líneas). Prefijos: `r` (raw), `f` (formato), `b` (bytes).
- **Enteros**: decimal, `0b101` (binario), `0o17` (octal), `0xA35f` (hexadecimal), con `_` para separar:
  `76_546_739_872`. **No tienen límite de tamaño**.
- **Reales**: `3.14`, `6.`, `.0001`, `3.14159e-6` (64 bits, doble precisión). **Imaginarios**: `3+4j`.
- El infinito no tiene literal: `float('inf')` o `math.inf`."""),
    ("def", "Tipos", r"""
| Categoría | Tipos |
|---|---|
| Texto | `str` |
| Numéricos | `int`, `float`, `complex` |
| Booleano | `bool` (`True`, `False`) |
| Secuencias | `list`, `tuple`, `range` |
| Nada | `NoneType` (`None`) |
| Más | `set`, `dict` |

El tipo lo fija el valor (`x = 3` → int; `x = 3.0` → float). Operar con tipos incompatibles da error al ejecutar
(`"2" + 3` → TypeError), aunque hay conversiones automáticas (`2.0 + 3` → 5.0). **Casting**: `int("5")`, `float(3)`,
`str(7)`, `int('ff', 16)` → 255, `bin(10)` → `'0b1010'`."""),
    ("py", "Adivina el resultado", "print(2+3, 2.0 + 3, 0x2 + 0x3)\nprint(\"2\" + '3')\nprint(2 and 3, 2 or 3, 2 & 3)\nprint(int('ff', 16), bin(10), hex(255), int(3.99))"),
]),

S("objetos", "3.3 Objetos y variables: etiquetas, no cajas", "Guía de Python · 3.5", [
    ("idea", "Etiquetas", r"""
En Python una variable **no es una caja**: es una **etiqueta** pegada a un objeto. `x = [1, 2]` pega `x` a una lista; si
luego `y = x`, pegas otra etiqueta a **la misma** lista (no la copias)."""),
    ("py", "Dos etiquetas, una lista", "x = [1, 2]\ny = x\ny.append(3)\nprint(x)          # ¡también cambia x!\nz = list(x)       # esto sí es una copia\nz.append(4)\nprint(x, z)"),
    ("def", "Mutables e inmutables", r"""
**Inmutables** (no pueden cambiar; para «cambiarlos» se crea otro objeto): `int`, `float`, `bool`, `str`, `tuple`.
**Mutables** (cambian por dentro sin dejar de ser el mismo objeto): `list`, `set`, `dict`.
Python tiene **tipado dinámico**: una variable puede guardar un int y luego una cadena; pero hay que darle valor antes de
usarla (si no, `NameError`)."""),
]),

S("operadores", "3.4 Operadores, booleanos y comparaciones", "Guía de Python · 3.6", [
    ("def", "Operadores numéricos", r"""
| Operación | Resultado | Ejemplo |
|---|---|---|
| `x / y` | cociente **real** (siempre float) | `7 / 2` → 3.5 |
| `x // y` | cociente entero (redondea **hacia abajo**) | `7 // 2` → 3 ; `-7 // 2` → −4 |
| `x % y` | resto | `7 % 3` → 1 |
| `x ** y` | potencia | `2 ** 10` → 1024 |
| `abs`, `round(x, n)`, `divmod(x, y)` | | `divmod(17, 5)` → (3, 2) |"""),
    ("truco", "// y % son la división del colegio", r"""
17 caramelos entre 5 amigos: a cada uno `17 // 5 = 3` y sobran `17 % 5 = 2`. Con `% 2` sabes si es par; con `% 10`
sacas la última cifra y con `// 10` la quitas."""),
    ("def", "Valor de verdad", r"""
Se evalúan a **False**: `None`, `False`, `0`, `0.0` y lo **vacío**: `''`, `()`, `[]`, `{}`, `set()`, `range(0)`.
Todo lo demás es True (¡también `' '` y `[0]`!). `and` y `or` son de **cortocircuito** y devuelven el último valor
evaluado (no siempre True/False)."""),
    ("def", "Comparaciones", r"""
`< <= > >= == != is is not`, todas con la misma prioridad y mayor que `and/or`. Se encadenan: `x < y <= z`.
**`==` compara valores; `is`, si son el mismo objeto**: `[] == []` es True pero `[] is []` es False. Usa `is` casi solo
para `None`."""),
    ("py", "Pruébalo", "print(bool(0 ** 0), bool(0.0), bool(' '), bool([0]))\nprint([] == [], [] is [])\nprint(1 < 2 < 3, 3 > 2 > 2)\nprint('' or 'Trondheim' or 'Hammer')"),
    ("def", "Precedencia (de más a menos)", r"""
`()` → `**` → `-x` → `* / // %` → `+ -` → comparaciones (`< == in is`…) → `not` → `and` → `or`.
Así `A and not B or C` es `(A and (not B)) or C`. Si dudas, **paréntesis**."""),
]),

S("cadenas", "3.5 Cadenas, expresiones y asignación", "Guía de Python · 3.7–3.8", [
    ("py", "Cadenas básicas", "print('Hola Mundo', \"'Sí', Hola\")\nprint(\"Primera línea\\nSegunda línea\")\nprint(3 * 'o' + 'h')\nprint('\\u25B2')"),
    ("ojo", "Rutas de Windows", r"""
`print("c:\home\nombreusuario")` imprime mal: `\n` es un salto de línea. Usa `"c:\\home\\nombreusuario"` o una cadena
**raw**: `r"c:\home\nombreusuario"`. Guarda tus `.py` siempre en **UTF-8**."""),
    ("def", "Expresión y sentencia", r"""
**Expresión**: combinación que produce un valor (`7*x+5`, `b and (a or b)`). **Sentencia**: unidad de ejecución; se
ejecutan en orden. La **asignación** `x = x + 1` no es una ecuación: «calcula lo de la derecha y guárdalo a la
izquierda». Para comparar, `==`."""),
]),
])

T4 = Tema("py4", "Python", 4, "Sentencias de control",
          "Algoritmos, programación estructurada, if/elif/else, for y range, while, break y continue.", [

S("algoritmos", "4.1 Problemas, algoritmos y programación estructurada", "Guía de Python · 4.1–4.3", [
    ("def", "Conceptos", r"""
- **Algoritmo**: conjunto finito de reglas precisas que resuelve una tarea en tiempo finito. **Problema decidible**: el que
  tiene algoritmo. Hay problemas **no decidibles**: el de la **parada** (saber si un programa cualquiera termina), el de
  decisión de la lógica de primer orden, el del embaldosado.
- **Tesis de Church-Turing**: algoritmo = lo que puede computar una máquina de Turing.
- **Teorema de la programación estructurada**: todo programa propio equivale a uno con solo **secuencia, selección y
  repetición** (tres piezas de Lego para construirlo todo, sin `goto`)."""),
    ("def", "Sentencias simples y compuestas", r"""
**Simples** (una línea lógica): de expresión y de asignación — también múltiple (`a, b = b, a` intercambia) y aumentada
(`x += 1`). **Compuestas**: `if`, `for`, `while`, `def`…: cabecera con **dos puntos** y bloque indentado."""),
]),

S("if", "4.2 if / elif / else", "Guía de Python · 4.4", [
    ("py", "Nota numérica a texto", 'nota = float(input("Nota: "))\nif nota < 0 or nota > 10:\n    print("Nota inválida")\nelif nota < 5:\n    print("Suspenso")\nelif nota < 7:          # aquí ya sabemos que nota >= 5\n    print("Aprobado")\nelif nota < 9:\n    print("Notable")\nelif nota < 9.5:\n    print("Sobresaliente")\nelse:\n    print("Matrícula de Honor")', "7.3"),
    ("errata", "Cuaderno 03", r"""En el cuaderno una nota negativa (−3) imprime «Suspenso»: hay que comprobar **primero** que la nota sea válida."""),
    ("ojo", "Un else pertenece al if con su misma sangría", r"""
```python
if a > 2 and b <= 3:              if a > 2 and b <= 3:
    if not par:                       if not par:
        c = 10                            c = 10
    if a == 3:                            if a == 3:
        z = 33                                z = 33
    else:     # del «if a == 3»       else:     # del «if not par»
        z = 31                            z = 31
```
Con a = 4, b = 1, par = False: el de la izquierda deja z = 31; el de la derecha no asigna z."""),
    ("truco", "De Morgan", r"""`not (A and B)` = `not A or not B` · `not (A or B)` = `not A and not B`."""),
]),

S("for", "4.3 for y range", "Guía de Python · 4.5", [
    ("def", "range", r"""
| Forma | Genera |
|---|---|
| `range(fin)` | 0 … fin−1 |
| `range(ini, fin)` | ini … fin−1 |
| `range(ini, fin, paso)` | de paso en paso, sin llegar a fin (paso negativo: hacia atrás) |

**El fin nunca se incluye**: de 1 a n es `range(1, n + 1)`."""),
    ("py", "Acumuladores", "suma = 0\nfor n in range(10):\n    suma += n + 1\nprint(suma)\nproducto = 1\nfor k in range(10, 21, 2):\n    producto *= k\nprint(\"El producto es:\", producto)\nprint(list(range(10, 0, -3)))"),
    ("ojo", "No llames sum a una variable", r"""Tapa la función `sum()`. Usa `suma`, `total`… (lo mismo con `list`, `str`, `max`)."""),
]),

S("while", "4.4 while, break y continue", "Guía de Python · 4.6", [
    ("py", "Sumar hasta una línea vacía", 'linea = input("Números, uno por línea:\\n")\nsuma = 0\nwhile linea != "":\n    suma += int(linea)\n    linea = input()\nprint("La suma es:", suma)', "3\n4\n5\n6\n\n"),
    ("truco", "¿for o while?", r"""**for**: sabes cuántas veces o tienes una secuencia que recorrer. **while**: repites hasta que pase algo."""),
    ("py", "break y continue", "for n in range(1, 10):\n    if n % 2 == 0:\n        continue       # los pares no se imprimen\n    if n > 7:\n        break          # al llegar a 9 se acaba\n    print(n)"),
    ("py", "Recorrer secuencias (y por qué las cadenas no cambian)", "cadena = 'hola'\nlista = ['h', 'o', 'l', 'a']\nfor c in cadena:\n    print(c, end=' ')\nprint()\nlista[0] = 'H'\nprint(lista)\ntry:\n    cadena[0] = 'H'\nexcept TypeError as e:\n    print('TypeError:', e)"),
    ("py", "Invertir los números de la entrada", 'numeros = []\nlinea = input()\nwhile linea != "":\n    numeros.append(int(linea))\n    linea = input()\nfor i in range(len(numeros) - 1, -1, -1):\n    print(numeros[i])', "3\n4\n5\n\n"),
]),
])

T5 = Tema("py5", "Python", 5, "Funciones",
          "def y return, la pila de llamadas, tipos de parámetros, ámbito, paso de argumentos, recursividad, lambda y main.", [

S("def", "5.1 Definir y llamar funciones", "Guía de Python · 5.1–5.2", [
    ("idea", "Una máquina de zumos", r"""
Le metes cosas por la entrada (**argumentos**), hace su trabajo (el **cuerpo**) y te devuelve un resultado (**return**).
Para usarla no necesitas saber cómo funciona por dentro."""),
    ("py", "def y return", 'def cuadrado(n):\n    """Devuelve n al cuadrado."""\n    return n ** 2\n\nx = cuadrado(100)\nprint(x)\nprint(print("hola"))     # print devuelve None'),
    ("def", "Reglas", r"""
Los paréntesis son obligatorios aunque no haya parámetros. Puede haber 0, 1 o varios `return`. Una función sin `return`
devuelve **None** (un *procedimiento*). La llamada forma parte de una expresión: se sustituye por lo que devuelve."""),
]),

S("pila", "5.2 La pila de llamadas", "Guía de Python · 5.3", [
    ("py", "Funciones que llaman a funciones", 'def nueva_linea():\n    print()\n\ndef tres_lineas():\n    nueva_linea()\n    nueva_linea()\n    nueva_linea()\n\ndef main():\n    print("Linea 1")\n    tres_lineas()\n    print("Linea 2")\n\nmain()'),
    ("idea", "Marcapáginas", r"""
Cada llamada **apila** un marco (dirección de vuelta, argumentos, resultado); al terminar se **desapila** y se vuelve
donde se quedó. Como leer notas al pie que remiten a otras: el último marcapáginas que pones es el primero que quitas.
(En MIPS lo harás a mano con `jal`, `$ra` y `$sp`.)"""),
]),

S("parametros", "5.3 Tipos de parámetros", "Guía de Python · 5.4", [
    ("def", "Las seis formas", r"""
1. **Posicionales**: por orden, mismo número.
2. **Con valor por defecto**: `def f(a, eps=1e-2)` (se calcula **al definir**; después de uno con valor no puede ir uno sin él).
3. **Por nombre**: `f(b=0, a=1)` (el orden da igual; un parámetro no puede recibir dos valores).
4. **`*args`**: los sobrantes en una **tupla**.
5. **`**kwargs`**: los con nombre sobrantes en un **diccionario**.
6. **`/` y `*`**: antes de `/`, solo posición; después de `*`, solo nombre.

Orden en la cabecera: normales → con defecto → `*args` → solo por nombre → `**kwargs`."""),
    ("py", "Comparar reales con margen", "def son_iguales(f1, f2, epsilon=1.0e-2):\n    return abs(f1 - f2) < epsilon\n\nprint(son_iguales(0.999, 1.0))\nprint(son_iguales(0.999, 1.0, 1.0e-3))\nprint(1.0 - 0.999)"),
    ("errata", "Diapositivas 03", r"""Se define `son_iguales` pero se llama `sonIguales(...)`: el nombre debe coincidir (si no, `NameError`)."""),
    ("ojo", "Nunca una lista como valor por defecto", r"""Se crea **una sola vez** y se comparte entre llamadas."""),
    ("py", "La trampa de la lista por defecto", "def f(valor, lista=[]):\n    lista.append(valor)\n    return lista\n\ndef g(valor, lista=None):\n    if lista is None:\n        lista = []\n    lista.append(valor)\n    return lista\n\nprint(f(1), f(2))      # ¡sorpresa!\nprint(g(1), g(2))"),
    ("py", "*args, **kwargs, / y *", 'def suma_todo(*numeros):\n    return sum(numeros)\n\ndef presentar(nombre, *aficiones, ciudad="León"):\n    print(nombre, aficiones, ciudad)\n\ndef ficha(**datos):\n    for clave, valor in datos.items():\n        print(clave, "=", valor)\n\ndef fpos(a, b, /, c, *, d):\n    return a + b + c + d\n\nprint(suma_todo(1, 2, 3))\npresentar("Lucía", "leer", ciudad="Madrid")\nficha(nombre="Lucía", edad=18)\nprint(fpos(1, 2, c=3, d=4))'),
]),

S("varios", "5.4 Varios resultados, docstrings, anotaciones y lambda", "Guía de Python · 5.5–5.7", [
    ("py", "Devolver una tupla", "def calculos(n):\n    return n * n, n * n * n\n\ncuadrado, cubo = calculos(3)\nprint(cuadrado, cubo, calculos(3))"),
    ("def", "Docstrings y type hints", r"""
La primera línea del cuerpo puede ser un **docstring** (`help(f)` lo muestra). Las **anotaciones** `def sumar(a: int,
b: int) -> int:` **no se comprueban al ejecutar** (`sumar("ho", "la")` funciona): son documentación para ti y VS Code."""),
    ("py", "lambda, map, filter, sorted", "multiplicar = lambda x, y: x * y\nprint(multiplicar(3, 4))\nprint(sorted(['banana', 'Kiwi', 'apple'], key=lambda s: s.lower()))\nprint(list(map(lambda x: x * 2, [1, 2, 3])))\nprint(list(filter(lambda x: x % 2 == 0, range(10))))"),
]),

S("ambito", "5.5 Ámbito: local, nonlocal y global", "Guía de Python · 5.8", [
    ("idea", "Habitaciones", r"""
Al buscar un nombre, Python mira primero en tu **cuarto** (local), luego en el **salón** (la función que contiene a la tuya),
luego en el **portal** (global) y por último en la **calle** (predefinidos: `print`, `len`…). Lo que dejas en tu cuarto
desaparece al salir."""),
    ("py", "global y nonlocal", 'x = "global"\ndef fx():\n    x = "local en fx"      # x NUEVA, local\n    print("x en fx:", x)\nfx()\nprint("x global:", x)\n\ny = "global"\ndef fy():\n    y = "local de fy"\n    def sy():\n        nonlocal y          # la y de fy\n        y = "local de sy"\n    sy()\n    print("y en fy:", y)\nfy()\nprint("y global:", y)'),
    ("errata", "Diapositivas 03 · nonlocal", r"""Dentro de `sy()` pone «local de gy» y «Valor de y en gy»: la función se llama **sy**."""),
    ("ojo", "UnboundLocalError", r"""
`contador += 1` dentro de una función sin `global contador` falla: como hay una asignación, Python decide que es local… y
aún no tiene valor. Mejor: pásalo como parámetro y devuélvelo."""),
]),

S("paso", "5.6 ¿Cómo se pasan los argumentos?", "Guía de Python · 5.9", [
    ("def", "Por valor de la referencia", r"""
La función recibe **otra etiqueta pegada al mismo objeto**. Si **reasignas** el parámetro (`l = [0]`), solo mueves la
etiqueta local. Si **modificas** un objeto mutable (`l.append(3)`), el cambio se ve fuera."""),
    ("py", "La copia de la llave", "unalista = [1, 2]\ndef f(l):\n    l.append(3)     # mismo objeto → se ve fuera\n    l = [0]         # otra lista (local)\nf(unalista)\nprint(unalista)"),
    ("idea", "La llave de casa", r"""Le das a tu amiga una copia de la llave (la referencia). Si mueve los muebles, al volver los verás movidos; si usa su llave para otra casa, la tuya no cambia."""),
]),

S("recursividad", "5.7 Recursividad", "Guía de Python · 5.10", [
    ("idea", "Matrioskas", r"""Abres una y dentro hay otra igual pero más pequeña… hasta la diminuta que no se abre (**caso base**). Sin ella, nunca acabarías (`RecursionError`, ~1000 llamadas)."""),
    ("pasos", "Receta", r"""1) ¿Cuál es el caso más simple que sé resolver? (**caso base**). 2) Si supiera resolver n−1, ¿cómo resuelvo n? (**caso recursivo**). 3) Comprueba que cada llamada se acerca al caso base."""),
    ("py", "Factorial recursivo", 'def factorial(n):\n    if n == 0:                     # caso base\n        return 1\n    return n * factorial(n - 1)     # problema más pequeño\n\nprint(factorial(3), factorial(10))'),
]),

S("main", "5.8 main(), __name__ y sys.exit", "Guía de Python · 5.11", [
    ("py", "El patrón", 'def main():\n    print("Este es el inicio del programa.")\n\nif __name__ == "__main__":\n    main()'),
    ("def", "Por qué", r"""
`__name__` vale `"__main__"` si ejecutas el fichero y el nombre del módulo si otro lo importa: así `main()` solo corre al
lanzarlo. `sys.exit(codigo)` termina y devuelve un **código de salida** (0 = bien, otro = error; en WSL lo ves con
`echo $?`). *La app usa justo esto para probar tus funciones sin ejecutar tu main.*"""),
]),
])

T6 = Tema("py6", "Python", 6, "Estructuras de datos",
          "Secuencias y slicing, listas, tuplas, range, pilas y colas, comprensiones, del, conjuntos y diccionarios.", [

S("tipos", "6.1 Atómicos y estructurados", "Guía de Python · 6.1", [
    ("def", "Comparativa", r"""
| | ¿Ordenado? | ¿Mutable? | ¿Duplicados? | Se escribe |
|---|---|---|---|---|
| `str` | sí | no | sí | `"hola"` |
| `tuple` | sí | no | sí | `(1, 'a', 3.0)` |
| `range` | sí | no | — | `range(5)` |
| `list` | sí | **sí** | sí | `[1, 'a', 3.0]` |
| `set` | no | sí | **no** | `{1, 2, 3}` |
| `dict` | orden de inserción | sí | claves no | `{'pepe': '17/01'}` |"""),
    ("idea", "DNI, lista de la compra, cromos y agenda", r"""**Tupla** = el DNI (datos fijos). **Lista** = la lista de la compra (añades, tachas). **Conjunto** = la colección de cromos sin repetidos. **Diccionario** = la agenda del móvil (buscas por nombre, obtienes el teléfono)."""),
    ("ojo", "Mutables dentro de inmutables", r"""`t = ([1], 2); t[0].append(5)` funciona → `([1, 5], 2)`; lo que no puedes es `t[0] = [7]`."""),
]),

S("secuencias", "6.2 Secuencias: índices y slicing", "Guía de Python · 6.2", [
    ("py", "PYTHON", 's = "PYTHON"\nprint(s[0], s[-1])\nprint(s[1:4], s[:2], s[2:], s[-3:])\nprint(s[::2], s[::-1])\nprint(repr(s[4:1]), s[1:100])\nprint("th" in "python", [1, 2] + [3], "ab" * 2, len(s), min([3, 1, 2]))\nprint([1, 2, 1].index(1, 1), "banana".count("a"))'),
    ("idea", "Cortes entre letras", r"""
Los índices de un slice señalan los **huecos** entre letras: `|P|Y|T|H|O|N|` con huecos 0…6. `s[1:4]` corta en los huecos 1 y
4 → YTH. Por eso el fin no se incluye y `s[:2] + s[2:]` es siempre la cadena entera. Los slices no dan error si te pasas;
los índices sí (`IndexError`)."""),
]),

S("listas", "6.3 Listas a fondo", "Guía de Python · 6.3 y 6.6", [
    ("py", "Modificar trozos", "l = list(range(10))\nl[2:5] = ['a', 'b']\nprint(l)\nl = list(range(10)); del l[::2]\nprint(l)\nl = [1, 2, 3]; l.insert(1, 'z'); print(l, l.pop(), l.pop(0), l)\nl = [1, 2, 3, 2]; l.remove(2); print(l)"),
    ("py", "Métodos (ejemplo del tutorial)", "fruits = ['orange', 'apple', 'pear', 'banana', 'kiwi', 'apple', 'banana']\nprint(fruits.count('apple'), fruits.index('banana'), fruits.index('banana', 4))\nfruits.reverse(); print(fruits)\nfruits.append('grape'); fruits.sort(); print(fruits)\nprint(fruits.pop())"),
    ("ojo", "Los métodos que modifican devuelven None", r"""`l = l.sort()` te deja `l = None`. Usa `l.sort()` a secas o `nueva = sorted(l)`. Y no todo se ordena: `[None, 'hola', 10]` da TypeError."""),
    ("py", "Recorrer, pila y cola", "lista = [10, 20, 30]\nfor i, v in enumerate(lista):\n    print(i, v)\npila = [3, 4, 5]\npila.append(6); print(pila.pop(), pila)\nfrom collections import deque\ncola = deque(['Eric', 'John', 'Michael'])\ncola.append('Terry'); print(cola.popleft(), cola)"),
    ("idea", "Platos y cafetería", r"""**Pila** (LIFO) = torre de platos: `append` y `pop`. **Cola** (FIFO) = la cola de la cafetería: usa `deque` con `append` y `popleft` (en una lista, quitar del principio es lento)."""),
    ("py", "del", "a = [-1, 1, 66.25, 333, 333, 1234.5]\ndel a[0]; print(a)\ndel a[2:4]; print(a)\ndel a[:]; print(a)"),
]),

S("tuplas", "6.4 Tuplas y range", "Guía de Python · 6.4", [
    ("py", "La coma hace la tupla", "x = 3, 4, 5\nprint(x, type(x))\nuno = 3,\nprint(uno, type((3)))\nt = 12345, 54321, 'hello!'\na, b, c = t        # desempaquetado\nprint(a, c)\nprint(list(range(0, -10, -3)), range(5)[2], list(range(5, 1)))"),
    ("errata", "Diapositivas 04 · tuplas", r"""Pone «3, genera la tupla (3)»: genera **(3,)**. `(3)` sin coma es el entero 3."""),
    ("truco", "¿Tupla o lista?", r"""Tupla para **registros heterogéneos** (nombre, edad, nota) con desempaquetado; lista para **muchos datos del mismo tipo** que recorres con bucles."""),
]),

S("cadenas", "6.5 Cadenas: métodos y formato", "Guía de Python · 6.5", [
    ("py", "Métodos útiles", 'print("hola mundo".find("mundo"), "hola".find("z"))\nprint("-".join(["2026", "10", "22"]))\nprint("banana".replace("a", "o", 2))\nprint("a,b,,c".split(","), "  x  ".strip(), "Hola".upper())\nprint("hola".startswith("ho"), "123".isdigit(), "-5".isdigit())'),
    ("py", "Formatear", 'nombre = "Ana"\nprint("Nombre: {}, edad: {}".format("Ana", 20))\nprint("{1} {0}".format("a", "b"), "{:.3f}".format(3.14159))\nprint(f"Hola {nombre}, 2+3={2+3}, pi={3.14159:.2f}")'),
    ("ojo", "Las cadenas no cambian", r"""`t.upper()` no cambia `t`: te da una **fotocopia**. Si no la guardas (`t = t.upper()`), se pierde."""),
]),

S("comprension", "6.6 Comprensiones", "Guía de Python · 6.8", [
    ("def", "Estructura", r"""`[expresión for variable in iterable if condición]` — «dame *expresión* para cada *variable* de *iterable* que cumpla *condición*». Los `for` e `if` van en el mismo orden que con bucles."""),
    ("py", "Ejemplos del tutorial", "vec = [-4, -2, 0, 2, 4]\nprint([x*2 for x in vec], [x for x in vec if x >= 0], [abs(x) for x in vec])\nprint([(x, x**2) for x in range(6)])\nvec = [[1,2,3], [4,5,6], [7,8,9]]\nprint([num for elem in vec for num in elem])\nprint([(x, y) for x in [1,2,3] for y in [3,1,4] if x != y])"),
    ("py", "Trasponer una matriz", "matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]\nprint([[row[i] for row in matrix] for i in range(4)])\nprint(list(zip(*matrix)))\nx = [1, 2, 3]\nprint([0, *x, 4])"),
    ("errata", "docs.python.org · 5.1.5", r"""`[*element for element in x]` solo funciona en versiones posteriores a la 3.13; en 3.13 da SyntaxError. Usa `[n for e in x for n in e]`."""),
]),

S("conjuntos", "6.7 Conjuntos", "Guía de Python · 6.9", [
    ("py", "Operaciones", "basket = {'apple', 'orange', 'apple', 'pear', 'orange', 'banana'}\nprint(sorted(basket), 'orange' in basket)\na = set('abracadabra'); b = set('alacazam')\nprint(sorted(a - b), sorted(a | b))\nprint(sorted(a & b), sorted(a ^ b))\nprint({x for x in 'abracadabra' if x not in 'abc'})\nprint(type({}), type(set()))"),
    ("ojo", "{} no es un conjunto vacío", r"""`{}` es un **diccionario** vacío: el conjunto vacío es `set()`. Los conjuntos no tienen orden ni índices (`basket[0]` da error)."""),
    ("errata", "Diapositivas 04 · conjuntos", r"""«1,2,3,1 creará el conjunto 2,1,3» sin llaves: es `{1, 2, 3, 1}` → `{1, 2, 3}`. Y «A los elementos de un conjunto se accede por su clave» se refería a los **diccionarios**."""),
]),

S("dict", "6.8 Diccionarios y técnicas de bucles", "Guía de Python · 6.10–6.13", [
    ("py", "Operaciones", "tel = {'jack': 4098, 'sape': 4139}\ntel['guido'] = 4127\nprint(tel['jack'], tel.get('irv'), tel.get('irv', 0))\ndel tel['sape']\nprint(list(tel), sorted(tel), 'guido' in tel)\nodds = {i: i**2 for i in (1, 3, 5)}; evens = {i: i**2 for i in (2, 4, 6)}\nprint({**odds, **evens})"),
    ("py", "Contar apariciones (patrón clásico)", 'texto = "hola mundo"\ncuenta = {}\nfor letra in texto:\n    cuenta[letra] = cuenta.get(letra, 0) + 1\nprint(cuenta)'),
    ("def", "Recorrer", r"""
`for k in d` (claves) · `for v in d.values()` · `for k, v in d.items()` · `for i, v in enumerate(s)` · `for a, b in zip(s1, s2)`
· `for x in reversed(s)` · `for x in sorted(s)` · `for x in sorted(set(s))` (sin repetir y en orden).
**No modifiques una lista mientras la recorres**: crea una nueva."""),
    ("py", "Comparar secuencias", "print((1, 2, 3) < (1, 2, 4), 'ABC' < 'C' < 'Pascal' < 'Python')\nprint((1, 2) < (1, 2, -1), (1, 2, 3) == (1.0, 2.0, 3.0))"),
    ("truco", "El operador morsa", r"""En Python no se asigna dentro de una expresión con `=` (evita el error de C). Si lo necesitas: `while (linea := input()) != "":`."""),
]),
])

T7 = Tema("py7", "Python", 7, "Chuleta de tipos y métodos (+ erratas)",
          "Tu chuleta rosa en una página: tipos, conversiones, métodos de str y list, split/join y erratas corregidas.", [

S("chuleta", "7.1 Chuleta de Python: tipos y métodos", "Chuleta «Python: tipos y métodos»", [
    ("resumen", "Los 5 tipos básicos", r"""
`int` (4, −5) · `float` (3.14, **¡punto, no coma!**) · `str` ("hola", "4") · `bool` (True, False) · `list` ([4, "a", True]).
⚠️ `4` y `"4"` no son lo mismo: uno es un número y el otro un 4 escrito en un papel. ¿Dudas? `type(x)`."""),
    ("py", "Convertir", 'print(int("-5"), int(3.9), float("2.5"), str(42), list("hola"))\ntry:\n    int("hola")\nexcept ValueError as e:\n    print("❌", e)'),
    ("idea", "¿Qué es el punto?", r"""Cada tipo tiene sus **habilidades** (métodos), como un perro sabe ladrar y un gato maullar: `cosa.metodo()`. Un método de texto no funciona con una lista, y al revés."""),
    ("ojo", "¿Cambia o no cambia?", r"""
📄 **Textos: NO cambian** (te dan una fotocopia): `t = t.upper()` ✅ · `t.upper()` ❌ (t sigue igual).
🛒 **Listas: SÍ cambian solas**: `l.append(4)` ✅ · `l = l.append(4)` ❌ (l pasa a ser None)."""),
    ("def", "Métodos de str y de list", r"""
| str | | list | |
|---|---|---|---|
| `.upper()` / `.lower()` | mayúsculas / minúsculas | `.append(x)` | añade al final 🛒 |
| `.strip()` | quita blancos de los bordes | `.insert(i, x)` | mete x en la posición i |
| `.replace(a, b)` | cambia a por b | `.remove(x)` | quita el primer x (un valor) |
| `.count(x)` | cuántas veces | `.pop()` / `.pop(i)` | quita y te da el último / el i |
| `.find(x)` | posición (−1 si no está) | `.sort()` / `.reverse()` | ordena / da la vuelta |
| `.startswith(x)` | ¿empieza por x? | `.count(x)` / `.index(x)` | cuántas / dónde |
| `.isdigit()` / `.isalpha()` | ¿cifras? (⚠️ "-5" da False) / ¿letras? | `x in lista` | ¿está? (también en textos) |"""),
    ("py", "split y join (la barra de chocolate 🍫)", 'print("4 -5 7".split(), "a,b,c".split(","))\nprint("-".join(["a", "b"]))\ntrozos = "4 -5 7".split()\nnums = []\ni = 0\nwhile i < len(trozos):\n    nums.append(int(trozos[i]))    # ¡los trozos siguen siendo texto!\n    i = i + 1\nprint(nums)'),
    ("truco", "Funciones generales (tijeras ✂️)", r"""`print`, `input` (**siempre da texto**), `len`, `type`, `max` / `min` / `sum`, `range(a, b)` (de a hasta b−1). ¿Dudas? `dir("")`, `dir([])`, `help(str.split)`."""),
]),

S("erratas", "7.2 Erratas corregidas del material de Python", "Guía de Python · 9", [
    ("errata", "Lo que estaba mal", r"""
| Dónde | Pone | Correcto |
|---|---|---|
| 03 Funciones · por defecto | se define `son_iguales` y se llama `sonIguales` | el nombre debe coincidir |
| 03 Funciones · nonlocal | «local de gy» dentro de `sy()` | la función es `sy` |
| 04 Estructuras · tuplas | «3, genera la tupla (3)» | genera `(3,)` |
| 04 Estructuras · conjuntos | «1,2,3,1 creará el conjunto 2,1,3» | `{1, 2, 3, 1}` → `{1, 2, 3}` |
| 04 Estructuras · comprensiones | sin llaves | `{x for x in …}` y `{x: x**2 for x in (2,4,6)}` |
| 04 Estructuras · diccionarios | «a los elementos de un conjunto se accede por su clave» | de un **diccionario** |
| 04 Estructuras · cadenas | «”. y esperar» | escribir `"".` y pulsar Tab |
| 02 Sentencias · for/while | comentarios con `//` | en Python es `#` (`//` es la división entera) |
| 02 Sentencias · if anidados | líneas acabadas en `;` | no hacen falta |
| 01 Introducción | `x = x + 1;` · vacíos `”,(),[],, set()` · `inf` como literal | `x = x + 1` · `'', (), [], {}, set(), range(0)` · `float('inf')` |
| Cuaderno 03 · notas | negativa da «Suspenso» | comprobar primero 0 ≤ nota ≤ 10 |
| Cuaderno 03 · sumas | `sum = 0` | mejor `suma` (no tapar `sum()`) |
| Cuaderno 02 · cadenas | `print("c:\home\nombreusuario")` | `r"c:\home\nombreusuario"` o `\\` |
| Hoja de funciones | `F = 95 C + 32` | `F = (9/5)·C + 32` |
| docs.python.org 5.1.5 | `[*element for element in x]` | solo > 3.13; usa `[n for e in x for n in e]` |"""),
]),
])

TEMAS = [T1, T2, T3, T4, T5, T6, T7]
