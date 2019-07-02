import networkx as nx


class Graph:
    def __init__(self, graph, seq):
        self.initial_seq = seq
        if graph is None:
            self.graph = self.create_graph()
        else:
            self.graph = graph
        self.modified_positions = set()

    def create_graph(self):
        g = nx.DiGraph()
        g.add_node(0, start=0, end=len(self.initial_seq), process="root", seq=self.initial_seq)
        return g

    def add_node(self, orig, mod, orig_start, orig_end, mod_start, mod_end, mode, process):
        if len(mod) > len(orig):
            offset = len(mod) - len(orig)
            self.shift_indices(offset, orig_start, orig_end, mod_start, mod_end)
        self.graph.add_node(len(self.graph.nodes), start=mod_start, end=mod_end,
                            orig=orig, mod=mod, process=process, mode=mode)
        node_id = len(self.graph.nodes) - 1
        self.add_edges(node_id)
        self.modified_positions.update(range(mod_start, mod_end))

    def shift_indices(self, offset, orig_start, orig_end, mod_start, mod_end):
        for i in range(1, len(self.graph.nodes())):
            if self.graph.node[i]["start"] >= orig_end:
                self.graph.node[i]["start"] += offset
                self.graph.node[i]["end"] += offset
        self.graph.node[0]["end"] += offset

    def add_edges(self, node_id):
        if self.graph.node[node_id]["start"] in self.modified_positions:
            self.nodesearch(self.graph.node[node_id]["start"], self.graph.node[node_id]["end"],
                            node_id - 1, node_id)
        else:
            self.graph.add_edge(0, node_id)

    def nodesearch(self, nodestart, nodeend, searchstart, node_id):
        for i in range(searchstart, -1, -1):
            n = self.graph.node[i]
            # If the new node is contained within an older node, create a single edge between them
            try:
                if nodestart in range(n["start"], n["end"]) and nodeend - 1 in range(n["start"], n["end"]):
                    self.graph.add_edge(i, node_id)
                # If a new node has its starting point within an older node,
                # search for the rest of the node in the other nodes
                elif nodestart in range(n["start"], n["end"]):
                    self.graph.add_edge(i, node_id)
                    self.nodesearch(n["end"], nodeend, i, node_id)
                # If a new node has its end point within an older node,
                # search for the rest of the node in the other nodes
                elif nodeend - 1 in range(n["start"], n["end"]):
                    self.graph.add_edge(i, node_id)
                    self.nodesearch(nodestart, n["start"], i, node_id)
                else:
                    pass
            except RecursionError:
                print("recerr")
                print(nodestart, nodeend)