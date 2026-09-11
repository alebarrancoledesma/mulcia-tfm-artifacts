# MASTER PLAN — TFM Planificación híbrida (LLM como heurística, foco VRP)

**Estado:** plan operativo vigente  
**Fecha:** 5 de septiembre de 2026  
**Precedencia:** este documento manda en el **orden de trabajo** y en el **alcance mínimo defendible**. Los docs `01`–`04` siguen siendo detalle (estrategia larga, XAI, observabilidad, preferencias); si chocan con este, gana el MASTER.

---

## 1. De dónde venimos

Este plan no parte de un diseño libre. Parte de un enunciado oficial y de una lista de papers que los tutores pasaron como orientación. **No hay que ceñirse a reproducir esos papers**, pero sí hay que tener claro el marco: planificación clásica + LLMs como heurística + foco VRP. El resto (metaheurísticas, OGA, estancamiento) es extensión, no el contrato.

### 1.1. Enunciado oficial

**Propuesta 77. Planificación Híbrida: Uso de LLMs como Sistemas Heurísticos en Planificadores Clásicos enfocados en el Vehicle Routing Problem**

**Proponentes:** Antonio Ramírez de Arellano, J. Luis Ruiz Reina

> Este Trabajo Fin de Máster analiza el uso de Large Language Models (LLMs) como sistemas heurísticos para la planificación clásica, con especial énfasis en problemas de rutas de reparto. El objetivo es explorar hasta qué punto los LLMs pueden generar heurísticas eficaces, ya sea complementando o sustituyendo métodos tradicionales basados en búsqueda informada. El proyecto evaluará la capacidad de los modelos para razonar sobre estados, acciones y costes, así como para estimar distancias a la meta en instancias del Vehicle Routing Problem (VRP) y problemas afines. Además, se comparará su rendimiento con heurísticas clásicas y enfoques híbridos, analizando aspectos como generalización, robustez, coste computacional e interpretabilidad. El trabajo pretende contribuir a entender el potencial de los LLMs como módulos heurísticos en sistemas de planificación, abriendo el camino a nuevas arquitecturas híbridas para optimizar rutas en escenarios reales de logística y reparto.

Lo que el texto **exige** (el contrato):

- LLMs como **sistemas heurísticos**, no como planificadores end-to-end.
- Ámbito: **planificadores clásicos**.
- Dominio de aplicación: **VRP y problemas afines** (rutas de reparto).
- Generar heurísticas que **complementen o sustituyan** búsqueda informada tradicional.
- Razonar sobre **estados, acciones y costes**; **estimar distancias a la meta**.
- Comparar con **heurísticas clásicas** y **enfoques híbridos**.
- Analizar **generalización, robustez, coste computacional e interpretabilidad**.

Lo que el texto **abre** (no obliga): “nuevas arquitecturas híbridas para optimizar rutas en escenarios reales”. Ahí caben las metaheurísticas, **después** de cubrir el contrato.

### 1.2. Papers de referencia que nos pasaron

Lista tal como la recibimos. Rol previsto: **citar y situarnos**; no implementar cada uno.

#### Surveys

1. **LLMs as Planning Modelers/Formalizers: A Survey** (2025). arXiv:2503.18971.  
   LLM como constructor de modelos / traducción a PDDL / marcos neuro-simbólicos.

2. **Large Language Models for Planning: A Comprehensive and Systematic Survey** (2025). arXiv:2505.19683.  
   Tres familias: aumentados con módulos externos; fine-tuning; basados en búsqueda.

3. **On the Prospects of Incorporating Large Language Models (LLMs) in Automated Planning and Scheduling (APS)** (2024). Pallagani et al., arXiv:2401.02500.  
   Ocho categorías (traducción, generación de planes, construcción de modelos, multi-agente, planificación interactiva, **optimización de heurísticas**, integración de herramientas, brain-inspired). Nuestro sitio natural: *heuristics optimization*, no *plan generation*.

#### Fundamentos y aproximación neuro-simbólica

4. **LLM+P: Empowering Large Language Models with Optimal Planning Proficiency** (2023). Liu et al., arXiv:2304.11477.  
   El LLM entiende lenguaje y **escribe PDDL**; el planner clásico resuelve. Paradigma inverso al nuestro.

5. **SayCanPay: Heuristic Planning with Large Language Models using Learnable Domain Knowledge**. Hazra et al., arXiv:2308.12682.  
   El LLM entra **en el bucle** de búsqueda (acciones guiadas por factibilidad y recompensa). Híbrido distinto: no genera un `h(s)` en Python de una vez.

6. **Fast and Accurate Task Planning using Neuro-Symbolic Language Models and Multi-level Goal Decomposition** (2024). Kwon & Kim, arXiv:2409.19250.  
   Descomposición en subobjetivos + planner simbólico o MCTS-LLM. Fuera del núcleo.

#### LLMs para heurísticas

7. **Classical Planning with LLM-Generated Heuristics: Challenging the State of the Art with Python Code** (2025). Corrêa et al., arXiv:2503.18809.  
   **Base del TFM.** El LLM genera funciones heurísticas dependientes del dominio (código Python); se evalúan en train y se usan en best-first. Repo: Pyperplan + `transport`.

8. **Inspire or Predict? Exploring New Paradigms in Assisting Classical Planners with Large Language Models** (2025). Yu et al., arXiv:2508.11524.  
   LLM4Inspire (guía heurística / elección de acciones) vs LLM4Predict (conocimiento de dominio e estados intermedios). Relacionado; no se reproduce.

#### Otros

9. **TwoStep: Multi-agent Task Planning using Classical Planners and Large Language Models** (2024). Singh et al., arXiv:2403.17246.  
   Multi-agente / subobjetivos. Fuera de alcance.

10. **Aligning LLM+PDDL Symbolic Plans with Human Objective Specifications through Evolutionary Algorithm Guidance** (2025). arXiv:2412.00300.  
    Preferencias de usuario sobre planes PDDL. Solo relevante si más adelante se tocan preferencias blandas.

11. **On the role of Large Language Models in Planning**. Tutorial ICAPS 2023.  
    Tesis de encuadre: los LLM **no** son buenos generando planes por sí solos; sí como **complemento** de planificadores *sound*.

### 1.3. Cómo lo leemos (y por qué el plan es así)

- El enunciado y la bibliografía son de **planning + heurística + VRP**, no de GRASP/ALNS.
- El único paper de la lista que implementa “LLM → `h(s)` → planner clásico” es **Corrêa (7)**. Por eso se parte de su fork.
- LLM+P, SayCanPay e Inspire/Predict se **citan** como granulidades híbridas distintas (el LLM escribe el modelo, o actúa en el bucle). No se usan como start.
- Los surveys y el tutorial ICAPS van al estado del arte y a la frase de defensa.
- La última frase del enunciado (“arquitecturas híbridas… logística y reparto”) autoriza una Fase 2 de metaheurísticas **después** de cumplir el contrato en PDDL.

### 1.4. ¿Alguien ha hecho ya la Fase 1? ¿Por qué modificar Corrêa?

Hay **dos literaturas** que casi no se cruzan. La Fase 1 se mete en el hueco entre ambas. No se reclama un método nuevo; se reclama una **especialización experimental** al VRP que pide el enunciado.

#### Planning + heurística LLM (ya existe)

Corrêa **ya incluye `transport`** como uno de los ocho dominios IPC 2023: genera `hLLM`, la compara con heurísticas clásicas / Fast Downward y describe una heurística de shortest-path + asignación greedy de vehículos. Tuisov et al. hacen el mismo truco (LLM → `h` → GBFS), en Rust, sin foco VRP. Trabajos 2026 evolucionan heurísticas o las hacen admisibles: más planning general, no CVRP.

**Consecuencia:** no se puede decir “nadie ha usado heurísticas LLM en un dominio de transporte”. Sí se puede decir: lo usaron como **un dominio IPC más**, no como TFM de VRP/CVRP.

#### LLM + CVRP de investigación operativa (otra cosa)

VRPAgent, AILS-AHD, HeurAgenix, EoH, etc. El LLM diseña **operadores** de LNS/ILS sobre rutas, no un `h(s)` PDDL. Eso es el mundo de la Fase 2, no el de la Fase 1.

#### Qué no está hecho (el hueco del TFM)

Nadie junta, que sepamos: **paradigma Corrêa + modelo CVRP-STRIPS + evaluación de routing** (presión de capacidad, km post-hoc, `h(s)` vs plan, XAI ligero). Esa intersección es la Fase 1.

Si solo se repite el `transport` IPC de Corrêa + `hFF`, es una **reproducción** y el TFM se queda corto. La aportación empieza al cambiar el **problema** y **cómo se mide**, no al reescribir el generador de heurísticas.

#### Qué se toca y qué no

| Tocar | ¿Sí? |
|---|---|
| Instancias / dominio PDDL hacia CVRP (depósito, paquetes desde `l0`, capacidad, retorno si es barato) | Sí: es la aportación |
| Generar `hLLM` otra vez **para ese dominio** | Sí: el `h` de `transport` IPC no tiene por qué servir |
| Métricas extra (km, stress, XAI) | Sí: lo pide el enunciado y el paper no lo hace |
| Motor, grounding, GBFS de Pyperplan | **No.** No aporta y come la semana |

El propio repo documenta cómo añadir un `DomainSuite`. Usar el pipeline y cambiar el problema es el uso previsto.

#### Cómo decirlo (y cómo no)

**No:** “Somos los primeros en heurísticas LLM para transporte / VRP.”  
Corrêa ya tiene `transport`; VRPAgent ya tiene CVRP (otro paradigma).

**Sí:** “El método de generar `h(s)` en Python está establecido. Lo que no está hecho es **ceñirlo a un CVRP modelado en STRIPS** y medirlo como problema de reparto (capacidad, distancia, interpretabilidad), que es lo que pide la propuesta 77.”

Riesgo a evitar: que el cambio de dominio sea tan cosmético que parezca el appendix de Corrêa. Se evita si las instancias **se ven** CVRP, el stress habla de capacidad/escala de reparto, y en memoria se distingue `transport` IPC (control, Fase 0) vs CVRP-STRIPS (contribución, Fase 1).

---

## 2. Decisión de secuencia (la puerta)

Sí: **todo el núcleo se hace en PDDL / planificación clásica.**  
Las metaheurísticas (GRASP/ALNS, OGA, LLM por estancamiento) **solo se tocan cuando la capa PDDL esté hecha y congelada**.

```text
Corrêa tal cual
      ↓
CVRP-STRIPS + clásicas + costes/h* + robustez + XAI
      ↓
  GATE: hay tablas y se puede defender la propuesta 77
      ↓
metaheurísticas (opcional / extra)
```

No se empieza el repo `llm-guided-cvrp-metaheuristic` ni se diseña ALNS “un rato” en paralelo. Si el tiempo se acaba en el GATE, el TFM **sigue siendo la propuesta**.

---

## 3. Encaje con la propuesta 77

**Título:** *Uso de LLMs como sistemas heurísticos en planificadores clásicos enfocados en el VRP.*

El contrato con los tutores es:

| Exigencia del enunciado | Dónde se cubre |
|---|---|
| LLM genera heurísticas (complementa/sustituye búsqueda informada) | `hLLM` vs `hFF` (+ otra clásica si entra) en GBFS |
| Estados, acciones y costes | estado PDDL + km post-hoc o `h(s)` vs plan |
| Distancia a la meta | `h(s)` en instancias pequeñas |
| VRP y afines | instancias **CVRP-STRIPS**, no solo `transport` IPC |
| Clásicas e híbridos | `hFF` / Fast Downward; híbrido = LLM escribe `h`, el planner busca |
| Generalización, robustez, coste, interpretabilidad | stress + métricas + XAI ligero |
| Arquitecturas híbridas para rutas reales | **después del GATE**, si hay tiempo |

Base técnica: **Corrêa et al. (NeurIPS 2025)**. No se reimplementa el pipeline. No se arranca por LLM+P, SayCanPay, Inspire/Predict ni GRASP.

---

## 4. Fase 0 — Probar Corrêa (sin tocar el dominio)

**Repo:** `llm-generated-heuristics-vrp`  
**Objetivo:** infraestructura viva. No es aún la aportación.

Checklist:

- [x] `uv sync`
- [x] `transport` IPC + `hFF` (`p01`, `easy-p01`, `easy-p10`)
- [x] `transport` IPC + `blind` (`p01`, `easy-p01`; `easy-p10` timeout >90s)
- [ ] generar una heurística LLM (`llm-heuristics.py --domain transport`) — **bloqueado: no hay API key en el entorno**
- [ ] `transport` + `hLLM` en al menos 1–2 instancias training/testing
- [x] primera tabla smoke en `llm-generated-heuristics-vrp/results/fase0_hff_blind.csv`

**Prohibido en esta fase:** PDDL nuevo, Fast Downward, XAI, metaheurísticas, unificar formatos de instancia.

**Salida:** “Corrêa corre en esta máquina.”

---

## 5. Fase 1 — Núcleo PDDL (aquí está el TFM)

Todo sigue en el fork de Corrêa / Pyperplan (y Fast Downward **solo si se engancha rápido**).  
No hay GRASP aquí.

### 5.1. VRP de verdad (CVRP-STRIPS)

Instancias PDDL con forma de CVRP, dominio `transport` o un suite nuevo `cvrp` / `transport-cvrp`:

- un depósito `l0`
- cada cliente = paquete que **sale del depósito** y acaba en su localización
- vehículos que salen de `l0`
- capacidad discreta (CVRP **unitario**: 1 cliente = 1 hueco)
- grafo desde geometría (completo o k-vecinos)
- retorno a depósito **si es barato** (`at v_i l0` en el goal); si complica la heurística, se documenta como CVRP abierto

Se mantiene el IPC `transport` como **control** (“el método original sigue funcionando”).  
Las instancias nuevas son **las del TFM**.

No se reescribe Pyperplan. No fluents numéricos. No `:action-costs` en Pyperplan.

### 5.2. Heurísticas clásicas de planning

Mismo buscador (GBFS), cambia `h`:

```text
mínimo:     blind | hFF | hLLM
preferible: + 1 heurística Fast Downward (FF / hAdd / CG)
```

Si FD no entra en poco tiempo, se deja y se sigue. No se implementa A\* óptimo ni se afirma admisibilidad de `hLLM`.

### 5.3. Costes / distancia a la meta

Sin tocar el motor de Pyperplan:

1. **Km post-hoc:** del plan `drive/pick/drop` se reconstruyen rutas y se mide distancia euclídea (misma geometría que usaríamos luego en OGA).
2. **`h(s)` vs plan:** en 3–5 instancias tiny, comparar el valor heurístico en el init (y, si es barato, en algún estado intermedio) con la longitud real del plan o con `h*` si se puede obtener.

Action costs reales (Fast Downward) = extra, no bloqueante.

### 5.4. Robustez (stress test)

Pocas instancias, bien elegidas — no ocho dominios IPC.

- **Escala:** p. ej. ~10 / 20 / 40 clientes (parar cuando haya timeouts).
- **Capacidad:** holgada → justa (`CP` ≈ carga / capacidad total).

Topología (denso / clusters / cuello de botella) solo si no retrasa el GATE.

Métricas: coverage, expansiones, tiempo, longitud de plan, timeout; km post-hoc si ya está el evaluador.

### 5.5. Interpretabilidad (XAI ligero)

Como en `02 - ampliacion_xai_bloque1_planificacion_clasica.md`, barato:

- junto a `heuristic.py`, un `metadata.json`: `features_used`, `intuition`, `expected_strengths`, `expected_weaknesses`
- contraste explicación vs código (manual, pocas heurísticas)
- contraste debilidades declaradas vs stress (capacidad / escala)

No es un paper de XAI. El planner no usa el JSON.

### 5.6. Salida de la Fase 1

- [ ] suite CVRP-STRIPS + (opcional) generador/exportador desde geometría canónica
- [ ] tabla `hFF` / `blind` / `hLLM` (+ FD si existe) en IPC control y en CVRP-STRIPS
- [ ] tabla/gráfica de stress (escala y/o capacidad)
- [ ] km post-hoc y/o `h(s)` vs plan en instancias pequeñas
- [ ] metadata XAI de la heurística LLM usada
- [ ] CSV/tabla única tipo `results_planning.csv`

---

## 6. GATE — congelar Parte I

Al terminar la Fase 1:

> **Feature freeze de planificación clásica.**

Criterio para pasar: se puede defender la propuesta 77 **sin** mencionar GRASP.

Si falta tiempo, **no se abre Fase 2**. Se escribe memoria con lo de PDDL.

---

## 7. Fase 2 — Metaheurísticas (solo después del GATE)

**Repo:** `llm-guided-cvrp-metaheuristic` (independiente, sin código GPL del fork).  
Detalle: `01`, `03`, `04`. Aquí solo el orden.

1. CVRP OGA sencillo (Solomon-lite, `Instance` / `Solution`, `get_quality()` = distancia). Sin LLM.
2. Misma geometría que alguna instancia CVRP-STRIPS de la Fase 1 (pack canónico → dos lecturas).
3. ALNS/GRASP-lite + Adaptive vs LLM-estancamiento.
4. Extras (`03` observabilidad, `04` preferencias) solo si 1–3 ya corren.

Esto es la frase final del enunciado (“arquitecturas híbridas para rutas”), no el contrato.

---

## 8. Instancias: canónico después, no antes

Durante Fase 0–1 se puede generar PDDL a mano o con un script mínimo.

Un formato canónico estilo OGA (Solomon-lite) + exporter PDDL **tiene sentido** cuando:

- las instancias CVRP-STRIPS ya existen, y
- se va a abrir Fase 2 y se quieren geometrías gemelas.

No bloquear Fase 1 a la espera de un formato unificado.

Significado honesto de “la misma instancia”: **misma geometría y flota**, dos modelos (STRIPS vs rutas). No el mismo óptimo ni las mismas unidades, salvo que más adelante haya action costs.

---

## 9. Repos

| Repo | Rol | Cuándo |
|---|---|---|
| `llm-generated-heuristics-vrp` | Fork Corrêa (GPL). Fases 0 y 1. | Ahora |
| `llm-guided-cvrp-metaheuristic` | CVRP OGA + selectores. Fase 2. | Tras el GATE |
| `docs/plan/` | Este MASTER + ampliaciones | — |

No mezclar código entre repos.

---

## 10. Recorte si falta tiempo

Quitar en este orden:

1. Fase 2 completa  
2. Preferencias blandas (`04`)  
3. Observabilidad rica / ablación XAI (`03`)  
4. Fast Downward  
5. Action costs  
6. `h(s)` vs `h*`  
7. Tercer eje de stress (topología)  
8. Retorno a depósito en el PDDL  

**No quitar:**

- Corrêa funcionando  
- al menos un lote CVRP-STRIPS  
- `hFF` vs `hLLM`  
- un stress (escala **o** capacidad)  
- XAI mínimo (los cuatro campos)  
- tablas y discusión

---

## 11. Claims

**Sí**

- Partimos de un método SOTA de heurísticas LLM para planning y lo especializamos a VRP/CVRP-STRIPS.
- Comparamos `hLLM` con heurísticas clásicas de planning, no con GRASP.
- Analizamos robustez, coste computacional e interpretabilidad ligera.
- Si hay Fase 2: el mismo rol de módulo heurístico puede subir a nivel de búsqueda cuando los estados no escalan.

**No**

- “Hemos propuesto el primer LLM para VRP / para generar heurísticas.” (Corrêa ya tiene `transport`; VRPAgent ya tiene CVRP en otro paradigma. Detalle: §1.4.)
- “`hLLM` es admisible / A\* óptimo.”
- “El planner resuelve CVRP mejor que ALNS” (unidades distintas).
- “La explicación XAI es el razonamiento interno del modelo.”

---

## 12. Roadmap compacto

| Orden | Qué | Hecho cuando |
|---|---|---|
| 0 | Corrêa + `transport` + `hFF`/`blind`/`hLLM` | Hay una tabla IPC |
| 1a | Instancias CVRP-STRIPS | `p01`… y un suite |
| 1b | Bake-off clásicas en esas instancias | Segunda tabla |
| 1c | Stress escala/capacidad | Gráfica o tabla por nivel |
| 1d | Km post-hoc y/o `h(s)` vs plan | Columna o mini-tabla |
| 1e | XAI ligero | `metadata.json` + 1 comentario en memoria |
| GATE | Freeze Parte I | Se puede escribir el capítulo 4 |
| 2 | Metaheurísticas | Solo si el GATE está cerrado |

---

## 13. Documentos relacionados

| Doc | Uso |
|---|---|
| Este MASTER, §1 | Enunciado oficial, papers, y §1.4 (qué hay ya / cómo reclamar la Fase 1) |
| `01 - estrategia_tfm_llm_planning_cvrp.md` | Estrategia larga, SoA, baselines Parte II, bibliografía |
| `02 - ampliacion_xai_bloque1_planificacion_clasica.md` | Cómo hacer el XAI de la Fase 1 |
| `03 - ampliacion_observabilidad_xai_metaheuristicas_tfm.md` | Solo Fase 2 |
| `04 - ampliacion_preferencias_blandas_lenguaje_natural_cvrp.md` | Solo Fase 2, último extra |

---

## 14. Una línea

> **Primero que Corrêa corra; después un CVRP en PDDL con heurísticas clásicas, costes/distancia a la meta, stress e interpretabilidad; solo entonces, si sobra, metaheurísticas.**
