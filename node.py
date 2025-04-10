#paso 1
import math
class Node:
    def __init__(self, name, x ,y):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.neighbors = []
    def AddNeighbor (self, n2):
        if n2 in self.neighbors:
           return False
        self.neighbors.append(n2)
        return True
    
def Distance(n1, n2):
    return math.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2)
