# Ampliación del TFM: observabilidad temporal, diagnóstico semántico y XAI en metaheurísticas CVRP

**Documento complementario a la estrategia consolidada del TFM**  
**Fecha:** 5 de septiembre de 2026

---

## 1. Objetivo de la ampliación

La segunda parte del TFM no se limitará a utilizar el LLM como selector de operadores o estrategias dentro de una metaheurística.

Se propone añadir una **capa de observabilidad semántica de la búsqueda**, capaz de transformar telemetría numérica de la metaheurística en:

1. un diagnóstico interpretable del estado de búsqueda;
2. una explicación estructurada y fundamentada;
3. una recomendación estratégica;
4. un registro temporal que permita analizar posteriormente la evolución de la optimización.

La idea central pasa a ser:

$$
\boxed{
\text{Search telemetry}
\rightarrow
\text{LLM}
\rightarrow
\text{Diagnosis + Strategy + Explanation}
}
$$

El LLM actúa por tanto como:

$$
\boxed{
\text{Observer}
+
\text{Diagnostician}
+
\text{Heuristic Controller}
}
$$

No sustituye al solver ni ejecuta directamente operaciones arbitrarias.

---

# 2. Motivación

Una metaheurística convencional proporciona normalmente telemetría numérica:

```text
iteration = 7500
best_cost = 15191.8
current_cost = 15320.4
iterations_without_improvement = 750
solution_similarity_to_best = 0.96
2opt_success_rate = 0.01
relocate_success_rate = 0.03
```

Estos datos son útiles para el algoritmo y para el investigador, pero no proporcionan necesariamente una interpretación de alto nivel.

La capa LLM transforma esa telemetría en algo como:

```text
The search is experiencing severe stagnation.

Recent local-search neighborhoods have almost completely
lost their ability to improve the solution and the current
solution remains highly similar to the best-known solution,
indicating insufficient diversification.

A stronger perturbation based on related removal followed
by regret insertion is recommended.
```

Esto introduce una forma de **observabilidad semántica** sobre la dinámica del algoritmo.

---

# 3. Dos funciones distintas: observabilidad e intervención

Es importante separar conceptualmente:

## 3.1. Observabilidad

El sistema registra y analiza cómo está evolucionando la búsqueda.

$$
O_t = \phi(S_t)
$$

donde \(S_t\) representa el estado interno de la búsqueda y \(\phi\) extrae las variables relevantes.

Ejemplos:

- mejor coste;
- coste actual;
- número de iteraciones sin mejora;
- diversidad;
- similitud respecto a la mejor solución;
- balance de rutas;
- utilización de capacidad;
- rendimiento reciente de operadores;
- historial de intervenciones.

## 3.2. Intervención

Sólo cuando se cumple un evento determinado, por ejemplo:

$$
iterationsWithoutImprovement > \tau
$$

el sistema permite al LLM seleccionar una acción estratégica.

Por tanto:

```text
observability != intervention
```

Se puede registrar telemetría cada \(K\) iteraciones sin realizar ninguna llamada al LLM.

---

# 4. Arquitectura propuesta

```text
                    METAHEURISTIC
                         |
                         v
                  search iteration
                         |
                         v
                     Telemetry
                         |
                +--------+--------+
                |                 |
                v                 v
        Periodic snapshot     Event detector
                                |
                           stagnation?
                                |
                                v
                         SearchStateSummary
                                |
                                v
                               LLM
                  +-------------+-------------+
                  |             |             |
                  v             v             v
              Diagnosis      Strategy        XAI
                  |             |             |
                  +-------------+-------------+
                                |
                                v
                           Event log
                                |
                                v
                     Optional intervention
```

---

# 5. Registro temporal de la búsqueda

La evolución completa se almacenará en CSV/XLSX para permitir análisis posterior.

Se utilizarán dos tipos principales de registros.

## 5.1. Periodic snapshots

Cada \(K\) iteraciones:

```text
event_type = periodic_snapshot
```

Ejemplo:

```text
K = 250
```

o:

```text
K = 500
```

Estos snapshots **no requieren llamada al LLM**.

Se registra únicamente telemetría.

## 5.2. Intervention events

Cuando se activa una condición como:

```text
iterations_without_improvement >= STAGNATION_THRESHOLD
```

se genera:

```text
event_type = llm_intervention
```

y se consulta al modelo.

---

# 6. Esquema de datos temporal

Una fila del dataset podría contener:

| Campo | Descripción |
|---|---|
| `run_id` | Identificador de ejecución |
| `instance` | Instancia CVRP |
| `seed` | Seed |
| `iteration` | Iteración |
| `event_type` | periodic / stagnation / intervention / improvement |
| `current_cost` | Coste actual |
| `best_cost` | Mejor coste |
| `gap_bks` | Gap frente a BKS |
| `stagnation` | Iteraciones sin mejora |
| `recent_improvement_rate` | Mejora reciente |
| `diversity` | Diversidad estimada |
| `similarity_to_best` | Similitud con mejor solución |
| `route_load_mean` | Utilización media |
| `route_load_std` | Desbalance |
| `last_operator` | Último operador |
| `operator_success_*` | Rendimiento reciente |
| `llm_called` | Boolean |
| `diagnosis` | Diagnóstico LLM |
| `strategy` | Estrategia recomendada |
| `xai` | Explicación |
| `llm_tokens_input` | Tokens entrada |
| `llm_tokens_output` | Tokens salida |
| `llm_latency_ms` | Latencia |
| `improvement_after_50` | Efecto |
| `improvement_after_100` | Efecto |
| `improvement_after_250` | Efecto |

Ejemplo conceptual:

| iteration | event | best_cost | stagnation | diversity | diagnosis | strategy | Δ250 |
|---:|---|---:|---:|---:|---|---|---:|
| 1000 | periodic | 15080 | 120 | 0.42 | — | — | — |
| 2000 | periodic | 15020 | 310 | 0.31 | — | — | — |
| 2487 | intervention | 15020 | 500 | 0.12 | severe stagnation | related+regret2 | -1.4% |
| 3000 | periodic | 14810 | 40 | 0.38 | — | — | — |

---

# 7. Salida estructurada del LLM

La salida debe ser JSON validable.

Ejemplo:

```json
{
  "search_status": "severe_stagnation",

  "diagnosis": {
    "diversity": "very_low",
    "intensification": "excessive",
    "capacity_balance": "acceptable",
    "operator_exhaustion": [
      "2opt",
      "swap"
    ]
  },

  "strategy": {
    "mode": "diversification",
    "destroy": "related_removal",
    "repair": "regret_2",
    "local_search": "relocate",
    "intensity": 0.25
  },

  "xai": {
    "evidence": [
      "750 iterations without improvement",
      "solution similarity to best = 0.96",
      "2-opt recent improvement rate = 0.01",
      "swap recent improvement rate = 0.00"
    ],

    "expected_effect": "Move the search to a structurally different region while preserving useful customer relationships.",

    "rejected_alternatives": [
      {
        "strategy": "2opt",
        "reason": "Its recent improvement rate indicates that the current local basin is largely exhausted."
      }
    ],

    "explanation": "The search presents strong evidence of stagnation..."
  }
}
```

---

# 8. Por qué colocar `xai` al final del JSON

Los modelos autoregresivos generan cada token condicionado por los anteriores:

$$
P(t_1,\ldots,t_n)
=
\prod_i P(t_i | t_{<i})
$$

Por tanto, cuando el modelo ya ha generado:

```json
"destroy": "related_removal"
```

el texto generado posteriormente dentro de:

```json
"xai": ...
```

no puede modificar retroactivamente esa decisión.

Esto permite separar visualmente:

```text
DECISION
   |
   v
EXPLANATION
```

Sin embargo, existe un matiz:

> El modelo conoce desde el prompt que deberá justificar posteriormente su elección.

Por tanto, la **obligación de generar una explicación sí puede influir indirectamente en la decisión seleccionada**.

Esto puede estudiarse experimentalmente mediante una ablación:

```text
LLM-NoXAI
vs
LLM-XAI
```

---

# 9. No usar el término XAI de forma excesivamente fuerte

La explicación generada por el propio LLM debe tratarse como:

> **post-hoc decision rationale**

o:

> **LLM-generated explanation layer**

No se afirmará que representa la verdadera cadena causal interna del modelo.

La literatura sobre explicabilidad de hiperheurísticas ya estudia cómo explicar decisiones de selección de operadores tanto en momentos concretos como a lo largo del tiempo [1].

Nuestra contribución no sería inventar la explicabilidad en hiperheurísticas.

---

# 10. Novedad relativa de la arquitectura

La idea general:

```text
LLM + heuristic selection
```

no es nueva.

HeurAgenix ya utiliza un LLM para seleccionar heurísticas durante la resolución, incluyendo CVRP. Su implementación permite configurar la frecuencia de selección y documenta un valor por defecto de cinco pasos [2][3].

TRACE aprende políticas de selección de operadores a partir de **search traces**, incluyendo información temporal, historial de acciones y estado de búsqueda. En CVRP mejora GVNS sobre 84 instancias [4].

La explicabilidad de decisiones de hiperheurísticas también ha sido estudiada específicamente [1].

Por tanto, **no se reclamará prioridad absoluta**.

### Combinación que se estudiará

Nuestra arquitectura concreta combina:

$$
\boxed{
\text{event-triggered intervention}
+
\text{search trajectory telemetry}
+
\text{semantic diagnosis}
+
\text{grounded explanation}
+
\text{strategy selection}
}
$$

La aportación experimental consiste en estudiar conjuntamente estos elementos en una metaheurística CVRP.

---

# 11. Diferencia frente a trabajos cercanos

## HeurAgenix

```text
Problem state
    |
    v
LLM heuristic selection
    |
    v
execution
```

La selección se realiza periódicamente durante la resolución.

Nuestro foco:

```text
normal metaheuristic
        |
        v
search trajectory
        |
        v
stagnation event
        |
        v
semantic diagnosis
        |
        v
strategy + explanation
```

La pregunta es:

> **¿Es necesario consultar continuamente al LLM o es más eficiente reservarlo para momentos críticos de búsqueda?**

---

## TRACE

TRACE utiliza:

```text
search traces
    |
    v
offline training
    |
    v
classifier
    |
    v
operator prediction
```

Nuestro enfoque:

```text
search traces / telemetry
        |
        v
      LLM
        |
        v
diagnosis + strategy + explanation
```

No requiere entrenamiento específico del selector.

TRACE es especialmente relevante porque demuestra que:

- las trazas de búsqueda contienen información útil;
- variables temporales e historial de acciones pueden guiar operator selection;
- este enfoque puede mejorar convergencia y calidad en CVRP [4].

---

## Explainable Hyper-Heuristics

Yates, Keedwell y Kheiri estudian métodos para explicar decisiones de selección de hiperheurísticas tanto online como offline y analizar su comportamiento a través del tiempo [1].

Nuestro añadido específico será utilizar una capa LLM que convierta telemetría en:

```text
diagnóstico semántico
+
evidencia
+
recomendación
+
resultado posterior
```

---

# 12. Search trace enriquecido semánticamente

Definimos cada observación como:

$$
O_t =
[
Telemetry_t,
Diagnosis_t,
Decision_t,
Outcome_t
]
$$

La ejecución completa genera:

$$
O_1,O_2,\ldots,O_n
$$

Esto constituye un **semantic-enriched search trace**.

Ejemplo:

```text
iteration 3000
----------------
best_cost: 15320
status: healthy
diversity: medium

iteration 5000
----------------
best_cost: 15190
status: mild stagnation
diversity: decreasing

iteration 6200
----------------
best_cost: 15190
status: severe stagnation

LLM:
related removal
+
regret-2
+
25%

iteration 6450
----------------
best_cost: 14940

outcome:
successful intervention
improvement: 1.65%
```

---

# 13. Análisis temporal

Esta ampliación permite estudiar no sólo:

```text
resultado final
```

sino:

```text
cómo se llegó al resultado
```

### Variables temporales

Podremos analizar:

- evolución del best cost;
- evolución del current cost;
- diversidad;
- estancamiento;
- éxito de operadores;
- cambios de estrategia;
- intervenciones;
- efecto posterior.

---

# 14. Gráficas previstas

## 14.1. Best cost vs iteration

Con líneas verticales en intervenciones:

```text
Cost
 ^
 |\
 | \
 |  \____
 |       |  LLM
 |       +------\
 |               \__
 |                  | LLM
 |                  +-------
 +--------------------------> iteration
```

---

## 14.2. Diversity vs iteration

Permite comprobar si una intervención:

```text
destroy + repair
```

realmente incrementó diversidad.

---

## 14.3. Stagnation counter

Visualización de la acumulación y reinicio del contador.

---

## 14.4. Operator success over time

Ejemplo:

```text
2-opt success
relocate success
swap success
destroy-repair success
```

---

## 14.5. Semantic status timeline

```text
healthy
healthy
mild_stagnation
severe_stagnation
recovering
healthy
...
```

---

## 14.6. Intervention outcome

Por estrategia:

```text
related + regret2
route removal + greedy
random removal + regret2
...
```

medir:

$$
\Delta C_{50}
$$

$$
\Delta C_{100}
$$

$$
\Delta C_{250}
$$

---

# 15. Evaluar el efecto real de cada intervención

Una explicación razonable no significa que una intervención sea útil.

Por eso, después de cada decisión almacenaremos:

```text
cost_before
best_cost_before

best_cost_after_50
best_cost_after_100
best_cost_after_250
```

Y calcularemos:

$$
\Delta_{50}
=
\frac{C_{before}-C_{after50}}{C_{before}}
$$

y equivalentes para otros horizontes.

Esto permitirá clasificar una intervención como:

```text
successful
neutral
harmful
```

Ejemplo:

| Strategy | Δ50 | Δ100 | Δ250 |
|---|---:|---:|---:|
| related + regret2 | 0.4% | 1.1% | 1.4% |
| route destroy | 0.0% | 0.2% | 0.2% |
| random removal | -0.1% | 0.0% | 0.0% |

---

# 16. Métricas específicas de observabilidad/XAI

## 16.1. Grounding rate

Queremos comprobar si las explicaciones están respaldadas por telemetría.

$$
GroundingRate =
\frac{
\text{claims supported by telemetry}
}{
\text{claims evaluated}
}
$$

Ejemplo:

```text
claim:
"solution diversity is very low"

telemetry:
similarity_to_best = 0.98
```

Puede considerarse coherente bajo un criterio previamente definido.

---

## 16.2. Diagnosis consistency

Podemos definir reglas simples.

Ejemplo:

```text
if stagnation > 500
and improvement_rate < epsilon
then expected_status in {
    mild_stagnation,
    severe_stagnation
}
```

Y comprobar consistencia.

---

## 16.3. Strategy-explanation consistency

Si el modelo diagnostica:

```text
excessive intensification
```

pero recomienda:

```text
2-opt
```

podemos marcar la decisión como potencialmente inconsistente.

---

## 16.4. Intervention success rate

$$
ISR =
\frac{
\text{successful LLM interventions}
}{
\text{total LLM interventions}
}
$$

---

## 16.5. Improvement per LLM call

$$
Efficiency_{LLM}
=
\frac{
\Delta Quality
}{
N_{LLMCalls}
}
$$

Esta será una métrica particularmente importante para comparar:

```text
LLM periodic
vs
LLM stagnation
```

---

# 17. Ablación XAI

Se propone, si el tiempo lo permite:

## LLM-NoXAI

```json
{
  "destroy": "related_removal",
  "repair": "regret_2",
  "intensity": 0.20
}
```

## LLM-XAI

```json
{
  "destroy": "related_removal",
  "repair": "regret_2",
  "intensity": 0.20,
  "xai": {
    "evidence": [],
    "explanation": ""
  }
}
```

Mediremos:

- agreement entre decisiones;
- calidad de solución;
- tokens;
- latencia;
- coste;
- robustez.

Pregunta:

> **¿La obligación de explicar la decisión cambia el comportamiento del selector?**

---

# 18. Frecuencia de observación

La observabilidad no debe implicar llamadas continuas al LLM.

### Telemetría local

Cada:

```text
K = 250-500 iterations
```

se registra localmente.

Coste LLM:

```text
0
```

### Diagnóstico LLM

Dos posibilidades experimentales:

#### Periodic LLM

```text
cada K_llm iteraciones
```

#### Event-driven LLM

```text
sólo cuando stagnation >= threshold
```

Esta comparación es importante.

---

# 19. Preguntas de investigación adicionales

### RQ-O1

¿Puede una capa LLM transformar telemetría numérica de una metaheurística en diagnósticos semánticos consistentes sobre su dinámica de búsqueda?

### RQ-O2

¿Hasta qué punto las explicaciones generadas están fundamentadas en la telemetría disponible?

### RQ-O3

¿Existe relación entre el diagnóstico del LLM y el éxito posterior de la estrategia recomendada?

### RQ-O4

¿Puede una política event-driven proporcionar una relación calidad/coste superior a una política LLM periódica?

### RQ-O5

¿La incorporación de una explicación estructurada modifica significativamente las estrategias seleccionadas?

---

# 20. Hipótesis adicionales

### H-O1

Los diagnósticos del LLM serán capaces de identificar patrones claros de estancamiento cuando éstos estén explícitamente reflejados en la telemetría.

### H-O2

El análisis de trayectorias proporcionará información más útil que una fotografía aislada de la solución.

### H-O3

La política event-driven realizará muchas menos llamadas al modelo que una selección periódica manteniendo una calidad comparable.

### H-O4

La explicación estructurada proporcionará valor de auditabilidad con un overhead moderado.

---

# 21. Valor práctico

La arquitectura tiene interés más allá del benchmark académico.

En un solver convencional normalmente se observan:

```text
cost
iterations
operator weights
acceptance rate
```

Con esta capa podrían generarse eventos legibles:

```text
Search stagnated after 6,200 iterations.

Recent improvement from 2-opt and relocate is negligible.
Solution similarity to the current best is 98%.

The optimizer is likely over-intensifying around the same
local basin.

A 25% related removal followed by regret-2 insertion was
selected.

250 iterations later:
best cost improved by 1.65%.
```

Esto permite:

- auditoría;
- debugging;
- supervisión humana;
- análisis de experimentos;
- comparación de estrategias;
- explicación de comportamientos inesperados.

---

# 22. Formulación académica prudente

Una formulación adecuada sería:

> **Se propone una capa de observabilidad e intervención asistida por LLM que transforma telemetría de la trayectoria de búsqueda en diagnósticos semánticos, explicaciones fundamentadas y recomendaciones estratégicas. A diferencia de esquemas de selección continua, la intervención se activa principalmente ante eventos de estancamiento, permitiendo estudiar el compromiso entre calidad de búsqueda, interpretabilidad y coste de las consultas al modelo.**

No se afirmará:

> “Es la primera arquitectura XAI para metaheurísticas.”

Ni:

> “Es la primera aplicación de LLMs a operator selection.”

---

# 23. Aportación ampliada de la Parte II

La contribución de la segunda parte queda entonces dividida en:

### C2.1 — Stagnation-triggered heuristic control

Intervención LLM activada ante eventos de estancamiento.

### C2.2 — Search trajectory representation

Representación compacta de la evolución de la búsqueda.

### C2.3 — Semantic observability

Conversión de telemetría numérica en diagnóstico interpretable.

### C2.4 — Decision rationale

Explicación estructurada asociada a cada intervención.

### C2.5 — Temporal trace analysis

Análisis longitudinal de:

```text
state
diagnosis
decision
outcome
```

### C2.6 — Intervention efficiency

Evaluación de mejora por intervención y por llamada al LLM.

---

# 24. Dataset experimental generado

Un resultado secundario del experimento será un dataset de trazas:

```text
search_trace.csv
```

o:

```text
search_trace.xlsx
```

que contendrá:

```text
telemetry
+
LLM diagnosis
+
strategy
+
explanation
+
observed outcome
```

Esto permitirá análisis posterior con:

- Pandas;
- Excel;
- notebooks;
- estadísticas;
- visualizaciones.

---

# 25. Prioridad en el roadmap

Esta ampliación **no debe aumentar significativamente el tiempo de implementación**.

La telemetría ya es necesaria para:

```text
StagnationDetector
SearchStateSummary
AdaptiveSelector
LLMSelector
```

Por tanto, registrar esos datos en CSV/XLSX tiene un coste pequeño.

La explicación se genera dentro de la misma llamada al LLM.

### Obligatorio

```text
telemetry logging
iteration index
stagnation events
LLM decision
LLM explanation
intervention outcome
```

### Deseable

```text
periodic semantic diagnosis
XAI ablation
grounding metric
automatic consistency checks
```

### Opcional

```text
dashboard
real-time UI
human evaluation study
```

No se desarrollará una interfaz gráfica durante el sprint inicial.

---

# 26. Resumen conceptual final

La segunda integración ya no se describe únicamente como:

$$
LLM \rightarrow operator
$$

sino como:

$$
\boxed{
SearchTrajectory
\rightarrow
LLM
\rightarrow
Diagnosis
+
Explanation
+
Strategy
\rightarrow
Outcome
}
$$

y temporalmente:

$$
O_1,O_2,\ldots,O_t
$$

permitiendo estudiar:

> **qué estaba ocurriendo, qué interpretó el LLM, qué decidió hacer y qué ocurrió después.**

Esta trazabilidad es la base de la nueva capa de **observabilidad temporal e interpretabilidad de la búsqueda**.

---

# 27. Referencias específicas para esta ampliación

[1] **W. B. Yates, E. C. Keedwell, A. Kheiri.**  
“Explainable Optimisation through Online and Offline Hyper-heuristics.”  
*ACM Transactions on Evolutionary Learning and Optimization*, 5(2), Article 10, 2025.  
El trabajo desarrolla métodos para explicar decisiones de hiperheurísticas tanto en momentos concretos como a lo largo de la ejecución.  
https://doi.org/10.1145/3701236

[2] **X. Yang, L. Zhang, H. Qian, L. Song, J. Bian.**  
“HeurAgenix: Leveraging LLMs for Solving Complex Combinatorial Optimization Challenges.” 2025.  
Framework de hiperheurísticas asistidas por LLM que incluye selección dinámica y experimentos sobre CVRP.  
https://arxiv.org/abs/2506.15196

[3] **Microsoft — HeurAgenix repository.**  
La implementación documenta `llm_hh`, `random_hh` y un parámetro `selection_frequency`, cuyo valor por defecto es 5 pasos.  
https://github.com/microsoft/HeurAgenix

[4] **P. Kalatzantonakis, A. Sifaleras, N. Samaras.**  
“An offline data-driven process for learning operator selection from metaheuristic search traces.”  
*Swarm and Evolutionary Computation*, 98, 102058, 2025.  
TRACE utiliza características derivadas de trazas de búsqueda —historial de acciones, estado temporal y métricas de grafo— para aprender selección de vecindarios; TRACE-VNS mejora convergencia y calidad sobre GVNS en 84 instancias CVRP.  
https://doi.org/10.1016/j.swevo.2025.102058

---

# 28. Frase compacta para explicar esta ampliación

> **Además de utilizar el LLM como selector estratégico, se propone emplear la misma interacción como una capa de observabilidad semántica de la metaheurística. La telemetría de búsqueda se registra temporalmente y, ante eventos relevantes como el estancamiento, el modelo produce un diagnóstico, una estrategia y una explicación fundamentada. Esto permite analizar no sólo el resultado final, sino también la evolución de la búsqueda, las razones asociadas a cada intervención y su efecto posterior.**

