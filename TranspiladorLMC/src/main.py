import argparse
import os
from parser import analizar_pseudocodigo
from generator import generar_lmc
from utils import leer_lineas, escribir_texto, asegurar_directorio


OPCIONES_DESTINO = ["Harry", "Juan", "Anthony", "Luis"]


def main():
    ap = argparse.ArgumentParser(description="Transpilador de pseudo-código a LMC")
    ap.add_argument("--input", required=True, help="Ruta del archivo de pseudo-código de entrada")
    ap.add_argument("--output", required=False, help="Ruta del archivo LMC de salida")
    ap.add_argument("--dest", choices=OPCIONES_DESTINO, help="Carpeta destino dentro del proyecto")
    args = ap.parse_args()

    in_path = args.input
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"No existe el archivo de entrada: {in_path}")

    lineas = leer_lineas(in_path)
    operaciones = analizar_pseudocodigo(lineas)
    lmc = generar_lmc(operaciones)

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
            for i, name in enumerate(OPCIONES_DESTINO, start=1):
                print(f"  {i}. {name}")
            choice = input("Ingrese número (1-4): ").strip()
            try:
                idx = int(choice)
                if idx < 1 or idx > len(OPCIONES_DESTINO):
                    raise ValueError()
                dest_folder = OPCIONES_DESTINO[idx - 1]
            except Exception:
                # Valor por defecto
                dest_folder = OPCIONES_DESTINO[0]
                print(f"Selección inválida. Usando '{dest_folder}'.")

        out_dir = os.path.join(project_root, "output_lmc", dest_folder)
        asegurar_directorio(out_dir)
        out_path = os.path.join(out_dir, f"{base}.lmc")

    escribir_texto(out_path, lmc)
    print(f"Archivo LMC generado en: {out_path}")


if __name__ == "__main__":
    main()
