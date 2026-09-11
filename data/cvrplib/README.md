# Procedencia y caracterización de familias de instancias VRP de CVRPLIB

## 1. Procedencia de los principales conjuntos de instancias

La Tabla 1 resume la procedencia de varias de las familias de instancias más utilizadas en la literatura de *Vehicle Routing Problems* (VRP) y disponibles, total o parcialmente, a través de CVRPLIB. La clasificación se refiere a la **procedencia de los datos y al mecanismo de construcción de las instancias**, no a su dificultad computacional ni a su utilidad como benchmark.

**Tabla 1. Procedencia y naturaleza de familias de instancias de VRP.**

| Familia | Referencia original / principal | Variante y escala aproximada | Procedencia y mecanismo de construcción | Clasificación de procedencia | Implicación para la evaluación |
|---|---|---|---|---|---|
| **A (Augerat)** | Augerat et al. (1995) | CVRP; instancias pequeñas y medianas | Coordenadas generadas aleatoriamente sobre una cuadrícula bidimensional. Las demandas se obtienen de una distribución uniforme, con una fracción de demandas aumentadas para introducir heterogeneidad. | **Sintética** | Benchmark clásico adecuado para comparación histórica, pero con diversidad estructural limitada frente a conjuntos modernos. |
| **B (Augerat)** | Augerat et al. (1995) | CVRP; instancias pequeñas y medianas | Coordenadas construidas para formar varios *clusters* de clientes. Las demandas siguen esencialmente el mismo esquema artificial utilizado en A. | **Sintética estructurada** | Permite estudiar el efecto del *clustering*, aunque continúa siendo un conjunto generado artificialmente. |
| **P (Augerat)** | Augerat et al. (1995) | CVRP; instancias pequeñas y medianas | Reutiliza instancias existentes de las familias A, B y E, modificando principalmente la capacidad de los vehículos y, en consecuencia, el número de rutas requerido. | **Derivada / reparametrizada** | No debe considerarse estadísticamente independiente de A, B y E en diseños experimentales que separen entrenamiento y prueba. |
| **E (Christofides–Eilon y otras fuentes históricas)** | Christofides & Eilon (1969) y fuentes relacionadas | CVRP; benchmark clásico | Familia histórica heterogénea. La procedencia depende de la instancia: algunas configuraciones fueron generadas aleatoriamente, otras son modificaciones de instancias previas y para algunas no se documenta con precisión el proceso de generación. | **Mixta / histórica** | Conviene evitar una etiqueta global de “real” o “sintética”; su valor principal es la comparabilidad con literatura clásica. |
| **M (Christofides–Mingozzi–Toth)** | Christofides et al. (1979) | CVRP; hasta aproximadamente 200 clientes | Parte de las instancias agrupa clientes en *clusters* para representar situaciones prácticas; otras se obtienen combinando clientes y parámetros procedentes de instancias E o M anteriores. | **Sintética y derivada** | Existe dependencia explícita con E y dentro de la propia familia M, por lo que no constituye una fuente completamente independiente. |
| **F (Fisher)** | Fisher (1994) | CVRP; tres instancias clásicas | Incluye problemas procedentes de operaciones reales: distribución de National Grocers desde Peterborough, Ontario, y datos de Exxon asociados a distribución a estaciones de servicio. | **Real / basada en operaciones reales** | Aporta evidencia histórica de comportamiento sobre datos reales, aunque a una escala relativamente pequeña. |
| **CMT** | Christofides et al. (1979) | CVRP y CVRP con restricciones de duración | Reutiliza datos de varias instancias E y M bajo convenciones distintas de distancia y número de rutas; parte del conjunto añade límites de duración de ruta y tiempos de servicio. | **Derivada** | No debe tratarse como una fuente de datos independiente de E/M. Resulta especialmente útil para estudiar restricciones de duración. |
| **Taillard (tai)** | Rochat & Taillard (1995); Taillard (1993) | CVRP; 75–385 clientes | Las instancias de 75, 100 y 150 clientes son generadas artificialmente mediante distribuciones espaciales agrupadas y demandas con distribución exponencial. `tai385` se construyó a partir de información del cantón de Vaud, Suiza. | **Mixta: sintética + basada en datos reales** | Debe distinguirse `tai385` del resto de la familia cuando se analiza procedencia o realismo. |
| **Golden** | Golden et al. (1998) | CVRP / CVRP con duración; aproximadamente 200–483 clientes | Instancias diseñadas mediante patrones geométricos altamente estructurados, como círculos concéntricos, cuadrados, rayos o estrellas. | **Sintética geométrica** | Útil para medir rendimiento y dificultad algorítmica, pero con estructuras espaciales poco representativas de una distribución logística genérica. |
| **Li** | Li, Golden & Wasil (2005) | Principalmente CVRP con restricción de duración; aproximadamente 560–1,200 clientes | Extiende la filosofía de los problemas de gran escala de Golden mediante instancias artificiales de mayor tamaño y con simetría geométrica. | **Sintética geométrica** | Adecuada para estudiar escalabilidad histórica; no debe interpretarse como un conjunto de datos procedente de operaciones reales. |
| **X** | Uchoa et al. (2017) | CVRP; 100 instancias principales de 100–1,000 clientes | Generador sintético que varía sistemáticamente posición del depósito, distribución espacial de clientes, distribución de demandas y longitud media de las rutas. Fue diseñado para cubrir una diversidad mucho mayor que los benchmarks clásicos y evitar patrones excesivamente artificiales. | **Sintética diversificada** | Benchmark generalista de referencia. Es especialmente apropiado para comparar algoritmos bajo múltiples estructuras controladas. |
| **AGS** | Arnold, Gendreau & Sörensen (2019) | CVRP de muy gran escala; hasta 30,000 clientes | Instancias basadas en datos de demanda de distribución de paquetería en Bélgica y concebidas para reflejar problemas logísticos de gran escala. | **Basada en datos reales** | Muy relevante para analizar escalabilidad y transferencia hacia estructuras logísticas realistas de última milla. |
| **DIMACS 2021** | 12th DIMACS Implementation Challenge | CVRP; 12 instancias | Seis instancias de Loggi proceden de problemas reales en áreas metropolitanas brasileñas y emplean distancias de redes viarias; seis instancias de ORTEC derivan de un servicio real de distribución de alimentación en Estados Unidos y emplean tiempos reales de conducción. En ambos casos las matrices se simetrizaron para adaptarlas al benchmark. | **Derivada de operaciones reales** | Uno de los conjuntos más relevantes para evaluar validez externa, ya que preserva información de redes de transporte y operaciones reales, aunque adaptada al CVRP público. |
| **XML100** | Queiroga et al. (2022) | CVRP; 10,000 instancias de 100 clientes | Generado mediante un esquema estrechamente relacionado con el de X, combinando posiciones del depósito, patrones de clientes, distintas distribuciones de demanda y tamaños de ruta. El conjunto dispone de soluciones óptimas. | **Sintética diversificada** | Diseñado específicamente para evaluación de métodos basados en aprendizaje. Los autores recomiendan generar datos adicionales para entrenamiento y reservar las 10,000 instancias publicadas para prueba. |
| **XL** | Queiroga et al. (2026) | CVRP; 100 instancias de aproximadamente 1,000–10,000 clientes | Extensión a gran escala de los principios de generación empleados en X y XML, con variación sistemática de atributos estructurales. | **Sintética diversificada de gran escala** | Adecuada para evaluar escalabilidad y robustez en problemas grandes; no constituye evidencia independiente de transferencia a datos reales si el método se entrena con el mismo generador. |
| **Solomon** | Solomon (1987) | VRPTW; 100 clientes | Instancias generadas artificialmente en seis familias: clientes aleatorios (R), agrupados (C) y mixtos (RC), combinados con horizontes de planificación cortos o largos y diferentes características de ventanas temporales. | **Sintética estructurada** | Benchmark canónico de VRPTW. No es directamente comparable con CVRP puro cuando las ventanas temporales condicionan la factibilidad. |
| **Gehring–Homberger** | Gehring & Homberger (1999) | VRPTW; 200, 400, 600, 800 y 1,000 clientes | Extensión a mayor escala de la estructura experimental de Solomon, manteniendo las familias R, C y RC y las dos configuraciones principales de horizonte temporal. | **Sintética estructurada de gran escala** | Benchmark de referencia para escalabilidad en VRPTW; debe analizarse separadamente de los conjuntos CVRP. |

### Nota sobre la terminología

En esta tabla se distinguen cuatro categorías principales:

- **Sintética**: la información espacial, las demandas o ambas se generan mediante un procedimiento artificial.
- **Derivada**: una instancia reutiliza de forma sustancial datos de otra familia o modifica parámetros de un problema preexistente.
- **Basada en datos reales**: la construcción utiliza información procedente de una operación o contexto geográfico real, aunque pueda existir simplificación o anonimización.
- **Derivada de operaciones reales**: el benchmark conserva información operacional real, pero transforma ciertos elementos para ajustarse a una formulación pública y reproducible del problema.

Por tanto, la etiqueta *real-world* no debe interpretarse como que la instancia reproduce íntegramente el problema industrial original. Es habitual que el proceso de publicación elimine restricciones, anonimice localizaciones, agregue información o transforme matrices de costes para obtener una formulación CVRP estandarizada.

---

## 2. Dependencia entre familias de benchmarks

Una cuestión metodológica relevante es que las familias disponibles en CVRPLIB no constituyen necesariamente muestras independientes del espacio de problemas VRP. Parte de los benchmarks históricos se construyó reutilizando o transformando instancias anteriores.

El caso más claro es la familia **P**, cuyas instancias proceden de modificaciones de capacidad de problemas previamente incluidos en A, B y E. De forma similar, varias instancias **M** fueron construidas combinando clientes procedentes de problemas E o de otras instancias M. A su vez, las instancias **CMT** reutilizan directamente datos de problemas E y M, cambiando determinadas convenciones de cálculo o añadiendo restricciones de duración y tiempos de servicio.

En consecuencia, un protocolo experimental que utilice, por ejemplo, instancias E para ajustar un método y posteriormente presente resultados sobre CMT como una prueba completamente externa puede sobreestimar la capacidad de generalización. La separación entre conjuntos de desarrollo, validación y prueba debería realizarse atendiendo a la **genealogía de las instancias**, y no únicamente al nombre con el que aparecen agrupadas en el repositorio.

Esta observación es especialmente importante en métodos basados en aprendizaje automático, selección algorítmica, configuración automática de heurísticas o generación de componentes algorítmicos, donde la similitud estructural entre entrenamiento y prueba puede introducir *data leakage* o una estimación excesivamente optimista del rendimiento fuera de distribución.

---

## 3. Benchmarks sintéticos clásicos frente a benchmarks sintéticos modernos

Los conjuntos clásicos A, B, Golden o Li fueron fundamentales para establecer comparaciones reproducibles entre algoritmos, pero presentan una diversidad relativamente limitada. En particular, algunas familias fueron construidas alrededor de patrones geométricos o mecanismos de generación muy concretos.

Uchoa et al. (2017) introdujeron la familia **X** precisamente para resolver varias de estas limitaciones. Su generador combina de forma independiente diferentes posiciones del depósito, distribuciones espaciales de clientes, distribuciones de demanda y tamaños medios de ruta. El objetivo no es reproducir una empresa o red logística concreta, sino proporcionar una colección sintética que cubra un espectro amplio de características observables en aplicaciones reales.

Desde esta perspectiva, X debe entenderse como un benchmark de **diversidad controlada**. Sigue siendo sintético, pero permite evaluar de forma más sistemática cómo responde un algoritmo ante cambios estructurales del problema.

La misma filosofía continúa en **XML100** y **XL**. XML100 amplía enormemente el número de observaciones disponibles manteniendo un tamaño de 100 clientes y proporciona soluciones óptimas, lo que lo hace particularmente atractivo para la evaluación de enfoques de *machine learning*. XL extiende el esquema hacia instancias de miles de clientes para estudiar la escalabilidad de los métodos modernos.

No obstante, compartir principios de generación implica también compartir una distribución de problemas. Un buen rendimiento simultáneo sobre X, XML y XL proporciona evidencia de robustez dentro de una familia sintética amplia, pero no sustituye a una evaluación sobre datos procedentes de una distribución externa.

---

## 4. Instancias basadas en operaciones reales

Para analizar la transferencia hacia contextos operacionales son especialmente relevantes F, `tai385`, AGS y DIMACS.

La familia **F** es históricamente significativa porque incluye problemas construidos a partir de operaciones reales de distribución de National Grocers y Exxon. Su principal limitación actual es la escala, considerablemente menor que la de muchos problemas logísticos modernos.

La instancia **tai385** constituye una excepción dentro del conjunto Taillard, ya que fue construida a partir de información geográfica real del cantón de Vaud, mientras que las restantes instancias de la familia son sintéticas.

Las instancias **AGS** fueron desarrolladas específicamente para estudiar problemas de muy gran escala y se basan en información de demanda de distribución de paquetería en Bélgica. Por ello resultan particularmente útiles cuando se desea evaluar si un método mantiene su eficiencia con varios miles o decenas de miles de clientes.

Las doce instancias incorporadas para el **DIMACS Implementation Challenge** ofrecen una forma adicional de evaluar validez externa. Las seis instancias de Loggi derivan de datos de varias áreas metropolitanas de Brasil y utilizan distancias procedentes de redes viarias reales. Las seis instancias de ORTEC derivan de un servicio real de distribución de alimentación en Estados Unidos y emplean tiempos de conducción. Estas matrices fueron simetrizadas para producir instancias compatibles con el CVRP utilizado en la competición, por lo que siguen siendo una representación simplificada del problema operacional original.

En términos experimentales, AGS y DIMACS proporcionan una evidencia de naturaleza distinta a X/XML/XL: los primeros permiten estudiar comportamiento sobre estructuras derivadas de operaciones reales, mientras que los segundos proporcionan un entorno sintético controlado y reproducible.

---

## 5. Implicaciones para el diseño experimental

La selección de benchmarks debería depender del tipo de afirmación que se desea sostener. Evaluar únicamente sobre un conjunto clásico permite comparar con trabajos anteriores, pero no es suficiente para demostrar generalización estructural, escalabilidad y transferencia a problemas reales de forma simultánea.

Una estrategia razonable es separar la evaluación en varios niveles:

1. **Comparabilidad histórica.**  
   Utilizar familias clásicas como A, B, E, M, P, Taillard o Golden permite contrastar el método con una parte importante de la literatura previa. Debe tenerse en cuenta la dependencia entre algunas de estas familias.

2. **Generalización estructural sintética.**  
   Utilizar **X** permite evaluar el algoritmo frente a un conjunto más diverso de configuraciones espaciales y de demanda. Para estudios con aprendizaje automático, **XML100** proporciona un benchmark especialmente útil debido a su tamaño y a la disponibilidad de soluciones óptimas.

3. **Escalabilidad.**  
   **XL** y **AGS** permiten estudiar el comportamiento con miles o decenas de miles de clientes. XL ofrece diversidad sintética controlada, mientras que AGS aporta una estructura basada en demanda logística real.

4. **Validez externa.**  
   **DIMACS** y **AGS** son particularmente adecuados para investigar si el rendimiento observado en benchmarks sintéticos se mantiene sobre instancias derivadas de operaciones reales. F y `tai385` pueden complementar este análisis como referencias históricas.

5. **Evaluación de variantes.**  
   Solomon y Gehring–Homberger pertenecen al **VRPTW**, no al CVRP puro. Deben emplearse cuando el método modela explícitamente ventanas temporales y sus resultados no deberían agregarse indiscriminadamente con los obtenidos en CVRP.

---

## 6. Síntesis

Las familias de CVRPLIB no deberían considerarse un conjunto homogéneo de instancias intercambiables. Existen diferencias relevantes tanto en su procedencia como en la finalidad con la que fueron diseñadas.

Los benchmarks clásicos A, B, E, M, P y CMT son esenciales para la comparabilidad histórica, pero presentan relaciones de dependencia que deben tenerse en cuenta. Golden y Li son principalmente benchmarks sintéticos de gran escala con fuerte estructura geométrica. X, XML y XL representan una generación posterior de benchmarks sintéticos diseñados para proporcionar mayor diversidad y una evaluación estadística más sólida. Por su parte, F, `tai385`, AGS y DIMACS introducen distintos grados de conexión con operaciones reales.

Por ello, una evaluación metodológicamente sólida debería combinar **comparabilidad histórica, diversidad sintética, escalabilidad y validez externa**, evitando interpretar el rendimiento sobre una única familia como evidencia suficiente de generalización general a problemas de routing reales.

---

## Referencias

- Arnold, F., Gendreau, M., & Sörensen, K. (2019). *Efficiently solving very large-scale routing problems*. **Computers & Operations Research, 107**, 32–42. https://doi.org/10.1016/j.cor.2019.03.006
- Augerat, P., Belenguer, J. M., Benavent, E., Corberán, A., Naddef, D., & Rinaldi, G. (1995). *Computational results with a branch and cut code for the capacitated vehicle routing problem*. Technical report.
- Christofides, N., & Eilon, S. (1969). *An algorithm for the vehicle-dispatching problem*. **Operational Research Quarterly, 20**(3), 309–318. https://doi.org/10.1057/jors.1969.75
- Christofides, N., Mingozzi, A., & Toth, P. (1979). *The vehicle routing problem*. In N. Christofides, A. Mingozzi, P. Toth, & C. Sandi (Eds.), **Combinatorial Optimization**.
- Fisher, M. L. (1994). *Optimal solution of vehicle routing problems using minimum K-trees*. **Operations Research, 42**(4), 626–642. https://doi.org/10.1287/opre.42.4.626
- Gehring, H., & Homberger, J. (1999). *A parallel hybrid evolutionary metaheuristic for the vehicle routing problem with time windows*. Proceedings of MIC'99.
- Golden, B. L., Wasil, E. A., Kelly, J. P., & Chao, I.-M. (1998). *The impact of metaheuristics on solving the vehicle routing problem: Algorithms, problem sets, and computational results*. In T. G. Crainic & G. Laporte (Eds.), **Fleet Management and Logistics**, 33–56. Kluwer.
- Li, F., Golden, B. L., & Wasil, E. A. (2005). *Very large-scale vehicle routing: New test problems, algorithms, and results*. **Computers & Operations Research, 32**(5), 1165–1179. https://doi.org/10.1016/j.cor.2003.10.002
- Queiroga, E., Sadykov, R., Uchoa, E., & Vidal, T. (2022). *10,000 optimal CVRP solutions for testing machine learning based heuristics*. https://openreview.net/forum?id=yHiMXKN6nTl
- Queiroga, E., Martinelli, R., Subramanian, A., Uchoa, E., & Vidal, T. (2026). *The XL Instances for the Capacitated Vehicle Routing Problem*. arXiv:2601.11467.
- Rochat, Y., & Taillard, É. D. (1995). *Probabilistic diversification and intensification in local search for vehicle routing*. **Journal of Heuristics, 1**(1), 147–167. https://doi.org/10.1007/BF02430370
- Solomon, M. M. (1987). *Algorithms for the vehicle routing and scheduling problems with time window constraints*. **Operations Research, 35**(2), 254–265. https://doi.org/10.1287/opre.35.2.254
- Uchoa, E., Pecin, D., Pessoa, A., Poggi, M., Vidal, T., & Subramanian, A. (2017). *New benchmark instances for the Capacitated Vehicle Routing Problem*. **European Journal of Operational Research, 257**(3), 845–858. https://doi.org/10.1016/j.ejor.2016.08.012
- DIMACS (2021–2022). *12th DIMACS Implementation Challenge: Vehicle Routing*. Competition documentation and CVRP instance descriptions. https://dimacs.rutgers.edu/programs/implementation-challenges/vehicle-routing/
- CVRPLIB. *Capacitated Vehicle Routing Problem Library*. https://galgos.inf.puc-rio.br/cvrplib/
