# Instancias CVRP-STRIPS resueltas (Fase 1, parcial)

Copias de `benchmarks/cvrp-strips/testing/` + planes guardados antes de pisarlos con otro run.

**Nomenclatura:** `01 - cvrp-{…}-open.pddl` (instancia) + `01 - cvrp-{…}-open-llm.soln` (plan).

## Procedencia de los planes

| Campo | Valor |
|---|---|
| Planificador | Pyperplan, `-s gbfs_early_goal_test` |
| Heurística | `01 - cvrp-strips-heuristic.py` (`CvrpStripsHeuristic`, candidata 01) |
| LLM | DeepSeek V4 Flash, thinking off |
| Fecha runs | 2026-09-05 |

Pyperplan escribe el `.soln`; el LLM solo genera la heurística. Dominio: CVRP-STRIPS open, depósito `l0`, modo B.

| Instancia | Plan (LLM $h$) | Long. |
|---|---|---:|
| `01 - cvrp-easy-p01-open.pddl` | `01 - cvrp-easy-p01-open-llm.soln` | 4 |
| `01 - cvrp-easy-p10-open.pddl` | `01 - cvrp-easy-p10-open-llm.soln` | 19 |
| `01 - cvrp-p10-open.pddl` | `01 - cvrp-p10-open-llm.soln` | 19 |

Instancias pendientes de barrido: `p20-open`, `medium-p01-open`, `easy-p20-open`, `p50-open` (ver `benchmarks/cvrp-strips/testing/README.md`).
