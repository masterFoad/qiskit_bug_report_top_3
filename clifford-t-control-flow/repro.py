import platform
import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import get_clifford_gate_names

print("Python", platform.python_version())
print("qiskit", qiskit.__version__)

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
with qc.if_test((qc.clbits[0], 1)):
    qc.x(0)

output = transpile(
    qc,
    basis_gates=get_clifford_gate_names() + ["t", "tdg"],
    optimization_level=2,
)
print("COMPILED", dict(output.count_ops()))
