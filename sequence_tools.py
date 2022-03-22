MEMOIZED_SUBSEQUENCES = {}


def generate_subsequences(
    sequence: list,
    max_subsequence: int = 8,
    *,
    _iterations: bool = False,
) -> set | tuple[set, int]:
    """
    Generates all possible subsequences for a given sequence. Subsequences are memoized for future function calls.
    """
    subsequences = set()
    iterations = 0

    if tuple(sequence) in MEMOIZED_SUBSEQUENCES:
        subsequences.update(MEMOIZED_SUBSEQUENCES[tuple(sequence)])
        return subsequences, iterations

    if sequence[:-1] != []:
        prev_subsequences, prev_iterations = generate_subsequences(
            sequence[:-1],
            max_subsequence,
            _iterations=True,
        )
        subsequences.update(prev_subsequences)
        iterations += prev_iterations

    # slicing an array further than it's length slices till the end, so we only need to define max size
    max_subsequence_size = min(len(sequence), max_subsequence)
    for subsequence_position in range(0, len(sequence)):
        subsequence = tuple(
            sequence[subsequence_position:subsequence_position + max_subsequence_size]
        )
        subsequences.add(subsequence)
        iterations += 1

    MEMOIZED_SUBSEQUENCES[tuple(sequence)] = tuple(subsequences)

    if _iterations:
        return subsequences, iterations
    return subsequences
