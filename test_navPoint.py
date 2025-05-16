from navPoint import NavPoint

def test_distance():
    p1 = NavPoint(1, "P1", 41.0, 2.0)
    p2 = NavPoint(2, "P2", 42.0, 3.0)
    print(f"Distancia entre {p1.name} y {p2.name}: {p1.distance(p2)} km")

test_distance()
