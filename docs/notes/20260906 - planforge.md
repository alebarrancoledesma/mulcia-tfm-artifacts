\## PlanForge



\### Objetivo

generar heurísticas externas y ejecutarlas





\### Mecanismo de heurísticas externas



nuevo crate



* copiar contenido de /tutorials/rust-plugin-library en /experiments/llm-cvrp-runner
* damos de alta en el Cargo.toml la carpeta en members



comando de compilación ahora



```bash

cargo build --release -p planforge-llm-cvrp

```



y ahora ya con el nuevo release se pueden utilizar las heuristicas custom externas. ejemplo:



```bash

./target/release/planforge-llm-cvrp --search 'astar(goalcount())' /mnt/c/Code/GitHub/TFM/data/cvrplib/domain.pddl /mnt/c/Code/GitHub/TFM/data/cvrplib/P/P-n16-k8.pddl

```





\### Diseño de heuristicas en PlanForge



Info estática
- demand(ci)

* travel-cost(ci,cj)
* capacity
* max-vehicles
* depot



Info dinámica

* loc
* visited(ci)
* load
* vehicles



Arquitectura



```

build\_llm\_cvrp(...)

│

├── encuentra IDs por nombre

├── precomputa demands

├── precomputa distance matrix

├── obtiene capacity

└── guarda todo en el struct

&#x20;         ↓

&#x20;    LlmCvrpHeuristic

&#x20;         ↓

compute\_heuristic(state)

│

├── lee loc actual

├── lee visited

├── lee load

├── lee vehicles

└── calcula h(s)

```





analizando hff heuristic salen cosas interesantes

* posibilidad de LLM genera h(s) + preferred actions


## Sentence

"La compilación de magnitudes numéricas como carga, demanda y capacidad a STRIPS introduce una expansión adicional, típicamente pseudo-polinómica en los valores numéricos y potencialmente muy grande en el número de acciones grounded."

“El procedimiento de generación se inspira en Corrêa et al., adaptando el contexto de prompting, la interfaz de código y el proceso de selección de heurísticas desde Pyperplan/STRIPS a PlanForge y planificación numérica aplicada al CVRP.”


"No evaluamos únicamente si un LLM puede generar una heurística, sino si puede generar una heurística especializada a partir de ejemplos de una distribución, evitando contaminación entre generación, selección y evaluación final, y midiendo su capacidad de generalización y transferencia."


"¿Puede un LLM utilizar ejemplos representativos de una distribución de instancias CVRP para sintetizar una función heurística de planificación especializada, y cuál es el compromiso entre especialización intra-distribución y capacidad de transferencia fuera de distribución?"


"¿Aporta la especialización condicionada por ejemplos una ventaja frente a una heurística LLM genérica cuando ambas se integran en el mismo planificador y estrategia de búsqueda?"


"The heuristic-generation prompt was designed following the general methodology of Corrêa et al., while adapting the heuristic objective, state-access interface, implementation language, and task representation to PlanForge and numeric classical planning."

