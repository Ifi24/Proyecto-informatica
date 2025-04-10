from node import Node
class Segment:
   def __init__ (self, name, origin: Node, destination: Node):
       self.name = name
       self.origin = origin
       self.destination = destination
       self.cost = self.calcular_cost()


   def calcular_cost(self):
       dx = self.destination.x - self.origin.x
       dy = self.destination.y - self.origin.y
       return (dx ** 2 + dy ** 2) ** 0.5


   def __str__(self) -> str:
       return (f"Segment '{self.name}': {self.origin.name} -> {self.destination.name}, "
               f"cost: {self.cost:.2f}")