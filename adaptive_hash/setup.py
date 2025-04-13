import time
import math
import csv
from qsearch.adaptive_search import run_full_search
from qsearch.utils import generate_input_text_fixed


class AHQuHSSA:
    def __init__(self,
                 test_results_file="results.csv",
                 repeats=1,
                 p_count_range=None,
                 shots_list=None,
                 target_n_qubits=None,
                 search_values=None,
                 num_correct_list=None,
                 hash_bits=4,
                 simulation=True,
                 verbose=True,
                 prime_index=6,
                 show_qc=False,
                 plot_results=False):
        """
        Helper class to run the Adaptive Hybrid Quantum Hash String Search Algorithm (AHQuHSSA).
        This class is designed to perform a series of tests with various parameters and
        configurations, and to log the results in a CSV file.
        Arguments can be passed to customize the test parameters, including the number of
        repetitions, the range of qubits, the number of shots, and the target substrings.

        Args:
            test_results_file (str): Path to the CSV file where results will be saved.
            repeats (int): Number of repetitions for averaging results.
            p_count_range (list): List of integers representing the range of counting qubits. Default is [5].
            shots_list (list): List of integers representing the number of shots for each test. Default is [1024].
            target_n_qubits (list): List of integers representing the target number of qubits. Default is [5].
            search_values (list): List of strings representing the substrings to search for. Default is ["ing", "pat"].
            num_correct_list (list): List of integers representing the number of correct substrings. Default is [1].
            hash_bits (int): Number of bits for the hash function.
            simulation (bool): If True, run the tests in simulation mode.
            verbose (bool): If True, print detailed output during the tests.
            prime_index (int): Index used to select the prime for hashing.
            show_qc (bool): If True, print the quantum circuit.
            plot_results (bool): If True, plot the results after each test.
        """

        self.test_results_file = test_results_file
        self.repeats = repeats
        self.p_count_range = p_count_range if p_count_range is not None else [5]
        self.shots_list = shots_list if shots_list is not None else [1024]
        self.target_n_qubits = target_n_qubits if target_n_qubits is not None else [5]
        self.search_values = search_values if search_values is not None else ["ing", "pat"]
        self.num_correct_list = num_correct_list if num_correct_list is not None else [1]
        self.hash_bits = hash_bits
        self.simulation = simulation
        self.verbose = verbose
        self.prime_index = prime_index
        self.show_qc = show_qc
        self.plot_results = plot_results

    def run_tests(self):
        fieldnames = [
            "timestamp", "target_list", "input_length", "n_substr", "n_qubits", "num_correct",
            "p_count", "shots", "optimal_iterations", "estimated_M", "abs_error", "rel_error",
            "expected_theta", "theta_est", "r_measured", "mean_r", "var_r", "valid_fraction",
            "qc_count_depth", "qc_count_gate_count", "runtime_count",
            "qc_search_depth", "qc_search_gate_count", "runtime_search",
            "run_time_sec"
        ]

        with open(self.test_results_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Iterate over all test parameter combinations.
            for p_count in self.p_count_range:
                for shots in self.shots_list:
                    for n_qubits_target in self.target_n_qubits:
                        for num_correct in self.num_correct_list:
                            current_targets = self.search_values[:num_correct]
                            L = len(current_targets[0])
                            input_length = (2 ** n_qubits_target) + L - 1

                            # Initialize accumulators for metrics over the repetitions.
                            accum = {
                                "run_time": 0,
                                "optimal_iterations": 0,
                                "estimated_M": 0,
                                "abs_error": 0,
                                "rel_error": 0,
                                "expected_theta": 0,
                                "theta_est": 0,
                                "r_measured": 0,
                                "mean_r": 0,
                                "var_r": 0,
                                "valid_fraction": 0,
                                "qc_count_depth": 0,
                                "qc_count_gate_count": 0,
                                "runtime_count": 0,
                                "qc_search_depth": 0,
                                "qc_search_gate_count": 0,
                                "runtime_search": 0,
                            }

                            # Run the test for the configured number of repeats.
                            for _ in range(self.repeats):
                                try:
                                    input_text = generate_input_text_fixed(
                                        input_length,
                                        search_values=current_targets
                                    )
                                except ValueError as e:
                                    print(e)
                                    continue

                                start_time = time.time()
                                results = run_full_search(
                                    input_text,
                                    current_targets,
                                    hash_bits=self.hash_bits,
                                    prime_index=self.prime_index,
                                    p_count=p_count,
                                    use_noise=True,
                                    shots=shots,
                                    simulation=self.simulation,
                                    verbose=self.verbose,
                                    show_qc=self.show_qc,
                                )
                                end_time = time.time()
                                run_time = end_time - start_time

                                # Compute the absolute and relative errors.
                                abs_error = abs(results["M_est"] - num_correct)
                                rel_error = abs_error / num_correct if num_correct != 0 else 0

                                counts_count = results["counts_count"]
                                total_shots = sum(counts_count.values())
                                mean_r = sum(int(k, 2) * v for k, v in counts_count.items()) / total_shots
                                var_r = sum(((int(k, 2) - mean_r) ** 2) * v for k, v in counts_count.items()) / total_shots

                                expected_theta = 2 * math.asin(
                                    math.sqrt(num_correct / results["n_substr"])
                                ) if num_correct > 0 else None

                                # Accumulate metrics.
                                accum["run_time"] += run_time
                                accum["optimal_iterations"] += results["optimal_iterations"]
                                accum["estimated_M"] += results["M_est"]
                                accum["abs_error"] += abs_error
                                accum["rel_error"] += rel_error
                                accum["expected_theta"] += expected_theta if expected_theta is not None else 0
                                accum["theta_est"] += results["theta_est"]
                                accum["r_measured"] += results["r_measured"]
                                accum["mean_r"] += mean_r
                                accum["var_r"] += var_r
                                accum["valid_fraction"] += results["valid_fraction"]
                                accum["qc_count_depth"] += results["qc_count_depth"]
                                accum["qc_count_gate_count"] += results["qc_count_gate_count"]
                                accum["runtime_count"] += results["runtime_count"]
                                accum["qc_search_depth"] += results["qc_search_depth"]
                                accum["qc_search_gate_count"] += results["qc_search_gate_count"]
                                accum["runtime_search"] += results["runtime_search"]

                            # Calculate averages over the number of repeats.
                            avg = {k: v / self.repeats for k, v in accum.items()}
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            writer.writerow({
                                "timestamp": timestamp,
                                "target_list": ",".join(current_targets),
                                "input_length": input_length,
                                "n_substr": results["n_substr"],
                                "n_qubits": results["n_qubits"],
                                "num_correct": num_correct,
                                "p_count": p_count,
                                "shots": shots,
                                "optimal_iterations": avg["optimal_iterations"],
                                "estimated_M": avg["estimated_M"],
                                "abs_error": avg["abs_error"],
                                "rel_error": avg["rel_error"],
                                "expected_theta": avg["expected_theta"],
                                "theta_est": avg["theta_est"],
                                "r_measured": avg["r_measured"],
                                "mean_r": avg["mean_r"],
                                "var_r": avg["var_r"],
                                "valid_fraction": avg["valid_fraction"],
                                "qc_count_depth": avg["qc_count_depth"],
                                "qc_count_gate_count": avg["qc_count_gate_count"],
                                "runtime_count": avg["runtime_count"],
                                "qc_search_depth": avg["qc_search_depth"],
                                "qc_search_gate_count": avg["qc_search_gate_count"],
                                "runtime_search": avg["runtime_search"],
                                "run_time_sec": avg["run_time"]
                            })
                            csvfile.flush()

                            print(
                                f"Test: target_list={current_targets}, p_count={p_count}, shots={shots}, "
                                f"target n_qubits={n_qubits_target}, num_correct={num_correct}, "
                                f"avg time = {avg['run_time']:.3f}s, count_depth = {avg['qc_count_depth']}, "
                                f"search_depth = {avg['qc_search_depth']}, valid fraction = {avg['valid_fraction'] * 100:.1f}%"
                            )
                            from qsearch.plotting import plot_results
                            if self.plot_results:
                                plot_results(results["counts_count"])
