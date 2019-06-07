from simulators.error_sources.homopolymers import homopolymer
import numpy as np
import random
import re

# err_rates and mutation attributes for PacBio (keys 3-6) are based on Attributes based on
# 10.12688/f1000research.10571.2, for Illumina (key 1&2), they are based on 10.1186/s12859-016-0976-y.
# The Illumina err_rates for the different types do not add up to 1, either some other form of error (Bases that
# could not be identified / N's?) are responsible for the rest of the errors or the people that wrote the
# paper were wrong. Also, for paired end I just summed the error rates for the R1 and R2 reads and divided it by 2.

err_rates = {"1": {"raw_rate": 0.0021, "mismatch": 0.81, "deletion": 0.0024, "insertion": 0.0013},
             "2": {"raw_rate": 0.0032, "mismatch": 0.79, "deletion": 0.0018, "insertion": 0.0011},
             "3": {"raw_rate": 0.02, "mismatch": 0.75, "deletion": 0.20, "insertion": 0.05},
             "4": {"raw_rate": 0.14, "mismatch": 0.37, "deletion": 0.21, "insertion": 0.42},
             "5": {"raw_rate": 0.2, "mismatch": 0.48, "deletion": 0.37, "insertion": 0.15},
             "6": {"raw_rate": 0.13, "mismatch": 0.41, "deletion": 0.36, "insertion": 0.23}}

mutation_attributes = {"1": {"deletion": {"position": {"random": 1},
                                          "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}},
                             "insertion": {"position": {"random": 1},
                                           "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}},
                             "mismatch": {"pattern": {"A": {"G": 0.50, "T": 0.25, "C": 0.25},
                                                      "T": {"G": 0.50, "A": 0.25, "C": 0.25},
                                                      "C": {"G": 0.50, "A": 0.25, "T": 0.25},
                                                      "G": {"T": 0.50, "A": 0.25, "C": 0.25}}}},
                       "2": {"deletion": {"position": {"random": 1},
                                          "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}},
                             "insertion": {"position": {"random": 1},
                                           "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}},
                             "mismatch": {"pattern": {"A": {"G": 0.50, "T": 0.25, "C": 0.25},
                                                      "T": {"G": 0.50, "A": 0.25, "C": 0.25},
                                                      "C": {"G": 0.50, "A": 0.25, "T": 0.25},
                                                      "G": {"T": 0.50, "A": 0.25, "C": 0.25}}}},
                       "3": {"deletion": {"position": {"homopolymer": 0.85, "random": 0.15},
                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                             "insertion": {"position": {"homopolymer": 0.85, "random": 0.15},
                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                             "mismatch": {"pattern": {"CG": {"CA":0.5, "TG":0.5}}}},
                       "4": {"deletion": {"position": {"homopolymer": 0.85, "random": 0.15},
                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                             "insertion": {"position": {"homopolymer": 0.85, "random": 0.15},
                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                             "mismatch": {"pattern": {"CG": {"CA": 0.5, "TG": 0.5}}}},
                       "5": {"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                             "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                             "mismatch": {"pattern": {"TAG": "TGG", "TAC": "TGC"}}},
                       "6": {"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},
                             "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},
                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},
                             "mismatch": {"pattern": {"TAG": "TGG", "TAC": "TGC"}}}}


class SequencingError:
    """
    Base class for the simulation of sequencing errors.
    Implemented error types are:
    -- insertion with and without patterns (preferred bases) randomly or
    in homopolymers
    -- deletion with and without patterns (preferred bases) randomly or
    in homopolymers
    -- mismatches with and without patterns (preferred bases) randomly or
    specific motives that are switched (e.g. TAC -> TGC)
    """
    def __init__(self, seq, attributes=None, error_rates=None):
        self.bases = ['A', 'T', 'C', 'G']
        self.checks = {'ins_no_prob': None, 'ins_no_pos': None, 'ins_poly_w': None, 'ins_poly_wo': None,
                       'del_no_prob': None, 'del_no_pos': None, 'del_poly_w': None, 'del_poly_wo': None,
                       'mis_no_prob': None, 'mis_no_pos': None}
        self.attributes = attributes
        self.error_rates = error_rates
        self.seq = seq
        self.out_seq = None

    def insertion(self, prob=None):
        if prob is not None:
            self.checks['ins_no_prob'] = 1
            return ''.join('{}{}'.format(char, random.choice(self.bases) if random.random() <= prob else '')
                           for char in self.seq)
        else:
            res = self.attributes['insertion']
            position, pattern, position_range = self._get_atts(res)

            if not position or position == 'random':
                self.checks['ins_no_pos'] = 1
                return self._indel(pattern, position_range, mode='insertion')

            if position == 'homopolymer':
                poly = homopolymer(self.seq)
                if poly:
                    self.checks['ins_poly_w'] = 1
                    return self._homopolymer_indel(poly, pattern, mode='insertion')
                else:
                    self.checks['ins_poly_wo'] = 1
                    return self._indel(pattern, position_range, mode='insertion')

    def deletion(self, prob=None):
        if prob is not None:
            self.checks['del_no_prob'] = 1
            return "".join(filter(lambda x: random.random() <= prob, self.seq))
        else:
            res = self.attributes["deletion"]
            position, pattern, pattern_range = self._get_atts(res)

            if not position or position == 'random':
                self.checks['del_no_pos'] = 1
                return self._indel(pattern, pattern_range, mode='deletion')

            if position == 'homopolymer':
                poly = homopolymer(self.seq)
                if poly:
                    self.checks['del_poly_w'] = 1
                    return self._homopolymer_indel(poly, pattern, mode='deletion')
                else:
                    self.checks['del_poly_wo'] = 1
                    return self._indel(pattern, pattern_range, mode='deletion')

    def mismatch(self, prob=None):
        if prob is not None:
            self.checks['mis_no_prob'] = 1
            return "".join('{}'.format(random.choice(self.bases)
                                       if random.random() <= prob else char) for char in self.seq)
        else:
            res = self.attributes["mismatch"]
            position, pattern, position_range = self._get_atts(res)

            if not position or position == 'random':
                self.checks['mis_no_pos'] = 1
                return self._random_position_mismatch(pattern)
            else:
                # Placeholder until we can find some positional
                # mismatching information.
                pass

    def _homopolymer_indel(self, poly, pattern, mode):
        poly_b = {ele['base'] for ele in poly}
        if pattern:
            # Get the base:weight pairs for all bases that exists in
            # homopolymer form in the sequence.
            poly_weights = {k: v for k, v in pattern.items() if k in poly_b}
        else:
            # If no base probabilities exist, just give all bases that
            # exist as homopolymer the same probability.
            poly_weights = {ele['base']: None for ele in poly}
            poly_weights.update((k, 1 / len(poly_weights)) for k in poly_weights)

        # Normalize the weights.
        s = sum(poly_weights.values())
        norm_poly_weights = {k: float(v) / s for k, v in poly_weights.items()}

        # Choose which base will be deleted / inserted.
        choose_ele = np.random.choice(list(norm_poly_weights.keys()),
                                      p=list(norm_poly_weights.values()))

        # Choose the homopolymer whose base will be deleted/in which
        # an insertion event will take place
        choose_poly = np.random.choice([ele for ele in poly if ele['base'] == choose_ele])

        # Choose a random position inside the homopolymer (not
        # necessary for deletions but this keeps the code more compact)
        pos = np.random.choice(range(choose_poly['startpos'], choose_poly['endpos'] + 1))

        return self._indel_mismatch_base(pos, mode)

    def _indel(self, pattern, position_range, mode):
        if not pattern:
            if position_range:
                pos = np.random.choice(range(position_range[0], (position_range[1] + 1)))
            else:
                pos = np.random.choice(range(len(self.seq)))
            return self._indel_mismatch_base(pos, mode)
        else:
            chosen_ele = np.random.choice(list(pattern.keys()),
                                          p=list(pattern.values()))
            return self._randomly_indel_base(chosen_ele, position_range, mode)

    # Checking for all matches using regex is quite slow.
    def _random_position_mismatch(self, pattern):
        if not pattern:
            return self._no_pattern_mismatch()
        else:
            return self._pattern_mismatch(pattern)

    def _no_pattern_mismatch(self):
        pos = np.random.choice(range(len(self.seq)))
        return self._indel_mismatch_base(pos, mode='mismatch')

    def _pattern_mismatch(self, pattern):
        reg = re.compile("|".join(pattern.keys()))
        try:
            chosen_ele = random.choice([(match.span(), match.group())
                                        for match in re.finditer(reg, self.seq)])
        except IndexError:
            return self._no_pattern_mismatch()

        if type(pattern[chosen_ele[1]]) == dict:
            new_ele = np.random.choice(list(pattern[chosen_ele[1]].keys()),
                                       p=list(pattern[chosen_ele[1]].values()))
        else:
            new_ele = pattern[chosen_ele[1]]
        return self.seq[:chosen_ele[0][0]] + new_ele + self.seq[chosen_ele[0][1]:]

    # Not really random and could end up in an infinite loop, but
    # better than to take all indices which satisfy the condition
    # and chosing one of these indices at random.
    def _randomly_indel_base(self, chosen_ele, position_range, mode):
        if position_range:
            seq_indices = range(position_range[0], (position_range[1] + 1))
        else:
            seq_indices = range(len(self.seq))
        count = 0
        while count <= 5000:
            pos = np.random.choice(seq_indices)
            if self.seq[pos] == chosen_ele:
                return self._indel_mismatch_base(pos, mode)
            else:
                count += 1
        try:
            pos = random.choice(np.where(np.array(list(self.seq)) == chosen_ele)[0])
        # If the base does not exists in the sequence, an IndexError
        # is raised. Have to change it it so it tries another base.
        except IndexError:
            return self.seq
        return self._indel_mismatch_base(pos, mode)

    def _indel_mismatch_base(self, pos, mode):
        assert mode in ['deletion', 'insertion', 'mismatch']
        if mode == 'deletion':
            return self.seq[:pos] + self.seq[(pos + 1):]
        elif mode == 'insertion':
            return self.seq[:pos] + random.choice(self.bases) + self.seq[pos:]
        else:
            return self.seq[:pos] + random.choice(self.bases) + self.seq[pos + 1:]

    @staticmethod
    def _get_atts(res):
        try:
            position = np.random.choice(list(res["position"].keys()),
                                        p=list(res["position"].values()))
        except KeyError:
            position = None
        try:
            pattern = res['pattern']
        except KeyError:
            pattern = None
        try:
            position_range = res['position_range']
        except KeyError:
            position_range = None

        return position, pattern, position_range

    def lit_error_rate_mutations(self, mutation_list=['insertion', 'deletion', 'mismatch']):
        assert all(ele in ['insertion', 'deletion', 'mismatch'] for ele in
                   mutation_list), 'Supported types of mutation are: "deletion", "mismatch" and "insertion".'
        out_seq = self.seq
        for mutation_type in mutation_list:
            if self.error_rates is not None:
                err_rate = self.error_rates["raw_rate"] * self.error_rates[str(mutation_type)]
                print(err_rate)
            else:
                err_rate = 0
            if self.attributes is False:
                self.seq = eval('self.' + mutation_type)(err_rate)
            else:
                for n in range(round((len(out_seq) * err_rate))):
                    self.seq = eval('self.' + mutation_type)()
        return self.seq

    def manual_mutation(self, error):
        if random.random() <= error['errorprob']:
            m_types = ['deletion', 'insertion', 'mismatch']
            m_weights = [self.error_rates['deletion'], self.error_rates['insertion'], self.error_rates['mismatch']]
            mut_type = np.random.choice(m_types, p=m_weights)
            att = {mut_type: {'position_range': [error['startpos'], error['endpos']]}}
            self.out_seq = eval('self.' + mut_type)(self.seq, att)
        return self.out_seq

