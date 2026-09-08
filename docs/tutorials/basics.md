## First: the basic mental model

Imagine \(n\) binary cells arranged in a circle:

```text
0 0 1 0 1 0
```

Because it is a circle, the last cell is adjacent to the first.

* A **configuration** is one complete binary pattern.
* The **shift** rotates the pattern by one position.
* A **subshift** restricts which patterns are allowed.
* A **cellular automaton** updates every cell simultaneously.
* A **periodic point** is unchanged after shifting it \(n\) times.
* An **orbit** groups configurations that are rotations of one another.

The most important distinction is:

* **Declared period \(n\):** represented using \(n\) cells.
* **Least period \(n\):** \(n\) is the smallest rotation returning the pattern to itself.

For example, `010101` is represented on six cells but has least period \(2\).

---

## 1. Golden mean subshift

```text
Model: Golden mean shift
Periodic Point Counts: [1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
```

The golden mean shift contains binary sequences in which `11` is forbidden.

Because the configurations are circular, the last and first symbols must also not form `11`.

Examples:

* Period 1: only `0` is allowed. Repeating `1` gives `...111...`, which contains `11`. Count: **1**
* Period 2: `00`, `01`, `10` are allowed. Count: **3**
* Period 3: `000`, `001`, `010`, `100` are allowed. Count: **4**
* Period 4: seven circular words are allowed. Count: **7**

This produces:

$$
P_1=1,\qquad P_2=3,\qquad P_n=P_{n-1}+P_{n-2}.
$$

Therefore:

$$
1,3,4,7,11,18,29,\ldots
$$

These are Lucas-type numbers. Their growth rate approaches the golden ratio,

$$
\varphi=\frac{1+\sqrt 5}{2},
$$

which explains the name “golden mean shift.”

These counts are configurations, not rotation classes.

---

## 2. Rule 110 simulation

```bash
uv run rubin-subshift ca simulate --rule 110 --initial 00010000
```

Rule 110 examines three cells at a time:

```text
left, centre, right
```

and calculates the new value of the centre cell.

Its lookup table is:

| Neighbourhood | New value |
| ------------- | --------: |
| `111`         |         0 |
| `110`         |         1 |
| `101`         |         1 |
| `100`         |         0 |
| `011`         |         1 |
| `010`         |         1 |
| `001`         |         1 |
| `000`         |         0 |

For the initial state:

```text
00010000
```

the neighbourhoods `001` and `010` around the original `1` produce new ones:

```text
00010000  initial
00110000  after one update
01110000  after two updates
...
```

All cells update simultaneously, and the boundary wraps around. The left neighbour of the first cell is the final cell.

The command prints **17 rows**:

* one initial state;
* sixteen updates, because `--steps` defaults to 16.

For this particular initial state on the eight-cell ring:

* the first four updates are transient;
* it then enters a cycle of length 16;
* at step 20, `11110001` appears again.

So the evolution does not continue creating new patterns forever. With only eight cells, there are only \(2^8=256\) possible states, so repetition is unavoidable.

---

## 3. Finite reversibility of Rule 110

```json
{
  "states": 256,
  "image_states": 154,
  "injective": false,
  "surjective": false,
  "bijective": false,
  "garden_of_eden": 102,
  "attractor_cycles": 6
}
```

Here, the program tests Rule 110 on **every possible eight-cell state**.

Since every cell is binary:

$$
\text{number of states}=2^8=256.
$$

Think of Rule 110 as a function:

$$
F:\{0,1\}^8\longrightarrow\{0,1\}^8.
$$

Each of the 256 states has one outgoing arrow pointing to its next state.

### `image_states: 154`

After applying Rule 110 to all 256 inputs, only 154 distinct outputs appear.

Some different inputs therefore produce the same output.

### `injective: false`

Injective means:

> Different inputs always produce different outputs.

That fails because multiple states collide onto the same next state.

### `surjective: false`

Surjective means:

> Every possible state can be produced from some previous state.

Only 154 of the 256 states can be produced, so it fails.

### `garden_of_eden: 102`

A Garden-of-Eden state has no predecessor. It can be selected as an initial state, but it can never arise after applying Rule 110.

$$
256-154=102.
$$

Hence there are exactly 102 Garden-of-Eden states.

### `bijective: false`

Bijective means both injective and surjective: a perfect rearrangement of the state space.

A finite CA is reversible exactly when this induced finite map is bijective. Rule 110 is not reversible on this eight-cell domain.

### `attractor_cycles: 6`

Every trajectory on a finite deterministic state space eventually reaches a repeating loop.

This period-8 state graph has six such loops, with lengths:

$$
1,\ 2,\ 2,\ 8,\ 16,\ 16.
$$

Your `00010000` simulation eventually enters one of the 16-state cycles.

### `guarantee: exact_finite`

All 256 states were examined, so the result is exact for an eight-cell periodic ring. It is not presented as a proof about every possible ring size or the entire infinite line.

---

## 4. Inverse of the left shift

The left shift is:

$$
L(x)_i=x_{i+1}.
$$

It rotates everything left:

```text
010011 → 100110
```

The natural inverse is the right shift:

$$
R(x)_i=x_{i-1}.
$$

The program found this rule:

```text
memory: 1
anticipation: 0
```

This means the candidate looks one cell to the left and no cells to the right.

Its rule table is:

```text
(0, 0) → 0
(0, 1) → 0
(1, 0) → 1
(1, 1) → 1
```

The output is always the first symbol of the pair. Therefore:

$$
R(x)_i=x_{i-1},
$$

which is exactly the right shift.

It satisfies:

$$
L(R(x))=x
$$

and

$$
R(L(x))=x.
$$

### `Tested Candidates: 24`

The search systematically tried local binary rules:

* 4 radius-zero rules;
* 16 rules looking at the current and right cells;
* then four rules looking at the left and current cells.

The fourth rule in that final group was the required right shift:

$$
4+16+4=24.
$$

### `Complete Within Bound: True`

The search found and verified a candidate before reaching its candidate limit.

The program tested periods \(1,2,3,4\), which explains the conservative limitation message. However, because the returned rule is visibly the right shift, its inverse relationship with the left shift can also be proved directly for configurations of every size.

---

## 5. Group generated by the shift

```json
{
  "domain_size": 64,
  "group_order": 6,
  "orbit_sizes": [1, 6, 6, ..., 3, ..., 2, ..., 1]
}
```

The domain is all binary words of length six:

$$
2^6=64.
$$

The only group generator is rotation by one position. Repeated rotation gives:

$$
\mathrm{id},\sigma,\sigma^2,\sigma^3,\sigma^4,\sigma^5.
$$

After six rotations:

$$
\sigma^6=\mathrm{id}.
$$

Therefore the generated group is the cyclic group:

$$
C_6,
$$

with order 6.

### Orbits

An orbit contains all distinct rotations of one configuration.

For example:

```text
000001
000010
000100
001000
010000
100000
```

This orbit has size 6.

The output contains:

| Orbit size | Number of orbits | Example                           |
| ---------: | ---------------: | --------------------------------- |
|          1 |                2 | `000000`, `111111`                |
|          2 |                1 | `010101`, `101010`                |
|          3 |                2 | rotations of `001001` or `011011` |
|          6 |                9 | generic six-cell patterns         |

There are 14 orbits in total, and their sizes sum to 64.

Every orbit size divides 6. This follows from the orbit–stabilizer theorem:

$$
|\operatorname{Orbit}(x)|\,
|\operatorname{Stabilizer}(x)|=6.
$$

### `truncated: false`

The program found the complete group before reaching the configured cap. The result is therefore exhaustive for this finite action.

This is not the complete automorphism group of the infinite binary full shift. It is only the finite group generated by the shift on six-cell configurations.

---

## 6. Reconstruction comparison

This command compares:

* the **binary full shift**, where every binary pattern is allowed;
* the **golden mean shift**, where `11` is forbidden.

It constructs a finite numerical fingerprint for each system.

### Periodic-point counts

For the binary full shift, every length-\(n\) binary word is allowed:

$$
P_n=2^n.
$$

Hence:

```text
2, 4, 8, 16, 32, 64, ...
```

For the golden mean shift:

```text
1, 3, 4, 7, 11, 18, ...
```

The systems already differ at period 1:

* Full shift: `0` and `1`, giving 2 points.
* Golden mean: only `0`, giving 1 point.

### Least-period counts

`periodic_point_count` includes configurations whose true period is smaller.

For example, all four two-cell full-shift words are fixed after two rotations:

```text
00, 01, 10, 11
```

But:

* `00` and `11` have least period 1;
* `01` and `10` have least period 2.

Therefore:

```text
periodic_point_count at n=2 = 4
least_period_count at n=2 = 2
```

Mathematically, the exact-period count is obtained by subtracting all smaller periods that divide \(n\):

$$
E_n=P_n-\sum_{\substack{d\mid n\\d<n}}E_d.
$$

The output’s `least_period_count` counts individual configurations, not orbits. The number of distinct least-period-\(n\) orbits is:

$$
\frac{E_n}{n}.
$$

For example, the golden mean shift has 110 least-period-10 configurations:

$$
110/10=11
$$

distinct period-10 orbits.

### Comparison result

```json
"differing_features": [
  "least_period_count",
  "periodic_point_count"
]
```

Both fingerprints differ.

```json
"matching_features": []
```

Neither complete feature vector agrees across periods \(1,\ldots,10\).

Periodic-point counts are preserved by topological conjugacy. Consequently, one exact mismatch is already enough to show that these two systems are not conjugate.

The reverse is not true:

> Matching finitely many counts would not prove that two systems are equivalent.

### Metadata

* `status: completed`: computation finished.
* `error: null`: no failure occurred.
* `identifier`: deterministic hash of the experiment configuration.
* `completed: true`: all selected periods were calculated.
* `truncated: false`: no computational limit stopped the calculation.
* `random_seed: 0`: recorded for reproducibility, although these counts are deterministic.
* `generators: []`: this experiment did not compare automorphism-group generators.
* Signature `guarantee: exact_finite`: the displayed finite counts are exact.
* Comparison `guarantee: experimental`: the broader reconstruction interpretation is deliberately limited.

The blunt point is that this command does **not yet reconstruct a subshift from its automorphism group**. It compares two systems using finite periodic-point fingerprints. That is useful, but it is only a Rubin-inspired experiment, not Rubin’s theorem itself.

## How the commands fit together

| Command                   | Mathematical question                                           |
| ------------------------- | --------------------------------------------------------------- |
| `subshift analyze`        | Which circular patterns are allowed?                            |
| `ca simulate`             | What happens to one initial state over time?                    |
| `ca finite-reversibility` | What does the complete finite state-transition graph look like? |
| `ca inverse-search`       | Can a local rule undo another local rule?                       |
| `group explore`           | How does rotation partition states into symmetry classes?       |
| `reconstruction compare`  | Can finite numerical fingerprints distinguish two systems?      |
