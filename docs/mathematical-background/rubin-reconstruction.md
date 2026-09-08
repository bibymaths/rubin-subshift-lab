# Rubin-inspired reconstruction

Rubin-type reconstruction theorems ask when an abstract transformation group remembers the space on which it acts. This laboratory does not implement a proof of such a theorem. It asks a bounded experimental question instead: which selected dynamical systems are distinguished by selected finite action invariants?

```mermaid
flowchart TD
    X[System X] --> SX[Finite signature X]
    Y[System Y] --> SY[Finite signature Y]
    SX --> C[Feature-by-feature comparison]
    SY --> C
    C --> D[Separating finite features]
    C --> N[Features not separating within bounds]
```

A match means only “not distinguished within the tested bounds.” A difference means “distinguished by the selected finite invariants.” Neither statement is silently promoted to an infinite-space theorem.

