# Crear instancias CVRP-STRIPS (adaptación desde IPC)

Guía operativa para pasar partidas **`transport` IPC** a **CVRP-STRIPS** sin generar benchmarks desde cero.

Léelo después de `04 - CVRP-STRIPS.md` (qué modelamos y por qué). Dominio PDDL: `02 - PDDL.md`. Lanzar planner: `03 - EJECUTAR.md`.

---

## 1. ¿Es buen enfoque?

**Sí**, para Fase 1:

- Reutilizamos **mapas y capacidades** del IPC; el **goal** lo escribimos en semántica CVRP (**modo B**, §3.2).
- Solo cambiamos el **`:init`** al relato CVRP (depósito + carga en almacén).
- **No hace falta resolver** cada instancia para darla por factible si pasa el chequeo estructural (§4).
- Adaptamos **pocos** ficheros bien elegidos (tiny / mediana / grande), no todo el benchmark IPC.

El IPC original sigue siendo **control** (Fase 0). La tabla Excel CVRP es **aparte**.

---

## 2. Carpeta y nombres

```text
llm-generated-heuristics-vrp/benchmarks/cvrp-strips/
  training/          ← prompt LLM (p01 + p99) + example-*.out (más adelante)
    domain.pddl
    p01-open.pddl
    p99-open.pddl
  testing/           ← evaluación (no entran al prompt)
    domain.pddl
    …-open.pddl
```

| Sufijo | Goal |
|--------|------|
| `-open` | Solo `(at p_i l_cliente)` — **empezar por aquí** |
| `-closed` | Además `(at v_k l0)` — más adelante, 1–2 tinies |

Convención: **`l0` = depósito**. Clientes = resto de `location` del IPC (`l1`…`lN`).

---

## 3. Dos modos de crear instancias

### 3.1. Modo A — adaptación rápida (goal IPC tal cual) — *histórico*

Copiar el goal IPC sin agrupar demandas (cada `p_i` a un destino distinto → demanda 1 implícita). **`p99-open` pasó a modo B** (demandas agrupadas). Reservar modo A solo si hace falta un puente rápido sin recontar goals.

### 3.2. Modo B — demanda por destino (**preferido**, próximas instancias)

Modelo alineado con CVRP clásico (demandas enteras \(q_i\), unidad = un paquete):

1. **Mapa y flota:** copiar `road`, `capacity`, vehículos del IPC (o diseñar a mano).
2. **Depósito:** `l0` + hub `l0↔l1` (igual que §3.1).
3. **Demandas:** tabla explícita, p. ej. `l2:3`, `l5:2`, `l7:1` → **6 paquetes** en total.
4. **Objects:** tantos `- package` como \(\sum q_i\); nombres opcionales `p_l2_1`, `p_l2_2`, …
5. **`:init`:** todos `(at p_* l0)`, todas las furgonetas en `l0`.
6. **`:goal`:** por cada paquete, `(at p_* l_cliente)` según su demanda — **varios paquetes pueden compartir destino**. Los nombres son **etiquetas al escribir** el problem; en runtime **no** se sustituye un `p_i` por otro (§3.4).

Ejemplo mínimo (demanda):

```text
;; demands: l1=2, l2=1  →  packages p1, p2, p3
(at p1 l0) (at p2 l0) (at p3 l0)
goal: (at p1 l1) (at p2 l1) (at p3 l2)
```

**Desde IPC:** contar cuántos goals apuntaban a cada `l_j` en el original → esas son las \(q_j\); reasignar paquetes a esos destinos (no hace falta conservar `p1→l7` del IPC).

Checklist de factibilidad: §4 (igual; los clientes del goal deben ser alcanzables desde el hub).

### 3.4. Limitación: identidades en el goal (misma mercancía)

Todos los `package` son iguales para el dominio (misma capacidad, mismas acciones). **Pero** el goal fija **qué objeto** debe estar en **qué** sitio.

Si en `l1` la demanda es 3 y el goal pide `(at p1 l1) (at p2 l1) (at p3 l1)`, un camión con `p1`, `p2`, `p5` **no** puede “cerrar” la demanda soltando `p5` en lugar de `p3`. Hay que entregar **`p3`**.

**Al instanciar:** convención de nombres (`p_l2_1`, `p_l2_2`, …) para leer demandas; no implica sustituibilidad en ejecución.

**Alternativas descartadas o futuras** (detalle en `04` §2.2–§2.3):

- **OR en el goal** — descartado (combinatoria, Pyperplan).
- **Fase 2.5** — PDDL 2.1 + fluents + Fast Downward; demanda agregada real; **solo tras GATE**, opcional.

### 3.3. Pasos comunes (ambos modos)

1. **Añadir** `l0 - location` a `:objects` si no existe.
2. **Depósito en el mapa:** solo **`(road l0 l1)`** y **`(road l1 l0)`** — no estrella desde `l0` a todos los clientes.
3. **Comentario** en cabecera: modo A/B, demandas, origen IPC, conteos.

### Qué no hacer

- No reescribir el `domain.pddl` (copia de `transport`).
- No mezclar instancias CVRP en la tabla de Fase 0.
- No asumir que el plan del IPC sirve tal cual (otro `:init`).
- No resolver con Pyperplan **solo** para certificar factibilidad (§4).

### Ejemplos ya hechos

| Fichero | Modo | Demandas (resumen) |
|---------|------|---------------------|
| `training/p01-open.pddl` | B | `l1=2`, `l2=1` (prompt LLM) |
| `training/p99-open.pddl` | B | 11 clientes; p. ej. `l12=4`, `l2=2`, … (prompt LLM) |
| `testing/p10-open.pddl` | B | `l2=1`, `l3=1`, `l4=2` (4 paquetes; origen `training/p10`) |

Catálogo completo, orden de evaluación y explicación easy/medium vs `p10`: **`benchmarks/cvrp-strips/testing/README.md`**.

---

## 4. Factibilidad sin resolver

Basta con argumento **estructural** (no hace falta `.soln` ni timeout de `hff`).

### Condiciones (checklist manual)

| # | Comprobar |
|---|-----------|
| 1 | Todos los paquetes en `(at p_i l0)` al inicio. |
| 2 | Todas las furgonetas en `(at v_k l0)`. |
| 3 | Existe `(road l0 l1)` y `(road l1 l0)` (o el hub que elijáis). |
| 4 | Desde **`l1`**, cada localización que aparece en el **`:goal`** es alcanzable y permite **vuelta** a `l1` (grafo IPC casi siempre **fuertemente conexo** entre `l1`…`lN`). |
| 5 | Al menos una furgoneta con capacidad ≥ 1 paquete (`capacity v c1` o superior). |

Si 1–5 se cumplen → **existe** un plan tipo:

```text
(recoger en l0) → (ir a cliente) → (soltar) → (volver hacia l0 vía hub) → repetir
```

Los viajes extra al depósito **no** están en el goal (`-open`); son parte del plan.

### Complejidad del mapa

- **No** fuertemente conectar `l0` con todo: solo **`l0 ↔ hub`**.
- La **complejidad** viene del grafo IPC (muchos `road`, rutas indirectas).
- Si en el futuro **podáis** aristas, hay que repetir el chequeo 4 (no partir el grafo entre depósito y algún goal).

### Qué no garantiza el checklist

- Que **`hff`** termine rápido (dificultad de **búsqueda**, no de factibilidad).
- Equivalencia con el certificado del plan de referencia IPC (otro `:init`).

Opcional: anotar en una nota “factibilidad estructural OK, fecha” — sin columna `solved` hasta evaluar heurísticas.

---

## 5. Cuántas y cuáles adaptar

**Estado actual:** 8 instancias en `testing/` (ver tabla y orden en `benchmarks/cvrp-strips/testing/README.md`).

Objetivo cumplido: **6–8 instancias** con variedad easy / medium / training, misma receta modo B.

| Rol | Carpeta | Ejemplos |
|-----|---------|----------|
| Prompt LLM | `training/` | `p01-open`, `p99-open` |
| Eval CVRP | `testing/` | `easy-p01` … `p50-open` (orden en README) |

**Training vs testing:** como Corrêa — `p01-open` + `p99-open` al prompt; el resto solo para Excel CVRP.

---

## 6. Orden de trabajo

### Hecho

- [x] `benchmarks/cvrp-strips/training/domain.pddl`
- [x] `p01-open.pddl` (modo B: `l1=2`, `l2=1`)
- [x] `p99-open.pddl` (modo B: demandas agrupadas desde conteo IPC)
- [x] `testing/p10-open.pddl` (modo B: 5+3+1+2)

### Próxima iteración

1. [ ] Crear **3–5 instancias modo B** en `testing/` (mapa IPC + **demanda por destino**).
2. [ ] Al menos **una** con algún cliente \(q_i > 1\) (paquetes fungibles en el mismo goal).
3. [ ] Checklist §4 en cada fichero.
4. [ ] (Opcional) Reescribir `p99-open` en modo B contando demandas del goal IPC.
5. [ ] `example-state.out` / `example-static.out` + `SUITES`.
6. [ ] Barrido heurísticas → Excel (factibilidad ya por §4).

---

## 7. Plantilla de cabecera

```text
;; CVRP-STRIPS open | mode B (demand-by-destination) | from ipc2023-learning/.../pXX
;; depot=l0 (hub l0↔l1) | demands: l2=3 l5=2 ... | vehicles=N packages=SUM(q_i)
;; feasibility: structural (connected hub + IPC graph)
```

---

## 8. Después de leer esto deberías poder…

- adaptar un `pXX` IPC en **modo A** o **modo B** (§3);
- escribir demandas \(q_i\) como varios `(at p_* l_j)` con la **misma** `l_j`;
- explicar por qué **p5 no sustituye a p3** en el goal (§3.4);
- explicar por qué **no hace falta resolver** para dar la instancia por factible;
- decir por qué **no** conectamos `l0` a todos los nodos;
- listar qué ficheros faltan antes del primer `--domain cvrp-strips` al LLM.

Siguiente doc relacionado: `04 - CVRP-STRIPS.md` §6–7 (heurísticas y checklist Fase 1).
