# Clifford+T transpilation fails on `if_else`

Qiskit fails to compile a one-qubit circuit that measures the qubit and applies
`X` when the result is 1. Both gates, `H` and `X`, already belong to the
requested Clifford+T basis.

[repro.py](repro.py) contains one circuit and one `transpile()` call, with
line-by-line comments. Including `t` and `tdg` in the basis selects the
Clifford+T pipeline; the circuit itself needs no T gates.

## Run

**Expected:** compilation succeeds and preserves the conditional `X`.

**Actual:** `BasisTranslator` raises `TranspilerError` with
`Unable to translate the operations in the circuit`, mentioning `if_else`.
The script shows the traceback and exits nonzero. On a successful version,
it prints `COMPILED`.


## Cause

In Qiskit 2.6.0,
[`TranslateToCliffordRZPassManager`](https://github.com/Qiskit/qiskit/blob/2.6.0/qiskit/transpiler/preset_passmanagers/builtin_plugins.py#L1124-L1159)
builds an intermediate basis containing Clifford gates, `t`, `tdg`, and `rz`,
but omits `if_else`. The translator therefore rejects the conditional container,
even though its `X` gate is supported.

## Related issues

A search of open and closed Qiskit issues and pull requests on October 22, 2026
found related reports, but no exact duplicate of this failure:

- [#14254 — `TranspilerError` with `if_test`](https://github.com/Qiskit/qiskit/issues/14254)
  and [#14338 — `TranspilerError` with `for_loop`](https://github.com/Qiskit/qiskit/issues/14338)
  were closed on May 13, 2025. They report similar translation errors after
  `CollectCliffords`. [PR #14349](https://github.com/Qiskit/qiskit/pull/14349)
  fixed `HighLevelSynthesis` returning early without checking unsupported
  operations inside control-flow blocks.
- [#14025 — Transpilation skips parameterized gates around `if` statements](https://github.com/Qiskit/qiskit/issues/14025),
  [#15734 — Nested `dcx` remains undecomposed](https://github.com/Qiskit/qiskit/issues/15734),
  and [#13162 — Transpiled circuits cause `AerError`](https://github.com/Qiskit/qiskit/issues/13162)
  were closed on March 26, 2026 by
  [PR #15875](https://github.com/Qiskit/qiskit/pull/15875). That fix prevents
  `BasisTranslator` from discarding transformations inside control-flow blocks.
- [#15457 — Improve the Clifford+T compiler pipeline](https://github.com/Qiskit/qiskit/issues/15457),
  closed on March 19, 2026, describes the intermediate Clifford+RZ translation
  stage. It provides pipeline background but does not report this failure.

This reproducer appears distinct: its conditional `X` already belongs to the
basis, but the intermediate basis omits the `if_else` container itself. The
earlier fixes address synthesis or translation of operations inside blocks.
