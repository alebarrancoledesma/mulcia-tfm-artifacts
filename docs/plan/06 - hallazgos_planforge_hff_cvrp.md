# Hallazgos técnicos — Heurísticas externas en PlanForge para CVRP

**Fecha:** 2026-09-06  
**Contexto:** TFM — uso de LLMs para generar funciones heurísticas en planificación clásica, aplicado a CVRP sobre PlanForge.

---

## 1. Objetivo de esta nota

Conservar los hallazgos técnicos obtenidos al inspeccionar:

1. La implementación oficial de `FfHeuristic` de PlanForge.
2. La API pública usada por `EvaluationState`, `AbstractNumericTask` y el registro de estados.
3. Un *dump* real de la tarea CVRP `P-n16-k8` después de que PlanForge traduzca el PDDL a su representación numérica/SAS+ interna.

El objetivo no es documentar FF en detalle, sino fijar qué información puede usar una heurística externa, cómo debe accederse a ella y qué arquitectura conviene usar para las heurísticas generadas por LLM.

---

# 2. Conclusión principal

La integración técnica necesaria para una heurística CVRP externa está disponible.

Una heurística registrada mediante el mecanismo de `ExternalHeuristic` puede:

- recibir el estado actual mediante `EvaluationState`;
- leer el estado proposicional;
- leer el estado numérico;
- inspeccionar la tarea y sus variables;
- inspeccionar operadores grounded;
- inspeccionar sus precondiciones y efectos;
- obtener costes de operadores;
- precomputar información estática una sola vez;
- calcular `h(s)` repetidamente sin modificar el núcleo de PlanForge.

La arquitectura recomendada es:

```text
PDDL CVRP
   ↓
PlanForge translator
   ↓
AbstractNumericTask
   ↓
CvrpTaskInfo::from_task(...)        ← una vez, al construir la heurística
   ↓
┌─────────────────────────────────────────────┐
│ información estática precomputada           │
│ clientes, IDs, distancias, mappings, etc.   │
└─────────────────────────────────────────────┘
   ↓
cada estado s
   ↓
CvrpStateView                        ← lectura barata del estado actual
   ↓
heurística generada por LLM
   ↓
h(s)
```

La parte de adaptación PlanForge → CVRP **no debería ser generada de nuevo por cada LLM**. Debe ser infraestructura fija del experimento.

---

# 3. Lo que confirma `FfHeuristic`

## 3.1. Trabajo pesado en construcción, evaluación barata por estado

`FfHeuristic::new(task)` compila previamente toda la información estática que necesita:

- universo de hechos;
- operadores;
- axiomas;
- achievers;
- consumers;
- costes;
- mappings;
- buffers reutilizables.

Esto confirma que la forma correcta de diseñar nuestra heurística es:

```text
constructor/build
    → descubrir estructura de la tarea
    → precomputar mappings
    → precomputar datos estáticos
    → reservar buffers

compute_heuristic
    → leer únicamente el estado actual
    → ejecutar cálculo de h(s)
```

No conviene recorrer nombres, operadores o construir matrices dentro de `compute_heuristic`, porque puede ejecutarse millones de veces.

## 3.2. Lectura eficiente de todo el estado numérico

FF obtiene los valores numéricos actuales mediante:

```rust
eval_state
    .state_registry()
    .view(eval_state.state())
    .fill_numeric(raw)
```

Por tanto, una heurística externa puede obtener un `Vec<f64>` con la representación numérica completa del estado actual.

Uso recomendado:

```rust
let registry = eval_state.state_registry();
let state = eval_state.state();

registry
    .view(state)
    .fill_numeric(&mut scratch.numeric)?;
```

Después se accede por IDs previamente descubiertos:

```rust
let load = scratch.numeric[self.load_var_id];
let vehicles = scratch.numeric[self.vehicles_var_id];
```

La heurística no debe buscar `"load"` por nombre en cada evaluación. El ID se descubre una vez en el constructor.

## 3.3. Lectura eficiente de todo el estado proposicional

FF usa:

```rust
let live_state = eval_state.state();
let registry = eval_state.state_registry();

live_state.fill_state(registry, &mut scratch.prop_state_values);
```

Esto permite obtener de una vez el valor actual de cada variable proposicional.

Por tanto, si durante la construcción hemos guardado:

```rust
visited_var_id[customer]
loc_var_id[location]
```

durante `compute_heuristic()` basta con consultar:

```rust
let visited_value = scratch.prop_state_values[var_id];
```

Esto es preferible a realizar múltiples accesos individuales al `StateRegistry`.

## 3.4. `ExplicitFact::is_hold(...)` sigue siendo válido

FF también demuestra que puede comprobarse directamente un hecho:

```rust
ExplicitFact::propositional(var, value)
    .is_hold(registry.view(live_state))
```

Es una API válida, aunque para recorrer muchos clientes el acceso por lote con `fill_state` es más apropiado.

## 3.5. Buffers reutilizables con `RefCell`

FF mantiene:

```rust
scratch: RefCell<ScratchBuffers>
```

y reutiliza memoria entre evaluaciones.

Esto es importante porque una heurística puede ser evaluada cientos de miles o millones de veces.

Para nuestros candidatos no es obligatorio optimizar desde el primer prototipo, pero la arquitectura final debería evitar allocations repetidas si usa:

- vectores de clientes pendientes;
- arrays temporales;
- estados proposicionales;
- estados numéricos;
- buffers para MST / nearest-neighbour / etc.

Patrón recomendado:

```rust
struct CvrpHeuristic {
    info: CvrpTaskInfo,
    scratch: RefCell<CvrpScratch>,
}
```

## 3.6. Costes reales de operadores

FF calcula durante su construcción:

```rust
metric_operator_cost_from_initial_values(task, op)
```

y almacena el resultado.

Esto es especialmente importante en nuestro CVRP: evita tener que reconstruir necesariamente `travel-cost` a partir de los nombres internos de variables numéricas.

Los operadores grounded conservan nombres semánticos claros, por ejemplo:

```text
visit c10 c11
visit d1 c7
return-to-depot c10
visit-via-depot c10 c12
```

Por tanto, podemos construir una matriz de costes usando **nombres de operadores + coste métrico del operador**.

## 3.7. Efectos numéricos de operadores

FF accede a:

```rust
op.assignment_effects()
```

y para cada efecto numérico están disponibles al menos:

```rust
assign.affected_var_id()
assign.var_id()
assign.operation()
assign.conditions()
```

Esto abre una vía robusta para extraer semántica del CVRP sin depender de strings complejos generados por el traductor.

Ejemplo conceptual:

```text
operador: visit c4 c7
efecto:   load += <numeric_var_x>
```

Si `<numeric_var_x>` es una constante con valor igual a `demand(c7)`, la demanda puede extraerse estructuralmente del propio operador.

**Pendiente:** confirmar una vez el patrón exacto de `assignment_effects()` para los operadores CVRP del dominio de Kuroiwa. La API existe; falta fijar el mapping concreto.

## 3.8. Goal y dead ends

FF empieza con:

```rust
if eval_state.is_goal() {
    return Ok(0.0);
}
```

Por tanto esta condición debe mantenerse en las heurísticas generadas.

FF puede devolver:

```rust
EvaluationError::DeadEnd { reliable: false }
```

cuando su relajación no alcanza el goal.

Para las primeras heurísticas LLM se recomienda **no declarar dead ends**, salvo que exista una prueba lógica clara. Una heurística experimental debe preferir devolver un valor finito y no negativo antes que eliminar incorrectamente un estado válido.

## 3.9. Preferred operators / helpful actions

El trait `Heuristic` soporta además la selección de operadores preferidos.

FF guarda `helpful actions` y expone:

```rust
copy_preferred_operator_ids(...)
```

Esto podría utilizarse en una extensión posterior:

```text
LLM → h(s)
```

o:

```text
LLM → h(s) + preferred operators
```

No debe mezclarse con el primer experimento. Para Block 1, primero se evaluará la generación de `h(s)`.

---

# 4. Qué revela el dump real de `P-n16-k8`

El dump elimina varias dudas y corrige una suposición previa importante.

## 4.1. Los nombres de las variables proposicionales NO son semánticos

PlanForge muestra:

```text
PROP #15: name='var0'
PROP #16: name='var1'
...
```

Por tanto, **no debemos interpretar `variable.name()` para localizar `loc` o `visited`**.

La semántica está en los nombres de los hechos:

```text
value 0: 'Atom loc(c10)'
value 1: 'NegatedAtom loc(c10)'

value 0: 'Atom visited(c10)'
value 1: 'NegatedAtom visited(c10)'
```

La API adecuada para descubrir la semántica proposicional es:

```rust
task.get_fact_name(&ExplicitFact::propositional(var_id, value))
```

Conclusión:

```text
variable.name()      → no fiable semánticamente: "var18", "var25", ...
get_fact_name(...)   → sí conserva: "Atom visited(c7)", "Atom loc(c7)", ...
```

## 4.2. `loc(...)` se conserva perfectamente

El dump contiene:

```text
Atom loc(c2)
Atom loc(c3)
...
Atom loc(c16)
Atom loc(d1)
```

Esto permite descubrir automáticamente todos los nodos y asociar:

```text
location_name → propositional var ID
```

Además, en el estado inicial:

```text
loc(d1) = true
loc(customer) = false
```

por lo que el depósito puede identificarse de forma consistente en esta representación.

No deben hardcodearse IDs como:

```rust
let depot_var = 45;
```

porque los IDs pueden cambiar entre instancias.

## 4.3. `visited(customer)` también se conserva perfectamente

El dump contiene:

```text
Atom visited(c2)
Atom visited(c3)
...
Atom visited(c16)
```

y todos aparecen inicialmente negados.

Podemos construir:

```rust
struct CustomerInfo {
    name: String,
    visited_var_id: usize,
    loc_var_id: usize,
}
```

y durante cada evaluación determinar en O(n) qué clientes quedan pendientes.

## 4.4. `vehicles` y `load` son variables `Regular` limpias

El dump de `P-n16-k8` termina con:

```text
NUM #87: name='PNE vehicles()', type=Regular, initial=1
NUM #88: name='PNE load()', type=Regular, initial=0
NUM #89: name='PNE total-cost()', type=Cost, initial=0
```

Esto es excelente para la heurística.

Durante la construcción se pueden localizar los IDs por nombre/patrón:

```text
"PNE vehicles()" → vehicles_var_id
"PNE load()"     → load_var_id
```

Después los valores dinámicos se leen con `fill_numeric`.

De nuevo: **no deben hardcodearse 87 y 88**. Esos IDs son específicos de esta traducción/instancia.

## 4.5. `total-cost` está separado como `Cost`

`total-cost` aparece como:

```text
type=Cost
```

No es necesario usarlo como feature principal de `h(s)`, porque el search ya mantiene `g(s)`.

En A*:

\[
f(s)=g(s)+h(s)
\]

Por tanto, meter el coste ya acumulado otra vez dentro de `h(s)` podría duplicar información y alterar la interpretación de la heurística.

---

# 5. Hallazgo importante: NO conviene parsear las variables numéricas estáticas por nombre

Antes del dump parecía plausible esperar nombres limpios del tipo:

```text
demand(c7)
capacity()
travel-cost(c7,c8)
max-vehicles()
```

El dump real demuestra que esa expectativa es demasiado optimista.

El traductor genera muchas variables como:

```text
PNE derived!sum_PNE demand(?customer_0)_PNE load()(c10)
PNE derived!difference_PNE derived!sum_PNE demand(?customer_0)_PNE load()(?customer_0)_PNE capacity()(c10)
```

y constantes genéricas como:

```text
PNE derived!35.0()
PNE derived!31.0()
PNE derived!30.0()
...
```

También aparecen expresiones compiladas relacionadas con costes:

```text
PNE derived!sum_PNE travel-cost(... d1)_PNE travel-cost(d1, ...)
```

Por tanto:

> **No debe basarse `CvrpTaskInfo` en parsear todas esas cadenas generadas por el translator.**

Sería frágil frente a cambios de traducción y mezclaría la evaluación de la heurística con reverse engineering de nombres internos.

---

# 6. Estrategia robusta para reconstruir la información CVRP

## 6.1. Clientes

Fuente primaria:

```text
Atom visited(customer)
```

Descubrimiento:

```rust
for var_id in 0..task.variables().len() {
    for value in 0..task.variables()[var_id].domain_size() {
        let fact = ExplicitFact::propositional(var_id, value);
        let name = task.get_fact_name(&fact);

        // detectar Atom visited(...)
    }
}
```

Esto proporciona la lista de clientes independientemente del tamaño de la instancia.

## 6.2. Posición actual

Fuente:

```text
Atom loc(node)
```

Precomputar:

```text
node → loc_var_id
```

Durante `compute_heuristic()`:

```text
prop_state_values[loc_var_id]
```

indica si la localización está activa.

## 6.3. Visitados / pendientes

Fuente:

```text
Atom visited(customer)
```

Precomputar:

```text
customer → visited_var_id
```

No asumir que `0=true` y `1=false` en todas las representaciones; el builder debe guardar también el valor que corresponde al hecho positivo.

Mejor mapping:

```rust
struct PropFactRef {
    var_id: usize,
    positive_value: usize,
}
```

Así la infraestructura no depende del orden de valores de la variable.

## 6.4. `load`

Descubrir una vez la variable numérica cuyo nombre corresponde a `PNE load()`.

Guardar:

```rust
load_var_id: usize
```

Leer por estado desde el vector devuelto por `fill_numeric`.

## 6.5. `vehicles`

Mismo patrón:

```text
PNE vehicles()
```

Guardar:

```rust
vehicles_var_id: usize
```

## 6.6. Distancias / costes de movimiento

### Recomendación

No parsear las expresiones `travel-cost` generadas por el translator.

Usar:

```rust
task.get_operators()
```

más:

```rust
metric_operator_cost_from_initial_values(task, op)
```

Los nombres grounded son claros.

### Matriz reconstruible

Para un operador:

```text
visit A B
```

el coste corresponde al desplazamiento `A -> B` bajo este dominio CVRP.

Por tanto:

```text
visit c4 c7  → distance[c4][c7]
visit d1 c7  → distance[d1][c7]
```

Para el retorno:

```text
return-to-depot c7 → distance[c7][d1]
```

Así puede reconstruirse una matriz dirigida completa sin asumir simetría.

### Validación adicional

Los operadores:

```text
visit-via-depot A B
```

pueden utilizarse como comprobación de consistencia:

```text
cost(visit-via-depot A B)
≈ cost(return-to-depot A) + cost(visit d1 B)
```

No es necesario usarlos como fuente primaria de la matriz si ya tenemos los arcos simples.

---

# 7. Demandas, capacidad y máximo de vehículos

Aquí el dump muestra que hay información, pero aún no debemos congelar una estrategia basada en strings.

## 7.1. Demandas

Se observa indirectamente:

```text
PNE derived!sum_PNE demand(... )_PNE load()(c10), initial=8
...
PNE derived!... (c7), initial=31
```

Como `load=0` inicialmente, esos valores coinciden con las demandas.

Sin embargo, parsear estas cadenas sería innecesariamente frágil.

### Vía preferida a comprobar

Inspeccionar los `assignment_effects()` de:

```text
visit A B
visit-via-depot A B
```

y seguir la variable numérica usada como RHS del efecto sobre `load`.

FF demuestra que tenemos disponibles:

```rust
assign.affected_var_id()
assign.var_id()
assign.operation()
```

Si el RHS es una `Constant`, su valor inicial se obtiene de:

```rust
task.get_initial_numeric_state_values()[assign.var_id()]
```

Esto permitiría recuperar:

```text
customer B → demand(B)
```

sin parsear expresiones derivadas.

**Estado:** API confirmada; mapping CVRP concreto pendiente de un dump pequeño de `assignment_effects()`.

## 7.2. Capacidad

La capacidad aparece incorporada en expresiones derivadas de precondiciones:

```text
demand(customer) + load - capacity <= 0
```

En `P-n16-k8`, el valor 35 existe como una `Constant`, pero no aparece una variable limpia llamada simplemente `capacity()`.

No conviene seleccionar `35` por valor: otra instancia puede usar otra capacidad y puede haber otras constantes con el mismo valor.

Opciones robustas:

1. reconstruir estructuralmente el comparison/assignment axiom que limita `load`;
2. seguir sus dependencias hasta la constante usada como capacidad;
3. si una primera heurística no necesita capacidad explícita, posponer este mapping.

La tercera opción es válida para empezar: PlanForge ya impide transiciones que violan la capacidad.

## 7.3. `max-vehicles`

Ocurre algo similar.

El dump muestra una expresión derivada equivalente a:

```text
1 + vehicles - max_vehicles
```

y en la instancia inicial produce `-6`, coherente con:

```text
vehicles = 1
max_vehicles = 8
```

Pero la implementación estable debe extraerlo estructuralmente, no inferirlo de posiciones fijas.

---

# 8. Diseño propuesto de la capa CVRP fija

## 8.1. `CvrpTaskInfo`

Ejemplo conceptual:

```rust
struct PropFactRef {
    var_id: usize,
    positive_value: usize,
}

struct CustomerInfo {
    name: String,
    visited: PropFactRef,
    location: PropFactRef,
}

struct CvrpTaskInfo {
    customers: Vec<CustomerInfo>,
    depot_name: String,
    depot_location: PropFactRef,

    load_var_id: usize,
    vehicles_var_id: usize,

    // Construido desde grounded operators + metric costs.
    distances: Vec<Vec<f64>>,

    // Añadir tras verificar assignment effects / numeric axioms.
    demands: Option<Vec<f64>>,
    capacity: Option<f64>,
    max_vehicles: Option<usize>,
}
```

Los `Option` reflejan el estado actual del trabajo: no bloquear la primera heurística por información que todavía no sea necesaria.

## 8.2. `CvrpStateView`

```rust
struct CvrpStateView<'a> {
    current_node: usize,
    visited: &'a [bool],
    load: f64,
    vehicles_used: f64,
}
```

Se construye usando únicamente:

```text
fill_state(...)
fill_numeric(...)
```

No debe realizar parsing de nombres.

## 8.3. Scratch

```rust
struct CvrpScratch {
    propositional: Vec<usize>,
    numeric: Vec<f64>,
    visited: Vec<bool>,
    unvisited: Vec<usize>,
}
```

Guardado en:

```rust
RefCell<CvrpScratch>
```

para reutilizar memoria.

---

# 9. Qué debería generar el LLM

Una vez exista la capa anterior, el LLM no debería recibir detalles del traductor de PlanForge.

No queremos evaluar:

> “¿Puede el LLM descubrir qué significa `var25` o parsear `PNE derived!...`?”

Queremos evaluar:

> “¿Puede el LLM diseñar una función heurística útil para orientar la búsqueda en CVRP?”

Por tanto, el objetivo ideal es que genere únicamente la lógica de estimación, conceptualmente:

```rust
fn estimate(
    task: &CvrpTaskInfo,
    state: &CvrpStateView,
    scratch: &mut CvrpScratch,
) -> f64
```

Ejemplos de features que podrá utilizar según la información disponible:

```text
- número de clientes restantes
- distancia desde posición actual al cliente pendiente más cercano
- mínimo coste para regresar al depósito
- MST sobre clientes pendientes
- sumas de aristas mínimas
- carga actual
- demanda restante
- estimación del número mínimo de rutas adicionales
```

La infraestructura de extracción debe mantenerse idéntica entre candidatos.

---

# 10. Generalización entre instancias

La misma heurística debe poder ejecutarse sobre distintas instancias producidas con el mismo dominio CVRP.

No se permiten IDs hardcodeados como:

```rust
load_var_id = 88
vehicles_var_id = 87
visited_c7_var = 42
```

El constructor descubre los IDs de nuevo para cada tarea.

Por tanto:

```text
P-n16-k8
   ↓
CvrpTaskInfo específico de esa tarea

P-n50-k10
   ↓
CvrpTaskInfo específico de esa tarea

misma lógica de h(s)
```

Esto es importante para evaluar generalización.

---

# 11. Qué NO debe hacer una heurística generada

Evitar:

```text
- parsear PDDL directamente dentro de compute_heuristic
- buscar strings de variables en cada estado
- hardcodear IDs
- hardcodear número de clientes
- hardcodear capacidad
- hardcodear nombres c2...c16
- reconstruir matrices en cada evaluación
- declarar dead-end sin prueba
- usar total-cost como sustituto de h(s)
- depender del orden concreto de variables de P-n16-k8
```

---

# 12. Qué sí debe hacer

```text
build/constructor:
    - validar que la tarea es compatible con nuestro CVRP
    - descubrir clientes
    - descubrir loc/visited
    - descubrir load/vehicles
    - reconstruir costes desde operadores
    - precomputar estructuras
    - reservar scratch

compute_heuristic:
    - if goal → 0
    - fill_state
    - fill_numeric
    - construir vista dinámica barata
    - calcular h(s)
    - devolver f64 >= 0
```

---

# 13. Distinción experimental importante

Debe separarse la calidad de:

```text
A) adaptador PlanForge → CVRP
```

de:

```text
B) heurística propuesta por el LLM
```

`A` es infraestructura fija escrita y validada una vez.

`B` es la variable experimental.

Así la comparación entre candidatos es justa:

```text
mismo planner
mismo dominio
mismo parser/adaptador
misma representación del estado
misma estrategia de búsqueda
────────────────────────────────
solo cambia h(s)
```

---

# 14. Admisibilidad

Nada de lo observado en FF implica que nuestras heurísticas generadas sean admisibles.

Una heurística es admisible si:

\[
h(s) \le h^*(s)
\]

para todo estado `s`.

`FF` no debe usarse como prueba de admisibilidad; sirve como referencia de ingeniería y como baseline de búsqueda.

Para una hLLM:

- si no existe prueba de admisibilidad, tratarla como **no admisible**;
- medir coste de solución / gap además de tiempo y expansiones;
- no afirmar optimalidad por usar A* con una h no demostrada admisible.

---

# 15. Siguiente paso técnico recomendado

No es necesario seguir inspeccionando toda la implementación de PlanForge.

El acceso al estado ya está resuelto.

El único punto estructural que merece una comprobación adicional antes de cerrar `CvrpTaskInfo` es:

```text
assignment_effects de:
- visit d1 cX
- visit cA cB
- visit-via-depot cA cB
- return-to-depot cA
```

Objetivo:

1. confirmar cómo se actualiza `load`;
2. verificar si de esos efectos puede recuperarse directamente `demand(customer)`;
3. opcionalmente seguir los comparison axioms para obtener `capacity` y `max-vehicles`.

Esto puede hacerse con un dump de unos pocos operadores, no con otra búsqueda completa.

Una primera heurística de distancias + clientes no visitados **no necesita esperar** a resolver capacidad/demandas.

---

# 16. Fuentes inspeccionadas

## PlanForge `FfHeuristic`

Hallazgos relevantes:

```text
- construcción estática en FfHeuristic::new
- fill_numeric sobre StateView
- fill_state sobre ConcreteState
- ExplicitFact::is_hold
- op.assignment_effects()
- metric_operator_cost_from_initial_values(...)
- scratch buffers reutilizables
- preferred operator IDs
```

## Dump real de `P-n16-k8`

Generado desde el runner externo `planforge-llm-cvrp`.

Hallazgos relevantes:

```text
proposicional:
    loc(c2...c16)
    loc(d1)
    visited(c2...c16)

numeric Regular:
    PNE vehicles()
    PNE load()

numeric Cost:
    PNE total-cost()

grounded operators:
    return-to-depot ...
    visit ...
    visit d1 ...
    visit-via-depot ...
```

---

# 17. Estado de decisiones

| Decisión | Estado |
|---|---|
| Usar PlanForge como planner | Congelada |
| CVRP numérico PDDL de Kuroiwa | Congelada |
| Runner externo `planforge-llm-cvrp` | Congelada |
| Registrar heurísticas con `ExternalHeuristic` | Validado |
| Leer estado con `EvaluationState` | Validado |
| Leer proposicional por lote con `fill_state` | Validado |
| Leer numérico por lote con `fill_numeric` | Validado |
| Precomputar información en constructor | Validado / recomendado |
| Extraer `loc` / `visited` desde fact names | Validado en P-n16-k8 |
| Extraer `load` / `vehicles` desde numeric names | Validado en P-n16-k8 |
| Hardcodear IDs | Prohibido |
| Parsear strings `PNE derived!...` para todo | Descartado como estrategia principal |
| Extraer distancias desde operadores + metric cost | Estrategia recomendada |
| Extraer demandas desde assignment effects | Pendiente de verificación concreta |
| Extraer capacidad/max vehicles | Pendiente; no bloquea primera h |
| LLM genera adaptador PlanForge | No |
| LLM genera lógica de h(s) | Sí |
| Preferred operators | Futuro / opcional |
