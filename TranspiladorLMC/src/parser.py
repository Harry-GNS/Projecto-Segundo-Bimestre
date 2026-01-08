import re
from typing import List, Dict, Any

Token = Dict[str, Any]


def _is_assignment(line: str) -> bool:
    return re.match(r"^\s*[A-Za-z][\w]*\s*=\s*(?:[A-Za-z][\w]*|\d+)\s*[+\-]\s*(?:[A-Za-z][\w]*|\d+)\s*$", line) is not None


def _parse_assignment(line: str) -> Token:
    m = re.match(r"^\s*([A-Za-z][\w]*)\s*=\s*([A-Za-z][\w]*|\d+)\s*([+\-])\s*([A-Za-z][\w]*|\d+)\s*$", line)
    assert m
    dest, left, op, right = m.groups()
    return {"type": "assign", "dest": dest.upper(), "left": left.upper(), "op": op, "right": right.upper()}


def _is_read(line: str) -> bool:
    return re.match(r"^\s*LEER\s+[A-Za-z][\w]*\s*$", line, re.IGNORECASE) is not None


def _parse_read(line: str) -> Token:
    var = re.findall(r"LEER\s+([A-Za-z][\w]*)", line, flags=re.IGNORECASE)[0]
    return {"type": "read", "var": var.upper()}


def _is_print(line: str) -> bool:
    return re.match(r"^\s*IMPRIMIR\s+[A-Za-z][\w]*\s*$", line, re.IGNORECASE) is not None


def _parse_print(line: str) -> Token:
    var = re.findall(r"IMPRIMIR\s+([A-Za-z][\w]*)", line, flags=re.IGNORECASE)[0]
    return {"type": "print", "var": var.upper()}


def _is_if(line: str) -> bool:
    return re.match(r"^\s*SI\s+\w+\s*(=|>|<)\s*\w+\s+ENTONCES\s*$", line, re.IGNORECASE) is not None


def _parse_if_header(line: str) -> Dict[str, str]:
    m = re.match(r"^\s*SI\s+(\w+)\s*(=|>|<)\s*(\w+)\s+ENTONCES\s*$", line, re.IGNORECASE)
    assert m
    left, op, right = m.groups()
    return {"left": left.upper(), "op": op, "right": right.upper()}


def parse_pseudocode(lines: List[str]) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if _is_read(line):
            tokens.append(_parse_read(line))
            i += 1
            continue
        if _is_print(line):
            tokens.append(_parse_print(line))
            i += 1
            continue
        if _is_assignment(line):
            tokens.append(_parse_assignment(line))
            i += 1
            continue
        if _is_if(line):
            cond = _parse_if_header(line)
            i += 1
            then_ops: List[Token] = []
            while i < n and not re.match(r"^\s*SINO\s*$", lines[i], re.IGNORECASE):
                inner = lines[i].strip()
                if not inner:
                    i += 1
                    continue
                if _is_read(inner):
                    then_ops.append(_parse_read(inner))
                elif _is_print(inner):
                    then_ops.append(_parse_print(inner))
                elif _is_assignment(inner):
                    then_ops.append(_parse_assignment(inner))
                elif _is_if(inner):
                    nested = parse_pseudocode(lines[i:])
                    then_ops.extend(nested)
                    # move i to end since we consumed remaining lines
                    i = n
                    break
                else:
                    # unknown line inside THEN, skip gracefully
                    pass
                i += 1
            else_ops: List[Token] = []
            if i < n and re.match(r"^\s*SINO\s*$", lines[i], re.IGNORECASE):
                i += 1
                while i < n:
                    inner = lines[i].strip()
                    if not inner:
                        break
                    # Heuristic: stop ELSE when a new top-level begins
                    if _is_if(inner) or _is_read(inner) or _is_print(inner):
                        break
                    if _is_assignment(inner):
                        else_ops.append(_parse_assignment(inner))
                        i += 1
                        continue
                    # unknown -> stop
                    break
            tokens.append({"type": "if", "cond": cond, "then": then_ops, "else": else_ops})
            continue
        # unknown top-level line -> skip
        i += 1
    return tokens
