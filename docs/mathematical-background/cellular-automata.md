# Cellular automata

A one-dimensional cellular automaton is a continuous shift-commuting map defined by a finite local rule. With memory \(m\) and anticipation \(a\),

\[
F(x)_i=f(x_{i-m},\ldots,x_{i+a}).
\]

The implementation applies this rule exactly to periodic configurations, composes local maps with the correct enlarged neighbourhood, simulates synchronous histories, and builds finite functional graphs.

Bijectivity on one quotient \(A^{\mathbb Z/n\mathbb Z}\) is labelled **bijective on the tested finite periodic quotient**. It is not automatically labelled reversible on the full shift.

