import mysql.connector

# Establecer la conexión a la base de datos MySQL
def conectar_bd():
    # Establecer la conexión a la base de datos MySQL
    conn = mysql.connector.connect(
        host='localhost',     # Cambia a la dirección de tu servidor MySQL
        user='root',    # Cambia a tu nombre de usuario
        password='291223',  # Cambia a tu contraseña
        database='axol_papeleria'  # Cambia al nombre de tu base de datos
    )

    return conn