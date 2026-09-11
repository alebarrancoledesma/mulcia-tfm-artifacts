# Ampliación del Bloque 1: XAI ligero para heurísticas LLM en planificación clásica

**Documento complementario al planteamiento consolidado del TFM**  
**Fecha:** 5 de septiembre de 2026

---

## 1. Objetivo

La primera parte del TFM utiliza como referencia el enfoque de Corrêa, Pereira y Seipp (NeurIPS 2025), donde un LLM genera funciones heurísticas dependientes del dominio en forma de código Python y éstas son utilizadas para guiar Greedy Best-First Search (GBFS) [1].

Se propone añadir una capa de **interpretabilidad ligera** a esta generación:

$$
\boxed{
LLM \rightarrow h(s) + explanation
}
$$

La finalidad no es convertir el Bloque 1 en un estudio completo de XAI, sino aprovechar prácticamente sin coste adicional la propia generación del LLM para obtener información sobre:

- qué variables afirma utilizar;
- cuál es la intuición de la heurística;
- qué situaciones espera manejar bien;
- qué situaciones espera manejar mal.

Posteriormente se contrastará esa explicación con:

1. el código realmente generado;
2. los resultados obtenidos en los stress tests.

---

# 2. Motivación

Corrêa et al. muestran que los LLMs pueden generar funciones heurísticas Python capaces de guiar eficazmente un planificador clásico y competir con heurísticas de planificación consolidadas [1].

Sin embargo, una heurística generada automáticamente puede resultar difícil de interpretar únicamente leyendo:

```python
def h(state):
    ...
```

La propuesta del TFM exige analizar aspectos como:

- interpretabilidad;
- robustez;
- generalización;
- capacidad de razonar sobre estados y costes.

Por tanto, resulta útil pedir al modelo que acompañe cada heurística con una explicación estructurada y breve.

Esta información no afecta al planner: el solver sólo ejecutará el código de la heurística.

---

# 3. Salida propuesta

En lugar de solicitar únicamente código Python, la generación podrá producir una estructura similar a:

```json
{
  "heuristic_code": "...",

  "xai": {
    "features_used": [
      "remaining_packages",
      "vehicle_locations",
      "package_destinations",
      "capacity",
      "graph_distance"
    ],

    "intuition": "The heuristic estimates the remaining transportation effort by combining package delivery progress with vehicle-to-package and package-to-destination distances.",

    "expected_strengths": [
      "instances where shortest-path distance is informative",
      "moderate interaction between packages",
      "sparse transport graphs"
    ],

    "expected_weaknesses": [
      "high coupling between vehicle assignments",
      "tight vehicle capacity",
      "situations where packages should be jointly routed"
    ]
  }
}
```

Alternativamente, si la infraestructura de Corrêa espera exclusivamente código, pueden hacerse dos pasos:

```text
LLM generation
    |
    +---- heuristic.py
    |
    +---- heuristic_metadata.json
```

Esto evita modificar la interfaz del planner.

---

# 4. XAI ligero, no cadena de razonamiento

El campo `xai` se tratará como:

> **LLM-generated post-hoc rationale / explanation metadata**

No se afirmará que representa la verdadera cadena interna de razonamiento del modelo.

La explicación sirve para:

- describir la intención aparente del programa;
- facilitar auditoría;
- identificar las variables que el modelo considera relevantes;
- generar hipótesis contrastables en los experimentos.

No se almacenará ni requerirá una cadena de pensamiento detallada.

---

# 5. Campos mínimos

Para mantener el coste bajo, el `xai` tendrá únicamente cuatro campos obligatorios.

## 5.1. `features_used`

Lista explícita de conceptos utilizados por la heurística.

Ejemplo:

```json
"features_used": [
  "remaining_packages",
  "shortest_path_distance",
  "vehicle_capacity"
]
```

---

## 5.2. `intuition`

Explicación muy breve de la idea principal.

Objetivo:

```text
50-100 palabras
```

No es necesario generar 300 palabras.

---

## 5.3. `expected_strengths`

Dos o tres situaciones donde el modelo espera que la heurística sea informativa.

---

## 5.4. `expected_weaknesses`

Dos o tres situaciones donde el modelo considera que la heurística puede degradarse.

Este último campo es especialmente útil porque se podrá contrastar directamente con el stress test.

---

# 6. Primera comprobación: explicación vs código

Para cada heurística seleccionada se revisará si existe correspondencia entre:

$$
\text{XAI declarado}
$$

y:

$$
\text{código generado}
$$

Ejemplos.

### Caso coherente

El XAI afirma:

```text
features_used:
- vehicle_capacity
```

y el código utiliza realmente información de capacidad.

Resultado:

```text
CONSISTENT
```

### Caso inconsistente

El XAI afirma:

```text
"The heuristic explicitly accounts for vehicle capacity."
```

pero el código no consulta ninguna variable relacionada con capacidad.

Resultado:

```text
INCONSISTENT
```

---

# 7. Métrica sencilla de consistencia

Se puede definir una métrica cualitativa o semicuantitativa:

$$
CodeExplanationConsistency =
\frac{
\text{features declaradas realmente utilizadas}
}{
\text{features declaradas}
}
$$

Ejemplo:

```text
features declaradas:
distance
capacity
remaining_packages
vehicle_assignment

features detectadas en código:
distance
remaining_packages
vehicle_assignment

consistency = 3 / 4 = 0.75
```

No es necesario construir un analizador estático sofisticado.

Para las pocas heurísticas finalmente analizadas puede realizarse:

- revisión manual;
- búsqueda de variables/funciones;
- una pequeña clasificación automática.

---

# 8. Segunda comprobación: explicación vs comportamiento experimental

Ésta es la parte más interesante.

Supongamos que el LLM indica:

```json
"expected_weaknesses": [
  "tight vehicle capacity"
]
```

Posteriormente, en el stress test de presión de capacidad, observamos:

```text
CP 0.40 -> 1,200 expansions
CP 0.60 -> 2,500 expansions
CP 0.80 -> 12,000 expansions
CP 0.95 -> timeout
```

Podemos discutir:

> La debilidad anticipada por el modelo es consistente con el deterioro observado experimentalmente.

O puede ocurrir lo contrario:

```text
El modelo predijo una debilidad que no aparece.
```

Eso también es interesante.

---

# 9. Relación directa con los stress tests

La explicación se diseñará para que haga referencia a las mismas dimensiones que vamos a estudiar.

## ST1 — Escala

Campos relacionados:

```text
number_of_packages
number_of_locations
vehicles
```

Pregunta:

> ¿La heurística anticipa problemas al aumentar el tamaño?

---

## ST2 — Presión de capacidad

Campos relacionados:

```text
capacity
package_vehicle_interaction
assignment
```

Pregunta:

> ¿Las debilidades declaradas relacionadas con capacidad aparecen realmente?

---

## ST3 — Topología

Campos relacionados:

```text
graph_distance
shortest_path
connectivity
bottlenecks
```

Pregunta:

> ¿La heurística depende fuertemente de shortest paths y se degrada en topologías concretas?

---

# 10. Registro de cada heurística

Cada candidata generada podrá guardarse como:

```text
heuristics/
    H001/
        heuristic.py
        metadata.json

    H002/
        heuristic.py
        metadata.json
```

Ejemplo de `metadata.json`:

```json
{
  "id": "H001",
  "model": "model_name",
  "generation_seed": 12,

  "xai": {
    "features_used": [
      "remaining_packages",
      "graph_distance",
      "vehicle_capacity"
    ],

    "intuition": "...",

    "expected_strengths": [
      "..."
    ],

    "expected_weaknesses": [
      "..."
    ]
  },

  "training_results": {
    "coverage": 0.90,
    "expanded_states": 14320
  }
}
```

---

# 11. No todas las heurísticas necesitan análisis XAI exhaustivo

Para ahorrar tiempo:

### Todas las candidatas

Guardar:

```text
features_used
intuition
expected_strengths
expected_weaknesses
```

### Sólo heurísticas relevantes

Analizar en profundidad:

- mejor heurística LLM;
- una heurística intermedia;
- una heurística claramente mala;
- heurística clásica de referencia cuando sea comparable.

Por ejemplo:

```text
H_best
H_median
H_worst
```

Esto permite estudiar si las explicaciones cambian según la calidad real.

---

# 12. Preguntas experimentales pequeñas

Esta ampliación puede responder tres preguntas secundarias.

### RQ-X1

¿Las explicaciones generadas por el LLM describen correctamente las características realmente utilizadas por el código heurístico?

### RQ-X2

¿Las fortalezas y debilidades anticipadas por el modelo se corresponden con el comportamiento observado en los stress tests?

### RQ-X3

¿Las heurísticas de mayor rendimiento presentan explicaciones o estructuras conceptuales distintas de las heurísticas de bajo rendimiento?

Estas preguntas serán secundarias y no condicionarán el éxito del TFM.

---

# 13. Comparación con la Parte II

Esta capa permite crear una simetría conceptual entre ambos bloques.

## Bloque 1 — interpretabilidad de la heurística

```text
LLM
 |
 v
heuristic code
 |
 +---- features
 +---- intuition
 +---- strengths
 +---- weaknesses
```

Es principalmente:

$$
\boxed{\text{static / algorithm-level interpretability}}
$$

---

## Bloque 2 — observabilidad de la búsqueda

```text
search telemetry
      |
      v
     LLM
      |
      +---- diagnosis
      +---- strategy
      +---- evidence
      +---- XAI
      |
      v
intervention outcome
```

Es:

$$
\boxed{\text{dynamic / search-level observability}}
$$

---

# 14. Hilo conductor

La interpretabilidad evoluciona junto con la granularidad del LLM.

### State-level

La pregunta es:

> ¿Qué información utiliza la función heurística y cuál es su intuición?

### Search-level

La pregunta pasa a ser:

> ¿Qué está ocurriendo durante la búsqueda, por qué se recomienda intervenir y qué resultado produce esa intervención?

Por tanto:

$$
\boxed{
\text{heuristic explanation}
\rightarrow
\text{search diagnosis}
}
$$

Esta transición refuerza la coherencia entre ambos bloques.

---

# 15. Coste de implementación

Esta ampliación debe mantenerse deliberadamente barata.

### Coste esperado

Muy bajo.

Sólo requiere:

1. modificar el prompt;
2. guardar un JSON junto al código;
3. revisar unas pocas heurísticas;
4. cruzar fortalezas/debilidades con resultados experimentales.

No requiere:

- otro modelo;
- otro planner;
- nuevas llamadas durante la búsqueda;
- entrenamiento;
- dashboard;
- framework XAI específico.

---

# 16. Prompt orientativo

Una versión sencilla podría incluir:

```text
Generate the Python heuristic function required by the planner.

After producing the heuristic, also provide a short structured explanation containing:

1. features_used:
   Which aspects of the planning state are explicitly used by the heuristic.

2. intuition:
   A concise explanation of why the heuristic should help rank states.

3. expected_strengths:
   Conditions under which the heuristic is expected to perform well.

4. expected_weaknesses:
   Conditions under which the heuristic may provide misleading estimates.

Keep the explanation concise and grounded in the generated code.
```

Si la infraestructura necesita código puro:

```text
Prompt A -> generate heuristic.py
Prompt B -> inspect heuristic.py and generate metadata.json
```

El segundo enfoque puede ser incluso más robusto porque la explicación se produce observando el código final.

---

# 17. Variante recomendada: explicar DESPUÉS de generar

Aunque puede hacerse en una sola respuesta, metodológicamente resulta atractivo separar:

```text
GENERATION
LLM -> heuristic.py
```

y posteriormente:

```text
EXPLANATION
LLM -> inspect heuristic.py -> metadata.json
```

Ventajas:

- la explicación se basa en el código que realmente se ejecutará;
- no condiciona necesariamente la generación inicial;
- permite utilizar el mismo proceso con heurísticas ya generadas;
- facilita detectar inconsistencias.

Con el poco tiempo disponible, cualquiera de los dos métodos es válido.

La opción de dos pasos se utilizará sólo si resulta fácil automatizarla.

---

# 18. Resultado esperado en el documento

Ejemplo de tabla:

| Heuristic | Distance | Capacity | Package interaction | Predicted weakness | Observed |
|---|---:|---:|---:|---|---|
| H1 | ✓ | ✓ | baja | tight capacity | ✓ |
| H2 | ✓ | ✗ | baja | bottlenecks | ✓ |
| H3 | ✗ | ✓ | media | large instances | ✗ |

Y un pequeño análisis:

> H1 identificó explícitamente la presión de capacidad como una posible limitación. En los experimentos, su número de expansiones aumentó de forma pronunciada al aproximarse la carga total a la capacidad agregada disponible.

Esto proporciona interpretabilidad sin ampliar significativamente el alcance.

---

# 19. Qué NO debemos reclamar

No diremos:

> “Hemos desarrollado un nuevo método XAI.”

No.

Tampoco:

> “La explicación representa fielmente el razonamiento interno del LLM.”

No.

Ni:

> “Una explicación correcta demuestra que la heurística es correcta.”

No.

La formulación será:

> **Se añade metadata explicativa generada por el LLM para facilitar la interpretación y auditoría de las funciones heurísticas, y se contrasta dicha explicación con el código y con el comportamiento experimental.**

---

# 20. Contribución secundaria

La formulación prudente sería:

> **Como complemento al análisis de rendimiento, se incorpora una capa ligera de interpretabilidad en la que cada heurística generada se acompaña de metadata estructurada sobre las variables utilizadas, su intuición y sus fortalezas y debilidades esperadas. Esta información se contrasta posteriormente con el código generado y con los resultados obtenidos en los stress tests.**

---

# 21. Relación con el estado del arte

Corrêa et al. 2025 muestran que los LLMs pueden generar directamente código Python para heurísticas dependientes del dominio y seleccionar las candidatas más fuertes mediante evaluación empírica [1].

Tuisov, Vernik y Shleyfman también estudian heurísticas generadas mediante LLM y discuten explícitamente el compromiso entre heurísticas específicas de dominio, eficiencia computacional y explicabilidad [2].

El trabajo posterior de Corrêa et al. de 2026 utiliza propiedades formalmente verificables y contraejemplos para proporcionar información mucho más precisa sobre por qué una heurística candidata falla y guiar su reparación [3].

Nuestro planteamiento es deliberadamente mucho más sencillo:

```text
generation
+
lightweight explanation metadata
+
experimental consistency check
```

No pretende competir con verificación formal ni síntesis guiada por propiedades.

---

# 22. Papel dentro del TFM completo

La arquitectura global queda:

```text
                      LLM AS HEURISTIC MODULE
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v

           BLOCK 1                        BLOCK 2

      Classical Planning           CVRP Metaheuristic

        LLM -> h(s)                 Search telemetry
             |                            |
             v                            v
         heuristic                        LLM
             |                            |
             +-> light XAI                +-> diagnosis
                                          +-> strategy
                                          +-> XAI
                                          |
                                          v
                                       outcome
```

Interpretabilidad:

```text
Block 1:
What does the heuristic use?

Block 2:
What is happening in the search,
why intervene,
and what happened afterwards?
```

---

# 23. Prioridad

### Obligatorio

```text
features_used
intuition
expected_strengths
expected_weaknesses
```

### Deseable

```text
code/XAI consistency
stress-test/XAI comparison
```

### Sólo si sobra tiempo

```text
automatic static analysis
formal grounding score
large XAI ablation
```

---

# 24. Resumen ejecutivo

> **En el Bloque 1 se añadirá una capa XAI ligera prácticamente gratuita: cada heurística LLM se acompañará de metadata estructurada sobre las características que utiliza, la intuición de diseño y sus fortalezas y debilidades esperadas. Estas explicaciones no se tratarán como cadena de razonamiento verdadera, sino como rationales auditables que podrán contrastarse tanto con el código generado como con el comportamiento real observado durante los stress tests. Esto aporta interpretabilidad al enfoque state-level sin aumentar significativamente la complejidad del TFM.**

---

# 25. Referencias

[1] **A. B. Corrêa, A. G. Pereira, J. Seipp.**  
“Classical Planning with LLM-Generated Heuristics: Challenging the State of the Art with Python Code.”  
*Advances in Neural Information Processing Systems 38 (NeurIPS 2025)*.  
El trabajo genera varias funciones heurísticas dependientes del dominio en Python, las evalúa mediante GBFS y selecciona las mejores para tareas OOD.  
https://proceedings.neurips.cc/paper_files/paper/2025/hash/3bf4b55960aaa23553cd2a6bdc6e1b57-Abstract-Conference.html  
Preprint: https://arxiv.org/abs/2503.18809

[2] **A. Tuisov, Y. Vernik, A. Shleyfman.**  
“LLM-Generated Heuristics for AI Planning: Do We Even Need Domain-Independence Anymore?” 2025.  
El trabajo explora heurísticas específicas del dominio generadas mediante LLM y discute eficiencia y explicabilidad frente a heurísticas tradicionales.  
https://arxiv.org/abs/2501.18784

[3] **A. B. Corrêa, A. G. Pereira, J. Seipp.**  
“Property-Guided LLM Program Synthesis for Planning.” 2026.  
Utiliza propiedades verificables y contraejemplos concretos para detectar cómo falla una heurística candidata y guiar su reparación.  
https://arxiv.org/abs/2605.16142

[4] **Repositorio oficial de Corrêa et al.**  
Código del framework `llm-generated-heuristics`, con soporte para generación de heurísticas y benchmarks de planificación.  
https://github.com/abcorrea/llm-generated-heuristics
