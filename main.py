__author__ = 'maury'

import json
import time
import networkx
from igraph import *
from os.path import isfile
from networkx.algorithms import bipartite

# Permette di definire la tipologia di grafo bipartito (user-cat) (user-bus) ...
tipoGrafo="friends"
categoria="Nightlife"
communitiesTypes=["fastgreedy", "walktrap", "label_propagation", "infomap", "multilevel"]
communityType="all"
pathInput="/home/maury/Desktop/ClusteringMethods/InputData/"
fileNameInput="user_"+tipoGrafo+"_("+categoria+").json"
pathOutput="/home/maury/Desktop/ClusteringMethods/OutputData/"
fileNameGraph="user_"+tipoGrafo+"_("+categoria+")_graph"
fileNameGraphML="user_"+tipoGrafo+"("+categoria+")_graphML"

def recuperaDati(fileName):
    return json.load(open(fileName))

def createGraph(inputData,tipoGrafo):
    g=Graph()
    if tipoGrafo!="friends":
        # Creo i vertici (business/tags) del grafo bipartito
        values={value for lista in inputData.values() for value in lista}
        for value in values:
            g.add_vertex(name=value,gender=tipoGrafo,label=value)

        # Recupero i vertici (users) del grafo bipartito
        users={user for user in inputData.keys()}
        for user in users:
            g.add_vertex(name=user,gender="user",label=user)

    else:
        # Recupero i vertici (users) del grafo delle amicizie
        users={user for user in inputData.keys()}.union({friend for listFriends in inputData.values() for friend,weight in listFriends})
        for user in users:
            g.add_vertex(name=user,gender="user",label=user)

        def createPairs(user,listFriends):
            return [(user,friend) for friend,_ in listFriends]

        # Creo gli archi (di amicizia) del grafo
        listaList=[createPairs(user,listFriends) for user,listFriends in inputData.items()]
        archi=[(user,friend) for lista in listaList for user,friend in lista]
        g.add_edges(archi)
        # Aggiungo i relativi pesi agli archi
        weights=[weight for user,listFriends in inputData.items() for friend,weight in listFriends]
        g.es["weight"]=weights
    return g

def saveGraphs(g):
    g.write_pickle(fname=open(pathOutput+fileNameGraph,"wb"))
    g.write_graphml(f=open(pathOutput+fileNameGraphML+".graphml","wb"))

def creazioneGrafo(tipoGrafo):
    # Recupero i dati dal file Json
    diz=recuperaDati(fileName=pathInput+fileNameInput)
    # Creo il grafo
    g=createGraph(inputData=diz,tipoGrafo=tipoGrafo)
    # g.vs["label"] = g.vs["name"]
    # Save graphs (binary format e GraphML format)
    saveGraphs(g)
    return g

def creazioneProiezione():
    g=Graph.Read_Pickle(fname=open(pathOutput+fileNameGraph))
    g1=g.bipartite_projection(which=1)
    # bipar=g.bipartite_projection(types="proiezione",which=0)
    # summary("\n{}".format(bipar))

def creazioneCommunities(g,communityType):
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

if __name__ == '__main__':
    startTime=time.time()
    g=creazioneGrafo(tipoGrafo)
    print("\nIl grafo e stato creato! Tempo: {} min.".format((time.time()-startTime)/60))
    print("Summary:\n{}".format(summary(g)))

    if tipoGrafo=="friends":
        # Sto andando a trovare le communities delle amicizie
        startTime=time.time()
        creazioneCommunities(g,communityType)
        print("\nFinito di calcolare le communities in TEMPO: {}".format((time.time()-startTime)/60))
"""
    else:
        # Dal grafo bipartito (Users-Tags)/(Users-Business) vado a creare la proiezione sugli users e da qui trovo le communities (overlapping)
        creazioneProiezione()
        startTime=time.time()
        creazioneCommunities(g)
        print("\nFinito di calcolare le commuities in TEMPO: {}".format((time.time()-startTime)/60))

    # Passo attraverso Networkx
    a=g.get_edgelist()
    b=networkx.Graph(a)
    bottom_nodes, top_nodes = bipartite.sets(b)
"""
