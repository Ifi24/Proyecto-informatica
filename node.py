import math

class Node:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.neighbors = []

    def AddNeighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
