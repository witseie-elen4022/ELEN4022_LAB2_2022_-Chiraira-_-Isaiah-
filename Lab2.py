from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit
from qiskit import *

# importing Qiskit
from qiskit import QuantumCircuit, transpile, assemble, Aer, IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from IPython.display import display
import pandas as pd

import matplotlib.pyplot as plt

print('\n')
def Circuit(first, second):
    l = len(first)
    l2 = len(second)
    if l > l2:
        n = l
    else:
        n = l2
    a = QuantumRegister(n) #First number
    b = QuantumRegister(n+1) #Second number, then sum
    c = QuantumRegister(n) #Carry bits
    cl = ClassicalRegister(n+1) #Classical output
    qc = QuantumCircuit(a, b, c, cl)

    #Setting up the registers using the values inputted
    for i in range(l):
        if first[i] == "1":
           qc.x(a[l - (i+1)]) #Flip the qubit from 0 to 1
    for i in range(l2):
       if second[i] == "1":
          qc.x(b[l2 - (i+1)]) #Flip the qubit from 0 to 1
    return a,b,c,cl,qc,n




#Implementing the carry gate 
def CARRY(n, a, b, c, qc):
    for i in range(n-1):
        qc.ccx(a[i], b[i], c[i+1])
        qc.cx(a[i], b[i])
        qc.ccx(c[i], b[i], c[i+1])

    qc.ccx(a[n-1], b[n-1], b[n])
    qc.cx(a[n-1], b[n-1])
    qc.ccx(c[n-1], b[n-1], b[n])

    #Reversing the gate operation performed on b[n-1]
    qc.cx(c[n-1], b[n-1])

    return n, a, b, c, qc



def SUM(n, a, b, c, qc):
    for i in range(n-1):
        #Reversing the gate operations performed during the carry gate implementations
        qc.ccx(c[(n-2)-i], b[(n-2)-i], c[(n-1)-i])
        qc.cx(a[(n-2)-i], b[(n-2)-i])
        qc.ccx(a[(n-2)-i], b[(n-2)-i], c[(n-1)-i])

        #SUM Gate
        qc.cx(c[(n-2)-i], b[(n-2)-i])
        qc.cx(a[(n-2)-i], b[(n-2)-i])
    return n, a, b, c, qc


def QFA(first, second,  Circuit, CARRY, SUM):
    a, b, c, cl, qc, n = Circuit(first, second)
    n, a, b, c, qc= CARRY(n, a, b, c, qc)
    n, a, b, c, qc = SUM(n, a, b, c, qc)
    return n,b,cl,qc



first = input("Enter an 8-bit binary number: ")
second = input("Enter another 8-bit binary number: ")



n, b, cl, qc = QFA(first, second, Circuit, CARRY, SUM)

#Measure qubits and store results in classical register cl
for i in range(n+1):
    qc.measure(b[i], cl[i])


backend = Aer.get_backend('qasm_simulator', shots = 2)
job = backend.run(qc)
result = job.result()                                                               
print(result.get_counts())


# Load our saved IBMQ accounts and get the least busy backend device with less than or equal to nqubits
IBMQ.load_account()
provider = IBMQ.get_provider(hub='ibm-q')
backend = least_busy(provider.backends(n_qubits =5, operational = True, simulator = False))
print("least busy backend: ", backend)

shots = 2048
transpiled_qc = transpile(qc, backend, optimization_level=3)
job = backend.run(transpiled_qc, shots=shots)
job_monitor(job)

counts = job.result().get_counts()
plot_histogram(counts)
qc.draw(output = 'mpl')
plt.show()


