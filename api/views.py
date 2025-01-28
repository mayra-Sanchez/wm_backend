from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from .models import ProductoEnCarrito, Producto, Carrito, Usuario, Categoria
from .serializers import ProductoSerializer, RegistroUsuarioSerializer, CategoriaSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.http import JsonResponse
from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


Usuario = get_user_model()

# Vista para agregar al carrito
@api_view(['POST'])
def agregar_al_carrito(request, product_id):
    try:
        # Obtener el producto
        producto = Producto.objects.get(id=product_id)
        
        # Obtener o crear el carrito del usuario
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        # Agregar el producto al carrito
        ProductoEnCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=1
        )
        
        return Response({"message": "Producto agregado al carrito"}, status=status.HTTP_201_CREATED)

    except Producto.DoesNotExist:
        return Response({"message": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@login_required
def ver_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if carrito:
        productos = carrito.productos.all()
        total = sum([producto.total_precio() for producto in productos])
        return render(request, 'carrito.html', {'productos': productos, 'total': total})
    return render(request, 'carrito.html', {'productos': [], 'total': 0})

# Vista para eliminar un producto del carrito
@login_required
def eliminar_del_carrito(request, producto_id):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if carrito:
        producto_en_carrito = carrito.productos.filter(id=producto_id).first()
        if producto_en_carrito:
            carrito.productos.remove(producto_en_carrito)
            return JsonResponse({'message': 'Producto eliminado del carrito'}, status=status.HTTP_200_OK)
    return JsonResponse({'error': 'Producto no encontrado en el carrito'}, status=status.HTTP_404_NOT_FOUND)

# Vista para obtener los tokens del usuario
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    access['id'] = user.id  # Add the user ID to the token
    return str(access), str(refresh)

# Vista para agregar al carrito (usando APIView)
class AgregarAlCarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            user = request.user
            product = get_object_or_404(Producto, id=product_id)  # Get the product by ID

            if product.stock <= 0:
                return Response({'message': 'Producto fuera de stock'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the product is already in the user's cart
            cart_item, created = Carrito.objects.get_or_create(user=user, product=product)

            if not created:
                # Increment quantity if the item is already in the cart
                cart_item.quantity += 1
                cart_item.save()

            return Response({'message': 'Producto agregado al carrito'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'message': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Error al agregar al carrito: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UsuarioDetalleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = RegistroUsuarioSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Vista para obtener todos los usuarios (solo admin)
class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = RegistroUsuarioSerializer

    def list(self, request, *args, **kwargs):
        usuarios = self.get_queryset()
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data)

# Vista personalizada para obtener el token de acceso (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Correo electrónico no encontrado')

        if not user.check_password(password):
            raise AuthenticationFailed('Contraseña incorrecta')

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        refresh['rol'] = user.rol
        access_token['rol'] = user.rol
        refresh['username'] = user.username
        access_token['username'] = user.username

        response_data = {
            'access': str(access_token),
            'refresh': str(refresh),
            'rol': user.rol,
            'username': user.username
        }

        return Response(response_data)

# Vista para obtener y crear categorías
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

# Vista para obtener lista de categorías
class CategoriaListView(APIView):
    def get(self, request):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

# Permiso personalizado para verificar si el usuario es admin
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.rol == 'admin':
            return True
        return False

# Vista para productos (CRUD)
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria', None)
        if categoria_id:
            queryset = queryset.filter(categoria__id=categoria_id)
        return queryset

    def perform_create(self, serializer):
        categoria_id = self.request.data.get('categoria')
        try:
            categoria = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            raise NotFound('La categoría seleccionada no existe.')

        serializer.save(categoria=categoria)

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsAdmin()]
        return [permissions.AllowAny()]

# Vista para registrar usuario
class RegistroUsuarioView(APIView):
    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Vista para logout
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Token de refresco es requerido"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Token inválido o ya expirado"}, status=status.HTTP_400_BAD_REQUEST)

# Vista para enviar carrito por WhatsApp
class EnviarCarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carrito = Carrito.objects.filter(usuario=request.user).first()
        if not carrito:
            return JsonResponse({"error": "No tienes productos en tu carrito."}, status=status.HTTP_400_BAD_REQUEST)

        productos = carrito.productos.all()
        mensaje = f"Carrito de compras de {request.user.username}:\n"
        
        total = 0
        for producto in productos:
            mensaje += f"- {producto.nombre} x {producto.cantidad} = ${producto.total_precio()}\n"
            total += producto.total_precio()

        mensaje += f"Total: ${total}\n"
        mensaje += "Confirma tu compra por favor."

        telefono_empresa = "3026929375"
        url_whatsapp = f"https://wa.me/{telefono_empresa}?text={quote(mensaje)}"

        return JsonResponse({"whatsapp_url": url_whatsapp})
