# RZZ angle bounds are ignored inside control flow

Qiskit compiles a circuit for a target that only accepts `RZZ` angles between
`0` and `pi/2`, but leaves an unsupported negative angle inside an `if_else`
block. Compilation succeeds even though the result violates the target's bounds.

For a beginner-friendly walkthrough of the circuit and its wrapping rule, see
[the detailed explanation](detailed_explanation.md).

[repro.py](repro.py) places the same `RZZ(-0.4)` gate at the top level and
inside a conditional block, then calls `transpile(..., optimization_level=0)`.
It explicitly registers an equivalent replacement, `X(0); RZZ(0.4); X(0)`,
so Qiskit has a rule for bringing the test angle into range.

The target declares only `RZZ`, `X`, and `if_else`. The top-level gate acts as
a control: it comes out as `RZZ(0.4)`, which shows that the rewrite works, while
the copy inside `if_else` still has `-0.4`.

## Related GitHub issues

Searched open and closed issues and pull requests in `Qiskit/qiskit` and
`Qiskit/qiskit-ibm-runtime` on October 22, 2026. No exact duplicate of this
control-flow reproduction was found. The following reports are related;
statuses reflect that search date.

| Report | Status | Relationship to this reproduction |
|---|---|---|
| [Qiskit #16462: `FoldRzzAngle` not applied](https://github.com/Qiskit/qiskit/issues/16462) | Closed | Similar symptom: `RZZ(-0.1)` survives transpilation. Maintainers traced it to missing target angle bounds, which allowed optimization to recreate negative angles. The reporter later confirmed a fix in Qiskit IBM Runtime 0.48.0. |
| [Qiskit #16638: Support removing instructions from a Target](https://github.com/Qiskit/qiskit/issues/16638) | Open | Describes angle bounds being lost when supplying `basis_gates`, allowing unsupported negative RZZ angles in the output. This has a different trigger from the conditional-block failure here. |
| [Runtime #2256: RZZ folding fails with `XXPlusYYGate`](https://github.com/Qiskit/qiskit-ibm-runtime/issues/2256) | Closed | Direct RZZ gates were corrected, while negative RZZ gates produced during compilation remained. The issue was closed following the introduction of target angle-bound support in Qiskit 2.2.0. |
| [Qiskit #13784: Extend target parameter constraints](https://github.com/Qiskit/qiskit/issues/13784) | Closed | Original feature request behind angle bounds and `WrapAngles`, implemented by [PR #14406](https://github.com/Qiskit/qiskit/pull/14406). Provides background for the mechanism used here. |
| [Runtime #2441: Adopt `angle_bounds` and `WrapAngles`](https://github.com/Qiskit/qiskit-ibm-runtime/issues/2441) | Closed | Integrated the mechanism into IBM backends through [PR #2960](https://github.com/Qiskit/qiskit-ibm-runtime/pull/2960), addressing the missing bounds underlying Qiskit #16462. |

This reproduction appears distinct because it explicitly supplies both the
target bounds and the wrapping callback. The top-level gate is corrected, but
the same gate inside `if_else` remains out of bounds at optimization level 0.
That points to a control-flow handling gap in `WrapAngles`; the related reports
above do not establish that this specific case has already been fixed.

When filing this report, cite Qiskit #16462 and #13784 / PR #14406 as related
work, and emphasize that the bounds are already present and the failure occurs
inside the conditional block.
