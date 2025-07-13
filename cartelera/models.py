from django.db import models
from .validators import validar_mayor, validar_vacio, validar_espacio_en_blanco, validar_email

# Create your models here.

class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True, validators=[validar_vacio,validar_espacio_en_blanco])

    def __str__(self):
        return self.nombre

class Pelicula(models.Model):
    titulo = models.CharField(max_length=200, validators=[validar_vacio,validar_espacio_en_blanco])
    genero = models.ForeignKey(Genero, on_delete=models.DO_NOTHING)
    duracion = models.IntegerField(validators=[validar_mayor,])  # Duración en minutos
    fecha_lanzamiento = models.DateField(blank=False, null=False)
    sinopsis = models.TextField(validators=[validar_vacio,validar_espacio_en_blanco])

    def __str__(self):
        return self.titulo


class Sala(models.Model):
    nro_sala = models.CharField(unique=True, max_length=10, validators=[validar_vacio,validar_espacio_en_blanco])
    capacidad = models.IntegerField(validators=[validar_mayor,])

    def __str__(self):
        return f"{self.nro_sala} (Capacidad: {self.capacidad})"
    
class FuncionTipo(models.TextChoices):
    DOSD = '2D', '2D'
    TRESD = '3D', '3D'
    IMAX = 'IMAX', 'IMAX'

class Funcion(models.Model):
    pelicula = models.ForeignKey('cartelera.Pelicula', on_delete=models.DO_NOTHING)
    sala = models.ForeignKey(Sala, on_delete=models.DO_NOTHING)
    hora = models.TimeField(blank=False, null=False)
    fecha_inicio = models.DateField(blank=False)
    fecha_fin = models.DateField(blank=False)
    tipo_funcion = models.CharField(
        max_length=4, 
        choices=FuncionTipo.choices, 
        default=FuncionTipo.DOSD
    )
    precio = models.DecimalField(max_digits=6, decimal_places=2, validators=[validar_mayor,])

    def __str__(self):
        return f"{self.pelicula.titulo} en {self.sala.nro_sala} a las {self.hora.strftime('%Y-%m-%d %H:%M')}"
    
class Venta(models.Model):
    funcion = models.ForeignKey(Funcion, on_delete=models.DO_NOTHING)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    nit = models.IntegerField(blank=True, null=True, validators=[validar_mayor,])
    email = models.CharField(blank=True, null=True, validators=[validar_email,])
    fecha_venta = models.DateTimeField(auto_now_add=True, blank=True)
    fecha_funcion = models.DateField(blank=False, null=False)
    cantidad_boletos = models.IntegerField(validators=[validar_mayor,])
    total = models.DecimalField(max_digits=10, decimal_places=2,validators=[validar_mayor,])

    def __str__(self):
        return f"Venta de {self.cantidad_boletos} boletos para {self.funcion.pelicula.titulo} - Total: {self.total}"

