# Cómo lanzar el planificador (y generar una $h$ con el LLM)

Léete esto con la terminal abierta en el repo del código, no en `docs/`.

```text
c:\Code\GitHub\TFM\llm-generated-heuristics-vrp
```

Si `01 - CORREA.md` era *qué* hace $h$, aquí es *cómo* se lo pides a Pyperplan y *qué* mirar cuando termina. Las §§1–6 no llaman a ninguna API. La §7 genera **una** $h$ (hace falta `DEEPSEEK_API_KEY`).

---

## 1. Dos programas, no uno

| Script | Qué hace | ¿Lo usamos? |
|---|---|---|
| `src/pyperplan/pyperplan.py` | Lee PDDL, busca un plan, escribe `*.pddl.soln` | **Sí** (siempre: el plan lo escribe esto) |
| `llm-heuristics.py` | Llama al LLM y guarda un `.py` con una $h$ | **Sí**, §7. Una ejecución = **una** candidata |
| `end-to-end.py` | El LLM escribe el plan | **No** (comparación A del paper) |

`uv run …` = “usa el `.venv` de este repo”. Hay que estar **dentro** de `llm-generated-heuristics-vrp`. Si lanzas desde `TFM\` o desde `docs\`, no encuentra el script ni los `benchmarks/`.

Una sola vez (ya está hecho si viste un `.venv`):

```text
uv sync
```

---

## 2. El comando, pieza a pieza

Plantilla (copia y cambia solo lo que entiendas):

```text
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H hff benchmarks/ipc2023-learning/training/transport/p01.pddl
```

| Trozo | Qué decide | Si lo omites / lo cambias mal |
|---|---|---|
| `uv run src/pyperplan/pyperplan.py` | “Arranca el planificador.” | Sin `uv run`, puede usar otro Python y fallar. |
| `-s gbfs_early_goal_test` | **Cómo** busca: GBFS del paper (siempre el de $h$ más baja). | El default es `bfs`. **`bfs` ignora `-H`.** Si comparas $h$ sin este flag, no estás comparando $h$. |
| `-H hff` | **Qué brújula.** Aquí, $h^{\mathrm{FF}}$ (ya viene en Pyperplan). | El default *también* es `hff`, pero escríbelo: así ves qué estás midiendo. Otras built-in: `blind`, `hadd`, `hmax`, `goalcount`, … Un `.py` generado se pasa igual: `-H transport-heuristic.py`. |
| ruta al `.pddl` de la **instancia** | **Qué partida.** | Si no pasas el dominio, busca `domain.pddl` **en la misma carpeta** que esa instancia. |

Opcional: puedes pasar dominio e instancia:

```text
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H hff ruta/domain.pddl ruta/p01.pddl
```

En `transport` no hace falta: cada carpeta (`training/transport/`, `testing/transport/`) ya tiene su `domain.pddl`.

**Una ejecución = una instancia + una $h$ + un buscador.** Si quieres otra $h$, otra ejecución. Si quieres otra partida, otra ejecución. No hay un flag “compara todas”.

---

## 3. Primera partida: `p01` + `hff`

Eso es lo de la plantilla de arriba. `p01` es la partida mínima (1 furgoneta, 1 paquete, `l1` → `l2`). Debería acabar en menos de un segundo.

Mientras corre, Pyperplan hace esto (lo de `01` §5.1):

1. Lee `domain.pddl` + `p01.pddl`.
2. *Grounding:* convierte `drive ?v ?l1 ?l2` en acciones concretas (`drive v1 l1 l2`, …).
3. GBFS con $h^{\mathrm{FF}}$.
4. Si hay plan → escribe `p01.pddl.soln` **al lado** de `p01.pddl` (pisa el anterior si existía).
5. Si tienes el binario `validate` en el PATH, lo llama; si no, un warning. Da igual.

---

## 4. Qué leer en el log (y qué ignorar)

Líneas que **sí** importan (nombres reales del programa):

| En el log | Qué significa |
|---|---|
| `using search: gbfs_early_goal_test` | Confirmas que no se te ha colado `bfs`. |
| `using heuristic: …Heuristic` | Confirmas la brújula (`RelaxationFFHeuristic` = `hff`). |
| `Initial h value: 3.00` | $h(s_0)$: la brújula en la foto inicial. En `p01` + `hff` suele ser 3. |
| `Found new best h: 2.00 after …` | Ha encontrado un estado que *parece* más cerca. |
| `N Nodes expanded` | Cuántos estados ha “abierto”. Menos = brújula más útil (misma partida). |
| `Plan length: 3` | Acciones del plan. En `p01` el óptimo es 3. |
| `Search time: 0.xx` | Tiempo de la búsqueda (no del grounding). |

Líneas que **puedes ignorar** al principio: versión de Python, parseo, grounding, `validate`, `Peak memory`.

Si ves `No solution could be found`: Pyperplan **agotó** la lista de estados por explorar y no halló goal (en `p01` no debería pasar). **No hay timeout** en el programa: no se rinde a los 5 min. Si tarda demasiado, lo paras tú (`Ctrl+C`) o lo mata el SO por memoria; eso no escribe `.soln` y a menudo ni siquiera esa frase. Los 5 min del paper son un cronómetro **externo** (ellos cortan el proceso), no un flag de `-s`/`-H`.

---

## 5. El plan: `p01.pddl.soln`

Ábrelo. En `p01` es esto:

```text
(pick-up v1 l1 p1 c0 c1)
(drive v1 l1 l2)
(drop v1 l2 p1 c0 c1)
```

Cada línea = una acción **ya groundeada** (objetos concretos, no `?v`). `c0`/`c1` son peldaños de capacidad, no coordenadas (lo de `02`).

Eso es el plan. $h$ **no** está en este fichero: $h$ solo sirvió para decidir el orden de prueba.

Si vuelves a lanzar la misma instancia, **se pisa** el `.soln`. Si quieres guardar dos planes (`hff` vs `blind`), cópialos a otro sitio *antes* del segundo run, o anota longitud/expansiones del log: para comparar $h$ casi nunca hace falta el texto del plan, sino esas métricas.

---

## 6. Misma partida, otra brújula

Cambia **solo** `-H`. Deja `-s` y el `.pddl` iguales.

```text
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H blind benchmarks/ipc2023-learning/training/transport/p01.pddl
```

`blind` = “¿soy el goal? no → $h = 1$”. No ordena. En `p01` igual encuentra el plan de 3 acciones, pero suele **expandir más** (4 vs 3).

Eso es el protocolo de `01` §3.2 en miniatura. Anota a mano:

| instancia | heuristic | solved | length | expansions | time |
|---|---|---|---|---|---|
| `training/…/p01` | `hff` | | | | |
| `training/…/p01` | `blind` | | | | |

`solved` = `1` si escribió `.soln`, `0` si no (no es el texto del plan). Si no resuelve, `length` vacío. Si lo paras tú, pon `timeout` en una columna extra `status` (`ok` / `timeout` / `unsolvable`).

Cuando `p01` te aburra, **misma tabla**, otra fila de instancia. Siguiente sitio natural: `testing/transport/easy-p01.pddl` (sigue cabiendo en la cabeza) y luego `easy-p10.pddl` (ahí `blind` se ahoga y `hff` no).

Rutas útiles:

```text
benchmarks/ipc2023-learning/training/transport/p01.pddl
benchmarks/ipc2023-learning/testing/transport/easy-p01.pddl
benchmarks/ipc2023-learning/testing/transport/easy-p10.pddl
```

`training/` = partidas con las que el paper *elige* $h$. `testing/` = partidas con las que *evalúa*. Hoy da igual: las dos son PDDL de `transport`. Más adelante no mezcles “elegir” y “medir” en la misma tanda.

---

## 7. Generar una $h$ con el LLM (DeepSeek)

Esto **no** resuelve partidas. Llama a la API, recorta un bloque Python y lo guarda en un `.py`. El plan sigue saliendo de Pyperplan, con `-H` apuntando a ese fichero.

Una llamada = **una** candidata. El paper genera ~25 y elige; el repo no hace ese torneo.

### 7.1. La key

Ponla en `.env` en la raíz de `llm-generated-heuristics-vrp` (ya está en `.gitignore`; **no** la subas a git):

```text
DEEPSEEK_API_KEY=sk-...
```

El script lee ese `.env` ( `uv run` **no** lo carga solo; el error de `OPENAI_API_KEY` era eso: DeepSeek usa el cliente de OpenAI y, sin key, pide la de OpenAI). Alternativa: `uv run --env-file .env llm-heuristics.py …`.

### 7.2. El comando, pieza a pieza

Sigue estando en `llm-generated-heuristics-vrp`:

```text
uv run llm-heuristics.py --framework deepseek --model deepseek-v4-flash --domain transport --heuristic-name TransportHeuristic --heuristic-file transport-heuristic.py
```

| Trozo | Qué decide |
|---|---|
| `--framework deepseek` | Cliente de `https://api.deepseek.com`. Sin esto, el default es **Gemini**. |
| `--model deepseek-v4-flash` | Clave de `DEEPSEEK_MODELS` en `models.py`. Empieza por Flash (barato). `deepseek-v4-pro` si Flash saca Python roto. |
| `--domain transport` | Suite: `domain.pddl` + `p01` + `p99` + estados de ejemplo. El LLM **no** ve `easy-p10`; eso es para *evaluar* después. |
| `--heuristic-name TransportHeuristic` | Nombre de la **clase** Python. Tiene que acabar en `Heuristic` o el script (y luego Pyperplan) no la carga. |
| `--heuristic-file transport-heuristic.py` | Dónde guarda el código (cwd del repo). Si existe, **lo pisa**. |

Thinking en DeepSeek va **apagado** por defecto (`--no-thinking`). Con thinking on se comió el tope de 65 536 tokens y cortó el `.py`. Para volver a encenderlo: `--thinking`. `temperature` / `top_p` solo cuentan con thinking off.

La consola va a vomitar el prompt entero (dominio, instancias, ejemplos de Gripper/Logistics, código de Pyperplan). Eso es normal: es lo que se manda. Al final debe aparecer el código y `Saving code to transport-heuristic.py` / `Finished correctly`.

Si falla: key mal o ausente, modelo no está en el diccionario, o el LLM no devolvió un bloque de código (el script entonces peta y **no** escribe un `.py` útil).

### 7.3. Usar esa $h$ en Pyperplan

Mismo `-s` y mismas instancias que `hff` / `blind`. Solo cambia `-H`:

```text
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H transport-heuristic.py benchmarks/ipc2023-learning/training/transport/p01.pddl
```

Luego la misma `easy-p10` que ya tienes en la tabla. Añade filas `heuristic = transport-heuristic.py` (o el nombre de la clase). Si el `.py` tiene syntax error o peta al calcular $h$, GBFS muere: `solved=0` y en notes el error; no es timeout.

Empieza por `p01`. Si ahí ya explota, no gastes crédito en `easy-p10`.

### 7.4. Lo que esto no es

- No es el experimento del paper (1 candidata ≠ 25 + ganadora).
- No llames a `end-to-end.py`.
- Fase 1 (CVRP): ver `docs/explain/04 - CVRP-STRIPS.md`.

---

## 8. Decisiones que ya puedes tomar (y las que no)

**Sí, con conocimiento de causa:**

- ¿Esta ejecución de Pyperplan es comparable con Corrêa? Solo si `-s gbfs_early_goal_test`.
- ¿Estoy midiendo $h$ o el tamaño del problema? Cambia **una** cosa: o `-H`, o el `.pddl`.
- ¿El plan es “el de $h$”? No: el plan es de Pyperplan; $h$ solo guió.
- ¿Puedo lanzar `p99` ya? Puedes, pero `blind` puede no acabar. Empieza pequeño.
- ¿Generar otra $h$? Otro `--heuristic-file` (si no, pisa la anterior). Misma tabla, nueva fila.

**Todavía no:**

- `end-to-end.py`.
- El bucle de 25 candidatas (Fase 1: diseño en `docs/explain/04 - CVRP-STRIPS.md`).

---

## 9. Después de leer esto, con la terminal delante

Deberías poder:

- situarte en `llm-generated-heuristics-vrp` y lanzar `p01` con `hff`;
- señalar en el log `Initial h`, expansiones y `Plan length`;
- abrir el `.soln` y leer las tres acciones;
- repetir con `-H blind` y decir *por qué* el plan puede ser igual y las expansiones no;
- explicar por qué sin `-s gbfs_early_goal_test` no estás haciendo el experimento de $h$;
- generar **una** $h$ con DeepSeek Flash y meterla en `-H` sobre las mismas instancias.
