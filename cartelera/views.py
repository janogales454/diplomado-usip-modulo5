from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from .models import Sala, Funcion, Venta, Pelicula, Genero
from .serializers import *
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Sum
from . import constants
from . import utils

logger = logging.getLogger(__name__)

class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer

class PeliculaViewSet(viewsets.ModelViewSet):
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer

class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer

class FuncionViewSet(viewsets.ModelViewSet):
    queryset = Funcion.objects.all()
    serializer_class = FuncionSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearFuncionSerializer
        if self.action == 'update':
            return ActualizarFuncionSerializer
        if self.action == 'partial_update':
            return ActualizarFuncionSerializer
        return FuncionSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = CrearFuncionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            sala_id = utils.convert_str_to_int(request.data.get('sala_id'))
            pelicula_id = utils.convert_str_to_int(request.data.get('pelicula_id'))

            sala = Sala.objects.get(id=sala_id)
            if not sala:
                raise ValueError("Sala no encontrada")
            pelicula = Pelicula.objects.get(id=pelicula_id)
            if not pelicula:
                raise ValueError("Película no encontrada")
            
            hora = utils.convert_str_to_datetime(request.data.get('hora'), constants.TIME_FORMAT).time()
            fecha_inicio = utils.convert_str_to_datetime(request.data.get('fecha_inicio'), constants.DATE_FORMAT).date()
            fecha_fin = utils.convert_str_to_datetime(request.data.get('fecha_fin'), constants.DATE_FORMAT).date()
            if fecha_inicio >= fecha_fin:
                raise ValueError("La fecha de inicio no puede ser mayor a la fecha de fin")
            
            tipo_funcion = request.data.get('tipo_funcion')
            precio = utils.convert_str_to_float(request.data.get('precio'))
            if precio <= 0:
                raise ValueError("El precio debe ser un número mayor a cero")

            funcion = Funcion(
                sala_id=sala_id,
                pelicula_id=pelicula_id,
                hora=hora,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                tipo_funcion=tipo_funcion,
                precio=precio
            )
            funcion.save()
            return JsonResponse(
                FuncionSerializer(funcion).data,
                safe=False,
                status=status.HTTP_200_OK
            )
        except Exception as ex:
            return JsonResponse(
                {"error": str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk):
        try:
            serializer = ActualizarFuncionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            funcion = Funcion.objects.get(id=pk)
            if not funcion:
                raise ValueError("Función no encontrada")
            
            sala_id = funcion.sala.id
            pelicula_id = funcion.pelicula.id
            hora = funcion.hora
            fecha_inicio = funcion.fecha_inicio
            fecha_fin = funcion.fecha_fin
            tipo_funcion = funcion.tipo_funcion
            precio = funcion.precio

            if request.data.get('sala_id') is not None:
                sala_id = utils.convert_str_to_int(request.data.get('sala_id'))
            if request.data.get('pelicula_id') is not None:
                pelicula_id = utils.convert_str_to_int(request.data.get('pelicula_id'))
            if request.data.get('hora') is not None:
                hora = utils.convert_str_to_datetime(request.data.get('hora'), constants.TIME_FORMAT).time()
            if request.data.get('fecha_inicio') is not None:
                fecha_inicio = utils.convert_str_to_datetime(request.data.get('fecha_inicio'), constants.DATE_FORMAT).date()
            if request.data.get('fecha_fin') is not None:
                fecha_fin = utils.convert_str_to_datetime(request.data.get('fecha_fin'), constants.DATE_FORMAT).date()
            if request.data.get('tipo_funcion') is not None:
                tipo_funcion = request.data.get('tipo_funcion')
            if request.data.get('precio') is not None:
                precio = utils.convert_str_to_float(request.data.get('precio'))
            
            sala = Sala.objects.get(id=sala_id)
            if not sala:
                raise ValueError("Sala no encontrada")
            pelicula = Pelicula.objects.get(id=pelicula_id)
            if not pelicula:
                raise ValueError("Película no encontrada")
            if fecha_inicio >= fecha_fin:
                raise ValueError("La fecha de inicio no puede ser mayor a la fecha de fin")
            if precio <= 0:
                raise ValueError("El precio debe ser un número mayor a cero")
            
            funcion.sala_id = sala_id
            funcion.pelicula_id = pelicula_id
            funcion.hora = hora
            funcion.fecha_inicio = fecha_inicio
            funcion.fecha_fin = fecha_fin
            funcion.tipo_funcion = tipo_funcion
            funcion.precio = precio
            
            funcion.save()
            return JsonResponse(
                {"message": "Función actualizada correctamente"},
                safe=False,
                status=status.HTTP_200_OK
            )
        except Exception as ex:
            return JsonResponse(
                {"error": str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, pk):
        return self.update(request, pk)


@swagger_auto_schema(method='post',request_body=CrearVentaSerializer)
@api_view(['POST'])
def venta_boleto(request):
    try:
        serializer = CrearVentaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cantidad_boletos = utils.convert_str_to_int(request.data.get('cantidad_boletos'))
        funcion_id = utils.convert_str_to_int(request.data.get('funcion_id'))
        nombre_cliente = request.data.get('nombre_cliente')
        email = request.data.get('email')
        nit = utils.convert_str_to_int(request.data.get('nit'))
        fecha_funcion = utils.convert_str_to_datetime(request.data.get('fecha_funcion'), constants.DATE_FORMAT).date()

        if nombre_cliente is None or nombre_cliente.isspace():
            raise ValueError("El nombre del cliente no puede estar vacío")
        if fecha_funcion < timezone.now().date():
            raise ValueError("La fecha de la función no puede ser anterior a la fecha actual")
        funcion = Funcion.objects.get(id=funcion_id)
        if funcion.fecha_inicio > fecha_funcion or fecha_funcion > funcion.fecha_fin:
            raise ValueError("La función aun no esta disponible o ya ha finalizado")
        
        funcion = Funcion.objects.filter(id=funcion_id).first()
        if not funcion:
            raise ValueError("Función no encontrada")
        sala = Sala.objects.get(id=funcion.sala_id)
        if not sala:
            raise ValueError("Sala de la funcion no encontrada")
        
        asientos_total = sala.capacidad
        ventas = Venta.objects.filter(funcion_id=funcion_id, fecha_funcion=fecha_funcion)
        asientos_ocupados = ventas.aggregate(total_column_sum=Sum('cantidad_boletos'))['total_column_sum']
        if asientos_ocupados is None:
            asientos_ocupados = 0
        asientos_disponibles = asientos_total - asientos_ocupados
        if asientos_disponibles < 0:
            raise ValueError("No hay asientos disponibles para esta función")
        if (asientos_disponibles - cantidad_boletos) < 0:
            raise ValueError("No hay suficientes asientos disponibles para la cantidad solicitada")
        total = cantidad_boletos * funcion.precio
        venta = Venta(
            nombre_cliente=nombre_cliente,
            nit=nit,
            email=email,
            fecha_funcion=fecha_funcion,
            cantidad_boletos=cantidad_boletos,
            total=total,
            funcion=funcion,
        )
        venta.save()
        return JsonResponse(
            VentaSerializer(venta).data,
            safe=False,
            status=status.HTTP_200_OK
        )
    except Exception as ex:
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def lista_ventas(request):
    try:
        ventas = Venta.objects.all()
        serializer = VentaSerializer(ventas, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    except Exception as ex:
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def buscar_venta(request, id):
    try:
        ventas = Venta.objects.get(id=id)
        serializer = VentaSerializer(ventas)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    except Exception as ex:
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(methods=['put','patch'],request_body=ActualizarVentaSerializer)
@api_view(['PUT','PATCH'])
def actualizar_venta(request, id):
    try:
        serializer = CrearVentaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        venta = Venta.objects.get(id=id)
        if not venta:
            raise ValueError("Venta no encontrada")
        
        cantidad_boletos = venta.cantidad_boletos
        nombre_cliente = venta.nombre_cliente
        email = venta.email
        nit = venta.nit

        if request.data.get('nombre_cliente') is not None:
            nombre_cliente = request.data.get('nombre_cliente')
        if request.data.get('email') is not None:
            email = request.data.get('email')
        if request.data.get('nit') is not None:
            nit = utils.convert_str_to_int(request.data.get('nit'))

        venta = Venta(
            cantidad_boletos=cantidad_boletos,
            nombre_cliente=nombre_cliente,
            nit=nit,
            email=email,
        )
        venta.save()
        return JsonResponse(
            VentaSerializer(venta).data,
            safe=False,
            status=status.HTTP_200_OK
        )
    except Exception as ex:
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def borrar_venta(request, id):
    return JsonResponse({}, safe=False, status=status.HTTP_200_OK)