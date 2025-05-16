import math

class NavPoint:
    def __init__(self, number, name, lat, lon):
        self.number = number
        self.name = name
        self.lat = lat
        self.lon = lon

    def distance(self, other):

        R = 6371.0

        # Convertir grados a radianes
        lat1 = math.radians(self.lat)
        lon1 = math.radians(self.lon)
        lat2 = math.radians(other.lat)
        lon2 = math.radians(other.lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance
