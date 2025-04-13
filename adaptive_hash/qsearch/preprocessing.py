import math
from .hashing import compare_hash, make_hash

def compute_n_qubits(n_substr):
    """
    Compute the number of qubits needed for the given number of substrings.
    Args:
        n_substr (int): Number of substrings.
    Returns:
        int: Number of qubits needed.
    """
    return math.ceil(math.log2(n_substr))

def classical_preprocessing(input_text, search_values, hash_bits=8, prime_index=1):
    """
    Preprocess the input text and search values to prepare for quantum search.
    Args:
        input_text (str): The input text to search within.
        search_values (list): List of values to search for in the input text.
        hash_bits (int): Number of bits for the hash.
        prime_index (int): Index used to select the prime for hashing.
    Returns:
        tuple: A tuple containing valid states, number of substrings, number of qubits,
               list of substrings, and list of targets.
    """
    substring_length = len(search_values[0])
    n_substr = len(input_text) - substring_length + 1
    n_qubits = compute_n_qubits(n_substr)
    valid_states = []
    substrings = []
    targets = []
    for i in range(n_substr):
        substring = input_text[i:i + substring_length]
        hash_substring = format(make_hash(substring, hash_bits, prime_index), f'0{hash_bits}b')
        substrings.append(hash_substring)
        if substring in search_values:
            targets.append(hash_substring)
        for search_value in search_values:
            if compare_hash(substring, search_value, hash_bits, prime_index):
                valid_states.append(format(i, f'0{n_qubits}b'))
    return valid_states, n_substr, n_qubits, substrings, targets

