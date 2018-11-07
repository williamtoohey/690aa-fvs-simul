import networkx as nx
import sys

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

# first argument is |V| in g, second argument is probability of any edge being in g
g = nx.erdos_renyi_graph(4, 0.5)
print(g.edges())
cycles = get_cycles(g)
for c in cycles:
	print(c)
	print(is_semidisjoint(g, c))