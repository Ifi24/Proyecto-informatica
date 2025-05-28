class Path:
    def __init__(self, nodes):
        self.nodes = nodes

    def LastNode(self):
        return self.nodes[-1]

    def ContainsNode(self, node):
        return node in self.nodes

    def CloneAndAdd(self, node):
        return Path(self.nodes + [node])

    def CostToNode(self, node):
        cost = 0
        for i in range(1, self.nodes.index(node) + 1):
            cost += self.Distance(self.nodes[i - 1], self.nodes[i])
        return cost

    def EstimatedTotalCost(self, goal):
        return self.CostToNode(self.LastNode()) + self.Distance(self.LastNode(), goal)

    def Distance(self, n1, n2):
        dx = n2.lon - n1.lon
        dy = n2.lat - n1.lat
        return (dx ** 2 + dy ** 2) ** 0.5
