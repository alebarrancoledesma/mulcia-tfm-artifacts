# Estrategia consolidada del TFM
## Planificación Híbrida: LLMs como módulos heurísticos en planificación clásica y metaheurísticas para CVRP

**Estado:** estrategia de trabajo consolidada  
**Fecha de consolidación:** 5 de septiembre de 2026  
**Objetivo temporal:** obtener un trabajo experimental sólido en aproximadamente una semana, priorizando un núcleo defendible y evitando *scope creep*.

---

## 1. Idea central del trabajo

La tesis se articula alrededor de una única idea:

> **Estudiar el uso de Large Language Models como módulos heurísticos que guían un proceso de búsqueda, sin delegar en el LLM la resolución completa del problema.**

Esta idea se estudia en **dos niveles de integración**:

1. **Heurística a nivel de estado (*state-level*)** en planificación clásica.
2. **Heurística estratégica a nivel de búsqueda (*search-level*)** en una metaheurística para CVRP.

La formulación resumida del trabajo será:

> **Partimos de un enfoque SOTA reciente de LLM como heurística de estado en planificación clásica, analizamos su comportamiento bajo condiciones de routing más exigentes y estudiamos una segunda integración, de mayor nivel, donde el LLM actúa como módulo heurístico estratégico ante estancamiento en CVRP.**

La segunda parte no se presenta como un trabajo separado ni como “GRASP/ALNS porque sí”. Se presenta como una **generalización del mismo paradigma de guía heurística**, aplicada a un método especializado en routing.

---

## 2. Encaje con la propuesta oficial

La propuesta oficial plantea:

- LLMs como **sistemas heurísticos**.
- Planificación clásica.
- VRP y problemas afines.
- Razonamiento sobre estados, acciones y costes.
- Comparación con heurísticas clásicas y enfoques híbridos.
- Generalización, robustez, coste computacional e interpretabilidad.
- Nuevas arquitecturas híbridas para optimización de rutas.

Nuestra estrategia cubre estos puntos de la siguiente forma:

| Propuesta | Estrategia del TFM |
|---|---|
| LLM como sistema heurístico | Parte I: genera `h(s)`. Parte II: selecciona estrategia de búsqueda. |
| Planificación clásica | Reproducción y stress test del paradigma de Corrêa et al. |
| Estados, acciones y costes | Análisis del estado PDDL y, si resulta viable, escenarios sensibles a costes/pesos. |
| VRP y problemas afines | `Transport` como dominio de planificación relacionado con routing + CVRP explícito en Parte II. |
| Heurísticas clásicas | `hFF` y un conjunto pequeño de heurísticas clásicas fuertes, preferiblemente mediante Fast Downward. |
| Enfoques híbridos | Planner + LLM y metaheurística + LLM. |
| Generalización y robustez | Stress tests de tamaño/estructura y múltiples ejecuciones/seeds. |
| Coste computacional | Tiempo, expansiones, llamadas LLM y mejora por llamada. |
| Interpretabilidad | Código de `h(s)` y explicación/decisión estructurada del selector estratégico. |
| Arquitecturas híbridas | Comparación de integración *state-level* y *search-level*. |

**Punto importante:** la Parte II sigue siendo una aplicación del LLM como **módulo heurístico**, concretamente como una **hiperheurística o política heurística de alto nivel**.

---

# PARTE I — PLANIFICACIÓN CLÁSICA

## 3. Punto de partida: Corrêa et al. 2025

Corrêa, Pereira y Seipp proponen generar mediante un LLM funciones heurísticas dependientes del dominio en forma de código Python. Generan varias candidatas, las prueban sobre tareas de entrenamiento con Greedy Best-First Search (GBFS) y seleccionan las más fuertes. El trabajo demuestra un rendimiento competitivo frente a heurísticas clásicas y métodos aprendidos, incluyendo generalización a tareas no vistas [1].

El repositorio oficial proporciona:

- Pyperplan integrado.
- Generación de heurísticas con LLM.
- `GBFS`.
- `hFF` y `blind`.
- Benchmarks IPC 2023.
- El dominio `transport`.
- Soporte actual para distintas APIs/modelos [2].

Por tanto, **no se reimplementará el sistema de Corrêa desde cero**.

### 3.1. Qué representa esta parte

Formalmente:

$$
LLM \longrightarrow h(s)
$$

y después:

$$
GBFS = \arg\min_s h(s)
$$

El LLM **no genera el plan durante la búsqueda**. Genera una función que intenta identificar qué estados parecen más prometedores.

La validez del plan continúa dependiendo del modelo simbólico y del planificador: acciones, precondiciones, efectos y condición objetivo.

### 3.2. Qué NO reclamamos como aportación

No reclamaremos como novedad:

- generar heurísticas Python con LLM;
- aplicarlas a `Transport`;
- seleccionar varias heurísticas y probar generalización OOD;
- comparar de forma básica `hLLM` frente a `hFF`.

Todo eso está ya cubierto en gran medida por Corrêa et al. [1].

La reproducción servirá como:

1. validación de la infraestructura;
2. punto de partida;
3. escenario de referencia para nuestros experimentos posteriores.

---

## 4. Nuestra aportación experimental en la Parte I: stress test orientado a routing

En lugar de reproducir toda la batería de Corrêa, someteremos el paradigma a una batería **pequeña y dirigida** de escenarios logísticos más exigentes.

La pregunta será:

> **¿Cómo se comporta una heurística generada por LLM cuando aumenta no sólo el tamaño, sino también la dificultad estructural del problema de transporte?**

No intentaremos repetir ocho dominios, numerosos LLMs ni todas las ablaciones del paper.

### 4.1. Stress tests mínimos

Se priorizan **tres dimensiones**.

#### ST1 — Escala

Variar de forma progresiva:

- número de localizaciones;
- número de paquetes/clientes;
- relación paquetes/vehículo.

Ejemplo orientativo:

```text
small   -> 10 paquetes
medium  -> 20 paquetes
large   -> 40 paquetes
xlarge  -> 60+ paquetes
```

Los valores finales dependerán de cuándo aparezcan timeouts.

#### ST2 — Presión de capacidad

Crear instancias donde la capacidad pase de holgada a muy restrictiva.

Podemos definir una métrica agregada tipo:

$$
CP = \frac{\text{carga total}}{\text{capacidad total disponible}}
$$

y generar niveles aproximados:

```text
CP ≈ 0.40
CP ≈ 0.60
CP ≈ 0.80
CP ≈ 0.95
```

El objetivo no es demostrar una propiedad matemática exacta de `CP`, sino construir escenarios comparables donde la coordinación de capacidad sea progresivamente más importante.

#### ST3 — Estructura/topología

Comparar redes con estructuras distintas:

- densas;
- dispersas;
- agrupadas por clusters;
- con cuellos de botella.

Esto es especialmente relevante porque las heurísticas de transporte pueden explotar información de conectividad y caminos más cortos.

### 4.2. Extensión opcional: costes/pesos

Si puede implementarse **sin reescribir el planner**, se añadirá un pequeño experimento sensible al coste:

```text
A -> B : coste 3
A -> C : coste 40
B -> C : coste 5
```

La finalidad sería estudiar el paso desde un problema donde las acciones son esencialmente homogéneas hacia un escenario donde la calidad de la ruta depende de costes heterogéneos.

**No es un requisito del TFM.**

La razón para mantenerlo como opcional es que ya existe investigación reciente sobre heurísticas LLM para planificación óptima, incluyendo heurísticas admisibles mediante pattern databases y saturated cost partitioning [4]. Por tanto, nuestro valor no depende de reclamar “LLM + costes” como novedad.

---

## 5. Baselines de planificación clásica

No debemos limitar el análisis a `blind` y `hFF`.

Si la integración es rápida, utilizaremos Fast Downward para incorporar un subconjunto pequeño de heurísticas clásicas consolidadas. Fast Downward proporciona, entre otras, FF, additive, causal graph, context-enhanced additive, landmarks y LM-Cut, con soporte de costes en numerosas configuraciones [16].

### Baselines objetivo

Mínimo:

```text
hFF
hLLM
```

Preferible:

```text
FF
Causal Graph
Additive o CEA
hLLM
```

No necesitamos diez heurísticas. Dos o tres baselines fuertes son suficientes para evitar una comparación de juguete.

### Métricas

- `solved / coverage`
- estados expandidos;
- tiempo;
- longitud del plan;
- timeout;
- si se introduce coste: coste del plan.

Si resulta barato, en instancias pequeñas se podrá analizar la relación entre `hLLM(s)` y una distancia real/óptima `h*(s)`, pero este análisis se considera secundario.

---

## 6. Rol del estado del arte 2026 en planificación

No intentaremos reproducir toda la evolución posterior del campo.

Dos referencias deberán aparecer en el estado del arte:

### Property-Guided LLM Program Synthesis for Planning

Corrêa et al. 2026 utilizan propiedades formalmente verificables y contraejemplos para guiar la síntesis de programas heurísticos, reduciendo el número de generaciones y el coste de evaluación [3].

### LLM-Evolved Pattern Generators for Optimal Classical Planning

Phung et al. 2026 diseñan mediante LLM estructuras que inducen heurísticas admisibles para A*, orientándose a planificación óptima [4].

Estos trabajos demuestran que la investigación *state-level* ya es sofisticada.

**Consecuencia estratégica:** no intentaremos competir en una semana con esa línea. La utilizaremos como estado del arte y concentraremos la contribución diferencial en la Parte II.

---

# PARTE II — CVRP + METAHEURÍSTICA

## 7. Motivación

El CVRP es NP-hard y las aplicaciones reales incorporan gran escala y múltiples restricciones. Revisiones de VRP muestran el uso extensivo de heurísticas y metaheurísticas para obtener soluciones de alta calidad en tiempos prácticos [13][14].

Esta segunda parte no afirma:

> “La planificación clásica es mala.”

La motivación es:

> **Para CVRP de mayor escala resulta natural estudiar un paradigma especializado que opere directamente sobre rutas y explote operadores específicos del dominio.**

Por ejemplo:

```text
2-opt
relocate
swap
destroy
repair
regret insertion
related removal
```

En lugar de trabajar con acciones elementales `drive`, `pick`, `drop`, la metaheurística trabaja directamente con cambios estructurales sobre soluciones de routing.

---

## 8. Idea principal de la Parte II

Durante la mayoría de la ejecución, la metaheurística funciona convencionalmente.

Sólo cuando se detecta **estancamiento** se consulta al LLM.

```text
Metaheurística
      |
      v
búsqueda normal
      |
      +---- mejora ----> continuar
      |
      +---- estancamiento
                |
                v
        Search State Summary
                |
                v
               LLM
                |
                v
       estrategia de escape
                |
                v
          continuar búsqueda
```

Formalmente:

$$
\phi(S_t) \rightarrow LLM \rightarrow a_t
$$

donde:

- \(S_t\) es el estado/trayectoria de búsqueda;
- \(\phi\) genera un resumen compacto;
- \(a_t\) es una estrategia heurística permitida.

Esta integración es de **grano grueso (*coarse-grained*)** y **event-driven**.

---

## 9. Qué recibe el LLM

No recibirá la instancia completa ni cientos de rutas salvo que sea estrictamente necesario.

Recibirá un resumen estructurado como:

```json
{
  "iteration": 12000,
  "iterations_without_improvement": 750,
  "current_cost": 15320.4,
  "best_cost": 15191.8,
  "recent_improvement_rate": 0.0,
  "solution_similarity_to_best": 0.96,
  "route_load_mean": 0.82,
  "route_load_std": 0.17,
  "operator_stats": {
    "2opt": {"uses": 420, "improvement_rate": 0.01},
    "relocate": {"uses": 380, "improvement_rate": 0.03},
    "swap": {"uses": 350, "improvement_rate": 0.00},
    "related_removal": {"uses": 30, "improvement_rate": 0.10}
  },
  "previous_interventions": [
    {
      "strategy": "related_removal+regret2",
      "improvement": 0.014
    }
  ]
}
```

El objetivo es que el LLM razone sobre **la dinámica de la búsqueda**, no únicamente sobre la descripción estática del CVRP.

---

## 10. Qué puede decidir el LLM

El espacio de decisión será **cerrado y validado**.

Ejemplo:

### Destroy / Shaker

```text
random_removal
related_removal
route_removal
random_relocate
```

### Repair

```text
greedy_insertion
regret_2
```

### Local search

```text
2opt
relocate
swap
```

### Intensidad

```text
0.10
0.20
0.30
```

Output esperado:

```json
{
  "mode": "diversification",
  "destroy": "related_removal",
  "repair": "regret_2",
  "local_search": "relocate",
  "intensity": 0.20,
  "reason": "The current neighborhoods show low recent success and solution diversity is very low."
}
```

El LLM **no podrá generar acciones arbitrarias ni ejecutar código nuevo** en el MVP.

---

# 11. Metaheurística base

Para reducir riesgo:

### Opción recomendada

**ALNS-lite**, porque la selección `destroy + repair` encaja directamente con nuestra pregunta experimental y existe abundante literatura sobre selección adaptativa de operadores en VRP [13].

### Excepción práctica

Si ya disponemos inmediatamente de un GRASP/VNS operativo y legalmente reutilizable, podemos utilizarlo manteniendo la misma abstracción:

```python
class StrategySelector:
    def select(search_state):
        ...
```

El TFM no depende de que el nombre sea “ALNS” o “GRASP”.

Depende de que exista:

1. una búsqueda metaheurística base;
2. varios operadores/estrategias;
3. detección de estancamiento;
4. una política intercambiable de selección.

---

# 12. Baselines de la Parte II

La comparación principal será:

```text
Random
Rule-based
Adaptive
LLM periodic          [opcional pero muy útil]
LLM stagnation        [método estudiado]
```

### Random

Selecciona aleatoriamente una estrategia.

### Rule-based

Por ejemplo:

```text
if stagnation:
    route_removal + regret_2
```

### Adaptive

Selección basada en recompensa histórica, roulette/UCB o mecanismo equivalente.

La literatura ya utiliza selección adaptativa y aprendizaje para elegir operadores en ALNS/CVRP [12].

### LLM periodic

El LLM selecciona una heurística/estrategia cada `K` pasos independientemente del estancamiento.

Será especialmente interesante porque sirve de aproximación conceptual a enfoques de selección online continua.

### LLM stagnation

Sólo consulta al LLM al activarse el detector de estancamiento.

---

# 13. Pregunta de investigación diferencial

No podemos reclamar:

> “Somos los primeros en usar un LLM para seleccionar operadores.”

Eso sería incorrecto.

HeurAgenix ya propone un framework LLM-hyper-heuristic que genera heurísticas y las selecciona dinámicamente según el estado del problema, incluyendo CVRP [5]. Su implementación ofrece una frecuencia configurable de selección; el valor por defecto documentado es cinco pasos [6].

LLMOA también utiliza un LLM como componente de alto nivel para seleccionar heurísticas de bajo nivel, aunque no está centrado específicamente en CVRP [11].

### Nuestra pregunta será más específica

> **¿Puede un LLM actuar eficazmente como mecanismo de intervención heurística activado por estancamiento, utilizando información compacta sobre la trayectoria de búsqueda para seleccionar estrategias de recuperación en CVRP?**

Y una segunda pregunta muy relevante:

> **¿Puede obtener una calidad comparable a una selección LLM periódica utilizando muchas menos consultas al modelo?**

Esto introduce una dimensión práctica clara:

$$
\text{quality gain per LLM call}
$$

---

# 14. Relación con trabajos recientes de LLM + metaheurísticas

## HeurAgenix

HeurAgenix es el antecedente más cercano. Genera/evoluciona heurísticas y durante la resolución selecciona dinámicamente una de ellas según el estado [5].

**Diferencia de nuestro enfoque:** no pretendemos controlar continuamente la búsqueda; el LLM interviene sólo ante un evento de estancamiento y recibe principalmente información de **search trajectory**.

## VRPAgent

VRPAgent utiliza LLMs para **diseñar operadores específicos para VRP** y los refina mediante búsqueda genética; prueba CVRP, VRPTW y prize-collecting VRP [7].

**Diferencia:** nuestro LLM no diseña operadores en el MVP; selecciona online estrategias preexistentes durante una ejecución concreta.

## G-LNS

G-LNS utiliza LLMs y evolución para co-diseñar pares destroy/repair de LNS y evalúa TSP/CVRP [8].

**Diferencia:** es automatic heuristic design; nuestro foco es intervención online basada en el estado de búsqueda.

## Full-Component ALNS Evolution

Yu et al. 2026 descomponen ALNS en siete módulos —destroy, repair, operator selection, weight update, initial solution, acceptance y destroy rate— y utilizan LLMs para evolucionar esos componentes [9].

**Diferencia:** diseñan/evolucionan el algoritmo. Nosotros usamos un algoritmo convencional y el LLM interviene durante la ejecución.

## TRACE

TRACE aprende políticas de selección desde trazas de metaheurísticas. En CVRP, TRACE-VNS utiliza características de la dinámica de búsqueda para guiar la selección y muestra mejoras sobre GVNS en 84 instancias [10].

**Importancia para nosotros:** valida que las características de la trayectoria de búsqueda contienen información útil para operator selection.

**Diferencia:** TRACE entrena clasificadores offline; nosotros queremos evaluar un LLM sin entrenamiento específico sobre el problema.

## Q-learning / adaptive operator selection

La selección de pares destroy-repair mediante Q-learning, UCB, softmax, epsilon-greedy, Thompson Sampling y mecanismos adaptativos ya está siendo estudiada en CVRP [12].

**Consecuencia:** `Adaptive` es una baseline obligatoria o casi obligatoria. Ganar sólo a `Random` sería una evidencia débil.

---

# 15. Hipótesis del TFM

## H1 — Planificación clásica

Las heurísticas LLM mantendrán un rendimiento competitivo bajo determinados niveles de dificultad, pero su comportamiento podrá degradarse de forma distinta a las heurísticas clásicas cuando cambie la estructura logística del problema.

No asumimos previamente que el LLM vaya a fallar.

## H2 — Granularidad

La forma adecuada de utilizar el LLM puede depender de la granularidad de la búsqueda:

$$
\text{state-level} \quad vs \quad \text{search-level}
$$

## H3 — Intervención escasa

El LLM puede ser especialmente útil en decisiones estratégicas infrecuentes y difíciles, sin necesidad de participar continuamente en todas las iteraciones de búsqueda.

## H4 — Coste

Una política activada por estancamiento puede alcanzar una relación calidad/coste superior a una política LLM periódica:

$$
\frac{\Delta \text{quality}}{\#LLMCalls}
$$

---

# 16. Preguntas de investigación

### RQ1

¿Cómo se comportan las heurísticas generadas por LLM frente a heurísticas clásicas cuando aumenta la escala y dificultad estructural de problemas de transporte?

### RQ2

¿Qué factores —tamaño, presión de capacidad, topología— afectan más a la robustez de la heurística LLM?

### RQ3

¿Cómo cambia el papel del LLM cuando se pasa de una heurística de estado en un planificador generalista a una heurística estratégica dentro de una búsqueda especializada para CVRP?

### RQ4

¿Puede un LLM activado únicamente ante estancamiento seleccionar estrategias de intensificación/diversificación eficaces?

### RQ5

¿Cómo se compara frente a selección aleatoria, reglas fijas y mecanismos adaptativos convencionales?

### RQ6

¿Cuál es el coste adicional del LLM en términos de tiempo, número de consultas y, si procede, coste monetario por ejecución?

---

# 17. Métricas

## Parte I

- cobertura;
- estados expandidos;
- tiempo;
- longitud del plan;
- timeouts;
- opcionalmente coste del plan.

## Parte II

Métrica principal:

$$
Gap(\%) =
100 \cdot \frac{C_{solution}-C_{BKS}}{C_{BKS}}
$$

Además:

- mejor coste;
- tiempo hasta mejor solución;
- iteraciones hasta mejor solución;
- convergencia;
- número de eventos de estancamiento;
- número de intervenciones LLM;
- porcentaje de intervenciones que producen mejora;
- mejora media después de una intervención;
- coste temporal de las llamadas;
- **mejora por llamada LLM**.

Cada método metaheurístico debe ejecutarse con varias seeds.

Objetivo mínimo:

```text
5 seeds
```

Deseable si el tiempo lo permite:

```text
10 seeds
```

---

# 18. Qué consideraremos un resultado positivo

No necesitamos demostrar:

$$
LLM > todos
$$

Posibles resultados publicables/defendibles dentro de un TFM:

### Caso A

```text
LLM-Stagnation > Adaptive
```

Resultado fuerte.

### Caso B

```text
LLM-Stagnation ≈ Adaptive
```

pero con pocas intervenciones y sin entrenamiento específico.

También interesante.

### Caso C

```text
LLM-Periodic ≈ LLM-Stagnation
```

pero `LLM-Stagnation` utiliza muchas menos consultas.

Resultado muy interesante por eficiencia.

### Caso D

```text
Adaptive > LLM
```

También válido: demostraría que el razonamiento LLM no justifica su overhead frente a mecanismos adaptativos especializados.

**El TFM no depende de que la hipótesis sea confirmada.**

---

# 19. Arquitectura de software

Por razones de licencia y posible reutilización profesional, se mantendrán **dos repositorios independientes**.

## Repo A — planificación clásica

```text
llm-classical-planning/
```

Basado en Corrêa et al.

El repositorio oficial utiliza licencia GPL-3.0 [2].

Contendrá:

```text
Corrêa/Pyperplan
benchmarks
stress tests
scripts de experimentación
resultados Parte I
```

Se mantendrá atribución clara y se citará el trabajo original.

## Repo B — metaheurística

```text
llm-cvrp-metaheuristic/
```

Código independiente.

No importará ni copiará código del Repo A.

Estructura aproximada:

```text
src/
  cvrp/
  construction/
  local_search/
  destroy/
  repair/
  search/
  stagnation/
  selectors/
    random_selector.py
    rule_selector.py
    adaptive_selector.py
    llm_periodic_selector.py
    llm_stagnation_selector.py

experiments/
results/
analysis/
```

Dependencias del Repo B: priorizar MIT/BSD/Apache u otras licencias permisivas si existe intención de reutilización privada.

---

# 20. Roadmap intensivo de 7 días

## Día 1 — Reproducción

Objetivo:

```text
Corrêa + Transport funcionando
```

Checklist:

- clonar repositorio;
- `uv sync`;
- ejecutar `Transport + hFF`;
- ejecutar `Transport + blind`;
- generar una heurística LLM;
- ejecutar `Transport + hLLM`;
- guardar una primera tabla.

**No tocar todavía metaheurísticas.**

---

## Día 2 — Benchmark y stress test

- Automatizar ejecuciones.
- Generar CSV.
- Preparar stress test de escala.
- Preparar presión de capacidad.
- Preparar topologías si no exige demasiada modificación.
- Integrar 1-2 baselines de Fast Downward si es rápido.

Resultado esperado:

```text
results_planning.csv
```

---

## Día 3 — Ejecutar Parte I y congelarla

Ejecutar experimentos.

Producir:

- coverage;
- expansiones;
- tiempo;
- gráficas por nivel de dificultad.

Opcional:

- pequeño experimento de costes;
- análisis `h(s)`.

Al final del día:

> **feature freeze de Parte I.**

No intentar superar el paper de Corrêa.

---

## Día 4 — Metaheurística base

Objetivo:

```text
CVRP base funciona sin LLM
```

Preferencia:

- ALNS-lite si se implementa desde cero;
- GRASP/VNS existente si ya está listo.

Operadores mínimos:

```text
2-opt
relocate

random removal
related removal
route removal

greedy insertion
regret-2
```

Implementar:

```text
RandomSelector
RuleSelector
AdaptiveSelector
```

---

## Día 5 — Stagnation + LLM

Implementar:

```text
StagnationDetector
SearchStateSummary
LLMPeriodicSelector
LLMStagnationSelector
```

Output LLM mediante JSON estructurado.

Añadir `cooldown` después de una intervención para evitar llamadas continuas.

---

## Día 6 — Experimentos CVRP

Benchmark inicial:

```text
10-20 instancias
small / medium / large
5 seeds
```

Comparar:

```text
Random
Adaptive
LLM periodic
LLM stagnation
```

Si falta tiempo, eliminar `Rule` o `Periodic`, pero **mantener Adaptive**.

---

## Día 7 — Resultados y escritura

Congelar código.

Generar:

```text
planning_coverage
planning_expansions
planning_runtime

cvrp_gap
cvrp_convergence
llm_calls
improvement_per_call
intervention_success
```

Escribir resultados, discusión y conclusiones.

---

# 21. Orden de recorte si falta tiempo

Eliminar en este orden:

1. múltiples modelos LLM;
2. cost-aware planning;
3. análisis `h(s)` vs `h*(s)`;
4. tercer stress test;
5. baseline `Rule`;
6. `LLM periodic` si técnicamente complica la ejecución;
7. número de instancias/seeds.

**No eliminar:**

- Corrêa + Transport funcionando;
- al menos un stress test;
- baseline clásica;
- metaheurística CVRP base;
- Adaptive vs LLM-Stagnation;
- métricas y resultados.

---

# 22. Claims que SÍ y que NO debemos hacer

## NO

> “Proponemos el primer LLM para CVRP.”

Falso.

> “Proponemos el primer LLM que selecciona operadores.”

Falso o al menos no defendible.

> “Nadie ha aplicado LLMs a metaheurísticas.”

Falso.

> “La planificación clásica sólo sirve para problemas pequeños.”

Demasiado absoluto.

> “Las metaheurísticas son siempre mejores.”

Falso.

## SÍ

> Partimos de un método reciente y competitivo de síntesis de heurísticas LLM para planificación clásica y lo sometemos a escenarios de routing estructuralmente más exigentes.

> Investigamos una segunda granularidad de integración del LLM como módulo heurístico dentro de una búsqueda especializada para CVRP.

> Estudiamos específicamente una política de intervención **event-driven**, activada ante estancamiento y basada en información de la trayectoria de búsqueda.

> Comparamos esta política con métodos adaptativos convencionales y analizamos no sólo calidad de solución, sino también coste y utilidad por llamada al LLM.

> No se reclama prioridad histórica absoluta; se estudia experimentalmente una variante concreta y pragmática de integración.

---

# 23. Contribuciones previstas

Una formulación prudente y defendible:

### C1. Caracterización experimental

Stress test orientado a routing de heurísticas LLM generadas para planificación clásica, analizando sensibilidad a escala y dificultad estructural.

### C2. Arquitectura search-level

Diseño de una integración donde un LLM actúa como módulo heurístico estratégico dentro de una metaheurística de CVRP.

### C3. Trigger por estancamiento

Uso de eventos de estancamiento para restringir las consultas LLM a momentos potencialmente relevantes.

### C4. Representación compacta de la trayectoria

Diseño de `SearchStateSummary` con información sobre progreso, diversidad, estructura de rutas y rendimiento de operadores.

### C5. Evaluación frente a baselines

Comparación contra selección Random/Rule/Adaptive y, si el tiempo permite, LLM periódica.

### C6. Evaluación de eficiencia

Medición explícita de:

$$
\text{quality gain per LLM call}
$$

además de calidad final y tiempo.

---

# 24. Estructura provisional del documento

```text
1. Introducción
2. Fundamentos
   2.1 Classical Planning
   2.2 Heuristic Search
   2.3 Vehicle Routing Problem
   2.4 Metaheuristics / ALNS / GRASP
   2.5 Large Language Models

3. Estado del arte
   3.1 LLMs for Planning
   3.2 LLM-generated Planning Heuristics
   3.3 LLM-based Automatic Heuristic Design
   3.4 Hyper-heuristics and Operator Selection
   3.5 LLMs for Vehicle Routing

4. Heurísticas LLM en planificación clásica
   4.1 Corrêa et al.
   4.2 Reproducción
   4.3 Diseño del stress test
   4.4 Baselines
   4.5 Resultados

5. Integración estratégica del LLM en CVRP
   5.1 Motivación
   5.2 Metaheurística base
   5.3 Detección de estancamiento
   5.4 Search State Summary
   5.5 Selectores
   5.6 Configuración experimental

6. Resultados CVRP
   6.1 Calidad
   6.2 Convergencia
   6.3 Robustez
   6.4 Coste LLM
   6.5 Análisis de intervenciones

7. Discusión conjunta
   7.1 State-level vs Search-level
   7.2 Escalabilidad
   7.3 Interpretabilidad
   7.4 Limitaciones

8. Conclusiones y trabajo futuro
```

---

# 25. Frase de defensa ante los tutores

> **El trabajo parte de un paradigma SOTA reciente en el que un LLM genera funciones heurísticas para guiar un planificador clásico. En una primera fase analizamos su robustez bajo escenarios de routing más exigentes. Posteriormente estudiamos cómo trasladar el mismo concepto de LLM como módulo heurístico a un paradigma especializado para CVRP: en lugar de evaluar estados individuales, el modelo interviene a nivel estratégico únicamente cuando la búsqueda se estanca, seleccionando mecanismos de intensificación o diversificación. De este modo se comparan dos granularidades de integración del conocimiento heurístico generado por LLM dentro de procesos de búsqueda.**

---

# 26. Decisión final de alcance

## Obligatorio

```text
Corrêa + Transport
        ↓
stress test pequeño
        ↓
baselines clásicas

CVRP
        ↓
metaheurística
        ↓
stagnation
        ↓
Adaptive vs LLM
```

## Deseable

```text
LLM periodic
más stress tests
costes/pesos
más seeds
```

## Fuera de alcance

```text
fine-tuning
reinforcement learning propio
MCTS
generación dinámica de operadores
evolución de código
time windows complejas
multi-agent
reimplementar un planner
reproducir el SOTA 2026 completo
```

---

# 27. Bibliografía y antecedentes principales

[1] **A. B. Corrêa, A. G. Pereira, J. Seipp.** “Classical Planning with LLM-Generated Heuristics: Challenging the State of the Art with Python Code.” *NeurIPS 2025*.  
https://proceedings.neurips.cc/paper_files/paper/2025/hash/3bf4b55960aaa23553cd2a6bdc6e1b57-Abstract-Conference.html  
Preprint: https://arxiv.org/abs/2503.18809

[2] **Corrêa et al. — LLM-Generated Heuristics, repositorio oficial.** GPL-3.0. Incluye Pyperplan, dominio `transport`, generación de heurísticas, `hFF`, `blind` y benchmarks IPC 2023.  
https://github.com/abcorrea/llm-generated-heuristics

[3] **A. B. Corrêa, A. G. Pereira, J. Seipp.** “Property-Guided LLM Program Synthesis for Planning.” 2026.  
https://arxiv.org/abs/2605.16142

[4] **W. Phung, D. Drexler, A. Lequen, J. Seipp.** “LLM-Evolved Pattern Generators for Optimal Classical Planning.” 2026.  
https://arxiv.org/abs/2606.02438

[5] **X. Yang, L. Zhang, H. Qian, L. Song, J. Bian.** “HeurAgenix: Leveraging LLMs for Solving Complex Combinatorial Optimization Challenges.” 2025.  
https://arxiv.org/abs/2506.15196

[6] **Microsoft — HeurAgenix, repositorio oficial.** Documenta `llm_hh`, `random_hh` y `selection_frequency` (por defecto 5 pasos).  
https://github.com/microsoft/HeurAgenix

[7] **A. Hottung et al.** “VRPAgent: LLM-Driven Discovery of Heuristic Operators for Vehicle Routing Problems.” 2025.  
https://arxiv.org/abs/2510.07073

[8] **B. Zhao, H. Wang, L. Zeng.** “G-LNS: Generative Large Neighborhood Search for LLM-Based Automatic Heuristic Design.” 2026.  
https://arxiv.org/abs/2602.08253

[9] **S. Yu, T. Chen, L. Liu.** “Large Language Model-Driven Full-Component Evolution of Adaptive Large Neighborhood Search.” 2026.  
https://arxiv.org/abs/2603.06996

[10] **“An offline data-driven process for learning operator selection from metaheuristic search traces.”** *Swarm and Evolutionary Computation*, 2025. TRACE/TRACE-VNS.  
https://doi.org/10.1016/j.swevo.2025.102058

[11] **R. Zhong, A. G. Hussien, J. Yu, M. Munetomo.** “LLMOA: A novel large language model assisted hyper-heuristic optimization algorithm.” *Advanced Engineering Informatics*, 2025, 64:103042.  
https://doi.org/10.1016/j.aei.2024.103042

[12] **H. Boualamia, I. Hafidi, A. Metrane.** “Adaptive Operator Selection in ALNS Using Q-Learning: A Comparative Study of Softmax, UCB, epsilon-Greedy and QTS Strategies for CVRP.” 2026.  
https://doi.org/10.19139/soic-2310-5070-3956

[13] **S. Voigt.** “A review and ranking of operators in adaptive large neighborhood search for vehicle routing problems.” *European Journal of Operational Research*, 2025, 322(2):357–375. Revisión de 211 artículos; identifica 57 operadores de removal y 42 de insertion.  
https://doi.org/10.1016/j.ejor.2024.05.033

[14] **“A taxonomic review of metaheuristic algorithms for solving the vehicle routing problem and its variants.”** *Computers & Industrial Engineering*, 2020, 140:106242.  
https://doi.org/10.1016/j.cie.2019.106242

[15] **X. Xiu, C. Shen, Y. Zhu, W. Liu.** “Vehicle Routing Problem Meets Large Language Models: An Overview and Perspectives.” 2026. Revisión reciente que organiza el uso de LLMs en VRP como modeladores, diseñadores y coordinadores.  
https://arxiv.org/abs/2607.00604

[16] **Fast Downward — Evaluator / Heuristic documentation.** Documentación de FF, additive, causal graph, CEA, landmarks, LM-Cut y otras heurísticas.  
https://www.fast-downward.org/latest/documentation/search/Evaluator/

---

## 28. Resumen ejecutivo de una línea

> **Reproducir Corrêa, poner a prueba las heurísticas LLM en routing más exigente y, como contribución principal, estudiar si un LLM puede utilizarse de forma más práctica y esporádica como hiperheurística activada por estancamiento en un solver metaheurístico de CVRP.**

