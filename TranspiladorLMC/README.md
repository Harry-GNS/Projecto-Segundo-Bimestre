# TranspiladorLMC

Transpila pseudo‑código en español a ensamblador LMC (Little Man Computer).

## Instalación

- Python 3.9+
- Instala dependencias:

```bash
pip install -r requirements.txt
```

## Uso rápido

- CLI:

```bash
python src/main.py --input "input_scripts/ejemplo1.txt" --output "output_lmc/ejemplo1.lmc"
```

Si omites `--output`, el archivo se crea automáticamente en `output_lmc/`.

- GUI:

```bash
python src/gui.py
```

## Carpetas

- input_scripts/: archivos de entrada (.txt)
- output_lmc/: resultados LMC (.lmc)
- src/: código del transpilador
