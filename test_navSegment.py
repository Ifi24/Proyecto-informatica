from navSegment import NavSegment

def test_navSegment():
    seg = NavSegment(100, 200, 145.6)
    print(f"Origen: {seg.OriginNumber}, Destino: {seg.DestinationNumber}, Distancia: {seg.Distance} km")

test_navSegment()
