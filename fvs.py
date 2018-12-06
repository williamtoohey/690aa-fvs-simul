import networkx as nx
import numpy as np
import itertools as it
import random as ran
import time

import math

# returns whether the provided set is an fvs for graph
def verify_fvs(graph, fvs):
    g = graph.copy()
    for i in fvs:
        g.remove_node(i)
    try:
        nx.find_cycle(g)
    except:
        return True
    return False

#deletes all vertices of degree < 2, since they cannot be a part of any cycle
def delete_sinks(graph):
    g = graph.copy()
    changed = False
    while not changed:
        graphNodes = list(g.nodes())
        i = 0
        while i < len(graphNodes):
            if g.degree(graphNodes[i]) < 2:
                #if we ever find a vertex of degree < 2, deleting it may cause a vertex we checked earlier of degree 2 to now be < 2 - so we run through this again to ensure the graph is actually cleaned
                changed = True
                g.remove_node(graphNodes[i])
            i += 1
        if changed:
            changed = False
        else:
            return g;

#transforms the graph into a branchy graph - whenever we have sequences of degree 2 vertices, we bypass a vertex with an edge joining its equally weighted or cheaper neighbors
def get_branchy_graph(graph):
    partialFvs = []
    g = graph.copy()
    g = delete_sinks(g)
    graphNodes = list(g.nodes())
    i = 0
    while i < len(graphNodes):
        neighbors = list(nx.neighbors(g, graphNodes[i]))
        if len(neighbors) == 1:
            #if at some point a vertex has degree 1, it was part of a closed cycle - in which case we must add either it or its neighbor to our fvs
            g.remove_node(graphNodes[i])
            if weights[neighbors[0]] < weights[graphNodes[i]]:
                partialFvs.append(neighbors[0])
                g.remove_node(neighbors[0])
            else:
                partialFvs.append(graphNodes[i])
            i = -1
            g = delete_sinks(g)
        if len(neighbors) == 2:
            #n1 and n2 are the i'th vertex's neighbors
            n1 = neighbors[0]
            n2 = neighbors[1]
            n1neighbors = list(nx.neighbors(g, n1))
            n2neighbors = list(nx.neighbors(g, n2))
            if len(n1neighbors) == 2 or len(n2neighbors) == 2:
                #if the i'th vertex and one of its neighbors have degree 2, the graph is not branchy so we must truncate some vertex
                iNeighbor = n1
                i2ndNeighbors = n1neighbors
                if len(n1neighbors) != 2:
                    iNeighbor = n2
                    i2ndNeighbors = n2neighbors
                #at this point iNeighbor is whichever of the i'th vertex's neighbors has degree 2 and i2ndNeighbor is the second neighbor
                #we now have 4 vertices to work with, being the i'th vertex, n1, n2, and either n1 or n2's additional neighbor, and since >= 2 of these vertices have degree 2 we truncate the more expensive one
                i2ndNeighbors.remove(graphNodes[i])
                if weights[iNeighbor] < weights[i2ndNeighbors[0]] and weights[iNeighbor] < weights[graphNodes[i]]:
                    g.remove_node(graphNodes[i])
                    g.add_edge(n1, n2)
                else:
                    g.remove_node(iNeighbor)
                    g.add_edge(graphNodes[i], i2ndNeighbors[0])
                i = -1
        #i is reset to 0 if we ever modify the graph - this is to ensure the graph is branchy when we finish, since some graphs may need multiple iterations to clean
        i += 1
        graphNodes = list(g.nodes())
    return (g, partialFvs)

#gets total degree of graph
def total_degree(graph):
    allDegrees = list(graph.degree(list(graph.nodes())))
    sum = 0
    for v in allDegrees:
        sum += v[1]
    return sum

def prob_deg(g, w):
    adj = np.array(nx.to_numpy_matrix(g))
    degs = np.sum(adj, axis=0)
    return degs / np.sum(degs)

def prob_deg_weights(g, w):
    adj = np.array(nx.to_numpy_matrix(g))
    degs = np.sum(adj, axis=0)
    return (degs / w[g.nodes()]) / np.sum(degs / w[g.nodes()])

#the probabilistic weighted algorithm presented in Becker-Yehuda-Geiger
#including the weights of the vertices allows the vertices to be selected with probability proportion to degree/weight
#not including the weights just picks with probability proportion to degree
def prob_alg(graph, weights, j, p=prob_deg):
    fvs = []
    gi = graph.copy()
    for _ in range(j):
        (gi, partialFvs) = get_branchy_graph(gi)
        if len(partialFvs) > 0:
            fvs = fvs + partialFvs
        if len(gi.nodes()) == 0:
            return fvs
        probs = p(gi, weights)
        vert_idx = np.random.choice(len(list(gi.nodes())), 1, p=probs)[0]
        vertex = list(gi.nodes())[vert_idx]
        fvs.append(vertex)
        gi.remove_node(vertex)
    if not verify_fvs(graph, fvs):
        return None
    return fvs

# returns the optimal fvs for graph - checks all possible selections of vertices and keeps track of the best fvs seen so far
def optimal_fvs(graph, weights):
    try:
        nx.find_cycle(graph)
    except:
        return [], 0
    optSol = []
    optWeight = np.inf
    size = len(graph.nodes())
    vertices = list(graph.nodes())
    for x in range(size - 2, 0, -1):
        combo = it.combinations(vertices, x)
        for y in combo:
            if verify_fvs(graph, y):
                weight = weight_fvs(list(y), weights)
                if weight <= optWeight:
                    optWeight = weight
                    optSol = y
    return optSol, optWeight

#returns total weight of provided fvs
def weight_fvs(fvs, weights):
    return np.sum(weights[fvs])

#probabilistic algorithm, run for min(max, c * 6^(current best weight)) iterations, probability proportional to degree ratio
def wra(graph, weights, c, max, p=prob_deg):
    size = len(list(graph.nodes()))
    fvs = prob_alg(graph, weights, size - 2, p=p)
    weight = weight_fvs(fvs, weights)
    m = min(max, c * (6 ** weight))
    i = 1
    while i <= m:
        newFvs = prob_alg(graph, weights, size - 2, p=p)
        newWeight = weight_fvs(newFvs, weights)
        if newWeight <= weight:
            fvs = newFvs
            weight = newWeight
            m = min(max, c * (6 ** newWeight))
        i += 1
    return fvs

if __name__ == "__main__":
    # first argument for erdos_renyi_graphs is |V| in g, second argument is probability of any edge being in g
    # currently generates a random graph and random weight assignments, and runs wra
    graph = nx.erdos_renyi_graph(8, 0.5)
    edges = graph.edges()
    size = len(graph.nodes())
    weights = np.round(np.random.uniform(100, 1, size))
    optF, optW = optimal_fvs(graph, weights)
    print("opt fvs: " + str(optF))
    print("opt had weight", optW)
    fvs = wra(graph, weights, 2, 10, p=prob_deg_weights)#2 ** (math.log(size - 2, 2) ** 3))
    print("sol fvs: " + str(fvs))
    print("min was", weight_fvs(fvs, weights))
