import networkx as nx
import itertools as it
import random as ran
import time

import math

# gets all cycles of size >= 3 in graph - converting from undirected to directed makes this easier with using networkx
def get_cycles(graph):
	graph = graph.to_directed()
	cycles = nx.simple_cycles(graph)
	out = []
	for c in cycles:
		if len(c) > 2:
			out.append(c)
	return out

# determines whether a cycle has at most 1 vertex of degree >= 3
def is_semidisjoint(graph, cycle):
	threeDegree = False
	for v in cycle:
		if graph.degree(v) > 2:
			if threeDegree:
				return False
			else:
				threeDegree = True
	return True

# returns whether the provided set is an fvs for graph
def verify_fvs(graph, fvs):
	cycles = get_cycles(graph)
	for cycle in cycles:
		isIn = False
		for v in fvs:
			if v in cycle:
				isIn = True
		if not isIn:
			return False
	return True

# returns the optimal fvs for graph - checks all possible selections of vertices and keeps track of the best fvs seen so far
def optimal_fvs(graph):
	cycles = get_cycles(graph)
	optSol = []
	optWeight = math.inf
	size = len(graph.nodes())
	vertices = set().union(*cycles)
	for x in range(1, size - 1):
		combo = it.combinations(vertices, x)
		for y in combo:
			if verify_fvs(graph, y):
				weight = 0
				for z in y:
					weight += weights[z]
				if weight < optWeight:
					optWeight = weight
					optSol = y
	return optSol, optWeight


# first argument is |V| in g, second argument is probability of any edge being in g
g = nx.erdos_renyi_graph(7, 1)
size = len(g.nodes())
weights = [ran.randint(1, size) for _ in range(size)]
t1 = time.time()
sol, weight = optimal_fvs(g)
t2 = time.time()
elapsed = t2 - t1
print(elapsed)