from simulators.error_sources.homopolymers import homopolymer
from time import time
import numpy as np
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
                             "mismatch": {"pattern": {"CG": {"CA": 0.5, "TG": 0.5}}}},
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

    def __init__(self, seq, graph, process, attributes=None, error_rates=None, seed=None):
        self.bases = ['A', 'T', 'C', 'G']
        self.attributes = attributes
        self.error_rates = error_rates if error_rates else {'insertion': 0.33, 'deletion': 0.34, 'mismatch': 0.33}
        self.seq = seq
        self.modified_positions = set()
        self.out_seq = None
        self.process = process
        self.g = graph
        self.seed = seed if seed else int(time())
        np.random.seed(self.seed)

    def insertion(self, att=None):
        if att:
            position, pattern, position_range = self._get_atts(att)
        else:
            res = self.attributes['insertion']
            position, pattern, position_range = self._get_atts(res)

        if not position or position == 'random':
            return self._indel(pattern, position_range, mode='insertion')

        if position == 'homopolymer':
            poly = homopolymer(self.seq)
            if poly:
                return self._homopolymer_indel(poly, pattern, mode='insertion')
            else:
                return self._indel(pattern, position_range, mode='insertion')

    def deletion(self, att=None):
        if att:
            position, pattern, pattern_range = self._get_atts(att)
        else:
            res = self.attributes["deletion"]
            position, pattern, pattern_range = self._get_atts(res)

        if not position or position == 'random':
            return self._indel(pattern, pattern_range, mode='deletion')

        if position == 'homopolymer':
            poly = homopolymer(self.seq)
            if poly:
                return self._homopolymer_indel(poly, pattern, mode='deletion')
            else:
                return self._indel(pattern, pattern_range, mode='deletion')

    def mismatch(self, att=None):
        if att:
            position, pattern, position_range = self._get_atts(att)
        else:
            res = self.attributes["mismatch"]
            position, pattern, position_range = self._get_atts(res)

        if not position or position == 'random':
            return self._positional_mismatch(pattern, position_range=position_range)
        else:
            pass

    def _homopolymer_indel(self, poly, pattern, mode):
        poly_b = {ele['base'] for ele in poly if ele['base'] is not " "}
        # If the only homopolymer found was empty spaces (deletions), randomly indel a base
        if not poly_b:
            return self._indel(pattern=None, position_range=None, mode=mode)
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
            # Exclude empty spaces (deletions)
            pos = " "
            if position_range:
                while pos == " ":
                    pos = np.random.choice(range(position_range[0], (position_range[1] + 1)))
            else:
                while pos == " ":
                    pos = np.random.choice(range(len(self.seq)))
            return self._indel_mismatch_base(pos, mode)
        else:
            chosen_ele = np.random.choice(list(pattern.keys()),
                                          p=list(pattern.values()))
            return self._randomly_indel_base(chosen_ele, position_range, mode)

    # Checking for all matches using regex is quite slow.
    def _positional_mismatch(self, pattern=None, position_range=None):
        if not pattern:
            return self._no_pattern_mismatch(position_range)
        else:
            return self._pattern_mismatch(pattern, position_range)

    def _no_pattern_mismatch(self, position_range=None):
        if position_range:
            check_range = range(position_range[0], position_range[1] + 1)
            if self.seq[position_range[0]:position_range[1] + 1] == ' ':
                return
        else:
            check_range = range(len(self.seq))
        pos = " "
        while pos == " ":
            pos = np.random.choice(check_range)
        return self._indel_mismatch_base(pos, mode='mismatch')

    # A problem with pattern mismatches is now that it does not find patterns separated by a
    # deletion.
    def _pattern_mismatch(self, pattern, position_range):
        reg = re.compile("|".join(pattern.keys()))  # '(?=(' + "|".join(pattern.keys()) + '))')
        if position_range:
            check_seq_range = self.seq[position_range[0]:position_range[1] + 1]
        else:
            check_seq_range = self.seq
        try:
            choices = [(match.span(), match.group())
                       for match in re.finditer(reg, check_seq_range)]
            idx = np.random.choice(len(choices))
            chosen_ele = choices[idx]
        except ValueError:
            return self._no_pattern_mismatch()

        if type(pattern[chosen_ele[1]]) == dict:  # TODO check: chosen_ele[1] in pattern and
            final_ele = np.random.choice(list(pattern[chosen_ele[1]].keys()),
                                         p=list(pattern[chosen_ele[1]].values()))
        else:
            new_ele = pattern[chosen_ele[1]]
            if type(new_ele) == list:
                final_ele = np.random.choice(new_ele)
            else:
                final_ele = new_ele
        self.g.add_node(orig=chosen_ele[1], mod=final_ele, orig_end=chosen_ele[0][1],
                        mod_start=chosen_ele[0][0], mod_end=chosen_ele[0][0] + len(final_ele),
                        mode="pattern_mismatch", process=self.process)
        # ... + self.seq[chosen_ele[0][1] + 1:] ????
        self.seq = self.seq[:chosen_ele[0][0]] + final_ele + self.seq[chosen_ele[0][1]:]

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
            pos = np.random.choice(np.where(np.array(list(self.seq)) == chosen_ele)[0])
        # If the base does not exists in the sequence, a ValueError
        # is raised. Have to change it it so it tries another base.
        except ValueError:
            return self.seq
        return self._indel_mismatch_base(pos, mode)

    def _indel_mismatch_base(self, pos, mode):
        assert mode in ['deletion', 'insertion', 'mismatch', 'pattern_mismatch']
        # The same position was already modified during evaluation of this particular process.
        if pos in self.g.visited_nodes[self.process]:
            return
        if mode == 'deletion':
            self.g.add_node(orig=self.seq[pos], mod=" ", orig_end=pos + 1,
                            mod_start=pos, mod_end=pos + 1, mode=mode, process=self.process)
            self.seq = self.seq[:pos] + " " + self.seq[pos + 1:]
        elif mode == 'insertion':
            ele = np.random.choice(self.bases)
            self.g.add_node(orig=self.seq[pos], mod=ele + self.seq[pos], orig_end=pos + 1, mod_start=pos,
                            mod_end=pos + 2, mode=mode, process=self.process)
            self.seq = self.seq[:pos] + ele + self.seq[pos:]
        else:
            ele = np.random.choice(self.bases)
            self.g.add_node(orig=self.seq[pos], mod=ele, orig_end=pos + 1, mod_start=pos, mod_end=pos + 1, mode=mode,
                            process=self.process)
            self.seq = self.seq[:pos] + ele + self.seq[pos + 1:]

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

    def lit_error_rate_mutations(self, mutation_list=['insertion', 'mismatch', 'deletion'], seed=None):
        assert all(ele in ['insertion', 'deletion', 'mismatch'] for ele in
                   mutation_list), 'Supported types of mutation are: "deletion", "mismatch" and "insertion".'
        for mutation_type in mutation_list:
            if self.error_rates is not None:
                err_rate = self.error_rates["raw_rate"] * self.error_rates[str(mutation_type)]
            else:
                err_rate = 0
            if self.attributes is False:
                eval('self.' + mutation_type)(err_rate)
            else:
                for n in range(round((len(self.seq) * err_rate))):
                    eval('self.' + mutation_type)()
        self.g.graph.nodes[0]['seq'] = self.seq
        return self.seed

    def manual_mutation(self, error):
        if np.random.random() <= error['errorprob']:
            m_types = ['deletion', 'insertion', 'mismatch']
            m_weights = [self.error_rates['deletion'], self.error_rates['insertion'], self.error_rates['mismatch']]
            mut_type = np.random.choice(m_types, p=m_weights)
            att = {'position_range': [error['startpos'], error['endpos']]}
            eval('self.' + mut_type)(att)
        self.g.graph.nodes[0]['seq'] = self.seq
        return self.seed


if __name__ == "__main__":
    seq = "ATCGAATCGGGATAGATAATCGAATCGGGATAGATA"
    g = Graph(None, seq)
    t = SequencingError(seq, g, process="sequencing", attributes=mutation_attributes["3"],
                        error_rates=err_rates["5"])  # err_rate 5
    t.lit_error_rate_mutations()
    {'deletion', 'insertion', 'mismatch', 'pattern_mismatch'}.issubset(
        nx.get_node_attributes(t.g.graph, 'mode').values())
