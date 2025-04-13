from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT

def create_hashed_oracle(n_qubits, valid_states):
    """
    Create a hashed oracle for Grover's algorithm that marks valid states directly.
    Args:
        n_qubits (int): number of qubits in the index register.
        valid_states (list of str): list of bitstrings representing valid indexes.
    Returns:
        QuantumCircuit: the oracle circuit.
    """
    oracle = QuantumCircuit(n_qubits)
    for bitstring in valid_states:
        for i, bit in enumerate(reversed(bitstring)):
            if bit == '0':
                oracle.x(i)
        oracle.h(n_qubits - 1)
        oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1, mode='noancilla')
        oracle.h(n_qubits - 1)
        for i, bit in enumerate(reversed(bitstring)):
            if bit == '0':
                oracle.x(i)
    oracle.name = "HashOracle"
    return oracle

def diffuser(n_qubits):
    """
    Diffuser circuit for Grover's algorithm.
    Args:
        n_qubits (int): number of qubits in the index register.
    Returns:
        QuantumCircuit: the diffuser circuit.
    """
    diff = QuantumCircuit(n_qubits)
    diff.h(range(n_qubits))
    diff.x(range(n_qubits))
    diff.h(n_qubits - 1)
    diff.mcx(list(range(n_qubits - 1)), n_qubits - 1, mode='noancilla')
    diff.h(n_qubits - 1)
    diff.x(range(n_qubits))
    diff.h(range(n_qubits))
    diff.name = "Diffuser"
    return diff

def grover_operator(n_qubits, valid_states):
    """
    Grover operator for the search algorithm.
    Args:
        n_qubits (int): number of qubits in the index register.
        valid_states (list of str): list of bitstrings representing valid indexes.
    Returns:
        QuantumCircuit: the Grover operator circuit.
    """
    oracle = create_hashed_oracle(n_qubits, valid_states)
    diff_op = diffuser(n_qubits)
    grover_op = diff_op.compose(oracle)
    grover_op.name = "GroverOP"
    return grover_op

def quantum_counting_circuit(n_qubits, p_count, valid_states):
    """
    Quantum counting circuit for Grover's algorithm.
    Args:
        n_qubits (int): number of qubits in the index register.
        p_count (int): number of qubits in the counting register.
        valid_states (list of str): list of bitstrings representing valid indexes.
    """
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    count_reg = QuantumRegister(p_count, 'count')
    search_reg = QuantumRegister(n_qubits, 'search')
    c_reg = ClassicalRegister(p_count, 'c')
    qc = QuantumCircuit(count_reg, search_reg, c_reg)

    # Prepare registers in uniform superposition.
    qc.h(count_reg)
    qc.h(search_reg)

    # Build controlled Grover operator.
    G = grover_operator(n_qubits, valid_states)
    controlled_G = G.to_gate().control(1)
    for j in range(p_count):
        exponent = 2 ** j
        controlled_G_power = controlled_G ** exponent
        qc.append(controlled_G_power, [count_reg[j]] + list(search_reg))

    # Append inverse QFT.
    iqft = QFT(p_count, inverse=True).to_gate()
    iqft.name = "QFTINV"
    qc.append(iqft, count_reg)
    qc.measure(count_reg, c_reg)
    return qc

def grover_basic_search_circuit(n_qubits, valid_states, iterations):
    """
    Grover search circuit for a basic search oracle implementation.
    Args:
        n_qubits (int): number of qubits in the index register.
        valid_states (list of str): list of bitstrings representing valid indexes.
        iterations (int): number of Grover iterations.
    Returns:
        QuantumCircuit: the Grover search circuit.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    oracle = create_hashed_oracle(n_qubits, valid_states)
    diff_op = diffuser(n_qubits)
    for _ in range(iterations):
        qc.append(oracle, range(n_qubits))
        qc.append(diff_op, range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def grover_search_circuit(n_qubits, valid_states, iterations, possible_states, targets):
    """
    Grover search circuit for a given set of possible states and targets.
    Args:
        n_qubits (int): number of qubits in the index register.
        valid_states (list of str): list of bitstrings representing valid indexes (unused).
        possible_states (list of str): list of bitstrings representing possible states.
        iterations (int): number of Grover iterations.
        targets (list of str): list of target bitstrings.
    Returns:
        QuantumCircuit: the Grover search circuit.
    """
    n = len(possible_states)
    num_val = len(possible_states[0])

    # Create registers
    qreg_idx = QuantumRegister(n_qubits, name='idx')
    qreg_val = QuantumRegister(num_val, name='val')
    qreg_phase = QuantumRegister(1, name='phase')
    creg = ClassicalRegister(n_qubits, name='c')

    qc = QuantumCircuit(qreg_idx, qreg_val, qreg_phase, creg)

    # Initialize index register in superposition and phase ancilla
    qc.h(qreg_idx)
    qc.x(qreg_phase)
    qc.h(qreg_phase)

    # Grover search iterations
    for _ in range(iterations):
        load_array(qc, possible_states, qreg_idx, qreg_val)
        mark_if_value_is_target(qc, targets, qreg_val, qreg_phase)
        unload_array(qc, possible_states, qreg_idx, qreg_val)
        qc.append(diffuser(n_qubits), qreg_idx)
    qc.measure(qreg_idx, creg)

    return qc

def load_array(qc, array, qreg_idx, qreg_val):
    """
    Loads the values of the array into the value register, performing controlled operation on the index.

    Args:
      qc (QuantumCircuit): the quantum circuit.
      array (list of str): list of bitstrings representing array entries.
      qreg_idx (QuantumRegister): the register holding the index.
      qreg_val (QuantumRegister): the register holding the values.
    """
    num_idx = len(qreg_idx)
    num_val = len(qreg_val)
    n = len(array)
    for i in range(n):
        index_bin = format(i, f"0{num_idx}b")
        val_bin = array[i]
        # iterate over each bit
        for val_qubit, bit_char in enumerate(reversed(val_bin)):
            if bit_char == '1':
                # flip any index qubit where bit is '0'
                for k, idx_bit in enumerate(index_bin):
                    if idx_bit == '0':
                        qc.x(qreg_idx[k])
                # Preform control-X gate to load the value bit
                qc.mcx(qreg_idx, qreg_val[val_qubit])
                # Undo the initial X on the index register
                for k, idx_bit in enumerate(index_bin):
                    if idx_bit == '0':
                        qc.x(qreg_idx[k])


def unload_array(qc, array, qreg_idx, qreg_val):
    """
    Uncomputes the array loading.
    Args:
      qc (QuantumCircuit): the quantum circuit.
      array (list of str): list of bitstrings representing array entries.
      qreg_idx (QuantumRegister): the register holding the index.
      qreg_val (QuantumRegister): the register holding the values.
    """
    num_idx = len(qreg_idx)
    num_val = len(qreg_val)
    n = len(array)
    for i in reversed(range(n)):
        index_bin = format(i, f"0{num_idx}b")
        val_bin = array[i]
        for val_qubit, bit_char in reversed(list(enumerate(reversed(val_bin)))):
            if bit_char == '1':
                for k, idx_bit in enumerate(index_bin):
                    if idx_bit == '0':
                        qc.x(qreg_idx[k])
                qc.mcx(qreg_idx, qreg_val[val_qubit])
                for k, idx_bit in enumerate(index_bin):
                    if idx_bit == '0':
                        qc.x(qreg_idx[k])


def mark_if_value_is_target(qc, targets, qreg_val, qreg_phase):
    """
    Marks the current state if the value register equals the target bitstring.
    This is done by applying an X gate to the qubits of the value register
    corresponding to '0' bits in the target, then applying a multi-controlled X gate

    Args:
      qc (QuantumCircuit): the quantum circuit.
      targets (list): list of target bitstrings (of length equal to len(qreg_val)).
      qreg_val (QuantumRegister): the register holding the values.
      qreg_phase (QuantumRegister): the phase qubit register.
    """

    for target in targets:
        # For each bit of the target, apply X gate if bit is '0'
        for val_qubit, bit_char in enumerate(reversed(target)):
            if bit_char == '0':
                qc.x(qreg_val[val_qubit])
        # Phase flip for the target
        qc.h(qreg_phase[0])
        qc.mcx(qreg_val, qreg_phase[0])
        qc.h(qreg_phase[0])
        # Undo the initial X gates on the value register
        for val_qubit, bit_char in enumerate(reversed(target)):
            if bit_char == '0':
                qc.x(qreg_val[val_qubit])
