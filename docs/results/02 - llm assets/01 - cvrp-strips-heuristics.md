# Candidata 01 — `CvrpStripsHeuristic` (DeepSeek Flash, sin thinking)

Análisis cualitativo de la primera $h$ CVRP-STRIPS guardada. Código: `01 - cvrp-strips-heuristic.py` (copia de `cvrp-strips-heuristic.py` del repo). Cómo se lanza: `docs/explain/03 - EJECUTAR.md` §7 (`--domain cvrp-strips` para generar; Pyperplan con `-H` para evaluar).

Esto **no** es el torneo del paper (~25 candidatas). Es una tirada.

---

## 1. Condiciones de generación (trazabilidad)

Fecha: **2026-09-05**. Cwd: `llm-generated-heuristics-vrp`.

| Campo | Valor |
|---|---|
| Script | `llm-heuristics.py` |
| Framework | `deepseek` |
| Modelo | `deepseek-v4-flash` |
| Dominio / suite | `cvrp-strips` (`training/domain.pddl`, `p01-open`, `p99-open`, `example-state` / `example-static`) |
| Prompt | `neurips`, `--ablation false` |
| `--heuristic-name` | `CvrpStripsHeuristic` |
| `--heuristic-file` | `cvrp-strips-heuristic.py` |
| Thinking | **off** (`--no-thinking`) |
| `--temperature` / `--top-p` | `1.0` / `0.5` (defaults) |
| `--idea` | vacío |

```text
uv run llm-heuristics.py --framework deepseek --model deepseek-v4-flash --domain cvrp-strips --heuristic-name CvrpStripsHeuristic --heuristic-file cvrp-strips-heuristic.py --no-thinking
```

Resultado: fichero **cerrado**, importable. No se documentó un intento fallido previo para esta suite (a diferencia de Transport con thinking on).

---

## 2. Objetivo Fase 1 (qué debería hacer una buena $h$)

Instancias **CVRP-STRIPS**: todos los paquetes en depósito `l0` al inicio, goal **open** (solo entregas `(at p_i l_cliente)`), demanda modo B, mismo dominio `transport`.

Una $h$ útil para GBFS debería:

- Ordenar estados “cerca del goal” antes que estados con muchas entregas pendientes.
- Usar el **mapa** (distancias entre sitios vía hub `l0↔l1` y grafo IPC).
- Tener en cuenta **capacidad** cuando varios paquetes compiten por la misma furgoneta o hacen falta varios viajes al depósito.
- No confundir goal open con **closed** (retorno obligatorio al depósito).

Comparación prevista: `blind`, $h^{\mathrm{FF}}$, esta $h$ — misma instancia, mismo `-s gbfs_early_goal_test`.

---

## 2b. Resultados experimentales (Fase 1)

Fuente: `docs/results/02 - cvrp-like pddl results.xlsx`. Mismo buscador y receta que Fase 0.

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

**Lectura rápida:**

- **`easy-p01-open`:** empate `hff` / LLM (4 expansiones); `blind` resuelve pero explora 67 nodos.
- **`easy-p10-open`:** LLM gana claro — plan más corto (19 vs 20), **13× menos expansiones** que FF; `blind` timeout (600 s).
- **`p20-open`:** LLM mejor que FF en expansiones (209 vs 399); `blind` encuentra plan más corto (16) pero a coste absurdo (2,3M expansiones, 175 s).
- **`medium-p01-open`:** LLM resuelve con **menos expansiones** que FF (24 vs 41); plan ligeramente más largo (24 vs 21); `blind` timeout.
- **`easy-p20-open` / `p50-open`:** LLM **peor** que FF — longitud similar, pero **~80× más expansiones** y tiempos ~5× mayores. Aquí la suma por paquete + return-to-`l0` parece confundir a GBFS.

`p10-open` no está en el Excel (sí en el catálogo `testing/README.md`).

---

## 3. Qué calcula esta $h$ (lectura del código)

### 3.1. Inicialización (`__init__`)

- Goals: mapa `package → localización destino`.
- Grafo `road` (no dirigido en la matriz).
- **Floyd–Warshall** → `self.dist[loc1][loc2]` para todas las localizaciones vistas en roads, goals o `:init`.
- Cadena `capacity-predecessor` → enteros `c0=0, c1=1, …` (huecos libres).
- `initial_capacities`: capacidad inicial por vehículo — **calculado pero no usado** después.

### 3.2. Evaluación (`__call__`)

Parsea el estado: posición de vehículos, paquetes (suelo o `in`), capacidad restante.

**Bucle por paquete no entregado:**

| Situación | Coste añadido |
|---|---|
| Paquete ya en goal | 0 (no entra en undelivered) |
| Paquete en vehículo $v$ en $\ell_v$ | $d(\ell_v, g) + 1$ |
| Paquete en suelo en $\ell_p$ | $\min_v \bigl[ d(\ell_v,\ell_p)+1+d(\ell_p,g)+1 \bigr]$ entre vehículos con $\mathrm{cap}(v)>0$ |
| Ningún vehículo con hueco | $+2$ fijo |

**Post-proceso:** cada vehículo sin paquetes pendientes a bordo y lejos de `l0` suma $d(\ell_v, \mathtt{l0})$.

Familia: **suma independiente por paquete** + penalización de “vuelta al almacén”, no un solver VRP.

---

## 4. Qué está bien (respecto al objetivo)

- **Encaje Pyperplan:** misma interfaz que Gripper/Logistics del prompt; importa `Heuristic`, usa `task.goals`, `task.static`, `node.state`.
- **Mejora respecto a `TransportHeuristic` (Fase 0):** para paquetes en el suelo no asume distancia suelo→goal directa; busca un vehículo con hueco y cuenta desplazamiento vehículo→paquete→goal.
- **Mapa:** Floyd–Warshall en el constructor evita repetir BFS en cada nodo expandido.
- **Capacidad dinámica:** lee `(capacity v c_k)` del estado; ignora vehículos llenos al asignar recogida.
- **CVRP en el relato:** docstring menciona depósito, capacidad unitaria por paquete, red undirected — coherente con las instancias `-open`.
- **Esqueleto del prompt:** `get_parts` / `match` / `fnmatch` reutilizado; el few-shot “pegó”.

---

## 5. Lo flojo (respecto al objetivo CVRP)

### 5.1. Suma por paquete (otra vez)

Igual que la $h$ de Transport: cada paquete aporta un “mini-plan” y se **suman**. Dos entregas en la misma ruta cuentan dos veces el mismo `drive`. GBFS tolera $h$ no admisibles, pero puede **inflar** $h$ y empeorar el orden frente a $h^{\mathrm{FF}}$ en instancias con muchos paquetes (`easy-p20-open`, `p50-open`).

### 5.2. Capacidad superficial

- Solo comprueba $\mathrm{cap}(v)>0$, no cuántos paquetes faltan ni si hacen falta **varios viajes** depósito→clientes→depósito.
- No asigna paquetes a vehículos de forma global (cada paquete elige su $\min_v$ por separado → el mismo $v$ puede “ganar” para muchos paquetes en la suma aunque no pueda cargarlos a la vez).

### 5.3. Vuelta a `l0` en goal **open**

El bloque final suma $d(\ell_v, \mathtt{l0})$ para vehículos vacíos. En CVRP-STRIPS **open** el plan óptimo **no** requiere volver al depósito. Esa parte:

- No aparece en el goal.
- Puede **sobreestimar** $h(s)$ en estados intermedios (vehículo vacío lejos de `l0` tras una entrega).
- Mezcla semántica closed/open — riesgo de confundir en la memoria si se presenta como “heurística CVRP open”.

### 5.4. Depósito fijo y fallback

- `l0` literal en el return-to-depot; acorde a nuestro benchmark, no genérico.
- Si todos los vehículos están llenos y hay paquetes en `l0`, suma **2** sin geometría — ciega para estados de “descargar y volver a cargar”.

### 5.5. Docstring vs código

El docstring (paso 5) habla de **agrupar paquetes por origen/destino**; no hay agrupación en el código. `initial_capacities` tampoco se usa. Típico desfase LLM: razonamiento en comentarios, implementación más simple.

### 5.6. Robustez

- Paquete ausente del estado: `continue` (coste 0 implícito).
- $d=\infty$: se propaga en sumas → $h$ infinita o comparaciones raras.
- Prefijos `p` / `v` / `l` en nombres de objeto.

---

## 6. Comparación rápida con Fase 0 (`TransportHeuristic`)

| Aspecto | Transport (Fase 0) | CVRP-STRIPS (esta $h$) |
|---|---|---|
| Distancias | BFS por consulta | Floyd–Warshall precalculado |
| Paquete en suelo | $2 + d(\ell_p, g)$ | $\min_v$ con vehículo→$\ell_p$→$g$ |
| Capacidad en $h$ | Parseada, no usada | Filtra vehículos llenos |
| Depósito | No modelado | Return-to-`l0` extra |
| Suma independiente | Sí | Sí |

La nueva $h$ **sí reacciona** al relato CVRP (depósito, vehículo debe ir a recoger). Sigue lejos de un estimador de rutas capacitadas “de verdad”.

---

## 7. Lectura para la memoria / el cuaderno

> Flash **sin thinking** produjo una $h$ ejecutable para CVRP-STRIPS. En 6 instancias del Excel resuelve todas; en `easy-p10` y `medium-p01` mejora claramente a $h^{\mathrm{FF}}$ en expansiones; en `easy-p20` y `p50` resuelve pero con órdenes de magnitud **más** expansiones que FF. `blind` timeout en 4/6 (corte 600 s). Una candidata ≠ protocolo de 25.

**Patrón observado:** la $h$ escala bien en problemas pequeños–medianos; en instancias grandes (10 paquetes, mapas IPC densos) el coste de búsqueda se dispara — coherente con suma independiente por paquete y el término return-to-`l0`.
