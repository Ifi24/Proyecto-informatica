import tkinter as tk
from tkinter import filedialog, messagebox
from graph import Graph
from test_graph import CreateGraph_1
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from node import Node

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rutas de vuelo")

        self.graph = None
        self.figure, self.ax = plt.subplots()

        # Marco derecho para los botones
        left_frame = tk.Frame(root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="Botones", font=("Arial", 10, "bold")).pack()

        tk.Button(left_frame, text="Mostrar ejemplo", width=20, command=self.show_example_graph).pack(pady=10)
        tk.Button(left_frame, text="Mostrar nuestro", width=20, command=self.show_invented_graph).pack(pady=10)
        tk.Button(left_frame, text="Cargar desde archivo", width=20, command=self.load_graph_file).pack(pady=10)

        self.output_text = tk.Text(left_frame, height=8, width=30)
        self.output_text.pack(pady=5)

        tk.Label(left_frame, text="--- Editar gráfico ---", font=("Arial", 10, "bold")).pack(pady=5)

        # Ver vecinos
        self.node_entry = tk.Entry(self.root)
        self.node_entry.pack(pady=5)

        self.neighbor_button = tk.Button(self.root, text="Mostrar vecinos", command=self.show_neighbors)
        self.neighbor_button.pack(pady=5)

        self.neighbor_label = tk.Label(self.root, text="")
        self.neighbor_label.pack(pady=5)

        # Añadir nodo
        self.node_name_entry = tk.Entry(left_frame)
        self.node_name_entry.pack()
        self.node_name_entry.insert(0, "Nombre del nodo")

        self.node_x_entry = tk.Entry(left_frame)
        self.node_x_entry.pack()
        self.node_x_entry.insert(0, "Coordenada X")

        self.node_y_entry = tk.Entry(left_frame)
        self.node_y_entry.pack()
        self.node_y_entry.insert(0, "Coordenada Y")

        tk.Button(left_frame, text="Añadir nodo", command=self.add_node).pack(pady=5)

        # Añadir segmento
        self.segment_origin_entry = tk.Entry(left_frame)
        self.segment_origin_entry.pack()
        self.segment_origin_entry.insert(0, "Nodo origen")

        self.segment_dest_entry = tk.Entry(left_frame)
        self.segment_dest_entry.pack()
        self.segment_dest_entry.insert(0, "Nodo destino")

        tk.Button(left_frame, text="Añadir segmento", command=self.add_segment).pack(pady=5)

        # Eliminar nodo
        self.delete_node_entry = tk.Entry(left_frame)
        self.delete_node_entry.pack()
        self.delete_node_entry.insert(0, "Nodo a eliminar")

        tk.Button(left_frame, text="Eliminar nodo", command=self.delete_node).pack(pady=5)

        # Crear nuevo grafico y guardar
        tk.Button(left_frame, text="Nuevo gráfico", command=self.new_graph).pack(pady=5)
        tk.Button(left_frame, text="Guardar gráfico", command=self.save_graph).pack(pady=5)

        # Marco derecho
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_graph(self): # dibuja el gráfico
        if not self.graph:
            return

        self.ax.clear()
        for segment in self.graph.segments: # dibuja un segmento
            x = [segment.origin.x, segment.destination.x]
            y = [segment.origin.y, segment.destination.y]
            self.ax.plot(x, y, marker="o")
            self.ax.text(segment.origin.x, segment.origin.y, segment.origin.name, fontsize=8)
            self.ax.text(segment.destination.x, segment.destination.y, segment.destination.name, fontsize=8)

        for node in self.graph.nodes: # dibuja un nodo
            self.ax.plot(node.x, node.y, 'o')  # punto simple
            self.ax.text(node.x, node.y, node.name, fontsize=8)

        self.ax.set_title("Visualización del gráfico")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.canvas.draw()

    def show_example_graph(self): # muestra el gráfico de ejemplo del paso 3
        self.graph = CreateGraph_1()
        self.output_text.insert(tk.END, "Ejemplo cargado.\n")
        self.draw_graph()

    def show_invented_graph(self): # muestra un gráfico nuestro inventado, guardado en el archivo filename.txt
        self.graph = Graph()
        if self.graph.LoadFromFile("filename.txt"):
            self.output_text.insert(tk.END, "Gráfico inventado cargado desde 'filename.txt'\n")
            self.draw_graph()
        else:
            messagebox.showerror("Error", "No se pudo cargar 'filename.txt'.")

    def load_graph_file(self): # carga el archivo .txt del ordenador
        file_path = filedialog.askopenfilename(title="Seleccionar archivo de gráfico", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.graph = Graph()
            if self.graph.LoadFromFile(file_path):
                self.output_text.insert(tk.END, f"Gráfico cargado desde {file_path}\n")
                self.draw_graph()
            else:
                messagebox.showerror("Error", "No se pudo cargar el archivo.")

    def show_neighbors(self): # muestra los nodos vecinos
        if not self.graph:
            messagebox.showwarning("Advertencia", "Carga un gráfico primero.")
            return
        
        node_name = self.node_entry.get().strip()
        node = self.graph.GetNodeByName(node_name)

        if node:
            neighbors = [n.name for n in node.neighbors]
            output = f"Vecinos de {node_name}: {', '.join(neighbors)}\n"
            self.output_text.insert(tk.END, output)
            # llama a PlotNode para mostrar el gráfico de los vecinos en una ventana nueva
            self.graph.PlotNode(node_name)
        else:
            messagebox.showinfo("No encontrado", f"No se encontró el nodo '{node_name}'.")
    
    def add_node(self): # añade los nuevos nodos al gráfico y al archivo .txt
        if not self.graph:
            self.graph = Graph()
        name = self.node_name_entry.get().strip()

        try:
            x = float(self.node_x_entry.get())
            y = float(self.node_y_entry.get())
            node = Node(name, x, y)
            self.graph.AddNode(node)
            self.output_text.insert(tk.END, f"Nodo '{name}' añadido.\n")
            self.draw_graph()

        except ValueError:
            messagebox.showerror("Error", "Coordenadas inválidas.")
    
    def add_segment(self): # añade los nuevos segmentos al gráfico y al archivo .txt
        if not self.graph:
            return

        origin_name = self.segment_origin_entry.get().strip()
        dest_name = self.segment_dest_entry.get().strip()

        origin = self.graph.GetNodeByName(origin_name)
        dest = self.graph.GetNodeByName(dest_name)

        if origin and dest:
            segment_name = f"{origin_name}_{dest_name}"
            self.graph.AddSegment(segment_name, origin.name, dest.name)
            self.output_text.insert(tk.END, f"Segmento '{segment_name}' añadido.\n")
            self.draw_graph()
            print("Current segments:")

            for seg in self.graph.segments:
                print(f"{seg.name}: {seg.origin.name} -> {seg.destination.name}")
        
        else:
            messagebox.showerror("Error", "Nodo origen o destino no encontrado.")

    def delete_node(self): # elimina el nodo seleccionado
        if not self.graph:
            return

        node_name = self.delete_node_entry.get().strip()
        node = self.graph.GetNodeByName(node_name)

        if node:
            # elimina los segmentos relacionados
            new_segments = []
            for s in self.graph.segments:
                if s.origin != node and s.destination != node:
                    new_segments.append(s)
            self.graph.segments = new_segments

            # elimina el nodo de los vecinos
            for n in self.graph.nodes:
                if node in n.neighbors:
                    n.neighbors.remove(node)

            # elimina el propio nodo
            self.graph.nodes.remove(node)
            self.output_text.insert(tk.END, f"Nodo '{node_name}' y segmentos eliminados.\n")
            self.draw_graph()
        else:
            messagebox.showinfo("No encontrado", f"No se encontró el nodo '{node_name}'.")
    
    def new_graph(self): # crea un nuevo gráfico
        self.graph = Graph()
        self.output_text.insert(tk.END, "Nuevo gráfico creado.\n")
        self.draw_graph()

    def save_graph(self): # guarda el gráfico editado o dibujado en formato .txt
        if not self.graph:
            messagebox.showwarning("Advertencia", "No hay gráfico para guardar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        
        # edita el archivo del gráfico de acuerdo al formato que queremos
        try:
            with open(file_path, "w") as f:
                f.write("#nodes\n")
                for node in self.graph.nodes:
                    f.write(f"{node.name},{node.x},{node.y}\n")
                f.write("\n#segments\n")
                for seg in self.graph.segments:
                    f.write(f"{seg.name},{seg.origin.name},{seg.destination.name}\n")

            self.output_text.insert(tk.END, f"Gráfico guardado en {file_path}\n")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")



# ejecuta la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
 