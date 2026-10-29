"""Teoría de C (guía «Programar en C desde cero» y chuleta de C)."""
from ui.teoria import Tema, S

HOLA = r"""#include <stdio.h>

int main(void)
{
    printf("Hola, mundo!\n");
    return 0;
}"""

T1 = Tema("c1", "C", 1, "Introducción y diseño de algoritmos",
          "Tu primer programa, compilar con gcc, leer los errores y pensar antes de programar.", [

S("primero", "1.1 Tu primer programa", "Guía de C · cap. 1", [
    ("c", "Hola mundo", HOLA),
    ("def", "Línea por línea", r"""
- `#include <stdio.h>` trae la librería de entrada/salida (`printf`, `scanf`).
- `int main(void)` es donde empieza todo programa; se ejecuta lo que hay entre `{ }`, de arriba abajo.
- `printf("...")` escribe; `\n` es un salto de línea. `return 0;` = «terminó bien».
- **Cada instrucción acaba en `;`** (olvidarlo es el error número 1). Comentarios: `// …` y `/* … */`."""),
    ("def", "Compilar y ejecutar (VS Code / WSL / Ubuntu)", r"""
```bash
gcc -Wall hola.c -o hola      # compila (con avisos) y crea el ejecutable «hola»
./hola                        # lo ejecuta
gcc -Wall prog.c -o prog -lm  # si usas math.h (sqrt, pow…)
```
**C es compilado**: el compilador traduce todo el programa a código máquina antes de ejecutarlo (en Python, el intérprete
va línea a línea)."""),
    ("ojo", "Errores de principiante", r"""
Falta un `;` o una `}` · escribir `Printf` (C distingue mayúsculas) · olvidar `#include <stdio.h>`.
**Lee el primer error del compilador**: dice archivo, línea y qué pasa; los demás suelen ser consecuencia de ese."""),
]),

S("algoritmos", "1.2 Diseñar el algoritmo", "Guía de C · cap. 2", [
    ("pasos", "Receta para diseñar un programa", r"""
1. **Entender** el problema: ¿qué datos entran? ¿qué tiene que salir?
2. **Pensar los pasos** en tu idioma (pseudocódigo).
3. **Traducir a C**.
4. **Probar** con varios casos (normales y raros: 0, negativos…)."""),
    ("ej", "Adivina el número en pseudocódigo", r"""
```
1. Elegir un número secreto
2. Repetir:
     Pedir un número
     Si es menor que el secreto → «más alto»; si es mayor → «más bajo»
   hasta que acierte
3. Escribir «¡Acertaste!»
```
Todo algoritmo se construye con **secuencia**, **selección** e **iteración**. En los diagramas de flujo: óvalo = inicio/fin,
rectángulo = acción, rombo = pregunta, paralelogramo = entrada/salida."""),
]),
])

T2 = Tema("c2", "C", 2, "Tipos, operadores y entrada/salida",
          "int, double, char…, la división entera, = frente a ==, printf y las reglas de oro del scanf.", [

S("tipos", "2.1 Tipos de datos y variables", "Guía de C · cap. 3 · Chuleta 2", [
    ("idea", "Un tarro con etiqueta", r"""Una variable es un tarro con etiqueta. En C tienes que decir **qué cabe en el tarro** (el tipo) antes de usarlo, y no puedes meter otra cosa."""),
    ("def", "Tipos", r"""
| Tipo | Guarda | Ejemplo | printf | scanf |
|---|---|---|---|---|
| `int` | entero | `int edad = 19;` | `%d` | `%d` |
| `float` | decimal (menos preciso) | `float x = 2.5f;` | `%f` | `%f` |
| `double` | decimal (más preciso, el normal) | `double pi = 3.1416;` | `%f` / `%.2f` | **`%lf`** ⚠️ |
| `char` | un carácter | `char letra = 'a';` | `%c` | **`" %c"`** ⚠️ |
| `char[]` | texto | `char nom[20];` | `%s` | `%s` (sin `&`) |
| `long long` | enteros grandes | `long long n = 10000000000LL;` | `%lld` | `%lld` |"""),
    ("c", "Tamaños y desbordamiento", r"""#include <stdio.h>
#include <limits.h>

int main(void)
{
    printf("int ocupa %zu bytes\n", sizeof(int));
    printf("double ocupa %zu bytes\n", sizeof(double));
    printf("El int mas grande: %d\n", INT_MAX);
    printf("Y si le sumo 1... %d\n", (int)((unsigned)INT_MAX + 1u));   /* da la vuelta: Ca2 */
    printf("'A' vale %d y 'a' + 1 es '%c'\n", 'A', 'a' + 1);
    return 0;
}"""),
    ("def", "Declarar, inicializar y constantes", r"""
`int edad;` (la caja existe **con basura dentro**) · `edad = 18;` · `int curso = 1;` (lo mejor: declarar e inicializar).
Constantes: `#define PI 3.14159` (sin `;`) o `const int MAX = 100;`. Los caracteres son números de la tabla ASCII: `'A'` = 65,
`'a'` = 97, `'0'` = 48."""),
    ("ojo", "La división entera", r"""`7 / 2` es **3**: entero entre entero da entero. Para decimales: `7 / 2.0` o `(double)a / b` (un *cast*). Y `int x = 3.9;` guarda 3."""),
    ("c", "Compruébalo", r"""#include <stdio.h>

int main(void)
{
    int a = 7, b = 2;
    printf("%d\n", a / b);
    printf("%f\n", (double)a / b);
    printf("1/2 = %d pero 1.0/2 = %.1f\n", 1 / 2, 1.0 / 2);
    return 0;
}"""),
], "Representación de enteros"),

S("operadores", "2.2 Operadores", "Guía de C · cap. 4 · Chuleta 3", [
    ("def", "Aritméticos, asignación y comparación", r"""
- `+ - * /` y **`%`** (resto, solo enteros): `n % 2 == 0` par · `n % 10` última cifra · `n / 10` la quita.
- `x += 5`, `x -= 2`, `x *= 3`, `x++`, `x--`.
- Comparación: `== != < > <= >=`. En C **0 es falso y cualquier otro número verdadero**; una comparación vale 1 o 0.
- Lógicos: `&&` (y), `||` (o), `!` (no). **No existe `0 < x < 10`**: se escribe `x > 0 && x < 10`.
- Ternario: `int mayor = (a > b) ? a : b;`"""),
    ("ojo", "El error más famoso de C", r"""`=` guarda, `==` compara. `if (x = 5)` **mete un 5 en x** y siempre es verdadero."""),
    ("def", "Precedencia", r"""paréntesis → `! ++ --` → `* / %` → `+ -` → `< > <= >=` → `== !=` → `&&` → `||` → `=`. Si dudas, paréntesis."""),
    ("c", "Operadores en acción", r"""#include <stdio.h>

int main(void)
{
    int a = 17, b = 5;
    printf("%d + %d = %d\n", a, b, a + b);
    printf("%d / %d = %d (cociente)\n", a, b, a / b);
    printf("%d %% %d = %d (resto)\n", a, b, a % b);
    printf("a > b es %d\n", a > b);
    printf("a == b es %d\n", a == b);
    a += 3;
    a++;
    printf("a ahora vale %d\n", a);
    return 0;
}"""),
]),

S("io", "2.3 Leer y escribir", "Guía de C · cap. 5", [
    ("def", "printf", r"""
| Marcador | Para | Ejemplo |
|---|---|---|
| `%d` | int | `printf("%d", 5)` → 5 |
| `%f` / `%.2f` | float/double | 2.500000 / 2.50 |
| `%c` · `%s` | carácter · cadena | A · hola |
| `%5d` | entero en 5 espacios | `   42` |
| `\n` · `\t` · `%%` | salto · tabulador · el símbolo % | |"""),
    ("truco", "Reglas de oro del scanf", r"""
1. **`&` delante de la variable** (menos en cadenas): `scanf("%d", &edad)` = «guárdalo en la dirección de edad».
2. `double` se lee con **`%lf`** (en printf vale `%f`).
3. Para un char, **espacio antes**: `scanf(" %c", &c)` (si no, se come el Enter anterior).
4. Un `printf` antes de cada `scanf` para que el usuario sepa qué escribir.
5. Varias a la vez: `scanf("%d %d", &a, &b)`."""),
    ("c", "Pedir datos y mostrarlos", r"""#include <stdio.h>

int main(void)
{
    int edad;
    double altura;
    char inicial;
    printf("Introduce tu edad: ");
    scanf("%d", &edad);
    printf("Introduce tu altura en metros: ");
    scanf("%lf", &altura);
    printf("Introduce la inicial de tu nombre: ");
    scanf(" %c", &inicial);
    printf("\nTienes %d anios, mides %.2f m y tu inicial es %c.\n", edad, altura, inicial);
    return 0;
}""", "19\n1.68\nL"),
    ("ojo", "Errores típicos", r"""Olvidar el `&` (el programa se cae) · `%f` para leer un double · no poner el espacio en `" %c"` · `%d` para imprimir un double (sale basura). `getchar()`/`putchar(c)` leen/escriben un carácter."""),
]),
])

T3 = Tema("c3", "C", 3, "Secuenciales y selectivas (if-else, switch)",
          "El esquema de un programa secuencial, math.h, if / else if / else y switch con break.", [

S("secuenciales", "3.1 Estructuras secuenciales", "Guía de C · cap. 6", [
    ("pasos", "El esquema de siempre", r"""1) Declarar variables → 2) Pedir datos → 3) Calcular → 4) Mostrar resultados."""),
    ("c", "Segundos a horas, minutos y segundos", r"""#include <stdio.h>

int main(void)
{
    int total, h, m, s;
    printf("Segundos totales: ");
    scanf("%d", &total);
    h = total / 3600;
    m = (total % 3600) / 60;
    s = total % 60;
    printf("%d s = %d h %d min %d s\n", total, h, m, s);
    return 0;
}""", "3725"),
    ("c", "Celsius a Fahrenheit (¡9.0/5.0, no 9/5!)", r"""#include <stdio.h>

int main(void)
{
    double c, f;
    printf("Grados Celsius: ");
    scanf("%lf", &c);
    f = c * 9.0 / 5.0 + 32.0;
    printf("%.1f C = %.1f F\n", c, f);
    printf("Con 9/5 saldria: %.1f F\n", c * (9 / 5) + 32.0);
    return 0;
}""", "25"),
    ("c", "Intercambiar dos variables (el tercer vaso)", r"""#include <stdio.h>

int main(void)
{
    int a = 3, b = 8, aux;
    printf("Antes:   a=%d b=%d\n", a, b);
    aux = a;
    a = b;
    b = aux;
    printf("Despues: a=%d b=%d\n", a, b);
    return 0;
}"""),
    ("def", "math.h (compila con -lm)", r"""`sqrt(x)` raíz · `pow(x, y)` potencia · `fabs(x)` valor absoluto real (`abs(n)` enteros, en stdlib.h) · `sin cos tan` · `exp` · `log` (neperiano) · `log10` · `floor` · `ceil` · `round`."""),
    ("c", "math.h", r"""#include <stdio.h>
#include <math.h>

int main(void)
{
    double x;
    printf("Numero: ");
    scanf("%lf", &x);
    printf("sqrt = %.3f\n", sqrt(x));
    printf("x al cubo = %.3f\n", pow(x, 3));
    printf("valor absoluto = %.3f\n", fabs(x));
    return 0;
}""", "2"),
]),

S("if", "3.2 if, else if y else", "Guía de C · cap. 7 · Chuleta 4", [
    ("ojo", "Reglas", r"""La condición va entre paréntesis y **sin `;` detrás**: `if (x > 0);` es un `if` que no hace nada. Pon siempre llaves aunque sea una instrucción. Se pueden anidar."""),
    ("c", "Ecuación de segundo grado (if anidados)", r"""#include <stdio.h>
#include <math.h>

int main(void)
{
    double a, b, c, d;
    printf("Coeficientes a b c: ");
    scanf("%lf %lf %lf", &a, &b, &c);
    if (a == 0) {
        printf("No es de segundo grado\n");
    } else {
        d = b * b - 4 * a * c;
        if (d > 0) {
            printf("x1 = %.3f\n", (-b + sqrt(d)) / (2 * a));
            printf("x2 = %.3f\n", (-b - sqrt(d)) / (2 * a));
        } else if (d == 0) {
            printf("Solucion doble: x = %.3f\n", -b / (2 * a));
        } else {
            printf("No hay soluciones reales\n");
        }
    }
    return 0;
}""", "1 -3 2"),
    ("c", "Año bisiesto", r"""#include <stdio.h>

int main(void)
{
    int anio;
    printf("Anio: ");
    scanf("%d", &anio);
    if ((anio % 4 == 0 && anio % 100 != 0) || anio % 400 == 0)
        printf("%d es bisiesto\n", anio);
    else
        printf("%d no es bisiesto\n", anio);
    return 0;
}""", "2024"),
]),

S("switch", "3.3 switch", "Guía de C · cap. 7", [
    ("def", "Cuándo y cómo", r"""
Para comparar un **int o char** con **valores exactos**. **`break` es imprescindible**: sin él el programa «se cae» al
siguiente `case`. `default` = «ninguno de los anteriores». No vale con decimales ni rangos (para eso, `if`). Varios `case`
seguidos comparten código."""),
    ("c", "Calculadora con switch", r"""#include <stdio.h>

int main(void)
{
    double a, b;
    char op;
    printf("Operacion (ej: 3 + 4): ");
    scanf("%lf %c %lf", &a, &op, &b);
    switch (op) {
        case '+': printf("= %.2f\n", a + b); break;
        case '-': printf("= %.2f\n", a - b); break;
        case '*': printf("= %.2f\n", a * b); break;
        case '/':
            if (b != 0) printf("= %.2f\n", a / b);
            else        printf("No se puede dividir entre 0\n");
            break;
        default:
            printf("Operador desconocido\n");
    }
    return 0;
}""", "7 / 2"),
    ("c", "¿Qué pasa sin break?", r"""#include <stdio.h>

int main(void)
{
    int n = 2;
    switch (n) {
        case 1: printf("uno\n");
        case 2: printf("dos\n");
        case 3: printf("tres\n");     /* ¡se ejecuta también! */
        default: printf("otro\n");
    }
    return 0;
}"""),
]),
])

T4 = Tema("c4", "C", 4, "Bucles y ámbito de las variables",
          "while, do-while y for, contadores y acumuladores, centinelas, menús y variables locales/globales.", [

S("bucles", "4.1 while, do-while y for", "Guía de C · cap. 8 · Chuleta 5", [
    ("idea", "La pista de atletismo", r"""**for** = «da 10 vueltas» (sabes cuántas). **while** = «corre mientras no llueva» (puede que ni empieces). **do-while** = «da una vuelta y luego decide» (mínimo una; ¡lleva `;` al final!)."""),
    ("def", "Equivalencias y patrones", r"""
`for (inicio; condición; paso) cuerpo` equivale a `inicio; while (condición) { cuerpo; paso; }`.
**Contador** (`contador++`, empieza en 0) · **Acumulador** (`suma += x`, empieza en 0; para productos, en 1).
`break` sale del bucle; `continue` salta a la siguiente vuelta. **Bucle infinito** = olvidaste actualizar la condición
(Ctrl+C para cortarlo)."""),
    ("c", "Tabla de multiplicar", r"""#include <stdio.h>

int main(void)
{
    int n;
    printf("Tabla del: ");
    scanf("%d", &n);
    for (int i = 1; i <= 10; i++)
        printf("%d x %2d = %3d\n", n, i, n * i);
    return 0;
}""", "7"),
    ("c", "Validar con do-while", r"""#include <stdio.h>

int main(void)
{
    int nota;
    do {
        printf("Nota (0-10): ");
        scanf("%d", &nota);
        if (nota < 0 || nota > 10)
            printf("Valor no valido, repite.\n");
    } while (nota < 0 || nota > 10);
    printf("Has introducido %d\n", nota);
    return 0;
}""", "15\n-2\n8"),
    ("c", "Media con centinela (0 para terminar)", r"""#include <stdio.h>

int main(void)
{
    double x, suma = 0;
    int cuantos = 0;
    printf("Numeros (0 para terminar): ");
    scanf("%lf", &x);
    while (x != 0) {
        suma += x;
        cuantos++;
        scanf("%lf", &x);
    }
    if (cuantos > 0) printf("Media = %.2f\n", suma / cuantos);
    else             printf("No has escrito ningun numero\n");
    return 0;
}""", "4 6 8 0"),
    ("c", "¿Es primo? (con break)", r"""#include <stdio.h>

int main(void)
{
    int n, primo = 1;
    printf("Numero: ");
    scanf("%d", &n);
    if (n < 2) primo = 0;
    for (int d = 2; d * d <= n; d++) {
        if (n % d == 0) {
            primo = 0;
            break;
        }
    }
    printf("%d %s primo\n", n, primo ? "es" : "no es");
    return 0;
}""", "97"),
    ("c", "Menú con do-while y switch (la estructura de las prácticas)", r"""#include <stdio.h>

int main(void)
{
    int opcion;
    do {
        printf("\n--- MENU ---\n1. Saludar\n2. Despedirse\n0. Salir\nOpcion: ");
        scanf("%d", &opcion);
        switch (opcion) {
            case 1: printf("Hola!\n"); break;
            case 2: printf("Adios!\n"); break;
            case 0: printf("Fin del programa\n"); break;
            default: printf("Opcion no valida\n");
        }
    } while (opcion != 0);
    return 0;
}""", "1\n2\n7\n0"),
]),

S("ambito", "4.2 Variables locales y globales", "Guía de C · cap. 9", [
    ("def", "Ámbito", r"""
**Local**: declarada dentro de una función o bloque; solo existe ahí y desaparece al terminar. **Global**: fuera de todas
las funciones; la ven todas. Una local con el mismo nombre que una global la **tapa** dentro de su función. La `i` de un
`for (int i…)` solo existe en ese for. **Las locales no se inicializan solas (basura); las globales valen 0.**"""),
    ("c", "Local contra global", r"""#include <stdio.h>

int x = 10;                 /* global */

void f(void)
{
    int x = 99;             /* local: tapa a la global dentro de f */
    printf("En f: x = %d\n", x);
}

int main(void)
{
    f();
    printf("En main: x = %d\n", x);
    return 0;
}"""),
    ("truco", "Consejo de estilo", r"""Usa **locales** y pasa los datos como **parámetros**. Las globales hacen los programas difíciles de entender y depurar (cualquiera puede cambiarlas)."""),
]),
])

T5 = Tema("c5", "C", 5, "Funciones",
          "Anatomía, prototipos, paso por valor, funciones que se llaman entre sí y recursividad.", [

S("anatomia", "5.1 Anatomía y prototipos", "Guía de C · cap. 10 · Chuleta 8", [
    ("def", "Partes", r"""
```c
tipo_que_devuelve nombre(tipo param1, tipo param2)
{
    instrucciones;
    return valor;
}
```
`void` si no devuelve nada (o no recibe nada). **C lee de arriba abajo**: una función debe estar declarada antes de usarla →
o la pones antes de `main`, o pones arriba su **prototipo** (la cabecera con `;`) y la definición después."""),
    ("c", "Prototipos", r"""#include <stdio.h>

int mayor(int a, int b);      /* prototipos */
void saludar(void);

int main(void)
{
    saludar();
    printf("El mayor de 4 y 9 es %d\n", mayor(4, 9));
    return 0;
}

int mayor(int a, int b)       /* definiciones */
{
    if (a > b) return a;
    return b;
}

void saludar(void)
{
    printf("Hola desde una funcion!\n");
}"""),
]),

S("valor", "5.2 Paso por valor", "Guía de C · cap. 10", [
    ("idea", "Una fotocopia", r"""La función recibe **una fotocopia** de los datos: si la pinta, el original no cambia. Para cambiar el original… punteros (capítulo 7). Los **vectores sí** se modifican dentro (se pasa su dirección)."""),
    ("c", "Intenta cambiarlo", r"""#include <stdio.h>

void intenta_cambiar(int x)
{
    x = 100;            /* solo cambia la copia */
}

int main(void)
{
    int a = 5;
    intenta_cambiar(a);
    printf("a = %d\n", a);
    return 0;
}"""),
    ("c", "factorial, es_primo y potencia", r"""#include <stdio.h>

long long factorial(int n)
{
    long long f = 1;
    for (int i = 2; i <= n; i++) f *= i;
    return f;
}

int es_primo(int n)
{
    if (n < 2) return 0;
    for (int d = 2; d * d <= n; d++)
        if (n % d == 0) return 0;
    return 1;
}

double potencia(double base, int exp)
{
    double r = 1;
    for (int i = 0; i < exp; i++) r *= base;
    return r;
}

int main(void)
{
    printf("5! = %lld\n", factorial(5));
    printf("13 es primo? %d\n", es_primo(13));
    printf("2^10 = %.0f\n", potencia(2, 10));
    return 0;
}"""),
    ("c", "Recursividad: factorial", r"""#include <stdio.h>

long long fact(int n)
{
    if (n <= 1) return 1;          /* caso base */
    return n * fact(n - 1);        /* caso recursivo */
}

int main(void)
{
    printf("6! = %lld\n", fact(6));
    return 0;
}"""),
    ("ojo", "Errores típicos", r"""Olvidar el `return` · número de argumentos incorrecto · `;` tras la cabecera de la **definición** · usar la función antes de declararla · creer que modificar un parámetro cambia la variable original."""),
]),
])

T6 = Tema("c6", "C", 6, "Vectores, matrices, cadenas y aleatorios",
          "Índices de 0 a N−1, recorrer, buscar, invertir, burbuja, vectores en funciones, matrices y rand().", [

S("vectores", "6.1 Vectores", "Guía de C · cap. 11 · Chuleta 6", [
    ("idea", "Taquillas numeradas", r"""Un vector es una fila de taquillas numeradas, todas del mismo tipo. **La primera es la 0**: con 5 taquillas, la última es la 4. `v[5]` se sale y **C no avisa**: lee basura o el programa peta."""),
    ("def", "Declarar", r"""`int notas[5];` (con basura) · `int v[5] = {4, 8, 15, 16, 23};` · `int w[] = {1, 2, 3};` · `int ceros[100] = {0};` · recórrelo con `for (int i = 0; i < N; i++)` y define el tamaño con `#define N 5`."""),
    ("c", "Máximo, mínimo y posición", r"""#include <stdio.h>
#define N 6

int main(void)
{
    int v[N] = {12, 7, 45, 3, 29, 45};
    int max = v[0], min = v[0], pos = 0;
    for (int i = 1; i < N; i++) {
        if (v[i] > max) { max = v[i]; pos = i; }
        if (v[i] < min) min = v[i];
    }
    printf("Maximo = %d (posicion %d)\n", max, pos);
    printf("Minimo = %d\n", min);
    return 0;
}"""),
    ("c", "Invertir un vector", r"""#include <stdio.h>
#define N 6

int main(void)
{
    int v[N] = {1, 2, 3, 4, 5, 6}, aux;
    for (int i = 0; i < N / 2; i++) {
        aux = v[i];
        v[i] = v[N - 1 - i];
        v[N - 1 - i] = aux;
    }
    for (int i = 0; i < N; i++) printf("%d ", v[i]);
    printf("\n");
    return 0;
}"""),
    ("c", "Vectores y funciones (el original SÍ cambia)", r"""#include <stdio.h>

double media(double v[], int n)
{
    double suma = 0;
    for (int i = 0; i < n; i++) suma += v[i];
    return suma / n;
}

void duplicar(int v[], int n)
{
    for (int i = 0; i < n; i++) v[i] *= 2;
}

int main(void)
{
    double notas[4] = {5, 7.5, 9, 6};
    int w[3] = {1, 2, 3};
    printf("Media = %.2f\n", media(notas, 4));
    duplicar(w, 3);
    printf("%d %d %d\n", w[0], w[1], w[2]);
    return 0;
}"""),
    ("ojo", "Errores típicos con vectores", r"""Acceder a `v[N]` · olvidar pasar el tamaño a la función · `i <= N` en vez de `i < N` · copiar con `a = b` (no se puede: elemento a elemento) · `scanf("%d", v[i])` sin `&`."""),
]),

S("matrices", "6.2 Matrices", "Guía de C · cap. 11", [
    ("c", "Suma y traspuesta", r"""#include <stdio.h>
#define N 3

int main(void)
{
    int a[N][N] = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    int b[N][N] = {{9, 8, 7}, {6, 5, 4}, {3, 2, 1}};
    int s[N][N], t[N][N];
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            s[i][j] = a[i][j] + b[i][j];
            t[j][i] = a[i][j];
        }
    printf("Suma:\n");
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) printf("%4d", s[i][j]);
        printf("\n");
    }
    printf("Traspuesta de a:\n");
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) printf("%4d", t[i][j]);
        printf("\n");
    }
    return 0;
}"""),
    ("def", "Matrices y funciones", r"""Hay que indicar el **número de columnas** en el parámetro: `int suma_matriz(int m[][C], int filas)`. Se guardan **por filas** (y por eso recorrerlas por filas es más rápido: mira el ejercicio de caché 14)."""),
]),

S("cadenas", "6.3 Cadenas (primer contacto)", "Guía de C · cap. 11", [
    ("c", "strlen, strcat y strcmp", r"""#include <stdio.h>
#include <string.h>

int main(void)
{
    char nombre[30];
    printf("Tu nombre: ");
    scanf("%29s", nombre);              /* sin &: un vector ya es una dirección */
    printf("Hola, %s! Tiene %zu letras\n", nombre, strlen(nombre));
    char saludo[20] = "Hola";
    strcat(saludo, " mundo");
    printf("%s\n", saludo);
    if (strcmp(nombre, "Ana") == 0) printf("Eres Ana\n");
    return 0;
}""", "Lucia"),
]),

S("aleatorios", "6.4 Números aleatorios", "Guía de C · cap. 12", [
    ("def", "rand y srand", r"""
`rand()` (stdlib.h) da un entero entre 0 y RAND_MAX, **siempre la misma secuencia** si no siembras: `srand(time(NULL));`
**una sola vez** al principio (time.h). En un rango $[a, b]$: `a + rand() % (b - a + 1)`.

| Quiero | Código |
|---|---|
| 0 a 9 | `rand() % 10` |
| 1 a 6 (dado) | `1 + rand() % 6` |
| 10 a 20 | `10 + rand() % 11` |
| decimal 0 a 1 | `rand() / (double)RAND_MAX` |"""),
    ("c", "Tirar un dado 10 veces", r"""#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(void)
{
    srand(time(NULL));
    for (int i = 0; i < 10; i++)
        printf("%d ", 1 + rand() % 6);
    printf("\n");
    return 0;
}"""),
    ("ojo", "srand dentro del bucle", r"""Si llamas a `srand(time(NULL))` en cada vuelta, como el reloj va por segundos, ¡sale siempre el mismo número!"""),
]),
])

T7 = Tema("c7", "C", 7, "Punteros y cadenas a fondo",
          "& y *, NULL, paso por referencia, devolver varios resultados, punteros y vectores, string.h y ctype.h.", [

S("punteros", "7.1 Punteros", "Guía de C · cap. 13 · Chuleta 9", [
    ("idea", "Casas y direcciones", r"""Cada variable vive en una **casa** de la memoria con su **dirección**. Un puntero es un **papelito** donde apuntas la dirección (no lo que hay dentro). `&x` = «¿dónde vive x?» · `*p` = «ve a la casa apuntada y mira/cambia lo que hay»."""),
    ("c", "Primer contacto", r"""#include <stdio.h>

int main(void)
{
    int a = 5;
    int *p = &a;                       /* p apunta a a */
    printf("a vale %d\n", a);
    printf("*p vale %d\n", *p);
    *p = 20;                           /* cambiar a través del puntero */
    printf("Ahora a vale %d\n", a);
    printf("La direccion de a es %p\n", (void *)&a);
    return 0;
}"""),
    ("def", "Dos significados del *", r"""En la **declaración** (`int *p`) dice «p es un puntero»; al **usarlo** (`*p`) dice «ve a esa dirección». Un puntero que no apunta a nada se inicializa a **NULL**; nunca hagas `*p` con NULL o sin inicializar (*segmentation fault*)."""),
    ("c", "Paso por referencia: intercambiar", r"""#include <stdio.h>

void intercambiar(int *x, int *y)
{
    int aux = *x;
    *x = *y;
    *y = aux;
}

int main(void)
{
    int a = 3, b = 8;
    intercambiar(&a, &b);          /* se pasan las DIRECCIONES */
    printf("a=%d b=%d\n", a, b);
    return 0;
}"""),
    ("c", "Devolver varios resultados", r"""#include <stdio.h>

void dividir(int a, int b, int *cociente, int *resto)
{
    *cociente = a / b;
    *resto = a % b;
}

int main(void)
{
    int c, r;
    dividir(17, 5, &c, &r);
    printf("17 = 5 * %d + %d\n", c, r);
    return 0;
}"""),
    ("def", "Punteros y vectores", r"""El **nombre de un vector es la dirección de su primera casilla**: `v[i]` es lo mismo que `*(v + i)`, y por eso una función que recibe un vector modifica el original. `p + 1` avanza **un elemento** (no un byte). *Es exactamente lo que haces en MIPS con `sll $t0, $t1, 2` y `add`.*"""),
    ("c", "Recorrer un vector con un puntero", r"""#include <stdio.h>

int main(void)
{
    int v[5] = {1, 2, 3, 4, 5};
    for (int *p = v; p < v + 5; p++)
        printf("%d ", *p);
    printf("\n");
    return 0;
}"""),
    ("ojo", "Errores típicos", r"""Puntero sin inicializar · olvidar `*` o `&` (`p = 5` en vez de `*p = 5`) · **devolver la dirección de una variable local** (desaparece al acabar la función) · confundir `int *p` con `*p`."""),
]),

S("cadenas", "7.2 Cadenas a fondo", "Guía de C · cap. 14 · Chuleta 7", [
    ("def", "La cadena y su '\\0'", r"""Una cadena es un vector de `char` que termina en **`'\0'`** (el «punto final» invisible): `char s[5]` guarda como mucho 4 letras. `scanf("%s", s)` para en el primer espacio; **`fgets(s, sizeof s, stdin)`** lee la línea entera (y guarda el `\n`: quítalo con `s[strcspn(s, "\n")] = '\0'`)."""),
    ("def", "string.h y ctype.h", r"""
| Función | Qué hace |
|---|---|
| `strlen(s)` | longitud (sin el `'\0'`) |
| `strcpy(d, o)` / `strncpy(d, o, n)` | copia (¡d debe tener sitio!) |
| `strcat(a, b)` | pega b al final de a |
| `strcmp(a, b)` | 0 si iguales, <0 si a va antes, >0 si después |
| `strchr(s, c)` / `strstr(s, sub)` | busca un carácter / una subcadena |
| `isalpha isdigit isspace isupper islower` · `toupper tolower` | sobre un carácter (ctype.h) |
| `atoi("123")`, `atof("3.5")`, `sprintf(cad, "%d", n)` | texto ↔ número (stdlib.h / stdio.h) |

⚠️ **No se puede** `a = "hola";` ni `if (a == b)` con cadenas: `strcpy` y `strcmp`."""),
    ("c", "Palíndromo", r"""#include <stdio.h>
#include <string.h>

int main(void)
{
    char s[50];
    int n, es = 1;
    printf("Palabra: ");
    scanf("%49s", s);
    n = strlen(s);
    for (int i = 0; i < n / 2; i++)
        if (s[i] != s[n - 1 - i]) { es = 0; break; }
    printf("%s %s un palindromo\n", s, es ? "es" : "no es");
    return 0;
}""", "reconocer"),
    ("c", "Contar palabras", r"""#include <stdio.h>
#include <ctype.h>

int main(void)
{
    char s[] = "esto es una frase de prueba";
    int palabras = 0, dentro = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        if (!isspace((unsigned char)s[i]) && !dentro) {
            palabras++;
            dentro = 1;
        } else if (isspace((unsigned char)s[i])) {
            dentro = 0;
        }
    }
    printf("%d palabras\n", palabras);
    return 0;
}"""),
]),
])

T8 = Tema("c8", "C", 8, "Memoria dinámica y estructuras",
          "malloc, calloc, realloc y free; struct, typedef, vectores de estructuras, -> y enum.", [

S("malloc", "8.1 Memoria dinámica", "Guía de C · cap. 15 · Chuleta 10", [
    ("idea", "La mesa del restaurante", r"""`int v[100]` es reservar siempre mesa para 100. Con **malloc** llamas cuando ya sabes cuántos sois y pides mesa para justo N. Al irte, devuelves la mesa con **free**."""),
    ("def", "Las funciones (stdlib.h)", r"""`malloc(bytes)` (devuelve un puntero, o **NULL** si no hay memoria) · `calloc(n, tam)` (y los pone a 0) · `realloc(p, nuevo)` (cambia el tamaño) · `free(p)`. Pide **`n * sizeof(int)`**, no `n`. **Regla de oro: cada malloc, su free.**"""),
    ("c", "Vector del tamaño que diga el usuario", r"""#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int n;
    printf("Cuantos numeros? ");
    scanf("%d", &n);
    int *v = malloc(n * sizeof(int));
    if (v == NULL) {
        printf("No hay memoria\n");
        return 1;
    }
    for (int i = 0; i < n; i++) scanf("%d", &v[i]);
    int suma = 0;
    for (int i = 0; i < n; i++) suma += v[i];
    printf("Suma = %d\n", suma);
    free(v);
    return 0;
}""", "4\n10 20 30 40"),
    ("c", "Ampliar con realloc", r"""#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int *v = calloc(3, sizeof(int));
    if (v == NULL) return 1;
    v[0] = 1; v[1] = 2; v[2] = 3;
    int *nuevo = realloc(v, 5 * sizeof(int));
    if (nuevo == NULL) { free(v); return 1; }
    v = nuevo;
    v[3] = 4; v[4] = 5;
    for (int i = 0; i < 5; i++) printf("%d ", v[i]);
    printf("\n");
    free(v);
    return 0;
}"""),
    ("c", "Matriz dinámica (vector de punteros a filas)", r"""#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int f = 3, c = 4;
    int **m = malloc(f * sizeof(int *));
    for (int i = 0; i < f; i++)
        m[i] = malloc(c * sizeof(int));
    for (int i = 0; i < f; i++)
        for (int j = 0; j < c; j++)
            m[i][j] = i * j;
    for (int i = 0; i < f; i++) {
        for (int j = 0; j < c; j++) printf("%3d", m[i][j]);
        printf("\n");
    }
    for (int i = 0; i < f; i++) free(m[i]);     /* primero las filas */
    free(m);
    return 0;
}"""),
    ("ojo", "Errores típicos", r"""No comprobar NULL · olvidar `free` (**fuga de memoria**) · usar la memoria después de `free` · `free` dos veces · calcular mal el tamaño."""),
]),

S("struct", "8.2 Estructuras, typedef y enum", "Guía de C · cap. 16", [
    ("def", "struct y typedef", r"""
Un vector junta datos del **mismo** tipo; una **estructura** junta datos de tipos **distintos** en un paquete:
```c
typedef struct {
    char nombre[30];
    int edad;
    double nota;
} Alumno;
Alumno a = {"Lucia", 18, 8.5};      /* a.nombre, a.edad, a.nota */
```
Con puntero se usa la flecha: `p->x` es `(*p).x`."""),
    ("c", "Vector de estructuras y la mejor nota", r"""#include <stdio.h>
#define N 3

typedef struct {
    char nombre[30];
    double nota;
} Alumno;

int main(void)
{
    Alumno clase[N];
    int mejor = 0;
    for (int i = 0; i < N; i++) {
        scanf("%29s %lf", clase[i].nombre, &clase[i].nota);
        if (clase[i].nota > clase[mejor].nota) mejor = i;
    }
    printf("La mejor nota es de %s: %.1f\n", clase[mejor].nombre, clase[mejor].nota);
    return 0;
}""", "Lucia 8.5\nAna 6\nPaula 9.2"),
    ("c", "Modificar una estructura con un puntero", r"""#include <stdio.h>

typedef struct {
    double x, y;
} Punto;

void mover(Punto *p, double dx, double dy)
{
    p->x += dx;
    p->y += dy;
}

void mostrar(Punto p)
{
    printf("(%.1f, %.1f)\n", p.x, p.y);
}

int main(void)
{
    Punto p = {1, 2};
    mover(&p, 3, -1);
    mostrar(p);
    printf("sizeof(Punto) = %zu bytes\n", sizeof(Punto));
    return 0;
}"""),
    ("def", "enum", r"""`enum Dia { LUNES, MARTES, MIERCOLES };` da nombres a constantes (empiezan en 0): `enum Dia hoy = MIERCOLES;` vale 2. *En MIPS, los campos de una estructura son desplazamientos: mira los ejercicios 34–36 de ensamblador.*"""),
]),
])

T9 = Tema("c9", "C", 9, "Ficheros y programas con varios archivos",
          "fopen, fprintf, fscanf, fgets y fclose; preprocesador, .h y .c, static, const y argc/argv.", [

S("ficheros", "9.1 Ficheros", "Guía de C · cap. 17", [
    ("pasos", "Siempre igual", r"""**Abrir** → **usar** → **cerrar**. `FILE *f = fopen("datos.txt", "modo");` con modo `"r"` (leer; debe existir), `"w"` (escribir; **borra** lo que hubiera) o `"a"` (añadir al final). Si falla devuelve **NULL**: compruébalo. Después, `fprintf(f, …)`, `fscanf(f, …)` (devuelve cuántos datos leyó), `fgets(cad, n, f)` y **`fclose(f)`**."""),
    ("c", "Escribir y leer un fichero", r"""#include <stdio.h>

int main(void)
{
    FILE *f = fopen("notas.txt", "w");
    if (f == NULL) { printf("No se pudo abrir\n"); return 1; }
    fprintf(f, "Lucia 8.5\nAna 6.0\nPaula 9.2\n");
    fclose(f);

    f = fopen("notas.txt", "r");
    if (f == NULL) return 1;
    char nombre[30];
    double nota, suma = 0;
    int n = 0;
    while (fscanf(f, "%29s %lf", nombre, &nota) == 2) {   /* 2 = se leyeron 2 datos */
        printf("%s: %.1f\n", nombre, nota);
        suma += nota;
        n++;
    }
    fclose(f);
    if (n > 0) printf("Media = %.2f\n", suma / n);
    return 0;
}"""),
    ("ojo", "Errores típicos", r"""No comprobar NULL · abrir con `"w"` y borrar sin querer un fichero que querías conservar · olvidar `fclose` · la ruta: el fichero se busca en la carpeta desde donde ejecutas."""),
]),

S("varios", "9.2 Preprocesador y varios archivos", "Guía de C · cap. 18", [
    ("def", "Preprocesador", r"""
Las líneas con `#` se procesan **antes de compilar**: `#include <lib.h>` (del sistema) · `#include "mio.h"` (tuyo) ·
`#define N 10` · macros `#define CUADRADO(x) ((x)*(x))` (¡paréntesis a todo y nada de `x++` dentro!)."""),
    ("def", "Dividir el programa", r"""
- `calculos.h`: los **prototipos**, entre guardas `#ifndef CALCULOS_H` / `#define CALCULOS_H` / `#endif` (evitan incluirlo dos veces).
- `calculos.c`: las definiciones (con `#include "calculos.h"`).
- `main.c`: `#include "calculos.h"` y el `main`.
- Compilar todo junto: `gcc -Wall main.c calculos.c -o programa`."""),
    ("c", "static, const y argc/argv", r"""#include <stdio.h>

int contador(void)
{
    static int veces = 0;      /* se inicializa UNA sola vez y conserva su valor */
    veces++;
    return veces;
}

int main(int argc, char *argv[])
{
    const int MAX = 10;        /* no se puede modificar */
    contador(); contador();
    printf("Llamada numero %d (MAX = %d)\n", contador(), MAX);
    printf("argc = %d, el programa se llama %s\n", argc, argv[0]);
    return 0;
}"""),
]),
])

T10 = Tema("c10", "C", 10, "Algoritmos clásicos y depuración",
           "Euclides, Fibonacci, binario, búsqueda binaria, selección, criba, Hanoi, chivato, burbuja y gdb.", [

S("clasicos", "10.1 Algoritmos clásicos", "Guía de C · cap. 19", [
    ("c", "Euclides y Fibonacci", r"""#include <stdio.h>

int mcd(int a, int b)
{
    while (b != 0) {
        int r = a % b;
        a = b;
        b = r;
    }
    return a;
}

int main(void)
{
    printf("mcd(48, 18) = %d\n", mcd(48, 18));
    int a = 0, b = 1;
    for (int i = 0; i < 12; i++) {
        printf("%d ", a);
        int sig = a + b;
        a = b;
        b = sig;
    }
    printf("\n");
    return 0;
}"""),
    ("c", "De decimal a binario", r"""#include <stdio.h>

int main(void)
{
    int n, bits[32], k = 0;
    printf("Numero: ");
    scanf("%d", &n);
    if (n == 0) { printf("0\n"); return 0; }
    while (n > 0) {
        bits[k++] = n % 2;      /* los restos, al revés */
        n /= 2;
    }
    for (int i = k - 1; i >= 0; i--) printf("%d", bits[i]);
    printf("\n");
    return 0;
}""", "37"),
    ("c", "Búsqueda binaria", r"""#include <stdio.h>

int busqueda_binaria(int v[], int n, int x)
{
    int ini = 0, fin = n - 1;
    while (ini <= fin) {
        int medio = (ini + fin) / 2;
        if (v[medio] == x) return medio;
        if (v[medio] < x) ini = medio + 1;
        else              fin = medio - 1;
    }
    return -1;
}

int main(void)
{
    int v[] = {2, 5, 8, 12, 16, 23, 38, 56};
    printf("23 esta en la posicion %d\n", busqueda_binaria(v, 8, 23));
    printf("7 esta en la posicion %d\n", busqueda_binaria(v, 8, 7));
    return 0;
}"""),
    ("c", "Criba de Eratóstenes", r"""#include <stdio.h>
#define N 50

int main(void)
{
    int es_primo[N + 1];
    for (int i = 0; i <= N; i++) es_primo[i] = 1;
    es_primo[0] = es_primo[1] = 0;
    for (int i = 2; i * i <= N; i++)
        if (es_primo[i])
            for (int j = i * i; j <= N; j += i)
                es_primo[j] = 0;
    for (int i = 2; i <= N; i++)
        if (es_primo[i]) printf("%d ", i);
    printf("\n");
    return 0;
}"""),
    ("c", "Torres de Hanoi", r"""#include <stdio.h>

void hanoi(int n, char origen, char destino, char aux)
{
    if (n == 0) return;
    hanoi(n - 1, origen, aux, destino);
    printf("Mover disco %d de %c a %c\n", n, origen, destino);
    hanoi(n - 1, aux, destino, origen);
}

int main(void)
{
    hanoi(3, 'A', 'C', 'B');
    return 0;
}"""),
    ("c", "Ordenación por selección", r"""#include <stdio.h>

void ordenar(int v[], int n)
{
    for (int i = 0; i < n - 1; i++) {
        int pos_min = i;
        for (int j = i + 1; j < n; j++)
            if (v[j] < v[pos_min]) pos_min = j;
        int aux = v[i];
        v[i] = v[pos_min];
        v[pos_min] = aux;
    }
}

int main(void)
{
    int v[] = {29, 7, 45, 3, 12};
    ordenar(v, 5);
    for (int i = 0; i < 5; i++) printf("%d ", v[i]);
    printf("\n");
    return 0;
}"""),
]),

S("chivato", "10.2 El chivato y la burbuja con chivato", "Chuleta de C · 11–12", [
    ("idea", "El chivato (bandera, flag)", r"""La profe sale y le dice a un alumno: «vigila, y si alguien habla, me lo dices». El chivato **empieza callado**, **cambia si pasa algo** y **al final le preguntas**."""),
    ("pasos", "Receta en 3 pasos", r"""① Antes del bucle: valor inicial (lo que supones). ② Dentro: si pasa lo que vigilas, lo cambias. ③ Después: miras cuánto vale y decides.
⚠️ No lo inicialices dentro del bucle, y no lo vuelvas al valor inicial en un `else`: **el chivato solo cambia en una dirección**."""),
    ("c", "Burbuja con chivato", r"""#include <stdio.h>
#define N 5

int main(void)
{
    int v[N] = {3, 1, 2, 5, 4};
    int cambios, pasadas = 0;
    do {
        cambios = 0;                         /* ① el chivato empieza callado */
        for (int j = 0; j < N - 1 - pasadas; j++) {
            if (v[j] > v[j + 1]) {
                int aux = v[j];              /* el tercer vaso */
                v[j] = v[j + 1];
                v[j + 1] = aux;
                cambios = 1;                 /* ② ¡ha habido un cambio! */
            }
        }
        pasadas++;
        printf("Pasada %d: ", pasadas);
        for (int i = 0; i < N; i++) printf("%d ", v[i]);
        printf("%s\n", cambios ? "(hubo cambios)" : "(sin cambios: FIN)");
    } while (cambios);                       /* ③ se le pregunta */
    return 0;
}"""),
    ("truco", "Por qué compensa", r"""Con 3 1 2 5 4, la burbuja con chivato para en **2 pasadas**; la normal haría siempre N − 1 = 4 (dos de ellas inútiles). Como hay que hacer al menos una pasada, encaja un `do-while`."""),
]),

S("depurar", "10.3 Depuración y buenas prácticas", "Guía de C · cap. 20", [
    ("def", "Mensajes del compilador", r"""
| Mensaje | Qué pasa |
|---|---|
| `expected ';' before …` | falta un `;` en la línea **anterior** |
| `undeclared` / `implicit declaration` | falta declarar, un `#include` o un prototipo |
| `undefined reference to 'sqrt'` | falta `-lm` |
| `format '%d' expects …` | el marcador no coincide con el tipo |
| `Segmentation fault` (al ejecutar) | te saliste de un vector o usaste mal un puntero |"""),
    ("def", "Herramientas", r"""
- `printf("DEBUG: i=%d suma=%d\n", i, suma);` en puntos clave.
- **gdb**: `gcc -g -Wall prog.c -o prog` → `gdb ./prog` → `break main`, `run`, `next`, `print suma`, `quit`.
- **valgrind** `./prog`: fugas de memoria y accesos fuera de rango."""),
    ("truco", "Buenas prácticas", r"""Indenta · nombres claros · una función = una tarea · inicializa siempre · compila con `-Wall -Wextra` y arregla los avisos · prueba casos límite (0, negativos, vector de 1, texto vacío) · **programa poco a poco**: 5–10 líneas, compilar, probar."""),
]),
])

T11 = Tema("c11", "C", 11, "Chuleta y los 18 errores típicos",
           "Lo esencial de C en una página y la lista de comprobación de errores.", [

S("chuleta", "11.1 Chuleta final", "Guía de C · chuleta", [
    ("resumen", "Quiero… → escribo…", r"""
| Quiero | Escribo |
|---|---|
| Programa base | `#include <stdio.h>` + `int main(void){ ... return 0; }` |
| Compilar | `gcc -Wall prog.c -o prog -lm` y `./prog` |
| Leer int / double / char | `scanf("%d",&n)` · `scanf("%lf",&x)` · `scanf(" %c",&c)` |
| Escribir | `printf("%d %.2f %c %s\n", n, x, c, texto)` |
| Resto / cociente | `a % b` · `a / b` (¡enteros!) |
| Decisión | `if (c) {...} else if (c2) {...} else {...}` |
| Valores exactos | `switch (v) { case 1: ...; break; default: ... }` |
| Repetir n veces | `for (int i = 0; i < n; i++) {...}` |
| Repetir mientras | `while (c) {...}` · `do {...} while (c);` |
| Función | `tipo nombre(tipo p) { ... return r; }` |
| Vector / matriz | `int v[N];` (0..N−1) · `int m[F][C];` → `m[i][j]` |
| Aleatorio 1..6 | `srand(time(NULL));` una vez + `1 + rand() % 6` |
| Puntero | `int *p = &a;` · `*p` es el valor · `p` la dirección |
| Función que modifica | `void f(int *x) { *x = 5; }` y `f(&a);` |
| Comparar / copiar texto | `strcmp(a,b)==0` · `strcpy(dest,orig)` |
| Leer una línea | `fgets(cad, sizeof(cad), stdin);` |
| Reservar memoria | `int *v = malloc(n*sizeof(int));` … `free(v);` |
| Estructura | `typedef struct { int x; } T;` → `t.x` / `p->x` |
| Fichero | `FILE *f = fopen("a.txt","r");` … `fclose(f);` |"""),
]),

S("errores", "11.2 Los 18 errores que más se cometen", "Guía de C · 18 errores · Chuleta 13", [
    ("ojo", "Lista de comprobación ✅", r"""
1. Olvidar el `;` o una `}`.
2. `=` en vez de `==` dentro de un `if`.
3. Olvidar el `&` en `scanf` (menos en cadenas).
4. `%f` en vez de `%lf` al leer un `double`.
5. `scanf("%c")` sin espacio antes (se salta la lectura).
6. División entera: `7/2` es 3.
7. Usar una variable sin inicializar.
8. Olvidar el `break` en un `switch`.
9. `;` justo después de `if (...)`, `for (...)` o `while (...)`.
10. Bucle infinito (no cambias la variable de la condición).
11. Salirse de un vector (`v[N]`) o recorrerlo con `<=`.
12. Llamar a una función antes de declararla (falta el prototipo).
13. Usar un puntero sin inicializar o con NULL.
14. Olvidar `free` o usar la memoria después de `free`.
15. Comparar cadenas con `==` en vez de `strcmp`.
16. No comprobar que `fopen` o `malloc` no devolvieron NULL.
17. Una cadena sin hueco para el `'\0'` (`char s[4]` para "hola").
18. Olvidar `fclose` o abrir con `"w"` un fichero que querías conservar.

✨ ¡Tú puedes! Error → corrección → error más pequeño → ¡funciona! ✨"""),
    ("c", "Encuentra los 3 errores (y compila para ver los avisos)", r"""#include <stdio.h>

int main(void)
{
    int v[5] = {1, 2, 3, 4, 5}, suma;      /* ① suma sin inicializar */
    for (int i = 0; i < 5; i++)
        suma += v[i];
    double media = suma / 5;               /* ② división entera */
    if (media = 3)                         /* ③ = en vez de == */
        printf("La media es 3\n");
    printf("suma = %d, media = %.2f\n", suma, media);
    return 0;
}"""),
]),
])

TEMAS = [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11]
