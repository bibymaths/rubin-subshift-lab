# Architecture

The dependency direction runs from exact domain objects toward presentation layers.

```mermaid
flowchart TD
    CFG[Configuration and limits] --> SYM[Symbolic core]
    SYM --> CA[Cellular automata]
    SYM --> GR[Graph constructions]
    CA --> GP[Finite permutation groups]
    GP --> REC[Reconstruction]
    SYM --> REC
    REC --> EXP[Experiment service]
    EXP --> VIS[Plotly visualization]
    EXP --> CLI[Typer CLI]
    VIS --> APP[Streamlit pages]
```

Immutable dataclasses represent mathematical objects; Pydantic validates user-facing configuration; pure functions perform transformations. Streamlit imports the service layer, never the reverse.

