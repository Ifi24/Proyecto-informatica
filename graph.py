from node import *
from segment import *
from path import *
import matplotlib.pyplot as plt
import math

class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []

    def AddNode(self, node):    #añade un nodo al grafo si aún no está en la lista.
        if node in self.nodes:
            return False
        self.nodes.append(node)
        return True

    def AddSegment(self, name, nameoriginNode, namedestinationNode):
        origin = self.GetNodeByName(nameoriginNode) if isinstance(nameoriginNode, str) else nameoriginNode
        destination = self.GetNodeByName(namedestinationNode) if isinstance(namedestinationNode, str) else namedestinationNode
        if not origin or not destination:
            return False
        segment = Segment(name, origin, destination)
        self.segments.append(segment)
        origin.AddNeighbor(destination)
        return True
   
    def LoadFromFile(self, filename): # lee y categoriza los datos de los archivos
        with open(filename, 'r') as f:
            section = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#nodes'):
                    section = 'nodes'
                    continue
                elif line.startswith('#segments'):
                    section = 'segments'
                    continue

                # lee los nodos
                if section == 'nodes':
                    parts = line.split(',')
                    if len(parts) == 3:
                        name, x, y = parts
                        self.AddNode(Node(name, float(x), float(y)))

                #lee los segmentos
                elif section == 'segments':
                    parts = line.split(',')
                    seg_name, origin, destination = parts[:3]
                    self.AddSegment(seg_name, origin, destination)
<<<<<<< HEAD


        return True

    def GetClosest(self, x, y): # encuentra los nodos más cercanos
            closest_node = None
            min_distance = float('100000')

            for node in self.nodes:
                d = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
                if d < min_distance:
                    min_distance = d
                    closest_node = node

            return closest_node

    def GetNodeByName(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def Plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        for segment in self.segments:
            x_values = [segment.origin.x, segment.destination.x]
            y_values = [segment.origin.y, segment.destination.y]
            ax.plot(x_values, y_values, 'blue', linewidth=1)
        for node in self.nodes:
            ax.scatter(node.x, node.y, color='red', s=100)
            ax.text(node.x, node.y, node.name, fontsize=12)
        ax.set_title("Graph")
        ax.grid(True)

    def PlotNode(self, nameorigin): # hace el plot de los nodos vecinos
        origin = next((n for n in self.nodes if n.name == nameorigin), None)
        if not origin:
            return False

        fig, ax = plt.subplots(figsize=(8, 6))
        for segment in self.segments:
            if segment.origin == origin or segment.destination == origin:
                x_values = [segment.origin.x, segment.destination.x]
                y_values = [segment.origin.y, segment.destination.y]

                ax.annotate('', xy=(segment.destination.x, segment.destination.y),
                    xytext=(segment.origin.x, segment.origin.y),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=2))

                mid_x = (segment.origin.x + segment.destination.x) / 2
                mid_y = (segment.origin.y + segment.destination.y) / 2
                ax.text(mid_x, mid_y, f"{segment.cost:.1f}", fontsize=10, color='black')

        # Dibuja los nodos
        for node in self.nodes:
            color = 'gray'
            if node == origin:
                color = 'blue'
            elif node in origin.neighbors:
                color = 'green'
            ax.scatter(node.x, node.y, color=color, s=100)
            ax.text(node.x, node.y, node.name, fontsize=12)

        ax.set_title('Gráfico de nodos y segmentos vecinos')
        ax.grid(True, color='red')
        fig.tight_layout()
        plt.show()
        return True


    def FindShortestPath(self, origin_name, dest_name):
        origin = self.GetNodeByName(origin_name)
        destination = self.GetNodeByName(dest_name)

        current_paths = [Path([origin])]    #Crea una lista con un camino inicial que solo contiene el nodo origen
        total=0
        while current_paths:    #Mientras haya caminos posibles
            current_path = None
            min_cost = float('1000000')
            #selecciona el camino más corto
            for path in current_paths:
                cost = path.EstimatedTotalCost(self, destination)
                if cost < min_cost:
                    min_cost = cost
                    current_path = path
                    total+=cost     #en esta variable se almacenan todos los costes

            current_paths.remove(current_path)  # Elimina el path seleccionado de la lista, hay otro mejor

            last = current_path.LastNode()

            if last == destination: #si hemos llegado al nodo de destino
                return current_path

            for segment in self.segments:   #Devuelve el destino si ha llegdo
                if segment.origin == last:
                    neighbor = segment.destination  #Mira todos los segmentos que parten del nodo actual
                    if current_path.ContainsNode(neighbor):
                        continue

                    better = True
                    for other_path in current_paths:    # salta el vecino ya está en el camino
                        if other_path.ContainsNode(neighbor):
                            if other_path.CostToNode(neighbor) <= current_path.CostToNode(last) + segment.length():
                                better = False
                                break
                            else:
                                current_paths.remove(other_path)
                    if better:      #hay un camino mejor hacia ese vecino?
                        new_path = current_path.CloneAndAdd(neighbor)
                        current_paths.append(new_path)
        return None
    
    def ShowReachability(self, origin_name):
        origin = self.GetNodeByName(origin_name)
        if not origin:
            return []

        visited = []
        lista = [origin]
        i = 0

=======


        return True

    def GetClosest(self, x, y): # encuentra los nodos más cercanos
            closest_node = None
            min_distance = float('100000')

            for node in self.nodes:
                d = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
                if d < min_distance:
                    min_distance = d
                    closest_node = node

            return closest_node

    def GetNodeByName(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def Plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        for segment in self.segments:
            x_values = [segment.origin.x, segment.destination.x]
            y_values = [segment.origin.y, segment.destination.y]
            ax.plot(x_values, y_values, 'blue', linewidth=1)
        for node in self.nodes:
            ax.scatter(node.x, node.y, color='red', s=100)
            ax.text(node.x, node.y, node.name, fontsize=12)
        ax.set_title("Graph")
        ax.grid(True)

    def PlotNode(self, nameorigin): # hace el plot de los nodos vecinos
        origin = next((n for n in self.nodes if n.name == nameorigin), None)
        if not origin:
            return False

        fig, ax = plt.subplots(figsize=(8, 6))
        for segment in self.segments:
            if segment.origin == origin or segment.destination == origin:
                x_values = [segment.origin.x, segment.destination.x]
                y_values = [segment.origin.y, segment.destination.y]

                # Dibuja flechas rojas entre los nodos
                ax.annotate('', xy=(segment.destination.x, segment.destination.y),
                    xytext=(segment.origin.x, segment.origin.y),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=2))

                mid_x = (segment.origin.x + segment.destination.x) / 2
                mid_y = (segment.origin.y + segment.destination.y) / 2
                ax.text(mid_x, mid_y, f"{segment.cost:.1f}", fontsize=10, color='black')

        # Dibuja los nodos
        for node in self.nodes:
            color = 'gray'
            if node == origin:
                color = 'blue'
            elif node in origin.neighbors:
                color = 'green'
            ax.scatter(node.x, node.y, color=color, s=100)
            ax.text(node.x, node.y, node.name, fontsize=12)

        ax.set_title('Gráfico de nodos y segmentos vecinos')
        ax.grid(True, color='red')
        fig.tight_layout()
        plt.show()
        return True


    def FindShortestPath(self, origin_name, dest_name):
        origin = self.GetNodeByName(origin_name)
        destination = self.GetNodeByName(dest_name)

        current_paths = [Path([origin])]    #Crea una lista con un camino inicial que solo contiene el nodo origen
        total=0
        while current_paths:    #Mientras haya caminos posibles
            current_path = None
            min_cost = float('1000000')
            #selecciona el camino más corto
            for path in current_paths:
                cost = path.EstimatedTotalCost(self, destination)
                if cost < min_cost:
                    min_cost = cost
                    current_path = path
                    total+=cost     #en esta variable se almacenan todos los costes

            current_paths.remove(current_path)  # Elimina el path seleccionado de la lista, hay otro mejor

            last = current_path.LastNode()

            if last == destination: #si hemos llegado al nodo de destino
                return current_path

            for segment in self.segments:   #Devuelve el destino si ha llegdo
                if segment.origin == last:
                    neighbor = segment.destination  #Mira todos los segmentos que parten del nodo actual
                    if current_path.ContainsNode(neighbor):
                        continue

                    better = True
                    for other_path in current_paths:    # salta el vecino ya está en el camino
                        if other_path.ContainsNode(neighbor):
                            if other_path.CostToNode(neighbor) <= current_path.CostToNode(last) + segment.length():
                                better = False
                                break
                            else:
                                current_paths.remove(other_path)
                    if better:      #hay un camino mejor hacia ese vecino?
                        new_path = current_path.CloneAndAdd(neighbor)
                        current_paths.append(new_path)
        return None
    
    def ShowReachability(self, origin_name):
        origin = self.GetNodeByName(origin_name)
        if not origin:
            return []

        visited = []
        lista = [origin]
        i = 0

>>>>>>> 4fe02013f78ebcf4b5e548b2cb03eb5f3b6e5f97
        while i < len(lista):
            current = lista[i]
            i += 1
            if current not in visited:
                visited.append(current)
                for neighbor in current.neighbors:
                    if neighbor not in visited and neighbor not in lista:
                        lista.append(neighbor)

        return visited
