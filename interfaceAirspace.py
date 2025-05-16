import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrow
from airSpace import Airspace
from path import Path

class AirSpaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Espacio Aéreo")

        self.airspace = Airspace()
        self.figure, self.ax = plt.subplots()

        left_frame = tk.Frame(root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(left_frame, text="Cargar NavPoints", command=self.load_navpoints).pack(pady=5)
        tk.Button(left_frame, text="Cargar NavSegments", command=self.load_navsegments).pack(pady=5)
        tk.Button(left_frame, text="Cargar Airports", command=self.load_airports).pack(pady=5)

#vecinos entrada
        tk.Label(left_frame, text="Número de punto").pack()
        self.entry_point_number = tk.Entry(left_frame)
        self.entry_point_number.pack(pady=2)

        tk.Button(left_frame, text="Mostrar vecinos", command=self.show_neighbors).pack(pady=5)

# Entradas para camino
        tk.Label(left_frame, text="Nombre del origen").pack()
        self.entry_origin = tk.Entry(left_frame)
        self.entry_origin.pack(pady=2)

        tk.Label(left_frame, text="Nombre del destino").pack()
        self.entry_dest = tk.Entry(left_frame)
        self.entry_dest.pack(pady=2)

        tk.Button(left_frame, text="Camino más corto", command=self.show_shortest_path).pack(pady=5)


        self.output_text = tk.Text(left_frame, height=10, width=35)
        self.output_text.pack(pady=5)

        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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
        if path:
            self.airspace.LoadNavAirports(path)
            self.output_text.insert(tk.END, "Aeropuertos cargados.\n")

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
                color = 'o'   # gris sin color definido = negro por defecto
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

    


if __name__ == "__main__":
    root = tk.Tk()
    app = AirSpaceApp(root)
    root.mainloop()