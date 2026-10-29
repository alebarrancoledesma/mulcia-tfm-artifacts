# Artefactos experimentales

Entradas y resultados históricos utilizados en el TFM, ordenados según la secuencia del trabajo. El código ejecutable se mantiene en los repositorios del pipeline, GRASP y los forks de los planificadores.

## Entradas

```text
inputs/
├── 01-classical-planning/   referencia a las entradas conservadas en el fork de Corrêa
├── 02-numeric-planning/
│   ├── 01-cvrplib-original/ instancias E/P y soluciones publicadas por CVRPLIB
│   ├── 02-pddl-converted/   dominio y problemas PDDL numéricos convertidos
│   └── 03-splits/           conjuntos de prompt, desarrollo y test
└── 03-grasp/
    ├── 01-instances/        instancias CVRPLIB utilizadas por GRASP
    └── 02-protocol/         familias, instancias y parámetros del experimento
```

La conversión de CVRPLIB a PDDL se realizó con `mulcia-tfm-didp-models/cvrp/cvrp_to_pddl.py`. Se conservan las 37 instancias `.vrp`, sus 37 soluciones de referencia y los 38 ficheros `.pddl` resultantes (dominio incluido), de modo que pueda comprobarse la transformación.

## Resultados

```text
outputs/
├── 01-classical-planning/
│   ├── 01-correa-reproduction/       validación sobre Transport
│   └── 02-cvrp-strips-adaptation/    primera adaptación proposicional al CVRP
├── 02-numeric-planning/
│   ├── 01-preliminary-model-prompt-selection/
│   ├── 02-candidate-selection/
│   └── 03-cross-evaluation/
└── 03-grasp/
    ├── 01-preliminary/                 tres subetapas preliminares numeradas
    ├── 02-candidate-selection/
    └── 03-cross-evaluation/
```

Las siete tandas de la fase preliminar numérica están numeradas en orden cronológico. Incluyen respuestas de GPT y DeepSeek, prompts, código Rust, registros de compilación y métricas disponibles. `PROCESS.md` resume qué se modificó y observó en cada tanda.

La primera etapa contiene tanto la reproducción reducida de Corrêa et al. con Transport como la adaptación posterior CVRP-STRIPS. Sus métricas, heurísticas, informes y planes se conservan por separado en las subcarpetas 01 y 02.

Los ficheros de `outputs/` son los resultados históricos empleados en la memoria: no se regeneran al ejecutar el pipeline actual. En los experimentos con candidatos, cada carpeta numerada contiene el prompt, el código recibido y su descripción `what`/`why`; `metrics.csv` recoge las mediciones y `ranking.csv` el orden de selección.
