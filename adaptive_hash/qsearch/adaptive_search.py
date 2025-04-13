import math
from .preprocessing import classical_preprocessing
from .runners import run_counting, run_grover_search
from .metrics import estimate_marked_state_count, compute_errors, compute_statistics


def run_full_search(input_text, search_value, hash_bits=8, prime_index=1,
                    p_count=4, use_noise=False, shots=1024, simulation=True, counting_simulation=True,
                    verbose=False, grover_search_circuit_func=None,
                    quantum_counting_circuit_func=None, show_qc=False):
    """
    Run the Adaptive Hybrid Quantum Hash Search algorithm.
    Args:
        input_text (str): The input text to search.
        search_value (str): The substring to search for.
        hash_bits (int): Number of bits for the hash function.
        prime_index (int): Index of the prime number to use in the hash function.
        p_count (int): Number of qubits in the counting register.
        use_noise (bool): Whether to use noise in the simulation.
        shots (int): Number of shots for the quantum circuit.
        simulation (bool): Whether to run in simulation mode.
        counting_simulation (bool): Whether to run the counting simulation.
        verbose (bool): Whether to print detailed results.
        grover_search_circuit_func: Custom Grover search circuit function.
        quantum_counting_circuit_func: Custom quantum counting circuit function.
        show_qc (bool): Whether to show the quantum circuit.
    """
    substring_length = len(search_value)
    valid_states, n_substr, n_qubits, substrings, targets = classical_preprocessing(input_text, search_value, hash_bits, prime_index)

    # Run quantum counting.
    counts_count, qc_count_depth, qc_count_gate_count, runtime_count = run_counting(
        n_qubits, p_count, valid_states, shots=shots, use_noise=use_noise, simulation=counting_simulation,
        quantum_counting_circuit_func=quantum_counting_circuit_func, show_qc=show_qc
    )
    M_est, theta_est, r_measured = estimate_marked_state_count(counts_count, p_count, n_substr)

    # Determine optimal Grover iterations.
    optimal_iterations = 0 if M_est < 1e-6 else int(round((math.pi / 4) * math.sqrt(n_substr / M_est)))

    # Run Grover search.
    counts_search, qc_search_depth, qc_search_gate_count, runtime_search = run_grover_search(
        n_qubits, valid_states, optimal_iterations, shots=shots, use_noise=use_noise, simulation=simulation,
        grover_search_circuit_func=grover_search_circuit_func, possible_states=substrings, targets=targets, show_qc=show_qc
    )

    # Validate Grover results.
    valid_indices = {int(bs, 2) for bs in valid_states}
    total_shots = sum(counts_search.values())
    valid_shots = sum(
        count for outcome, count in counts_search.items()
        if int(outcome[::-1], 2) in valid_indices
    )
    valid_fraction = valid_shots / total_shots if total_shots > 0 else 1.0

    # Expected phase (ideal) based on true marked states.
    true_M = len(valid_states)
    expected_theta = 2 * math.asin(math.sqrt(true_M / n_substr)) if true_M > 0 else None

    # Compute error metrics and statistics.
    abs_error, rel_error = compute_errors(M_est, true_M)
    mean_r, var_r = compute_statistics(counts_count)

    results = {
        "counts_count": counts_count,
        "M_est": M_est,
        "theta_est": theta_est,
        "r_measured": r_measured,
        "optimal_iterations": optimal_iterations,
        "counts_search": counts_search,
        "qc_count_depth": qc_count_depth,
        "qc_count_gate_count": qc_count_gate_count,
        "runtime_count": runtime_count,
        "qc_search_depth": qc_search_depth,
        "qc_search_gate_count": qc_search_gate_count,
        "runtime_search": runtime_search,
        "valid_fraction": valid_fraction,
        "n_substr": n_substr,
        "n_qubits": n_qubits,
        "p_count": p_count,
        "filtered_states": valid_states,
        "expected_theta": expected_theta,
        "abs_error": abs_error,
        "rel_error": rel_error,
        "mean_r": mean_r,
        "var_r": var_r
    }

    if verbose:
        print_summary(results, input_text, search_value, substring_length, n_substr, n_qubits, p_count)

    return results


def print_summary(results, input_text, search_value, substring_length, n_substr, n_qubits, p_count):
    print("=== Adaptive Hybrid Quantum Hash Search Summary ===")
    print(f"Input text: {input_text}")
    print(f"Search value: {search_value}")
    print(f"Substring length: {substring_length}")
    print(f"Number of substrings (N): {n_substr}")
    print(f"Number of search qubits: {n_qubits}")
    print(f"Counting register qubits: {p_count}")
    print(f"Filtered valid states (binary): {results['filtered_states']}")
    print("\n--- Quantum Counting ---")
    print("Counting register results:", results["counts_count"])
    print(f"Estimated phase (theta): {results['theta_est']:.4f} rad (from measurement: {results['r_measured']})")
    if results["expected_theta"] is not None:
        print(f"Expected phase (theta): {results['expected_theta']:.4f} rad")
    print(f"Estimated marked states: {results['M_est']:.2f} out of {n_substr}")
    print(f"Absolute error in M: {results['abs_error']:.2f}")
    print(f"Relative error in M: {results['rel_error'] * 100:.1f}%")
    print(f"Weighted mean of r: {results['mean_r']:.2f}")
    print(f"Variance of r: {results['var_r']:.2f}")
    print(f"Quantum Counting circuit depth: {results['qc_count_depth']}, gate count: {results['qc_count_gate_count']}")
    print(f"Quantum Counting runtime: {results['runtime_count']:.4f} sec")
    print("\n--- Adaptive Grover Search ---")
    print(f"Optimal Grover iterations: {results['optimal_iterations']}")
    print("Grover search raw results:", results["counts_search"])
    print(f"Grover search circuit depth: {results['qc_search_depth']}, gate count: {results['qc_search_gate_count']}")
    print(f"Grover search runtime: {results['runtime_search']:.4f} sec")
    print(f"Fraction of valid outcomes: {results['valid_fraction'] * 100:.1f}%")

