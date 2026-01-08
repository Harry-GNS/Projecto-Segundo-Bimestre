# TranspiladorLMC

Transpilador simple de pseudo-código (en español) a ensamblador LMC (Little Man Computer).

## Estructura

```
TranspiladorLMC/
├─ src/
│  ├─ main.py
│  ├─ parser.py
│  ├─ generator.py
│  └─ utils.py
├─ input_scripts/
├─ output_lmc/
├─ README.md
└─ requirements.txt
```

## Uso rápido

1. Coloca tu pseudo-código en `input_scripts/ejemplo1.txt`.
2. Ejecuta el transpilador:

```bash
python src/main.py --input "input_scripts/ejemplo1.txt" --output "output_lmc/ejemplo1.lmc"
```

Si omites `--output`, se crea automáticamente en `output_lmc/` con el mismo nombre.

## Formato de pseudo-código soportado

- Lectura: `LEER A`
- Impresión: `IMPRIMIR A`
- Asignaciones: `C = A + B`, `C = A - B`
- Condicional simple:
  - `SI A > B ENTONCES` … `SINO` …
  - `SI A < B ENTONCES` … `SINO` …
  - `SI A = B ENTONCES` … `SINO` …

Limitaciones: Anidación de `SI` mínima; se recomienda usar `SINO` y separar los bloques por líneas en blanco o continuar con instrucciones top‑nivel (p.ej., `IMPRIMIR`).

## Ejemplo

Entrada:
```
LEER A
LEER B
SI A > B ENTONCES
    C = A - B
SINO
    C = B - A
IMPRIMIR C
```

Salida LMC (generada):
```
INP
STA A
INP
STA B
LDA A
SUB B
BRZ ELSE1
BRP THEN1
ELSE1
LDA B
SUB A
STA C
BRA ENDIF1
THEN1
LDA A
SUB B
STA C
ENDIF1
LDA C
OUT
HLT
A DAT
B DAT
C DAT
```

Puedes pegar esto en un simulador LMC como el de 101computing (Peter Higginson) o el de York University para validarlo.

## Análisis comparativo sugerido

- Escenario 1: Genera código con el transpilador para algoritmos como multiplicación por sumas sucesivas o Fibonacci.
- Escenario 2: Escribe el mismo programa manualmente optimizando saltos y uso de memoria.
- Entregable: Tabla con número de instrucciones generadas y ciclos de reloj observados en el simulador.

## Requisitos

No hay dependencias externas. Python 3.9+.
