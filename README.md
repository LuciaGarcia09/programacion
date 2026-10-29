# 🌸 ProgLucía

Mi app de estudio para **Fundamentos de Computadores** (teoría y práctica), **Programación en C** y **Programación en Python**.

- 📖 **Teoría** de todos los temas, con analogías y ejemplos que se ejecutan con ▶ Ejecutar.
- ✍️ **197 ejercicios** de las hojas, resueltos paso a paso, con **«Corrígeme»**: escribe tu programa (MIPS, C o Python) o tus resultados y la app te dice qué está bien y qué falla.
- 🧪 **Herramientas**: simulador MIPS (con dispositivos de E/S), codificador de instrucciones, bases, enteros, IEEE 754, caché, memoria virtual, segmentación, rendimiento, discos y consistencia.
- 💻 Compilador de C y 🐍 intérprete de Python integrados.
- 📚 Guías en PDF, buscador, erratas y progreso.

## Abrirla en el ordenador (Windows)
Doble clic en `iniciar.bat` (la primera vez instala todo). Para C hace falta `gcc` (por ejemplo, con MSYS2 o MinGW).

## Abrirla a mano
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tests
```bash
pytest -q
```
