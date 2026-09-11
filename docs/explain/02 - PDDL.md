# PDDL para este TFM (sobre todo `transport`)

PDDL = *Planning Domain Definition Language*. Es el idioma en el que se escribe **el juego** y **una partida**.

Léete esto con `domain.pddl` y `p01.pddl` de `transport` abiertos. Luego `01 - CORREA.md`. Para lanzar el planner: `03 - EJECUTAR.md`.

Rutas:

```text
llm-generated-heuristics-vrp/benchmarks/ipc2023-learning/training/transport/domain.pddl
llm-generated-heuristics-vrp/benchmarks/ipc2023-learning/training/transport/p01.pddl
llm-generated-heuristics-vrp/benchmarks/ipc2023-learning/training/transport/p10.pddl
```

---

## 1. Dos ficheros, no uno

| Fichero | Qué es | Analogía |
|---|---|---|
| `domain.pddl` | Reglas del juego. Igual para todas las partidas de `transport`. | “Existen furgonetas, paquetes, carreteras; puedes conducir, cargar, descargar.” |
| `p01.pddl`, `p10.pddl`, `easy-p03.pddl`… | **Una partida:** objetos concretos, dónde está cada cosa al empezar, qué hay que conseguir. | “Esta vez hay 1 furgoneta y 1 paquete en `l1`; el paquete debe acabar en `l2`.” |

El planificador siempre lee **los dos**. Si solo le das la instancia, busca un `domain.pddl` en la misma carpeta.

Comentarios: líneas que empiezan por `;`. El resto es Lisp: muchos paréntesis. No te asustes: cada bloque `(:algo …)` es una sección.

---

## 2. El dominio: `domain.pddl`

Cabecera:

```text
(define (domain transport)
  (:requirements :typing)
```

“Este juego se llama `transport` y usa tipos.”

### 2.1. Tipos (el vocabulario)

```text
(:types
    size location locatable - object
    vehicle package - locatable
)
```

- `location` = sitio del mapa (`l1`, `l2`…).
- `vehicle` = furgoneta.
- `package` = paquete.
- `locatable` = “cosa que puede estar en un sitio” (furgonetas y paquetes).
- `size` = peldaños de capacidad (`c0`, `c1`, `c2`…), **no** un número 17.

### 2.2. Predicados (frases verdaderas o falsas)

Un predicado es una plantilla. En una partida se rellena y pasa a ser un **hecho**.

| Plantilla | Significado |
|---|---|
| `(road ?l1 ?l2)` | Hay carretera de `l1` a `l2` (una dirección; si es de ida y vuelta, el problema pone las dos). |
| `(at ?x ?loc)` | La furgoneta o el paquete `x` está en `loc`. |
| `(in ?p ?v)` | El paquete `p` va **dentro** de la furgoneta `v`. |
| `(capacity ?v ?s)` | A `v` le quedan huecos de tamaño `s` (el peldaño actual). |
| `(capacity-predecessor ?s1 ?s2)` | `s1` es el peldaño **justo debajo** de `s2` (`c0` debajo de `c1`, etc.). |

Los `?l1`, `?v` son variables. En `p01` se convierten en `(at p1 l1)`, `(road l1 l2)`, …

El **estado** que ve $h(s)$ es, más o menos, el conjunto de esos hechos que ahora mismo son ciertos. Los `road` y `capacity-predecessor` no los cambia ninguna acción: son **estáticos**. `at`, `in`, `capacity` sí cambian.

### 2.3. Acciones (lo único que el planner puede hacer)

Cada acción: **parámetros**, **precondiciones** (qué tiene que ser verdad), **efectos** (qué pasa a ser verdad / deja de serlo).

En este dominio **no hay costes**. Cada acción cuenta 1. El “buen” plan es el de **menos acciones**, no el de menos km.

#### `drive` — mover una furgoneta

```text
parámetros:  furgoneta v, origen l1, destino l2
hace falta:  v está en l1  y  hay (road l1 l2)
efecto:      v deja de estar en l1  y  pasa a estar en l2
```

El paquete que vaya `in` esa furgoneta **viaja con ella** (no hace falta un efecto extra: `in` no cambia).

#### `pick-up` — cargar

```text
parámetros:  v, sitio l, paquete p, peldaños s1 y s2
hace falta:  v y p en el mismo l
             capacity de v es s2
             s1 es el peldaño debajo de s2
efecto:      p ya no está “en el suelo” de l
             p pasa a (in p v)
             capacity baja de s2 a s1
```

Ejemplo: capacidad `c1` (1 hueco). Predecesor `c0 < c1`. Al cargar: `capacity` pasa a `c0` (llena).

#### `drop` — descargar

Al revés: el paquete sale del vehículo, aparece `(at p l)`, la capacidad **sube** un peldaño (`c0` → `c1`).

Por eso la cadena `c0 < c1 < c2` es una forma de contar huecos **sin números**. Si ves `c0 c1 c2 c3` y un vehículo en `c3`, caben 3 paquetes de 1 hueco.

---

## 3. Una partida mínima: `p01.pddl`

```text
(define (problem transport-01)
 (:domain transport)          ; usa las reglas de arriba
```

### Objetos (quién sale en esta partida)

```text
v1          - vehicle
p1          - package
l1 l2       - location
c0 c1       - size
```

Un mapa de **dos pueblos** unidos. Capacidad máxima 1 paquete.

### Inicio (`:init`) — foto al empezar

```text
(capacity v1 c1)              ; v1 tiene 1 hueco libre
(capacity-predecessor c0 c1)  ; bajar un peldaño = llenarse
(at p1 l1)                    ; el paquete está en l1
(at v1 l1)                    ; la furgoneta también
(road l1 l2)  (road l2 l1)    ; carretera de ida y vuelta
```

Dibujo:

```text
l1 ●────────● l2
   v1, p1
```

### Goal — qué tiene que ser verdad al final

```text
(at p1 l2)
```

**Solo el paquete.** La furgoneta puede quedarse donde sea. No hay “volver al almacén”.

Plan que ya vimos (3 acciones):

```text
(pick-up v1 l1 p1 c0 c1)   ; carga; capacity c1 → c0
(drive v1 l1 l2)           ; se mueve; p1 viaja porque está in v1
(drop v1 l2 p1 c0 c1)      ; deja p1 en l2; capacity c0 → c1
```

Eso es lo que $h^{\mathrm{FF}}$ estimó al inicio: $h(s_0) = 3$.

---

## 4. Una partida un poco más real: `p10.pddl`

Comentario del fichero: grafo `l1 — l3 — l2 — l4` (en el init las carreteras son `l1—l4—l2—l3`; el dibujo del comentario y las `road` a veces no coinciden al 100%; **manda el `:init`**).

Objetos: 2 furgonetas (`v1`, `v2`), 4 paquetes, 4 sitios, tamaños `c0 c1 c2` (hasta 2 huecos). Las dos furgonetas empiezan en `c2`.

El goal son **cuatro** facts: cada `p` en su destino. El planner tiene que entremezclar `drive` / `pick-up` / `drop` de las dos furgonetas.

Esto ya se parece más a “reparto”, pero sigue sin ser CVRP: los paquetes **no salen todos del mismo depósito** (`p1` está en `l3`, `p4` en `l1`…).

---

## 5. Training vs testing (los “problemas propuestos”)

```text
training/transport/     p01.pddl … p99.pddl     (pequeño → grande)
testing/transport/      easy-p01 …  hard-p30
```

Mismo `domain.pddl`. Cambia el tamaño: más `v`, más `p`, más `l`, a veces más peldaños `c`.

El **prompt** del LLM (cuando generas $h$) ve el dominio + `p01` + `p99`, no las 90 de test.

Cabeceras tipo `;; vehicles=4, packages=5, …` son del generador. Útiles; no las lee Pyperplan.

---

## 6. Qué *no* hay en este PDDL (y por qué el TFM lo nota)

| En CVRP-STRIPS (Fase 1) | En IPC `transport` (Fase 0) |
|---|---|
| Depósito `l0`, carga inicial en almacén | Sitios sueltos, sin almacén |
| Demanda \(q_i\): **\(q_i\) paquetes** con goal en cliente `i` (fungibles) | Un paquete = un origen aleatorio |
| Distancia / km | Cada `drive` cuesta **1**; km post-hoc |
| Capacidad | Peldaños `c0 < c1 < …` (1 paquete = 1 hueco) |
| Volver al depósito | Opcional (`-closed`); en `-open` solo en el plan |
| Ventanas de tiempo | No |
| Demanda agregada `(demand A)=20` sin 20 objetos | No (PDDL 2.1; §2.2 en `04`) |
| Sustitución en runtime (p5 vale por p3) | No en goal `(at p_i l_j)`; sí con fluents (futuro) |

Detalle, escalera de modelado y limitación §2.2: `04 - CVRP-STRIPS.md`. Instancias: `05 - CVRP-INSTANCE-CREATE.md` §3.4.

---

## 7. Del texto PDDL a lo que usa $h(s)$

Pyperplan **no** busca sobre el texto con `?v`. Hace *grounding*: instancia cada acción con objetos reales.

`(drive ?v ?l1 ?l2)` + `{v1}` + `{l1,l2}` → `(drive v1 l1 l2)` y `(drive v1 l2 l1)`.

Un estado es un conjunto de strings, por ejemplo:

```text
(at v1 l1)
(at p1 l1)
(capacity v1 c1)
```

más los estáticos (`road`, `capacity-predecessor`) guardados aparte.

La $h$ del LLM (o $h^{\mathrm{FF}}$) recibe **eso**, no el `.pddl` crudo. El `.pddl` es para definir el mundo y para el prompt.

---

## 8. Mini glosario

| Palabra | Significado aquí |
|---|---|
| Dominio | Reglas (`domain.pddl`) |
| Problema / instancia / tarea | Una partida (`pXX.pddl`) |
| Hecho / átomo / fact | Una frase cierta, p. ej. `(at p1 l2)` |
| Estado | El conjunto de hechos ciertos ahora |
| Acción / operador | `drive`, `pick-up`, `drop` (luego, ya concretas) |
| Goal | Hechos que tienen que acabar siendo ciertos |
| Grounding | Pasar de plantillas `?x` a objetos `v1`, `l2`… |
| Estático | Hecho que ninguna acción cambia |

---

## 9. Después de leer esto, con `p01` delante

Deberías poder señalar:

- dónde se dice que existe `drive`;
- dónde se dice que *en esta* partida el paquete empieza en `l1`;
- por qué hacen falta dos `(road …)`;
- por qué `c0` y `c1` no son coordenadas;
- por qué el goal no menciona `v1`;
- por qué esto aún no es un CVRP.

Siguiente lectura: `docs/explain/01 - CORREA.md` (§3: qué hace $h$ con esos hechos). Para lanzar: `docs/explain/03 - EJECUTAR.md`. Fase 1 (CVRP): `04 - CVRP-STRIPS.md`, instancias: `05 - CVRP-INSTANCE-CREATE.md`.
