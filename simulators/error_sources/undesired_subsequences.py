import regex as re

undesired_ssequences = {"ATAACTTCGTATAGCATACATTATACGAAGTTAT": 0.9, "ATAACTTCGTATAGCATACATTATACGAACGGTA": 0.9,
                        "TACCGTTCGTATAGCATACATTATACGAAGTTAT": 0.9, "TACCGTTCGTATAGCATACATTATACGAACGGTA": 0.9,
                        "TACCGTTCGTATATGGTATTATATACGAAGTTAT": 0.9, "TACCGTTCGTATATTCTATCTTATACGAAGTTAT": 0.9,
                        "TACCGTTCGTATAGGATACTTTATACGAAGTTAT": 0.9, "TACCGTTCGTATATACTATACTATACGAAGTTAT": 0.9,
                        "TACCGTTCGTATACTATAGCCTATACGAAGTTAT": 0.9, "ATAACTTCGTATATGGTATTATATACGAACGGTA": 0.9,
                        "ATAACTTCGTATAGTATACCTTATACGAAGTTAT": 0.9, "ATAACTTCGTATAGTATACATTATACGAAGTTAT": 0.9,
                        "ATAACTTCGTATAGTACACATTATACGAAGTTAT": 0.9,
                        "GCATACAT": 0.9, "TGGTATTA": 0.9, "TTCTATCT": 0.9, "GGATACTT": 0.9, "TACTATAC": 0.9,
                        "CTATAGCC": 0.9, "AGGTATGC": 0.9, "TTGTATGG": 0.9, "GGATAGTA": 0.9, "GTGTATTT": 0.9,
                        "GGTTACGG": 0.9, "TTTTAGGT": 0.9, "GTATACCT": 0.9, "GTACACAT": 0.9, "GAAGAC": 0.9,
                        "GGTCTC": 0.9}


def undesired_subsequences(sequence, dict_of_subsequences=None):
    if dict_of_subsequences is None:
        dict_of_subsequences = undesired_ssequences
    res = []
    # for undesired_sequence, error_prob in list_of_subsequences:
    regextext = "|".join(dict_of_subsequences.keys())
    for m in re.finditer(regextext, sequence, overlapped=True):
        res.append({'startpos': m.start(), 'endpos': m.start() + len(m.group(0)) - 1,
                    'errorprob': dict_of_subsequences[m.group(0)],
                    'undesired_sequence': m.group(0)})
    return res


if __name__ == "__main__":
    txt = """ATAACTTCGTATAGCATACATTATACGAAGTTAT 0.9
ATAACTTCGTATAGCATACATTATACGAACGGTA 0.9
TACCGTTCGTATAGCATACATTATACGAAGTTAT 0.9
TACCGTTCGTATAGCATACATTATACGAACGGTA 0.9
TACCGTTCGTATATGGTATTATATACGAAGTTAT 0.9
TACCGTTCGTATATTCTATCTTATACGAAGTTAT 0.9
TACCGTTCGTATAGGATACTTTATACGAAGTTAT 0.9
TACCGTTCGTATATACTATACTATACGAAGTTAT 0.9
TACCGTTCGTATACTATAGCCTATACGAAGTTAT 0.9
ATAACTTCGTATATGGTATTATATACGAACGGTA 0.9
ATAACTTCGTATAGTATACCTTATACGAAGTTAT 0.9
ATAACTTCGTATAGTATACATTATACGAAGTTAT 0.9
ATAACTTCGTATAGTACACATTATACGAAGTTAT 0.9
GCATACAT 0.9
TGGTATTA 0.9
TTCTATCT 0.9
GGATACTT 0.9
TACTATAC 0.9
CTATAGCC 0.9
AGGTATGC 0.9
TTGTATGG 0.9
GGATAGTA 0.9
GTGTATTT 0.9
GGTTACGG 0.9
TTTTAGGT 0.9
GTATACCT 0.9
GTACACAT 0.9
GAAGAC 0.9
GGTCTC 0.9"""
    sequence = "ATAACTTCGTATAGTACACATTATACGAAGTTATCTATAGCCTACCGTTCGTATACTATAGCCTATACGAAGTTATGTACACATGAAGACGAGCCGCG"
    undesired_subsequence = {}
    for line in txt.splitlines():
        seq, prob = line.split(" ")
        undesired_subsequence[seq] = float(prob)

    print(undesired_subsequences(sequence, undesired_subsequence))
