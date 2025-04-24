from graph import Graph
from node import Node
from path import PlotPath

def test_path():
    G = Graph()
    G.AddNode(Node("A", 1, 20))
    G.AddNode(Node("B", 8, 17))
    G.AddNode(Node("C", 15, 20))
    G.AddNode(Node("D", 18, 15))
    G.AddNode(Node("E", 2, 4))
    G.AddNode(Node("F", 6, 5))
    G.AddNode(Node("G", 12, 12))
    G.AddNode(Node("H", 10, 3))
    G.AddNode(Node("I", 19, 1))
    G.AddNode(Node("J", 13, 5))
    G.AddNode(Node("K", 3, 15))
    G.AddNode(Node("L", 4, 10))

    G.AddSegment("AB", "A", "B")
    G.AddSegment("AE", "A", "E")
    G.AddSegment("AK", "A", "K")
    G.AddSegment("BA", "B", "A")
    G.AddSegment("BC", "B", "C")
    G.AddSegment("BF", "B", "F")
    G.AddSegment("BK", "B", "K")
    G.AddSegment("BG", "B", "G")
    G.AddSegment("CD", "C", "D")
    G.AddSegment("CG", "C", "G")
    G.AddSegment("DG", "D", "G")
    G.AddSegment("DH", "D", "H")
    G.AddSegment("DI", "D", "I")
    G.AddSegment("EF", "E", "F")
    G.AddSegment("FL", "F", "L")
    G.AddSegment("GB", "G", "B")
    G.AddSegment("GF", "G", "F")
    G.AddSegment("GH", "G", "H")
    G.AddSegment("ID", "I", "D")
    G.AddSegment("IJ", "I", "J")
    G.AddSegment("JI", "J", "I")
    G.AddSegment("KA", "K", "A")
    G.AddSegment("KL", "K", "L")
    G.AddSegment("LK", "L", "K")
    G.AddSegment("LF", "L", "F")
    path = G.FindShortestPath(str(input('Origen: ')), str(input('Final: ')))

    if path:
        print("Camino + corto:", " > ".join(n.name for n in path.nodes))
        print("Coste total:", path.cost)
        PlotPath(G, path)
    else:
        print("Camino no encontrado")
        
if __name__ == '__main__':
    test_path()