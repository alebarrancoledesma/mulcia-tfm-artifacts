# Candidata 01 — `TransportHeuristic` (DeepSeek Flash, sin thinking)

Análisis de la primera $h$ que **sí** se guardó entera. El código (esta misma carpeta): `01 - transport-heuristic.py` (copia del `transport-heuristic.py` del repo). Cómo se lanza: `docs/explain/03 - EJECUTAR.md` §7.

Esto **no** es el torneo del paper (~25 candidatas). Es una tirada.

---

## 1. Condiciones de generación (trazabilidad)

Fecha: **2026-09-05**. Cwd: `llm-generated-heuristics-vrp`.

### 1.1. La que vale (este `.py`)

| Campo | Valor |
|---|---|
| Script | `llm-heuristics.py` |
| Framework | `deepseek` (`https://api.deepseek.com`) |
| Modelo (CLI → API) | `deepseek-v4-flash` → `deepseek-v4-flash` |
| Dominio / suite | `transport` (`domain.pddl` + `p01` + `p99` + `example-state` / `example-static`) |
| Prompt | `neurips` (paper), `--ablation false` |
| `--heuristic-name` | `TransportHeuristic` |
| `--heuristic-file` | `transport-heuristic.py` (cwd del repo; luego copiado a `01 - llm assets/`) |
| Thinking | **off** (`--no-thinking`, default tras el corte de la 1.2) |
| `reasoning_effort` | no aplica (thinking disabled) |
| `--temperature` | `1.0` (default) |
| `--top-p` | `0.5` (default) |
| `--idea` | vacío |
| Key | `DEEPSEEK_API_KEY` en `.env` (el script la lee; `uv run` **no** carga `.env` solo) |
| Resultado | `Finished correctly` (~14:18). Fichero **cerrado**. |

```text
uv run llm-heuristics.py --framework deepseek --model deepseek-v4-flash --domain transport --heuristic-name TransportHeuristic --heuristic-file transport-heuristic.py
```

### 1.2. Intento anterior (no hay `.py` usable)

Misma línea de comando, **antes** de `--no-thinking`. Thinking iba **on** (default de la API V4, `high`).

| Campo | Valor |
|---|---|
| Thinking | on (no había flag todavía) |
| `prompt_tokens` | 11 554 |
| `reasoning_tokens` | 63 788 |
| `completion_tokens` | **65 536** (tope; se cortó) |
| Duración | ~9 min (14:05 → 14:14) |
| Fallo | respuesta sin ` ``` ` de cierre → `sanitize_llm_answer` → `None.group(1)` |
| Artefacto | no se escribió fichero |

No relanzar así: vuelve a comerse el techo de salida. Término medio si se quiere thinking: `reasoning_effort=low` (aún no está en el CLI).

---

## 2. Condiciones de evaluación (Pyperplan)

Misma $h$, **otro** programa. El LLM no se llama.

```text
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H transport-heuristic.py benchmarks/ipc2023-learning/training/transport/p01.pddl
```

| Campo | Valor |
|---|---|
| Buscador | `gbfs_early_goal_test` (el del paper; sin esto `bfs` ignora `-H`) |
| `-H` | `transport-heuristic.py` → clase `TransportHeuristic` |
| Instancia | `training/transport/p01` |

Resultado `p01` (2026-09-05 ~14:21):

| Métrica | Valor |
|---|---|
| `using heuristic` | `TransportHeuristic` |
| `Initial h` | **3.00** |
| Mejor $h$ | 3 → 2 → 1 |
| `solved` | 1 |
| `length` | 3 |
| `expansions` | 3 |
| `Search time` | 0.00 s (CPU, redondeo) |

Igual que $h^{\mathrm{FF}}$ en esta partida. `validate` no está en el PATH (da igual).

`easy-p10` y el resto: misma receta, otra fila; aún no en esta nota.

---

## 3. Qué calcula esta $h$

Por cada paquete que aparece en el goal y **no** está ya en su sitio:

- En el suelo: $2 + d(\text{sitio del paquete},\ \text{goal})$ — pick-up + drives + drop.
- Dentro de una furgoneta: $1 + d(\text{sitio del vehículo},\ \text{goal})$ — drives + drop.

$d$ = BFS sobre `road` (cada carretera = 1 acción `drive`). Suma de todos los paquetes.

En `p01` (paquete en `l1`, goal `l2`, un `drive`): $2+1=3$. Cuadra con el log.

Familia: caminos más cortos + cargar/descargar, como la $h$ de Transport del paper. **No** es un solver de rutas. No usa capacidad en el número final (el docstring lo menciona y el código no).

---

## 4. Qué está bien

- Encaja con Pyperplan: `class …Heuristic(Heuristic)`, `__init__(self, task)`, `__call__(self, node)`.
- Hechos estáticos (`road`, `capacity-predecessor`) en el constructor; el estado dinámico en `__call__`.
- $h=0$ si todos los paquetes del goal ya están.
- Esqueleto tipo Gripper del prompt (`get_parts` / `match` / `fnmatch`): el few-shot hizo su trabajo.
- En `p01` no petó y ordenó el camino corto (3 expansiones).

---

## 5. Lo flojo (para no olvidarlo; no reescribir a mano)

- **No cuenta “ir a por el paquete”.** Solo suelo→goal. Si la furgoneta está lejos, peca de **baja**.
- **Suma paquetes como si no compartieran viaje** (estilo $h^{\mathrm{add}}$). Un `drive` útil para dos se cuenta dos veces → peca de **alta**.
- Capacidad: parsea `c0`, `c1`, … y **no entra** en $h$.
- Inalcanzable (`BFS = \infty`) o paquete ausente: **suma 0** en vez de $\infty$. Un callejón sin salida parece barato. En `transport` conexo de IPC, poco probable.
- Distingue paquetes/furgonetas por el **nombre** (`p…` / `v…`). En IPC vale; es frágil.
- Grafo: si el PDDL solo pone `road` en un sentido, el código añade el inverso.
- BFS desde cero en cada paquete / cada nodo; en mapas grandes es lento, no incorrecto.

El paper permite $h$ no admisibles. GBFS solo necesita que **ordene**. Estas chapuzas no invalidan la candidata; invalidan tomarla como “km óptimos”.

---

## 6. Lectura para la memoria / el cuaderno

> Flash **sin thinking** produjo una $h$ de dominio ejecutable: caminos + pick/drop, $h(s_0)=3$ en `p01`, mismo plan y expansiones que $h^{\mathrm{FF}}$. Thinking **on** (default API) agotó 65 536 tokens de salida y no dejó fichero. Una candidata ≠ el protocolo de 25. Falta medarla en instancias donde `blind` ya falla (`easy-p10`, etc.).

Siguiente medida natural: la misma `testing/transport/easy-p10.pddl` de la tabla `hff` / `blind`, solo cambia `-H`.
