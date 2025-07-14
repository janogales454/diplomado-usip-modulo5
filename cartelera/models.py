import datetime
from django.db import models
from django.forms import ValidationError

from . import constants
from .validators import *

# Create your models here.

class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True, validators=[validar_vacio,validar_espacio_en_blanco])

    def __str__(self):
        return self.nombre

class Pelicula(models.Model):
    titulo = models.CharField(max_length=200, validators=[validar_vacio,validar_espacio_en_blanco])
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE)
    duracion = models.IntegerField(validators=[validar_mayor,]) # la duracion siempre se mide en minutos
    fecha_lanzamiento = models.DateField(blank=False, null=False)
    fecha_retiro = models.DateField(blank=False, null=False)
    sinopsis = models.TextField(validators=[validar_vacio,validar_espacio_en_blanco])

    def __str__(self):
        return f"{self.titulo} ({self.genero.nombre}) - {self.duracion} min - Lanzamiento: {self.fecha_lanzamiento} - Retiro: {self.fecha_retiro}"
    
    def clean(self):
        if self.fecha_lanzamiento and self.fecha_retiro:
            if self.fecha_lanzamiento >= self.fecha_retiro:
                raise ValidationError("La fecha de lanzamiento debe ser anterior a la fecha de retiro.")
        super().clean()


class Sala(models.Model):
    nro_sala = models.CharField(unique=True, max_length=10, validators=[validar_vacio,validar_espacio_en_blanco])
    capacidad = models.IntegerField(validators=[validar_mayor,])

    def __str__(self):
        return f"{self.nro_sala} (Capacidad: {self.capacidad})"
    
    def clean(self):
        if self.nro_sala is None or not self.nro_sala.startswith('Sala '):
            raise ValidationError("El valor no cumple con el formato apropiado.")
        super().clean()
    
class FuncionTipo(models.TextChoices):
    DOSD = '2D', '2D'
    TRESD = '3D', '3D'
    IMAX = 'IMAX', 'IMAX'


class Funcion(models.Model):
    TIME_CHOICES = (
        (datetime.time(0, 0, 0), '00:00'),
        (datetime.time(10, 0, 0), '10:00'),
        (datetime.time(12, 0, 0), '12:00'),
        (datetime.time(14, 0, 0), '14:00'),
        (datetime.time(16, 0, 0), '16:00'),
        (datetime.time(18, 0, 0), '18:00'),
        (datetime.time(20, 0, 0), '20:00'),
        (datetime.time(22, 0, 0), '22:00'),
    )
    pelicula = models.ForeignKey('cartelera.Pelicula', on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    hora = models.TimeField(blank=False, null=False,
        choices=TIME_CHOICES)
    tipo_funcion = models.CharField(
        max_length=4, 
        choices=FuncionTipo.choices, 
        default=FuncionTipo.DOSD
    )
    precio = models.DecimalField(max_digits=6, decimal_places=2, validators=[validar_mayor,])
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pelicula.titulo} ({self.tipo_funcion}) en {self.sala.nro_sala} a las {self.hora.strftime(constants.TIME_FORMAT)}"
    

class Venta(models.Model):
    funcion = models.ForeignKey(Funcion, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    nit = models.IntegerField(blank=True, null=True, validators=[validar_mayor,])
    email = models.CharField(blank=True, null=True, validators=[validar_email,])
    fecha_venta = models.DateTimeField(auto_now_add=True, blank=True)
    fecha_funcion = models.DateField(blank=False, null=False)
    cantidad_boletos = models.IntegerField(validators=[validar_mayor,])
    total = models.DecimalField(max_digits=10, decimal_places=2,validators=[validar_mayor,])

    def __str__(self):
        return f"Venta de {self.cantidad_boletos} boletos a nombre de {self.nombre_cliente} para {self.funcion.pelicula.titulo} - Total: {self.total}"

