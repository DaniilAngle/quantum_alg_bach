import random

def generate_input_text_fixed(input_length, search_values):
    """
    Generate a fixed-length input text with specific search values embedded at regular intervals.
    Args:
        input_length (int): The desired length of the input text.
        search_values (list): A list of search values to embed in the input text.
    Returns:
        str: The generated input text with the search values embedded.
    """
    num_correct = len(search_values)
    L = len(search_values[0])
    filler = "xxx"
    base_text = (filler * ((input_length // L) + 1))[:input_length]
    base_text = list(base_text)

    valid_positions = list(range(0, input_length - L + 1, L))
    if num_correct > len(valid_positions):
        raise ValueError("num_correct is too high for the given input_length.")
    selected_positions = random.sample(valid_positions, num_correct)
    for i, search_value in enumerate(search_values):
        base_text[selected_positions[i]:selected_positions[i] + L] = list(search_value)
    return "".join(base_text)

