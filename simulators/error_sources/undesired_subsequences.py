import regex as re

undesired_ssequences = [
    {
        "sequence": "TATAAA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Eukaryotic promotor recognition motif https://doi.org/10.1016/0022-2836(90)90223-9"
    },
    {
        "sequence": "TTGACA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Prokaryotic promoter recognition motif https://doi.org/10.1016/j.jmb.2011.01.018"
    },
    {
        "sequence": "TGTATAATG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Prokaryotic promoter recognition motif https://doi.org/10.1016/j.jmb.2011.01.018"
    },
    {
        "sequence": "GCCACCATGG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Eukaryotic ribosomal binding site https://doi.org/10.1016/0022-2836(87)90418-9"
    },
    {
        "sequence": "ACCACCATGG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Eukaryotic ribosomal binding site https://doi.org/10.1016/0022-2836(87)90418-9"
    },
    {
        "sequence": "AATAAA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Eukaryotic polyadenylation signal https://doi.org/10.1016/0092-8674(87)90292-3"
    },
    {
        "sequence": "TTGTGTGTTG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Eukaryotic polyadenylation signal https://doi.org/10.1016/0092-8674(87)90292-3"
    },
    {
        "sequence": "ATAACTTCGTATAGCATACATTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "loxP https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "ATAACTTCGTATAGCATACATTATACGAACGGTA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "loxR https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATAGCATACATTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "loxL https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATAGCATACATTATACGAACGGTA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "loxLR https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATATGGTATTATATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "lox1R https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATATTCTATCTTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "lox2R https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATAGGATACTTTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "lox3R https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATATACTATACTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "lox4R https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TACCGTTCGTATACTATAGCCTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "lox5R https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "ATAACTTCGTATATGGTATTATATACGAACGGTA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox1L https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "ATAACTTCGTATAGTATACCTTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "loxN https://doi.org/10.1038/nature06293"
    },
    {
        "sequence": "ATAACTTCGTATAGTATACATTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "loxP 511 https://doi.org/10.1093/nar/14.5.2287"
    },
    {
        "sequence": "ATAACTTCGTATAGTACACATTATACGAAGTTAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "lox 5171 https://doi.org/10.1007/978-981-10-3874-733"
    },
    {
        "sequence": "GCATACAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer loxP WT https://doi.org/10.1007/978-981-10-3874-733"
    },
    {
        "sequence": "TGGTATTA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox1 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "TTCTATCT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox2 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "GGATACTT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox3 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "TACTATAC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox4 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "CTATAGCC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox5 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "AGGTATGC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox6 https://doi.org/10.1007/978-981-10-3874-733"
    },
    {
        "sequence": "TTGTATGG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox7 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "GGATAGTA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox8 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "GTGTATTT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox9 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "GGTTACGG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox10 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "TTTTAGGT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer lox11 https://doi.org/10.1186/1471-2164-7-73"
    },
    {
        "sequence": "GTATACCT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer loxN https://doi.org/10.1038/nature06293"
    },
    {
        "sequence": "GTACACAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Lox site spacer loxP 5171 https://doi.org/10.1007/978-981-10-3874-733"
    },
    {
        "sequence": "GAAGAC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "BbsI"
    },
    {
        "sequence": "GGTCTC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "BsaI"
    },
    {
        "sequence": "CGTCTC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "BsmBI"
    },
    {
        "sequence": "GCTCTTC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "BspQI"
    },
    {
        "sequence": "GCGATG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "BtgZI"
    },
    {
        "sequence": "CGTCTC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Esp3I"
    },
    {
        "sequence": "GCTCTTC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "SapI"
    },
    {
        "sequence": "CTCGTAGACTGCGTACCA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Adapter F https://doi.org/10.1186/1746-4811-8-32"
    },
    {
        "sequence": "GACGATGAGTCCTGAGTA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "Adapter R https://doi.org/10.1186/1746-4811-8-32"
    },
    {
        "sequence": "GGTTCCACGTAAGCTTCC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "H1 (HindIII) https://doi.org/10.1016/j.jbiotec.2003.08.005"
    },
    {
        "sequence": "GCGATTACCCTGTACACC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "B4 (BsrGI) https://doi.org/10.1016/j.jbiotec.2003.08.005"
    },
    {
        "sequence": "GCCAGTACATCAATTGCC",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "M3 (MfeI) https://doi.org/10.1016/j.jbiotec.2003.08.005"
    },
    {
        "sequence": "AAATAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - Eukaryotic promotor recognition motif https://doi.org/10.1016/0022-2836(90)90223-9"
    },
    {
        "sequence": "ACAGTT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - Prokaryotic promoter recognition motif https://doi.org/10.1016/j.jmb.2011.01.018"
    },
    {
        "sequence": "GTAATATGT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - Prokaryotic promoter recognition motif https://doi.org/10.1016/j.jmb.2011.01.018"
    },
    {
        "sequence": "GGTACCACCG",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - Eukaryotic ribosomal binding site https://doi.org/10.1016/0022-2836(87)90418-9"
    },
    {
        "sequence": "GGTACCACCA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - Eukaryotic ribosomal binding site https://doi.org/10.1016/0022-2836(87)90418-9"
    },
    {
        "sequence": "AAATAA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - Eukaryotic polyadenylation signal https://doi.org/10.1016/0092-8674(87)90292-3"
    },
    {
        "sequence": "GTTGTGTGTT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed -Eukaryotic polyadenylation signal https://doi.org/10.1016/0092-8674(87)90292-3"
    },
    {
        "sequence": "TATTGAAGCATATTACATACGATATGCTTCAATA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - loxP https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "ATGGCAAGCATATTACATACGATATGCTTCAATA",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - loxR https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TATTGAAGCATATTACATACGATATGCTTGCCAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - loxL https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "ATGGCAAGCATATTACATACGATATGCTTGCCAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - loxLR https://doi.org/10.1016/j.jbiotec.2016.06.033"
    },
    {
        "sequence": "TATTGAAGCATATATTATGGTATATGCTTGCCAT",
        "error_prob": "100.0",
        "enabled": 'true',
        "description": "reversed - lox1R https://doi.org/10.1016/j.jbiotec.2016.06.033"
    }
]


def undesired_subsequences(sequence, dict_of_subsequences=None):
    """
    Checks the sequence for undesired subsequences. If no subsequences are passed, default sequences are used.
    :param sequence:
    :param dict_of_subsequences:
    :return:
    """
    if dict_of_subsequences is None:
        dict_of_subsequences = {}
        for useq in undesired_ssequences:
            dict_of_subsequences[useq['sequence']] = [float(useq['error_prob']) / 100.0, useq['description']]
    res = []
    # for undesired_sequence, error_prob in list_of_subsequences:
    regextext = "|".join(dict_of_subsequences.keys())
    i = 0
    for m in re.finditer(regextext, sequence, overlapped=True):
        res.append({'startpos': m.start(), 'endpos': m.start() + len(m.group(0)) - 1,
                    'errorprob': dict_of_subsequences[m.group(0)][0],
                    'identifier': "subsequences_" + str(i),
                    'undesired_sequence': m.group(0),
                    'description': dict_of_subsequences[m.group(0)][1]})
        i += 1
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
