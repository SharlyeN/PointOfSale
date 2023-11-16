from conexion_bd import conectar_bd

#Conexión con la base de datos
conn = conectar_bd()
cursor = conn.cursor()

def select_product():
    term = '12345' # Obtener el término de búsqueda desde la solicitud GET
    cursor.execute("SELECT Barcode FROM products WHERE Barcode LIKE %s", ('%' + term + '%',))
    return