import setup


def main():
    # Define the parameters for the algorithm
    ahquhssa = setup.AHQuHSSA(
        test_results_file="results.csv",
        repeats=1,
        p_count_range=[4],
        shots_list=[1024],
        target_n_qubits=[3, 4],
        search_values=["ing", "pat"],
        num_correct_list=[1, 2],
        hash_bits=8,
        simulation=True,
        verbose=True,
        prime_index=1,
        show_qc=True,
        plot_results=True,
    )

    # Run the algorithm
    ahquhssa.run_tests()

if __name__ == "__main__":
    main()