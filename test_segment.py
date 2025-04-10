from node import *
from segment import *

N1 = Node("node1", 2.3335, 6.6578)
N2 = Node("node2", 3.5709, 7.5213)
N3 = Node("node3", 7.0991, 10.6781)

S1 = Segment("segment1", N1, N2)
S2 = Segment("segment2", N2, N3)
print(S1)
print(S2)