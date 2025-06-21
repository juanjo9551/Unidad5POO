import pandas as pd
from models import db
from models import Producto
# Asegúrate de que el modelo Producto esté definido correctamente en models.py
# y que la base de datos esté configurada correctamente.
from app import app


def cargar_productos():
    # Cargar el archivo Excel
    df = pd.read_excel('/data/productos.xlsx')
    #cargar desde la fila numero 10
    df = df.iloc[9:]  # Ignorar las primeras 9 filas
    # Renombrar las columnas
    df.columns = ['codigo', 'descripcion', 'precio']
    # Convertir el DataFrame a una lista de diccionarios
    productos = df.to_dict(orient='records')
    # Crear instancias de Producto y agregar a la sesión
    for producto_data in productos:
        producto = Producto(
            codigo=producto_data['codigo'],
            descripcion=producto_data['descripcion'],
            precio=producto_data['precio']
        )
        db.session.add(producto)
    # Confirmar los cambios en la base de datos
    db.session.commit()
if __name__ == "__main__":
    cargar_productos()
    print("Productos cargados exitosamente.")
# Nota: Asegúrate de que el archivo 'productos.xlsx' esté en el mismo directorio que este script.
# Si el archivo tiene un nombre diferente o está en otra ubicación, actualiza la ruta en
# pd.read_excel('productos.xlsx') en consecuencia.
# También asegúrate de que la base de datos esté configurada correctamente y que el modelo