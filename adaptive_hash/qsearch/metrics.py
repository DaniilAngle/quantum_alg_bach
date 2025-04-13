import math

def estimate_marked_state_count(counts, p_count, n_substr):
    """
    Estimate the number of marked states based on the measurement counts.
    Args:
        counts (dict): Dictionary of measurement counts.
        p_count (int): Number of qubits in the counting register.
        n_substr (int): Number of substrings in the input text.
    Returns:
        tuple: Estimated marked state count (M_est), estimated phase (theta_est), and measured value (r).
    """
    most_common = max(counts, key=counts.get)
    r = int(most_common, 2)
    theta_est = (r / (2 ** p_count)) * 2 * math.pi
    M_est = n_substr * (1 - (math.sin(theta_est / 2)) ** 2)
    return M_est, theta_est, r

def compute_errors(M_est, true_M):
    """
    Compute absolute and relative errors between estimated and true marked state counts.
    Args:
        M_est (float): Estimated marked state count.
        true_M (int): True marked state count.
    Returns:
        tuple: Absolute error and relative error.
    """
    abs_error = abs(M_est - true_M)
    rel_error = abs_error / true_M if true_M != 0 else 0
    return abs_error, rel_error

def compute_statistics(counts):
    """
    Compute mean and variance of the measurement results.
    Args:
        counts (dict): Dictionary of measurement counts.
    Returns:
        tuple: Mean and variance of the measurement results.
    """
    total_shots = sum(counts.values())
    mean_r = sum(int(k, 2) * v for k, v in counts.items()) / total_shots
    var_r = sum(((int(k, 2) - mean_r) ** 2) * v for k, v in counts.items()) / total_shots
    return mean_r, var_r

