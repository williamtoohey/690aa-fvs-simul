import networkx as nx
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

#the probabilistic weighted algorithm presented in Becker-Yehuda-Geiger
#including the weights of the vertices allows the vertices to be selected with probability proportion to degree/weight
#not including the weights just picks with probability proportion to degree
def prob_alg(graph, j, weights = []):
	fvs = []
	gi = graph.copy()
	for i in range(1, j + 1):
		(gi, partialFvs) = get_branchy_graph(gi)
		if len(partialFvs) > 0:
			fvs = fvs + partialFvs
		if len(gi.nodes()) == 0:
			return fvs
		probabilities = []
		vertices = list(gi.nodes())
		totDegree = total_degree(gi)
		for v in vertices:
			if len(weights) > 0:
				sum = 0
				for x in vertices:
					sum += gi.degree(x) / weights[x]
				probabilities.append((gi.degree(v) / weights[v]) / sum)
			else:
				probabilities.append(gi.degree(v) / totDegree)
		toss = ran.uniform(0, 1)
		count = 0
		vertex = vertices[0];
		for j in range(0, len(probabilities)):
			count += probabilities[j]
			if count >= toss:
				vertex = vertices[j]
				break
		fvs.append(vertex)
		gi.remove_node(vertex)
	if not verify_fvs(graph, fvs):
		return None
	return fvs

# returns the optimal fvs for graph - checks all possible selections of vertices and keeps track of the best fvs seen so far
def optimal_fvs(graph):
	try:
		nx.find_cycle(graph)
	except:
		return [], 0
	optSol = []
	optWeight = math.inf
	size = len(graph.nodes())
	vertices = list(graph.nodes())
	for x in range(size - 2, 0, -1):
		combo = it.combinations(vertices, x)
		for y in combo:
			if verify_fvs(graph, y):
				weight = weight_fvs(y)
				if weight <= optWeight:
					optWeight = weight
					optSol = y
	return optSol, optWeight

#returns total weight of provided fvs
def weight_fvs(fvs):
	weight = 0
	for i in fvs:
		weight += weights[i]
	return weight

#probabilistic algorithm, run for min(max, c * 6^(current best weight)) iterations, probability proportional to degree/weight ratio
def wra2(graph, c, max):
	size = len(list(graph.nodes()))
	fvs = prob_alg(graph, size - 2, weights)
	weight = weight_fvs(fvs)
	m = min(max, c * (6 ** weight))
	i = 1
	while i <= m:
		newFvs = prob_alg(graph, size - 2, weights)
		newWeight = weight_fvs(newFvs)
		if newWeight <= weight:
			fvs = newFvs
			weight = newWeight
			m = min(max, c * (6 ** newWeight))
		i += 1
	return fvs

#probabilistic algorithm, run for min(max, c * 6^(current best weight)) iterations, probability proportional to degree ratio
def wra(graph, c, max):
	size = len(list(graph.nodes()))
	fvs = prob_alg(graph, size - 2)
	weight = weight_fvs(fvs)
	m = min(max, c * (6 ** weight))
	i = 1
	while i <= m:
		newFvs = prob_alg(graph, size - 2)
		newWeight = weight_fvs(newFvs)
		if newWeight <= weight:
			fvs = newFvs
			weight = newWeight
			m = min(max, c * (6 ** newWeight))
		i += 1
	return fvs

# first argument for erdos_renyi_graphs is |V| in g, second argument is probability of any edge being in g
# currently generates a random graph and random weight assignments, and runs wra
graph = nx.erdos_renyi_graph(8, 0.5)
edges = graph.edges()
print(list(edges))
size = len(graph.nodes())
weights = [ran.randint(1, size) for _ in range(size)]
optF, optW = optimal_fvs(graph)
print("opt had weight", optW)
print(optF)
fvs = wra(graph, 2, 2 ** (math.log(size - 2, 2) ** 3))
print("min was", weight_fvs(fvs))