from copy import copy

MAX_TOKEN_SIZE = 8
MEMOIZED_TOKENS = {}


def generate_sequence_tokens(sequence):
    tokens = set()
    iterations = 0

    for token_start_position in range(0, len(sequence)):
        for token_size in range(1, MAX_TOKEN_SIZE):
            token = tuple(sequence[token_start_position:token_start_position + token_size])

            tokens.add(token)
            iterations += 1

            # exit if we're at the end of the build
            if token_start_position + token_size >= len(sequence):
                break

    return tokens, iterations

def generate_sequence_tokens_size(sequence):
    tokens = set()
    iterations = 0
    prev_window = None

    for sequence_size in range(1, len(sequence) + 1):
        sequence_window = tuple(sequence[:sequence_size])
        window_tokens = set()

        # if sequence size is 1 then skip everything

        # print('current memoized', MEMOIZED_TOKENS)
        # print('current sequence window', sequence_window)
        if sequence_window in MEMOIZED_TOKENS:
            # print('found memoized token', MEMOIZED_TOKENS[sequence_window])
            prev_window = copy(sequence_window)
            tokens.update(MEMOIZED_TOKENS[sequence_window])
            continue

        if prev_window in MEMOIZED_TOKENS:
            print('filling with previously memoized tokens', sequence_window, prev_window)
            window_tokens.update(MEMOIZED_TOKENS[prev_window])
            filled_tokens, filled_iterations = _fill_memoized_sequence(sequence_size, sequence_window, len(prev_window))

            print('filled tokens', filled_tokens, filled_iterations)

            prev_window = copy(sequence_window)
            window_tokens.update(filled_tokens)
            MEMOIZED_TOKENS[sequence_window] = copy(window_tokens)
            iterations += filled_iterations
            print('window tokens', window_tokens)
            tokens.update(window_tokens)
            continue

        for token_start_position in range(0, len(sequence_window)):
            for token_size in range(1, min(len(sequence_window), MAX_TOKEN_SIZE) + 1):
                token = tuple(sequence_window[token_start_position:token_start_position + token_size])

                window_tokens.add(token)
                iterations += 1

                # exit if we're at the end of the build
                if token_start_position + token_size >= sequence_size:
                    break

        MEMOIZED_TOKENS[sequence_window] = copy(window_tokens)
        prev_window = copy(sequence_window)
        tokens.update(window_tokens)
        print('window tokens', window_tokens)
        # print('new sequence window', sequence_window)
        # print('new memoized', MEMOIZED_TOKENS[sequence_window], '\n')

    return tokens, iterations

def _fill_memoized_sequence(sequence_size, sequence_window, prev_window_size):
    window_tokens = set()
    iterations = 0

    print('filling sequence', sequence_size, sequence_window, prev_window_size)

    # memoized_token_position = prev_window_size
    # for token_size in range(1, min(len(sequence_window), MAX_TOKEN_SIZE) + 1):
    #     token = tuple(sequence_window[memoized_token_position:memoized_token_position + token_size])
    #     print('filled position token', token)

    #     window_tokens.add(token)
    #     iterations += 1

    #     # exit if we're at the end of the build
    #     if memoized_token_position + token_size >= sequence_size:
    #         break

    memoized_token_size = min(prev_window_size, MAX_TOKEN_SIZE) + 1
    for token_start_position in range(0, len(sequence_window)):
        token = tuple(sequence_window[token_start_position:token_start_position + memoized_token_size])
        print('filled size token', token)

        window_tokens.add(token)
        iterations += 1

        # exit if we're at the end of the build
        if token_start_position >= sequence_size - 1:
            break

    # window_size_diff = len(sequence_window) - prev_window_size
    # for token_size in range(window_size_diff + 1, min(len(sequence_window), MAX_TOKEN_SIZE) + 1):
    #     # start with +1 overlap relative to previous window
    #     overlap_start_position = (prev_window_size + 1) - token_size
    #     token = tuple(sequence_window[overlap_start_position:overlap_start_position + token_size])
    #     print('filled diff token', token)

    #     window_tokens.add(token)
    #     iterations += 1

    #     # exit if we're at the end of the build
    #     if token_start_position + token_size >= sequence_size:
    #         break

    return window_tokens, iterations


# what happens with sequences of the same length?
# what happens with sequences of different length but no common ancestor?
# what about memoizing subsequences instead of just full sequences? I.e. midway through a sequence

# assumes sequences are direct ancestors and have different lengths
def subsequence_diff(sequence, other_sequence=[], max_subsequence=8, *, memo=None):
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

    if sequence_length_diff == 1 and sequence != [] and sequence != other_sequence[:-1]:
        raise ValueError(f'Cannot compare sequences with different ancestors. Expected ancestor sequence to be {sequence} but got {other_sequence[:-1]}')

    if sequence_length_diff > 1:
        prev_subsequences, prev_iterations = subsequence_diff(sequence, other_sequence[:-1], max_subsequence, memo=memo)
        subsequences.update(prev_subsequences)
        iterations += prev_iterations

    subsequence_start_size = min(len(other_sequence), max_subsequence)
    for subsequence_start_position in range(0, len(other_sequence)):
        subsequence = tuple(other_sequence[subsequence_start_position:subsequence_start_position + subsequence_start_size])

        # print('diff token', subsequence, subsequence_start_position, subsequence_start_size)

        subsequences.add(subsequence)
        iterations += 1

    if memo is not None:
        if sequence == []:
            total_sequence = set(memo[tuple(other_sequence[:-1])]) if len(other_sequence) != 1 else set()
            total_sequence.update(subsequences)
            memo[tuple(other_sequence)] = tuple(total_sequence)

        if tuple(sequence) in memo:
            total_sequence = set(memo[tuple(sequence)])
            total_sequence.update(subsequences)
            memo[tuple(other_sequence)] = tuple(total_sequence)

        # print('memo', sequence, other_sequence, memo)

    return subsequences, iterations

def generate_build_tokens(buildings):
    tokens = set()
    iterations = 0

    if tuple(buildings) in MEMOIZED_TOKENS:
        return MEMOIZED_TOKENS[tuple(buildings)], iterations

    # reverse-scan build for memoized ancestors
    print(buildings)
    for i in range(1, len(buildings) + 1):
        partial_build = buildings[:-i]
        iterations += 1

        if tuple(partial_build) in MEMOIZED_TOKENS:
            tokens.add(MEMOIZED_TOKENS[tuple(partial_build)])
            diff_tokens, diff_iterations = subsequence_diff(partial_build, buildings, memo=MEMOIZED_TOKENS)
            tokens.update(diff_tokens)
            iterations += diff_iterations
            break

        if partial_build == []:
            diff_tokens, diff_iterations = subsequence_diff(buildings, memo=MEMOIZED_TOKENS)
            tokens.update(diff_tokens)
            iterations += diff_iterations
            break

    return tokens, iterations



sequence = [n for n in range(1, 6)]
sequence2 =  [1, 2, 3, 4, 5, 6]
sequence3 = [1, 2, 5, 6]

memo = {}

print('first sequence', subsequence_diff(sequence, memo=memo))
diff, iters = subsequence_diff(sequence, sequence2, memo=memo)
print(diff, iters)
if len(diff) == iters:
    print('Optimal diff')

t, i = generate_build_tokens(sequence)
t2, i2 = generate_build_tokens(sequence2)

print('first sequence', t, i)
print('second sequence', t2, i2)


tokens, iterations = generate_sequence_tokens(sequence)
print('\n', iterations, tokens, '\n')
tokens2, iterations2 = generate_sequence_tokens(sequence)
print('\n', iterations2, tokens2, '\n')
tokens3, iterations3 = generate_sequence_tokens(sequence2)
print('\n', iterations3, tokens3, '\n')
tokens4, iterations4 = generate_sequence_tokens(sequence3)
print('\n', iterations4, tokens4, '\n')

size_tokens, size_iterations = generate_sequence_tokens_size(sequence)
print('\n', size_iterations, size_tokens, '\n')
size_tokens2, size_iterations2 = generate_sequence_tokens_size(sequence)
print('\n', size_iterations2, size_tokens2, '\n')
size_tokens3, size_iterations3 = generate_sequence_tokens_size(sequence2)
print('\n', size_iterations3, size_tokens3, '\n')
size_tokens4, size_iterations4 = generate_sequence_tokens_size(sequence3)
print('\n', size_iterations4, size_tokens4, '\n')

print('memoized tokens')
for s, t in MEMOIZED_TOKENS.items():
    print(s, t)
