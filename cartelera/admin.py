from django.contrib import admin
from .models import Genero, Pelicula, Sala, Funcion, Venta

# Register your models here.
admin.site.register(Genero)

class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'genero', 'duracion', 'fecha_lanzamiento','fecha_retiro', 'sinopsis')
    ordering = ('fecha_lanzamiento',)
    search_fields = ('titulo', 'genero__nombre')
    list_filter = ('genero', 'fecha_lanzamiento')

admin.site.register(Pelicula, PeliculaAdmin)

class SalaAdmin(admin.ModelAdmin):
    list_display = ('nro_sala', 'capacidad')
    search_fields = ('nro_sala',)
    ordering = ('nro_sala',)

admin.site.register(Sala, SalaAdmin)

class FuncionAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'sala', 'hora', 'tipo_funcion', 'precio','disponible')
    search_fields = ('pelicula__titulo', 'sala__nro_sala')
    list_filter = ('sala_id','tipo_funcion','disponible')
    ordering = ('sala_id','hora')

admin.site.register(Funcion, FuncionAdmin)

class VentaAdmin(admin.ModelAdmin):
    list_display = ('funcion', 'nombre_cliente', 'nit', 'email', 'fecha_venta', 'fecha_funcion', 'cantidad_boletos', 'total')
    search_fields = ('nombre_cliente', 'email', 'funcion__pelicula__titulo')
    list_filter = ('fecha_venta', 'fecha_funcion')
    ordering = ('fecha_venta', 'fecha_funcion')

admin.site.register(Venta,VentaAdmin)
