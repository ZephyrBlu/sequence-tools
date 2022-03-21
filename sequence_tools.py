MEMOIZED_SUBSEQUENCES = {}


def subsequence_diff(
    sequence: list,
    other_sequence: list = [],
    max_subsequence: int = 8,
    *,
    _iterations=False,
) -> set | tuple[set, int]:
    """
    Generates the set difference of subsequences between both input sequences. Sequences are memoized for future function calls.
    """
    if not other_sequence:
        other_sequence = sequence
        sequence = []

    sequence_length_diff = len(other_sequence) - len(sequence)
    subsequences = set()
    iterations = 0

    if sequence_length_diff < 0:
        raise ValueError('Sequence parameters must be ordered shortest then longest')

    if sequence_length_diff == 0:
        raise ValueError('Sequences cannot be the same length')

    # sequences must have a common ancestor sequence for the algorithm to work
    if sequence_length_diff == 1 and sequence != [] and sequence != other_sequence[:-1]:
        raise ValueError(f'Cannot compare sequences with different ancestors. Expected ancestor sequence to be {sequence} but got {other_sequence[:-1]}')

    if sequence_length_diff > 1:
        prev_subsequences, prev_iterations = subsequence_diff(
            sequence,
            other_sequence[:-1],
            max_subsequence,
            _iterations=_iterations,
        )
        subsequences.update(prev_subsequences)
        iterations += prev_iterations

    # slicing an array further than it's length slices till the end, so we only need to define max size
    max_subsequence_size = min(len(other_sequence), max_subsequence)
    for subsequence_position in range(0, len(other_sequence)):
        subsequence = tuple(
            other_sequence[subsequence_position:subsequence_position + max_subsequence_size]
        )
        subsequences.add(subsequence)
        iterations += 1

    # when generating a full set of subsequences we memoize from the bottom up
    # hash keys and values are converted to tuples so they are immutable
    if sequence == []:
        total_sequence = set(MEMOIZED_SUBSEQUENCES[tuple(other_sequence[:-1])]) if len(other_sequence) != 1 else set()
        total_sequence.update(subsequences)
        MEMOIZED_SUBSEQUENCES[tuple(other_sequence)] = tuple(total_sequence)


    # if the smaller sequence has been memoized we can memoize the larger sequence as well
    # since we have access to the full set of subsequences
    if tuple(sequence) in MEMOIZED_SUBSEQUENCES:
        total_sequence = set(MEMOIZED_SUBSEQUENCES[tuple(sequence)])
        total_sequence.update(subsequences)
        MEMOIZED_SUBSEQUENCES[tuple(other_sequence)] = tuple(total_sequence)

    if _iterations:
        return subsequences, iterations
    return subsequences


def generate_subsequences(sequence: list, *, _iterations=False) -> set | tuple[set, int]:
    """
    Generates all subsequences for a given sequence.
    """
    subsequences = set()
    iterations = 0

    if tuple(sequence) in MEMOIZED_SUBSEQUENCES:
        return MEMOIZED_SUBSEQUENCES[tuple(sequence)], iterations

    # reverse-scan sequence for memoized ancestors, aiming for largest possible memoized ancestor
    for i in range(1, len(sequence) + 1):
        partial_sequence = sequence[:-i]
        iterations += 1

        # a memoized ancestor means we only have to build the difference in subsequences
        if tuple(partial_sequence) in MEMOIZED_SUBSEQUENCES:
            subsequences.add(MEMOIZED_SUBSEQUENCES[tuple(partial_sequence)])
            diff_subsequences, diff_iterations = subsequence_diff(
                partial_sequence,
                sequence,
                _iterations=_iterations,
            )
            subsequences.update(diff_subsequences)
            iterations += diff_iterations
            break

        # if we haven't memoized any of the sequence yet we have to build the full set of subsequences
        if partial_sequence == []:
            diff_subsequences, diff_iterations = subsequence_diff(sequence, _iterations=_iterations)
            subsequences.update(diff_subsequences)
            iterations += diff_iterations
            break

    if _iterations:
        return subsequences, iterations
    return subsequences
