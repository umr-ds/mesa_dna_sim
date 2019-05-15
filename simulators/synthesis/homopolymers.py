def default_error_function(homopolymere_length, base=None):
    # we might apply different rules based on the base the homopolymere consists of
    if homopolymere_length < 3:
        return 0
    elif homopolymere_length < 4:
        return 0.3
    elif homopolymere_length < 5:
        return 0.6
    elif homopolymere_length < 6:
        return 0.9
    else:
        return 1.0
    # return min(1.0, tmp)


def create_result(startpos, endpos, errorprob):
    res = dict()
    res['startpos'] = startpos
    res['endpos'] = endpos
    res['errorprob'] = errorprob
    return res


def homopolymer(sequence, apply_for=None, error_function=default_error_function):
    # returns a list of dicts, each dict has the following entries: base, startpos, endpos, errorprob
    result = []
    if apply_for is None:
        apply_for = {'G', 'T', 'A', 'C'}
    prev_char = sequence[0]
    curr_start_pos = 0
    length = len(sequence)
    for char_pos in range(1, length):
        if prev_char != sequence[char_pos]:
            error_prob = error_function(char_pos - curr_start_pos)
            if error_prob > 0.0:
                tmp = create_result(curr_start_pos, char_pos - 1, error_prob)
                tmp['base'] = prev_char
                result.append(tmp)
            curr_start_pos = char_pos
            prev_char = sequence[char_pos]
    error_prob = error_function(length - curr_start_pos)
    if error_prob > 0.0:
        tmp = create_result(curr_start_pos, length - 1, error_prob)
        tmp['base'] = prev_char
        result.append(tmp)
    return result


if __name__ == "__main__":
    print(homopolymer("AAAAAAAAAACACACTTTTTTTTAAAAAAAAAAA"))
    # print(homopolymer("AAAAGGGGGGCGGGGAGCCCTTTTTCGCGCCCCCCGGGGTTTTTT"))
