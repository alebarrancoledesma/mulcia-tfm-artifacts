# DAY-01 — Informe de sesión (2026-09-05)

Documento de handoff para conversación de alto nivel con otra IA / tutores. Resume **todo** lo trabajado hoy en **Fase 0** (IPC `transport`) y **Fase 1** (CVRP-STRIPS), resultados conocidos, limitaciones del modelado, y **inquietudes abiertas** del autor.

**Repo:** `llm-generated-heuristics-vrp`  
**Docs:** `docs/explain/`, `docs/plan/MASTER_PLAN.md`, `docs/results/`

---

## 1. Contexto y objetivo del TFM (recordatorio mínimo)

- **Propuesta 77:** LLMs como **heurísticas** (`h(s)` en Python) dentro de **planificadores clásicos** (Pyperplan + GBFS), aplicado a **VRP/CVRP**, no planificación end-to-end.
- **Base metodológica:** Corrêa et al. (NeurIPS 2025) — fork del repo oficial.
- **Secuencia acordada (MASTER_PLAN):**
  1. Fase 0 — reproducir pipeline en dominio IPC `transport` (control).
  2. Fase 1 — instancias **CVRP-like** en el mismo dominio STRIPS + nueva heurística LLM + tabla comparativa.
  3. **GATE** — tablas defendibles antes de metaheurísticas / PDDL 2.1 / XAI pesado.
- **Lo que el LLM no hace:** no escribe planes `.soln`; genera código de heurística. Pyperplan busca con `-s gbfs_early_goal_test -H …`.

---

## 2. Infraestructura montada hoy

| Componente | Estado |
|---|---|
| Entorno `uv` + Pyperplan | OK |
| `.env` con `DEEPSEEK_API_KEY` | OK (script lee `.env` desde cwd del repo) |
| Guías operativas | `docs/explain/01`–`05` (Corrêa, PDDL, ejecutar, CVRP-STRIPS, crear instancias) |
| `MASTER_PLAN.md` | Actualizado (Fase 0/1, GATE, claims) |
| Suite LLM `transport` | Ya existía (IPC training) |
| Suite LLM **`cvrp-strips`** | Añadida en `src/llm_heuristics/suites.py` |
| Benchmark CVRP | `benchmarks/cvrp-strips/training/` + `testing/` |
| Artefactos LLM | `docs/results/01 - llm assets/` (Fase 0), `02 - llm assets/` (Fase 1) |

**Comandos clave:**

```text
# Generar heurística
uv run llm-heuristics.py --framework deepseek --model deepseek-v4-flash --domain <transport|cvrp-strips> --heuristic-name …Heuristic --heuristic-file ….py --no-thinking

# Evaluar
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H <hff|blind|….py> benchmarks/…/instancia.pddl
```

---

## 3. Fase 0 — IPC `transport` (control)

### 3.1. Qué se hizo

1. Smoke **Pyperplan + GBFS** con `hff` y `blind` en instancias pequeñas/medias del IPC.
2. Generación **heurística LLM candidata 01** (`TransportHeuristic`, DeepSeek V4 Flash, **thinking off**).
3. Evaluación de esa $h$ en varias instancias `testing/transport/`.
4. Documentación cualitativa + copia de instancias/planes resueltos en `docs/results/01 - llm assets/`.

### 3.2. Generación LLM (Transport)

| Campo | Valor |
|---|---|
| Modelo | DeepSeek V4 Flash |
| Thinking | **off** (`--no-thinking`) — obligatorio tras fallo |
| Clase | `TransportHeuristic` |
| Artefacto | `01 - transport-heuristic.py` |

**Intento fallido previo (misma config, thinking ON por defecto API):** ~11 554 tokens prompt; ~63 788 reasoning; salida truncada en **65 536** tokens → **sin `.py` usable** (~9 min).

### 3.3. Tabla smoke `hff` / `blind` (Fase 0)

*(Datos de la sesión; formato tipo Excel `fase0_hff_blind.csv` — el CSV puede vivir fuera del repo o pendiente de consolidar.)*

| Instancia | Heurística | ¿Resuelve? | Long. plan | Expansiones | Tiempo | Notas |
|---|---|:---:|---:|---:|---:|---|
| `training/transport/p01` | `hff` | sí | 3 | 3 | ~0 s | 1 veh., 1 paq. |
| `training/transport/p01` | `blind` | sí | 3 | 4 | ~0 s | mismo plan, más expansión |
| `testing/transport/easy-p01` | `hff` | sí | 3 | 3 | ~0 s | |
| `testing/transport/easy-p01` | `blind` | sí | 3 | 21 | ~0 s | blind explora mucho más |
| `testing/transport/easy-p10` | `hff` | sí | 21 | 51 | ~0,75 s | 5 paq., 4 veh. |
| `testing/transport/easy-p10` | `blind` | **no** | — | — | **>90 s** | cortado manualmente |

**Lectura:** $h^{\mathrm{FF}}$ ya separa claramente de `blind` en cuanto crece el problema. GBFS con `blind` no escala ni en instancias modestas.

### 3.4. Tabla heurística LLM — Transport (candidata 01)

| Instancia | Long. plan (LLM $h$) | Comparación conocida |
|---|---:|---|
| `easy-p01` | 3 | Mismo orden que `hff` |
| `easy-p10` | 19 | Plan **más corto** que `hff` (21) |
| `easy-p20` | 39 | **Menos** que `hff` (~45 en pruebas previas) |
| `medium-p01` | 23 | **`hff` no terminó** en tiempo razonable; LLM **sí** |

Planes copiados: `docs/results/01 - llm assets/01 - transport-*-llm.soln`.

### 3.5. Conclusión cualitativa — `TransportHeuristic`

**Idea de $h$:** suma por paquete de distancia BFS en `road` + coste fijo pick-up/drop; distingue paquete en suelo vs. en vehículo.

**Fortalezas:** código válido; usa mapa; en Fase 0 **compite con $h^{\mathrm{FF}}$** en el recorte probado; en `medium-p01` **desbloquea** donde FF no acaba.

**Debilidades:** no admisible; suma independiente por paquete; **no cuenta ir a recoger** el paquete (subestima si el vehículo está lejos); capacidad parseada pero **no entra** en el número; una sola candidata (no protocolo ~25 del paper).

**Frase defendible para memoria (borrador):**

> En Pyperplan + GBFS, una candidata DeepSeek V4 Flash (thinking off) se comparó con `blind` y $h^{\mathrm{FF}}$ sobre un recorte de `transport`. En instancias pequeñas es del orden de $h^{\mathrm{FF}}$ y claramente mejor que `blind`. En `easy-p20` reduce expansiones/longitud respecto a $h^{\mathrm{FF}}$. En `medium-p01`, $h^{\mathrm{FF}}$ no termina en el tiempo de corte y la $h$ del LLM sí. No se ha ejecutado el protocolo de ~25 candidatas ni Fast Downward.

---

## 4. Fase 1 — CVRP-STRIPS

### 4.1. Qué es CVRP-STRIPS (decisión de modelado)

Mismo **`domain.pddl`** que IPC `transport` (`drive`, `pick-up`, `drop`, capacidad por peldaños `c0<c1<…`). Cambia la **instancia**:

| | IPC original | CVRP-STRIPS |
|---|---|---|
| Depósito | no existe | `l0` + hub `l0↔l1` |
| Inicio paquetes | repartidos | **todos en `l0`** |
| Inicio vehículos | repartidos | **todos en `l0`** |
| Goal | entregas | `(at p_i l_cliente)` — sufijo **`-open`** (sin retorno al depósito) |
| Demanda | implícita 1/paq. | **Modo B:** varios paquetes pueden compartir destino (demanda $q_j$ = varios literales al mismo `l_j`) |

**Training (prompt LLM):** `p01-open` (tiny manual), `p99-open` (grande, adaptada modo B).  
**Testing (evaluación):** 7 instancias — catálogo y orden en `benchmarks/cvrp-strips/testing/README.md`.

### 4.2. Montaje del prompt LLM (sin prompt específico nuevo)

- **Misma plantilla NeurIPS 2025** que Corrêa; cambia la suite (`cvrp-strips` → otros `.pddl` + `example-state.out` / `example-static.out`).
- Entrada `SUITES` apunta a `training/`.
- **`testing/` no entra al prompt.**

Generación realizada:

| Campo | Valor |
|---|---|
| `--domain` | `cvrp-strips` |
| Modelo | DeepSeek V4 Flash, thinking off |
| Clase | `CvrpStripsHeuristic` |
| Artefacto | `cvrp-strips-heuristic.py` + copia en `docs/results/02 - llm assets/` |

### 4.3. Limitaciones estructurales al crear instancias

Documentadas en `04 - CVRP-STRIPS.md` y `05 - CVRP-INSTANCE-CREATE.md`:

1. **Identidades en el goal:** `(at p3 l1)` no es “cualquier paquete”; `p5` **no sustituye** a `p3`. Es CVRP unitario discretizado con etiquetas, no demanda agregada OR.
2. **OR combinatorio en goal:** descartado (explosión, Pyperplan).
3. **Factibilidad:** argumento **topológico** (hub `l1` alcanza clientes del goal; no hace falta resolver cada `.pddl` para certificar).
4. **Mapa:** solo hub `l0↔l1`, no estrella desde depósito a todos los clientes; complejidad viene del grafo IPC.
5. **`hff` lento ≠ infactible** — dificultad de búsqueda, no de existencia de plan.
6. **Fase 2.5 (opcional post-GATE):** PDDL 2.1 + fluents + Fast Downward para demanda agregada “de libro”.

### 4.4. Resultados experimentales (Fase 1)

Fuente: **`docs/results/02 - cvrp-like pddl results.xlsx`**. Pyperplan, `-s gbfs_early_goal_test`. Heurística LLM: `CvrpStripsHeuristic` (DeepSeek V4 Flash, thinking off). Corte `blind`: 600 s.

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

**Coverage:** LLM 6/6 instancias del Excel. `blind` timeout en 4/6. `p10-open` (en catálogo `testing/`) **no** está en el Excel.

**Lectura:** resultado **mixto**. La $h$ LLM brilla en `easy-p10` (menos expansiones, plan más corto) y `medium-p01` (24 vs 41 expansiones). En `easy-p20` y `p50` resuelve pero con **~80× más expansiones** que $h^{\mathrm{FF}}$ — la heurística guía peor cuando crece carga y mapa.

### 4.5. Conclusión cualitativa — `CvrpStripsHeuristic`

**Idea de $h$:** Floyd–Warshall precalculado; por paquete pendiente, coste mínimo usando un vehículo con hueco (vehículo→paquete→goal + pick/drop); extra de “vuelta a `l0`” para vehículos vacíos.

**Mejoras vs. Transport (Fase 0):** sí intenta acercar vehículo al paquete; filtra capacidad $>0$; distancias precalculadas.

**Problemas respecto al objetivo CVRP open:**

- Sigue siendo **suma independiente** por paquete (no routing capacitado real).
- **Return-to-`l0`** en vehículos vacíos — el goal **open** no lo exige → posible sobreestimación / ruido en GBFS.
- Docstring promete **agrupación por destino**; código **no** la implementa.
- Fallback `+2` si ningún vehículo tiene hueco — arbitrario.
- `initial_capacities` calculado y no usado.

**Empírico (Excel):** buena en pequeño/medio (`easy-p10`, `medium-p01`); degradación fuerte en `easy-p20` y `p50` (expansiones ~80× peores que FF pese a resolver).

Análisis extendido: `docs/results/02 - llm assets/01 - cvrp-strips-heuristics.md` y `-report.md`.

---

## 5. Documentación y artefactos producidos

```
docs/explain/
  01 - CORREA.md
  02 - PDDL.md
  03 - EJECUTAR.md
  04 - CVRP-STRIPS.md
  05 - CVRP-INSTANCE-CREATE.md

docs/results/
  01 - llm assets/     ← Transport (Fase 0)
  02 - llm assets/     ← CVRP (Fase 1)

benchmarks/cvrp-strips/
  training/            ← prompt (p01-open, p99-open, example-*.out)
  testing/             ← eval (7 instancias, README con orden)

src/llm_heuristics/suites.py   ← entrada "cvrp-strips"
```

**Nota de proceso:** en un momento se añadió un script `adapt_ipc_to_cvrp_strips.py` — **eliminado**; las instancias ya estaban en el repo y no forman parte del pipeline de evaluación/prompt.

---

## 6. Coste API (orden de magnitud)

- Gasto acumulado hoy: **~$0,10** (dos generaciones Flash + pruebas).
- Presupuesto disponible mencionado: **$6** inicialmente; el autor indica que puede subir a **~$20** si hace falta para candidatas extra y fases siguientes.
- **Conclusión de coste:** hay margen amplio para 1–2 candidatas **Pro** y reintentos controlados; no hace falta protocolo de 25 candidatas para un TFM defendible.

---

## 7. ¿Vamos por buen camino?

**Sí, con matices.**

| Criterio (propuesta 77 / MASTER) | Estado |
|---|---|
| Pipeline Corrêa funcionando | ✅ |
| Comparación `blind` / $h^{\mathrm{FF}}$ / $h$ LLM | ✅ Fase 0; ✅ Fase 1 (Excel 6 instancias) |
| Problema **VRP-like** (no solo IPC crudo) | ✅ CVRP-STRIPS con depósito y modo B |
| Métricas (coverage, expansiones, tiempo, longitud) | ✅ `02 - cvrp-like pddl results.xlsx` |
| Interpretabilidad | 📋 planificado (XAI ligero) |
| Una candidata vs. paper | ⚠️ limitación conocida y documentada |

**No es reproducción pura de Corrêa:** cambiamos el **problema** (instancias CVRP) y generamos **nueva** $h$. Eso es exactamente el hueco que describe MASTER §1.4.

**GATE parcial:** tabla Fase 1 con 6 instancias defendible; falta `p10-open` en Excel y posible 2.ª candidata LLM antes de metaheurísticas o PDDL 2.1.

---

## 8. Inquietudes abiertas (autor — para discutir con IA/tutores)

### 8.1. ¿Segunda generación con Pro y/o thinking?

- **Flash sin thinking** funciona y es barato; es la **línea base** actual (candidata 01 en ambas fases).
- **Thinking ON** falló en Transport (truncado 65 536 tokens, sin código).
- **Recomendación razonable:**
  1. Terminar tablas con candidata 01.
  2. Generar **candidata 02: `deepseek-v4-pro`, thinking OFF**.
  3. Probar **Pro + thinking** solo una vez, verificando que el `.py` cierra; si trunca, no insistir.
  4. Opcional: `--idea "…"` (goal open, sin return-to-depot, evitar suma por paquete) — barato y a veces más efectivo que thinking.

Con **$20** de techo, 2–4 generaciones extra es razonable; no hace falta quemarlo todo.

### 8.2. ¿Construir CVRP “total” con PDDL avanzado y otra heurística LLM?

- **Fase 2.5 (PDDL 2.1 + fluents + Fast Downward):** demanda agregada real, más fiel al CVRP de libro; **fuera de Pyperplan + Corrêa tal cual**.
- **Cuándo:** solo **después del GATE** de Fase 1, si el STRIPS ya se defiende y hay tiempo.
- **Otras heurísticas clásicas:** MASTER y estrategia mencionan ampliar más allá de `blind`/`hff` (p. ej. Fast Downward en dominios derivados). No es obligatorio para cerrar Fase 1; sería refuerzo metodológico.
- **Riesgo:** abrir FD + PDDL 2.1 **antes** de cerrar tablas STRIPS dispersa el esfuerzo.

### 8.3. ¿Vamos por buen camino? (duda del autor)

Ver §7. El núcleo contractual (LLM → $h$ → GBFS → comparar con clásicas → dominio routing) **sí** se está cumpliendo. La incertidumbre es normal en la **magnitud del resultado** (¿la $h$ CVRP bate a FF?) y en **cuánto profundizar** (candidatas, PDDL+, XAI). El plan por fases + GATE está pensado precisamente para no perderse.

### 8.4. ¿XAI en algún momento sin reescribir el pipeline?

**Sí encaja**, y el repo lo permite con poco cambio:

- **Hoy:** el LLM ya escribe un **docstring largo** (Summary, Assumptions, Initialization, Step-by-Step) — es explicación implícita no estructurada.
- **Propuesta (doc `02 - ampliacion_xai_bloque1…`):**
  - Pedir al LLM un bloque final delimitado, p. ej. `# XAI_JSON … #` o comentario markdown, y extraer con **regex** en `sanitize_llm_answer` / post-proceso → `heuristic_metadata.json`.
  - El planner **solo ejecuta** el `.py`; la explicación no entra en Pyperplan.
  - Contrastar `features_used` declaradas vs. variables realmente leídas en el código vs. stress tests (capacidad, muchos paquetes).
- **Cuándo:** Bloque 1 / GATE, **después** de tener al menos una $h$ estable; no bloquea el barrido actual.
- **Ventaja:** encaja con “no cambiar mucho la implementación Corrêa” — extensión en generación + parser, no en GBFS.

### 8.5. ¿Torneo de candidatas (replicar Corrêa) o modelado CVRP más realista antes?

**Inquietud del autor (sin decidir aún):**

Corrêa genera **~25 candidatas**, las prueba en training y se queda con la ganadora. Nosotros llevamos **1 candidata** por fase (Flash, thinking off). Cuando tengamos un **modelo “guay”** (¿Pro? ¿Flash + `--idea`?) y veamos que el código sale estable, **¿merece la pena montar un mini-torneo** (p. ej. 5–10 tiradas, selección en `training/p01-open` + `p99-open`, evaluación ciega en `testing/`)?

**A favor del torneo:**

- Acerca el relato al paper sin llegar a 25.
- Con ~$20 de presupuesto, 5–10 generaciones Pro **cabe** si no se repite thinking truncado.
- Podría arreglar casos donde candidata 01 falla fuerte (`easy-p20`, `p50` en expansiones).

**En contra / dudas:**

- Es **más lío operativo**: N `.py`, trazabilidad, elegir ganadora, documentar por qué — tiempo que no va a la memoria “bonita” si el resultado es marginal.
- El paper elige en dominios IPC **genéricos**; nosotros ya cambiamos el **problema** a CVRP-STRIPS. ¿Tiene sentido un torneo sobre un modelado que el propio autor siente **aún imperfecto**?
- **Alternativa que tira más:** antes del torneo, **modelar algo más fiel al CVRP de verdad** (demanda agregada, PDDL 2.1, FD — Fase 2.5 del MASTER; o al menos cerrar limitaciones STRIPS: identidades en goal, goal open vs closed, instancias más duras tipo `hard-p01`). Si el dominio cambia, **hay que regenerar** todas las candidatas igualmente.

**Tensión que resume la duda:**

```text
¿Profundizar en el PROTOCOLO (torneo Corrêa) con el STRIPS actual?
        vs
¿Profundizar en el PROBLEMA (CVRP más realista) y luego 1–2 candidatas buenas?
```

**Sesgo provisional (para debatir con la otra IA):** con un solo día de datos, el cuello de botella no parece “solo faltaba la candidata 12”, sino que la $h$ **degrada** en instancias grandes dentro del STRIPS actual. Eso sugiere que **arreglar modelado o prompt** (`--idea`, quitar return-to-`l0`, Pro) puede rendir más que un torneo largo sobre el mismo dominio. Pero **no está cerrado**: un torneo pequeño **después** de fijar modelo + suite podría ser un capítulo defendible (“mini-replicación del protocolo de selección”) sin bloquear Fase 2.5.

**Preguntas concretas para la otra conversación:**

1. ¿Mini-torneo (N candidatas, N≈5–10) es requisito defendible para el TFM o basta 2–3 candidatas documentadas?
2. ¿Torneo sobre CVRP-STRIPS actual o solo después de un salto de fidelidad (PDDL+ / demanda agregada)?
3. ¿El torneo compite con tiempo para instancias **más difíciles** (`hard-p01`, más paquetes) o las sustituye?

### 8.6. ¿Instancias aún más difíciles?

Relacionado con lo anterior: el Excel ya muestra estrés en `easy-p20` y `p50` (LLM resuelve pero con ~80× expansiones vs FF). **¿Hace falta añadir `hard-p01` u otras del IPC** antes de cerrar Fase 1, o eso solo tiene sentido **después** de mejorar la heurística / modelado?

- **A favor:** demuestra dónde muere cada $h$; alinea con “robustez” del enunciado.
- **En contra:** más filas en Excel, más tiempo de cómputo (`blind` ya timeout a 600 s); si el modelado STRIPS no es el final, puede ser esfuerzo desechable.

**Estado:** catálogo actual = 6 instancias en Excel + `p10-open` pendiente; `hard-*` no adaptadas. Decisión abierta.

---

## 9. Próximos pasos concretos (prioridad)

1. **Añadir `p10-open`** al Excel (misma schema) si se quiere cerrar el catálogo de 7.
2. **Decidir candidata 02** (Pro sin thinking) sobre todo por el fallo en `easy-p20` / `p50`.
3. **GATE:** ¿tabla Fase 0 + Fase 1 defendible? → entonces metaheurísticas / PDDL+ / XAI.
4. **Opcional:** párrafo `--idea` o bloque XAI en prompt antes de gastar en thinking.

---

## 10. Referencias rápidas internas

| Tema | Dónde |
|---|---|
| Cómo ejecutar | `docs/explain/03 - EJECUTAR.md` |
| Modelado CVRP | `docs/explain/04 - CVRP-STRIPS.md` |
| Catálogo instancias eval | `benchmarks/cvrp-strips/testing/README.md` |
| Análisis $h$ Transport | `docs/results/01 - llm assets/01 - transport-heuristics.md` |
| Análisis $h$ CVRP | `docs/results/02 - llm assets/01 - cvrp-strips-heuristics.md` |
| Plan global | `docs/plan/MASTER_PLAN.md` |
| XAI ligero (diseño) | `docs/plan/02 - ampliacion_xai_bloque1_planificacion_clasica.md` |

---

*Fin DAY-01 — 2026-09-05*
