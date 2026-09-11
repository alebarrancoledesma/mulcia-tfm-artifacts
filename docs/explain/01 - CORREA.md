# Qué hace Corrêa, en claro

Léete esto entero y deberías poder **usar el repo** y **explicar el paper** sin abrir el código. Distingue siempre dos cosas:

- **El paper** (NeurIPS 2025): método + experimentos + tablas.
- **El repo** (`llm-generated-heuristics-vrp`): herramientas. **No automatiza** todo lo del paper.

**Paper:** Corrêa, Pereira y Seipp. *Classical Planning with LLM-Generated Heuristics.*  
**Repo:** fork del oficial, licencia GPL-3.0.

Si el PDDL de `transport` no se entiende: `docs/explain/02 - PDDL.md` (léelo con `domain.pddl` y `p01.pddl` abiertos). Para lanzar Pyperplan: `docs/explain/03 - EJECUTAR.md`.

---

## 1. El problema, con un ejemplo

Imagina que tienes que llevar paquetes de un sitio a otro con furgonetas (el dominio `transport`).

El ordenador no “ve” la solución. Prueba **acciones** de una en una:

- mover una furgoneta por una carretera
- cargar un paquete
- descargar un paquete

Cada secuencia de acciones es un posible plan. Hay **muchísimas**. Si pruebas a lo loco, no acabas.

Hace falta una brújula: en cada situación (estado), un número que diga *“¿cuánto falta, más o menos, para tener todos los paquetes en su sitio?”*

Ese número es la **heurística**, $h(s)$:

- $h$ alta → este estado parece lejos del objetivo → el buscador lo deja para después
- $h$ baja → parece cerca → lo prueba antes

El buscador que usa Corrêa se llama **GBFS** (greedy best-first search): siempre expande el estado con la $h$ más baja. No garantiza el plan más corto; intenta **encontrar uno pronto**.

El plan lo fabrica el **planificador** (Pyperplan), no el ChatGPT. Por eso el plan, si sale, respeta las reglas (no cargas un paquete que no está ahí, etc.).

---

## 2. Qué hace el *paper* (y qué no)

**No** le piden al LLM: “escribe el plan para esta instancia”.  
Eso se llama planificación *end-to-end* y suele fallar o no generalizar a problemas más grandes.

**Sí** le piden: “mira el manual del juego (el fichero PDDL del dominio) y escribe un **programa Python** que, dado un estado, calcule $h$”.

Esa $h$ es **de ese dominio**. La de Transport no sirve para apilar bloques, y al revés.

En el paper el procedimiento completo es:

1. El LLM genera **varias** funciones candidatas (unas 25, con un poco de aleatoriedad).
2. Las prueban en un lote de problemas **pequeños** (training), cada una 5 minutos.
3. Se quedan con la que **más problemas resuelve** (si empatan, la más rápida: *agile score*).
4. Esa ganadora se usa en problemas **más grandes** (test), sin volver a llamar al LLM.

El LLM trabaja **al generar** $h$. Durante la búsqueda no hay más llamadas a la API.

**Ojo:** el repo **no** lanza esas 25 candidatas ni elige la ganadora solo. Una llamada a `llm-heuristics.py` = **una** $h$ guardada en un `.py`. El torneo training/test del paper lo tienes que hacer tú (o nosotros en el TFM) a mano: generar varias, correr Pyperplan, comparar.

---

## 3. Teoría: qué produce una $h$ y cómo se compara

La tabla de flags (`blind`, `hff`, …) solo es la lista de brújulas. Aquí está lo que importa.

### 3.1. Qué *produce* una heurística

No produce un plan. Produce **un número por estado**.

$$
h(s) \approx \text{cuántas acciones faltan para llegar al objetivo desde } s
$$

- En el estado inicial de `p01` (paquete en `l1`, hay que llevarlo a `l2`), una $h$ buena debería decir algo cerca de **3** (cargar, conducir, descargar).
- Cuando el paquete ya está en `l2`, **todas** deben decir $h = 0$.

Ese número **no tiene que ser exacto**. GBFS solo necesita que *ordene* bien: los estados de verdad cercanos deberían tener $h$ más baja que los lejanos. Por eso el paper permite $h$ **no admisibles** (pueden pasarse de listillas y decir un número mayor que el óptimo).

Cada tipo de $h$ calcula ese número de una forma distinta. Misma foto del mundo, distinta cuenta:

| $h$ | Qué mira para sacar el número | En `p01` al empezar (aprox.) |
|---|---|---|
| `blind` / $h_0$ | ¿Soy el objetivo? No → **1**. Siempre 1 hasta el final. | $1$ |
| `goalcount` / $h^{\mathrm{GC}}$ | ¿Cuántos facts del goal faltan? Aquí solo `(at p1 l2)`. | $1$ |
| `hff` / $h^{\mathrm{FF}}$ | Inventa un mundo sin “deshacer” y cuenta un plan relajado. | $3$ (en el run real: *Initial h value: 3.00*) |
| `hadd` | Suma, por cada fact del goal, lo que costaría conseguirlo en el mundo relajado (puede contar de más). | un entero $\ge 0$ |
| `hmax` | Como `hadd`, pero se queda con el fact **más caro**, no la suma. Suele ser más pequeña. | un entero $\ge 0$ |
| landmarks / LM-Cut | “Cosas que todo plan tiene que hacer”; cuenta las que aún no has hecho. | un entero $\ge 0$ |
| $h$ del LLM | Lo que haya escrito el Python: caminos, paquetes, furgonetas… | lo que salga; en Transport suele parecerse a “viajes + cargas” |

`blind` y `goalcount` en `p01` dan el **mismo** 1, pero no ordenan igual el resto de la búsqueda: `goalcount` baja a 0 solo cuando el paquete llega; `blind` también, pero *por el camino* todos los estados no-goal empatan a 1, así que GBFS no sabe a cuál ir. Por eso `blind` explora más (en `p01`: 4 nodos vs 3 de $h^{\mathrm{FF}}$; en `easy-p01`: 21 vs 3).

### 3.2. Sí: el *mismo* problema, varias $h$, luego se compara

No es “cada heurística tiene su problema”. El protocolo es:

```text
para cada instancia  (ej. easy-p10.pddl)
    para cada heurística que estemos comparando  (blind, h_FF, h_LLM, …)
        misma búsqueda GBFS
        anotar: ¿resolvió?  longitud del plan  expansiones  tiempo
```

Misma foto, distinta brújula. Luego miras la tabla.

**No se lanzan todas las $h$ de Pyperplan en cada experimento.** El paper, en Pyperplan, se centra en `blind` y $h^{\mathrm{FF}}$ frente a la $h$ del LLM. Las otras (`hadd`, `hmax`, landmarks…) existen en el programa y salen sobre todo en Fast Downward o en ablaciones. Nosotros, Fase 0: solo `hff` y `blind`. Fase 1: esas dos + la $h$ que genere el LLM (y FD si entra).

Una fila de esa tabla es *una* ejecución: un `.pddl` + un `-H`. Por eso en `fase0_hff_blind.csv` hay dos filas por instancia.

### 3.3. Ejemplo concreto: `training/transport/p01`

- 1 furgoneta `v1` en `l1`, 1 paquete `p1` en `l1`, destino `l2`, carretera de ida y vuelta.
- Plan que salió (con $h^{\mathrm{FF}}$ y con `blind`):

```text
(pick-up v1 l1 p1 …)
(drive v1 l1 l2)
(drop v1 l2 p1 …)
```

Longitud 3. $h^{\mathrm{FF}}$ empezó diciendo 3 y fue bajando 3 → 2 → 1 → 0. `blind` dijo 1, 1, 1, 0 y dio más rodeos (4 expansiones vs 3).

Cuando el problema crece (`easy-p10`, 5 paquetes), `blind` se pierde (timeout). $h^{\mathrm{FF}}$ sigue teniendo una cuenta útil y acaba (plan 21, 51 expansiones). **Eso es comparar:** misma instancia, dos $h$, una no da abasto.

### 3.4. Cómo se decide quién “gana”

Nadie mira el número $h(s)$ de la tabla final (eso es interno). Se miran **resultados de la búsqueda**:

| Métrica | Qué significa | Quién gana |
|---|---|---|
| **Coverage** | ¿Cuántas instancias resuelve antes del timeout? | Más resueltas. *La* métrica del paper. |
| **Expansiones** | ¿Cuántos estados abre? | Menos = la brújula ordena mejor. |
| **Tiempo** | Reloj | Menos. (Pyperplan es lento; comparar tiempos con Fast Downward es tramposo.) |
| **Longitud del plan** | Nº de acciones del plan encontrado | Menos suele ser mejor, pero GBFS **no** es óptimo: una $h$ puede resolver más problemas con planes un poco más largos. |

Empate típico del paper al *elegir* entre 25 $h$ del LLM: más coverage en training; si empatan, mejor *agile score* (más rápida).

**No se compara** “$h^{\mathrm{FF}}(s_0) = 3$ vs $h_{\mathrm{LLM}}(s_0) = 5$” como ganador. Se compara el **efecto** de usar esa $h$ dentro de GBFS. (En Fase 1 sí miraremos $h(s)$ vs longitud real en instancias tiny, como extra, no como ranking principal.)

### 3.5. Las tres ligas del paper (después de entender lo de arriba)

Hay **tres comparaciones**. No las mezcles.

### Comparación A — ¿Y si el LLM escribe el plan él solo?

| Uso del LLM | Qué produce | Resultado en el paper |
|---|---|---|
| End-to-end | El plan (lista de acciones) | Mal, sobre todo si el modelo no es “de razonar” |
| Generar $h$ | Un `.py` que estima lo que falta | **Muchísimo mejor** (el planner termina el trabajo) |

Ejemplo: Gemini Flash resuelve 19 tareas escribiendo planes y **296** si solo escribe la heurística.

En el repo esto es `end-to-end.py` (el LLM escribe el plan). **No es el método principal.** Nosotros no lo necesitamos para la Fase 0.

### Comparación B — Heurísticas clásicas **dentro de Pyperplan** (el mismo programa)

Pyperplan ya trae brújulas hechas por humanos, **iguales para todos los dominios**.

| Flag `-H` | Nombre | Qué hace, en cristiano | ¿Es “lista”? |
|---|---|---|---|
| `blind` | $h_0$ | Si ya estás en el objetivo, dice 0. Si no, dice **siempre 1**. | No. Ir a ciegas. Suelo. |
| `hff` | $h^{\mathrm{FF}}$ (Fast Forward) | Imagina un mundo más fácil: las acciones no “deshacen” nada. Calcula un planito relajado y usa su longitud como $h$. | Bastante. **La clásica de referencia.** |
| `goalcount` | $h^{\mathrm{GC}}$ | Cuenta cuántos trozos del objetivo faltan. | Tosca: no mira si hay que cruzar medio mapa. |
| `hadd`, `hmax`, `hsa` | familia “relajada” | Variantes de la misma idea que FF. | El paper las usa poco en la tabla principal. |
| `landmark`, `lmcut` | landmarks | Marca hechos que *cualquier* plan tiene que cumplir y cuenta los que faltan. | Más elaboradas; el paper las compara sobre todo fuera de Pyperplan. |

**Baseline del paper en Pyperplan:** `blind` y sobre todo **$h^{\mathrm{FF}}$**.

**Lo que nosotros ya corrimos:** `transport` + $h^{\mathrm{FF}}$ y `transport` + `blind`. En un problema pequeño los dos acaban; en `easy-p10` (5 paquetes) $h^{\mathrm{FF}}$ tarda menos de 1 s y `blind` no acabó.

Números del paper (720 tareas de test, 8 dominios):

- $h^{\mathrm{FF}}$ en Pyperplan: unas **234–243** resueltas
- $h$ del LLM DeepSeek V3 ($h^{V3}$): **343**
- $h$ del LLM DeepSeek R1 ($h^{R1}$): **373**

La $h$ del LLM **gana en total**. No en todos los dominios.

### Comparación C — Fast Downward (otro planificador, más serio)

Pyperplan es **didáctico, Python, lento**. Fast Downward es el estándar, C++, rápido. **No viene en el repo.** El paper lo usa como rival externo.

Comparan GBFS + $h$ del LLM (en Pyperplan) contra GBFS + $h^{\mathrm{GC}}$, $h^{\mathrm{lmc}}$, $h^{\mathrm{FF}}$, $h^{\mathrm{add}}$, $h^{\mathrm{cea}}$, $h^{\mathrm{cg}}$ y una aprendida $h^{\mathrm{WLF}}$ (todas en Fast Downward).

Resultado agregado: $h^{R1}$ en Pyperplan (**373** / 720) supera a las clásicas de FD (~295–324) y queda parecida a $h^{\mathrm{WLF}}$ (371). La tesis: una $h$ de dominio buena **compensa** un motor flojo.

Nuestra Fase 0 **no** necesita Fast Downward. El MASTER lo deja para “si entra fácil” más adelante.

---

## 4. Transport en el paper (no es CVRP)

Uno de **ocho** dominios IPC 2023 Learning (`blocksworld`, `childsnack`, `floortile`, `miconic`, `rovers`, `sokoban`, `spanner`, `transport`). No es el centro del artículo.

90 tareas de test:

| Quién guía | Resueltas |
|---|---:|
| $h^{\mathrm{FF}}$ en Pyperplan | 29 |
| $h^{\mathrm{FF}}$ en Fast Downward | 41 |
| $h^{V3}$ (LLM) | 42 |
| $h^{R1}$ (LLM) | **59** |
| $h^{\mathrm{WLF}}$ (aprendida) | 28 |

La $h$ que eligieron para Transport: caminos más cortos en el mapa y, para cada paquete, “ir a por él + llevarlo + cargar/descargar”, eligiendo a veces la furgoneta más conveniente. Puede pecar de más o de menos. **No es un solver de rutas.**

`transport` **no es un CVRP**: los paquetes pueden nacer en cualquier sitio, no hay depósito obligatorio, no se minimizan km. Por eso luego (Fase 1) haremos instancias “con pinta de CVRP” y **otra** $h$.

---

## 5. Mapa del repo (esto es lo que vas a tocar)

```text
llm-generated-heuristics-vrp/
  llm-heuristics.py          ← genera UNA h (llama al LLM, guarda un .py)
  end-to-end.py              ← el LLM escribe el plan (comparación A; lo ignoramos)
  src/llm_heuristics/        ← prompts, modelos, lista de dominios (suites)
  src/pyperplan/             ← el planificador (parsea PDDL, busca, escribe el plan)
  benchmarks/ipc2023-learning/
    training/<dominio>/      ← p01.pddl … p99.pddl + domain.pddl
    testing/<dominio>/       ← easy- / medium- / hard- + domain.pddl
  results/                   ← lo nuestro (smoke Fase 0)
```

Tres piezas mentales:

1. **Instancia PDDL** = un problema concreto (`p01.pddl`: estos paquetes, estas carreteras).
2. **Dominio PDDL** = las reglas del juego (`domain.pddl`: qué es un vehículo, qué hace `drive`).
3. **Heurística** = brújula. O built-in (`-H hff`) o un `.py` generado (`-H mi-h.py`).

### 5.1. Qué hace Pyperplan cuando le das una instancia

Sin magia:

1. Lee `domain.pddl` + la instancia (si no pasas el dominio, busca `domain.pddl` al lado).
2. **Grounding:** convierte las reglas con variables (`¿mover vehículo ?v de ?a a ?b?`) en acciones concretas (`mover v1 de l1 a l2`). El estado pasa a ser un conjunto de frases tipo `(at p1 l2)`.
3. Arranca GBFS con la $h$ que hayas elegido.
4. Si encuentra plan, lo escribe en **`instancia.pddl.soln`** (junto al `.pddl`).
5. Log: longitud del plan, nodos expandidos, tiempo. (El `validate` oficial no lo tenemos instalado; no pasa nada.)

Eso es lo que ya corrimos con `-H hff` y `-H blind`.

### 5.2. Qué hace `llm-heuristics.py`

1. Mira `--domain transport` y carga la **suite**: dominio + `p01` + `p99` + un estado de ejemplo + hechos estáticos de ejemplo.
2. Monta un **prompt** enorme (el del paper): reglas, dos instancias, ejemplos de Gripper y Logistics con sus $h$ hechas a mano, cómo se ve un estado por dentro, código de Pyperplan, una checklist.
3. Llama a Gemini / OpenAI / DeepSeek / NVIDIA (hace falta la API key en el entorno).
4. Recorta el bloque de código Python de la respuesta.
5. Lo guarda en `--heuristic-file` (por defecto `new-heuristic.py`).

**Para.** No resuelve instancias. No elige entre 25 candidatas.

La clase del `.py` tiene que llamarse `…Heuristic`. Pyperplan, si le pasas un fichero a `-H`, carga esa clase y la usa como brújula.

Si el código que genera el LLM está mal (syntax error, peta al calcular $h$), GBFS muere. El paper tira esas candidatas; nosotros también tendremos que hacerlo.

### 5.3. Suites: cómo “existe” un dominio en el repo

`src/llm_heuristics/suites.py` registra cada dominio con:

- `domain.pddl`
- instancia pequeña (`p01`) e instancia grande (`p99`) — van al prompt
- `example-state.out` / `example-static.out` — un estado a medias y los hechos que no cambian (`road`, etc.), en el formato interno de Pyperplan

Para la Fase 1 (CVRP-STRIPS) no hay que reescribir el planner: se añade una carpeta + una entrada en `SUITES`, como dice el README.

### 5.4. Qué no está en el repo

- Fast Downward
- El bucle “genera 25 → evalúa training → elige ganadora”
- Nuestras instancias CVRP (aún)
- Las tablas del paper (están en el PDF, no en el código)

Ablaciones del prompt (`--ablation`): para el paper. Nosotros no las tocamos.

---

## 6. Cómo se usa, en la práctica

Hace falta `uv` (ya hicimos `uv sync`).

```text
# 1) Resolver con una heurística que YA existe (sin LLM)
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H hff   benchmarks/ipc2023-learning/testing/transport/easy-p01.pddl
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H blind benchmarks/.../easy-p01.pddl

# 2) Generar una h (API key: GOOGLE_API_KEY, OPENAI_API_KEY, …)
uv run llm-heuristics.py --domain transport --heuristic-name TransportHeuristic --heuristic-file transport-heuristic.py

# 3) Resolver con ESA h
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H transport-heuristic.py benchmarks/.../easy-p01.pddl
```

`-s gbfs_early_goal_test` es el buscador del paper. No uses el default `bfs` si quieres comparar con ellos.

API keys: el README lista Gemini, OpenAI, DeepSeek, NVIDIA. En esta máquina, al hacer el smoke, **no había ninguna**.

Smoke Fase 0: `results/fase0_hff_blind.csv`.

---

## 7. Esquema para no perderse

```text
¿Quién escribe el plan?
    el PLANIFICADOR (Pyperplan)
    nunca el LLM en el método principal

¿Quién escribe la brújula h?
    o un humano / algoritmo clásico  (h^FF, blind, …)   → ya en Pyperplan
    o un LLM (un .py)                                  → llm-heuristics.py

¿Qué compara el PAPER?
    1. el mismo LLM escribiendo el plan
    2. h^FF y blind en Pyperplan
    3. Fast Downward (fuera del repo)

¿Qué hace el REPO por ti?
    generar un .py  +  buscar un plan con la h que le pidas
    el resto (25 candidatas, tablas, FD) es trabajo nuestro / del paper
```

---

## 8. Frase para la memoria

> Corrêa no usa el LLM como planificador, sino como generador de una heurística de dominio en Python. Esa heurística guía una búsqueda clásica (GBFS). La comparan con la planificación end-to-end del propio LLM, con heurísticas clásicas del mismo planner (`blind`, sobre todo $h^{\mathrm{FF}}$) y con las de Fast Downward. En coverage ganan, también en Transport. El repositorio implementa la generación de una candidata y Pyperplan; la selección entre candidatas y el benchmark son el protocolo experimental, no un botón. Nosotros partimos de ese pipeline y lo especializamos a un CVRP en PDDL.

---

## 9. Después de leer esto deberías poder…

- Explicar que $h(s)$ es un número (“acciones que faltan”), no un plan.
- Decir que se lanza **la misma instancia** con varias $h$ y se comparan coverage / expansiones / tiempo / longitud.
- Distinguir `blind`, $h^{\mathrm{FF}}$ y $h$ del LLM, y saber que **no** corremos `hadd`/`lmcut` en cada experimento.
- Encontrar en el disco: un dominio, una instancia, el script que genera $h$, el planner.
- Correr `hff` / `blind` sobre `transport` y saber que el plan queda en `*.pddl.soln`.
- Entender que generar $h$ exige API key y que **una** ejecución ≠ el experimento del paper.
- Ver por qué Fase 1 = nuevas instancias + nueva $h$, no un planner nuevo.
