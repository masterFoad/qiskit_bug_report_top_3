# Three Qiskit bug reproductions

Minimal reproductions of three problems in the Qiskit transpiler. Each folder
holds one script and a short README. This repository was prepared from the
`ophir-review` branch of
[masterFoad/qiskit_bug_repro_report](https://github.com/masterFoad/qiskit_bug_repro_report/tree/ophir-review),
which includes Ophir's review fixes; the folder contents are carried over from
that branch.

| # | Problem | Effect | Qiskit 2.6.0 |
|---|---|---|---|
| 1 | [CommutativeCancellation drops small rotations](commutative-cancellation-angle-cutoff/) | Output circuit is not equivalent to the input | Reproduced |
| 2 | [Clifford+T transpilation fails on `if_else`](clifford-t-control-flow/) | `transpile()` raises `TranspilerError` | Reproduced |
| 3 | [RZZ angle bounds are ignored inside control flow](rzz-angle-bounds-in-control-flow/) | Output violates the target's angle bounds | Reproduced |
