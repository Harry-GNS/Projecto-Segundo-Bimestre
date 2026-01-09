import os
from typing import List


def leer_lineas(ruta: str) -> List[str]:
    with open(ruta, 'r', encoding='utf-8') as f:
        return [linea.rstrip('\n') for linea in f]


def escribir_texto(ruta: str, contenido: str) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)


def asegurar_directorio(ruta: str) -> None:
    os.makedirs(ruta, exist_ok=True)
