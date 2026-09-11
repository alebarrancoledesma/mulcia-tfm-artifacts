# Heurística generada por LLM para Transport (candidata 01)

Artefacto: `01 - transport-heuristic.py`. Una candidata; no hay selección entre un conjunto de ~25.

## Metadatos

| Ítem | Valor |
|---|---|
| Fecha | 2026-09-05 |
| Dominio | `transport` (IPC 2023 Learning, training suite) |
| Generador | `llm-heuristics.py`, prompt NeurIPS 2025 (sin ablación) |
| LLM | DeepSeek V4 Flash (`deepseek-v4-flash`) |
| Sampling | $T = 1.0$, $\mathrm{top}\text{-}p = 0.5$ |
| Thinking | desactivado |
| Clase | `TransportHeuristic` |
| Planificador (cuando se evalúe) | Pyperplan, GBFS `gbfs_early_goal_test` |

Entrada del prompt: `domain.pddl`, `p01.pddl`, `p99.pddl` y estados de ejemplo de la suite. El LLM no interviene durante la búsqueda. Cifras de coverage, longitud, expansiones y tiempo: hoja aparte.

**Generación fallida (misma configuración, thinking activo, esfuerzo por defecto `high`).** $11\,554$ tokens de prompt; $63\,788$ de razonamiento; $65\,536$ de salida (tope). Respuesta truncada; no se obtuvo código válido. Tiempo de pared $\approx 9$ min.

**Generación aceptada (thinking desactivado).** Código Python cerrado, importable por Pyperplan.

## Definición de $h$

Sea $d(\cdot,\cdot)$ la distancia más corta en el grafo dirigido de predicados `road` (BFS; cada arco $= 1$). Para cada paquete $p$ con destino $g_p$ que no está en $g_p$:

- si $p$ está en una localización $\ell$: $h_p = 2 + d(\ell, g_p)$ (carga, desplazamientos, descarga);
- si $p$ está en un vehículo en $\ell$: $h_p = 1 + d(\ell, g_p)$ (desplazamientos, descarga).

$$
h(s) = \sum_p h_p(s).
$$

$h(s) = 0$ si todos los paquetes del goal están en su destino. La capacidad se parsea y no entra en $h$. No se cuenta el desplazamiento del vehículo hasta el paquete. Los paquetes se tratan de forma independiente.

## Pros

- Interfaz correcta (`Heuristic`, `__init__(task)`, `__call__(node)`); código cerrado e importable.
- Usa el mapa (`road`) y distingue paquete en suelo vs. en vehículo.
- Familia alineada con heurísticas de Transport del trabajo base (caminos + carga/descarga), no planificación end-to-end.

## Contras

- No admisible: un mismo `drive` puede contarse una vez por paquete.
- Incompleta en el sentido de “ir a recoger”: subestima si el vehículo no está en $\ell$.
- Capacidad ignorada en el valor numérico.
- Estados sin camino a un goal: $h_p = 0$ en lugar de $\infty$.
- Identificación de objetos por prefijo de nombre (`p`, `v`); el grafo se trata como simétrico.
- BFS repetido por paquete y por nodo (coste, no sesgo).
- Una sola muestra de generación; thinking activo no es usable con el tope de salida observado ($2^{16}$ tokens).

## Nota de método

Una sola muestra de generación. El protocolo de Corrêa et al. (varias candidatas, selección en training, test ciego) no se ha ejecutado.
