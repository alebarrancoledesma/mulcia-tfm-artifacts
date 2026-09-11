# Diseño experimental propuesto: heurísticas LLM especializadas por familia de instancias CVRP

## 1. Idea central

El objetivo no será obligar al LLM a generar una única función heurística $h(s)$ “universal” capaz de rendir igual de bien sobre cualquier instancia CVRP imaginable.

La hipótesis más interesante para este TFM es que un LLM puede **diseñar heurísticas de búsqueda condicionadas por una distribución o familia concreta de problemas**, aprovechando ejemplos representativos de esa familia para generar código heurístico adaptado a sus regularidades estructurales.

La idea general es:

```text
familia / distribución de instancias
            ↓
ejemplos representativos en el prompt
            ↓
            LLM
            ↓
genera una heurística h_F(s)
especializada en esa familia
            ↓
evaluación sobre instancias NO vistas
de la misma familia
            ↓
evaluación cruzada sobre otras familias
```

Por tanto, la cuestión principal deja de ser únicamente:

> ¿Puede un LLM generar una heurística válida para CVRP?

y pasa a ser también:

> ¿Puede un LLM generar una heurística especializada para una distribución concreta de instancias CVRP y, si lo hace, cuánto mejora dentro de esa distribución y cuánto pierde al transferirse a otra?

Esto introduce de forma natural los conceptos de **especialización**, **generalización intra-distribución**, **transferencia fuera de distribución** y **robustez**.

---

## 2. Por qué esta idea tiene más sentido que una única heurística universal

Si al LLM solo se le proporciona:

- el dominio CVRP;
- la interfaz de PlanForge;
- la definición general del problema;

entonces el modelo tratará de diseñar una heurística genérica para CVRP.

Eso sigue siendo válido, pero desaprovecha una capacidad especialmente interesante de los LLM: utilizar contexto y ejemplos concretos para adaptar el diseño algorítmico a una distribución de problemas.

Una situación más realista sería la siguiente:

```text
una empresa / operación logística
        ↓
genera repetidamente problemas
con características parecidas
        ↓
se proporcionan algunos ejemplos
representativos al LLM
        ↓
el LLM diseña un módulo heurístico
especializado en ese tipo de problema
```

El código generado no tendría que memorizar instancias específicas. Debe seguir siendo una heurística generalizable y reutilizable, pero puede estar **sesgada deliberadamente hacia las regularidades de la familia observada**.

Conceptualmente, el proceso puede verse como:

$$
\text{características de una distribución de problemas}
\rightarrow
\text{LLM}
\rightarrow
\text{diseño algorítmico}
$$

No se entrenan los pesos del LLM. El modelo realiza **algorithm synthesis conditioned on examples**: los ejemplos forman parte del contexto de generación del algoritmo.

---

## 3. Familia A y familia B de Augerat como experimento principal

Una primera configuración especialmente atractiva consiste en utilizar las familias **A** y **B** de Augerat.

### Familia A

Las instancias A presentan una distribución espacial fundamentalmente aleatoria de clientes y demandas sintéticas.

### Familia B

Las instancias B están diseñadas con una estructura espacial más agrupada, formando *clusters* de clientes.

Esto proporciona dos distribuciones que:

- pertenecen al mismo problema base, CVRP;
- comparten muchas características generales;
- son comparables;
- presentan una diferencia estructural clara en la geometría de los clientes.

Esto permite generar:

$$
h_A(s)
$$

una heurística generada a partir de ejemplos de la familia A,

y:

$$
h_B(s)
$$

una heurística generada a partir de ejemplos de la familia B.

También se puede generar:

$$
h_G(s)
$$

una heurística **genérica**, sin ejemplos específicos de A o B, que sirva como baseline de especialización.

---

## 4. Diseño experimental principal

El experimento puede organizarse como una evaluación cruzada.

```text
                      TEST A       TEST B
                    ─────────     ─────────
h_A  (prompt A)         ✓             ✓

h_B  (prompt B)         ✓             ✓

h_G  (genérica)         ✓             ✓
```

Esto permite responder simultáneamente a varias preguntas.

### Rendimiento intra-distribución

$$
h_A \rightarrow A
$$

y

$$
h_B \rightarrow B
$$

miden si una heurística especializada funciona bien sobre nuevas instancias de la distribución que vio durante la generación.

### Transferencia fuera de distribución

$$
h_A \rightarrow B
$$

y

$$
h_B \rightarrow A
$$

miden cuánto se conserva el rendimiento cuando la heurística se aplica a una familia estructuralmente distinta.

### Valor de la especialización

La comparación:

$$
h_A \text{ vs } h_G \quad \text{sobre A}
$$

y:

$$
h_B \text{ vs } h_G \quad \text{sobre B}
$$

permite medir si proporcionar ejemplos de la familia al LLM genera una ventaja real frente a pedir una heurística CVRP genérica.

---

## 5. Qué resultados serían interesantes

No existe un único resultado “correcto”. Varias posibilidades serían científicamente interesantes.

### Caso 1: especialización clara

```text
h_A:
muy buena en A
peor en B

h_B:
muy buena en B
peor en A

h_G:
rendimiento intermedio en ambas
```

Esto apoyaría la hipótesis de que el LLM puede generar heurísticas especializadas que explotan propiedades de una distribución concreta, a costa de cierta capacidad de transferencia.

### Caso 2: especialización sin pérdida importante de transferencia

```text
h_A:
muy buena en A
también buena en B
```

Esto sugeriría que el LLM ha descubierto principios heurísticos más generales de CVRP a partir de ejemplos concretos.

### Caso 3: los ejemplos no ayudan

```text
h_A ≈ h_B ≈ h_G
```

Esto indicaría que la información específica de familia no está aportando una mejora significativa, o que el LLM no está utilizando correctamente esas regularidades.

### Caso 4: especialización perjudicial

```text
h_A < h_G en A
```

También sería un resultado válido: la especialización mediante ejemplos podría inducir sobreajuste algorítmico o estrategias demasiado particulares.

---

## 6. No utilizar un split aleatorio clásico 70/15/15

No se recomienda mezclar todas las instancias disponibles y realizar posteriormente un split aleatorio tipo:

```text
70 % train
15 % validation
15 % test
```

Hay dos razones principales.

### 6.1. No estamos entrenando los pesos de un modelo

En este trabajo, “train” no significa entrenamiento paramétrico del LLM.

El proceso real es:

```text
ejemplos en prompt
        ↓
generación de código
        ↓
selección de candidatos
        ↓
evaluación final
```

Por ello, una terminología más precisa sería:

```text
PROMPT / GENERATION
DEV / SELECTION
FINAL TEST
```

### 6.2. Las familias de CVRPLIB no son necesariamente independientes

Algunas familias reutilizan o modifican otras instancias.

Por ejemplo, la familia **P** de Augerat deriva en gran medida de instancias de A, B y E modificando parámetros como la capacidad y, en consecuencia, el número de rutas.

Por tanto, no sería metodológicamente limpio hacer:

```text
A / B / E → generación o selección
P         → test "externo"
```

y presentar P como una distribución completamente independiente.

La partición debe hacerse teniendo en cuenta la **genealogía y el mecanismo de generación de las instancias**, no únicamente el nombre de la carpeta o benchmark.

---

## 7. Split recomendado dentro de cada familia

Para cada familia $F$, se propone separar las instancias en tres subconjuntos.

### F-PROMPT

Pequeño conjunto de instancias representativas que el LLM puede ver directamente durante la generación.

Ejemplo:

```text
A-PROMPT
2–4 instancias A
```

Estas instancias forman parte del contexto del LLM.

### F-DEV

Instancias de la misma familia que **no aparecen en el prompt** y que se utilizan para seleccionar entre varias heurísticas generadas.

Ejemplo:

```text
A-DEV
5–8 instancias A
```

### F-TEST

Instancias que no se utilizan ni durante la generación ni durante la selección.

Ejemplo:

```text
A-TEST
resto de instancias A disponibles
```

Estas instancias deben permanecer completamente vírgenes hasta que se congele la heurística ganadora.

---

## 8. Pipeline completo para una familia

Para la familia A:

```text
A-PROMPT
   ↓
LLM genera N candidatos

h_A1
h_A2
h_A3
h_A4
h_A5
   ↓
A-DEV
   ↓
ranking
   ↓
selección de h_A*
   ↓
CONGELACIÓN DEL CÓDIGO
   ↓
A-TEST
   ↓
rendimiento intra-distribución
   ↓
B-TEST
   ↓
transferencia fuera de distribución
```

Exactamente el mismo procedimiento se repetiría para B:

```text
B-PROMPT
   ↓
LLM genera N candidatos
   ↓
B-DEV
   ↓
selección de h_B*
   ↓
congelación
   ↓
B-TEST
   ↓
A-TEST
```

---

## 9. Experimento genérico de control

Además de $h_A$ y $h_B$, conviene generar una heurística genérica:

$$
h_G
$$

El prompt genérico incluiría:

- definición del dominio CVRP;
- `domain.pddl`;
- explicación semántica del problema;
- interfaz de PlanForge;
- plantilla Rust;
- información general sobre los estados, acciones y costes;

pero **sin mostrar instancias específicas de las familias A o B**.

Después:

```text
h_G → A-TEST
h_G → B-TEST
```

Esto es fundamental para saber si los ejemplos de familia realmente están aportando valor.

Sin $h_G$, observar que $h_A$ funciona bien sobre A no permite separar fácilmente:

```text
"es una buena heurística CVRP"
```

de:

```text
"es una buena heurística específicamente gracias
a haber visto ejemplos de A"
```

---

## 10. Qué debe recibir el LLM en el experimento especializado

Para generar $h_A$, el prompt podría contener:

```text
1. Objetivo experimental
2. Descripción del CVRP
3. domain.pddl completo
4. 2–4 problem.pddl representativos de A
5. Un estado intermedio representativo
6. API relevante de PlanForge
7. Plantilla Rust funcional
8. Restricciones de generalización
9. Instrucción para devolver código Rust completo
```

Para $h_B$, exactamente el mismo procedimiento cambiando únicamente las instancias representativas.

Esto mantiene controladas las variables del experimento.

---

## 11. Qué NO debería recibir el LLM en el experimento base

No se deberían proporcionar inicialmente:

- rutas óptimas;
- soluciones completas;
- Best Known Solutions como objetivo de aprendizaje;
- código de una heurística ganadora anterior;
- resultados sobre DEV;
- información de TEST;
- IDs concretos de variables internas de PlanForge;
- nombres concretos de clientes que puedan inducir hardcoding.

En particular, evitaría proporcionar al LLM:

```text
optimal route = ...
optimal cost = ...
```

porque eso cambiaría la pregunta de investigación.

El experimento dejaría de ser simplemente:

> generar una heurística a partir de la estructura de una distribución

y empezaría a parecerse a:

> diseñar una heurística usando ejemplos etiquetados con soluciones óptimas.

Ese segundo caso también podría estudiarse posteriormente como una variante *few-shot* supervisada, pero no debería mezclarse con el experimento base.

---

## 12. Restricciones de generalización del código generado

Aunque una heurística esté especializada en una familia, no puede memorizar las instancias concretas del prompt.

El código generado NO debe contener:

- nombres concretos como `c7`, `c14`, etc.;
- IDs numéricos internos de variables;
- número fijo de clientes;
- capacidad fija;
- número fijo de vehículos;
- distancias hardcodeadas;
- demandas específicas copiadas del prompt.

La especialización debe emerger de una **estrategia algorítmica**, no de memorizar datos.

Por ejemplo, sí sería válido que el LLM dedujera que una determinada estructura espacial favorece una combinación de:

```text
distancia al cliente más cercano
+
estimación de retorno al depósito
+
clientes pendientes
+
penalización por carga / capacidad
```

siempre que el algoritmo calcule esas cantidades dinámicamente para cualquier instancia.

---

## 13. Número inicial de candidatos

Una configuración razonable para la primera versión del experimento sería:

$$
N = 5
$$

heurísticas generadas por condición.

Por ejemplo:

```text
Prompt A
↓
h_A1 ... h_A5

Prompt B
↓
h_B1 ... h_B5

Prompt Generic
↓
h_G1 ... h_G5
```

Todas deben generarse bajo las mismas condiciones:

- mismo modelo;
- mismo nivel de razonamiento;
- mismos parámetros;
- misma plantilla;
- mismo contexto técnico;
- mismo número de candidatos.

La única diferencia entre A y B debe ser la información específica de la familia.

---

## 14. Ranking en DEV

Los candidatos no se seleccionan por una única instancia.

Cada candidato debe ejecutarse sobre el conjunto DEV completo de su condición.

Posibles métricas:

- porcentaje de instancias resueltas;
- número de *timeouts*;
- tiempo de búsqueda;
- tiempo total;
- estados expandidos;
- estados generados;
- evaluaciones heurísticas;
- coste de la solución;
- longitud del plan;
- gap respecto al BKS cuando esté disponible;
- coste temporal medio de evaluar $h(s)$.

Una política de ranking razonable podría priorizar:

```text
1. coverage / solved
2. menos timeouts
3. menos expansiones
4. menor runtime
5. calidad del plan / gap
```

El procedimiento exacto debe fijarse antes de mirar los resultados finales.

Una vez seleccionado el ganador en DEV:

```text
h_A*
```

su código queda congelado.

No se modifica después de observar A-TEST ni B-TEST.

---

## 15. Búsqueda fija para comparar heurísticas

Para comparar correctamente heurísticas:

```text
A* + h1
A* + h2
A* + h3
```

o:

```text
GBFS + h1
GBFS + h2
GBFS + h3
```

No se deben comparar directamente:

```text
A* + LM-Cut
vs
GBFS + h_LLM
```

y atribuir la diferencia exclusivamente a la heurística, porque también ha cambiado la estrategia de búsqueda.

El experimento principal debe fijar el algoritmo de búsqueda.

Después puede añadirse una segunda dimensión experimental comparando A* y GBFS.

---

## 16. Baselines clásicos

Cada conjunto TEST debería ejecutarse también con heurísticas clásicas disponibles en PlanForge.

Candidatos:

```text
blind
FF
Numeric LM-Cut
```

teniendo en cuenta sus propiedades y costes.

Esto permite comparar:

```text
PlanForge + heurística clásica
vs
PlanForge + heurística LLM genérica
vs
PlanForge + heurística LLM especializada
```

La comparación con un solver CVRP especializado puede añadirse como contextualización, pero no sustituye esta evaluación porque el objetivo principal del trabajo sigue siendo estudiar heurísticas dentro de un sistema de planificación.

---

## 17. Matriz experimental final recomendada

Una tabla conceptual del experimento principal:

| Heurística | Información usada para generarla | A-TEST | B-TEST |
|---|---|---:|---:|
| `h_G*` | CVRP genérico | ✓ | ✓ |
| `h_A*` | ejemplos A | ✓ | ✓ |
| `h_B*` | ejemplos B | ✓ | ✓ |
| FF | ninguna generación LLM | ✓ | ✓ |
| LM-Cut | ninguna generación LLM | ✓ | ✓ |
| Blind | ninguna generación LLM | ✓ | ✓ |

Con esto pueden analizarse:

### Especialización A

$$
h_A^* - h_G^*
\quad \text{sobre A}
$$

### Especialización B

$$
h_B^* - h_G^*
\quad \text{sobre B}
$$

### Transferencia A → B

$$
h_A^*
\quad \text{sobre B}
$$

### Transferencia B → A

$$
h_B^*
\quad \text{sobre A}
$$

### Comparación con heurísticas tradicionales

$$
h_A^*,h_B^*,h_G^*
\quad \text{vs}
\quad
FF,\ LM\text{-}Cut,\ Blind
$$

---

## 18. Extensión posterior: más familias

Si el pipeline A/B funciona, el diseño puede ampliarse.

Posibles familias:

- X, por diversidad sintética;
- F, por procedencia real histórica;
- `tai385`, como caso particular basado en datos geográficos reales;
- DIMACS, por estar derivado de operaciones reales.

Sin embargo, el tamaño de las instancias debe adaptarse a las capacidades de PlanForge.

No tendría sentido seleccionar un benchmark excelente desde la perspectiva del routing si las búsquedas duran horas y no permiten suficientes repeticiones experimentales.

El objetivo es obtener suficiente número de observaciones para comparar heurísticas de forma razonable.

Por ello, el primer experimento debería centrarse en instancias pequeñas/medianas que PlanForge pueda resolver repetidamente.

---

## 19. Papel de la familia P de Augerat

La familia P no debe tratarse como una familia externa completamente independiente de A y B.

P reutiliza de forma importante instancias procedentes de A, B y E y modifica principalmente parámetros como la capacidad.

Por tanto:

```text
A/B/E usados para generación o DEV
+
P usado como "OOD completamente independiente"
```

sería una afirmación excesiva.

P sí puede utilizarse para:

- ingeniería;
- pruebas de integración;
- *smoke tests*;
- estudiar sensibilidad a cambios de capacidad;
- experimentos de transferencia relacionados.

En particular, la instancia:

```text
P-n16-k8
```

que ya se ha utilizado extensamente durante el desarrollo de la integración PlanForge debería considerarse:

```text
ENGINEERING / SMOKE TEST
```

y excluirse de cualquier conjunto FINAL que se presente como totalmente no visto.

---

## 20. Diferencia entre generalización y universalidad

Una heurística no necesita ser universal para poder decir que generaliza.

Si el LLM ve:

```text
A-PROMPT
```

y después la misma heurística, sin modificar código, funciona sobre:

```text
A-TEST
```

entonces existe **generalización a nuevas instancias dentro de la misma distribución**.

Posteriormente:

```text
h_A → B-TEST
```

mide **generalización fuera de distribución**.

Por tanto pueden distinguirse dos niveles:

$$
\text{Generalización ID}
$$

y:

$$
\text{Generalización OOD}
$$

Esta distinción es más informativa que exigir desde el principio una única heurística universal.

---

## 21. Posible pregunta de investigación

Una formulación especialmente adecuada sería:

> **¿Puede un LLM generar heurísticas de planificación especializadas a partir de ejemplos representativos de una familia de instancias CVRP, y qué relación existe entre el rendimiento obtenido dentro de dicha distribución y su capacidad de transferencia a distribuciones estructuralmente diferentes?**

Subpreguntas:

1. ¿Las heurísticas condicionadas por ejemplos de una familia superan a una heurística LLM genérica en esa misma familia?
2. ¿Cuánto rendimiento pierden al aplicarse a una familia diferente?
3. ¿Las heurísticas generadas capturan propiedades generales del CVRP o características específicas de la distribución mostrada?
4. ¿Cómo se comparan con heurísticas clásicas de planificación?
5. ¿Qué coste computacional introduce la heurística generada?
6. ¿Son interpretables las estrategias algorítmicas generadas?
7. ¿Qué características de las instancias parecen favorecer o perjudicar a cada heurística?

---

## 22. Hipótesis experimentales posibles

### H1 — Valor de la especialización

> Una heurística generada utilizando ejemplos representativos de una familia obtendrá mejor rendimiento medio sobre nuevas instancias de esa familia que una heurística generada únicamente con información genérica del CVRP.

### H2 — Coste de transferencia

> La ventaja obtenida mediante especialización disminuirá al evaluar la heurística sobre una familia con características estructurales diferentes.

### H3 — Generalización parcial

> Las heurísticas especializadas conservarán parte de su utilidad fuera de distribución si el LLM ha capturado propiedades algorítmicas generales del CVRP y no únicamente características particulares de las instancias de contexto.

No es necesario que las hipótesis se confirmen. Su rechazo también constituye un resultado.

---

## 23. Interpretabilidad / XAI

Una vez estabilizado el pipeline principal, cada candidato generado puede guardar metadatos como:

```json
{
  "features_used": [
    "...",
    "..."
  ],
  "intuition": "...",
  "expected_strengths": [
    "..."
  ],
  "expected_weaknesses": [
    "..."
  ]
}
```

No se trataría de solicitar ni almacenar *chain-of-thought*.

El objetivo sería comparar:

```text
explicación declarada
        vs
código generado
        vs
comportamiento experimental
```

Por ejemplo:

- el LLM afirma que la heurística explota clustering;
- se inspecciona si el código realmente utiliza relaciones espaciales;
- se comprueba si mejora especialmente en B;
- se observa qué ocurre al pasar a A.

Esto conecta directamente especialización, generalización e interpretabilidad.

---

## 24. Reproducibilidad

Cada ejecución de generación debe almacenar como mínimo:

```text
experiment_id
modelo
versión / endpoint
parámetros
nivel de razonamiento
timestamp
prompt exacto
domain.pddl
instancias incluidas en el prompt
plantilla Rust
salida cruda del LLM
código generado
errores de compilación
logs de PlanForge
resultados DEV
ranking
heurística ganadora
resultados TEST
```

El código generado debe conservarse **sin editar manualmente**.

Si un candidato no compila, debe registrarse como fallo de generación, no corregirse silenciosamente antes de compararlo con los demás.

---

## 25. Diseño mínimo viable recomendado

Para empezar sin sobredimensionar el experimento:

```text
FAMILIA A
─────────
A-PROMPT: 2–3 instancias
A-DEV:    5–8 instancias
A-TEST:   resto seleccionado

FAMILIA B
─────────
B-PROMPT: 2–3 instancias
B-DEV:    5–8 instancias
B-TEST:   resto seleccionado

GENÉRICO
────────
sin instancias A/B específicas

CANDIDATOS
──────────
N = 5 por condición
```

Generaciones:

```text
5 candidatos genéricos
5 candidatos especializados en A
5 candidatos especializados en B
```

Selección:

```text
h_G* mediante DEV conjunto o DEV neutro definido previamente
h_A* mediante A-DEV
h_B* mediante B-DEV
```

Evaluación final:

```text
h_G* → A-TEST + B-TEST
h_A* → A-TEST + B-TEST
h_B* → A-TEST + B-TEST

FF     → A-TEST + B-TEST
LM-Cut → A-TEST + B-TEST
Blind  → A-TEST + B-TEST
```

---

## 26. Decisión metodológica propuesta

La decisión que se propone congelar es:

> **El experimento principal no buscará únicamente una heurística LLM universal para CVRP. Se estudiará explícitamente la capacidad del LLM para generar heurísticas condicionadas por ejemplos representativos de distintas familias de instancias, evaluando tanto su especialización intra-distribución como su transferencia fuera de distribución.**

La heurística generada seguirá siendo código generalizable y no podrá memorizar instancias concretas.

La especialización debe producirse en el **diseño de la estrategia heurística**, no mediante *hardcoding*.

---

## 27. Narrativa para la memoria del TFM

Una posible redacción:

> En lugar de considerar la generación de una única heurística universal para todas las instancias CVRP, se estudia también un escenario de especialización condicionada por distribución. Para ello, el LLM recibe ejemplos representativos de una familia concreta de instancias y genera un módulo heurístico reutilizable sobre nuevas instancias de dicha familia. Los candidatos se seleccionan utilizando un conjunto de desarrollo independiente y la heurística resultante se congela antes de su evaluación final. Posteriormente se realiza una evaluación cruzada sobre familias estructuralmente distintas, permitiendo analizar el compromiso entre especialización y capacidad de transferencia. Este diseño permite estudiar si los LLMs actúan únicamente como generadores de heurísticas generales o si pueden aprovechar regularidades de una distribución de problemas para sintetizar estrategias algorítmicas adaptadas a ella.

---

## 28. Resumen visual

```text
                         CVRP
                          │
              ┌───────────┼───────────┐
              │           │           │
         prompt gen.   prompt A    prompt B
              │           │           │
             LLM         LLM         LLM
              │           │           │
            h_G*        h_A*        h_B*
              │           │           │
              └──────┬────┴────┬──────┘
                     │         │
                  A-TEST     B-TEST
                     │         │
                     └────┬────┘
                          │
                  evaluación cruzada
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
 especialización     transferencia     generalización
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                comparación clásica
                          │
                 FF / LM-Cut / Blind
                          │
                robustez + coste + XAI
```

---

## 29. Referencias de apoyo para el diseño de familias

- Augerat, P., Belenguer, J. M., Benavent, E., Corberán, A., Naddef, D., & Rinaldi, G. (1995). *Computational results with a branch and cut code for the capacitated vehicle routing problem*.
- Uchoa, E., Pecin, D., Pessoa, A., Poggi, M., Vidal, T., & Subramanian, A. (2017). *New benchmark instances for the Capacitated Vehicle Routing Problem*. European Journal of Operational Research, 257(3), 845–858.
- CVRPLIB. *Capacitated Vehicle Routing Problem Library*.

La selección definitiva de instancias concretas de A y B deberá realizarse después de un pequeño estudio de escalabilidad con PlanForge, de modo que los tamaños elegidos permitan ejecutar de forma repetible todos los candidatos y baselines dentro de los límites temporales del TFM.
