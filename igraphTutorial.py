__author__ = 'maury'

import json
from igraph import *

# Recupero dei dati salvati
data = json.load(open("/home/maury/Desktop/ClusteringMethods/InputData/user_cat.json","r"))
# print(data)

g=Graph()
# Aggiunta dei vertici al grafo
g.add_vertices(4)
# Aggiunta degli archi al grafo
g.add_edges([(0,1),(2,3),(3,1),(2,0)])

# Plotting del grafo
# plot(g)
# Stampa del numero di nodi e archi del grafo
summary(g)
print("\nStampa degli archi che compongono il grafo:\n{}".format(g))
print("\nStampa una lista di coppie che rappresentano gli archi del grafo:\n{}".format(g.get_edgelist()))

"""
    igraph knows the concept of attributes, i.e., auxiliary objects associated to a given vertex or edge of a graph,
    or even to the graph as a whole.
    Every igraph Graph, vertex and edge behaves as a standard Python dictionary in some sense:
    you can add key-value pairs to any of them, with the key representing the name of your attribute
    (the only restriction is that it must be a string) and the value representing the attribute itself
"""

"""
    Attributes can be arbitrary Python objects, but if you are saving graphs to a file, only string and numeric attributes
    will be kept. See the pickle module in the standard Python library if you are looking for a way to save other attribute types.
    You can either pickle your attributes individually, store them as strings and save them, or you can pickle the whole Graph
    if you know that you want to load the graph back into Python only.
"""

"""
    Every Graph object contains two special members called vs and es, standing for the sequence of all vertices and all edges,
    respectively. you can simply alter the attributes of vertices and edges individually by indexing vs or es with integers as
    if they were lists.
"""
g.vs[0]["name"]="Giacomo"
print("\nStampa degli attributi del vertice indicizzato: {}".format(g.vs[0].attributes()))

g.es[0]["w"]=0.4
print("\nL'arco connete la coppia di nodi: {} e ha attributi: {}".format(g.es[0].tuple,g.es[0].attributes()))

g["nome"]="Grafo User_Cat"
print("\nNome del grafo: {}".format(g["nome"]))

"""
    igraph provides a large set of methods to calculate various structural properties of graphs.
    This calling convention applies to most of the structural properties igraph can calculate.
    For vertex properties, the methods accept a vertex ID or a list of vertex IDs (and if they are omitted,
    the default is the set of all vertices). For edge properties, the methods accept a single edge ID or
    a list of edge IDs. Instead of a list of IDs, you can also supply a VertexSeq or an EdgeSeq instance appropriately
"""

print("\nStampa del grado del nodo: {}".format(g.vs[0].degree()))

"""
    Besides degree, igraph includes built-in routines to calculate many other centrality properties,
    including vertex and edge betweenness (Graph.betweenness(), Graph.edge_betweenness()) or Google PageRank (Graph.pagerank())...
"""

"""
    Selecting vertices and edges.t is a common task to select vertices and edges based on attributes or structural properties,
    igraph gives you an easier way to do that:
"""
print("\nIl vertice/i selezioanto e/sono: {}".format(g.vs.select(_degree = g.maxdegree())["name"]))

"""
    If the first positional argument is a callable object (i.e., a function, a bound method or anything that behaves like
    a function), the object will be called for every vertex that is currently in the sequence.  If the function returns True,
    the vertex will be included, otherwise it will be excluded:
"""
graph = Graph.Full(10)
only_odd_vertices = graph.vs.select(lambda vertex: vertex.index % 2 == 1)
print("\nVertici selezionati dalla funzione: {}".format([v.index for v in only_odd_vertices]))

"""
    Keyword arguments can be used to filter the vertices based on their attributes or their structural properties.
    The name of each keyword argument should consist of at most two parts: the name of the attribute or structural property
    and the filtering operator. structural property names must always be preceded by an underscore (_) when used for filtering.
"""

print("\nSeleziono il vertice/i in base alle loro proprieta: {}".format(list(g.vs(name_eq="Giacomo"))))

"""
    There are also a few special structural properties for selecting edges:
"""
print("\nRecupero tutti gli archi connessi con il dato nodo: {}".format(list(g.es.select(_source=g.vs(name_eq="Giacomo")[0].index))))

"""
    _within= : takes a VertexSeq object or a list or set of vertex indices and selects all the edges that originate
    and terminate in the given vertex set.
    _between= : takes a tuple consisting of two VertexSeq objects or lists containing vertex indices or Vertex objects
    and selects all the edges that originate in one of the sets and terminate in the other.
"""

"""
    VertexSeq and EdgeSeq objects provide the find() method for such use-cases.
    find() works similarly to select(), but it returns only the first match if there are multiple matches,
    and throws an exception if no match is found.
"""
print("\nIl nodo cercato e: {}".format(g.vs.find(name="Giacomo")))

"""
    To this end, igraph treats the name attribute of vertices specially; they are indexed such that vertices can be looked up
    by their names in amortized constant time. To make things even easier, igraph accepts vertex names (almost) anywhere
    where it expects vertex IDs, and also accepts collections (list, tuples etc) of vertex names anywhere where it expects
    lists of vertex IDs or VertexSeq instances.
"""
# Creazione di un grafo tramite direttamente i nomi dei nodi...
g2=Graph()
g2.add_vertices(["Pedro","Angela","Simone"])
g2.add_edges([("Pedro","Angela"),("Pedro","Simone")])
plot(g2)


g = Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)])
g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]
color_dict = {"m": "blue", "f": "pink"}
layout = g.layout("kk")
visual_style = {}
visual_style["vertex_size"] = 20
visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
visual_style["vertex_label"] = g.vs["name"]
visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
visual_style["layout"] = layout
visual_style["bbox"] = (300, 300)
visual_style["margin"] = 10
plot(g, **visual_style)
plot(g, "social_network.pdf", **visual_style)
