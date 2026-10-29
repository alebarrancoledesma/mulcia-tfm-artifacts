# Entradas de planificación clásica

La reproducción metodológica utiliza el dominio `Transport` y los problemas de entrenamiento y prueba del fork `llm-generated-heuristics-vrp`, que conserva la estructura de Corrêa et al. La adaptación posterior utiliza en ese mismo fork el dominio y los problemas propios `CVRP-STRIPS`.

```text
llm-generated-heuristics-vrp/benchmarks/
├── ipc2023-learning/{training,testing}/transport/
└── cvrp-strips/{training,testing}/
```

No se duplican aquí para mantener la procedencia y la relación directa con el código de Pyperplan que los ejecuta. Los resultados de ambas etapas sí se conservan en `outputs/01-classical-planning/`.
