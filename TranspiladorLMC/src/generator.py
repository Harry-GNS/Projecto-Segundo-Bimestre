from typing import List, Dict, Any, Tuple


def _es_numero(token: str) -> bool:
    return token.isdigit()


def _recolectar_simbolos(operaciones: List[Dict[str, Any]]) -> Tuple[set, Dict[int, str]]:
    conjunto_vars = set()
    constantes: Dict[int, str] = {}

    def agregar_token(tok: str):
        nonlocal conjunto_vars, constantes
        if _es_numero(tok):
            valor = int(tok)
            if valor not in constantes:
                constantes[valor] = f"CTE{valor}"
        else:
            conjunto_vars.add(tok.upper())

    for op in operaciones:
        t = op["tipo"]
        if t == "leer" or t == "imprimir":
            agregar_token(op["var"])
        elif t == "asignacion":
            agregar_token(op["destino"])
            agregar_token(op["izquierda"])
            agregar_token(op["derecha"])
            if op.get("op") == "*":
                # Temporal para multiplicación y constantes 0 y 1
                conjunto_vars.add("TMPMUL")
                if 0 not in constantes:
                    constantes[0] = "CTE0"
                if 1 not in constantes:
                    constantes[1] = "CTE1"
        elif t == "si":
            agregar_token(op["condicion"]["izquierda"])
            agregar_token(op["condicion"]["derecha"])
            vars_int, consts_int = _recolectar_simbolos(op["entonces"])
            conjunto_vars |= vars_int
            for k, v in consts_int.items():
                constantes.setdefault(k, v)
            vars_int, consts_int = _recolectar_simbolos(op["sino"])
            conjunto_vars |= vars_int
            for k, v in consts_int.items():
                constantes.setdefault(k, v)
    return conjunto_vars, constantes


def _etiqueta_mem(token: str, constantes: Dict[int, str]) -> str:
    if _es_numero(token):
        return constantes[int(token)]
    return token.upper()


def _gen_asignacion(op: Dict[str, Any], constantes: Dict[int, str]) -> List[str]:
    lineas: List[str] = []
    lineas.append(f"LDA {_etiqueta_mem(op['izquierda'], constantes)}")
    if op["op"] == "+":
        lineas.append(f"ADD {_etiqueta_mem(op['derecha'], constantes)}")
    elif op["op"] == "-":
        lineas.append(f"SUB {_etiqueta_mem(op['derecha'], constantes)}")
    else:  # '*' manejado fuera
        return []
    lineas.append(f"STA {_etiqueta_mem(op['destino'], constantes)}")
    return lineas


def _gen_multiplicacion(op: Dict[str, Any], constantes: Dict[int, str]) -> List[str]:
    destino = _etiqueta_mem(op['destino'], constantes)
    izq = _etiqueta_mem(op['izquierda'], constantes)  # multiplicando
    der = _etiqueta_mem(op['derecha'], constantes)    # multiplicador

    # Asegurar CTE0 y CTE1
    if 0 not in constantes:
        constantes[0] = "CTE0"
    if 1 not in constantes:
        constantes[1] = "CTE1"

    tmp = "TMPMUL"
    # Etiquetas únicas
    idx = _gen_op._ix_etq
    etq_loop = f"MULT{idx}"
    etq_fin = f"FINMULT{idx}"
    _gen_op._ix_etq += 1

    lineas: List[str] = []
    # destino = 0
    lineas.append(f"LDA {constantes[0]}")
    lineas.append(f"STA {destino}")
    # tmp = der
    lineas.append(f"LDA {der}")
    lineas.append(f"STA {tmp}")
    # loop
    lineas.append(f"{etq_loop} LDA {tmp}")
    lineas.append(f"BRZ {etq_fin}")
    lineas.append(f"LDA {destino}")
    lineas.append(f"ADD {izq}")
    lineas.append(f"STA {destino}")
    lineas.append(f"LDA {tmp}")
    lineas.append(f"SUB {constantes[1]}")
    lineas.append(f"STA {tmp}")
    lineas.append(f"BRA {etq_loop}")
    lineas.append(f"{etq_fin} LDA {destino}")  # etiqueta de fin (no cambia valor)
    return lineas


def _gen_si(op: Dict[str, Any], indice_etq: int, constantes: Dict[int, str]) -> Tuple[List[str], int]:
    lineas: List[str] = []
    izquierda = _etiqueta_mem(op["condicion"]["izquierda"], constantes)
    derecha = _etiqueta_mem(op["condicion"]["derecha"], constantes)
    etq_entonces = f"ENTONCES{indice_etq}"
    etq_sino = f"SINO{indice_etq}"
    etq_finsi = f"FINSI{indice_etq}"
    cmp = op["condicion"]["op"]
    if cmp == ">":
        lineas.append(f"LDA {izquierda}")
        lineas.append(f"SUB {derecha}")
        lineas.append(f"BRZ {etq_sino}")
        lineas.append(f"BRP {etq_entonces}")
        primero = True
        for interior in op["sino"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_sino} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        lineas.append(f"BRA {etq_finsi}")
        primero = True
        for interior in op["entonces"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_entonces} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        _gen_op._etiquetas_pendientes.append(etq_finsi)
    elif cmp == "<":
        lineas.append(f"LDA {derecha}")
        lineas.append(f"SUB {izquierda}")
        lineas.append(f"BRZ {etq_sino}")
        lineas.append(f"BRP {etq_entonces}")
        primero = True
        for interior in op["sino"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_sino} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        lineas.append(f"BRA {etq_finsi}")
        primero = True
        for interior in op["entonces"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_entonces} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        _gen_op._etiquetas_pendientes.append(etq_finsi)
    elif cmp == "=":
        lineas.append(f"LDA {izquierda}")
        lineas.append(f"SUB {derecha}")
        lineas.append(f"BRZ {etq_entonces}")
        lineas.append(f"BRA {etq_sino}")
        primero = True
        for interior in op["entonces"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_entonces} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        lineas.append(f"BRA {etq_finsi}")
        primero = True
        for interior in op["sino"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_sino} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        _gen_op._etiquetas_pendientes.append(etq_finsi)
    elif cmp == ">=":
        lineas.append(f"LDA {izquierda}")
        lineas.append(f"SUB {derecha}")
        lineas.append(f"BRZ {etq_entonces}")
        lineas.append(f"BRP {etq_entonces}")
        lineas.append(f"BRA {etq_sino}")
        primero = True
        for interior in op["entonces"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_entonces} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        lineas.append(f"BRA {etq_finsi}")
        primero = True
        for interior in op["sino"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_sino} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        _gen_op._etiquetas_pendientes.append(etq_finsi)
    elif cmp == "<=":
        lineas.append(f"LDA {derecha}")
        lineas.append(f"SUB {izquierda}")
        lineas.append(f"BRZ {etq_entonces}")
        lineas.append(f"BRP {etq_entonces}")
        lineas.append(f"BRA {etq_sino}")
        primero = True
        for interior in op["entonces"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_entonces} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        lineas.append(f"BRA {etq_finsi}")
        primero = True
        for interior in op["sino"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_sino} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        _gen_op._etiquetas_pendientes.append(etq_finsi)
    elif cmp == "!=":
        lineas.append(f"LDA {izquierda}")
        lineas.append(f"SUB {derecha}")
        lineas.append(f"BRZ {etq_sino}")
        lineas.append(f"BRA {etq_entonces}")
        primero = True
        for interior in op["entonces"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_entonces} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        lineas.append(f"BRA {etq_finsi}")
        primero = True
        for interior in op["sino"]:
            gen = _gen_op(interior, constantes)
            if gen:
                if primero:
                    gen[0] = f"{etq_sino} {gen[0]}"
                    primero = False
                lineas.extend(gen)
        _gen_op._etiquetas_pendientes.append(etq_finsi)
    return lineas, indice_etq + 1


def _gen_op(op: Dict[str, Any], constantes: Dict[int, str]) -> List[str]:
    t = op["tipo"]
    if t == "leer":
        lineas = ["INP", f"STA {_etiqueta_mem(op['var'], constantes)}"]
        return _adjuntar_etiqueta_pendiente(lineas)
    if t == "imprimir":
        lineas = [f"LDA {_etiqueta_mem(op['var'], constantes)}", "OUT"]
        return _adjuntar_etiqueta_pendiente(lineas)
    if t == "asignacion":
        if op["op"] == "*":
            # Añadir tmp y constantes a símbolos para DAT
            _gen_op._vars_tmp.add("TMPMUL")
            lineas = _gen_multiplicacion(op, constantes)
            return _adjuntar_etiqueta_pendiente(lineas)
        else:
            lineas = _gen_asignacion(op, constantes)
            return _adjuntar_etiqueta_pendiente(lineas)
    if t == "si":
        lineas, nuevo_ix = _gen_si(op, _gen_op._ix_etq, constantes)
        _gen_op._ix_etq = nuevo_ix
        return lineas
    return []

_gen_op._ix_etq = 1
_gen_op._etiquetas_pendientes = []
_gen_op._vars_tmp = set()


def _adjuntar_etiqueta_pendiente(lineas: List[str]) -> List[str]:
    if _gen_op._etiquetas_pendientes and lineas:
        etq = _gen_op._etiquetas_pendientes.pop(0)
        lineas[0] = f"{etq} {lineas[0]}"
    return lineas


def generar_lmc(operaciones: List[Dict[str, Any]]) -> str:
    conjunto_vars, constantes = _recolectar_simbolos(operaciones)
    _gen_op._ix_etq = 1
    _gen_op._etiquetas_pendientes = []
    _gen_op._vars_tmp = set()
    codigo: List[str] = []
    for op in operaciones:
        codigo.extend(_gen_op(op, constantes))
    codigo.append("HLT")
    # Incluir temporales si se usaron
    conjunto_total = set(conjunto_vars) | set(_gen_op._vars_tmp)
    for v in sorted(conjunto_total):
        codigo.append(f"{v} DAT")
    for valor, etq in sorted(constantes.items()):
        codigo.append(f"{etq} DAT {valor}")
    return "\n".join(codigo)
