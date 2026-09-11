# Ampliación del Bloque 2: preferencias blandas en lenguaje natural para guiar una metaheurística CVRP

**Documento complementario a la estrategia consolidada del TFM**  
**Fecha:** 5 de septiembre de 2026

---

## 1. Idea central

La segunda parte del TFM incorpora un LLM como módulo heurístico de alto nivel dentro de una metaheurística para CVRP.

La ampliación propuesta consiste en permitir que el sistema reciba, además de la telemetría de búsqueda, una **preferencia operacional blanda expresada en lenguaje natural**.

La formulación general será:

$$
\boxed{
Strategy_t =
\pi_{LLM}
(
SearchState_t,
OperationalIntent
)
}
$$

donde:

- `SearchState_t` resume la situación actual de la búsqueda;
- `OperationalIntent` expresa prioridades blandas de negocio o del operador;
- `Strategy_t` determina cómo debe intervenir la metaheurística.

Ejemplos de instrucciones:

```text
"Preserva la planificación actual tanto como sea posible."

"Evita reasignar clientes entre conductores salvo que sea necesario."

"Aceptamos algo más de distancia si se reducen mucho los cambios."

"Prioriza el equilibrio de carga entre conductores."

"Minimiza distancia de forma agresiva aunque haya que reorganizar rutas."

"En caso de estancamiento, diversifica de forma moderada, no agresiva."
```

La idea no es sustituir restricciones matemáticas por lenguaje natural.

La separación será:

$$
\boxed{\text{Solver} \rightarrow \text{factibilidad}}
$$

$$
\boxed{\text{Metaheurística} \rightarrow \text{optimización}}
$$

$$
\boxed{\text{LLM} \rightarrow \text{interpretación contextual + guía heurística}}
$$

---

# 2. Motivación

Los optimizadores tradicionales necesitan objetivos y restricciones expresados de forma estructurada.

Sin embargo, en un entorno real pueden existir preferencias blandas difíciles de fijar de forma única o estable:

- minimizar cambios respecto a un plan ya comunicado;
- preservar asignaciones vehículo-cliente;
- reducir cambios de orden dentro de las rutas;
- equilibrar carga entre conductores;
- tolerar un pequeño aumento de distancia para mejorar estabilidad;
- favorecer cambios locales frente a reorganizaciones globales;
- priorizar robustez sobre pequeñas mejoras marginales.

Estas preferencias pueden variar entre ejecuciones.

Programar una regla específica para cada formulación natural eliminaría gran parte del valor de utilizar un LLM.

El objetivo es que el desarrollador programe una vez:

> **qué puede observar el solver**

y que el usuario exprese:

> **qué quiere priorizar**

mientras el LLM actúa como capa semántica de traducción entre ambos.

---

# 3. No es necesario programar una métrica por cada frase

El usuario NO tendrá que definir una métrica nueva cada vez que escriba una preferencia.

El solver expondrá un **catálogo fijo de métricas generales**.

Ejemplo:

## Coste

```text
total_distance
distance_vs_reference
gap_to_best
```

## Estabilidad

```text
assignment_changes
assignment_preservation
edge_similarity_to_reference
route_order_similarity
routes_modified
```

## Balance

```text
route_distance_std
workload_std
max_route_workload
min_route_workload
```

## Capacidad

```text
capacity_utilization_mean
capacity_utilization_std
max_capacity_utilization
```

## Dinámica de búsqueda

```text
iteration
iterations_without_improvement
recent_improvement_rate
diversity
similarity_to_best
```

## Operadores

```text
2opt_success_rate
relocate_success_rate
swap_success_rate
related_removal_success_rate
route_removal_success_rate
```

A partir de ese catálogo, el LLM interpreta la intención.

---

# 4. Ejemplo de interpretación automática

Entrada:

```text
"Intenta mantener la planificación actual y,
sobre todo, conserva los clientes asignados
a cada conductor."
```

El LLM puede asociar esa preferencia a:

```text
assignment_preservation     -> prioridad muy alta
assignment_changes          -> minimizar
edge_similarity             -> prioridad media
route_order_similarity      -> prioridad media
total_distance              -> prioridad secundaria
```

El usuario no ha programado ninguna de estas relaciones.

Otro ejemplo:

```text
"Hoy quiero que las rutas estén lo más equilibradas posible."
```

Puede asociarse a:

```text
workload_std
max_route_workload
min_route_workload
route_distance_std
```

Otro:

```text
"Prefiero tocar lo mínimo posible y sólo las rutas afectadas."
```

Puede traducirse a:

```text
routes_modified
assignment_changes
edge_similarity
affected_routes
destroy_intensity
```

---

# 5. Límite del enfoque

El LLM sólo puede razonar correctamente sobre información disponible.

Por ejemplo:

```text
"Evita zonas peligrosas."
```

no puede evaluarse si el sistema no dispone de:

```text
zone_risk
road_risk
restricted_areas
```

Por tanto, se distinguirán tres niveles.

## Nivel 1 — Preferencia soportada directamente

Ejemplos:

```text
preserva rutas
minimiza distancia
evita reasignaciones
equilibra carga
```

Se puede relacionar con métricas ya disponibles.

## Nivel 2 — Preferencia semántica compuesta

Ejemplo:

```text
"haz cambios conservadores"
```

No existe una única métrica, pero puede interpretarse mediante:

```text
low destroy intensity
few routes modified
high route similarity
few customer reassignments
```

## Nivel 3 — Concepto no observable

Ejemplo:

```text
"evita zonas conflictivas"
```

Si esa información no está en el sistema, debe añadirse una nueva feature externa.

El LLM no deberá inventar datos ausentes.

---

# 6. Información enviada al LLM

Cuando se produzca una intervención se enviarán cuatro grupos de información.

## 6.1. Preferencia operacional

```json
{
  "operational_intent": "Preserve the existing route organization as much as possible. Avoid moving customers between drivers unless necessary."
}
```

## 6.2. Solución de referencia

La solución previa o plan ya desplegado:

```json
{
  "reference_solution": {
    "routes": 8,
    "total_distance": 14980.2
  }
}
```

No siempre será necesario mandar todas las rutas completas.

## 6.3. Diferencias respecto a la referencia

```json
{
  "solution_metrics": {
    "total_distance": 15240.8,
    "distance_vs_reference": 0.0174,
    "assignment_changes": 5,
    "assignment_preservation": 0.93,
    "edge_similarity_to_reference": 0.89,
    "route_order_similarity": 0.91,
    "routes_modified": 2
  }
}
```

## 6.4. Estado de búsqueda

```json
{
  "search_state": {
    "iteration": 7200,
    "iterations_without_improvement": 650,
    "recent_improvement_rate": 0.0,
    "diversity": 0.13
  }
}
```

## 6.5. Historial de operadores

```json
{
  "operator_metrics": {
    "2opt": {
      "uses": 420,
      "recent_success_rate": 0.01
    },
    "relocate": {
      "uses": 380,
      "recent_success_rate": 0.03
    },
    "related_removal": {
      "uses": 40,
      "recent_success_rate": 0.12
    }
  }
}
```

---

# 7. No hace falta mandar todas las soluciones intermedias

La metaheurística puede producir miles o millones de soluciones.

No se enviarán todas al LLM.

El solver mantendrá telemetría local y, ante un evento relevante, generará un snapshot:

$$
Snapshot_t =
[
ReferenceSolution,
CurrentSolution,
SearchTrajectory,
OperationalIntent
]
$$

El LLM verá una **representación compacta de la situación relevante**.

Ejemplo temporal:

```text
iteration 1000
iteration 2000
iteration 3000
iteration 4000
iteration 5000
       |
       v
  STAGNATION
       |
       v
  Snapshot_t
       |
       v
      LLM
```

---

# 8. Fragmentos estructurales cuando sean útiles

Las métricas agregadas serán la entrada principal.

Sin embargo, cuando una decisión dependa de una ruta concreta se podrá incluir un subconjunto reducido:

```json
{
  "affected_routes": [
    {
      "route_id": 2,
      "reference": ["D", "A", "B", "C", "D"],
      "current": ["D", "A", "C", "D"],
      "issue": "customer B currently unassigned"
    }
  ]
}
```

Esto permite al LLM comprender:

> “preservar la organización”

en relación con una estructura concreta.

No se mandará todo el CVRP salvo que el tamaño lo permita y sea necesario.

---

# 9. Salida del LLM

La respuesta será estructurada y validable.

Ejemplo:

```json
{
  "objective_interpretation": {
    "primary": "route_stability",
    "secondary": "distance",
    "description": "Preserving current vehicle-customer assignments is more important than small distance improvements."
  },

  "diagnosis": {
    "search_status": "severe_stagnation",
    "diversity": "low",
    "current_objective_alignment": "good"
  },

  "strategy": {
    "mode": "localized_repair",
    "scope": "affected_routes_only",
    "destroy": "related_removal",
    "repair": "regret_2",
    "local_search": "relocate",
    "intensity": 0.10
  },

  "xai": {
    "evidence": [
      "assignment_preservation = 0.93",
      "edge_similarity_to_reference = 0.89",
      "only 2 routes are currently modified",
      "650 iterations without improvement"
    ],

    "decision_reason": "A large route destruction would conflict with the stated objective of preserving the deployed plan. The search is stagnating, but the current solution already retains most assignments, therefore a low-intensity repair restricted to affected routes is preferable."
  }
}
```

---

# 10. Preferencias blandas frente a restricciones duras

Esta distinción debe quedar explícita en el TFM.

## Restricciones duras

Ejemplos:

```text
vehicle capacity
customer must be served
valid depot
time window
forbidden edge
mandatory assignment
```

Las controla el solver.

El LLM no puede decidir ignorarlas.

## Preferencias blandas

Ejemplos:

```text
prefer fewer route changes
prefer workload balance
prefer route stability
prefer smaller perturbations
accept slightly more distance
prefer preserving assignments
```

El LLM puede utilizarlas para orientar la estrategia.

Formalmente:

$$
Feasible(S)=true
$$

continúa siendo obligatorio.

La preferencia sólo afecta a:

$$
\text{cómo explorar el conjunto de soluciones factibles}
$$

y potencialmente a qué soluciones factibles se consideran más deseables.

---

# 11. El punto más interesante: cambiar cómo busca, no sólo cómo puntúa

Una opción convencional sería traducir:

```text
"preserva las rutas"
```

a una función:

$$
F(S)=Distance(S)+\lambda Disruption(S,S_0)
$$

Eso es totalmente válido y deberá mencionarse como alternativa.

Sin embargo, nuestra hipótesis es ligeramente diferente.

Queremos estudiar si la preferencia también puede modificar:

$$
\boxed{\text{la estrategia de búsqueda}}
$$

Por ejemplo:

## Preferencia A

```text
"Minimize total distance aggressively.
Major route reorganizations are acceptable."
```

El LLM podría seleccionar:

```text
route_removal
high destroy intensity
cross-route relocate
```

## Preferencia B

```text
"Preserve the current organization.
Avoid customer reassignment."
```

Podría seleccionar:

```text
affected-routes-only
low destroy intensity
related removal
local repair
```

## Preferencia C

```text
"Prioritize workload balance between drivers."
```

Podría seleccionar:

```text
cross-route relocate
swap
load-focused neighborhoods
```

Por tanto:

$$
OperationalIntent
\rightarrow
SearchPolicy
$$

no sólo:

$$
OperationalIntent
\rightarrow
ObjectiveWeight
$$

---

# 12. Context-aware heuristic controller

La arquitectura puede describirse como:

> **Context-aware LLM heuristic controller**

porque la estrategia depende simultáneamente de:

1. situación de búsqueda;
2. estructura de la solución;
3. historial reciente;
4. preferencia operacional.

Formalmente:

$$
a_t =
\pi_{LLM}
(
\phi(S_t),
I
)
$$

donde:

- \(\phi(S_t)\) es la telemetría resumida;
- \(I\) es la intención operacional;
- \(a_t\) es la estrategia.

---

# 13. Integración con el trigger de estancamiento

Esta ampliación no reemplaza la arquitectura event-driven.

La mantiene:

```text
metaheuristic
     |
     v
normal search
     |
     v
stagnation?
     |
     +---- no ---> continue
     |
     +---- yes
             |
             v
       SearchStateSummary
             +
      OperationalIntent
             |
             v
            LLM
             |
             v
   Diagnosis + Strategy + XAI
             |
             v
        intervention
```

El LLM continúa siendo utilizado sólo cuando existe una razón para consultarlo.

Esto mantiene bajo:

- coste;
- latencia;
- número de tokens;
- dependencia de API.

---

# 14. Integración con la observabilidad temporal

Cada intervención se almacenará junto con la preferencia activa.

Ejemplo:

| iteration | intent | best cost | assignment preservation | stagnation | strategy | Δcost | Δstability |
|---:|---|---:|---:|---:|---|---:|---:|
| 3400 | preserve plan | 15230 | 0.94 | 500 | local repair | -0.4% | +0.01 |
| 6200 | preserve plan | 15140 | 0.95 | 500 | related+regret2 | -0.2% | 0.00 |
| 8900 | distance first | 14990 | 0.82 | 500 | route destroy | -1.3% | -0.09 |

Esto permite analizar:

> no sólo si mejora el coste,

sino:

> si la estrategia respeta la prioridad semántica activa.

---

# 15. Métricas para preferencias concretas

Las preferencias blandas deben tener métricas observables cuando sea posible.

## 15.1. Preservar asignaciones

$$
AssignmentPreservation =
1-
\frac{N_{reassigned}}{N_{customers}}
$$

## 15.2. Preservar estructura de rutas

$$
EdgeSimilarity =
\frac{|E(S)\cap E(S_0)|}{|E(S_0)|}
$$

## 15.3. Número de rutas alteradas

$$
RoutesChanged
$$

## 15.4. Balance

Por ejemplo:

$$
WorkloadStd
$$

o:

$$
Range_{workload}
=
max(workload)-min(workload)
$$

## 15.5. Distancia

$$
TotalDistance
$$

## 15.6. Disrupción agregada

Opcionalmente:

$$
D(S,S_0)
=
\alpha D_{assignment}
+
\beta D_{edges}
+
\gamma D_{order}
$$

Esta función será útil para evaluación aunque el usuario no tenga que definir sus pesos manualmente en cada ejecución.

---

# 16. El caso de uso de reoptimización

Un escenario especialmente atractivo es:

```text
Existe una planificación S0.
```

Posteriormente ocurre un evento:

```text
new customer
road closure
vehicle unavailable
new restriction
updated demand
```

La solución anterior puede:

- volverse infactible;
- seguir siendo factible pero subóptima;
- requerir cambios parciales.

El objetivo empresarial puede ser:

> “Repara el plan realizando el menor número posible de cambios.”

Este tipo de problema está relacionado con:

- reoptimization;
- route stability;
- disruption minimization;
- dynamic vehicle routing.

La literatura de route stability argumenta precisamente que una nueva solución de VRP puede necesitar permanecer próxima a una solución ya desplegada, aun a costa de un pequeño incremento de distancia [5].

---

# 17. Experimento principal de preferencias semánticas

Para no ampliar demasiado el alcance, se utilizarán sólo **tres preferencias principales**.

## Intent A — Distance-first

```text
Minimize total routing distance aggressively.
Major route reorganizations are acceptable if they reduce cost.
```

## Intent B — Stability-first

```text
Preserve the existing plan as much as possible.
Avoid reassigning customers between vehicles.
A small increase in distance is acceptable.
```

## Intent C — Balance-first

```text
Prioritize workload balance between drivers while keeping total distance reasonably low.
```

---

# 18. Diseño experimental especialmente limpio

La prueba más convincente consiste en mantener constante:

```text
same CVRP instance
same initial solution
same seed
same stagnation event
same search telemetry
same available operators
```

y variar únicamente:

```text
OperationalIntent
```

Entonces observamos:

$$
Strategy_A,
Strategy_B,
Strategy_C
$$

La pregunta será:

> **¿El mismo estado de búsqueda produce estrategias coherentemente diferentes cuando cambia la prioridad operacional expresada en lenguaje natural?**

---

# 19. Resultados esperables

Ejemplo conceptual:

| Intent | Distance | Assignment changes | Route similarity | Workload balance | Typical strategy |
|---|---:|---:|---:|---:|---|
| Distance-first | **mejor** | alto | bajo | medio | aggressive destroy |
| Stability-first | bueno | **muy bajo** | **alto** | medio | local repair |
| Balance-first | bueno | medio | medio | **mejor** | cross-route moves |

No se presupone que estos resultados vayan a aparecer.

La tabla representa la señal que queremos comprobar.

---

# 20. Métrica de preference alignment

Podemos construir una medida sencilla de alineación.

Por ejemplo:

$$
Alignment(I,S)
$$

donde la función depende de la intención.

### Stability-first

Puede considerar:

```text
assignment preservation
edge similarity
routes changed
```

### Distance-first

Puede priorizar:

```text
total distance
gap to BKS
```

### Balance-first

Puede priorizar:

```text
workload std
route distance std
```

No es necesario crear una métrica universal perfecta.

Se pueden evaluar por separado las dimensiones relevantes.

---

# 21. Consistencia semántica

Podemos evaluar tres niveles.

## Nivel A — Interpretation consistency

¿El LLM comprendió la preferencia?

Ejemplo:

```text
intent:
"preserve routes"
```

Debe producir algo equivalente a:

```text
priority = stability
```

## Nivel B — Strategy consistency

¿La estrategia es coherente con esa interpretación?

Ejemplo:

```text
stability-first
+
destroy_intensity = 0.60
+
global route destruction
```

sería sospechoso.

## Nivel C — Outcome alignment

¿El resultado realmente avanzó hacia la prioridad?

Por ejemplo:

```text
assignment preservation:
0.92 -> 0.96
```

o:

```text
workload std:
31 -> 18
```

---

# 22. XAI específico de preferencias

La explicación deberá incluir:

```json
"xai": {
  "objective_interpretation": "...",
  "relevant_metrics": [
    "assignment_preservation",
    "edge_similarity_to_reference"
  ],
  "tradeoff": "A 1-2% distance penalty is considered acceptable to reduce customer reassignment.",
  "decision_reason": "..."
}
```

Esto permite auditar:

1. qué entendió;
2. qué métricas utilizó;
3. qué trade-off asumió;
4. por qué escogió el operador.

---

# 23. Catálogo de métricas visible al LLM

El prompt deberá describir brevemente cada métrica.

Ejemplo:

```text
assignment_preservation:
Fraction of customers assigned to the same vehicle
as in the reference solution. Higher is more stable.

edge_similarity_to_reference:
Fraction of route edges preserved from the reference plan.

workload_std:
Standard deviation of route workload.
Lower values indicate better balance.
```

El modelo no debe tener que deducir semánticas ambiguas de nombres de variables.

---

# 24. Catálogo de estrategias visible al LLM

Igualmente:

```text
related_removal:
Removes customers that are structurally related.
Suitable for controlled diversification.

route_removal:
Removes most or all customers from one route.
Stronger structural perturbation.

relocate:
Moves a customer between positions/routes.
Useful for local modifications and balancing.

swap:
Exchanges customers between routes.
Useful for local balancing.

regret_2:
Repair method that prioritizes customers whose delayed insertion
would become expensive.
```

Esto mejora reproducibilidad y limita al LLM a un espacio seguro.

---

# 25. No permitir al LLM inventar nuevas restricciones

El LLM no tendrá autoridad para transformar:

```text
"prefer..."
```

en:

```text
"must..."
```

La salida deberá distinguir explícitamente:

```text
hard_constraints
soft_preferences
```

Las primeras proceden sólo del solver/problema.

Las segundas pueden interpretarse por lenguaje natural.

---

# 26. Comparación con alternativas clásicas

La existencia de preferencias blandas no implica que el LLM sea la única solución posible.

Una alternativa sería:

$$
NaturalLanguage
\rightarrow
manual weights
\rightarrow
multiobjective optimization
$$

Otra:

$$
NaturalLanguage
\rightarrow
LLM parser
\rightarrow
objective weights
$$

Nuestro enfoque estudia:

$$
NaturalLanguage
+
SearchTelemetry
\rightarrow
LLM
\rightarrow
SearchStrategy
$$

La diferencia es que la intención puede modificar **la política de búsqueda**, no sólo el valor de la función objetivo.

---

# 27. Relación con trabajos recientes

## LLMAP

LLMAP utiliza un LLM como parser para comprender preferencias expresadas en lenguaje natural y combinarlas con búsqueda multiobjetivo. El sistema adapta pesos de objetivos y utiliza un algoritmo de búsqueda sobre grafos [1].

**Relación:** confirma el interés de usar lenguaje natural como interfaz para preferencias de routing.

**Diferencia:** nuestro objetivo no es principalmente traducir preferencias a pesos, sino utilizar la preferencia junto con la telemetría de una metaheurística para seleccionar estrategias de búsqueda.

---

## Multi-objective e-mobility 2026

Un trabajo reciente utiliza LLMs para traducir preferencias de movilidad a prioridades lexicográficas dentro de un problema multiobjetivo [2].

**Relación:** demuestra que las prioridades semánticas pueden integrarse en optimización de transporte.

**Diferencia:** nosotros estudiamos adaptación de operator/search strategy durante una metaheurística CVRP.

---

## ChatPlanner

ChatPlanner interpreta preferencias naturales y las integra en una función objetivo para planificación de transporte público [3].

De nuevo, la principal integración es:

```text
language -> optimization preferences
```

mientras que nuestro foco es:

```text
language + search dynamics -> heuristic strategy
```

---

## LAPPI

LAPPI utiliza LLMs para convertir preferencias vagas en instancias de optimización estructuradas y permite interacción iterativa con el usuario [4].

Esto refuerza la idea de que los LLMs pueden ser una capa de interfaz entre preferencias humanas y optimizadores.

---

## HeurAgenix

HeurAgenix utiliza LLMs para seleccionar dinámicamente heurísticas según el estado del problema y evalúa CVRP [6].

**Diferencia:** no está centrado en preferencias operacionales expresadas libremente por el usuario ni en una política activada específicamente por estancamiento con observabilidad temporal y XAI.

---

## TRACE

TRACE aprende operator selection a partir de search traces, incluyendo historial de acciones, estado temporal y características del problema, y mejora GVNS sobre 84 instancias CVRP [7].

**Importancia:** demuestra que la dinámica temporal de búsqueda contiene señal suficiente para guiar operator selection.

**Diferencia:** TRACE aprende una política offline; nuestro controlador utiliza un LLM y puede condicionar la estrategia además por una intención semántica cambiante.

---

## Route stability / reoptimization

La literatura clásica de route stability formaliza el problema de obtener nuevas rutas de calidad manteniéndolas próximas a una solución ya desplegada. Sörensen propone explícitamente un enfoque biobjetivo entre coste y estabilidad [5].

Esto proporciona el fundamento matemático para preferencias del tipo:

```text
"preserva la planificación existente"
```

---

# 28. Novedad: formulación prudente

No se afirmará:

> “Somos los primeros en usar lenguaje natural para routing.”

No es cierto.

No se afirmará:

> “Somos los primeros en usar preferencias con LLM.”

Tampoco.

No se afirmará:

> “Somos los primeros en usar un LLM para seleccionar heurísticas.”

HeurAgenix ya está muy cerca de esa afirmación.

La formulación defendible será:

> **Se estudia una arquitectura en la que preferencias operacionales blandas expresadas en lenguaje natural se combinan con telemetría temporal de la búsqueda para condicionar las intervenciones de un controlador heurístico basado en LLM dentro de una metaheurística CVRP.**

La combinación estudiada es:

$$
\boxed{
NaturalLanguageIntent
+
SearchTrajectory
+
EventTriggeredControl
+
SemanticDiagnosis
+
XAI
+
OutcomeEvaluation
}
$$

---

# 29. Por qué esta ampliación aporta valor práctico

En una implementación convencional, modificar prioridades puede exigir:

- ajustar pesos;
- cambiar reglas;
- modificar thresholds;
- cambiar operadores;
- recompilar o redeployar;
- consultar a un experto en optimización.

Con esta capa se busca habilitar interacciones como:

```text
"Hoy evita tocar las rutas ya comunicadas."
```

o:

```text
"En esta ejecución quiero priorizar equilibrio."
```

sin modificar código.

El sistema seguirá teniendo límites claros, pero proporciona una interfaz operativa mucho más flexible.

---

# 30. Ejemplo empresarial completo

Situación:

```text
Una planificación ya ha sido comunicada.
Un vehículo deja de estar disponible.
```

El solver repara la factibilidad.

Preferencia:

```text
"Realiza los mínimos cambios posibles respecto
a lo ya comunicado. Mantén los clientes con
sus conductores originales cuando sea posible."
```

Telemetría:

```text
assignment_preservation = 0.91
edge_similarity = 0.88
routes_modified = 3
stagnation = 600
```

LLM:

```text
diagnosis:
search stagnating, but plan remains relatively stable

strategy:
localized related removal
regret-2
low intensity
affected routes only

xai:
global route destruction would conflict with the
stability preference
```

Resultado:

```text
assignment_preservation = 0.95
edge_similarity = 0.92
distance = +1.7% relative to minimum-distance solution
```

Este trade-off puede ser perfectamente razonable desde un punto de vista operacional.

---

# 31. Experimentos mínimos

Para evitar scope creep, esta ampliación se puede evaluar con:

```text
3 semantic intents
x
5-10 CVRP scenarios
x
3-5 seeds
```

No necesitamos cientos de prompts.

El objetivo es comprobar comportamiento, no construir un benchmark lingüístico gigante.

---

# 32. Ablación sugerida

Si existe tiempo:

## Without intent

```text
SearchTelemetry -> LLM -> Strategy
```

## With intent

```text
SearchTelemetry + OperationalIntent -> LLM -> Strategy
```

Comparamos:

- strategy diversity;
- alignment;
- final distance;
- route stability;
- balance;
- número de llamadas;
- XAI consistency.

---

# 33. Preguntas de investigación adicionales

### RQ-P1

¿Puede un LLM adaptar la estrategia de una metaheurística CVRP en función de preferencias operacionales blandas expresadas en lenguaje natural?

### RQ-P2

¿Produce el mismo estado de búsqueda estrategias significativamente diferentes cuando cambia únicamente la intención operacional?

### RQ-P3

¿Las estrategias seleccionadas son coherentes con las métricas relacionadas con la preferencia?

### RQ-P4

¿Los resultados finales reflejan realmente la preferencia expresada o únicamente la explicación textual del modelo?

### RQ-P5

¿Puede esta capa proporcionar flexibilidad sin comprometer la factibilidad, que permanece controlada por el solver?

---

# 34. Hipótesis

### H-P1

Las instrucciones semánticas producirán estrategias diferentes de forma consistente cuando expresen prioridades claramente distintas.

### H-P2

Las preferencias orientadas a estabilidad producirán perturbaciones de menor intensidad y menor número de reasignaciones.

### H-P3

Las preferencias orientadas a distancia producirán estrategias de diversificación más agresivas cuando el algoritmo se encuentre estancado.

### H-P4

La combinación de métricas explícitas + intención natural será más auditable que una decisión basada únicamente en texto libre.

---

# 35. Integración con XAI

Esta ampliación refuerza especialmente la explicación.

En cada intervención se podrá responder a:

```text
WHAT IS HAPPENING?
diagnosis

WHAT DOES THE USER WANT?
objective_interpretation

WHAT WILL THE SOLVER DO?
strategy

WHY?
xai

DID IT WORK?
outcome
```

Esto produce una traza temporal especialmente rica.

---

# 36. Registro en Excel/CSV

Cada evento podrá almacenar:

```text
run_id
instance
seed
iteration

operational_intent
intent_category

best_cost
total_distance
assignment_preservation
edge_similarity
workload_std

stagnation
diversity

llm_objective_interpretation
llm_diagnosis
llm_strategy
llm_xai

cost_after_50
cost_after_100
cost_after_250

stability_after_250
balance_after_250
```

Esto permitirá análisis temporal y comparación entre preferencias.

---

# 37. Scope y prioridad

Esta ampliación debe permanecer **ligera**.

No exige crear otro algoritmo.

La infraestructura principal ya existe para:

```text
SearchStateSummary
LLMSelector
XAI
telemetry
```

Se añaden:

```text
OperationalIntent
reference-solution metrics
preference-alignment analysis
```

### Obligatorio si se incluye

```text
3 intents
fixed metric registry
structured intent input
XAI objective interpretation
alignment metrics
```

### Deseable

```text
reference-route snippets
intent/no-intent ablation
```

### Fuera de alcance inicial

```text
automatic discovery of arbitrary new metrics
long conversational preference negotiation
fine-tuning
RL from human feedback
dynamic preference learning
full multiobjective Pareto front generation
```

---

# 38. Mensaje principal para la defensa

> **La intención no es sustituir la función objetivo o las restricciones formales por lenguaje natural. El solver sigue siendo responsable de la factibilidad y de las métricas cuantitativas. El LLM actúa como una capa semántica que interpreta preferencias blandas y las utiliza, junto con el estado temporal de la búsqueda, para adaptar la estrategia heurística.**

---

# 39. Formulación compacta de la contribución

> **Se explora una interfaz de guía heurística en lenguaje natural para metaheurísticas CVRP, donde el operador expresa preferencias operacionales blandas sin programar reglas específicas. El LLM interpreta dichas preferencias sobre un catálogo fijo de métricas del solver y las combina con la telemetría de búsqueda para seleccionar intervenciones estratégicas explicables, manteniendo las restricciones duras bajo control determinista.**

---

# 40. Arquitectura global del Bloque 2

```text
                  HUMAN / ORGANIZATION
                          |
                          v
                Operational Intent
                  natural language
                          |
                          |
                  +-------+-------+
                  |               |
                  v               v
             Reference       Search
              Solution       Telemetry
                  |               |
                  +-------+-------+
                          |
                          v
                 SearchStateSummary
                          |
                          v
                         LLM
              +-----------+-----------+
              |           |           |
              v           v           v
          Diagnosis   Strategy       XAI
                          |
                          v
                    Metaheuristic
                          |
                          v
                       Outcome
                          |
                          v
                 Temporal Trace / Excel
```

---

# 41. Encaje con el TFM completo

## Bloque 1

```text
LLM -> h(s)
```

El LLM aporta conocimiento heurístico sobre estados.

## Bloque 2 inicial

```text
SearchTelemetry -> LLM -> Strategy
```

El LLM aporta conocimiento heurístico sobre la dinámica de búsqueda.

## Bloque 2 ampliado

```text
SearchTelemetry
+
OperationalIntent
        |
        v
       LLM
        |
        v
Context-aware Strategy
```

El LLM incorpora además contexto humano/organizacional.

Por tanto, existe una evolución clara:

$$
\boxed{
State-level guidance
\rightarrow
Search-level guidance
\rightarrow
Context-aware search guidance
}
$$

---

# 42. Referencias relevantes

[1] **L. Yuan, D.-J. Han, C. Brinton, S. Brunswicker.**  
“LLMAP: LLM-Assisted Multi-Objective Route Planning with User Preferences.”  
*Findings of EMNLP 2025*.  
Utiliza un LLM como parser de preferencias naturales y las integra con búsqueda multiobjetivo.  
https://aclanthology.org/2025.findings-emnlp.416/  
DOI: 10.18653/v1/2025.findings-emnlp.416

[2] **Large language model-assisted multi-objective optimization for an integrated multimodal e-mobility platform.**  
*Transportation Research Interdisciplinary Perspectives*, Vol. 37, 2026, 101948.  
Los LLMs traducen preferencias de movilidad en prioridades lexicográficas de optimización.  
https://doi.org/10.1016/j.trip.2026.101948

[3] **T. Yang, C. Xue, J. Chen.**  
“ChatPlanner: A Large Language Model Framework for Personalized Public Transit Routing.” 2026.  
Extrae e interpreta preferencias naturales para integrarlas en la función objetivo de un planificador de transporte.  
https://arxiv.org/abs/2606.15315

[4] **S. Kuroki, M. Nakagawa, S. Yoshida, Y. Koyama, T. Kozuno.**  
“LAPPI: Interactive Optimization With LLM-Assisted Preference-Based Problem Instantiation.”  
*IEEE Access*, 2026.  
Utiliza LLMs para convertir preferencias vagas en problemas de optimización estructurados dentro de un bucle interactivo.  
https://omron-sinicx.github.io/lappi/

[5] **K. Sörensen.**  
“Route stability in vehicle routing decisions: a bi-objective approach using metaheuristics.”  
*Central European Journal of Operations Research*, 14(2), 193–207, 2006.  
Formaliza el trade-off entre minimizar coste de ruta y mantener una nueva solución próxima a un plan ya utilizado.  
https://doi.org/10.1007/s10100-006-0168-3

[6] **X. Yang, L. Zhang, H. Qian, L. Song, J. Bian.**  
“HeurAgenix: Leveraging LLMs for Solving Complex Combinatorial Optimization Challenges.” 2025.  
Hiperheurística LLM que selecciona dinámicamente heurísticas según el estado del problema e incluye CVRP.  
https://arxiv.org/abs/2506.15196

[7] **P. Kalatzantonakis, A. Sifaleras, N. Samaras.**  
“An offline data-driven process for learning operator selection from metaheuristic search traces.”  
*Swarm and Evolutionary Computation*, 98, 102058, 2025.  
TRACE aprende operator selection a partir de temporal state, action history y otras características de search traces; TRACE-VNS se evalúa sobre 84 instancias CVRP.  
https://doi.org/10.1016/j.swevo.2025.102058

[8] **X. Xiu, C. Shen, Y. Zhu, W. Liu.**  
“Vehicle Routing Problem Meets Large Language Models: An Overview and Perspectives.” 2026.  
Survey reciente que clasifica el papel de los LLMs en VRP como modeladores, diseñadores y coordinadores, incluyendo traducción de requisitos naturales a estructuras de optimización.  
https://arxiv.org/abs/2607.00604

[9] **Sustainable Transportation Decision-Making Enabled by Specialized Large Language Models: A Supervised Fine-Tuning Framework for Route Planning.**  
*Sustainability*, 2026, 18(10), 4683.  
Defiende separar la comprensión de lenguaje natural de la optimización exacta: el LLM estructura solicitudes y delega la resolución en herramientas deterministas para TSP/CVRP/VRPTW.  
https://doi.org/10.3390/su18104683

---

# 43. Resumen ejecutivo

> **La ampliación introduce preferencias operacionales blandas en lenguaje natural como una entrada adicional al controlador heurístico LLM. El solver expone un catálogo fijo de métricas —coste, estabilidad, balance, capacidad y dinámica de búsqueda— y el modelo interpreta instrucciones como “preserva las rutas actuales” o “prioriza equilibrio” sin exigir que el usuario programe nuevas reglas. La preferencia se combina con la telemetría temporal de la búsqueda para escoger una estrategia de intervención, producir una explicación auditable y evaluar posteriormente si la solución obtenida se alineó realmente con la prioridad expresada. Las restricciones duras permanecen bajo control determinista del solver.**
