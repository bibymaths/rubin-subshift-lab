## Best biological applications

| Data/application                        | Useful parts                                                              |
| --------------------------------------- | ------------------------------------------------------------------------- |
| Drug-response phosphoproteomics         | Subshifts, attractors, irreversibility, reconstruction signatures         |
| Kinase/signalling activity time courses | Allowed transitions, forbidden temporal motifs, state convergence         |
| Circadian or cell-cycle data            | Periodic points, least periods, shift groups and phase-independent orbits |
| Live-cell or spatial tumour imaging     | Cellular automata and attractor analysis                                  |
| Patient/control comparisons             | Reconstruction signatures                                                 |
| Single-cell pseudotime                  | Transition analysis, but not literal time-dependent conclusions           |

Time-resolved phosphoproteomics has already been used to infer signalling pathways, making this a realistic application direction. [Köksal et al., 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6295338/)

## A concrete phosphoproteomics example

Suppose you have:

```text
condition  replicate  time  ERK  AKT  JNK  apoptosis
control    1          0     ...
control    1          5     ...
control    1          15    ...
drug       1          0     ...
drug       1          5     ...
```

### 1. Estimate meaningful activities

Start with normalized measurements or inferred kinase/pathway activities—not individual noisy phosphosites where possible.

For example:

```text
time       ERK       AKT       JNK
0          0.1       0.0       0.2
5          1.8       1.1       0.1
15         1.2       0.4       0.8
30         0.2      -0.3       1.4
```

### 2. Convert values into symbols

Several encodings are possible.

Absolute activity:

```text
L = low
B = baseline
H = high
```

Or, often more useful for signalling dynamics:

```text
D = decreasing
S = stable
U = increasing
```

For example:

```text
ERK: B → H → H → B
AKT: B → H → B → L
JNK: B → B → H → H
```

Use biological thresholds, confidence intervals or replicate-supported changes. A median split would be easy but usually scientifically weak.

### 3. Learn a temporal grammar

For ERK, the observed transitions might be:

```text
B → H
H → H
H → B
```

These transitions define an adjacency matrix:

$$
A_{ij} =
\begin{cases}
1,&\text{if transition }i\rightarrow j\text{ is supported},\\
0,&\text{otherwise}.
\end{cases}
$$

That matrix can be passed to `OneStepSFT`.

Then the tool can answer:

* Which temporal transitions are allowed?
* Which short response motifs never occur?
* How many cyclic response programs are compatible with the model?
* Does treatment reduce or increase the repertoire of possible dynamics?
* Do control and treated conditions have different symbolic fingerprints?

An important qualification: an unobserved transition is not automatically biologically forbidden. It could simply be missing because sampling is sparse. Require replicate support, bootstrap confidence or a minimum transition count.

## What each existing module means biologically

| Current mathematical output | Possible biological interpretation                               |
| --------------------------- | ---------------------------------------------------------------- |
| Forbidden word              | Temporal activation pattern inconsistent with the inferred model |
| Periodic point              | Possible cyclic signalling program                               |
| Least period                | Smallest intrinsic cycle length                                  |
| Attractor                   | Stable phenotype or recurring activation program                 |
| Basin of attraction         | Initial states converging to the same outcome                    |
| Collision                   | Different initial states producing the same later state          |
| Garden-of-Eden state        | State that the fitted model cannot produce                       |
| Non-injectivity             | Historical information is lost during evolution                  |
| Inverse rule                | Rule for reconstructing a previous state                         |
| Shift orbit                 | Same oscillation observed at different starting phases           |
| Reconstruction signature    | Finite fingerprint for comparing conditions                      |

These interpretations belong to the fitted discrete model. A Garden-of-Eden state is not automatically biologically impossible—it might expose incomplete data or a bad model.

## What must not be done

Do not arrange kinases arbitrarily into a binary string and apply Rule 110.

The current CA assumes:

$$
x_i(t+1)=f\bigl(x_{i-1}(t),x_i(t),x_{i+1}(t)\bigr),
$$

with:

* the same rule at every position;
* nearest-neighbour interactions;
* positions arranged in a circle.

An arbitrary ordering such as:

```text
AKT – ERK – JNK – EGFR – mTOR – AKT
```

has no biological justification.

For signalling networks, you need a graph-based Boolean model:

$$
x_i(t+1)
=
f_i\left(x_i(t),\{x_j(t):j\in\operatorname{Regulators}(i)\}\right).
$$

Here:

* each protein can have its own rule \(f_i\);
* neighbours come from the biological network;
* updates may include delays or asynchronous behaviour.

Boolean signalling models and patient-specific discrete networks have been used for drug-response simulation, so this extension is biologically defensible. [Montagud et al., 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9018074/)

Standard cellular automata fit more naturally when the sites are genuinely spatial—for example, cells or pixels in time-lapse tumour imaging. Spatial CA models have been used to study tumour invasion and emergent growth patterns. [Jiao and Torquato, 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3245298/)

## Where every module becomes useful

The complete toolkit fits most naturally with either:

1. **Periodic biological processes**, such as circadian rhythms or the cell cycle.

   Shift groups identify the same cycle observed at different phases. Periodic counts and least periods have meaningful interpretations.

2. **Spatial time-lapse data**, where cells occupy a real lattice or neighbourhood graph.

   CA simulation, attractors, reversibility and Garden-of-Eden analysis become meaningful.

3. **A graph Boolean extension for signalling data.**

   This is the most relevant direction for your kinase and phosphoproteomic work.

For ordinary drug-response time courses, use the subshift and reconstruction components first. The existing shift-group component is only useful if phase or cyclic behaviour matters.

## What works in the current Python API

After encoding a trajectory, you can already construct a data-derived transition model:

```python
from rubin_subshifts.symbolic import Alphabet, OneStepSFT
from rubin_subshifts.reconstruction import build_signature

states = ["baseline", "high", "high", "baseline", "low"]
labels = ("low", "baseline", "high")
index = {state: i for i, state in enumerate(labels)}

adjacency = [[0] * len(labels) for _ in labels]

for source, target in zip(states, states[1:]):
    adjacency[index[source]][index[target]] = 1

model = OneStepSFT.from_matrix(
    Alphabet(labels),
    adjacency,
    name="ERK response model",
)

print([model.periodic_point_count(n) for n in range(1, 7)])

signature = build_signature(model, periods=(1, 2, 3, 4, 5, 6))
```

For production analysis, build the adjacency matrix from all replicates rather than one trajectory.

The current CLI does not expose this workflow. Its comparison command is hard-coded to the full shift and golden mean shift.