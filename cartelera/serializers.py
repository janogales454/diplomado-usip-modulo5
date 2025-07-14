from rest_framework import serializers
from .models import Sala, Funcion, Venta, Pelicula, Genero
from .validators import *

class GeneroSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(default='', validators=[validar_vacio, validar_espacio_en_blanco])
    class Meta:
        model = Genero
        fields = '__all__'

class PeliculaSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(default='', validators=[validar_vacio, validar_espacio_en_blanco])
    duracion = serializers.IntegerField(default=0, validators=[validar_mayor])
    sinopsis = serializers.CharField(default='', validators=[validar_vacio, validar_espacio_en_blanco])
    fecha_lanzamiento = serializers.DateField(required=True, allow_null=False, validators=[validar_fecha])
    fecha_retiro = serializers.DateField(required=True, allow_null=False, validators=[validar_fecha])
    class Meta:
        model = Pelicula
        fields = '__all__'

    def validate(self, data):
        fecha_lanzamiento = data.get('fecha_lanzamiento')
        fecha_retiro = data.get('fecha_retiro')
        if fecha_lanzamiento and fecha_retiro:
            if fecha_lanzamiento >= fecha_retiro:
                raise serializers.ValidationError("La fecha de lanzamiento debe ser anterior a la fecha de retiro.")
        return data

class SalaSerializer(serializers.ModelSerializer):
    nro_sala = serializers.CharField(default='Sala 1', validators=[validar_espacio_en_blanco, validar_nro_sala])
    capacidad = serializers.IntegerField(default=50)
    class Meta:
        model = Sala
        fields = '__all__'

class FuncionSerializer(serializers.ModelSerializer):
    pelicula = PeliculaSerializer(read_only=True)
    sala = SalaSerializer(read_only=True)

    class Meta:
        model = Funcion
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    funcion = FuncionSerializer(read_only=True)

    class Meta:
        model = Venta
        fields = '__all__'
        read_only_fields = ('fecha_venta', 'total')

class CrearFuncionSerializer(serializers.Serializer):
    sala_id = serializers.IntegerField()
    pelicula_id = serializers.IntegerField()
    hora = serializers.TimeField(default='00:00:00')
    tipo_funcion = serializers.CharField(max_length=4, default='2D')
    precio = serializers.DecimalField(max_digits=6, decimal_places=2, default=0.00)

class ActualizarFuncionSerializer(serializers.Serializer):
    sala_id = serializers.IntegerField()
    pelicula_id = serializers.IntegerField()
    hora = serializers.TimeField(default='00:00:00')
    tipo_funcion = serializers.CharField(max_length=4, default='2D')
    precio = serializers.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    disponible = serializers.BooleanField(default=True)

class CrearVentaSerializer(serializers.Serializer):
    funcion_id = serializers.IntegerField()
    cantidad_boletos = serializers.IntegerField()
    nombre_cliente = serializers.CharField(max_length=100, required=False, allow_blank=True, default='Cliente Anónimo')
    email = serializers.CharField(max_length=100, required=False, allow_blank=True, default='example@email.com')
    nit = serializers.IntegerField(required=False, allow_null=True)
    fecha_funcion = serializers.DateField(required=True, allow_null=False)

class ActualizarVentaSerializer(serializers.Serializer):
    cantidad_boletos = serializers.IntegerField()
    nombre_cliente = serializers.CharField(max_length=100, required=False, allow_blank=True, default='Cliente Anónimo')
    email = serializers.CharField(max_length=100, required=False, allow_blank=True, default='example@email.com')
    nit = serializers.IntegerField(required=False, allow_null=True)
