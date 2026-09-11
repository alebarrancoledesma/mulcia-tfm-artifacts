# Instancias transport resueltas (Fase 0)

Copias de `benchmarks/ipc2023-learning/testing/transport/` + planes guardados antes de pisarlos con otro run.

**Nomenclatura:** `01 - transport-{easy|medium}-p{id}.pddl` (instancia) + `01 - transport-{easy|medium}-p{id}-llm.soln` (plan).

## Procedencia de los planes

| Campo | Valor |
|---|---|
| Planificador | Pyperplan, `-s gbfs_early_goal_test` |
| Heurística | `01 - transport-heuristic.py` (`TransportHeuristic`, candidata 01) |
| LLM | DeepSeek V4 Flash, thinking off |
| Fecha runs | 2026-09-05 |

El LLM **no** escribe el plan: genera la heurística; Pyperplan busca y escribe el `.soln`. La longitud coincide con la columna `length` del Excel para esa heurística (p. ej. easy-p20: 39 vs 45 con `hff`).

Origen del dominio: IPC `transport` (`drive` / `pick-up` / `drop`). Cada acción cuenta **1** en la longitud del plan; no hay km.

| Instancia | Plan (LLM $h$) | Veh. | Paq. | Sitios | Long. |
|---|---|---:|---:|---:|---:|
| `01 - transport-easy-p01.pddl` | `01 - transport-easy-p01-llm.soln` | 3 | 1 | 5 | 3 |
| `01 - transport-easy-p10.pddl` | `01 - transport-easy-p10-llm.soln` | 4 | 5 | 8 | 19 |
| `01 - transport-easy-p20.pddl` | `01 - transport-easy-p20-llm.soln` | 5 | 10 | 11 | 39 |
| `01 - transport-medium-p01.pddl` | `01 - transport-medium-p01-llm.soln` | 10 | 5 | 20 | 23 |

---

## `easy-p20` — goal e interpretación

**Metadatos:** 5 vehículos, 10 paquetes, 11 localizaciones, capacidad máxima 2 (tamaños `c0 < c1 < c2`).

### Situación inicial (extracto)

| Objeto | Dónde empieza |
|---|---|
| v1 | l8 |
| v2 | l11 |
| v3 | l6 |
| v4 | l5 |
| v5 | l10 |
| p1 | l4 |
| p2, p6 | l10, l6 |
| p3 | l7 |
| p4 | l8 |
| p5, p7, p8 | l9 |
| p9, p10 | l2 |

Los paquetes están **repartidos** por el mapa; no hay depósito. El grafo `road` conecta pares de `l1`…`l11` (arcos bidireccionales en la instancia).

### Goal

Cada paquete debe acabar en **una** localización concreta (entrega, no “visitar”):

| Paquete | Destino goal |
|---|---|
| p1 | l2 |
| p2 | l1 |
| p3 | l5 |
| p4 | l10 |
| p5 | l3 |
| p6 | l10 |
| p7 | l1 |
| p8 | l5 |
| p9 | l8 |
| p10 | l11 |

No se exige dónde terminan los vehículos.

### Plan (39 acciones) — reparto por vehículo

Solo intervienen **v1, v2, v3**; v4 y v5 no se usan.

**v3 — primer bloque (p6, p2, p4):**

1. En l6 recoge **p6** (ya está allí).
2. Conduce l6 → l9 → l10 (2 `drive`).
3. En l10 recoge **p2** (doble carga: p6 + p2, capacidad llena).
4. Paralelo conceptual: **v1** en l8 recoge **p4** y conduce a l10.
5. En l10 suelta **p6** (goal p6 ✓).
6. Conduce a l1 y suelta **p2** (goal p2 ✓).
7. **v1** suelta **p4** en l10 (goal p4 ✓).

**v2 — bloque central (p9, p10, p5, p8, p3):**

8. l11 → l2, recoge **p9**, l2 → l8, suelta **p9** (goal ✓).
9. l8 → l2, recoge **p10**, l2 → l11, suelta **p10** (goal ✓).
10. l11 → l9, recoge **p5**, l9 → l3, suelta **p5** (goal ✓).
11. l3 → l9, recoge **p8**, l9 → l11 → l5, suelta **p8** (goal ✓).
12. l5 → l7, recoge **p3**, l7 → l5, suelta **p3** (goal ✓).

**v3 — cierre (p7, p1):**

13. l1 → l9, recoge **p7**, l9 → l1, suelta **p7** (goal ✓).
14. l1 → l4, recoge **p1**, l4 → l2, suelta **p1** (goal ✓).

### Lectura tipo VRP

- Sí hay tramos **sitio a sitio** (`drive`): cada arco `road` es una acción coste 1.
- Los camiones pueden circular **vacíos** entre recogidas (p. ej. v2: l8 → l2 tras dejar p9).
- Se aprovecha **capacidad 2** para llevar dos paquetes a la vez (v3: p6 + p2 hacia l10/l1).
- No hay “vuelta al almacén”; el objetivo es solo `(at p_i destino_i)`.

---

## Resumen de las otras instancias resueltas

### `easy-p01` (3 acciones)

Un paquete en l2, goal l3. v1 ya está en l2: `pick-up` → `drive l2 l3` → `drop`. Caso mínimo.

### `easy-p10` (19 acciones)

5 paquetes, 4 vehículos. v4 mueve p5 (l8→l5); v1 mueve p3 y luego p1, p2 en secuencia; v3 mueve p4 (l1→l5). Varios `drive` encadenados entre sitios antes de cada carga/descarga.

### `medium-p01` (23 acciones)

5 paquetes, 10 vehículos, 20 sitios, capacidades hasta 4. Usa v4, v6, v10. Rutas más largas en el grafo (p. ej. v4: l2 → l7 → l13 → l11 para p3). Instancia donde `hff` no terminó en tiempo razonable en las pruebas; la heurística LLM sí cerró plan corto.
