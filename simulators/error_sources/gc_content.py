from math import ceil


def default_error_function(gc_percentage, base=None):
    """
    Default function to calculate error probabilities based on the gc_content.
    :param gc_percentage: gc_content
    :param base:
    :return: Error probability based on the gc_percentage
    """
    gc_percentage = 1.0 * gc_percentage / 100.0
    if 0.5 <= gc_percentage <= 0.6:
        return 0
    elif gc_percentage > 0.6:
        return (gc_percentage - 0.6) * 2.5
    else:
        return (0.5 - gc_percentage) * 2


def create_result(startpos, endpos, errorprob, identifier):
    """
    Creates a dictionary containing all results.
    :param startpos:
    :param endpos:
    :param errorprob:
    :param identifier:
    :return:
    """
    res = dict()
    res['startpos'] = startpos
    res['endpos'] = endpos
    res['errorprob'] = errorprob
    res['identifier'] = identifier
    return res


def windowed_gc_content(sequence, window_size=15, error_function=default_error_function):
    """
    Calculates the error probabilities based on the gc_content for subsequences based on the windows_size.
    :param sequence: Sequence to calculate the error probabilities for.
    :param window_size: Window_size to use for the calculation.
    :param error_function: Error_function to use for the calculation.
    :return: List of results with error probabilities and other information.
    """
    if error_function is None:
        error_function = default_error_function
    # returns a list of dicts, each dict has the following entries: base, startpos, endpos, errorprob
    result = []
    length = len(sequence)
    no_windows = ceil(1.0 * length / window_size)
    j = 0
    for i in range(no_windows):
        basecount = dict()
        window_sequence = sequence[i * window_size:min((i + 1) * window_size, length)]
        curr_length = len(window_sequence)
        for char_pos in range(curr_length):
            if window_sequence[char_pos] in basecount:
                basecount[window_sequence[char_pos]] += 1
            else:
                basecount[window_sequence[char_pos]] = 1
        gc_sum = 1.0 * ((basecount["G"] if "G" in basecount else 0.0) + (basecount["C"] if "C" in basecount else 0.0))
        error_prob = error_function(gc_sum / curr_length * 100.0)
        if error_prob > 0.0:
            result.append(create_result(i * window_size, min((i + 1) * window_size - 1, length-1), error_prob,
                                        "window_gc_content_" + str(j)))
            j += 1
    return result


def overall_gc_content(sequence, error_function=default_error_function):
    """
    Calculates the gc_content for a whole sequence and returns the error probabilities based on the content.
    :param sequence:
    :param error_function:
    :return:
    """
    if error_function is None:
        error_function = default_error_function
    # returns a list of dicts, each dict has the following entries: base, startpos, endpos, errorprob
    result = []
    length = len(sequence)
    basecount = dict()
    for char_pos in range(length):
        if sequence[char_pos] in basecount:
            basecount[sequence[char_pos]] += 1
        else:
            basecount[sequence[char_pos]] = 1
    gc_sum = 1.0 * (basecount["G"] if "G" in basecount else 0.0 + basecount["C"] if "C" in basecount else 0.0)
    error_prob = error_function(gc_sum / length)
    result.append(create_result(0, length, error_prob, "overall_gc_content_0"))
    return result


if __name__ == "__main__":
    print([default_error_function(1.0 * x / 100.0) for x in range(101)])
    print(overall_gc_content("AAAAAAAAGAACACACTTTTTTTTAAAAAAAAAAA"))
    print(windowed_gc_content("GCGCATATATATATATATAGCGCGCGCGCGCGCG"))
