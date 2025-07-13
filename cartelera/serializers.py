from rest_framework import serializers
from .models import Sala, Funcion, Venta, Pelicula, Genero

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

class PeliculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pelicula
        fields = '__all__'

class SalaSerializer(serializers.ModelSerializer):
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
    fecha_inicio = serializers.DateField(required=True, allow_null=False)
    fecha_fin = serializers.DateField(required=True, allow_null=False)
    tipo_funcion = serializers.CharField(max_length=4, default='2D')
    precio = serializers.DecimalField(max_digits=6, decimal_places=2, default=0.00)

class ActualizarFuncionSerializer(serializers.Serializer):
    sala_id = serializers.IntegerField()
    pelicula_id = serializers.IntegerField()
    hora = serializers.TimeField(default='00:00:00')
    fecha_inicio = serializers.DateField(required=True, allow_null=False)
    fecha_fin = serializers.DateField(required=True, allow_null=False)
    tipo_funcion = serializers.CharField(max_length=4, default='2D')
    precio = serializers.DecimalField(max_digits=6, decimal_places=2, default=0.00)

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
