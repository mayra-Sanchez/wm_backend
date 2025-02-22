from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.text import slugify
from django.conf import settings

# Modelo ProductoEnCarrito (debe ser definido antes de Carrito)
class ProductoEnCarrito(models.Model):
    id = models.AutoField(primary_key=True)
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE)  # Referencia al Carrito
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)  # Referencia al Producto
    cantidad = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('carrito', 'producto')

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"

    def total_precio(self):
        return self.producto.precio * self.cantidad

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
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=3)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', null=False, default='productos/default.jpg')
    slug = models.SlugField(unique=True, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=1)

    def total_precio(self):
        # Suponiendo que la cantidad es 1 por defecto
        return self.precio
    
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
        extra_fields.setdefault('is_active', True)  # Esto asegura que el superusuario esté activo
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser):
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
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    productos_en_carrito = models.ManyToManyField(Producto, through='ProductoEnCarrito')

    @property
    def total(self):
        return sum([producto.total_precio() for producto in self.productos_en_carrito.all()])

    def __str__(self):
        return f"Carrito de {self.usuario.email}"
    
class Compra(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    productos_lista = models.ManyToManyField(Producto, through='ProductoComprado')
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = sum([item.precio * item.cantidad for item in self.productos_comprados.all()])
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Compra {self.id} - {self.total} COP"

class ProductoComprado(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='productos_comprados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} x{self.cantidad}"
