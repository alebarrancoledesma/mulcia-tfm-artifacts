# CVRP-STRIPS (Fase 1)

Fase 0 = IPC `transport` + pipeline Corrêa. **Fase 1 = partidas con pinta de CVRP** en el mismo Pyperplan.

Léelo después de `02 - PDDL.md` (dominio vs instancia, `drive`/`pick-up`/`drop`, peldaños `c0`…). Para lanzar el planner: `03 - EJECUTAR.md`. Plan oficial: `docs/plan/MASTER_PLAN.md` §5.

Todavía **no** hay ficheros en el repo: esto es el diseño que hay que entender antes de escribir el primer `.pddl`.  
*(Actualización: ya existen `benchmarks/cvrp-strips/` y guía de adaptación en `05 - CVRP-INSTANCE-CREATE.md`.)*

---

## 1. Qué problema estamos modelando

**CVRP** (capacitated vehicle routing): hay un **depósito**, clientes con **demanda unitaria** (1 paquete = 1 hueco), furgonetas con **capacidad limitada**, y un **mapa** (carreteras). Hay que llevar cada paquete del depósito a su cliente.

En planning no minimizamos km en el PDDL: cada `drive` cuesta **1 acción** (como en `transport`). Los km los mediremos **después**, del plan, con la misma geometría (MASTER §5.3).

Lo que importa en Fase 1:

- la **partida se lee** como reparto desde un almacén;
- la **demanda por cliente** (cuántas unidades hay que dejar en cada sitio);
- la **misma** comparación de heurísticas (`blind`, $h^{\mathrm{FF}}$, $h$ LLM **nueva**);
- el IPC `transport` sigue como **control** (Fase 0), no se mezcla en la tabla CVRP.

Este encaje con el TFM: la propuesta pide **VRP/CVRP en planning**, no solo repetir el dominio IPC. CVRP-STRIPS es ese paso (ver §2.1).

---

## 2. `transport` IPC vs CVRP-STRIPS

Las **acciones** pueden ser las mismas (`domain.pddl` de `transport` casi tal cual). Lo que cambia es **cómo rellenamos** cada instancia.

| | IPC `transport` (`p01`, `p10`…) | CVRP-STRIPS (nuestro) |
|---|---|---|
| Depósito | No hay. Sitios `l1`, `l2`… sueltos | Un sitio fijo, p. ej. `l0` = depósito |
| Paquetes al empezar | Donde sea (`at p1 l3`, …) | **Todos** en `l0`: `(at p1 l0)`, `(at p2 l0)`, … |
| Furgonetas al empezar | Donde sea | En `l0`: `(at v1 l0)`, … |
| Goal | Cada paquete en su destino | `(at p_i l_cliente)` — ver §2.1 |
| Volver al depósito | No está en el goal | **Opcional** (ver §5) |
| Capacidad | Peldaños `c0 < c1 < …` | Igual; 1 paquete = 1 hueco de capacidad |
| Distancia | 1 `drive` = 1 paso | Igual en PDDL |

Por eso no hace falta otro planificador: es **otras partidas** (carpeta `benchmarks/cvrp-strips/` + entrada en `SUITES`), no reescribir Pyperplan.

### 2.1. Qué tan “CVRP de verdad” es (escalera de modelado)

| Nivel | Qué modeláis | Relación con CVRP clásico |
|---|---|---|
| IPC `transport` | Orígenes sueltos, sin almacén | Routing + capacidad; **no** CVRP |
| **CVRP-STRIPS** (Fase 1) | Depósito `l0`, carga inicial en almacén, demandas **enteras unitarias** | **CVRP capacitado** con \(q_i \in \mathbb{N}\) |
| CVRP agregado numérico | `(demand client-a) = 20` sin 20 objetos | CVRP “de libro” en PDDL 2.1; **fuera** de Pyperplan + Corrêa |

**Demanda en nuestro STRIPS:** cliente `lA` con demanda \(q=3\) → **3 objetos** `package` en `:init` en `l0`, y en `:goal` **tres** literales `(at p_* lA)`. Al **escribir** la instancia elegimos nombres arbitrarios para contar unidades; ver §2.2 sobre qué significa “intercambiable”.

- Caso **demanda 1** por cliente: un paquete por destino (`p01-open`: `l1=2`, `l2=1` con paquetes agrupados por destino).
- Caso **demanda > 1**: varios paquetes con el **mismo** destino en el goal → paso hacia CVRP general (sin fluents numéricos).

**No hacemos (de momento):** minimizar \(\sum\) distancia **dentro** del planner ni demanda en un solo fluent numérico. Los km van **post-hoc** (MASTER §5.3); el dominio sigue siendo `transport` IPC.

Cómo escribir instancias: `05 - CVRP-INSTANCE-CREATE.md` §3.2.

### 2.2. Limitación: no sustitución de paquetes en el goal

En STRIPS el `:goal` nombra **individuos**: `(at p1 l1) (at p2 l1) (at p3 l1)` significa que el objeto **`p1`**, **`p2`** y **`p3`** deben acabar en `l1` — no “cualquier tres paquetes”.

**Ejemplo:** demanda 3 en `l1`; el camión lleva `p1`, `p2`, `p5`. Puede soltar `p1` y `p2`. **`p5` no sustituye a `p3`**: el goal pide `(at p3 l1)`. Soltar `p5` en `l1` no lo cumple; hace falta recoger **`p3`** en el depósito y entregarlo.

| Qué decimos en la memoria | Qué es en PDDL |
|---|---|
| “Misma mercancía / misma demanda” | Todos son tipo `package`; misma capacidad |
| “Demanda \(q_i=3\) en cliente A” | Tres objetos con tres literales `(at p_* A)` en el goal |
| “Intercambiables en runtime” | **No** — identidades fijadas al instanciar |
| Plan válido | Debe colocar **cada** `p_i` del goal en **su** sitio |

Esto es **CVRP unitario discretizado con etiquetas**, no CVRP agregado OR donde solo importa `(cliente, cantidad)` y cualquier unidad física vale.

**¿Tiene solución?** Sí, pero con trade-offs (Fase 1 **no** las implementa; documentar por honestidad):

| Enfoque | ¿Sustitución p5 ↔ p3? | Encaje Fase 1 |
|---|---|---|
| Goal `(at p_i l_j)` (actual) | No | Sí — Pyperplan + Corrêa |
| `(dest p_i l_j)` estático en init + reglas de drop | No (cada unidad tiene cliente asignado) | Dominio modificado |
| **Disyunción `(or …)` en el goal** (“cualquier 3 de N paquetes en `l1`”) | En teoría sí | **Descartado** — ver abajo |
| Fluents `(demand l)` + acción `serve` sin `package` | **Sí** | PDDL 2.1 + otro planner → **Fase 2.5** |

**Goal con `(or …)` — descartado.** Para demanda \(q=3\) habría que enumerar \(\binom{N}{3}\) combinaciones de `(and (at p_i l1) …)` por cliente. Goal ilegible, grounding enorme, Pyperplan/$h^{\mathrm{FF}}$/heurística LLM no están pensados para metas disyuntivas. Peor que fluents numéricos; no se implementa.

Para el TFM basta el encoding actual (Fase 1) si se explicita la limitación.

### 2.3. Fase 2.5 (opcional) — CVRP agregado en PDDL+, **después del GATE**

**No es Fase 1** (no bloquea el TFM). **No es Fase 2** (metaheurísticas / OR-Tools / ALNS). Es un **apéndice de planning** si tras cerrar Parte I sobra tiempo **antes** de abrir el repo metaheurístico — o en lugar de parte de Fase 2 si el calendario aprieta.

| | Fase 1 (ahora) | Fase 2.5 (opcional) | Fase 2 (MASTER §7) |
|---|---|---|---|
| Objetivo TFM | Sí — GATE | No obligatoria | Solo tras GATE |
| Dominio | `transport` STRIPS | **`cvrp-numeric`** PDDL 2.1 | Rutas OGA, no PDDL |
| Demanda | N paquetes + goal `(at p_i l_j)` | `(demand ?c)` numérico | Demanda en solver CVRP |
| Sustitución p5 ↔ p3 | No | **Sí** (carga agregada) | N/A |
| Planner | Pyperplan + GBFS | **Fast Downward** (u otro con `:metric`) | Metaheurística |
| Heurística LLM Corrêa | Sí (suite CVRP-STRIPS) | **Nueva** generación (otro dominio) | LLM en estancamiento |
| Minimizar km en búsqueda | No (post-hoc) | **Sí** `:metric minimize (total-cost)` | Sí (función objetivo) |

**Esquema de dominio (borrador, no implementado):**

```text
;; requirements :typing :fluents :action-costs
;; functions: (demand ?c - customer) (load ?v - vehicle) (total-cost)

(:action drive
  :parameters (?v ?from ?to - location)
  :precondition (and (at ?v ?from) (road ?from ?to))
  :effect (and (not (at ?v ?from)) (at ?v ?to)
               (increase (total-cost) (distance ?from ?to))))

(:action serve
  :parameters (?v - vehicle ?c - customer)
  :precondition (and (at ?v ?c) (> (demand ?c) 0) (> (load ?v) 0))
  :effect (and (decrease (demand ?c) 1) (decrease (load ?v) 1)))

(:action load-at-depot ... )   ;; opcional: subir carga en l0

(:metric minimize (total-cost))
```

**Problem:** `(demand A)=20`, `(demand B)=35`, …; `(load v1)=0`; vehículo en depósito; sin objetos `package`.

**Entregables mínimos si se hace:** `benchmarks/cvrp-numeric/` (2–3 instancias), 1 tabla FD vs STRIPS en tiny, párrafo en memoria (“extensión agregada”). **No** sustituye tablas GATE de Fase 1.

**Orden oficial:** Fase 0 → Fase 1 → **GATE** → (2.5 opcional) → Fase 2. Ir rápido el día 1 no salta el GATE: Fase 2/2.5 siguen prohibidas hasta tablas CVRP-STRIPS defendibles (`MASTER_PLAN.md` §6).

---

## 3. Partida mínima (la primera que diseñaremos)

Objetivo pedagógico: poder señalar depósito, clientes y goal **como en un dibujo de CVRP**.

### 3.1. Historia

- Depósito `l0`.
- Clientes `l1`, `l2` (destinos).
- 1 furgoneta `v1`, capacidad 2 peldaños (`c0` / `c1` / `c2` → puede llevar 2 paquetes).
- 2 paquetes `p1`, `p2`; al inicio **en el depósito**.
- Goal: `p1` en `l1`, `p2` en `l2`.
- Mapa sencillo (ejemplo):

```text
        l1
        |
  l0 ---+--- l2
```

Carreteras bidireccionales entre sitios que haya que usar (como en `p01`: `(road l0 l1)` y `(road l1 l0)`, etc.).

### 3.2. Qué iría en `:init` (idea)

- `(at v1 l0)`
- `(at p1 l0)` `(at p2 l0)`
- `(capacity v1 c2)` y `(capacity-predecessor c0 c1)` `(capacity-predecessor c1 c2)`
- `(road …)` según el mapa

### 3.3. Qué iría en `:goal`

Mínimo CVRP “abierto” (sin obligar a volver):

```text
(at p1 l1)
(at p2 l2)
```

Un plan posible (no único): cargar en `l0`, repartir, descargar en cada cliente. Con 1 furgoneta y capacidad 2 puede hacerse en **un solo viaje** si el mapa lo permite.

### 3.4. Qué comprobar cuando exista el fichero

- ¿Todos los paquetes empiezan en `l0`?
- ¿Todas las furgonetas empiezan en `l0`?
- ¿El goal solo pide paquetes en clientes (no “origen aleatorio”)?
- ¿Pyperplan con `-H hff` encuentra plan? (antes de gastar LLM)

Ruta en repo:

```text
llm-generated-heuristics-vrp/benchmarks/cvrp-strips/training/p01-open.pddl
llm-generated-heuristics-vrp/benchmarks/cvrp-strips/training/domain.pddl
```

---

## 5. Decisión: CVRP abierto vs cerrado

| | CVRP abierto | CVRP cerrado |
|---|---|---|
| Goal | Solo `(at p_i l_cliente)` | Además `(at v_k l0)` para cada furgoneta |
| Planner | Más simple | Más acciones al final (volver) |
| Memoria | “Reparto desde depósito” | “Reparto + retorno al almacén” |

**Recomendación para empezar:** **abierto** (solo paquetes en clientes). Si el goal pide retorno y la $h$ del LLM no lo contempla, la búsqueda se complica sin aportar mucho al primer GATE.

Se documenta la elección en el report de la suite CVRP.

---

## 6. Cuántas instancias (después de la mínima)

No hace falta un catálogo IPC. Bastan **pocas**, bien elegidas (MASTER §5.4):

| Tipo | Para qué | Ejemplo de tamaño |
|---|---|---|
| Tiny | Entender PDDL, $h(s_0)$ vs plan | 1–2 furgonetas, 2–3 clientes |
| Escala | ¿Aguanta GBFS? | ~10, ~20 clientes |
| Capacidad justa | Stress: hace falta 2 viajes | demanda total ≈ capacidad de flota; algún cliente con \(q_i > 1\) |

Generación: a mano al principio; luego script desde coordenadas (misma geometría para km post-hoc).

**Training vs testing:** como Corrêa — instancias pequeñas (+ una grande) al **prompt** del LLM; otras para **evaluar** sin mezclar “elegir $h$” y “medir $h$”.

---

## 7. Heurísticas en Fase 1

Mismo protocolo que Fase 0 (`03` §6):

```text
para cada instancia CVRP
    blind | hff | h_LLM_cvrp
    GBFS gbfs_early_goal_test
    Excel: solved, length, expansions, time
```

- **`transport-heuristic.py` (candidata 01) no sirve** para CVRP: es heurística de otro dominio/partida. Hay que **generar otra** con `--domain` apuntando a la suite nueva.
- Hace falta registrar la suite en `src/llm_heuristics/suites.py`: `domain.pddl`, `p01`, `p99` (o la grande), `example-state.out`, `example-static.out` (copiar formato de `transport`).

Extras Fase 1 (no bloquean el primer `p01`):

- km post-hoc del plan;
- en 3–5 tinies: comparar $h(s_0)$ con longitud del plan;
- Fast Downward solo si entra fácil (opcional).

---

## 8. Orden de trabajo (checklist)

1. [x] Leer este doc + §6 de `02 - PDDL.md`.
2. [x] Fijar: depósito = `l0`, CVRP abierto, demanda unitaria (§2.1).
3. [x] Instancia tiny + `domain` (`p01-open`).
4. [ ] Instancias con **demanda por destino** (§2.1, guía en `05` §3.2).
5. [ ] `example-state.out` / `example-static.out` + entrada `SUITES`.
6. [ ] Generar **una** $h$ LLM CVRP (Flash, thinking off).
7. [ ] Pyperplan: `hff` / `blind` / $h$ LLM → Excel CVRP.
8. [ ] Report + assets en `docs/results/`.

**Prohibido** en este tramo: metaheurística GRASP, reescribir Pyperplan, fluents numéricos, torneo de 25 candidatas (salvo que lo pidáis expreso).

---

## 9. Después de leer esto deberías poder…

- decir en una frase en qué se diferencia CVRP-STRIPS de `training/transport/p10`;
- explicar demanda \(q_i\) como **varios paquetes** con goal en el mismo cliente (§2.1);
- explicar la **limitación** §2.2 (no sustitución p5 ↔ p3 en el goal);
- dibujar la partida mínima (depósito, clientes, paquetes en `l0`);
- explicar por qué reutilizamos `drive`/`pick-up`/`drop` pero **no** `TransportHeuristic` de Fase 0;
- distinguir CVRP-STRIPS (Fase 1) de CVRP numérico agregado (Fase 2.5 opcional, §2.3);
- decir por qué **no** usamos `(or …)` en el goal (§2.2).

Siguiente paso práctico: instancias con demanda por destino — `05 - CVRP-INSTANCE-CREATE.md`.
