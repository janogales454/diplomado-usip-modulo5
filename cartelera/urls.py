
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'generos', views.GeneroViewSet)
router.register(r'peliculas', views.PeliculaViewSet)
router.register(r'salas', views.SalaViewSet)
router.register(r'funciones', views.FuncionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('funciones/ver_disponibles', views.lista_funciones_disponibles, name='lista_funciones_disponibles'),
    path('funciones/actualizar_funciones', views.actualizar_funciones_disponibles, name='actualizar_funciones_disponibles'),
    path('venta/compra_boleto', views.venta_boleto, name='venta_boleto'),
    path('venta/buscar', views.lista_ventas, name='lista_ventas'),
    path('venta/buscar/<int:id>', views.buscar_venta, name='buscar_venta'),
    path('venta/modificar/<int:id>', views.actualizar_venta, name='actualizar_venta'),
    path('venta/eliminar/<int:id>', views.borrar_venta, name='borrar_venta'),
]
