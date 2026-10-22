from math import pi

from qiskit import QuantumCircuit, __version__, transpile
from qiskit.circuit import IfElseOp, Parameter
from qiskit.circuit.library import RZZGate, XGate
from qiskit.converters import circuit_to_dag
from qiskit.transpiler import Target
from qiskit.transpiler.passes import WrapAngles

target = Target(num_qubits=2)
target.add_instruction(RZZGate(Parameter("theta")), angle_bounds=[(0, pi / 2)])
target.add_instruction(XGate())
target.add_instruction(IfElseOp, name="if_else")


def wrap_rzz(angles, _qubits):
    replacement = QuantumCircuit(2)
    replacement.x(0)
    replacement.rzz(-angles[0], 0, 1)
    replacement.x(0)
    return circuit_to_dag(replacement)


WrapAngles.DEFAULT_REGISTRY.add_wrapper("rzz", wrap_rzz)

qc = QuantumCircuit(2, 1)
qc.rzz(-0.4, 0, 1)
with qc.if_test((qc.clbits[0], 0)):
    qc.rzz(-0.4, 0, 1)

out = transpile(qc, target=target, optimization_level=0)
body = out.data[-1].operation.blocks[0]

print("qiskit", __version__)
print("Expected: all RZZ angles in [0, pi/2]")
for label, circuit in (("Top level", out), ("Inside if_else", body)):
    angles = [float(i.operation.params[0]) for i in circuit.data if i.operation.name == "rzz"]
    print(f"{label}: {angles}")
