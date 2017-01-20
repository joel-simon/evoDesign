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

cdef float sigmoid(float x):
    return 1 / (1 + exp(-x))


cdef class FeedForwardNetwork:
    cdef int max_node
    cdef ITYPE_t [:] input_nodes, output_nodes, nodes
    # cdef float [:] biases, responses, values
    # cdef list links
    cdef list links

    cdef double [:] biases, responses, values

    def __init__(self, max_node, input_nodes, output_nodes,
                                            nodes, biases, responses, links):
        self.input_nodes = np.array(input_nodes, dtype=ITYPE)
        self.output_nodes = np.array(output_nodes, dtype=ITYPE)
        self.nodes = np.array(nodes, dtype=ITYPE)
        self.biases = np.array(biases)
        self.responses = np.array(responses)
        self.links = links
        self.values = np.zeros(1 + max_node)

    def serial_activate(self, np.ndarray[DTYPE_t, ndim=1] inputs):
        cdef int i, j, node, nid
        cdef double bias, response, s

        # if len(self.input_nodes) != len(inputs):
        #     raise Exception("Expected {} inputs, got {}".format(len(self.input_nodes), len(inputs)))

        for i in range(self.input_nodes.shape[0]):
        # for nid, v in zip(self.input_nodes, inputs):
            self.values[self.input_nodes[i]] = inputs[i]

        for i in range(self.nodes.shape[0]):
            node = self.nodes[i]
            bias = self.biases[i]
            response = self.responses[i]
            links = self.links[i]
            s = 0.0
            for j, w in links:
                s += self.values[j] * w
            self.values[node] = sigmoid(bias + response * s)

        return [self.values[i] for i in self.output_nodes]

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
    max_inputs = []

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
            max_inputs = max(max_inputs, len(inputs))


    # return FeedForwardNetwork(int(max(used_nodes)), np.array(input_nodes, dtype=int), np.array(output_nodes, dtype=int), \
    #     np.array(nodes, dtype=int), np.array(biases), np.array(responses), all_inputs)

    return FeedForwardNetwork(int(max(used_nodes)), input_nodes, output_nodes, \
                                            nodes, biases, responses, all_inputs)
