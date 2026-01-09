import argparse
import os
from parser import parse_pseudocode
from generator import generate_lmc
from utils import read_lines, write_text, ensure_dir


DEST_CHOICES = ["Harry", "Juan", "Anthony", "Luis"]


def main():
    ap = argparse.ArgumentParser(description="Transpilador de pseudo-código a LMC")
    ap.add_argument("--input", required=True, help="Ruta del archivo de pseudo-código de entrada")
    ap.add_argument("--output", required=False, help="Ruta del archivo LMC de salida")
    ap.add_argument("--dest", choices=DEST_CHOICES, help="Carpeta destino dentro del proyecto")
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
        project_root = os.path.dirname(os.path.dirname(__file__))
        # Elegir carpeta destino
        if args.dest:
            dest_folder = args.dest
        else:
            print("Seleccione carpeta destino:")
            for i, name in enumerate(DEST_CHOICES, start=1):
                print(f"  {i}. {name}")
            choice = input("Ingrese número (1-4): ").strip()
            try:
                idx = int(choice)
                if idx < 1 or idx > len(DEST_CHOICES):
                    raise ValueError()
                dest_folder = DEST_CHOICES[idx - 1]
            except Exception:
                # Valor por defecto
                dest_folder = DEST_CHOICES[0]
                print(f"Selección inválida. Usando '{dest_folder}'.")

        out_dir = os.path.join(project_root, "output_lmc", dest_folder)
        ensure_dir(out_dir)
        out_path = os.path.join(out_dir, f"{base}.lmc")

    write_text(out_path, lmc)
    print(f"Archivo LMC generado en: {out_path}")


if __name__ == "__main__":
    main()
