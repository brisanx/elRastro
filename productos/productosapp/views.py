from productosapp.serializers import  ProductoSerializer

import pymongo

from datetime import datetime
from dateutil import parser

from bson import ObjectId
from rest_framework.response import Response

from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status

from pymongo import ReturnDocument

from django.shortcuts import render, get_object_or_404

# ----------------------------------------  VISTAS DE LA APLICACIÓN ------------------------------
# Conexión a la base de datos MongoDB
my_client = pymongo.MongoClient('mongodb+srv://usuario:usuario@elrastrodb.oqjmaaw.mongodb.net/')

# Nombre de la base de datos
dbname = my_client['ElRastro']

# Colecciones
collection_productos = dbname["productos"]

# -------------------------------------  VISTAS DE PRODUCTO ----------------------------------------
# Lista con todos los productos
@api_view(['GET'])
def productos_list_view(request):
    if request.method == 'GET':
        productos = list(collection_productos.find({}))
        
        # Transformar los objectid en strings
        for p in productos:
            p['_id'] = str(ObjectId(p.get('_id',[])))
            p['vendedor'] = str(ObjectId(p.get('vendedor',[])))
            p['pujas'] = [str(ObjectId(puja)) for puja in p.get('pujas',[])]
        
        productos_serializer = ProductoSerializer(data=productos, many= True)
        if productos_serializer.is_valid():
            json_data = productos_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(productos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Detalles de un producto
@api_view(['GET'])
def productos_detail_view(request, idProducto):
    if request.method == 'GET':
        producto = collection_productos.find_one(ObjectId(idProducto))
        
        # Transformar los objectid en strings
        producto['_id'] = str(ObjectId(producto.get('_id',[])))
        producto['vendedor'] = str(ObjectId(producto.get('vendedor',[])))
        producto['pujas'] = [str(ObjectId(puja)) for puja in producto.get('pujas',[])]
            
        producto_serializer = ProductoSerializer(data=producto, many = False) 
        if producto_serializer.is_valid():
            json_data = producto_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Crear un producto
@api_view(['POST'])
def productos_create_view(request):
    if request.method == 'POST':        
        data = request.data   
        
        fecha = datetime.now()

        nombre = data.get("Nombre")
        descripcion = data.get("descripcion")
        fotoURL = data.get("fotoURL")
        precio = data.get("precio")
        tags = data.get("tags")
        ubicacion = data.get("ubicacion")
        vendedor = data.get("vendedor")
        cierre = data.get("cierre")
        
        producto = {
            "_id" : ObjectId(),
            "Nombre" : nombre,
            "descripcion" : descripcion,
            "fecha" : fecha,
            "fotoURL" : fotoURL,
            "precio" : float(precio),
            "tags" : tags,
            "ubicacion" : ubicacion,
            "vendedor" : ObjectId(vendedor),
            "cierre" : parser.parse(cierre),
            "pujas" : []
        }
        
        result = collection_productos.insert_one(producto)
        if result.acknowledged:
            return Response({"message" : "Producto creado con éxito."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Algo salió mal. Producto no creado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Borrar un producto
@api_view(['DELETE'])
def delete_producto_view(request, idProducto):
    if request.method == 'DELETE':
        result = collection_productos.delete_one({'_id': ObjectId(idProducto)})
        if result.deleted_count == 1:
            return Response({"message": "Producto eliminado con éxito."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

# Actualizar un producto
@api_view(['PUT'])
def update_producto_view(request, idProducto):
    if request.method == 'PUT':
        data = request.data
                
        nombre = data.get("Nombre")
        descripcion = data.get("descripcion")
        fotoURL = data.get("fotoURL")
        precio = data.get("precio")
        tags = data.get("tags")
        ubicacion = data.get("ubicacion")
        cierre = data.get("cierre")
        
        result = collection_productos.update_one(
            {'_id': ObjectId(idProducto)},
            {'$set':{
                "Nombre" : nombre,
                "descripcion" : descripcion,
                "fotoURL" : fotoURL,
                "precio" : precio,
                "tags" : tags,
                "ubicacion" : ubicacion,
                "cierre" : cierre,}
            })
        if result.acknowledged:
            return Response({"message": "Producto actualizado."}, status=status.HTTP_200_OK)
        else:
            # Failed to create the document
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)


# Devuelve los productos de un determinado usuario y cuya fecha de cierre sea anterior a la actual
@api_view(['GET'])
def productos_usuario_anterior_view(request, idUsuario):
    if request.method == 'GET':
        productos = list(collection_productos.find({"vendedor": ObjectId(idUsuario), 
                                                    "cierre": {"$lt": datetime.now()}}))
        
        for p in productos:
            p['_id'] = str(ObjectId(p.get('_id',[])))
            p['vendedor'] = str(ObjectId(p.get('vendedor',[])))
            p['pujas'] = [str(ObjectId(puja)) for puja in p.get('pujas',[])]
        
        productos_serializer = ProductoSerializer(data=productos, many= True)
        if productos_serializer.is_valid():
            json_data = productos_serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(productos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Buscar productos cuyo precio sea menor o igual de un número dado.
@api_view(['GET'])
def productos_menor_precio_view(request, precio):
    if request.method == 'GET':
        productos = list(collection_productos.find({'precio': {'$lte': float(precio)}}))
        for producto in productos:
            producto['_id'] = str(ObjectId(producto.get('_id',[])))
            producto['vendedor'] = str(ObjectId(producto.get('vendedor',[])))
            producto['pujas'] = [str(ObjectId(puja)) for puja in producto.get('pujas',[])]
        
        producto_serializer = ProductoSerializer(data=productos, many=True)
        if producto_serializer.is_valid():
            json_data = producto_serializer.data 
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)