import random

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def assign_flow(graph, matrix):
    nx.set_edge_attributes(graph, 0, 'a')
    nodes = nx.number_of_nodes(graph)
    for i in range(nodes):
        for j in range(nodes):
            path = nx.shortest_path(graph, i, j)
            for n in range(len(path) - 1):
                graph[path[n]][path[n + 1]]['a'] += matrix[i][j]


def T(graph, matrix):
    G = matrix.sum()
    SUM = sum(
        [graph.get_edge_data(*e).get('a') / (graph.get_edge_data(*e).get('c') - graph.get_edge_data(*e).get('a')) for e
         in graph.edges()])
    return (SUM / G)


def test_model(graph, matrix, reps=1000):
    delays = []
    for rep in range(reps):
        g = nx.Graph(graph)

        for e in graph.edges():
            if random.random() > g.get_edge_data(*e).get('p'):
                g.remove_edge(*e)

        if not nx.is_connected(g):
            continue

        assign_flow(g, matrix)

        for e in g.edges():
            if g.get_edge_data(*e).get('a') > g.get_edge_data(*e).get('c'):
                break
        else:
            delays.append(T(g, matrix))

    if len(delays) == 0:
        print("failed")
        return 1
    else:
        print("Succeded in", len(delays) / reps * 100, "%. Average delay:", sum(delays) / len(delays))

    return delays

def reliability(graph, matrix, T_max, p = 0.95):
    g = nx.Graph(graph)
    nx.set_edge_attributes(g, p, 'p')
    delays = test_model(g, matrix) or [1]
    counter = 0
    for d in delays:
        if d < T_max:
            counter += 1
    return counter/len(delays)*100

def test1(graph, matrix, T_max = 0.009):
    g = nx.Graph(graph)
    for i in range(3):
        # print(matrix)
        for x in matrix:
            x += 1
        # print(matrix)
        assign_flow(g,matrix)
        print("Reliability of the network: ",reliability(g, matrix, T_max))

def test2(graph, matrix, T_max = 0.0007):
    g = nx.Graph(graph)
    for i in range(6):
        for e in g.edges():
            tmp = g.get_edge_data(*e).get('c') + 40
            nx.set_edge_attributes(g, tmp, 'c')
        print("Reliability of the network: ", reliability(g, matrix, T_max))

def test3(graph, matrix, T_max = 0.004689):
    g = nx.Graph(graph)
    for i in range(5):
        g.add_edge(i + 4, i + 14)
        nx.set_edge_attributes(g, 0.95, 'p')  # stala niezawodnosc
        nx.set_edge_attributes(g, 1024, 'c')  # stala przepustowosc
        assign_flow(g, matrix)
        print("Reliability of the network after adding the edge: ", reliability(g, matrix, T_max))
    #nx.draw(graph)
    #plt.savefig("graph2.png")
    #print("(just in case) number of edges: ", nx.number_of_edges(graph))





def main():
    G = nx.cycle_graph(20)
    C = nx.Graph(G)
    for i in range(5):
        C.add_edge(i, i + 5)
    for i in range(5):
        C.add_edge(i + 10, i + 15)
    print("(just in case) number of edges: ", nx.number_of_edges(C))
    # macierz natezen
    RANGE = C.number_of_nodes()
    N = np.zeros((RANGE, RANGE))
    for i in range(RANGE):
        for j in range(RANGE):
            if i != j:
                N[i][j] = random.randint(1, 10)
            else:
                N[i][j] = 0
        nx.set_edge_attributes(C, 0.95, 'p')  # stala niezawodnosc
        nx.set_edge_attributes(C, 1024, 'c')  # stala przepustowosc
    assign_flow(C, N)

    # graf
    nx.draw(C)
    plt.figure(figsize=(5, 5))
    plt.show()
    plt.savefig("graph.png")

    N_copy = N  # kopia poczatkowej macierzy natezen

    test_model(C, N)
    print("Reliability of the network: ",reliability(C, N, 0.009))

    print("Test 1 (incrementing the matrix)")
    test1(C,N_copy)
    print("Test 2 (incrementing the c)")
    test2(C,N)
    print("Test 3 (adding new edges)")
    test3(C,N)


if __name__ == "__main__":
    main()
