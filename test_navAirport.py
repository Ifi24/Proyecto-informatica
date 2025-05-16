from navAirport import NavAirport

def test_navAirport():
    airport = NavAirport("LEIB", "IZA.D", "IZA.A")
    print(f"Airport name: {airport.name}")
    print(f"SIDs: {airport.sid}")
    print(f"STARs: {airport.star}")

test_navAirport()
