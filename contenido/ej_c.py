import re

from contenido.base import Ejercicio, Hoja, Prueba, Programa

P = Prueba
C = "c"


def cod(s):
    return "\n```c\n" + s.strip("\n") + "\n```\n"


def _nums(t):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", t)]


# --------------------------------------------------------------------------- verificadores de salidas aleatorias
def v_piramide(n):
    bueno = [" " * (n - i) + "*" * (2 * i - 1) for i in range(1, n + 1)]

    def v(salida):
        lineas = [l.rstrip() for l in salida.split("\n") if "*" in l][-n:]
        ok = len(lineas) == n
        for i, l in enumerate(lineas, 1):
            if not ok:
                break
            if re.sub(r"^.*[^ *]", "", l).strip() != "*" * (2 * i - 1):
                ok = False
            elif i > 1 or not re.search(r"[^ *]", l):      # la 1.ª fila puede ir pegada al mensaje «Filas: »
                ok = l == bueno[i - 1]
        return [] if ok else ["la pirámide no tiene la forma esperada:\n" + "\n".join(bueno)]
    return v


def v_ordenado_mediana(salida):
    xs = _nums(salida)
    for i in range(len(xs) - 19):
        w = xs[i:i + 20]
        if w == sorted(w) and all(1 <= x <= 100 and x == int(x) for x in w):
            med = (w[9] + w[10]) / 2
            if any(abs(y - med) < 1e-6 for y in xs[i + 20:]):
                return []
            return [f"el vector ordenado está bien, pero no encuentro la mediana {med:g} después"]
    return ["no encuentro 20 números del 1 al 100 ordenados de menor a mayor"]


def v_matriz(salida):
    xs = _nums(salida)
    if len(xs) < 21:
        return ["no encuentro la matriz de 16 números y las sumas"]
    m = xs[:16]
    diag = m[0] + m[5] + m[10] + m[15]
    filas = [sum(m[4 * i:4 * i + 4]) for i in range(4)]
    resto = iter(xs[16:])
    if not all(any(abs(r - x) < 1e-9 for r in resto) for x in [diag] + filas):
        return [f"con esa matriz la diagonal suma {diag:g} y las filas {', '.join(f'{f:g}' for f in filas)}"]
    return []


def v_maxmin(n):
    def v(salida):
        xs = _nums(salida)
        if len(xs) < n + 2:
            return [f"imprime los {n} números del vector y después «Max: …» y «Min: …»"]
        vec, mx, mn = xs[-(n + 2):-2], xs[-2], xs[-1]
        if mx != max(vec) or mn != min(vec):
            return [f"del vector {vec} el máximo es {max(vec):g} y el mínimo {min(vec):g}"]
        return []
    return v


def v_fibo(salida):
    xs = _nums(salida)
    if 88 in xs or 143 in xs:
        return []
    return ["la suma de los 10 primeros términos es 88 (empezando 0, 1, 1, 2…) o 143 (empezando 1, 1, 2…)"]


# --------------------------------------------------------------------------- soluciones
S_IVA = r"""
#include <stdio.h>

int main(void)
{
    double precio, iva;
    printf("Precio: ");
    scanf("%lf", &precio);
    printf("IVA (%%): ");
    scanf("%lf", &iva);
    printf("Precio final: %.2f\n", precio * (1 + iva / 100));
    return 0;
}
"""

S_BILLETES = r"""
#include <stdio.h>

int main(void)
{
    int euros;
    printf("Cantidad en euros: ");
    scanf("%d", &euros);
    int b20 = euros / 20;   euros = euros % 20;   /* cuántos caben y lo que sobra */
    int b10 = euros / 10;   euros = euros % 10;
    int b5  = euros / 5;    euros = euros % 5;
    int m1  = euros;                              /* lo que queda, en monedas de 1 */
    printf("Billetes de 20: %d\n", b20);
    printf("Billetes de 10: %d\n", b10);
    printf("Billetes de 5: %d\n", b5);
    printf("Monedas de 1: %d\n", m1);
    return 0;
}
"""

S_HIPOT = r"""
#include <stdio.h>
#include <math.h>          /* sqrt; compila con -lm */

int main(void)
{
    double a, b;
    printf("Catetos: ");
    scanf("%lf %lf", &a, &b);
    printf("Hipotenusa: %.2f\n", sqrt(a * a + b * b));
    return 0;
}
"""

S_SIGNO = r"""
#include <stdio.h>

int main(void)
{
    double x;
    printf("Numero: ");
    scanf("%lf", &x);
    if (x > 0)
        printf("Es positivo\n");
    else if (x < 0)
        printf("Es negativo\n");
    else
        printf("Es cero\n");
    return 0;
}
"""

S_TRIANG = r"""
#include <stdio.h>

int main(void)
{
    double a, b, c;
    printf("Tres lados: ");
    scanf("%lf %lf %lf", &a, &b, &c);
    if (a < b + c && b < a + c && c < a + b) {          /* desigualdad triangular */
        if (a == b && b == c)
            printf("Forman triangulo equilatero\n");
        else if (a == b || b == c || a == c)
            printf("Forman triangulo isosceles\n");
        else
            printf("Forman triangulo escaleno\n");
    } else {
        printf("No forman triangulo\n");
    }
    return 0;
}
"""

S_NOTAS = r"""
#include <stdio.h>

int main(void)
{
    double nota;
    int dia;
    printf("Nota: ");
    scanf("%lf", &nota);
    if (nota < 0 || nota > 10)
        printf("Nota no valida\n");
    else if (nota < 5)
        printf("Suspenso\n");
    else if (nota < 7)
        printf("Aprobado\n");
    else if (nota < 9)
        printf("Notable\n");
    else
        printf("Sobresaliente\n");

    printf("Dia (1-7): ");
    scanf("%d", &dia);
    switch (dia) {
        case 1: printf("Lunes\n"); break;
        case 2: printf("Martes\n"); break;
        case 3: printf("Miercoles\n"); break;
        case 4: printf("Jueves\n"); break;
        case 5: printf("Viernes\n"); break;
        case 6: printf("Sabado\n"); break;
        case 7: printf("Domingo\n"); break;
        default: printf("Dia no valido\n");
    }
    return 0;
}
"""

S_PARES = r"""
#include <stdio.h>

int main(void)
{
    for (int i = 2; i <= 100; i += 2)
        printf("%d ", i);
    printf("\n");
    return 0;
}
"""

S_CIFRAS = r"""
#include <stdio.h>

int main(void)
{
    int n, suma = 0;
    printf("Numero: ");
    scanf("%d", &n);
    if (n < 0) n = -n;          /* las cifras de -123 son las de 123 */
    while (n > 0) {
        suma += n % 10;         /* última cifra */
        n /= 10;                /* quitarla */
    }
    printf("Suma de cifras: %d\n", suma);
    return 0;
}
"""

S_PIRAMIDE = r"""
#include <stdio.h>

int main(void)
{
    int n;
    printf("Filas: ");
    scanf("%d", &n);
    for (int i = 1; i <= n; i++) {
        for (int j = 0; j < n - i; j++)       /* espacios: n - i */
            printf(" ");
        for (int j = 0; j < 2 * i - 1; j++)   /* asteriscos: 2i - 1 */
            printf("*");
        printf("\n");
    }
    return 0;
}
"""

S_MAXIMO = r"""
#include <stdio.h>

int main(void)
{
    int x, max, hay = 0;
    printf("Numeros (negativo para terminar): ");
    scanf("%d", &x);
    while (x >= 0) {
        if (!hay || x > max) {   /* el primero siempre es el máximo provisional */
            max = x;
            hay = 1;
        }
        scanf("%d", &x);
    }
    if (hay)
        printf("Maximo: %d\n", max);
    else
        printf("No has introducido ningun numero\n");
    return 0;
}
"""

S_FUNC1 = r"""
#include <stdio.h>

int max(int a, int b)
{
    return a > b ? a : b;
}

int es_par(int n)
{
    return n % 2 == 0;           /* 1 si es par, 0 si no */
}

long long potencia(int b, int e)
{
    long long r = 1;
    for (int i = 0; i < e; i++)
        r *= b;
    return r;
}

int main(void)
{
    printf("max(3, 8) = %d\n", max(3, 8));
    printf("es_par(7) = %d\n", es_par(7));
    printf("potencia(2, 10) = %lld\n", potencia(2, 10));
    return 0;
}
"""

M_FUNC1 = r"""
int main(void)
{
    printf("%d %d %d %d %d ", max(3, 8), max(-2, -9), max(5, 5), es_par(7) != 0, es_par(10) != 0);
    printf("%d %lld %lld %lld\n", es_par(-4) != 0, potencia(2, 10), potencia(3, 0), potencia(10, 12));
    return 0;
}
"""

S_FUNC2 = r"""
#include <stdio.h>

int suma_cifras(int n)
{
    int s = 0;
    if (n < 0) n = -n;
    while (n > 0) {
        s += n % 10;
        n /= 10;
    }
    return s;
}

int main(void)
{
    int cuantos = 0;
    for (int i = 1; i <= 1000; i++)
        if (suma_cifras(i) == 10)
            cuantos++;
    printf("Entre 1 y 1000 hay %d numeros cuyas cifras suman 10\n", cuantos);
    return 0;
}
"""

M_FUNC2 = r"""
int main(void)
{
    printf("%d %d %d %d\n", suma_cifras(1234), suma_cifras(0), suma_cifras(9), suma_cifras(1000));
    return 0;
}
"""

S_MEDIA = r"""
#include <stdio.h>
#define N 10

int main(void)
{
    double v[N], suma = 0;
    printf("Introduce %d numeros: ", N);
    for (int i = 0; i < N; i++) {
        scanf("%lf", &v[i]);
        suma += v[i];
    }
    double media = suma / N;
    int encima = 0;
    for (int i = 0; i < N; i++)          /* segunda pasada: ya conocemos la media */
        if (v[i] > media)
            encima++;
    printf("Media: %.2f\n", media);
    printf("Por encima de la media: %d\n", encima);
    return 0;
}
"""

S_BURBUJA = r"""
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define N 20

void burbuja(int v[], int n)
{
    for (int i = 0; i < n - 1; i++)              /* n - 1 pasadas */
        for (int j = 0; j < n - 1 - i; j++)      /* el final ya está colocado */
            if (v[j] > v[j + 1]) {
                int aux = v[j];
                v[j] = v[j + 1];
                v[j + 1] = aux;
            }
}

int main(void)
{
    int v[N];
    srand(time(NULL));                           /* semilla: una vez, al principio */
    for (int i = 0; i < N; i++)
        v[i] = 1 + rand() % 100;                 /* aleatorio de 1 a 100 */
    burbuja(v, N);
    printf("Ordenado: ");
    for (int i = 0; i < N; i++)
        printf("%d ", v[i]);
    /* N es par: la mediana es la media de los dos centrales */
    printf("\nMediana: %.1f\n", (v[N / 2 - 1] + v[N / 2]) / 2.0);
    return 0;
}
"""

S_MATRIZ = r"""
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define N 4

int main(void)
{
    int m[N][N], diag = 0;
    srand(time(NULL));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            m[i][j] = rand() % 10;
            printf("%3d", m[i][j]);
        }
        printf("\n");
    }
    for (int i = 0; i < N; i++)
        diag += m[i][i];
    printf("Diagonal: %d\n", diag);
    for (int i = 0; i < N; i++) {
        int s = 0;
        for (int j = 0; j < N; j++)
            s += m[i][j];
        printf("Fila %d: %d\n", i, s);
    }
    return 0;
}
"""

S_VOCALES = r"""
#include <stdio.h>
#include <ctype.h>

int main(void)
{
    char texto[200];
    int vocales = 0;
    printf("Texto: ");
    fgets(texto, sizeof texto, stdin);
    for (int i = 0; texto[i] != '\0'; i++) {
        switch (tolower((unsigned char)texto[i])) {
            case 'a': case 'e': case 'i': case 'o': case 'u':
                vocales++;            /* los case se «caen» hasta aquí */
                break;
        }
    }
    printf("Vocales: %d\n", vocales);
    return 0;
}
"""

S_ORDENAR2 = r"""
#include <stdio.h>

void ordenar2(int *a, int *b)
{
    if (*a > *b) {              /* *a es «lo que hay en la dirección a» */
        int aux = *a;
        *a = *b;
        *b = aux;
    }
}

int main(void)
{
    int x = 9, y = 4;
    ordenar2(&x, &y);           /* se pasan las DIRECCIONES */
    printf("%d %d\n", x, y);    /* 4 9 */
    return 0;
}
"""

M_ORDENAR2 = r"""
int main(void)
{
    int a = 9, b = 4, c = 1, d = 2, e = -3, f = -3;
    ordenar2(&a, &b);
    ordenar2(&c, &d);
    ordenar2(&e, &f);
    printf("%d %d %d %d %d %d\n", a, b, c, d, e, f);
    return 0;
}
"""

S_MALLOC = r"""
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void max_min(const int v[], int n, int *max, int *min)
{
    *max = *min = v[0];
    for (int i = 1; i < n; i++) {
        if (v[i] > *max) *max = v[i];
        if (v[i] < *min) *min = v[i];
    }
}

int main(void)
{
    int n;
    printf("Cuantos numeros? ");
    scanf("%d", &n);
    if (n <= 0) return 1;
    int *v = malloc(n * sizeof(int));
    if (v == NULL) {                    /* malloc puede fallar */
        printf("No hay memoria\n");
        return 1;
    }
    srand(time(NULL));
    for (int i = 0; i < n; i++) {
        v[i] = rand() % 1000;
        printf("%d ", v[i]);
    }
    int mx, mn;
    max_min(v, n, &mx, &mn);            /* dos resultados → dos punteros */
    printf("\nMax: %d Min: %d\n", mx, mn);
    free(v);                            /* ¡siempre! */
    return 0;
}
"""

S_REVES = r"""
#include <stdio.h>
#include <string.h>

int main(void)
{
    char frase[200];
    printf("Frase: ");
    fgets(frase, sizeof frase, stdin);
    frase[strcspn(frase, "\n")] = '\0';      /* quitar el salto de línea que guarda fgets */
    for (int i = (int)strlen(frase) - 1; i >= 0; i--)
        putchar(frase[i]);
    putchar('\n');
    return 0;
}
"""

S_LIBROS = r"""
#include <stdio.h>
#include <string.h>
#define N 5

typedef struct {
    char titulo[100];
    char autor[100];
    int paginas;
} Libro;

void leer_linea(char *s, int tam)
{
    fgets(s, tam, stdin);
    s[strcspn(s, "\n")] = '\0';
}

int main(void)
{
    Libro libros[N];
    char aux[20];
    for (int i = 0; i < N; i++) {
        printf("Titulo: ");
        leer_linea(libros[i].titulo, sizeof libros[i].titulo);
        printf("Autor: ");
        leer_linea(libros[i].autor, sizeof libros[i].autor);
        printf("Paginas: ");
        leer_linea(aux, sizeof aux);            /* así no mezclamos scanf y fgets */
        sscanf(aux, "%d", &libros[i].paginas);
    }
    int mejor = 0;
    for (int i = 1; i < N; i++)
        if (libros[i].paginas > libros[mejor].paginas)
            mejor = i;
    printf("El mas largo: %s, de %s (%d paginas)\n",
           libros[mejor].titulo, libros[mejor].autor, libros[mejor].paginas);
    return 0;
}
"""

S_FIBO = r"""
#include <stdio.h>

int main(void)
{
    FILE *f = fopen("fibonacci.txt", "w");
    if (f == NULL) { printf("No se puede crear el fichero\n"); return 1; }
    long a = 0, b = 1;
    for (int i = 0; i < 10; i++) {          /* 0 1 1 2 3 5 8 13 21 34 */
        fprintf(f, "%ld\n", a);
        long sig = a + b;
        a = b;
        b = sig;
    }
    fclose(f);

    f = fopen("fibonacci.txt", "r");
    if (f == NULL) { printf("No se puede abrir el fichero\n"); return 1; }
    long x, suma = 0;
    while (fscanf(f, "%ld", &x) == 1)       /* leer hasta que no quede nada */
        suma += x;
    fclose(f);
    printf("Suma de los 10 primeros: %ld\n", suma);
    return 0;
}
"""

S_GESTOR = r"""
#include <stdio.h>
#include <string.h>
#define MAX 50

typedef struct {
    char nombre[30];
    double nota;
} Alumno;

int leer_alumnos(Alumno lista[])
{
    int n;
    printf("Cuantos alumnos? ");
    scanf("%d", &n);
    if (n > MAX) n = MAX;
    for (int i = 0; i < n; i++) {
        printf("Nombre %d: ", i + 1);
        scanf("%29s", lista[i].nombre);
        printf("Nota: ");
        scanf("%lf", &lista[i].nota);
    }
    return n;
}

void mostrar(Alumno lista[], int n)
{
    for (int i = 0; i < n; i++)
        printf("%-15s %5.2f\n", lista[i].nombre, lista[i].nota);
}

double media(Alumno lista[], int n)
{
    double s = 0;
    for (int i = 0; i < n; i++) s += lista[i].nota;
    return n > 0 ? s / n : 0;
}

void guardar(Alumno lista[], int n)
{
    FILE *f = fopen("alumnos.txt", "w");
    if (f == NULL) { printf("Error al guardar\n"); return; }
    for (int i = 0; i < n; i++)
        fprintf(f, "%s %.2f\n", lista[i].nombre, lista[i].nota);
    fclose(f);
    printf("Guardado en alumnos.txt\n");
}

/* NUEVO: cargar el fichero al empezar (si no existe, se empieza con 0 alumnos) */
int cargar(Alumno lista[])
{
    FILE *f = fopen("alumnos.txt", "r");
    int n = 0;
    if (f == NULL) return 0;
    while (n < MAX && fscanf(f, "%29s %lf", lista[n].nombre, &lista[n].nota) == 2)
        n++;
    fclose(f);
    return n;
}

/* NUEVO: mejor y peor nota */
void mejor_y_peor(Alumno lista[], int n)
{
    if (n == 0) { printf("No hay alumnos\n"); return; }
    int mej = 0, peo = 0;
    for (int i = 1; i < n; i++) {
        if (lista[i].nota > lista[mej].nota) mej = i;
        if (lista[i].nota < lista[peo].nota) peo = i;
    }
    printf("Mejor: %s %.2f\n", lista[mej].nombre, lista[mej].nota);
    printf("Peor: %s %.2f\n", lista[peo].nombre, lista[peo].nota);
}

int main(void)
{
    Alumno lista[MAX];
    int opcion;
    int n = cargar(lista);
    printf("Cargados %d alumnos\n", n);
    mejor_y_peor(lista, n);
    do {
        printf("\n1. Introducir alumnos\n2. Mostrar\n3. Media\n");
        printf("4. Guardar en fichero\n5. Mejor y peor\n0. Salir\nOpcion: ");
        if (scanf("%d", &opcion) != 1) break;
        switch (opcion) {
            case 1: n = leer_alumnos(lista); break;
            case 2: mostrar(lista, n); break;
            case 3: printf("Media = %.2f\n", media(lista, n)); break;
            case 4: guardar(lista, n); break;
            case 5: mejor_y_peor(lista, n); break;
            case 0: printf("Hasta luego!\n"); break;
            default: printf("Opcion no valida\n");
        }
    } while (opcion != 0);
    return 0;
}
"""

ALUMNOS = "Ana 7.50\nLuis 4.25\nMarta 9.00\nPablo 6.10\n"
LIBROS_IN = ("El Quijote\nCervantes\n1250\nCien anos de soledad\nGarcia Marquez\n471\nRayuela\nCortazar\n600\n"
             "La Regenta\nClarin\n1300\nNiebla\nUnamuno\n240\n")

HOJA = Hoja("c-ejercicios", "Ejercicios propuestos de C (22)", "c", "Guía «Programar en C desde cero» (tu guía rosa)",
            "Los 22 ejercicios de la guía, resueltos, explicados y con corrección automática (se compilan con gcc).", [

Ejercicio("c-1", "Precio con IVA", r"""Pide el precio de un producto y el % de IVA; muestra el precio final.""",
r"""**Idea:** el IVA es un porcentaje del precio: final = precio + precio·iva/100 = precio·(1 + iva/100).

⚠️ Usa `double` y escribe `iva / 100` con un `double`: si `iva` fuera `int`, `21 / 100` daría **0** (división entera).
Para imprimir el símbolo % en `printf` se escribe `%%`.""" + cod(S_IVA),
pista="precio * (1 + iva / 100)", tema="Secuenciales",
programa=Programa(C, [P("100\n21", "121.00", descripcion="100 € con 21 %"), P("19.99\n10", "21.99", descripcion="19,99 € con 10 %"),
                      P("50\n0", "50.00", descripcion="sin IVA")], solucion=S_IVA)),

Ejercicio("c-2", "Billetes y monedas", r"""Pide una cantidad de euros y muestra cuántos billetes de 20, 10 y 5 y cuántas monedas de 1 €
hacen falta.

*En la app:* imprime una línea por tipo, así: `Billetes de 20: 4` · `Billetes de 10: 0` · `Billetes de 5: 1` · `Monedas de 1: 2`.""",
r"""**Idea (cambio con el menor número de piezas):** `/` da cuántos billetes caben y `%` lo que sobra para el siguiente,
como al pasar segundos a horas, minutos y segundos.

Con 87 €: 87 / 20 = **4** (sobran 7) → 7 / 10 = **0** → 7 / 5 = **1** (sobran 2) → **2** monedas.""" + cod(S_BILLETES),
pista="/ y % encadenados", tema="Secuenciales",
programa=Programa(C, [P("87", "20 4 10 0 5 1 1 2", descripcion="87 €"), P("40", "20 2 10 0 5 0 1 0", descripcion="40 €"),
                      P("19", "20 0 10 1 5 1 1 4", descripcion="19 €")], solucion=S_BILLETES)),

Ejercicio("c-3", "Hipotenusa", r"""Pide los catetos de un triángulo rectángulo y calcula la hipotenusa.""",
r"""**Pitágoras:** $h = \sqrt{a^2 + b^2}$. `sqrt` está en `<math.h>` y al compilar hay que añadir **`-lm`**
(`gcc -Wall prog.c -o prog -lm`). Para elevar al cuadrado, `a * a` (en C `^` NO es potencia: es el XOR de bits).""" + cod(S_HIPOT),
pista="sqrt y math.h", tema="Secuenciales",
programa=Programa(C, [P("3 4", "5.00", descripcion="3 y 4"), P("5 12", "13.00", descripcion="5 y 12"),
                      P("1 1", "1.41", descripcion="1 y 1")], solucion=S_HIPOT)),

Ejercicio("c-4", "Positivo, negativo o cero", r"""Pide un número y di si es positivo, negativo o cero.""",
r"""Tres casos que se excluyen → `if` / `else if` / `else`. El último no necesita condición: si no es ni mayor ni menor
que 0, es 0.""" + cod(S_SIGNO), tema="Selectivas",
programa=Programa(C, [P("5", "positivo", descripcion="5"), P("-3.5", "negativo", descripcion="−3,5"),
                      P("0", "cero", descripcion="0")], solucion=S_SIGNO)),

Ejercicio("c-5", "¿Forman triángulo? ¿De qué tipo?", r"""Pide tres lados y di si forman triángulo (cada lado menor que la suma
de los otros dos) y de qué tipo es (equilátero, isósceles, escaleno).""",
r"""1. Primero la **desigualdad triangular**: las tres condiciones unidas con `&&`.
2. Dentro, el tipo: los tres iguales → equilátero; si no, alguno igual a otro (`||`) → isósceles; si no, escaleno.

⚠️ El orden importa: un equilátero también cumple «dos lados iguales», por eso se pregunta antes.""" + cod(S_TRIANG),
tema="Selectivas",
programa=Programa(C, [P("3 3 3", "equilatero", descripcion="3 3 3"), P("2 2 3", "isosceles", descripcion="2 2 3"),
                      P("3 4 5", "escaleno", descripcion="3 4 5"), P("1 2 3", "no", descripcion="1 2 3 (degenerado)"),
                      P("1 1 5", "no", descripcion="1 1 5")], solucion=S_TRIANG)),

Ejercicio("c-6", "Calificación con else if y día con switch", r"""Pide una nota y muestra la calificación con `else if`
(suspenso, aprobado, notable, sobresaliente) y, con `switch`, el día de la semana a partir de un número 1–7.

*En la app:* primero se lee la nota y después el número del día.""",
r"""- **else if** para **rangos** (< 5, < 7, < 9…): como los casos van en orden, cada condición ya sabe que las anteriores
  fallaron (por eso basta `nota < 7`, no hace falta `nota >= 5 && nota < 7`). Comprueba antes que esté entre 0 y 10.
- **switch** para **valores exactos** de un entero. ¡No olvides el `break`! Sin él, se ejecutan también los `case` de abajo.""" +
cod(S_NOTAS), tema="Selectivas",
programa=Programa(C, [P("7.5\n3", "notable miercoles", descripcion="7,5 y día 3"), P("4.99\n7", "suspenso domingo", descripcion="4,99 y 7"),
                      P("9\n1", "sobresaliente lunes", descripcion="9 y 1"), P("5\n9", "aprobado no valido", descripcion="5 y 9")],
                  solucion=S_NOTAS)),

Ejercicio("c-7", "Pares del 1 al 100", r"""Muestra los números pares del 1 al 100.""",
r"""Dos formas: empezar en 2 y sumar de 2 en 2 (`i += 2`), o recorrer todos y quedarse con los que cumplen `i % 2 == 0`.
La primera hace la mitad de vueltas.""" + cod(S_PARES), tema="Bucles",
programa=Programa(C, [P("", " ".join(str(i) for i in range(2, 101, 2)), descripcion="2 4 … 100")], solucion=S_PARES)),

Ejercicio("c-8", "Suma de las cifras", r"""Pide un número y muestra la suma de sus cifras.""",
r"""**Truco:** `n % 10` es la última cifra y `n / 10` la quita (división entera). Se repite mientras queden cifras.

| n | n % 10 | suma | n / 10 |
|---|---|---|---|
| 1234 | 4 | 4 | 123 |
| 123 | 3 | 7 | 12 |
| 12 | 2 | 9 | 1 |
| 1 | 1 | **10** | 0 |""" + cod(S_CIFRAS), pista="n % 10 y n /= 10 dentro de un while", tema="Bucles",
programa=Programa(C, [P("1234", "10", descripcion="1234"), P("9", "9", descripcion="9"), P("1000", "1", descripcion="1000"),
                      P("98765", "35", descripcion="98765")], solucion=S_CIFRAS)),

Ejercicio("c-9", "Pirámide de asteriscos", r"""Dibuja una pirámide de asteriscos con n filas.""",
r"""Para n = 4:
```
   *
  ***
 *****
*******
```
En la fila *i* (de 1 a n) hay **n − i espacios** y **2i − 1 asteriscos**. Bucle externo para las filas; dentro, dos bucles
seguidos: primero los espacios y luego los asteriscos.""" + cod(S_PIRAMIDE),
pista="en cada fila, primero espacios y luego asteriscos (bucles anidados)", tema="Bucles",
programa=Programa(C, [P("4", verificar=v_piramide(4), descripcion="4 filas"), P("1", verificar=v_piramide(1), descripcion="1 fila"),
                      P("6", verificar=v_piramide(6), descripcion="6 filas")], solucion=S_PIRAMIDE)),

Ejercicio("c-10", "Máximo hasta un negativo", r"""Pide números hasta que el usuario escriba un negativo y muestra el máximo.""",
r"""Es un bucle con **centinela** (el negativo marca el final). Patrón: leer uno antes del bucle, y dentro procesarlo y leer
el siguiente. Para el máximo, el **primer** número leído es el máximo provisional (no inicialices `max = 0`: fallaría si…
bueno, aquí todos son ≥ 0, pero es una mala costumbre; con negativos fallaría).""" + cod(S_MAXIMO), tema="Bucles",
programa=Programa(C, [P("3\n9\n2\n-1", "9", descripcion="3 9 2 −1"), P("0\n0\n-5", "0", descripcion="0 0 −5"),
                      P("7\n-1", "7", descripcion="un solo número")], solucion=S_MAXIMO)),

Ejercicio("c-11", "max, es_par y potencia", r"""Escribe `int max(int a, int b)`, `int es_par(int n)` y
`long long potencia(int b, int e)` y pruébalas desde `main`.

*En la app:* se comprueban tus funciones con un `main` de prueba (el tuyo se renombra solo).""",
r"""- `max` con el operador ternario `condición ? a : b`.
- `es_par` puede devolver directamente la comparación (`n % 2 == 0` ya vale 1 o 0).
- `potencia` multiplica `e` veces; con `long long` caben resultados hasta ~9·10¹⁸ (2¹⁰ = 1024, 10¹² ya no cabe en un `int`).
  Para imprimirlo: `%lld`.""" + cod(S_FUNC1), tema="Funciones",
programa=Programa(C, [P(salida="8 -2 5 0 1 1 1024 1 1000000000000", main=M_FUNC1,
                        descripcion="max(3,8), max(−2,−9), max(5,5), es_par(7/10/−4), 2¹⁰, 3⁰, 10¹²")], solucion=S_FUNC1)),

Ejercicio("c-12", "suma_cifras reutilizada", r"""Escribe `int suma_cifras(int n)` y reutilízala en un programa que diga
cuántos números del 1 al 1000 tienen suma de cifras 10.""",
r"""La función encapsula el bucle del ejercicio 8; `main` la llama 1000 veces y cuenta. Resultado: **63** números
(19, 28, 37, …, 910).

💡 Esto es la gracia de las funciones: escribes una vez, usas mil.""" + cod(S_FUNC2), tema="Funciones",
programa=Programa(C, [P(salida="63", descripcion="tu programa completo"),
                      P(salida="10 0 9 1", main=M_FUNC2, descripcion="suma_cifras(1234), (0), (9), (1000)")], solucion=S_FUNC2)),

Ejercicio("c-13", "Media y cuántos por encima", r"""Lee 10 números, calcula su media y cuenta cuántos están por encima de ella.""",
r"""Hace falta un **vector**: para contar los que superan la media primero hay que conocerla, así que se recorren los datos
**dos veces** (y sin vector ya no los tendríamos).""" + cod(S_MEDIA), tema="Vectores",
programa=Programa(C, [P("1 2 3 4 5 6 7 8 9 10", "5.50 5", descripcion="1…10"),
                      P("5 5 5 5 5 5 5 5 5 5", "5.00 0", descripcion="todos iguales"),
                      P("0 0 0 0 0 0 0 0 0 10", "1.00 1", descripcion="un 10 y nueve 0")], solucion=S_MEDIA)),

Ejercicio("c-14", "Aleatorios ordenados con burbuja y mediana", r"""Rellena un vector de 20 elementos con aleatorios 1–100,
muéstralo ordenado de menor a mayor (burbuja) y calcula la mediana.""",
r"""- Aleatorio entre 1 y 100: `1 + rand() % 100`; `srand(time(NULL))` **una sola vez** al principio.
- **Burbuja:** se comparan parejas vecinas y se intercambian si están al revés; tras cada pasada, el mayor «sube» al final.
- **Mediana** con 20 elementos (par): media de los dos centrales, posiciones 9 y 10. ¡Divide entre `2.0` para no perder el
  decimal!

*La app no puede adivinar tus aleatorios: comprueba que los 20 números estén ordenados, entre 1 y 100, y que la mediana que
imprimes después sea la de esos números.*""" + cod(S_BURBUJA), tema="Vectores",
programa=Programa(C, [P(verificar=v_ordenado_mediana, descripcion="ejecución 1"),
                      P(verificar=v_ordenado_mediana, descripcion="ejecución 2")], solucion=S_BURBUJA)),

Ejercicio("c-15", "Matriz 4×4: diagonal y filas", r"""Crea una matriz 4×4 aleatoria y calcula la suma de su diagonal principal
(`m[i][i]`) y la de cada fila.

*En la app:* imprime primero la matriz, luego la diagonal y luego la suma de cada fila.""",
r"""La diagonal principal son los elementos con fila = columna: un solo bucle con `m[i][i]`. Para cada fila, un bucle
interno que suma sus 4 columnas (reiniciando la suma en cada fila).""" + cod(S_MATRIZ), tema="Vectores",
programa=Programa(C, [P(verificar=v_matriz, descripcion="ejecución 1"), P(verificar=v_matriz, descripcion="ejecución 2")],
                  solucion=S_MATRIZ)),

Ejercicio("c-16", "Contar vocales (cadenas + switch)", r"""Dado un texto, cuenta cuántas vocales tiene (cadenas + `switch`).""",
r"""Se lee la línea con `fgets` y se recorre carácter a carácter hasta el `'\0'`. `tolower` (de `<ctype.h>`) convierte a
minúscula para contar también las mayúsculas. En el `switch`, varios `case` seguidos sin `break` comparten el mismo código.""" +
cod(S_VOCALES), tema="Vectores",
programa=Programa(C, [P("Hola Mundo", "4", descripcion="«Hola Mundo»"), P("AEIOU aeiou", "10", descripcion="mayúsculas y minúsculas"),
                      P("xyz", "0", descripcion="sin vocales")], solucion=S_VOCALES)),

Ejercicio("c-17", "ordenar2 con punteros", r"""Escribe `void ordenar2(int *a, int *b)` que deje en `a` el menor y en `b` el mayor.""",
r"""Una función en C recibe **copias** de los argumentos; para poder cambiar las variables de quien llama hay que pasarle
**sus direcciones** (`&x`) y trabajar con `*a` («lo que hay en esa dirección»).

💡 Analogía: no te doy mi libreta (copia), te doy la dirección de mi casa para que cambies lo que hay dentro.""" + cod(S_ORDENAR2),
tema="Punteros",
programa=Programa(C, [P(salida="4 9 1 2 -3 -3", main=M_ORDENAR2, descripcion="(9,4), (1,2), (−3,−3)")], solucion=S_ORDENAR2)),

Ejercicio("c-18", "Vector dinámico con malloc: máximo y mínimo", r"""Pide n, reserva un vector con `malloc`, rellénalo con
aleatorios y muestra el máximo y el mínimo con una sola función. No olvides el `free`.

*En la app:* imprime los n números y después `Max: …` y `Min: …`.""",
r"""- `malloc(n * sizeof(int))` reserva n enteros y devuelve un puntero (o `NULL` si no hay memoria: compruébalo).
- Una función solo devuelve un valor con `return`; para devolver **dos** (máximo y mínimo) se pasan dos punteros.
- `free(v)` al final: lo que se pide con `malloc` se devuelve con `free`.""" + cod(S_MALLOC), tema="Punteros",
programa=Programa(C, [P("8", verificar=v_maxmin(8), descripcion="n = 8"), P("1", verificar=v_maxmin(1), descripcion="n = 1")],
                  solucion=S_MALLOC)),

Ejercicio("c-19", "Una frase al revés", r"""Lee una frase con `fgets` y muéstrala al revés.""",
r"""`fgets` guarda también el `'\n'` del final: se quita con `frase[strcspn(frase, "\n")] = '\0'`. Luego se recorre desde
el último carácter (`strlen - 1`) hasta el 0.""" + cod(S_REVES), tema="Cadenas",
programa=Programa(C, [P("Hola mundo", "odnum aloH", modo="texto", descripcion="«Hola mundo»"),
                      P("ana", "ana", modo="texto", descripcion="palíndromo")], solucion=S_REVES)),

Ejercicio("c-20", "Estructura Libro: el de más páginas", r"""Define una estructura `Libro` (título, autor, páginas) y un vector
de 5 libros; muestra el de más páginas.

*En la app:* se leen los 5 libros, cada uno en tres líneas: título, autor y páginas.""",
r"""`typedef struct { … } Libro;` crea el tipo; `libros[i].paginas` accede a un campo. Para buscar el máximo se guarda el
**índice** del mejor (así luego tenemos todos sus datos). Los títulos tienen espacios → `fgets`; y para no mezclar `scanf` y
`fgets` (el `\n` que deja `scanf` estropea el siguiente `fgets`), también las páginas se leen con `fgets` + `sscanf`.""" +
cod(S_LIBROS), tema="Estructuras",
programa=Programa(C, [P(LIBROS_IN, "La Regenta 1300", descripcion="cinco clásicos")], solucion=S_LIBROS)),

Ejercicio("c-21", "Fibonacci en un fichero", r"""Guarda en un fichero los 10 primeros términos de Fibonacci y léelos después
para sumarlos.""",
r"""1. `fopen("fibonacci.txt", "w")` → `fprintf` de cada término → `fclose`.
2. `fopen(…, "r")` → `while (fscanf(f, "%ld", &x) == 1)` suma hasta que no quedan números → `fclose`.

Con 0, 1, 1, 2, 3, 5, 8, 13, 21, 34 la suma es **88** (si empiezas en 1, 1, 2…, sale 143; la app acepta los dos).""" + cod(S_FIBO),
tema="Ficheros", programa=Programa(C, [P(verificar=v_fibo, descripcion="suma de los 10 primeros")], solucion=S_FIBO)),

Ejercicio("c-22", "Gestor de notas: cargar el fichero y mejor/peor", r"""Amplía el gestor de notas (Ejemplo 20.1) para que cargue
los alumnos del fichero al empezar y muestre el mejor y el peor.

*En la app:* existe un `alumnos.txt` (Ana 7.50, Luis 4.25, Marta 9.00, Pablo 6.10). Al arrancar, tu programa debe imprimir
`Mejor: …` y `Peor: …`; luego se elige la opción 0 (salir).""",
r"""Dos funciones nuevas:
- **`cargar`**: abre `alumnos.txt` en modo `"r"`; si no existe (`NULL`) empieza con 0 alumnos; lee con
  `fscanf(f, "%29s %lf", …) == 2` mientras haya líneas (y como mucho MAX).
- **`mejor_y_peor`**: recorre guardando los índices del máximo y del mínimo.

`main` las llama antes del menú (y se añade la opción 5 para consultarlo cuando quieras).""" + cod(S_GESTOR), tema="Ficheros",
programa=Programa(C, [P("0", "mejor marta 9.00 peor luis 4.25", ficheros={"alumnos.txt": ALUMNOS}, descripcion="4 alumnos"),
                      P("0", "no hay alumnos", descripcion="sin fichero")], solucion=S_GESTOR)),
], icono="💻")
