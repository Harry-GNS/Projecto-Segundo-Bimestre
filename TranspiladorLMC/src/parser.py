import re
from typing import List, Dict, Any

Token = Dict[str, Any]


def _es_asignacion(linea: str) -> bool:
    return re.match(r"^\s*[A-Za-z][\w]*\s*=\s*(?:[A-Za-z][\w]*|\d+)\s*[+\-*/]\s*(?:[A-Za-z][\w]*|\d+)\s*$", linea) is not None


def _parsear_asignacion(linea: str) -> Token:
    m = re.match(r"^\s*([A-Za-z][\w]*)\s*=\s*([A-Za-z][\w]*|\d+)\s*([+\-*/])\s*([A-Za-z][\w]*|\d+)\s*$", linea)
    assert m
    destino, izquierda, op, derecha = m.groups()
    return {"tipo": "asignacion", "destino": destino.upper(), "izquierda": izquierda.upper(), "op": op, "derecha": derecha.upper()}


def _es_leer(linea: str) -> bool:
    return re.match(r"^\s*LEER\s+[A-Za-z][\w]*\s*$", linea, re.IGNORECASE) is not None


def _parsear_leer(linea: str) -> Token:
    var = re.findall(r"LEER\s+([A-Za-z][\w]*)", linea, flags=re.IGNORECASE)[0]
    return {"tipo": "leer", "var": var.upper()}


def _es_imprimir(linea: str) -> bool:
    return re.match(r"^\s*IMPRIMIR\s+[A-Za-z][\w]*\s*$", linea, re.IGNORECASE) is not None


def _parsear_imprimir(linea: str) -> Token:
    var = re.findall(r"IMPRIMIR\s+([A-Za-z][\w]*)", linea, flags=re.IGNORECASE)[0]
    return {"tipo": "imprimir", "var": var.upper()}


def _es_si(linea: str) -> bool:
    return re.match(r"^\s*SI\s+\w+\s*(>=|<=|!=|=|>|<)\s*\w+\s+ENTONCES\s*$", linea, re.IGNORECASE) is not None


def _parsear_encabezado_si(linea: str) -> Dict[str, str]:
    m = re.match(r"^\s*SI\s+(\w+)\s*(>=|<=|!=|=|>|<)\s*(\w+)\s+ENTONCES\s*$", linea, re.IGNORECASE)
    assert m
    izquierda, op, derecha = m.groups()
    return {"izquierda": izquierda.upper(), "op": op, "derecha": derecha.upper()}


def _es_mientras(linea: str) -> bool:
    return re.match(r"^\s*MIENTRAS\s+\w+\s*(>=|<=|!=|=|>|<)\s*\w+\s+HACER\s*$", linea, re.IGNORECASE) is not None


def _parsear_encabezado_mientras(linea: str) -> Dict[str, str]:
    m = re.match(r"^\s*MIENTRAS\s+(\w+)\s*(>=|<=|!=|=|>|<)\s*(\w+)\s+HACER\s*$", linea, re.IGNORECASE)
    assert m
    izquierda, op, derecha = m.groups()
    return {"izquierda": izquierda.upper(), "op": op, "derecha": derecha.upper()}


def analizar_pseudocodigo(lineas: List[str]) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(lineas)
    while i < n:
        linea = lineas[i].strip()
        if not linea:
            i += 1
            continue
        if _es_leer(linea):
            tokens.append(_parsear_leer(linea))
            i += 1
            continue
        if _es_imprimir(linea):
            tokens.append(_parsear_imprimir(linea))
            i += 1
            continue
        if _es_asignacion(linea):
            tokens.append(_parsear_asignacion(linea))
            i += 1
            continue
        if _es_si(linea):
            condicion = _parsear_encabezado_si(linea)
            i += 1
            entonces_ops: List[Token] = []
            while i < n and not re.match(r"^\s*SINO\s*$", lineas[i], re.IGNORECASE):
                interior = lineas[i].strip()
                if not interior:
                    i += 1
                    continue
                if _es_leer(interior):
                    entonces_ops.append(_parsear_leer(interior))
                elif _es_imprimir(interior):
                    entonces_ops.append(_parsear_imprimir(interior))
                elif _es_asignacion(interior):
                    entonces_ops.append(_parsear_asignacion(interior))
                elif _es_mientras(interior):
                    # Parse nested 'mientras' bloque completo
                    # Encontrar el cierre correspondiente 'FIN MIENTRAS'
                    depth = 1
                    j = i + 1
                    while j < n and depth > 0:
                        linea_j = lineas[j].strip()
                        if _es_mientras(linea_j):
                            depth += 1
                        elif re.match(r"^\s*FIN\s+MIENTRAS\s*$", linea_j, re.IGNORECASE):
                            depth -= 1
                        j += 1
                    sub_tokens = analizar_pseudocodigo(lineas[i:j])
                    entonces_ops.extend(sub_tokens)
                    i = j
                    continue
                elif _es_si(interior):
                    anidado = analizar_pseudocodigo(lineas[i:])
                    entonces_ops.extend(anidado)
                    i = n
                    break
                else:
                    pass
                i += 1
            sino_ops: List[Token] = []
            if i < n and re.match(r"^\s*SINO\s*$", lineas[i], re.IGNORECASE):
                i += 1
                while i < n:
                    interior = lineas[i].strip()
                    if not interior:
                        break
                    if _es_leer(interior):
                        sino_ops.append(_parsear_leer(interior))
                        i += 1
                        continue
                    if _es_imprimir(interior):
                        sino_ops.append(_parsear_imprimir(interior))
                        i += 1
                        continue
                    if _es_asignacion(interior):
                        sino_ops.append(_parsear_asignacion(interior))
                        i += 1
                        continue
                    if _es_mientras(interior):
                        depth = 1
                        j = i + 1
                        while j < n and depth > 0:
                            linea_j = lineas[j].strip()
                            if _es_mientras(linea_j):
                                depth += 1
                            elif re.match(r"^\s*FIN\s+MIENTRAS\s*$", linea_j, re.IGNORECASE):
                                depth -= 1
                            j += 1
                        sub_tokens = analizar_pseudocodigo(lineas[i:j])
                        sino_ops.extend(sub_tokens)
                        i = j
                        continue
                    if _es_si(interior):
                        anidado = analizar_pseudocodigo(lineas[i:])
                        sino_ops.extend(anidado)
                        i = n
                        break
                    break
            tokens.append({"tipo": "si", "condicion": condicion, "entonces": entonces_ops, "sino": sino_ops})
            continue
        if _es_mientras(linea):
            condicion = _parsear_encabezado_mientras(linea)
            i += 1
            cuerpo_ops: List[Token] = []
            while i < n and not re.match(r"^\s*FIN\s+MIENTRAS\s*$", lineas[i], re.IGNORECASE):
                interior = lineas[i].strip()
                if not interior:
                    i += 1
                    continue
                if _es_leer(interior):
                    cuerpo_ops.append(_parsear_leer(interior))
                elif _es_imprimir(interior):
                    cuerpo_ops.append(_parsear_imprimir(interior))
                elif _es_asignacion(interior):
                    cuerpo_ops.append(_parsear_asignacion(interior))
                elif _es_si(interior):
                    # Parse nested 'si' usando analizar_pseudocodigo desde aquí hasta fin del bloque si
                    anidado = analizar_pseudocodigo(lineas[i:])
                    cuerpo_ops.extend(anidado)
                    i = n
                    break
                elif _es_mientras(interior):
                    # Soportar anidamiento de mientras
                    depth = 1
                    j = i + 1
                    while j < n and depth > 0:
                        linea_j = lineas[j].strip()
                        if _es_mientras(linea_j):
                            depth += 1
                        elif re.match(r"^\s*FIN\s+MIENTRAS\s*$", linea_j, re.IGNORECASE):
                            depth -= 1
                        j += 1
                    sub_tokens = analizar_pseudocodigo(lineas[i:j])
                    cuerpo_ops.extend(sub_tokens)
                    i = j
                    continue
                i += 1
            # Saltar 'FIN MIENTRAS'
            if i < n and re.match(r"^\s*FIN\s+MIENTRAS\s*$", lineas[i], re.IGNORECASE):
                i += 1
            tokens.append({"tipo": "mientras", "condicion": condicion, "cuerpo": cuerpo_ops})
            continue
        i += 1
    return tokens
