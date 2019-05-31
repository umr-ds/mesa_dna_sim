from sequencing_error import SequencingError
import random


class Nanopore(SequencingError):
    """
    Class for the simulation of errors that can occur using the Oxford
    Nanopore technology.

    Arguments:
    method -- Which variation of the Nanopore method should be
    simulated, this is used to define the rates for the different
    errors.
        Possible values:
            '1D' -- Sequencing one strand of the duplex DNA.
            '2D' -- Sequencing both the template and the complementary
            strand.
            'user' -- User defined error rates, a dictionary in the form
            user_rates = {"raw_rate": x, "mismatch": y, "deletion": z,
            "insertion": a},
            the raw_rate defines the overall error rate, the specific
            error forms define the fraction of the total error the
            specific error occurs.
    seq -- The input DNA sequence in capital letters.
    attributes -- Attributes (like positioning, preferred bases) for
    the different error types.
        Possible values:
            None -- Attributes based on 10.12688/f1000research.10571.2
            False -- No Attributes are used
            or a dictionary in the form:
            {"deletion": {"position" :{"homopolymer" : x, "random" : y},
                          "pattern": {"G":x, "C":y, "A":z, "T":a}},
             "insertion" : {"position" :{"homopolymer" : x, "random" : y},
                            "pattern": {"A":x, "T":y "C":z "G":a}},
             "mismatch": {"pattern": {"TAG":"TGG", "TAC":"TGC"}}}
    """
    def __init__(self, method, seq, attributes=None, user_rates=None):
        super().__init__(seq, attributes)
        self.in_seq = seq
        if method == '1D':
            self.error_rates = {"raw_rate": 0.2, "mismatch": 0.48, "deletion": 0.37, "insertion": 0.15}
        elif method == '2D':
            self.error_rates = {"raw_rate": 0.13, "mismatch": 0.41, "deletion": 0.36, "insertion": 0.23}
        elif method == 'user':
            self.error_rates = user_rates
        else:
            raise ValueError(
                "Supported sequencing methods are: '1D' "
                "(sequencing one strand of the duplex DNA), "
                "'2D' (sequencing both the template and the "
                "complementary strand) or 'user' (using "
                "custom error rates)")
        if attributes is None:
            self.attributes = {"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                            "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                               "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                             "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                               "mismatch": {"pattern": {"TAG": "TGG", "TAC": "TGC"}}}


if __name__ == "__main__":
    def testing():
        # Patterns
        attributes = {"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                   "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                      "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                    "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                      "mismatch": {"pattern": {"TAG": "TGG", "TAC": "TGC"}}}

        nano = Nanopore('2D', 'ATGC', attributes)

        # Test sequence with homopolymers
        seq1 = ''.join(random.choices(['A', 'T', 'G', 'C'], k=20000))

        # Test sequence without homopolymers
        seq_l = []
        while len(seq_l) < 20000:
            c1 = random.choice(['A', 'T', 'G', 'C'])
            if not seq_l or seq_l[-1] != c1:
                seq_l.append(c1)
        seq2 = "".join(seq_l)

        # Run
        for seq in [seq1, seq2]:
            nano.seq = seq
            for mutation_type in ['insertion', 'deletion', 'mismatch']:
                err_rate = nano.error_rates["raw_rate"] * nano.error_rates[str(mutation_type)]
                for n in range(round((len(nano.seq) * err_rate))):
                    nano.seq = eval('nano.' + mutation_type)(prob=None)
                nano.seq = eval('nano.' + mutation_type)(err_rate)

        return nano


    test = testing()
    print(test.checks)
