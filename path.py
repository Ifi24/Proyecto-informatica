import matplotlib.pyplot as plt

class Path:
    def __init__(self, nodes):
        self.nodes = nodes
        self.cost = 0.0

    def AddNodeToPath(self, node, cost):    #Añade un nodo al camino y actualiza su coste
        self.nodes.append(node)
        self.cost += cost

    def ContainsNode(self, node):   #Verifica si un nodo está en el camino
        if node in self.nodes:
            return True
        else:
            return False 

    def CostToNode(self, node):
        if node not in self.nodes:  #Si el nodo no está en la lista de nodos que forman el camino
            return -1
        posicion = self.nodes.index(node)   #Busca la posición (index) del nodo dentro de la lista
        total = 0
        for i in range(posicion):
            total += self.nodes[i].distance(self.nodes[i+1])    #Calcula distancia total
        return total

    def CloneAndAdd(self, node):    #Crea una copia del camino actual y le añade un nuevo nodo al final actualizando el coste total
        new_path = Path(self.nodes.copy())
        new_path.cost = self.cost + self.nodes[-1].distance(node)
        new_path.nodes.append(node)
        return new_path 

    def LastNode(self):
        return self.nodes[-1]   #Devuelve el último nodo añadido al camino

    def EstimatedTotalCost(self, graph, destination):   #Se suma el coste actual con la distancia estimada entre el último nodo y el destino
        return self.cost + self.LastNode().distance(destination)    #Llama al método LastNode y luego a su método distance (definido en Node)

def PlotPath(graph, path):  #Crea un gráfico
    fig, ax = plt.subplots()
    graph.Plot(ax)
    for i in range(len(path.nodes) - 1):
        n1 = path.nodes[i]
        n2 = path.nodes[i + 1]
        ax.plot([n1.x, n2.x], [n1.y, n2.y], 'green', linewidth=3) #crea una línea conectando un nodo con el siguiente del camino
    plt.title("Camino + corto")
    plt.show()