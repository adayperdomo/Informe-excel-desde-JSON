#Importación de librerías
import requests                    
import tkinter as tk               
from tkinter import ttk           
from tkinter import messagebox     
from tkinter import filedialog     

# ReportLab se usa para generar el PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

# Endpoint de la API
# URL desde donde obtenemos los productos
API_URL = "https://dummyjson.com/products"


class App(tk.Tk):
    """
    Clase principal de la aplicación.
    Hereda de tk.Tk para crear la ventana principal.
    """
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.title("DummyJSON Viewer")
        self.geometry("800x500")

        # Almacena todos los datos obtenidos de la API
        self.data = []
        # Almacena los datos luego de aplicar filtros
        self.filtered = []

    
        # Construcción de la Interfaz (UI)

        # Frame superior (controles)
        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=5)

        # Etiqueta y campo de texto para filtrar por categoría
        tk.Label(top, text="Filtro por categoría:").pack(side="left")
        self.category_var = tk.StringVar()
        self.category_entry = tk.Entry(top, textvariable=self.category_var)
        self.category_entry.pack(side="left", padx=5)

        # Botones de acción
        tk.Button(top, text="Cargar datos", command=self.load_data).pack(side="left", padx=5)
        tk.Button(top, text="Filtrar", command=self.apply_filter).pack(side="left", padx=5)
        tk.Button(top, text="Generar PDF", command=self.generate_pdf).pack(side="left", padx=5)

    
        # Tabla para mostrar los datos
    
        # Definición de columnas
        columns = ("id", "title", "category", "price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        # Configuración de encabezados y ancho
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(expand=True, fill="both", padx=10, pady=10)


    # Consumo de la API (HTTP GET)
    def load_data(self):
        """
        Realiza una petición HTTP GET a la API
        y carga los datos en la tabla.
        """
        try:
            # Petición HTTP
            response = requests.get(API_URL)

            # Lanza una excepción si hay error HTTP
            response.raise_for_status()

            # Extraemos la lista de productos del JSON
            self.data = response.json().get("products", [])

            # Inicialmente no hay filtro aplicado
            self.filtered = self.data

            # Actualizamos la tabla
            self.refresh_table()

        except Exception as e:
            # Muestra error si la API falla
            messagebox.showerror("Error", str(e))


    # Filtrado de datos
    def apply_filter(self):
        """
        Filtra los productos según la categoría ingresada.
        """
        category = self.category_var.get().lower()

        # Si no se escribe nada, se muestran todos los datos
        if not category:
            self.filtered = self.data
        else:
            # Filtrado por coincidencia de texto
            self.filtered = [
                p for p in self.data
                if category in p["category"].lower()
            ]

        # Refresca la tabla con los datos filtrados
        self.refresh_table()

    def refresh_table(self):
        """
        Limpia y vuelve a cargar la tabla con los datos actuales.
        """
        # Eliminar filas existentes
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar nuevas filas
        for p in self.filtered:
            self.tree.insert(
                "",
                "end",
                values=(p["id"], p["title"], p["category"], p["price"])
            )


    # Generación del PDF
    def generate_pdf(self):
        """
        Genera un informe PDF con los datos filtrados.
        """
        if not self.filtered:
            messagebox.showwarning("Aviso", "No hay datos para exportar")
            return

        # Diálogo para elegir dónde guardar el PDF
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )

        if not path:
            return

        # Crear documento PDF
        doc = SimpleDocTemplate(path)
        styles = getSampleStyleSheet()

        # Contenido del PDF
        elements = []
        elements.append(Paragraph("Informe de Productos Filtrados", styles["Title"]))

        # Datos de la tabla
        table_data = [["ID", "Título", "Categoría", "Precio"]]
        for p in self.filtered:
            table_data.append([
                p["id"],
                p["title"],
                p["category"],
                p["price"],
            ])

        elements.append(Table(table_data))

        # Construir PDF
        doc.build(elements)

        messagebox.showinfo("OK", "PDF generado correctamente")


# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = App()
    app.mainloop()
