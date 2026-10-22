# CommutativeCancellation drops small rotations

Two `RZ(6e-5)` gates should combine into `RZ(1.2e-4)`. Instead, `CommutativeCancellation` removes both, changing the circuit's behavior. The operator distance from the original is `6e-5`, even after ignoring global phase. The same problem occurs at transpiler optimization levels 2 and 3 when CX gates separate the rotations.

The script checks the pass directly and both optimization levels, printing `REPRODUCED` or `NOT_REPRODUCED`. It flags the bug only when the rotations disappear and the operator distance exceeds `1e-6`. It also checks that a single `RZ(1.2e-4)` gate survives, showing that the problem occurs when merging gates. `NOT_REPRODUCED` means this specific bug was not detected.

## Cause

In the [Qiskit 2.6.0 implementation](https://github.com/Qiskit/qiskit/blob/2.6.0/crates/transpiler/src/passes/commutation_cancellation.rs), merged rotations are checked against multiples of `4π` using a fixed tolerance of `1e-5` on the normalized angle. Near zero, this allows a total angle below approximately `1.2566e-4` radians to be discarded, including this reproduction's `1.2e-4`. The merge logic only runs for groups containing more than one gate, explaining why the equivalent single rotation survives.

This cutoff is independent of the `approximation_degree` used for commutation analysis, so setting `approximation_degree=1.0` does not disable it.

## Related issues and pull requests

Checked on October 22, 2026, including closed issues. No issue with this exact two-RZ reproduction was found.

| Reference | Status | Relationship |
|---|---|---|
| [#13547: Incorrect transpilation with a small-angle RY](https://github.com/Qiskit/qiskit/issues/13547) | Closed; fixed by [#13874](https://github.com/Qiskit/qiskit/pull/13874) | Inconsistent tolerances caused incorrect cancellation at optimization levels 2 and 3. The fix aligned the commutation checker's metric with other passes; it did not address this merged-angle cutoff. |
| [#16782: CX pair cancelled across a non-commuting RY](https://github.com/Qiskit/qiskit/issues/16782) | Closed as expected numerical-tolerance behavior | Same pass and small-angle theme. Maintainers explain that numerical approximation remains even with `approximation_degree=1.0`. This concerns approximate commutation rather than the separate merged-angle check. |
| [#3433: Incorrect transpilation of small-angle phase gadgets](https://github.com/Qiskit/qiskit/issues/3433) | Open | Older RZ/CX report at optimization levels 2 and 3. Its discussion identifies inconsistent thresholds for identity removal and commutation. |
| [#14115: Expose `approximation_degree` in `CommutativeCancellation`](https://github.com/Qiskit/qiskit/issues/14115) | Closed; implemented by [#16679](https://github.com/Qiskit/qiskit/pull/16679) | Added control over commutation approximation and connected it to the preset pass managers. The fixed merged-angle cutoff remains independent. |
| [#16864: Fidelity cutoff despite `approximation_degree=1.0`](https://github.com/Qiskit/qiskit/issues/16864) | Open | Similar concern in a different pass, `TwoQubitPeepholeOptimization`, where a nonzero rotation component becomes zero despite requesting no approximation. |

The most directly relevant PR is [#16790: Improve the `CommutativeCancellation` docstring](https://github.com/Qiskit/qiskit/pull/16790), which is open and explicitly describes the independent fixed merged-angle cutoff. It changes documentation only.

The distinguishing behavior in this reproduction is that two rotations disappear while an equivalent single rotation survives. The resulting operator error also remains after ignoring global phase. These details separate this report from approximate-commutation and global-phase-only reports.
