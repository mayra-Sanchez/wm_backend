from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import RegistroUsuarioView, ProductoViewSet, LogoutView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import  TokenRefreshView
from . import views
from .views import CustomTokenObtainPairView, ver_carrito, eliminar_del_carrito, CategoriaListView,EnviarCarritoView, UsuarioViewSet,CategoriaViewSet, UsuarioDetalleView

router = DefaultRouter()
router.register('productos', ProductoViewSet)
router.register('categorias', CategoriaViewSet)
router.register('usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Rutas para productos
    path('', include(router.urls)),

    # Rutas para autenticación JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Ruta para registro de usuarios
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('categorias/', CategoriaListView.as_view(), name='categoria-list'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('usuarios/<int:pk>/', UsuarioDetalleView.as_view(), name='usuario-detalle'),  # Obtener un usuario específico
    path('usuario_detalle/', UsuarioDetalleView.as_view(), name='usuario-detalle'),
    path('enviar-carrito/', EnviarCarritoView.as_view(), name='enviar_carrito'),
    path('agregar_al_carrito/<int:product_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver-carrito/', ver_carrito, name='ver_carrito'),
    path('eliminar-del-carrito/<int:producto_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
