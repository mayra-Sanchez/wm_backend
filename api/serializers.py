from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Producto, Categoria, Carrito, ProductoEnCarrito
from django.core.exceptions import ValidationError
from django.conf import settings

Usuario = get_user_model()

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']
        
# Serializer para el modelo Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'imagen', 'stock']# Asegura incluir 'id'

    
    def create(self, validated_data):
        imagen = validated_data.pop('imagen', None)  # Esto garantiza que no se pase 'imagen' a create().
        producto = Producto.objects.create(**validated_data)  # Crear el producto sin 'imagen'
        
        if imagen:
            # Aquí deberías manejar la lógica para guardar la imagen
            producto.imagen = imagen
            producto.save()

        return producto
    
    def validate_imagen(self, value):
        # Verifica si el archivo es una imagen
        if not value.name.endswith(('.png', '.jpg', '.jpeg')):
            raise ValidationError('Solo se permiten imágenes PNG, JPG o JPEG.')
        return value
    
    def get_imagen(self, obj):
        if obj.imagen:
            return settings.MEDIA_URL + str(obj.imagen)
        return None



# Serializer para crear usuarios (con campos básicos)
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email', 'password']

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# Serializer para registrar nuevos usuarios con más campos
class RegistroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email', 'password', 'username', 'rol', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Asignar el rol (default 'client')
        user.rol = validated_data.get('rol', Usuario.CLIENTE)  # Usar constante de rol
        user.save()
        return user

class ProductoEnCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()  # Serializamos la relación de Producto

    class Meta:
        model = ProductoEnCarrito
        fields = ['producto', 'cantidad']

# class CarritoSerializer(serializers.ModelSerializer):
#     productos_en_carrito = ProductoEnCarritoSerializer(source='productosen_carrito', many=True)  # Usamos el serializer de ProductoEnCarrito

#     class Meta:
#         model = Carrito
#         fields = ['id', 'productos_en_carrito']

class CarritoSerializer(serializers.ModelSerializer):
    productos_en_carrito = ProductoEnCarritoSerializer(many=True)  # Asegúrate de que se serialicen los productos en carrito

    class Meta:
        model = Carrito
        fields = ['usuario', 'productos_en_carrito']
