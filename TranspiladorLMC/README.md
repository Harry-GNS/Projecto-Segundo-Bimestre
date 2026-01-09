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
python src/main.py --input "input_scripts/ejemplo1.txt" --dest Harry
```

- `--dest` (Harry/Juan/Anthony/Luis): guarda en `output_lmc/<dest>`.
- Si omites `--output`, se genera automáticamente usando el nombre del input.

- GUI:

```bash
python src/gui.py
```

## Carpetas

- input_scripts/: archivos de entrada (.txt)
- output_lmc/: resultados LMC (.lmc) por usuario
- src/: código del transpilador

## Qué soporta

- Instrucciones: `LEER X`, `IMPRIMIR X`
- Asignaciones: `Z = A + B`, `Z = A - 3`, `Z = A * B`, `Z = A / B` (una operación por línea)
- Condicionales: `SI A > B ENTONCES ... SINO ...`
	- Comparadores: `>`, `<`, `=`, `>=`, `<=`, `!=`
	- En `ENTONCES` y `SINO` se permiten `LEER`, `IMPRIMIR`, asignaciones y `SI` anidado simple

Notas:
- La multiplicación se implementa por sumas sucesivas (sin subrutinas externas).
- La división se implementa por restas sucesivas; si `B = 0`, el cociente queda en `0`.
- Aún no soporta paréntesis/múltiples operaciones por asignación, bucles (`MIENTRAS/PARA`) ni división.
