import matplotlib
# This is a workaround for the issue with matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

def plot_results(counts):
    """
    Plot the results of the quantum search.
    Args:
        counts (dict): dictionary of counts from the quantum search.
    """
    fig = plot_histogram(counts)
    plt.show(block=True)
