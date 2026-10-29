from contenido.base import Ejercicio, Hoja, Prueba, Programa, Respuesta

P = Prueba
PY = "python"
R = Respuesta


def py(s):
    return "\n```python\n" + s.strip("\n") + "\n```\n"


# =========================================================================== condicionales y bucles
S1 = '''
numero = float(input("Ingrese un número: "))
if numero > 0:
    print("El número es positivo.")
elif numero < 0:
    print("El número es negativo.")
else:
    print("El número es cero.")
'''
S2 = '''
a = float(input("Ingrese el primer número: "))
b = float(input("Ingrese el segundo número: "))
c = float(input("Ingrese el tercer número: "))
mayor = a
if b > mayor:
    mayor = b
if c > mayor:
    mayor = c
print("El número mayor es:", mayor)       # o simplemente max(a, b, c)
'''
S3 = '''
n = int(input("Ingrese un número entero: "))
if n % 2 == 0:
    print("El número es par.")
else:
    print("El número es impar.")
'''
S4 = '''
import random
secreto = random.randint(1, 10)      # entero aleatorio entre 1 y 10, ambos incluidos
intento = int(input("Adivina el número (1-10): "))
while intento != secreto:
    if intento < secreto:
        print("El número es mayor.")
    else:
        print("El número es menor.")
    intento = int(input("Prueba otra vez: "))
print("¡Correcto! Era el", secreto)
'''
S5 = '''
for n in range(2, 21, 2):
    print(n, end=" ")
print()
'''
S6 = '''
suma, i = 0, 1
while i <= 100:
    suma += i
    i += 1
print("La suma de los números del 1 al 100 es:", suma)
'''
S7 = '''
negativos = 0
for i in range(1, 6):
    n = float(input(f"Ingrese el número {i}: "))
    if n < 0:
        negativos += 1
print("Cantidad de números negativos:", negativos)
'''
S8 = '''
n = int(input("Ingrese un número entero positivo: "))
factorial, i = 1, n
while i > 1:
    factorial *= i
    i -= 1
print(f"El factorial de {n} es: {factorial}")
'''
S9 = '''
lista = [2, 5, 10]
for n in lista:
    print(n * 2, end=" ")
print()
'''
S10 = '''
cadena = input("Ingrese una cadena: ")
vocales = 0
for c in cadena.lower():           # lower() para contar también A, E…
    if c in "aeiouáéíóú":
        vocales += 1
print("Cantidad de vocales:", vocales)
'''
S11 = '''
import statistics
texto = input("Ingrese una lista de números separados por comas: ")
numeros = [int(x) for x in texto.split(",")]   # "1, 2, 2" → [1, 2, 2]
print("Media:", float(statistics.mean(numeros)))
print("Moda:", statistics.mode(numeros))
print("Mediana:", statistics.median(numeros))
'''

# =========================================================================== funciones
F1 = '''
def calcular_cuadrado(x):
    return x * x

n = float(input("Ingrese un número: "))
print(f"El cuadrado de {n:g} es: {calcular_cuadrado(n):g}")
'''
F2 = '''
import math

def area_circulo(radio):
    return math.pi * radio ** 2

r = float(input("Ingrese el radio del círculo: "))
print(f"El área del círculo es: {area_circulo(r):.2f}")
'''
F3 = '''
def es_primo(n):
    """True si n es primo, False si no."""
    if n < 2:                 # 0 y 1 no son primos
        return False
    d = 2
    while d * d <= n:         # basta probar hasta la raíz cuadrada de n
        if n % d == 0:
            return False      # encontrado un divisor: no es primo
        d += 1
    return True               # ningún divisor: es primo

n = int(input("Ingrese un número: "))
print(f"El número {n} es primo: {es_primo(n)}")
'''
F4 = '''
def celsius_a_fahrenheit(c):
    return 9 / 5 * c + 32             # F = (9/5)·C + 32

c = float(input("Ingrese la temperatura en grados Celsius: "))
print("La temperatura en grados Fahrenheit es:", celsius_a_fahrenheit(c))
'''
F5 = '''
def calcular_mcd(a, b):
    while b != 0:
        a, b = b, a % b         # mcd(a, b) = mcd(b, a % b)
    return a

a = int(input("Primer número: "))
b = int(input("Segundo número: "))
print("El MCD es:", calcular_mcd(a, b))
'''
F6 = '''
def calcular_tiempo(distancia, velocidad):
    return distancia / velocidad              # horas

def calcular_consumo(distancia, rendimiento):
    return distancia / rendimiento            # litros

def calcular_costo(consumo, precio_litro):
    return consumo * precio_litro             # euros

def main():
    distancia = float(input("Ingrese la distancia en kilómetros: "))
    velocidad = float(input("Ingrese la velocidad media en km/h: "))
    rendimiento = float(input("Ingrese el rendimiento del vehículo en km por litro: "))
    precio = float(input("Ingrese el precio del combustible por litro: "))
    tiempo = calcular_tiempo(distancia, velocidad)
    costo = calcular_costo(calcular_consumo(distancia, rendimiento), precio)
    print(f"El tiempo estimado de viaje es: {tiempo} horas")
    print(f"El costo total de combustible es: {costo:.2f}")

if __name__ == "__main__":
    main()
'''

# =========================================================================== programas con estructuras de datos
D1 = '''
def suma_cuadrados(n):
    """Devuelve 1² + 2² + ... + n² de forma recursiva."""
    if n == 0:                              # caso base
        return 0
    return n ** 2 + suma_cuadrados(n - 1)    # caso recursivo

def main():
    n = int(input("Introduce un entero positivo: "))
    print("La suma de los", n, "primeros cuadrados es", suma_cuadrados(n))

if __name__ == "__main__":
    main()
'''
D2 = '''
def divisores_propios(n):
    """Lista de divisores de n menores que n."""
    divisores = []
    for d in range(1, n):
        if n % d == 0:
            divisores.append(d)
    return divisores

# la misma idea con una comprensión:
# def divisores_propios(n):
#     return [d for d in range(1, n) if n % d == 0]

if __name__ == "__main__":
    n = int(input("Número: "))
    print(divisores_propios(n))
'''
D3 = F3
D4 = '''
def divisores_propios(n):
    return [d for d in range(1, n) if n % d == 0]

def suma_divisores(n):
    return sum(divisores_propios(n))

def parejas_amigos(limite):
    """Lista de tuplas (a, b) de números amigos con a < b <= limite."""
    parejas = []
    for a in range(2, limite + 1):
        b = suma_divisores(a)
        if a < b <= limite and suma_divisores(b) == a:
            parejas.append((a, b))
    return parejas

def main():
    limite = int(input("Introduce un número natural: "))
    for a, b in parejas_amigos(limite):
        print(a, "y", b, "son amigos")

if __name__ == "__main__":
    main()
'''
D5 = '''
def a_romano(n):
    """Convierte un entero 1 <= n < 4000 a número romano."""
    valores = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
               (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
               (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    resultado = ""
    for valor, letras in valores:      # desempaquetado de cada tupla
        while n >= valor:
            resultado += letras
            n -= valor
    return resultado

def main():
    n = int(input("Número decimal (1-3999): "))
    if 1 <= n < 4000:
        print(a_romano(n))
    else:
        print("El número debe estar entre 1 y 3999")

if __name__ == "__main__":
    main()
'''

HOJA_CONTROL = Hoja("py-control", "Condicionales y bucles", "py", "Guía «Programación en Python» · hoja de repaso",
                    "Los 11 ejercicios de la hoja de repaso de sentencias de control, resueltos y con corrección.", [

Ejercicio("py-c1", "Positivo, negativo o cero", "Pide un número y di si es positivo, negativo o cero.",
"Tres casos excluyentes → `if` / `elif` / `else`. `float(input())` para admitir decimales." + py(S1),
programa=Programa(PY, [P("5", "positivo", descripcion="5"), P("-2.5", "negativo", descripcion="−2,5"), P("0", "cero", descripcion="0")],
                  solucion=S1), tema="Condicionales"),

Ejercicio("py-c2", "El mayor de tres números", "Pide tres números y muestra el mayor.",
"Patrón del **máximo provisional**: supongo que el mayor es el primero y lo cambio si encuentro uno mayor. "
"(En Python también vale `max(a, b, c)`.) Con `float`, 12 se imprime como `12.0`; con `int()`, como `12`." + py(S2),
programa=Programa(PY, [P("3\n9\n4", "9", descripcion="3 9 4"), P("-1\n-7\n-3", "-1", descripcion="negativos"),
                       P("5\n5\n2", "5", descripcion="empate")], solucion=S2), tema="Condicionales"),

Ejercicio("py-c3", "Par o impar", "Pide un número entero y di si es par o impar.",
"`n % 2` es el resto de dividir entre 2: 0 → par. En Python `-3 % 2` vale 1 (el resto tiene el signo del divisor), así que "
"también funciona con negativos." + py(S3),
programa=Programa(PY, [P("8", "par", descripcion="8"), P("7", "impar", descripcion="7"), P("-3", "impar", descripcion="−3")],
                  solucion=S3), tema="Condicionales"),

Ejercicio("py-c4", "Adivinar el número (while)", "El programa elige un número aleatorio entre 1 y 10 y el usuario lo intenta "
"adivinar; tras cada fallo se le dice si es mayor o menor.\n\n*En la app:* se prueban los números del 1 al 10 en orden: "
"tu programa debe acabar diciendo «Correcto».",
"`random.randint(1, 10)` incluye los dos extremos. El `while` se repite **mientras no acierte**; se lee un intento antes "
"del bucle y otro al final de cada vuelta." + py(S4),
programa=Programa(PY, [P("\n".join(map(str, range(1, 11))), "correcto", descripcion="intentos 1, 2, …, 10"),
                       P("\n".join(map(str, range(1, 11))), "correcto", descripcion="otra partida")], solucion=S4),
tema="Bucles"),

Ejercicio("py-c5", "Pares del 1 al 20 (for)", "Muestra los números pares del 1 al 20 con un `for`.",
"`range(inicio, fin, paso)` no incluye el fin: `range(2, 21, 2)` → 2, 4, …, 20. `end=\" \"` evita el salto de línea." + py(S5),
programa=Programa(PY, [P("", "2 4 6 8 10 12 14 16 18 20", descripcion="2 … 20")], solucion=S5), tema="Bucles"),

Ejercicio("py-c6", "Sumar del 1 al 100 (while)", "Suma los números del 1 al 100 con un `while`.",
"Acumulador (`suma = 0`, `suma += i`) y contador (`i += 1`). ¡Sin el `i += 1` el bucle no acaba nunca! "
"Resultado: 100·101/2 = **5050**. (Evita llamar `sum` a la variable: taparías la función `sum()`.)" + py(S6),
programa=Programa(PY, [P("", "5050", descripcion="5050")], solucion=S6), tema="Bucles"),

Ejercicio("py-c7", "Contar negativos entre 5 números", "Pide 5 números y cuenta cuántos son negativos.",
"Patrón **contador**: `negativos = 0` y `+= 1` cuando se cumple la condición. `f\"…{i}…\"` mete el valor de i en el texto." + py(S7),
programa=Programa(PY, [P("-5\n3\n-2\n0\n8", "2", descripcion="−5 3 −2 0 8"), P("1\n2\n3\n4\n5", "0", descripcion="ninguno"),
                       P("-1\n-1\n-1\n-1\n-1", "5", descripcion="todos")], solucion=S7), tema="Bucles"),

Ejercicio("py-c8", "Factorial con while", "Pide un entero positivo y calcula su factorial con `while`.",
"$n! = n\\cdot(n-1)\\cdots2\\cdot1$. Patrón **producto**: empieza en 1 (no en 0). Con 0 el bucle no entra y da 1, que es "
"correcto (0! = 1). Los `int` de Python no tienen límite: 30! sale exacto." + py(S8),
programa=Programa(PY, [P("5", "5 120", descripcion="5! = 120"), P("0", "0 1", descripcion="0! = 1"),
                       P("20", "20 2432902008176640000", descripcion="20!")], solucion=S8), tema="Bucles"),

Ejercicio("py-c9", "Multiplicar por 2 cada número de una lista", "Dada la lista `[2, 5, 10]`, muestra cada número multiplicado por 2.",
"`for n in lista` recorre los **elementos** directamente (no hace falta índice). Con comprensión: `[n * 2 for n in lista]`." + py(S9),
programa=Programa(PY, [P("", "4 10 20", descripcion="[2, 5, 10]")], solucion=S9), tema="Bucles"),

Ejercicio("py-c10", "Contar vocales", "Pide una cadena y cuenta sus vocales.",
"Se recorre la cadena carácter a carácter; `c in \"aeiou…\"` pregunta si está en la cadena de vocales; `lower()` para contar "
"también las mayúsculas." + py(S10),
programa=Programa(PY, [P("Hola Mundo", "4", descripcion="«Hola Mundo»"), P("AEIOU", "5", descripcion="mayúsculas"),
                       P("canción", "3", descripcion="con tilde")], solucion=S10), tema="Bucles"),

Ejercicio("py-c11", "Media, moda y mediana", "Pide una lista de números separados por comas y muestra su media, moda y mediana.",
"`split(\",\")` corta la cadena por las comas e `int()` ignora los espacios. **Media** = suma / cantidad; **moda** = el que "
"más se repite; **mediana** = el central una vez ordenados (con cantidad par, la media de los dos centrales). El módulo "
"`statistics` lo hace todo." + py(S11),
programa=Programa(PY, [P("1, 2, 2, 5, 10", "4.0 2 2", descripcion="1, 2, 2, 5, 10"),
                       P("3,3,3", "3.0 3 3", descripcion="3, 3, 3")], solucion=S11), tema="Estructuras de datos"),
], icono="🔁")

HOJA_FUNC = Hoja("py-funciones", "Funciones", "py", "Guía «Programación en Python» · hoja de ejercicios de funciones",
                 "Las 6 funciones de la hoja, resueltas; la app prueba tus funciones directamente.", [

Ejercicio("py-f1", "calcular_cuadrado", "Escribe `calcular_cuadrado(x)` y un programa que pida un número y muestre su cuadrado.",
"Una función recibe parámetros y **devuelve** (`return`) un resultado; no imprime. El `:g` del f-string quita el `.0` sobrante." + py(F1),
programa=Programa(PY, [P("5", "5 25", descripcion="programa con 5"),
                       P(main="print(calcular_cuadrado(3), calcular_cuadrado(-4), calcular_cuadrado(0.5))", salida="9 16 0.25",
                         descripcion="la función con 3, −4 y 0,5")], solucion=F1), tema="Funciones"),

Ejercicio("py-f2", "area_circulo", "Escribe `area_circulo(radio)` y un programa que muestre el área con dos decimales.",
"$A = \\pi r^2$ con `math.pi`; `**` es la potencia. `:.2f` redondea a 2 decimales **al imprimir** (el valor sigue completo)." + py(F2),
programa=Programa(PY, [P("3", "28.27", descripcion="radio 3"),
                       P(main="print(round(area_circulo(1), 5), round(area_circulo(2), 5))", salida="3.14159 12.56637",
                         descripcion="la función con 1 y 2")], solucion=F2), tema="Funciones"),

Ejercicio("py-f3", "es_primo", "Escribe una función que diga si un número natural es primo.",
"Primo = mayor que 1 y sin más divisores que 1 y él mismo. **Basta probar hasta $\\sqrt n$**: si n = a·b y los dos fueran "
"mayores que √n, el producto sería mayor que n. Por eso el bucle es `while d * d <= n`." + py(F3),
programa=Programa(PY, [P("7", "true", descripcion="7"), P("1", "false", descripcion="1"),
                       P(main="print([p for p in range(30) if es_primo(p)])", salida="2 3 5 7 11 13 17 19 23 29",
                         descripcion="primos menores que 30"),
                       P(main="print(es_primo(97), es_primo(91), es_primo(2), es_primo(0))", salida="true false true false",
                         descripcion="97, 91 = 7·13, 2 y 0")], solucion=F3), tema="Funciones"),

Ejercicio("py-f4", "celsius_a_fahrenheit", "Escribe `celsius_a_fahrenheit(c)` y un programa que la use.",
"$F = \\tfrac95 C + 32$. (En la hoja original salió «F = 95 C + 32» porque se perdió la fracción al copiar.)" + py(F4),
errata="En la hoja pone «F = 95 C + 32»: es F = (9/5)·C + 32.",
programa=Programa(PY, [P("25", "77.0", descripcion="25 °C"), P("-40", "-40.0", descripcion="−40 °C"),
                       P(main="print(celsius_a_fahrenheit(100), celsius_a_fahrenheit(0))", salida="212.0 32.0",
                         descripcion="la función con 100 y 0")], solucion=F4), tema="Funciones"),

Ejercicio("py-f5", "calcular_mcd (Euclides)", "Escribe `calcular_mcd(a, b)` con el algoritmo de Euclides.",
"**Euclides:** mcd(a, b) = mcd(b, a mod b), y cuando el resto es 0 el otro número es el MCD. Traza con 56 y 98: "
"(56, 98) → (98, 56) → (56, 42) → (42, 14) → (14, 0) → **14**. La asignación múltiple `a, b = b, a % b` hace el cambio "
"sin variable auxiliar." + py(F5),
programa=Programa(PY, [P("56\n98", "14", descripcion="56 y 98"),
                       P(main="print(calcular_mcd(56, 98), calcular_mcd(17, 5), calcular_mcd(12, 0), calcular_mcd(100, 75))",
                         salida="14 1 12 25", descripcion="varios pares")], solucion=F5), tema="Funciones"),

Ejercicio("py-f6", "Tiempo de viaje y coste de combustible", "Escribe `calcular_tiempo`, `calcular_consumo` y `calcular_costo` y un "
"`main` que pida distancia, velocidad, rendimiento (km por litro) y precio del litro y muestre el tiempo y el coste.",
"Cada función hace **una sola cosa** (alta cohesión) y `main` las combina. `if __name__ == \"__main__\":` hace que `main()` "
"solo se ejecute al lanzar el archivo (no al importarlo)." + py(F6),
programa=Programa(PY, [P("200\n80\n15\n1.50", "2.5 20.00", descripcion="200 km, 80 km/h, 15 km/l, 1,50 €/l"),
                       P(main="print(calcular_tiempo(300, 100), calcular_consumo(300, 20), calcular_costo(15, 2))",
                         salida="3.0 15.0 30", descripcion="las tres funciones por separado")], solucion=F6), tema="Funciones"),

Ejercicio("py-adivina", "Adivina el resultado", r"""¿Qué devuelve cada expresión? `2+3` · `2.0 + 3` · `0x2 + 0x3` ·
`"2" + '3'` · `2 and 3` · `2 or 3` · `2 & 3`""",
r"""| Expresión | Resultado | Por qué |
|---|---|---|
| `2+3` | 5 | suma de enteros |
| `2.0 + 3` | 5.0 | int + float → float |
| `0x2 + 0x3` | 5 | enteros escritos en hexadecimal; se muestran en decimal |
| `"2" + '3'` | '23' | con cadenas, `+` concatena |
| `2 and 3` | 3 | `and` devuelve el primer falso o, si todos son verdaderos, el último |
| `2 or 3` | 2 | `or` devuelve el primer verdadero |
| `2 & 3` | 2 | AND bit a bit: 10 & 11 = 10 |""",
respuestas=[R("2.0 + 3", 5.0), R('"2" + \'3\'', ["23", "'23'", '"23"'], "texto"), R("2 and 3", 3), R("2 or 3", 2), R("2 & 3", 2)],
tema="Tipos"),
], icono="🧩")

HOJA_PROG = Hoja("py-programas", "Programas con estructuras de datos", "py", "Guía «Programación en Python» · semana 6",
                 "Suma de cuadrados recursiva, divisores, primos, números amigos y números romanos.", [

Ejercicio("py-d1", "Suma de los n primeros cuadrados (recursiva)", "Lee n y devuelve 1² + 2² + … + n² de forma **recursiva**.",
"**Receta recursiva:** caso base (n = 0 → 0) y caso recursivo (la suma hasta n es n² más la suma hasta n − 1).\n\n"
"Traza n = 3: 9 + (4 + (1 + 0)) = **14**. Comprobación con la fórmula n(n+1)(2n+1)/6 = 3·4·7/6 = 14 ✓." + py(D1),
programa=Programa(PY, [P("3", "3 14", descripcion="n = 3"), P("10", "10 385", descripcion="n = 10"),
                       P(main="print(suma_cuadrados(0), suma_cuadrados(1), suma_cuadrados(100))", salida="0 1 338350",
                         descripcion="la función con 0, 1 y 100")], solucion=D1), tema="Recursividad"),

Ejercicio("py-d2", "Divisores propios", "Programa una función que calcule los divisores propios de un número natural (todos salvo él mismo).",
"d es divisor de n si `n % d == 0`. Se prueban todos los d de 1 a n − 1. Mejora: ninguno es mayor que n/2, así que basta "
"`range(1, n // 2 + 1)` (para n ≥ 2)." + py(D2),
programa=Programa(PY, [P(main="print(divisores_propios(12), divisores_propios(7), divisores_propios(1))",
                         salida="1 2 3 4 6 1", descripcion="12, 7 y 1 (lista vacía)"),
                       P(main="print(sum(divisores_propios(28)))", salida="28", descripcion="28 es perfecto")],
                  solucion=D2), tema="Listas"),

Ejercicio("py-d3", "¿Es primo?", "Escribe una función que diga si un número natural es primo (igual que en la hoja de funciones).",
"Ver el ejercicio *es_primo*. Versión sencilla pero lenta: `return n > 1 and divisores_propios(n) == [1]`." + py(D3),
programa=Programa(PY, [P(main="print([p for p in range(50) if es_primo(p)])", salida="2 3 5 7 11 13 17 19 23 29 31 37 41 43 47",
                         descripcion="primos menores que 50")], solucion=D3), tema="Funciones"),

Ejercicio("py-d4", "Números amigos", "Toma un número natural y muestra todas las parejas de números amigos hasta él. Dos números "
"son amigos si cada uno es la suma de los divisores propios del otro.",
"Ejemplo: divisores de 220 suman 284 y los de 284 suman 220. Para cada a, b = suma de divisores de a; si la suma de "
"divisores de b vuelve a ser a, son amigos. Se pide **a < b** para no repetir la pareja y descartar los perfectos "
"(6 = 1 + 2 + 3 sería «amigo de sí mismo»). Reutiliza funciones: cada una hace una cosa." + py(D4),
programa=Programa(PY, [P("1500", "220 y 284 son amigos\n1184 y 1210 son amigos", modo="tokens", descripcion="hasta 1500"),
                       P("100", "", descripcion="hasta 100 (ninguna)",
                         verificar=lambda s: [] if "amig" not in s.lower() else ["hasta 100 no hay números amigos"])],
                  solucion=D4), tema="Listas"),

Ejercicio("py-d5", "De decimal a romano", "Transforma un número decimal menor que 4000 a números romanos.",
"Lista de pares (valor, letras) de mayor a menor, **incluyendo los casos de resta** (900 = CM, 400 = CD, 90 = XC, 40 = XL, "
"9 = IX, 4 = IV). Mientras el número sea ≥ que el valor, se añaden las letras y se resta: como pagar con el menor número de "
"billetes.\n\n| Paso (1994) | Se añade | Queda |\n|---|---|---|\n| 1994 ≥ 1000 | M | 994 |\n| 994 ≥ 900 | CM | 94 |\n"
"| 94 ≥ 90 | XC | 4 |\n| 4 ≥ 4 | IV | 0 |\n\n→ **MCMXCIV**." + py(D5),
programa=Programa(PY, [P("1994", "MCMXCIV", modo="texto", descripcion="1994"), P("3999", "MMMCMXCIX", modo="texto", descripcion="3999"),
                       P(main="print(a_romano(4), a_romano(2026), a_romano(49))", salida="IV MMXXVI XLIX", modo="texto",
                         descripcion="4, 2026 y 49")], solucion=D5), tema="Tuplas"),
], icono="📚")
