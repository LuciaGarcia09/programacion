from core.diagnostico import diagnosticar, explicar_error_ejecucion


def test_errores_tipicos():
    cod = "n = int(input())\nif n = 0:\n  print(f{n} es cero)\n"
    m, sintaxis = diagnosticar(cod)
    assert sintaxis and "Línea 2" in m and "==" in m and 'print(f"{n} es cero")' in m


def test_codigo_bien_sin_avisos():
    assert diagnosticar('x = 3\nif x == 3:\n    print(f"{x} vale", x)\nelse:\n    print("no")\n') == ("", False)


def test_int_con_decimal():
    assert "float" in explicar_error_ejecucion("ValueError: invalid literal for int() with base 10: '-2.5'")
