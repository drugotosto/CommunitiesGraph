__author__ = 'maury'

import json
import time
import networkx as nx
from igraph import *
from os.path import isfile
from networkx.algorithms import bipartite

# Permette di definire la tipologia di grafo bipartito (user-cat) (user-bus) ...
tipoGrafo="cat"
single=False
categoria="Nightlife"
communitiesTypes=["fastgreedy", "walktrap", "label_propagation", "infomap", "multilevel"]
communityType="all"
pathInput="/home/maury/Desktop/ClusteringMethods/InputData/"
pathOutput="/home/maury/Desktop/ClusteringMethods/OutputData/"
fileNameGraph="user_"+tipoGrafo+"_("+categoria+")_graph"
fileNameGraphML="user_"+tipoGrafo+"("+categoria+")_graphML"

def recuperaDati(fileName):
    return json.load(open(fileName))

def createGraph(inputData,tipoGrafo):
    g=Graph()
    if tipoGrafo!="friends":
        # Creo i vertici (business/tags) del grafo bipartito
        values={elem for lista in inputData.values() for elem,_ in lista}
        for value in values:
            g.add_vertex(name=value,gender=tipoGrafo,label=value,bipartite=1)

        # Recupero i vertici (users) del grafo bipartito
        users={user for user in inputData.keys()}
        for user in users:
            g.add_vertex(name=user,gender="user",label=user,bipartite=0)
    else:
        # Recupero i vertici (users) del grafo delle amicizie
        users={user for user in inputData.keys()}.union({friend for listFriends in inputData.values() for friend,weight in listFriends})
        for user in users:
            g.add_vertex(name=user,gender="user",label=user)

    def createPairs(user,listItems):
        return [(user,item[0]) for item in listItems]

    # Creo gli archi (amicizie/tag) del grafo
    listaList=[createPairs(user,listItems) for user,listItems in inputData.items()]
    archi=[(user,elem) for lista in listaList for user,elem in lista]
    g.add_edges(archi)
    # Aggiungo i relativi pesi agli archi
    weights=[weight for user,listItems in inputData.items() for _,weight in listItems]
    g.es["weight"]=weights
    return g

def saveGraphs(g):
    g.write_pickle(fname=open(pathOutput+fileNameGraph,"wb"))
    g.write_graphml(f=open(pathOutput+fileNameGraphML+".graphml","wb"))

def creazioneGrafo(tipoGrafo):
    fileNameInput="user_"+tipoGrafo+"_("+categoria+").json"
    # Recupero i dati dal file Json
    if tipoGrafo=="cat":
        if single:
            fileNameInput="user_"+tipoGrafo+"_("+categoria+")_singleWeight.json"
        else:
            fileNameInput="user_"+tipoGrafo+"_("+categoria+")_2moreWeight.json"
    diz=recuperaDati(fileName=pathInput+fileNameInput)
    # Creo il grafo
    g=createGraph(inputData=diz,tipoGrafo=tipoGrafo)
    # g.vs["label"] = g.vs["name"]
    # Save graphs (binary format e GraphML format)
    saveGraphs(g)
    return g

def creazioneProiezione(g):
    """
    Dal grafo bipartito (User-Tag) vado a generare la proiezione sugli users
    :param g:
    :type g: Graph
    :return:
    """
    def my_weight(G, u, v, weight='weight'):
        w = 0
        for nbr in set(G[u]) & set(G[v]):
            w += G.edge[u][nbr].get(weight, 1) + G.edge[v][nbr].get(weight, 1)
        return w

    print("\nVado a creare prima il grafo bipartito e poi la proiezione sugli utenti!")
    # Passo attraverso Networkx
    B=nx.read_graphml(path=pathOutput+fileNameGraphML+".graphml")
    if nx.is_connected(B):
        top_nodes = set((n,d["gender"]) for n,d in B.nodes(data=True) if d['bipartite']==1)
        bottom_nodes = set(B) - top_nodes
        print("\nGrafo bipartito?: {}".format(nx.is_bipartite(B)))
        print("NODI: {}".format(list(top_nodes)[:10]))
        G = bipartite.generic_weighted_projected_graph(B,bottom_nodes,weight_function=my_weight)
        print("\nArchi: {}".format(G.edges(data=True)[:10]))

def creazioneCommunities(g):
    if tipoGrafo=="friends":
        print("\nCreo le communities in base alla friendships!")
        # calculate dendrogram
        dendrogram=None
        clusters=None
        if communityType=="all":
            types=communitiesTypes
        else:
            types=[communityType]

        for type in types:
            if type=="fastgreedy":
                dendrogram=g.community_fastgreedy(weights="weight")
            elif type=="walktrap":
                dendrogram=g.community_walktrap(weights="weight")
            elif type=="label_propagation":
                clusters=g.community_label_propagation(weights="weight")
            elif type=="multilevel":
                clusters=g.community_multilevel(weights="weight",return_levels=False)
            elif type=="infomap":
                clusters=g.community_infomap(edge_weights="weight")

            # convert it into a flat clustering (VertexClustering)
            if type!="label_propagation" and type!="multilevel" and type!="infomap":
                clusters = dendrogram.as_clustering()
            # get the membership vector
            membership = clusters.membership
            json.dump([(name,membership) for name, membership in zip(g.vs["name"], membership)],open(pathOutput+"communities_friends_("+categoria+")_"+type+".json","w"))
            print("Clustering Summary for '{}' : {}".format(type,clusters.summary()))
    else:
        print("\nCreo le overlapping communities in base alle relazioni (User-Tag) esistenti!")
        pass

if __name__ == '__main__':
    if not isfile(pathOutput+fileNameGraph):
        print("\nVado a creare il grafo!")
        startTime=time.time()
        g=creazioneGrafo(tipoGrafo)
        print("\nIl grafo e stato creato! Tempo: {} min.".format((time.time()-startTime)/60))
        print("Summary:\n{}".format(summary(g)))

        if tipoGrafo=="friends":
            # Sto andando a trovare le communities delle amicizie
            startTime=time.time()
            creazioneCommunities(g)
            print("\nFinito di calcolare le communities in TEMPO: {}".format((time.time()-startTime)/60))

        else:
            # Dal grafo bipartito (Users-Tags)/(Users-Business) vado a creare la proiezione sugli users e da qui trovo le communities (overlapping)
            startTime=time.time()
            print("\nFinito di calcolare la proiezione in TEMPO: {}".format((time.time()-startTime)/60))
    else:
        print("\nVado a prelevare il grafo!")
        g=Graph.Read_Pickle(fname=open(pathOutput+fileNameGraph))
        if tipoGrafo=="friends":
            startTime=time.time()
            creazioneCommunities(g)
            print("\nFinito di calcolare le communities in TEMPO: {}".format((time.time()-startTime)/60))
        else:
            creazioneProiezione(g)

