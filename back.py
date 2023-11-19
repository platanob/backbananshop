from flask import Flask, request , jsonify 
from werkzeug.security import generate_password_hash , check_password_hash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_login import LoginManager , login_user , logout_user , UserMixin, login_required, current_user
from flask_cors import CORS

global esadmin
global sesion
esadmin = False
sesion = False
uri = "mongodb+srv://benja:123@bananashop.tzmfwsy.mongodb.net/?retryWites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
app = Flask(__name__)
CORS(app, supports_credentials=True, methods=["GET", "POST", "PATCH", "DELETE"])
login_manager_app = LoginManager(app)
# Configura Flask-Login
app.secret_key = 'papaya'  
class user(UserMixin):
    def __init__(self,nombre,correo,telefono,rut,direccion,admin):
        self.id = correo
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.rut = rut 
        self.direccion = direccion
        self.admins = admin

def conbd():
    if client is None:
        return {'message': 'Error al conectar a la base de datos'}, 500
    
@app.route('/login', methods=['GET','POST'])
def login():
    global esadmin ,sesion
    if request.method == 'POST':
        correo = request.json.get("correo")
        contra = request.json.get("contra")
        usuario = client.bananashop.users.find_one({'correo' : correo})
        if usuario == None :
            return {'message' : 'ns'}
        if check_password_hash(usuario['contra'] , contra):
            us = user(nombre=usuario['nombre'],
                      correo=usuario['correo'],
                      telefono=usuario['telefono'],
                      rut=usuario['rut'],
                      direccion=usuario['direccion'],
                      admin=usuario['admin']
                      )
            login_user(us)
            sesion = True
            if us.admins == "si":
                esadmin = True
            if us.admins == "no":
                esadmin = False
            return {'message': 'si'}
        else : 
            return {'message': 'np'}

#para hacer vistas protegidas que se requiera le inicio de secion se ocupara @login_required


@app.route('/logout',methods=['GET'])
def logout():
    global esadmin ,sesion
    sesion = False
    esadmin = False
    return {'message': 'secion cerrada'}

@app.route('/registro', methods=['POST'])
def create_user():
    nombre = request.json.get("nombre")
    correo = request.json.get("correo")
    telefono = request.json.get("telefono")
    rut = request.json.get("rut")
    direccion = request.json.get("direccion")
    contra = request.json.get("contra")

    conbd()

    a = client.bananashop.users.find_one({'correo' : correo})
    if a :
        return {'message' : 'correo ya en uso'}

    if nombre and telefono and rut and direccion and correo and contra  :
        contra_hashed = generate_password_hash(contra)
        id = client.bananashop.users.insert_one(
            {'nombre': nombre,'correo' : correo ,'telefono': telefono, 'rut': rut, 'direccion': direccion, 'contra': contra_hashed ,'admin' : 'no'}
        )
        response = {
            'id': str(id),
            'nombre': nombre,
            'correo':correo,
            'telefono': telefono,
            'rut': rut,
            'direccion': direccion,
            'contra': contra,
            'admin' : 'no'
        }
        return {'message' : 'si'} 
    else:
        return not_found()
    
@app.errorhandler(404)
def not_found(erro=None):

    response = jsonify({
        'message':'Recurso no encontrado : ' + request.url,
        'status': 404
    })
    response.status_code = 404

    return response


@app.route('/newproduc' , methods=['POST'])
def crear_producto():
    nombre = request.json.get("nombre")
    genero = request.json.get("genero")
    categoria = request.json.get("categoria")
    talla  = request.json.get("talla")
    marca  = request.json.get("marca")
    costo  = request.json.get("costo")
    color = request.json.get("color")
    url = request.json.get("url")

    conbd()

    if nombre and genero and talla and categoria and marca and costo :
        id = client.bananashop.productos.insert_one(
            {'nombre': nombre,'genero': genero , 'talla' : talla , 'categoria': categoria , 'marca' : marca , 'costo' : int(costo), 'color' : color , 'url' : url}
        )
        response = {
            'id': str(id),
            'nombre': nombre,
            'genero': genero,
            'talla' : talla,
            'categoria' : categoria , 
            'marca' : marca , 
            'costo' : costo,


        }
        return response, 201  
    else:
        return not_found()
    

@app.route('/productos/nombre/<string:nombre>', methods=['GET'])
def obtener_productos_por_nombre(nombre):
    conbd() 
    productos = client.bananashop.productos.find({'nombre': nombre})
    productos_encontrados = []

    for producto in productos:
        producto_encontrado = {
            'nombre': producto['nombre'],
            'genero': producto['genero'],
            'talla': producto['talla'],
            'categoria': producto['categoria'],
            'marca': producto['marca'],
            'costo': producto['costo'],
            'color': producto['color'],
            'url' :producto['url']
        }
        productos_encontrados.append(producto_encontrado)

    return productos_encontrados, 201

@app.route('/productos/nombre/<string:nombre>', methods=['PATCH'])
def actualizar_producto(nombre):
    conbd()
    # Obtener los datos actualizados del producto desde la solicitud
    datos_actualizados = request.json

    # Actualizar el producto en la base de datos
    result = client.bananashop.productos.update_one({'nombre': nombre}, {'$set': datos_actualizados})

    if result.modified_count == 1:
        return {'message': 'Producto actualizado con éxito'}, 200
    else:
        return {'message': 'No se pudo actualizar el producto'}, 404

@app.route('/productos', methods=['GET'])
def obtener_todos_los_productos():
    conbd()  # Esto parece ser tu función de conexión a la base de datos
    
    productos = client.bananashop.productos.find({})
    
    # Inicializamos una lista para almacenar todos los productos
    todos_los_productos = []
    for producto in productos:
        # Creamos un diccionario para cada producto encontrado
        producto_encontrado = {
            'nombre': producto['nombre'],
            'genero': producto['genero'],
            'talla': producto['talla'],
            'color': producto['color'],
            'marca': producto['marca'],
            'costo': producto['costo'],
            'categoria' : producto['categoria'],
            'url' : producto['url']
            # Puedes agregar más campos aquí si es necesario
        }
        # Agregamos el producto al listado de todos los productos
        todos_los_productos.append(producto_encontrado)

    # Devolvemos la lista de todos los productos como respuesta
    return todos_los_productos, 200

@app.route('/productos/<string:nombre>', methods=['DELETE'])
def eliminar_producto(nombre):
    conbd()  
    # Eliminar producto con ID proporcionado
    result = client.bananashop.productos.delete_one({'nombre': nombre})

    if result.deleted_count == 1:
        return {'message': 'Producto eliminado con éxito'}, 200
    else:
        return {'message': 'No se pudo eliminar'}, 404   

@app.route('/usuariorol', methods=['GET'])
def crear_admin():
    if esadmin :
        return jsonify({'message' : 'si'}),200
    if sesion :
        return jsonify({'message' : 'siu'}),200
    else:
        return jsonify({'message': 'no'}), 200
if __name__ == '__main__':
    app.run(debug=True)
