from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from conexion_bd import conectar_bd


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'


#Conexión con la base de datos
conn = conectar_bd()
cursor = conn.cursor()

#=============================================
#               VERIFY SESSION
#=============================================

def notsession():
    if 'email' not in session:
        return redirect(url_for('index'))

def verifysession():
    error = notsession()
    if error:
        return error
#=============================================
#                 SING IN
#=============================================

@app.route('/')
def index():
    if 'email' in session:
        return 'Ya has iniciado sesión como ' + session['email'] + '. <a href="/">Cerrar sesión</a>'
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():  
    
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
    user = cursor.fetchone()

    if user:
        session['email'] = email
        return 'Inicio de sesión exitoso. <a href="/">Inicio</a>'
    else:
        return 'Credenciales incorrectas. <a href="/">Volver</a>'
    


#=============================================
#              POINT OF SALE
#=============================================

@app.route('/pointofsale')

def pointofsale():
    verifysession()
    
    return render_template('pointofsale2.html')



@app.route('/buscar_barcode', methods=['GET'])
def buscar_barcode():
    term = request.args.get('term')
    
    # Conectar al cursor dentro del bloque try-except
    try:
        cursor.execute("SELECT Barcode FROM products WHERE Barcode LIKE %s", (term + '%',))
        resultados = cursor.fetchall()

        # Formatear los resultados para que tengan la propiedad 'label'
        formatted_results = [{'label': item[0]} for item in resultados]

        return jsonify(formatted_results)
    except Exception as e:
        # Manejar la excepción (puedes imprimir un mensaje de error o hacer lo que consideres necesario)
        print(f"Error: {e}")
        return jsonify({'error': 'Ocurrió un error en la consulta'})
    finally:
        # Asegurarse de cerrar el cursor después de ejecutar la consulta
        if 'cursor' in locals() and cursor:
            cursor.close()

@app.route('/getall_frombarcode', methods=['GET'])
def getall_frombarcode():
    term = int(request.args.get('selectedItem'))

    try:
        with  conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM products WHERE Barcode = %s", (term,))
            resultados = cursor.fetchall()

        # Formatear los resultados para que tengan propiedades necesarias
        formatted_results = [
            {
                "Barcode": item['Barcode'],
                "name_product": item['name_product'],
                "cantidad_cajas": item['cantidad_cajas'],
                "precio_por_unidad": item['precio_por_unidad'],
                "precio_mayoreo": item['precio_mayoreo'],
                "tipo_de_producto": item['tipo_de_producto'],
                "marca": item['marca'],
                "unidades_por_caja": item['unidades_por_caja'],
                "cantidad_unidades": item['cantidad_unidades']
            }
            for item in resultados
        ]

        return jsonify(formatted_results)
    except Exception as e:
        error2 = f"Error Type: {type(e).__name__}"
        error = f"Error Details: {e}"
        print(f"Term: {term}")
        return jsonify({'error': f'Ocurrió un error en la consulta, {error2}: {error}, Term: {term}'})


    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()



                           


#=============================================
#              PROCESAR VENTA
#=============================================


@app.route('/calcular_total', methods=['POST'])
def calcular_total():
    try:
        # Obtener datos JSON de la solicitud
        datos_json = request.get_json()

        # Inicializar el total de la venta
        total_venta = 0

        # Iterar sobre los productos en los datos JSON
        for producto in datos_json:
            precio_por_unidad = float(producto['precio_por_unidad'])
            cantidad_unidades = int(producto['cantidad_unidades'])
            total_venta += precio_por_unidad * cantidad_unidades

        # Puedes devolver el total de la venta como respuesta
        return jsonify({'total_venta': total_venta}), 200
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir
        print("Error al procesar la venta:", str(e))
        return jsonify({'mensaje': 'Error en el servidor'}), 500


#=============================================
#         PROCESAR Y REGISTRAR VENTA
#=============================================


@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    try:
        # Obtener datos JSON de la solicitud
        datos_json = request.get_json()

        # Inicializar una lista para almacenar los valores a insertar en la tabla
        valores_insert = []

        # Iterar sobre los productos en los datos JSON
        for producto in datos_json:
            barcode = producto.get('barcode', '')
            name_product = producto.get('name_product', '')
            precio_por_unidad = float(producto.get('precio_por_unidad', 0))
            precio_mayoreo = float(producto.get('precio_mayoreo', 0))
            cantidad_unidades = int(producto.get('cantidad_unidades', 0))

            # Agregar los valores a la lista
            valores_insert.append((barcode, name_product, precio_por_unidad, precio_mayoreo, cantidad_unidades))


        # Query para insertar los datos en la tabla (ajusta la tabla y las columnas según tu esquema)
        query = "INSERT INTO sales (barcode, name_product, cantidad_cajas, precio_por_unidad, precio_mayoreo, cantidad_unidades) VALUES (%s, %s, %s, %s, %s, %s)"

        # Ejecutar la inserción
        cursor.executemany(query, valores_insert)

        # Hacer commit para efectuar los cambios en la base de datos
        conn.commit()

        # Cerrar el cursor
        cursor.close()

        return jsonify({'mensaje': 'Datos registrados correctamente en la base de datos'}), 200
    except Exception as e:
        print("Error al registrar la venta en la base de datos:", str(e))
        return jsonify({'mensaje': 'Error en el servidor'}), 500









#=============================================
#              ADD PRODUCTS
#=============================================

#insert products /modify DB
@app.route('/addproduct', methods=['GET', 'POST'])
def home():
    verifysession()
    
    if request.method == 'POST':
        barcode = request.form['barcode']
        name_product = request.form['name_product']
        cantidad_cajas = int(request.form['cantidad_cajas'])
        precio_por_unidad = float(request.form['precio_por_unidad'])
        precio_mayoreo = float(request.form['precio_mayoreo'])
        tipo_de_producto = request.form['tipo_de_producto']
        marca = request.form['marca']
        unidades_por_caja = int(request.form['unidades_por_caja'])
        cantidad_unidades = int(request.form['cantidad_unidades'])

        # Inserta los datos en la base de datos
        insert_query = "INSERT INTO products (barcode, name_product, cantidad_cajas, precio_por_unidad, precio_mayoreo, tipo_de_producto, marca, unidades_por_caja, cantidad_unidades) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (barcode, name_product, cantidad_cajas, precio_por_unidad, precio_mayoreo, tipo_de_producto, marca, unidades_por_caja, cantidad_unidades)
        cursor.execute(insert_query, data)
        conn.commit()
        cursor.close()

    return render_template('insert_product.html')

if __name__ == '__main__':
    app.run(debug=True)



