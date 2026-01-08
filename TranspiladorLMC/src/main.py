import argparse
import os
from parser import parse_pseudocode
from generator import generate_lmc
from utils import read_lines, write_text, ensure_dir


def main():
    ap = argparse.ArgumentParser(description="Transpilador de pseudo-código a LMC")
    ap.add_argument("--input", required=True, help="Ruta del archivo de pseudo-código de entrada")
    ap.add_argument("--output", required=False, help="Ruta del archivo LMC de salida")
    args = ap.parse_args()

    in_path = args.input
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"No existe el archivo de entrada: {in_path}")

    lines = read_lines(in_path)
    ops = parse_pseudocode(lines)
    lmc = generate_lmc(ops)

    if args.output:
        out_path = args.output
    else:
        base = os.path.splitext(os.path.basename(in_path))[0]
        out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output_lmc")
        ensure_dir(out_dir)
        out_path = os.path.join(out_dir, f"{base}.lmc")

    write_text(out_path, lmc)
    print(f"Archivo LMC generado en: {out_path}")


if __name__ == "__main__":
    main()
