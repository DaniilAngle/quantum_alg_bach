import time as pytime
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

def run_circuit(qc, shots=1024, use_noise=False, simulation=True, optimisation_level=3):
    """
    Run a quantum circuit on a simulator or real device.
    Args:
        qc (QuantumCircuit): The quantum circuit to run.
        shots (int): Number of shots to run algorithm with.
        use_noise (bool): If True, use noise model.
        simulation (bool): If True, run on simulator.
        optimisation_level (int): Optimization level for transpilation.
    Returns:
        tuple: A tuple containing counts, depth, gate count, and runtime.
    """
    if simulation:
        simulator = AerSimulator()
        noise_model = NoiseModel.from_backend(simulator) if use_noise else None
        transpiled = transpile(qc, simulator, optimization_level=optimisation_level)
        start = pytime.perf_counter()
        result = simulator.run(transpiled, shots=shots, noise_model=noise_model).result()
        end = pytime.perf_counter()
        counts = result.get_counts()
        depth = transpiled.depth()
        gate_count = sum(transpiled.count_ops().values())
        runtime = end - start
        return counts, depth, gate_count, runtime
    else:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        service = QiskitRuntimeService()
        ibm_backend = service.least_busy(operational=True, simulator=False)
        pm = generate_preset_pass_manager(backend=ibm_backend, optimization_level=optimisation_level)
        isa_circuit = pm.run(qc)
        start = pytime.perf_counter()
        sampler = SamplerV2(mode=ibm_backend)
        job = sampler.run([isa_circuit], shots=shots)
        result = job.result()
        pub_result = result[0]
        end = pytime.perf_counter()
        counts = pub_result.data.c.get_counts()
        transpiled = transpile(qc, ibm_backend, optimization_level=optimisation_level)
        depth = transpiled.depth()
        gate_count = sum(transpiled.count_ops().values())
        runtime = end - start
        return counts, depth, gate_count, runtime

def run_counting(n_qubits, p_count, valid_states, shots=1024, use_noise=False, simulation=True, quantum_counting_circuit_func=None, show_qc=False):
    """
    Run the quantum counting circuit.
    Args:
        n_qubits (int): Number of qubits in the index register.
        p_count (int): Number of qubits in the counting register.
        valid_states (list of str): List of bitstrings representing valid indexes.
        shots (int): Number of measurement shots.
        use_noise (bool): If True, use noise model.
        simulation (bool): If True, run on simulator.
        quantum_counting_circuit_func (function): Custom quantum counting circuit function.
        show_qc (bool): If True, print the quantum circuit.
    Returns:
        tuple: A tuple containing counts, depth, gate count, and runtime.
    """
    if quantum_counting_circuit_func is None:
        from .circuits import quantum_counting_circuit
        quantum_counting_circuit_func = quantum_counting_circuit
    qc = quantum_counting_circuit_func(n_qubits, p_count, valid_states)
    if show_qc:
        print(qc.draw(output='text', fold=-1))
    return run_circuit(qc, shots=shots, use_noise=use_noise, simulation=simulation)

def run_grover_search(n_qubits, valid_states, iterations, shots=1024, use_noise=False, simulation=True, grover_search_circuit_func=None, possible_states=None, targets=None, show_qc=False):
    """
    Run the Grover search circuit.
    Args:
        n_qubits (int): Number of qubits in the index register.
        valid_states (list of str): List of bitstrings representing valid indexes.
        iterations (int): Number of Grover iterations.
        shots (int): Number of measurement shots.
        use_noise (bool): If True, use noise model.
        simulation (bool): If True, run on simulator.
        grover_search_circuit_func (function): Custom Grover search circuit function.
        possible_states (list of str): List of possible states for the search.
        targets (list of str): List of target states for the search.
        show_qc (bool): If True, print the quantum circuit.
    Returns:
        tuple: A tuple containing counts, depth, gate count, and runtime.
    """
    if grover_search_circuit_func is None:
        from .circuits import grover_search_circuit
        grover_search_circuit_func = grover_search_circuit
    qc = grover_search_circuit_func(n_qubits, valid_states, iterations, possible_states, targets,)
    if show_qc:
        print(qc.draw(output='text', fold=-1))
    return run_circuit(qc, shots=shots, use_noise=use_noise, simulation=simulation)

