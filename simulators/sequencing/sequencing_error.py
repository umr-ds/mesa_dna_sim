from simulators.error_sources.homopolymers import homopolymer
import numpy as np
import random
import re

class Sequencing_error:
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
    def __init__(self, seq, attributes):
        self.bases = ['A', 'T', 'C', 'G']
        self.checks = {'ins_no_prob': None, 'ins_no_pos': None, 'ins_poly_w': None, 'ins_poly_wo': None,
                       'del_no_prob': None, 'del_no_pos': None, 'del_poly_w': None, 'del_poly_wo': None,
                       'mis_no_prob': None, 'mis_no_pos': None}
        self.attributes = attributes
        self.seq = seq

    def insertion(self, prob=None):
        if prob != None:
            self.checks['ins_no_prob'] = 1
            return "".join('{}{}'.format(char, random.choice(self.bases)
            if random.random() <= prob else '') for char in self.seq)
        else:
            res = self.attributes["insertion"]
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
        if prob != None:
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
        if prob != None:
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
            # homopolymer form in the sequence
            poly_weights = {k: v for k, v in pattern.items() if k in poly_b}
        else:
            # If no base pobabilities exist, just give all bases that
            # exist as homopolymer the same probability
            poly_weights = {ele['base']: None for ele in poly}
            poly_weights.update((k, 1 / len(poly_weights)) for k in poly_weights)

        # Normalize the weigths
        s = sum(poly_weights.values())
        norm_poly_weights = {k: float(v) / s for k, v in poly_weights.items()}

        # Choose which base will be deleted / inserted
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

        return self.seq[:chosen_ele[0][0]] + pattern[chosen_ele[1]] + self.seq[chosen_ele[0][1]:]

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