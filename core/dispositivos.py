"""Periféricos simulados para los ejercicios de E/S (sensores, semáforo, horno, lector de códigos…).

Cada uno responde a sus direcciones (mapa común: lw/sw) o puertos (mapa separado: in/out) y apunta lo que
le hacen en `log`, para que la app pueda comprobar que el programa los maneja bien.
"""
from __future__ import annotations

from core.mips import Dispositivo, s32


class Registros(Dispositivo):
    """Base: un diccionario dirección → valor, con ganchos al leer/escribir."""
    def __init__(self, direcciones):
        self.dirs = set(direcciones)
        self.log = []           # ("R"/"W", dirección, valor)

    def leer(self, d):
        if d not in self.dirs:
            return None
        v = self.al_leer(d)
        self.log.append(("R", d, s32(v)))
        return v

    def escribir(self, d, v):
        if d not in self.dirs:
            return False
        self.log.append(("W", d, s32(v)))
        self.al_escribir(d, s32(v))
        return True

    def escrituras(self, d=None):
        return [v for t, dd, v in self.log if t == "W" and (d is None or dd == d)]

    def al_leer(self, d):
        return 0

    def al_escribir(self, d, v):
        pass


class SensorPiezas(Registros):
    """Ej. E/S 3: estado 0x100, control 0x104 (2 = medir), datos 0x108, 0x10C, 0x110."""
    def __init__(self, alto=10, ancho=20, largo=30, espera=3):
        super().__init__([0x100, 0x104, 0x108, 0x10C, 0x110])
        self.vals = {0x108: alto, 0x10C: ancho, 0x110: largo}
        self.espera, self.cuenta, self.midiendo, self.listo = espera, 0, False, False

    def al_escribir(self, d, v):
        if d == 0x104 and v == 2:
            self.midiendo, self.listo, self.cuenta = True, False, 0

    def al_leer(self, d):
        if d == 0x100:
            if self.midiendo:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.listo, self.midiendo = True, False
            return 1 if self.listo else 0
        return self.vals.get(d, 0) if self.listo else 0


class SensorTemperatura(Registros):
    """Ej. E/S 4: estado 0x100 (0 ocupado / 1 listo / −1 error), control 0x104 (2 = inicializar), datos 0x108."""
    def __init__(self, temperatura=25, error=False, espera=3):
        super().__init__([0x100, 0x104, 0x108])
        self.t, self.error, self.espera = temperatura, error, espera
        self.fase, self.cuenta, self.inicializado = "apagado", 0, False

    def al_escribir(self, d, v):
        if d == 0x104 and v == 2:
            self.fase, self.cuenta = "iniciando", 0

    def al_leer(self, d):
        if d == 0x108:
            return self.t if self.fase == "lectura_lista" else 0
        if d != 0x100:
            return 0
        self.cuenta += 1
        if self.fase == "iniciando":
            if self.cuenta >= self.espera:
                self.fase, self.cuenta, self.inicializado = "iniciado", 0, True
                return 1
            return 0
        if self.fase == "iniciado":           # ya se vio el 1 de «inicializado»: ahora se mide
            if self.error:
                return -1
            if self.cuenta >= self.espera:
                self.fase = "lectura_lista"
                return 1
            return 0
        if self.fase == "lectura_lista":
            return 1
        return 0


class LectorBarras(Registros):
    """Ej. E/S 5: datos 0x1000, control 0x1004 (111 = inicializar), estado 0x1008 (1 = hay código)."""
    def __init__(self, codigos=(11, 22, 33), espera=2):
        super().__init__([0x1000, 0x1004, 0x1008])
        self.codigos, self.espera = list(codigos), espera
        self.iniciado, self.cuenta, self.hay, self.leidos = False, 0, False, []

    def al_escribir(self, d, v):
        if d == 0x1004 and v == 111:
            self.iniciado = True

    def al_leer(self, d):
        if d == 0x1008:
            if self.iniciado and not self.hay and self.codigos:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.hay, self.cuenta = True, 0
            return 1 if self.hay else 0
        if d == 0x1000:
            if self.hay:
                self.hay = False
                c = self.codigos.pop(0)
                self.leidos.append(c)
                return c
            return 0
        return 0


class Semaforo(Registros):
    """Ej. E/S 6 (mapa separado): 1000 cuenta atrás, 1004 empezar, 1008 fin, 1012 color (100 rojo, 010 ámbar, 001 verde)."""
    def __init__(self, espera=3):
        super().__init__([1000, 1004, 1008, 1012])
        self.color, self.segundos, self.espera = None, 0, espera
        self.contando, self.cuenta, self.fases = False, 0, []      # (color, segundos)

    def al_escribir(self, d, v):
        if d == 1000:
            self.segundos = v
        elif d == 1012:
            self.color = v
        elif d == 1004 and v == 1:
            self.contando, self.cuenta = True, 0
            self.fases.append((self.color, self.segundos))

    def al_leer(self, d):
        if d == 1008:
            if self.contando:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.contando = False
            return 0 if self.contando else 1
        return {1000: self.segundos, 1012: self.color or 0}.get(d, 0)


class HornoAlarma(Registros):
    """Ej. E/S 8 (mapa separado): sensor 0x100 control (0 init, 1 leer), 0x104 datos, 0x108 estado (1 listo);
    alarma 0x200 control (1 on / 0 off), 0x204 estado."""
    def __init__(self, temperaturas=(80, 120, 130, 90, 101, 99), espera=2):
        super().__init__([0x100, 0x104, 0x108, 0x200, 0x204])
        self.temps, self.espera = list(temperaturas), espera
        self.ocupado, self.cuenta, self.t, self.alarma = False, 0, None, 0
        self.medidas = []        # (temperatura, alarma tras procesarla) — se rellena en la siguiente lectura
        self.inicializado = False

    def al_escribir(self, d, v):
        if d == 0x100:
            if v == 0:
                self.inicializado = True
            elif v == 1:
                if self.t is not None:
                    self.medidas.append((self.t, self.alarma))
                self.t = self.temps.pop(0) if self.temps else None
            self.ocupado, self.cuenta = True, 0
        elif d == 0x200:
            self.alarma = 1 if v else 0

    def al_leer(self, d):
        if d == 0x108:
            if self.ocupado:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.ocupado = False
            return 0 if self.ocupado else 1
        if d == 0x104:
            return self.t if self.t is not None else 0
        if d == 0x204:
            return self.alarma
        return 0


class SensorAgua(Registros):
    """Ej. E/S 10 (mapa separado): R_CONTROL 0x300 (ON = 1, OFF = 0), R_ESTADO 0x304 (MIDIENDO 0, NUEVO 1,
    ERROR 2), R_DATOS 0x308."""
    def __init__(self, n=100, error_en=None, espera=2):
        super().__init__([0x300, 0x304, 0x308])
        self.n, self.error_en, self.espera = n, error_en, espera
        self.activo, self.cuenta, self.nuevo, self.k = False, 0, False, 0

    def al_escribir(self, d, v):
        if d == 0x300:
            self.activo = v == 1

    def valor(self, k):
        return 1000 + 7 * k

    def al_leer(self, d):
        if d == 0x304:
            if not self.activo:
                return 0
            if self.error_en is not None and self.k >= self.error_en:
                return 2
            if not self.nuevo:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.nuevo, self.cuenta = True, 0
            return 1 if self.nuevo else 0
        if d == 0x308:
            if self.nuevo:
                self.nuevo = False
                v = self.valor(self.k)
                self.k += 1
                return v
            return 0
        return 0


class Microondas(Registros):
    """Ej. E/S 11 (mapa común): 1000 segundos, 1004 empezar cuenta, 1008 fin (1), 1012 potencia, 1016 encender (1/0)."""
    def __init__(self, espera=4):
        super().__init__([1000, 1004, 1008, 1012, 1016])
        self.segundos = self.potencia = 0
        self.encendido, self.contando, self.cuenta, self.espera = 0, False, 0, espera
        self.terminada = False
        self.apagado_tras_fin = None

    def al_escribir(self, d, v):
        if d == 1000:
            self.segundos = v
        elif d == 1012:
            self.potencia = v
        elif d == 1004 and v == 1:
            self.contando, self.cuenta, self.terminada = True, 0, False
        elif d == 1016:
            self.encendido = v
            if v == 0:
                self.apagado_tras_fin = self.terminada

    def al_leer(self, d):
        if d == 1008:
            if self.contando:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.contando, self.terminada = False, True
            return 1 if self.terminada else 0
        return {1000: self.segundos, 1012: self.potencia, 1016: self.encendido}.get(d, 0)


class Tensiometro(Registros):
    """Ej. E/S 12 (mapa común): 1000 empezar (1), 1004 fin (1), 1008 sistólica, 1012 diastólica."""
    def __init__(self, sis=120, dia=80, espera=3):
        super().__init__([1000, 1004, 1008, 1012])
        self.sis, self.dia, self.espera = sis, dia, espera
        self.midiendo, self.cuenta, self.listo = False, 0, False

    def al_escribir(self, d, v):
        if d == 1000 and v == 1:
            self.midiendo, self.cuenta, self.listo = True, 0, False

    def al_leer(self, d):
        if d == 1004:
            if self.midiendo:
                self.cuenta += 1
                if self.cuenta >= self.espera:
                    self.midiendo, self.listo = False, True
            return 1 if self.listo else 0
        if d == 1008:
            return self.sis if self.listo else 0
        if d == 1012:
            return self.dia if self.listo else 0
        return 0
