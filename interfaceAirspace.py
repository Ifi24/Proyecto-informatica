import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrow
from airSpace import Airspace
from path import Path
from tkinter import ttk
import os
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

#vecinos entrada
        tk.Label(scrollable_frame, text="Nombre del punto").pack()
        self.entry_point_number = tk.Entry(scrollable_frame)
        self.entry_point_number.pack(pady=2)

        tk.Button(scrollable_frame, text="Mostrar vecinos", command=self.show_neighbors).pack(pady=5)

# para camino
        tk.Label(scrollable_frame, text="Nombre del origen").pack()
        self.entry_origin = tk.Entry(scrollable_frame)
        self.entry_origin.pack(pady=2)

        tk.Label(scrollable_frame, text="Nombre del destino").pack()
        self.entry_dest = tk.Entry(scrollable_frame)
        self.entry_dest.pack(pady=2)

        tk.Button(scrollable_frame, text="Camino más corto", command=self.show_shortest_path).pack(pady=5)


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
            
        self.airspace.LoadNavAirports(path)
        self.output_text.insert(tk.END, "Aeropuertos cargados.\n")
        

        for airport in self.airspace.airports.values():
            if not airport.sid or not airport.star:
                self.output_text.insert(tk.END, f"- {airport.name} omitido (SID/STAR vacíos).\n")
                continue

            sid_point = self.airspace.navpoints.get(airport.sid.strip())
            star_point = self.airspace.navpoints.get(airport.star.strip())

            if not sid_point or not star_point:
                missing = ""
                if not sid_point:
                    missing += f"SID ({airport.sid})"
                if not star_point:
                    missing += f"SID ({airport.star})"
                self.output_text.insert(tk.END, f"- {airport.name} omitido (no encontrado: {', '.join(missing)})\n")                
                continue

            try:
                avg_lat = float(sid_point["lat"] + star_point["lat"]) / 2 
                avg_lon = float(sid_point["lon"] + star_point["lon"]) / 2
                self.ax.plot(avg_lon, avg_lat, 's', color='black', markersize=8)
                self.ax.text(avg_lon, avg_lat, airport.name, fontsize=9, fontweight='bold', ha='center', va='bottom')
                self.output_text.insert(tk.END, f"- {airport.name} añadido (Posición: {avg_lat:.4f}N, {avg_lon:.4f}E)\n")            
            except KeyError as e:
                self.output_text.insert(tk.END, f"- {airport.name} omitido (no se encontró {sid_point} o {star_point}).\n")

        self.canvas.draw()
        self.output_text.insert(tk.END, "Proceso completado.\n")
        print(f"{airport.name} -> SID: {airport.sid}, STAR: {airport.star}")


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
        for navpoint in self.airspace.navpoints.values():
            if navpoint.name == name:
                return navpoint
        return None
    
    def FindShortestPath(self, origin_name, dest_name):
        origin = self.GetNavPointByName(origin_name)
        destination = self.GetNavPointByName(dest_name)

        from collections import deque

        visited = set()
        queue = deque()
        queue.append((origin, [origin]))  # (actual, camino hasta ahora)

        while queue:
            current, path = queue.popleft()

            if current == destination:
                return path  # lista de NavPoints

            visited.add(current.number)

            for segment in self.airspace.segments:
                o = self.airspace.navpoints.get(segment.OriginNumber)
                d = self.airspace.navpoints.get(segment.DestinationNumber)

                neighbor = None
                if o == current and d.number not in visited:
                    neighbor = d
                elif d == current and o.number not in visited:
                    neighbor = o

                if neighbor:
                    queue.append((neighbor, path + [neighbor]))

        return None  # si no hay camino
        
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

    # Dibujar puntos
        for point in self.airspace.navpoints.values():
            if point in path:
                self.ax.plot(point.lon, point.lat, 'ro')
            else:
                self.ax.plot(point.lon, point.lat, marker='o', color='gray')
            self.ax.text(point.lon, point.lat, point.name, fontsize=8)

        self.ax.set_title("Camino más corto")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True)
        self.canvas.draw()

    
    def on_close(self):
        top = tk.Toplevel()
        top.title("adeu! 👋")
        
        lbl = tk.Label(top)
        lbl.pack()

        # Ruta al GIF animado
        gif_path = "airplane-dancing.gif"

        img = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(img)]

        def animate(index=0):
            lbl.config(image=frames[index])
            top.after(80, animate, (index + 1) % len(frames))

        animate()
        top.after(2000, self.root.destroy)


#extra1
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
            self.root.after(20, lambda: self.animate_plane(points, i, step + 1))
        else:
            self.root.after(20, lambda: self.animate_plane(points, i + 1, 0))


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