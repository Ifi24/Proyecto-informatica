from node import *
from segment import *
import matplotlib.pyplot as plt


class Graph:
    def __init__(self): # inicia la clase Graph
        self.nodes = []
        self.segments = []


    def AddNode(self, node): # añade un node, versión solo para usar en graph.py
        if node in self.nodes:
            return False
        self.nodes.append(node)
        return True


    def AddSegment(self, name, nameoriginNode, namedestinationNode):  # No se pasa 'self' explícitamente, versión solo para usar en graph.py
        origin = next((n for n in self.nodes if n.name == nameoriginNode), None)
        destination = next((n for n in self.nodes if n.name == namedestinationNode), None)

        if not origin or not destination:
            return False

        # Aquí se pasa correctamente el objeto origin y destination a Segment
        segment = Segment(name, origin, destination)
        self.segments.append(segment)
        origin.AddNeighbor(destination)
        return True


    def GetClosest(self, x, y): # encuentra los nodos más cercanos
            closest_node = None
            min_distance = float('inf')

            for node in self.nodes:
                d = ((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5
                if d < min_distance:
                    min_distance = d
                    closest_node = node

            return closest_node


    def Plot(self): # hace el plot del gráfico
        plt.figure(figsize=(8, 6))
        for segment in self.segments:
            x_values = [segment.origin.x, segment.destination.x]
            y_values = [segment.origin.y, segment.destination.y]
            plt.annotate('', xy=(segment.destination.x, segment.destination.y),
                         xytext=(segment.origin.x, segment.origin.y),
                         arrowprops=dict(arrowstyle='->', color='blue', lw=2))            
            plt.plot(x_values, y_values, 'k-', linewidth=1)
            mid_x = (segment.origin.x + segment.destination.x) / 2
            mid_y = (segment.origin.y + segment.destination.y) / 2
            plt.text(mid_x, mid_y, f"{segment.cost:.1f}", fontsize=10, color='red')

        for node in self.nodes:
            plt.scatter(node.x, node.y, color='red', s=100)
            plt.text(node.x, node.y, node.name, fontsize=12)

        plt.title("Gráfico con nodos y segmentos")
        plt.grid(True)
        plt.show()
        return plt.subplots()


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


        return True
    
    def GetNodeByName(self, name): # encuentra el nodo por su nombre
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    

    

    