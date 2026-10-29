# Heurística generada por LLM para CVRP-STRIPS (candidata 01)

Artefacto: `01 - cvrp-strips-heuristic.py`. Una candidata; no hay selección entre un conjunto de ~25.

## Metadatos

| Ítem | Valor |
|---|---|
| Fecha | 2026-09-05 |
| Dominio | `cvrp-strips` (mismo `domain.pddl` que `transport`; instancias modo B, goal open) |
| Generador | `llm-heuristics.py`, prompt NeurIPS 2025 (sin ablación) |
| LLM | DeepSeek V4 Flash (`deepseek-v4-flash`) |
| Sampling | $T = 1.0$, $\mathrm{top}\text{-}p = 0.5$ |
| Thinking | desactivado |
| Clase | `CvrpStripsHeuristic` |
| Planificador (cuando se evalúe) | Pyperplan, GBFS `gbfs_early_goal_test` |

Entrada del prompt: `benchmarks/cvrp-strips/training/domain.pddl`, `p01-open.pddl`, `p99-open.pddl` y estados de ejemplo. El LLM no interviene durante la búsqueda.

**Generación aceptada (thinking desactivado).** Código Python cerrado, importable por Pyperplan.

## Resultados experimentales (Fase 1)

Fuente: `docs/results/02 - cvrp-like pddl results.xlsx`. Pyperplan, `-s gbfs_early_goal_test`. Corte `blind`: 600 s donde aparece timeout.

| Instancia | Heurística | solved | length | expansions | time (s) |
|---|---|:---:|---:|---:|---:|
| `easy-p01-open` | `hff` | 1 | 4 | 4 | 0,00 |
| `easy-p01-open` | `blind` | 1 | 4 | 67 | 0,02 |
| `easy-p01-open` | `llm` | 1 | 4 | 4 | 0,00 |
| `easy-p10-open` | `hff` | 1 | 20 | 250 | 2,08 |
| `easy-p10-open` | `blind` | 0 | — | — | 600 |
| `easy-p10-open` | `llm` | 1 | 19 | 19 | 0,05 |
| `p20-open` | `hff` | 1 | 23 | 399 | 0,94 |
| `p20-open` | `blind` | 1 | 16 | 2 364 625 | 175,19 |
| `p20-open` | `llm` | 1 | 21 | 209 | 0,14 |
| `medium-p01-open` | `hff` | 1 | 21 | 41 | 12,98 |
| `medium-p01-open` | `blind` | 0 | — | — | 600 |
| `medium-p01-open` | `llm` | 1 | 24 | 24 | 0,28 |
| `easy-p20-open` | `hff` | 1 | 47 | 1 071 | 64,95 |
| `easy-p20-open` | `blind` | 0 | — | — | 600 |
| `easy-p20-open` | `llm` | 1 | 46 | 88 043 | 356,67 |
| `p50-open` | `hff` | 1 | 37 | 1 022 | 85,25 |
| `p50-open` | `blind` | 0 | — | — | — |
| `p50-open` | `llm` | 1 | 38 | 88 393 | 376,89 |

**Resumen:** 6 instancias en el Excel (falta `p10-open`). Coverage LLM = 6/6. En `easy-p10` y `medium-p01` la $h$ LLM reduce mucho expansiones vs. $h^{\mathrm{FF}}$; en `easy-p20` y `p50` la $h$ LLM resuelve pero con **~80× más expansiones** y tiempos ~5× peores que FF.

## Definición de $h$ (resumen)

Sea $d(\cdot,\cdot)$ la distancia más corta entre localizaciones (Floyd–Warshall sobre `road`, precalculado en `__init__`; cada arco $= 1$ acción `drive`).

Para cada paquete $p$ del goal que **no** está en su destino $g_p$:

- **En vehículo** $v$ en $\ell_v$: $h_p = d(\ell_v, g_p) + 1$ (desplazamientos + `drop`).
- **En localización** $\ell_p$: $h_p = \min_{v:\ \mathrm{cap}(v)>0} \bigl[ d(\ell_v,\ell_p) + 1 + d(\ell_p,g_p) + 1 \bigr]$ (ir al paquete + `pick-up` + ir al goal + `drop`). Si ningún vehículo tiene hueco: $h_p = 2$ ( estimación fija).
- **Extra:** para cada vehículo vacío (sin paquetes pendientes a bordo) que no está en `l0`, se suma $d(\ell_v, \mathtt{l0})$.

$$
h(s) = \sum_p h_p(s) + \sum_{v\ \text{vacio}} d(\ell_v, \mathtt{l0}).
$$

$h(s)=0$ si no quedan paquetes por entregar. $\mathrm{cap}(v)$ se lee del predicado `capacity` mapeado a enteros (`c0`→0, `c1`→1, …).

## Pros

- Interfaz correcta (`Heuristic`, `__init__(task)`, `__call__(node)`); código cerrado e importable.
- Usa el mapa (`road`) con distancias precalculadas (Floyd–Warshall), más eficiente que BFS por consulta.
- Distingue paquete en suelo vs. en vehículo; para paquetes en suelo elige el vehículo con hueco que minimiza un coste compuesto (mejor que la $h$ de Fase 0, que no miraba dónde está la furgoneta).
- Docstring y comentarios alineados con semántica CVRP (depósito, capacidad, entregas).
- Lee capacidad restante del estado dinámico (`capacity v c_k`).

## Contras

- **No admisible:** suma costes por paquete de forma independiente; un mismo `drive` puede contarse varias veces.
- **Capacidad parcial:** solo filtra $\mathrm{cap}(v)>0$; no modela reparto entre paquetes ni viajes múltiples al depósito cuando la flota está llena.
- **Fallback $+2$** si ningún vehículo puede recoger: arbitrario; puede subestimar estados difíciles o inflar otros sin criterio claro.
- **Retorno a `l0`:** suma coste de vuelta al depósito para vehículos vacíos; en instancias **open** el goal no exige retorno — puede **sobreestimar** sin ayudar a la búsqueda.
- **`l0` hardcodeado** como depósito (válido en nuestro benchmark, frágil en general).
- Docstring promete agrupación por destino (paso 5); el código **no** agrupa — discrepancia texto/implementación.
- `initial_capacities` se calcula en `__init__` y **no se usa** en `__call__`.
- Inalcanzable ($d=\infty$) o paquete ausente: puede propagar $\infty$ o ignorar el paquete (`continue`) según el caso.
- Identificación por prefijo de nombre (`p…`, `v…`, `l…`).
- Una sola muestra de generación.

## Nota de método

Una sola muestra de generación. El protocolo de Corrêa et al. (varias candidatas, selección en training, test ciego) no se ha ejecutado. Detalle cualitativo: `01 - cvrp-strips-heuristics.md`.
