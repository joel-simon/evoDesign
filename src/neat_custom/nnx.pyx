import numpy as np
from neat.activations import sigmoid_activation

import numpy as np
cimport numpy as np

import cython
cimport cython

from libc.math cimport exp

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

ITYPE = np.int64
ctypedef np.int64_t ITYPE_t

@cython.cdivision(True)
@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline float sigmoid(float x):
    return 1 / (1 + exp(-x))

# @cython.cdivision(True)
# @cython.nonecheck(False)
# @cython.boundscheck(False)
# @cython.wraparound(False)
# @cython.initializedcheck(False)
cdef class FeedForwardNetwork:
    cdef int max_node, num_input_nodes, num_nodes, num_output_nodes
    cdef int [::1] input_nodes, output_nodes, nodes, edges_per_node
    cdef int [:,::1] conns
    cdef list links

    cdef double [::1] biases, responses, values
    cdef double [:,::1] conn_weights

    def __init__(self, max_node, input_nodes, output_nodes,
                                            nodes, biases, responses, links):
        # print(len(input_nodes), len(nodes), len(biases), len(responses), len(links))

        self.input_nodes = np.array(input_nodes, dtype=np.dtype("i"))
        self.num_input_nodes = len(input_nodes)
        self.num_nodes = len(nodes)
        self.output_nodes = np.array(output_nodes, dtype=np.dtype("i"))
        self.num_output_nodes = len(output_nodes)
        self.nodes = np.array(nodes, dtype=np.dtype("i"))
        self.biases = np.array(biases)
        self.responses = np.array(responses)
        self.values = np.zeros(1 + max_node)

        if len(links) != 0:
            max_links = max(len(l) for l in links)
        else:
            max_links = 0
        self.conns = np.zeros((self.num_nodes, max_links), dtype=np.dtype("i"))
        self.conn_weights = np.zeros((self.num_nodes, max_links))
        self.edges_per_node = np.zeros(self.num_nodes, dtype=np.dtype("i"))

        for i, l in enumerate(links):
            self.edges_per_node[i] = len(l)
            for j, (conn, conn_weights) in enumerate(l):
                self.conns[i, j] = conn
                self.conn_weights[i, j] = conn_weights

        # self.links = links

    def serial_activate(self, double[::1] inputs, double[::1] outputs):
        cdef int i, j, node, nid, m, l, node_id, epn
        cdef double bias, response, s, n, conn_weight

        for i in range(self.num_input_nodes):
            m = self.input_nodes[i]
            n = inputs[i]
            self.values[m] = n

        for i in range(self.num_nodes):
            node = self.nodes[i]
            bias = self.biases[i]
            response = self.responses[i]
            epn = self.edges_per_node[i]
            s = 0.0
            for j in range(epn):
                node_id = self.conns[i, j]
                conn_weight = self.conn_weights[i, j]
                s += self.values[node_id] * conn_weight
            self.values[node] = sigmoid(bias + response * s)

        for i in range(self.num_output_nodes):
            nid = self.output_nodes[i]
            outputs[i] = self.values[nid]

def find_feed_forward_layers(inputs, connections):
    '''
    Collect the layers whose members can be evaluated in parallel in a feed-forward network.
    :param inputs: list of the network input nodes
    :param connections: list of (input, output) connections in the network.

    Returns a list of layers, with each layer consisting of a set of node identifiers.
    '''

    # TODO: Detect and omit nodes whose output is ultimately never used.

    layers = []
    S = set(inputs)
    while 1:
        # Find candidate nodes C for the next layer.  These nodes should connect
        # a node in S to a node not in S.
        C = set(b for (a, b) in connections if a in S and b not in S)
        # Keep only the nodes whose entire input set is contained in S.
        T = set()
        for n in C:
            if all(a in S for (a, b) in connections if b == n):
                T.add(n)

        if not T:
            break

        layers.append(T)
        S = S.union(T)

    return layers

def create_feed_forward_phenotype(genome):
    """ Receives a genome and returns its phenotype (a neural network). """

    # Gather inputs and expressed connections.
    input_nodes = [ng.ID for ng in genome.node_genes.values() if ng.type == 'INPUT']
    output_nodes = [ng.ID for ng in genome.node_genes.values() if ng.type == 'OUTPUT']
    connections = [(cg.in_node_id, cg.out_node_id) for cg in genome.conn_genes.values() if cg.enabled]

    layers = find_feed_forward_layers(input_nodes, connections)
    node_evals = []
    used_nodes = set(input_nodes + output_nodes)

    nodes = []
    biases = []
    responses = []
    all_inputs = []

    for layer in layers:
        for node in layer:
            inputs = []
            # TODO: This could be more efficient.
            for cg in genome.conn_genes.values():
                if cg.out_node_id == node and cg.enabled:
                    inputs.append((cg.in_node_id, cg.weight))
                    used_nodes.add(cg.in_node_id)

            used_nodes.add(node)
            ng = genome.node_genes[node]
            # node_evals.append((node, ng.bias, ng.response, inputs))
            nodes.append(node)
            biases.append(ng.bias)
            responses.append(ng.response)
            all_inputs.append(inputs)


    # return FeedForwardNetwork(int(max(used_nodes)), np.array(input_nodes, dtype=int), np.array(output_nodes, dtype=int), \
    #     np.array(nodes, dtype=int), np.array(biases), np.array(responses), all_inputs)

    return FeedForwardNetwork(int(max(used_nodes)), input_nodes, output_nodes, \
                                            nodes, biases, responses, all_inputs)
