from typing import List, Dict, Any, Tuple


def _is_number(token: str) -> bool:
    return token.isdigit()


def _collect_symbols(ops: List[Dict[str, Any]]) -> Tuple[set, Dict[int, str]]:
    vars_set = set()
    consts: Dict[int, str] = {}
    def add_token(tok: str):
        nonlocal vars_set, consts
        if _is_number(tok):
            val = int(tok)
            if val not in consts:
                consts[val] = f"CONST{val}"
        else:
            vars_set.add(tok.upper())
    for op in ops:
        t = op["type"]
        if t == "read" or t == "print":
            add_token(op["var"]) 
        elif t == "assign":
            add_token(op["dest"])
            add_token(op["left"]) 
            add_token(op["right"]) 
        elif t == "if":
            add_token(op["cond"]["left"]) 
            add_token(op["cond"]["right"]) 
            inner_vars, inner_consts = _collect_symbols(op["then"]) 
            vars_set |= inner_vars
            for k, v in inner_consts.items():
                consts.setdefault(k, v)
            inner_vars, inner_consts = _collect_symbols(op["else"]) 
            vars_set |= inner_vars
            for k, v in inner_consts.items():
                consts.setdefault(k, v)
    return vars_set, consts


def _mem_label(token: str, consts: Dict[int, str]) -> str:
    if _is_number(token):
        return consts[int(token)]
    return token.upper()


def _gen_assign(op: Dict[str, Any], consts: Dict[int, str]) -> List[str]:
    lines: List[str] = []
    lines.append(f"LDA {_mem_label(op['left'], consts)}")
    if op["op"] == "+":
        lines.append(f"ADD {_mem_label(op['right'], consts)}")
    else:
        lines.append(f"SUB {_mem_label(op['right'], consts)}")
    lines.append(f"STA {_mem_label(op['dest'], consts)}")
    return lines


def _gen_if(op: Dict[str, Any], label_ix: int, consts: Dict[int, str]) -> Tuple[List[str], int]:
    lines: List[str] = []
    left = _mem_label(op["cond"]["left"], consts)
    right = _mem_label(op["cond"]["right"], consts)
    then_lbl = f"THEN{label_ix}"
    else_lbl = f"ELSE{label_ix}"
    end_lbl = f"ENDIF{label_ix}"
    cmp = op["cond"]["op"]
    if cmp == ">":
        lines.append(f"LDA {left}")
        lines.append(f"SUB {right}")
        lines.append(f"BRZ {else_lbl}")
        lines.append(f"BRP {then_lbl}")
        lines.append(f"{else_lbl}")
        for inner in op["else"]:
            lines.extend(_gen_op(inner, consts))
        lines.append(f"BRA {end_lbl}")
        lines.append(f"{then_lbl}")
        for inner in op["then"]:
            lines.extend(_gen_op(inner, consts))
        lines.append(f"{end_lbl}")
    elif cmp == "<":
        lines.append(f"LDA {right}")
        lines.append(f"SUB {left}")
        lines.append(f"BRZ {else_lbl}")
        lines.append(f"BRP {then_lbl}")
        lines.append(f"{else_lbl}")
        for inner in op["else"]:
            lines.extend(_gen_op(inner, consts))
        lines.append(f"BRA {end_lbl}")
        lines.append(f"{then_lbl}")
        for inner in op["then"]:
            lines.extend(_gen_op(inner, consts))
        lines.append(f"{end_lbl}")
    else:  # '='
        lines.append(f"LDA {left}")
        lines.append(f"SUB {right}")
        lines.append(f"BRZ {then_lbl}")
        lines.append(f"BRA {else_lbl}")
        lines.append(f"{then_lbl}")
        for inner in op["then"]:
            lines.extend(_gen_op(inner, consts))
        lines.append(f"BRA {end_lbl}")
        lines.append(f"{else_lbl}")
        for inner in op["else"]:
            lines.extend(_gen_op(inner, consts))
        lines.append(f"{end_lbl}")
    return lines, label_ix + 1


def _gen_op(op: Dict[str, Any], consts: Dict[int, str]) -> List[str]:
    t = op["type"]
    if t == "read":
        return ["INP", f"STA {_mem_label(op['var'], consts)}"]
    if t == "print":
        return [f"LDA {_mem_label(op['var'], consts)}", "OUT"]
    if t == "assign":
        return _gen_assign(op, consts)
    if t == "if":
        lines, _ = _gen_if(op, _gen_op._lbl_ix, consts)
        _gen_op._lbl_ix = _ + 0  # keep updated
        return lines
    return []

_gen_op._lbl_ix = 1


def generate_lmc(ops: List[Dict[str, Any]]) -> str:
    vars_set, consts = _collect_symbols(ops)
    _gen_op._lbl_ix = 1
    code: List[str] = []
    for op in ops:
        code.extend(_gen_op(op, consts))
    code.append("HLT")
    for v in sorted(vars_set):
        code.append(f"{v} DAT")
    for val, lbl in sorted(consts.items()):
        code.append(f"{lbl} DAT {val}")
    return "\n".join(code)
