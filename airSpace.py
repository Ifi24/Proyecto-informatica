from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport

class Airspace:
    def __init__(self):
        self.navpoints = {}       # número -> NavPoint
        self.segments = []        # lista de NavSegment
        self.airports = {}        # nombre -> NavAirport
        self.routes = []     # rutas: lista de navpoints o coords
        self.current_route = []
        
    def LoadNavPoints(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 4:
                    number = int(parts[0])
                    name = parts[1]
                    lat = float(parts[2])
                    lon = float(parts[3])
                    self.navpoints[number] = NavPoint(number, name, lat, lon)

    def LoadNavSegments(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    origin_num = int(parts[0])
                    dest_num = int(parts[1])
                    distance = float(parts[2])
                    if origin_num in self.navpoints and dest_num in self.navpoints:
                        segment = NavSegment(origin_num, dest_num, distance)
                        self.segments.append(segment)

    def LoadNavAirports(self, filename):
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            current_airport = None
            for line in lines:
                if '.' not in line:
                    current_airport = NavAirport(line)
                    self.airports[line] = current_airport
                elif current_airport:
                    if line.endswith('.D'):
                        current_airport.sid= line
                    elif line.endswith('.A'):
                        current_airport.star= line

    def start_new_route(self):
            self.current_route = []
        
    def add_to_route(self, point_number):
        if point_number in self.navpoints:
            self.current_route.append(point_number)
            
    def remove_last_from_route(self):
        if self.current_route:
            self.current_route.pop()
            
    def save_current_route(self):
        if len(self.current_route) > 1:  #  ruta al menos 2 puntos
            self.routes.append(self.current_route.copy())
            self.current_route = []
            
    def clear_current_route(self):
        self.current_route = []
        
    def get_route_points(self):
        return [self.navpoints[num] for num in self.current_route if num in self.navpoints]
        
    def get_saved_routes(self):
        return [[self.navpoints[num] for num in route if num in self.navpoints] for route in self.routes]