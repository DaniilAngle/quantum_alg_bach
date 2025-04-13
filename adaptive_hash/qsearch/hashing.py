def get_prime(prime_index=1):
    """
    Simple function to get a prime number based on the index.
    Args:
        prime_index (int): index of the prime number to retrieve.
    Returns:
        int: the prime number.
    """
    primes = [17, 19, 23, 29, 31, 37, 41, 43, 47]
    return primes[prime_index - 1]

def make_hash(substring, hash_bits=8, prime_index=1):
    """
    Create a hash of the substring using a prime number.
    Args:
        substring (str): the substring to hash.
        hash_bits (int): number of bits for the hash.
        prime_index (int): index used to select the prime for hashing.
    Returns:
        int: the hash value.
    """
    p = get_prime(prime_index)
    r = int.from_bytes(substring.encode('utf-8'), 'big')
    h = (r * p) % (2 ** hash_bits)
    return h

def compare_hash(substring, target, hash_bits=8, prime_index=1):
    """
    Compare the hash of the substring with the target hash.
    Args:
        substring (str): the substring to hash.
        target (str): the target string to compare against.
        hash_bits (int): number of bits for the hash.
        prime_index (int): index used to select the prime for hashing.
    Returns:
        bool: True if hashes match, False otherwise.
    """
    return make_hash(substring, hash_bits, prime_index) == make_hash(target, hash_bits, prime_index)

