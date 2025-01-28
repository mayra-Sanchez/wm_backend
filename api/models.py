from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.text import slugify
from django.conf import settings

# Modelo Categoría
class Categoria(models.Model):
    CATEGORIA_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('accesorio', 'Accesorio')
    ]
    
    nombre = models.CharField(max_length=255, choices=CATEGORIA_CHOICES)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

# Modelo Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=3)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', null=False, default='productos/default.jpg')
    slug = models.SlugField(unique=True, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email debe ser proporcionado")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser):
    # Opciones para el campo 'rol'
    CLIENTE = 'client'
    ADMINISTRADOR = 'admin'
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=[('client', 'Cliente'), ('admin', 'Administrador')],
        default='client'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
    
class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    productos = models.ManyToManyField('Producto', through='ProductoEnCarrito')


    def __str__(self):
        return f"Carrito de {self.usuario.email} - {self.fecha_creacion}"

class ProductoEnCarrito(models.Model):
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
    
    def total_precio(self):
        return self.cantidad * self.producto.precio
