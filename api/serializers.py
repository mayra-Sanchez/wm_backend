from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Producto, Categoria
from django.core.exceptions import ValidationError

Usuario = get_user_model()

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']
        
# Serializer para el modelo Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
    
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


