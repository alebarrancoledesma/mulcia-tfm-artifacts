kuroiwa cvrp -> NLM-cutplan -> Numeric FeedDownward


cvrp instances (cvrplib)
https://galgos.inf.puc-rio.br/cvrplib/index.php/en/instances



CVRPLIB / VRPLIB (.vrp)
“the standard format for the Capacitated Vehicle Routing Problem (CVRP)”
extensión de TSPLIB95
        ↓
formato benchmark habitual de CVRP
        ↓
Kuroiwa read_tsplib.py
        ↓
cvrp_to_pddl.py
        ↓
problem.pddl

pyperplan (motor de correa) no admite este tipo de pddl, solo soporta strips
esto es pddl 2.1 con planificación numérica


### Procesado por lotes

```powershell
cd mulcia-tfm-didp-models\cvrp
.\convert_vrp_to_pddl.ps1 C:\ruta\a\tu\carpeta
```


Numeric Fast Downward

repo
https://github.com/alebarrancoledesma/mulcia-tfm-numeric-fast-downward

utiliza A* no 

Linux como entorno natural del repo

```bash
sudo apt update
sudo apt install -y build-essential cmake git wget zlib1g-dev
```

antes de copilar NumericFD hay que compilar Bliss
```bash
cd src/search/bliss-0.73
make -j$(nproc)
```

para compilar NumericFD
```bash
uv run python build.py release64
```

## Primeras pruebas

CVRPLIB -> PDDL -> NumericFD  (basico)

```bash
uv run python fast-downward.py --build=release64 /mnt/c/Code/GitHub/TFM/data/cvrplib/domain.pddl /mnt/c/Code/GitHub/TFM/data/cvrplib/P/P-n16-k8.pddl --search "astar(blind())"
```

ERROR:

para el solver hace falta python 2.7 mandatory

```bash
cd mulcia-tfm-numeric-fast-downward

/usr/local/python2.7/bin/python2.7 -m pip install virtualenv
/usr/local/python2.7/bin/python2.7 -m virtualenv .venv27

source .venv27/bin/activate
```

cambiamos de estrategia a PlanForge

##PlanForge

https://github.com/mrlab-ai/PlanForge

creamos fork

vamos en linux (wsl)

Instalar Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

cargo build para compilar - sin problemas

primera prueba

```bash
./target/release/planforge --search 'astar(blind())' /mnt/c/Code/GitHub/TFM/data/cvrplib/domain.pddl /mnt/c/Code/GitHub/TFM/data/cvrplib/P/P-n16-k8.pddl
```

CORRECTA

---

### heurística admisible vs no admisible

admisible nunca sobreestima 

h(s) <= h*(s)

h*(s) = optimo real que falta

admisible
= optimista o exacta
= nunca dice que falta MÁS de lo que realmente falta

no admisible
= puede ser pesimista
= puede sobreestimar
= pierde garantía de optimalidad


Las heurísticas generadas por LLM probablemente serán no admisibles, el modelo puede inventar combinaciones de distancias, demanda, capacidad... que sobreestimen.

NOTA (complejidad de las heurísticas):
Aunque LM-Cut tarde muchísimo más calculando \(h(s)\) para cada estado, puede ganar porque evita explorar prácticamente todo el espacio.
