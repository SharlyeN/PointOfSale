from flask import Flask
import mysql.connector

app = Flask(__name__)

# Configura la conexión a la base de datos
conn = mysql.connector.connect(
    host='localhost',      # Cambia a la dirección de tu servidor MySQL
    user='root',     # Cambia a tu nombre de usuario
    password='291223',   # Cambia a tu contraseña
    database='axol_papeleria'   # Cambia al nombre de tu base de datos
)

@app.route('/insert_products')
def insert_products():
    try:
        # Crear un cursor
        cursor = conn.cursor()

        # Insertar productos en la tabla
        productos = [
            ('12345', 'Libreta', 5.99, 100),
            ('67890', 'Lápiz', 0.99, 500),
            ('54321', 'Tijeras', 2.49, 200)
        ]

        for producto in productos:
            query = "INSERT INTO products (Barcode, Name_product, Price, Units_quantity) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, producto)
        
        # Confirmar la transacción y cerrar el cursor
        conn.commit()
        cursor.close()

        return "Productos insertados con éxito."
    except Exception as e:
        return f"Error al insertar productos: {str(e)}"
    finally:
        # Cerrar la conexión a la base de datos
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
