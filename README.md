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

## Setup

The scripts were run with Python 3.13. From the repository root:

```sh
python3.13 -m venv venv && venv/bin/pip install -r requirements.txt
```

`requirements.txt` pins `qiskit==2.6.0` (the latest PyPI release on
2026-10-22) and the dependency versions used for the recorded runs. Each script
can then be run from the repository root with `venv/bin/python <folder>/repro.py`.

## 1. CommutativeCancellation drops small rotations

Two `RZ(6e-5)` gates on the same qubit should combine into `RZ(1.2e-4)`.
`CommutativeCancellation` removes both instead. The operator distance between
input and output is `6e-5` after removing global phase. The same happens at
transpiler optimization levels 2 and 3 when CX gates separate the rotations.
A single `RZ(1.2e-4)` gate is kept, so the loss occurs when gates are merged.

```sh
venv/bin/python commutative-cancellation-angle-cutoff/repro.py
```

Expected: the merged `RZ(1.2e-4)` is kept and the output is equivalent to the input.

Observed on Qiskit 2.6.0:

```text
single_pass {} equiv False distance 6e-05 REPRODUCED
control_single_rz {'rz': 1} equiv True
preset 2 {'cx': 2} equiv False distance 6e-05 REPRODUCED
preset 3 {'cx': 2} equiv False distance 6e-05 REPRODUCED
```

Versions checked: reproduced on 2.5.0, 2.5.2 and 2.6.0; not reproduced on
2.3.1, 2.4.0 and 2.4.2. The review branch also records a reproduction on main
at `ef112241` (2.7.0.dev0), kept in the folder's `outputs/`.

Folder: [commutative-cancellation-angle-cutoff/](commutative-cancellation-angle-cutoff/)

## 2. Clifford+T transpilation fails on `if_else`

Qiskit fails to compile a one-qubit circuit that measures the qubit and applies
`X` when the result is 1. Both gates, `H` and `X`, already belong to the
requested Clifford+T basis.

```sh
venv/bin/python clifford-t-control-flow/repro.py
```

Expected: compilation succeeds, preserves the conditional `X`, and the script
prints `COMPILED`.

Observed on Qiskit 2.6.0: `BasisTranslator` raises `TranspilerError` with
`Unable to translate the operations in the circuit`, listing `if_else`, and the
script exits nonzero.

Versions checked: fails on 2.4.0, 2.5.2 and 2.6.0; compiles on 2.3.1 and prints
`COMPILED {'h': 1, 'measure': 1, 'if_else': 1}`.

Likely cause (from the folder README): in Qiskit 2.6.0,
`TranslateToCliffordRZPassManager` builds an intermediate basis containing
Clifford gates, `t`, `tdg`, and `rz`, but omits `if_else`, so the translator
rejects the conditional container even though its `X` gate is supported.

Folder: [clifford-t-control-flow/](clifford-t-control-flow/)

## 3. RZZ angle bounds are ignored inside control flow

Qiskit compiles a circuit for a target that only accepts `RZZ` angles between
`0` and `pi/2`, but leaves an unsupported negative angle inside an `if_else`
block. Compilation succeeds even though the result violates the target's bounds.
The script registers an exact replacement, `X(0); RZZ(0.4); X(0)`, for the test
angle and places `RZZ(-0.4)` both at the top level and inside `if_else`. The
top-level copy is rewritten, which shows that the rule works.

```sh
venv/bin/python rzz-angle-bounds-in-control-flow/repro.py
```

Expected: all RZZ angles in `[0, pi/2]`, both at the top level and inside `if_else`.

Observed on Qiskit 2.6.0:

```text
qiskit 2.6.0
Expected: all RZZ angles in [0, pi/2]
Top level: [0.4]
Inside if_else: [-0.4]
```

Versions checked: the same output on 2.3.1, 2.4.0, 2.5.2 and 2.6.0.
The folder also has a longer
[explanation of the circuit and the replacement rule](rzz-angle-bounds-in-control-flow/detailed_explanation.md).

Folder: [rzz-angle-bounds-in-control-flow/](rzz-angle-bounds-in-control-flow/)

## Environment

All runs above were made on 2026-10-22 on macOS arm64 with CPython 3.13.14,
numpy 2.5.4, scipy 1.18.1 and rustworkx 0.18.1, using PyPI wheels of each
Qiskit version listed. Full outputs, one file per script and version, are in
[`outputs/`](outputs/); local paths in tracebacks are replaced by `<venv>`.
Each script ran in under one second.
