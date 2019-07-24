import networkx as nx


class Graph:
    def __init__(self, graph, seq):
        self.initial_seq = seq
        if graph is None:
            self.graph = self.create_graph()
        else:
            self.graph = graph
        self.modified_positions = set()
        self.source_node = self.graph.node[0]

    def create_graph(self):
        g = nx.DiGraph()
        g.add_node(0, startpos=0, endpos=len(self.initial_seq) - 1, identifier="root", seq=self.initial_seq)
        return g

    def add_node(self, orig, mod, orig_end, mod_start, mod_end, mode, process):
        # The error probs are used only for color coding here.
        if process == 'synthesis':
            error_prob = 2.0
        elif process == 'storage':
            error_prob = 3.0
        elif process == 'sequencing':
            error_prob = 4.0
        else:
            error_prob = 5.0
        if mode == 'insertion':
            error_prob += 0.3
        elif mode == 'deletion':
            error_prob += 0.6
        else:
            error_prob += 0.9

        # In the case of an insertion
        if len(mod) > len(orig):
            offset = len(mod) - len(orig)
            self.shift_indices(offset, orig_end)
            orig = ' ' + orig
        for i in range(len(mod)):
            # In the case of an mismatch where one of the mismatched bases stayed the same or if a mismatch happens
            # at a deleted position.
            if mod[i] == orig[i] or (orig[i] == ' ' and mode != 'insertion'):
                pass
            else:
                self.graph.add_node(len(self.graph.nodes), startpos=mod_start + i, endpos=mod_start + i,
                                    errorprob=error_prob, orig=orig[i], mod=mod[i],
                                    identifier=process, mode=mode)
                node_id = len(self.graph.nodes) - 1
                self.add_edges(node_id)
                self.modified_positions.update(range(mod_start, mod_end))

    def shift_indices(self, offset, orig_end):
        for i in range(1, len(self.graph.nodes())):
            if self.graph.node[i]["startpos"] >= orig_end:
                self.graph.node[i]["startpos"] += offset
                self.graph.node[i]["endpos"] += offset
        self.graph.node[0]["endpos"] += offset

    def add_edges(self, node_id):
        if self.graph.node[node_id]["startpos"] in self.modified_positions:
            self.nodesearch(self.graph.node[node_id]["startpos"], node_id)
        else:
            self.graph.add_edge(0, node_id)

    def nodesearch(self, nodepos, node_id):
        for i in range(node_id - 1, -1, -1):
            n = self.graph.node[i]
            if nodepos == n['startpos'] or i == 0:
                self.graph.add_edge(i, node_id)
                break

    def get_lineages(self):
        self.graph.remove_node(0)
        error_lineages = dict()
        c = 0
        for subgraph in nx.weakly_connected_component_subgraphs(self.graph):
            sc = str(c)
            error_lineages[sc] = dict()
            for node in subgraph.nodes(data=True):
                if 'errors' in error_lineages[sc].keys():
                    node = self.space_to_string(node)
                    error_lineages[sc]['errors'] = error_lineages[sc][
                                            'errors'] + "Was {}, is now {}, Error Source: {}, Error Type: {}\n".format(
                        node[1]['orig'], node[1]['mod'], node[1]['identifier'], node[1]['mode'])
                else:
                    node = self.space_to_string(node)
                    error_lineages[sc]['errors'] = "Was {}, is now {}, Error Source: {}, Error Type: {}\n".format(
                        node[1]['orig'], node[1]['mod'], node[1]['identifier'], node[1]['mode'])
                    error_lineages[sc]['startpos'] = node[1]['startpos']
                    error_lineages[sc]['endpos'] = node[1]['endpos']
                    error_lineages[sc]['errorprob'] = node[1]['errorprob']
                    error_lineages[sc]['identifier'] = node[1]['identifier'] + '_' + sc
            c += 1
        return list(error_lineages.values())

    @staticmethod
    def space_to_string(node):
        if node[1]['orig'] == ' ':
            node[1]['orig'] = 'empty'
        elif node[1]['mod'] == ' ':
            node[1]['mod'] = 'empty'
        return node