## CORREA

### Básicamente

Heurística == brujula - cuanto falta mas o menos para decidir
h(s)

### Acciones que puede probar el planificador

- mover furgoneta
- cargar paquete
- descargar paquete

**Utiliza h para priorizar**

h alta - se deja esa opción para despues
h baja - prueba antes

es decir, prioriza busqueda usando h(s)  (s == state)

buscador usa GBFS (greedy best-first search). expande siempre con la h mas baja.

planificador -> Pyperplan

end-to-end == caca

### Qué hace el paper

- LLM genera unas 25 h(s) candidatas
- prueba con lote de problemas pequeños 5 min cada una ¿?
- se queda con la que mas problemas resuelve
- ganadora en problemas grandes

el repo solo genera 1 candidata cada vez que se ejecuta heuristics.py

### Para que sirve realmente h(s)

En verdad lo que hace es ordenar, no hace falta que sea perfecta

Nosotros nos limitamos a comparar

- blind
- h_ff
- llm_h(s)

## PDDL

Idioma para "juego" y "partida"

dominio (domain.pddl) e instancias (p01.pddl, p02.pddl...)

### Dominio

#### Cabecera

Definición. nombre y "requisitos" como que usa tipos.

#### Tipos

Vocabulario que se usara

#### Predicados

plantilla de hechos. pero con variables tipo ?l1 ?l2. despues la instancia generará tanto como quiera siguiendo un predicado concreto

#### Acciones 

lo que el planner puede hacer
en nuestro caso puede: drive, pickup, drop

### Instancia

#### Cabecera

definición y qué dominio usa

#### Objetos

los objetos que juegan en esta partida

#### Inicio (:init)

fotografía inicial


#### Goal

objetivo, lo que tiene que ser al final


### Instancias del proyecto

- training/p01: minima
- training/p10: partida un poco mas real
- testing/easy-p10: algo mas complejo, blind exhausted seguramente

El prompt del llm ve dominio + p01 + p99

### Ejecución

Ejecución solver:

```powershell
uv run src/pyperplan/pyperplan.py -s gbfs_early_goal_test -H blind benchmarks/ipc2023-learning/testing/transport/easy-p10.pddl
```

-H cambia entre blind y hff
va cambiando el archivo de entrada pddl segun la instancia

Ejecución generación h(s) por LLM:

```powershell
uv run llm-heuristics.py --framework deepseek --model deepseek-v4-flash --domain transport --heuristic-name TransportHeuristic --heuristic-file transport-heuristic.py
```

Con thinking primera ejecución ha truncado el codigo resultando en codigo inservible
thinking como parametro, por defecto off...

### Tesis (Fase 0, cómo decirlo)

Paper: 3 ligas. Nosotros solo B (mismo Pyperplan, GBFS): `blind` y $h^{\mathrm{FF}}$ vs $h$ LLM. No A (end-to-end) ni C (Fast Downward). Ahí se queda el experimento de `transport`.

No decir: “heurísticas competitivas” / “mejor que el SOTA” / “replicamos Corrêa”.

Sí:

> En Pyperplan + GBFS, **una** candidata DeepSeek V4 Flash (thinking off) se comparó con `blind` y $h^{\mathrm{FF}}$ sobre un recorte de `transport`. En instancias pequeñas es del orden de $h^{\mathrm{FF}}$ y claramente mejor que `blind`. En `easy-p20` reduce expansiones y longitud respecto a $h^{\mathrm{FF}}$. En `medium-p01`, $h^{\mathrm{FF}}$ no termina en el tiempo de corte y la $h$ del LLM sí. No se ha ejecutado el protocolo de ~25 candidatas ni Fast Downward.

“Competitiva” = con $h^{\mathrm{FF}}$ **de Pyperplan** en este recorte, no con FD ni con las 90 de test del paper.





