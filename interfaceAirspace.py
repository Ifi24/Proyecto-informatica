import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrow
from airSpace import Airspace
import webbrowser
from tkinter import simpledialog
from PIL import Image, ImageTk, ImageSequence

class AirSpaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Espacio Aéreo")

        self.airspace = Airspace()
        self.figure, self.ax = plt.subplots()

        self.figure.set_size_inches(8, 6) 
        self.ax.set_aspect('auto') 

        self.animating = False
        self.paused = False
        self.animation_data = None  # Guarda el estado actual (points, i, step)

        left_container = tk.Frame(root)
        left_container.pack(side=tk.LEFT, fill=tk.Y)

        canvas = tk.Canvas(left_container)
        scrollbar = tk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        zoom_frame = tk.Frame(scrollable_frame)
        zoom_frame.pack(pady=5)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(scrollable_frame, text="Cargar NavPoints", command=self.load_navpoints).pack(pady=5)
        tk.Button(scrollable_frame, text="Cargar NavSegments", command=self.load_navsegments).pack(pady=5)
        tk.Button(scrollable_frame, text="Cargar Airports", command=self.load_airports).pack(pady=5)

        graph_frame = tk.LabelFrame(scrollable_frame, text="Visualización de grafo", padx=5, pady=5)
        graph_frame.pack(pady=5, fill=tk.X)

#vecinos entrada

        self.entry_point_number = tk.Entry(graph_frame)
        self.entry_point_number.pack()
        self.entry_point_number.insert(0, "Nombre del punto")

        tk.Button(graph_frame, text="Mostrar vecinos", command=self.show_neighbors).pack(pady=5)

# para camino
        self.entry_origin = tk.Entry(graph_frame)
        self.entry_origin.pack(pady=2)
        self.entry_origin.insert(0, "Nombre del origen (Ej: GODOX)")

        self.entry_dest = tk.Entry(graph_frame)
        self.entry_dest.pack(pady=2)
        self.entry_dest.insert(0, "Nombre del destino (Ej: MANDY)")
        tk.Button(graph_frame, text="Camino más corto", command=self.show_shortest_path).pack(pady=5)


        self.output_text = tk.Text(scrollable_frame, height=10, width=35)
        self.output_text.pack(pady=5)

#  construcción de rutas
        route_frame = tk.LabelFrame(scrollable_frame, text="Construcción de Rutas", padx=5, pady=5)
        route_frame.pack(pady=5, fill=tk.X)

        tk.Label(route_frame, text="Nombre del punto").pack()
        self.entry_route_point = tk.Entry(route_frame)
        self.entry_route_point.pack(pady=2)

        buttons_frame = tk.Frame(route_frame)
        buttons_frame.pack(pady=5)

        tk.Button(buttons_frame, text="Iniciar Ruta", command=self.start_route).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="Añadir Punto", command=self.add_to_route).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="Eliminar Último", command=self.remove_last_point).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="Guardar Ruta", command=self.save_route).pack(side=tk.LEFT, padx=2)
        tk.Button(buttons_frame, text="Cancelar Ruta", command=self.cancel_route).pack(side=tk.LEFT, padx=2)

        # Lista de rutas guardadas
        self.routes_listbox = tk.Listbox(scrollable_frame, height=5)
        self.routes_listbox.pack(pady=5, fill=tk.X)
        tk.Button(scrollable_frame, text="Mostrar Ruta", command=self.show_selected_route).pack(pady=2)
        tk.Button(scrollable_frame, text="Eliminar Ruta", command=self.delete_selected_route).pack(pady=2)
        tk.Button(scrollable_frame, text="Reproducir Ruta", command=self.animate_selected_route).pack(pady=2)
        
        btn_frame = tk.Frame(scrollable_frame)
        btn_frame.pack(pady=2)

        tk.Button(btn_frame, text="▶ Reproducir", command=self.animate_selected_route).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⏸ Pausar", command=self.pause_animation).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⏵ Reanudar", command=self.resume_animation).pack(side=tk.LEFT, padx=2)

        
        tk.Button(scrollable_frame, text="Guardar KML de Ruta", command=self.save_route_as_kml).pack(pady=2)
        tk.Button(scrollable_frame, text="Abrir KML en Google Earth", command=self.open_kml_in_google_earth).pack(pady=2)


        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def load_navpoints(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.airspace.LoadNavPoints(path)
            self.output_text.insert(tk.END, "NavPoints cargados.\n")
            self.draw_airspace()

    def load_navsegments(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.airspace.LoadNavSegments(path)
            self.output_text.insert(tk.END, "NavSegments cargados.\n")
            self.draw_airspace()

    def load_airports(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not path:
            return

        airports = {}
        current_airport = None
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                if len(line) == 4:
                    current_airport = line
                    airports[current_airport] = {'points': {}}
                elif current_airport:
                    parts = line.split('.')
                    if len(parts) == 2 and parts[1] in ['A', 'D']:
                        point_name = line
                        point = self.GetNavPointByName(point_name)
                        if point:
                            airports[current_airport]['points'][point_name] = {
                                'lat': point.lat,
                                'lon': point.lon
                            }

        # Calcular promedios y dibujar
        self.ax.clear()
        
        # Dibujar segmentos existentes
        for segment in self.airspace.segments:
            o = self.airspace.navpoints.get(segment.OriginNumber)
            d = self.airspace.navpoints.get(segment.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], 'gray', linewidth=0.5)

        # Dibujar puntos de navegación
        for point in self.airspace.navpoints.values():
            self.ax.plot(point.lon, point.lat, 'ro', markersize=4)
            self.ax.text(point.lon, point.lat, point.name, fontsize=8)

        # Procesar y dibujar aeropuertos
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Aeropuertos cargados\n")
        
        for airport, data in airports.items():
            points = list(data['points'].values())
            
            if len(points) >= 2:
                # Calcular posición  del aeropuerto haciendo la media entre .A y .D
                avg_lat = sum(p['lat'] for p in points) / len(points)
                avg_lon = sum(p['lon'] for p in points) / len(points)
                
                # Dibujar aeropuerto
                self.ax.plot(avg_lon, avg_lat, 's', color='green',
                            markersize=10, markerfacecolor='none', 
                            markeredgewidth=2)
                self.ax.text(avg_lon, avg_lat, airport, fontsize=10,
                            fontweight='bold', ha='center', va='bottom')
                
                # Dibujar puntos SID/STAR
                for point_name, coordenadas in data['points'].items():
                    self.ax.plot(coordenadas['lon'], coordenadas['lat'], 'o',
                            color='blue', markersize=6)
                    self.ax.text(coordenadas['lon'], coordenadas['lat'], point_name,
                            fontsize=8, ha='right')
                    self.ax.plot([coordenadas['lon'], avg_lon],
                            [coordenadas['lat'], avg_lat], '--',
                            color='green', linewidth=1)
                
            else:
                self.output_text.insert(tk.END, f"- {airport}: No tiene suficientes puntos SID/STAR\n")

        self.ax.set_title("Espacio aéreo")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()

    def draw_airspace(self):
        self.ax.clear()
        for segment in self.airspace.segments:
            o = self.airspace.navpoints.get(segment.OriginNumber)
            d = self.airspace.navpoints.get(segment.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], 'blue')
                self.ax.text(o.lon, o.lat, o.name, fontsize=8)
                self.ax.text(d.lon, d.lat, d.name, fontsize=8)

        for point in self.airspace.navpoints.values():
            self.ax.plot(point.lon, point.lat, 'ro')

        self.ax.set_title("Espacio Aéreo")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()
    
    def get_neighbors(self, point_number):
        vecinos = set()
        for seg in self.airspace.segments:
            if seg.OriginNumber == point_number:
                vecinos.add(seg.DestinationNumber)
            elif seg.DestinationNumber == point_number:
                vecinos.add(seg.OriginNumber)
        return list(vecinos)

    def show_neighbors(self):
        name = self.entry_point_number.get().strip()
        self.output_text.delete("1.0", tk.END)

        point = next((p for p in self.airspace.navpoints.values() if p.name == name), None)

        if not point:
            self.output_text.insert(tk.END, "Punto no encontrado.\n")
            return

        neighbors = self.get_neighbors(point.number)

        if neighbors:
            self.output_text.insert(tk.END, f"Vecinos de {name}:\n")
            for n in neighbors:
                neighbor = self.airspace.navpoints.get(n)
                if neighbor:
                    self.output_text.insert(tk.END, f"- {neighbor.name}\n")
        else:
            self.output_text.insert(tk.END, "No se encontraron vecinos.\n")

        #que me plotee los vecinos
        self.ax.clear()
        highlighted_pairs = {(point.number, n) for n in neighbors} | {(n, point.number) for n in neighbors}

        for segment in self.airspace.segments:
            o = self.airspace.navpoints.get(segment.OriginNumber)
            d = self.airspace.navpoints.get(segment.DestinationNumber)
            if not o or not d:
                continue

        # Resalta solo si es una conexión directa al punto central
            if (segment.OriginNumber, segment.DestinationNumber) in highlighted_pairs:
                color = 'green'
                linewidth = 2
            else:
                color = 'gray'
                linewidth = 1

            self.ax.plot([o.lon, d.lon], [o.lat, d.lat], color=color, linewidth=linewidth)

        for p in self.airspace.navpoints.values():
            if p.number == point.number:
                color = 'yo'  # amarillo
            elif p.number in neighbors:
                color = 'go'  # verde
            else:
                color = 'o'   # gris sin color definido, negro por defecto
                self.ax.plot(p.lon, p.lat, color, markerfacecolor='gray', markeredgecolor='gray')
                self.ax.text(p.lon, p.lat, p.name, fontsize=8, color='gray')
                continue

            self.ax.plot(p.lon, p.lat, color)
            self.ax.text(p.lon, p.lat, p.name, fontsize=8)

        self.ax.set_title("Espacio Aéreo con Vecinos Destacados")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()
    
    def GetNavPointByName(self, name):
    # Buscar primero en los puntos de navegación
        for navpoint in self.airspace.navpoints.values():
            if navpoint.name == name:
                return navpoint
        
        # Si no se encuentra, buscar en los aeropuertos
        for airport in self.airspace.airports.values():
            if airport.name == name:
                return airport
        
        return None

    def FindShortestPath(self, origin_name, dest_name):
        origin = self.GetNavPointByName(origin_name)
        destination = self.GetNavPointByName(dest_name)

        if origin is None or destination is None:
            return None

        paths = [[origin]]  # Lista de caminos, cada uno es una lista de nodos

        while paths:
            # Seleccionamos y eliminamos el primer camino 
            current_path = paths[0]
            paths = paths[1:]

            current_node = current_path[-1]

            if current_node == destination:
                return current_path  # Camino encontrado

            for segment in self.airspace.segments:
                o = self.airspace.navpoints.get(segment.OriginNumber)
                d = self.airspace.navpoints.get(segment.DestinationNumber)

                neighbor = None
                if o == current_node and d not in current_path:
                    neighbor = d
                elif d == current_node and o not in current_path:
                    neighbor = o

                if neighbor:
                    new_path = current_path + [neighbor]
                    paths.append(new_path)

        return None  # No se encontró camino
    
    def show_shortest_path(self):
        origin_name = self.entry_origin.get().strip()
        dest_name = self.entry_dest.get().strip()
        self.output_text.delete("1.0", tk.END)

        if not origin_name or not dest_name:
            self.output_text.insert(tk.END, "Debes introducir ambos nombres.\n")
            return

        path = self.FindShortestPath(origin_name, dest_name)

        if not path:
            self.output_text.insert(tk.END, "No se encontró un camino.\n")
            return

        self.output_text.insert(tk.END, f"Camino de {origin_name} a {dest_name}:\n")
        for p in path:
            self.output_text.insert(tk.END, f"- {p.name}\n")

        # Dibujo
        self.ax.clear()

        # Dibujar segmentos en gris
        for seg in self.airspace.segments:
            o = self.airspace.navpoints.get(seg.OriginNumber)
            d = self.airspace.navpoints.get(seg.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], color='gray', linewidth=0.5)

        # Dibujar camino en rojo
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            self.ax.plot([a.lon, b.lon], [a.lat, b.lat], color='red', linewidth=2)

        # Dibujar puntos de navegación
        for point in self.airspace.navpoints.values():
            if point in path:
                self.ax.plot(point.lon, point.lat, 'ro')
            else:
                self.ax.plot(point.lon, point.lat, marker='o', color='gray')
            self.ax.text(point.lon, point.lat, point.name, fontsize=8)

        # Dibujar aeropuertos (con un marcador diferente)
        for airport in self.airspace.airports.values():
            if airport in path:
                self.ax.plot(airport.lon, airport.lat, 's', color='red')  # cuadrado rojo
            else:
                self.ax.plot(airport.lon, airport.lat, 's', color='blue')  # cuadrado azul
            self.ax.text(airport.lon, airport.lat, airport.name, fontsize=8, color='blue')

        self.ax.set_title("Camino más corto")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()

    # Métodos para manejar rutas
    def start_route(self):
        """Inicia una nueva ruta"""
        self.airspace.start_new_route()
        self.output_text.insert(tk.END, "Nueva ruta iniciada. Añade puntos.\n")
        self.update_routes_list()

    def add_to_route(self):
        """Añade un punto a la ruta actual"""
        name = self.entry_route_point.get().strip()
        point = self.GetNavPointByName(name)
        
        if not point:
            self.output_text.insert(tk.END, f"Punto {name} no encontrado.\n")
            return
            
        self.airspace.add_to_route(point.number)
        self.output_text.insert(tk.END, f"Añadido {name} a la ruta.\n")
        self.draw_current_route()

    def remove_last_point(self):
        """Elimina el último punto de la ruta actual"""
        if not self.airspace.current_route:
            self.output_text.insert(tk.END, "No hay puntos en la ruta actual.\n")
            return
            
        last_num = self.airspace.current_route[-1]
        last_name = self.airspace.navpoints[last_num].name
        self.airspace.remove_last_from_route()
        self.output_text.insert(tk.END, f"Eliminado {last_name} de la ruta.\n")
        self.draw_current_route()

    def save_route(self):
        """Guarda la ruta actual"""
        if len(self.airspace.current_route) < 2:
            self.output_text.insert(tk.END, "Una ruta debe tener al menos 2 puntos.\n")
            return
            
        self.airspace.save_current_route()
        self.output_text.insert(tk.END, "Ruta guardada.\n")
        self.update_routes_list()
        self.draw_airspace()

    def cancel_route(self):
        """Cancela la ruta actual sin guardar"""
        self.airspace.clear_current_route()
        self.output_text.insert(tk.END, "Ruta cancelada.\n")
        self.draw_airspace()

    def update_routes_list(self):
        """Actualiza la lista de rutas guardadas"""
        self.routes_listbox.delete(0, tk.END)
        for i, route in enumerate(self.airspace.routes, 1):
            names = [self.airspace.navpoints[num].name for num in route]
            self.routes_listbox.insert(tk.END, f"Ruta {i}: {' -> '.join(names)}")

    def show_selected_route(self):
        """Muestra la ruta seleccionada en el mapa"""
        selection = self.routes_listbox.curselection()
        if not selection:
            self.output_text.insert(tk.END, "Selecciona una ruta de la lista.\n")
            return
            
        route_index = selection[0]
        route = self.airspace.routes[route_index]
        route_points = [self.airspace.navpoints[num] for num in route]
        
        self.ax.clear()
        
        # Dibujar todos los segmentos en gris
        for seg in self.airspace.segments:
            o = self.airspace.navpoints.get(seg.OriginNumber)
            d = self.airspace.navpoints.get(seg.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], color='gray', linewidth=0.5)
        
        # Dibujar la ruta seleccionada en rojo
        for i in range(len(route_points) - 1):
            a, b = route_points[i], route_points[i+1]
            self.ax.plot([a.lon, b.lon], [a.lat, b.lat], color='red', linewidth=2)
        
        # Dibujar todos los puntos
        for point in self.airspace.navpoints.values():
            if point in route_points:
                self.ax.plot(point.lon, point.lat, 'ro')
            else:
                self.ax.plot(point.lon, point.lat, 'ko')
            self.ax.text(point.lon, point.lat, point.name, fontsize=8)
        
        self.ax.set_title(f"Ruta {route_index+1}")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()

    def delete_selected_route(self):
        """Elimina la ruta seleccionada"""
        selection = self.routes_listbox.curselection()
        if not selection:
            self.output_text.insert(tk.END, "Selecciona una ruta para eliminar.\n")
            return
            
        route_index = selection[0]
        self.airspace.routes.pop(route_index)
        self.output_text.insert(tk.END, f"Ruta {route_index+1} eliminada.\n")
        self.update_routes_list()
        self.draw_airspace()

    def draw_current_route(self):
        """Dibuja la ruta actual en construcción"""
        self.ax.clear()
        
        # Dibujar todos los segmentos en gris
        for seg in self.airspace.segments:
            o = self.airspace.navpoints.get(seg.OriginNumber)
            d = self.airspace.navpoints.get(seg.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], color='gray', linewidth=0.5)
        
        # Dibujar la ruta actual en azul
        route_points = self.airspace.get_route_points()
        for i in range(len(route_points) - 1):
            a, b = route_points[i], route_points[i+1]
            self.ax.plot([a.lon, b.lon], [a.lat, b.lat], color='blue', linewidth=2)
        
        # Dibujar todos los puntos
        for point in self.airspace.navpoints.values():
            if point in route_points:
                self.ax.plot(point.lon, point.lat, 'bo')
            else:
                self.ax.plot(point.lon, point.lat, 'ko')
            self.ax.text(point.lon, point.lat, point.name, fontsize=8)
        
        self.ax.set_title("Ruta en construcción")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()

    def export_kml(self, points, filename):
        with open(filename, 'w') as f:
            f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            f.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n<Document>\n")
            f.write("<name>Ruta Aérea</name>\n")

            for p in points:
                f.write(f"<Placemark><name>{p.name}</name>\n")
                f.write("<Point><coordinates>{},{},0</coordinates></Point>\n".format(p.lon, p.lat))
                f.write("</Placemark>\n")

            if len(points) >= 2:
                f.write("<Placemark><LineString><coordinates>\n")
                for p in points:
                    f.write(f"{p.lon},{p.lat},0\n")
                f.write("</coordinates></LineString></Placemark>\n")

            f.write("</Document></kml>")
        messagebox.showinfo("KML generado", f"KML guardado en:\n{filename}")

    def save_route_as_kml(self):
        selection = self.routes_listbox.curselection()
        if not selection:
            self.output_text.insert(tk.END, "Selecciona una ruta primero.\n")
            return
        route_index = selection[0]
        route = self.airspace.routes[route_index]
        points = [self.airspace.navpoints[num] for num in route]
        filename = filedialog.asksaveasfilename(defaultextension=".kml", filetypes=[("KML Files", "*.kml")])
        if filename:
            self.export_kml(points, filename)

    def open_kml_in_google_earth(self):
        filename = filedialog.askopenfilename(filetypes=[("KML Files", "*.kml")])
        if filename:
            try:
                webbrowser.open(filename)  # o usa os.startfile(filename) en Windows
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir Google Earth:\n{e}")

    def draw_path_on_map(self, path, origin_name, dest_name):
        self.ax.clear()
        
        # Dibujar todos los segmentos en gris claro
        for seg in self.airspace.segments:
            o = self.airspace.navpoints.get(seg.OriginNumber)
            d = self.airspace.navpoints.get(seg.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], 'gray', linewidth=0.5, alpha=0.5)
        
        # Dibujar el camino encontrado
        for i in range(len(path)-1):
            start, end = path[i], path[i+1]
            self.ax.plot([start.lon, end.lon], [start.lat, end.lat], 'red', linewidth=2)
        
        # Dibujar puntos especiales
        for i, point in enumerate(path):
            # Aeropuertos
            if (i == 0 and origin_name in self.airspace.airports) or \
            (i == len(path)-1 and dest_name in self.airspace.airports):
                self.ax.plot(point.lon, point.lat, 's', markersize=12, 
                            color='green' if i == 0 else 'blue')
                self.ax.text(point.lon, point.lat, point.name, 
                            fontsize=10, fontweight='bold',
                            ha='right' if i == 0 else 'left')
            # Puntos intermedios
            else:
                self.ax.plot(point.lon, point.lat, 'ro', markersize=6)
                self.ax.text(point.lon, point.lat, point.name, fontsize=8)
        
        self.ax.set_title(f"Ruta: {origin_name} → {dest_name}")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()
    
    def on_close(self):
        # Crear ventana de despedida
        top = tk.Toplevel(self.root)
        top.title("¡Adiós! 👋")
        
        # Configurar el cierre para ambas ventanas
        def close_all():
            try:
                top.destroy()
            except:
                pass
            try:
                self.root.destroy()
            except:
                pass
        
        top.protocol("WM_DELETE_WINDOW", close_all)
        self.root.protocol("WM_DELETE_WINDOW", close_all)
        
        # Mostrar el GIF
        lbl = tk.Label(top)
        lbl.pack()

        try:
            # Cargar el GIF
            gif_path = "airplane-dancing.gif"
            img = Image.open(gif_path)
            frames = []
            
            # Almacenar referencias a los frames
            for frame in ImageSequence.Iterator(img):
                frame_image = ImageTk.PhotoImage(frame.copy())
                frames.append(frame_image)
            
            def animate(index=0):
                try:
                    if not top.winfo_exists():  # Verificar si la ventana sigue abierta
                        return
                    lbl.config(image=frames[index])
                    lbl.image = frames[index]  # Mantener referencia
                    top.after(80, animate, (index + 1) % len(frames))
                except:
                    pass  # Ignorar errores si la ventana se cerró
            
            # Iniciar animación
            animate()
            
            # Cierre
            top.after(5000, close_all)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el GIF: {str(e)}")
            close_all()

    def animate_selected_route(self):
        selection = self.routes_listbox.curselection()
        if not selection:
            self.output_text.insert(tk.END, "Selecciona una ruta para animar.\n")
            return

        route_data = self.airspace.routes[selection[0]]
        route = route_data[0] if isinstance(route_data, tuple) else route_data
        points = [self.airspace.navpoints[num] for num in route]

        self.animating = True
        self.paused = False
        self.animation_data = (points, 0, 0)
        self.animate_plane(*self.animation_data)

    def animate_plane(self, points, i, step):
        if not self.animating or self.paused:
            self.animation_data = (points, i, step)
            return

        if i >= len(points) - 1:
            self.animating = False
            return

        a = points[i]
        b = points[i + 1]
        t = step / 10
        lat = a.lat + (b.lat - a.lat) * t
        lon = a.lon + (b.lon - a.lon) * t

        self.ax.clear()
        for seg in self.airspace.segments:
            o = self.airspace.navpoints.get(seg.OriginNumber)
            d = self.airspace.navpoints.get(seg.DestinationNumber)
            if o and d:
                self.ax.plot([o.lon, d.lon], [o.lat, d.lat], color='lightgray', linewidth=0.5)
        for j in range(len(points) - 1):
            self.ax.plot([points[j].lon, points[j+1].lon], [points[j].lat, points[j+1].lat], 'red', linewidth=2)
        for p in points:
            self.ax.plot(p.lon, p.lat, 'ro')
            self.ax.text(p.lon, p.lat, p.name, fontsize=8)

        self.ax.text(lon, lat, "✈", fontsize=14, ha='center', va='center')
        self.ax.set_title("Reproduciendo Ruta")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()

        if step < 10:
            self.root.after(5, lambda: self.animate_plane(points, i, step + 1))
        else:
            self.root.after(10, lambda: self.animate_plane(points, i + 1, 0))

    def pause_animation(self):
        self.paused = True

    def resume_animation(self):
        if self.animation_data and self.paused:
            self.paused = False
            self.animate_plane(*self.animation_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = AirSpaceApp(root)
    root.mainloop()