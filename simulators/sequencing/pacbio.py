from sequencing_error import SequencingError


class PacBio(SequencingError):
    """
    Class for the simulation of errors that can occur using the PacBio
    technology.

    Arguments:
    method -- Which variation of the PacBio method should be
    simulated, this is used to define the rates for the different
    errors.
        Possible values:
            'Subread' --  Sequence from a single pass of a polymerase
            on a single strand of an insert within a SMRTbell template
            and no adapter sequences.
            'CCS' -- Sequence based on circular consensus sequencing.
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
        if method == 'CCS':
            self.error_rates = {"raw_rate": 0.02, "mismatch": 0.75, "deletion": 0.20, "insertion": 0.05}
        elif method == 'Subread':
            self.error_rates = {"raw_rate": 0.14, "mismatch": 0.37, "deletion": 0.21, "insertion": 0.42}
        elif method == 'user':
            self.error_rates = user_rates
        else:
            raise ValueError(
                "Supported sequencing methods are: 'Subread' "
                "(Sequence from a single pass of a polymerase), "
                "'CCS' (Sequence based on circular consensus "
                "sequencing) or 'user' (using "
                "custom error rates)")
        if attributes is None:
            self.attributes = {"deletion": {"position": {"homopolymer": 0.85, "random": 0.15},
                                            "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                               "insertion": {"position": {"homopolymer": 0.85, "random": 0.15},
                                             "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                               "mismatch": {"pattern": {"CG": ["CA", "TG"]}}}
