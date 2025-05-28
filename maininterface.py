import tkinter as tk
from interface import GraphApp
from interfaceAirspace import AirSpaceApp

def graph_interface():
    selector.destroy()
    root = tk.Tk()
    GraphApp(root)
    root.mainloop()

def airspace_interface():
    selector.destroy()
    root = tk.Tk()
    AirSpaceApp(root)
    root.mainloop()

selector = tk.Tk()
selector.title("Selecciona una interfaz")
selector.geometry("300x200")

# Título
tk.Label(selector, text="¿Qué quieres visualizar?", font=("Arial", 12, "bold")).pack(pady=20)

# Botones con un poco de estilo y espacio
tk.Button(selector, text="Visualizar nodos", width=30, pady=5, command=graph_interface).pack(pady=10)
tk.Button(selector, text="Visualizar espacio aéreo real", width=30, pady=5, command=airspace_interface).pack(pady=10)

selector.mainloop()
