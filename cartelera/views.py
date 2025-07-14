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

    ## Se agrego diferentes serializers para que el Swagger permita emplear las estructuras de request apropiadas de acuerdo al metodo.
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
            tipo_funcion = request.data.get('tipo_funcion')
            if tipo_funcion is None or tipo_funcion.isspace():
                raise ValueError("El tipo de funcion no puede estar vacio")
            precio = utils.convert_str_to_float(request.data.get('precio'))
            if precio <= 0:
                raise ValueError("El precio debe ser un número mayor a cero")

            if timezone.now().date() > pelicula.fecha_retiro:
                raise ValueError("La película ya fue retirada y no se pueden crear más funciones")
            
            funciones_existentes = Funcion.objects.filter(
                sala_id=sala_id,
                hora=hora,
                disponible=True,
            ).count()
            if funciones_existentes > 0:
                raise ValueError("Ya existe una función programada en esta sala a esta hora")

            funcion = Funcion(
                sala_id=sala_id,
                pelicula_id=pelicula_id,
                hora=hora,
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
            tipo_funcion = funcion.tipo_funcion
            precio = funcion.precio
            disponible = funcion.disponible

            if request.data.get('sala_id') is not None:
                sala_id = utils.convert_str_to_int(request.data.get('sala_id'))
            if request.data.get('pelicula_id') is not None:
                pelicula_id = utils.convert_str_to_int(request.data.get('pelicula_id'))
            if request.data.get('hora') is not None:
                hora = utils.convert_str_to_datetime(request.data.get('hora'), constants.TIME_FORMAT).time()
            if request.data.get('tipo_funcion') is not None:
                tipo_funcion = request.data.get('tipo_funcion')
            if request.data.get('precio') is not None:
                precio = utils.convert_str_to_float(request.data.get('precio'))
            if request.data.get('disponible') is not None:
                disponible = utils.convert_str_to_bool(request.data.get('disponible'))
            
            sala = Sala.objects.get(id=sala_id)
            if not sala:
                raise ValueError("Sala no encontrada")
            pelicula = Pelicula.objects.get(id=pelicula_id)
            if not pelicula:
                raise ValueError("Película no encontrada")
            if precio <= 0:
                raise ValueError("El precio debe ser un número mayor a cero")
            
            if timezone.now().date() > pelicula.fecha_retiro:
                raise ValueError("La película ya fue retirada y no se pueden crear más funciones")
            
            funciones_existentes = Funcion.objects.filter(
                sala_id=sala_id,
                hora=hora,
                disponible=True,
            ).count()
            if funciones_existentes > 0:
                raise ValueError("Ya existe una función programada en esta sala a esta hora")
            
            funcion.sala_id = sala_id
            funcion.pelicula_id = pelicula_id
            funcion.hora = hora
            funcion.tipo_funcion = tipo_funcion
            funcion.precio = precio
            funcion.disponible = disponible
            
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


## Retorna una lista de las funciones disponibles.
@api_view(['GET'])
def lista_funciones_disponibles(request):
    try:
        funciones = Funcion.objects.filter(disponible=True,pelicula__fecha_retiro__gte=timezone.now().date())
        if not funciones:
            raise ValueError("No hay funciones disponibles")
        serializer = FuncionSerializer(funciones, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    except Exception as ex:
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

## Revisa las funciones disponibles y cambia su estado si la pelicula ya no está disponible en cartelera.
## Podria ser ejecutado por una tarea de fondo para mantener actualizada la lista de funciones disponibles.
@api_view(['GET'])
def actualizar_funciones_disponibles(request):
    try:
        funciones = Funcion.objects.filter(disponible=True)
        if not funciones:
            raise ValueError("No hay funciones disponibles")
        if funciones.count() > 0:
            count = 0
            for funcion in funciones:
                try:
                    pelicula = Pelicula.objects.get(id=funcion.pelicula_id)
                    if not pelicula:
                        raise ValueError("Película de la función no encontrada")
                    if timezone.now().date() > pelicula.fecha_retiro:
                        funcion.disponible = False
                        funcion.save()
                        count += 1
                except Exception as ex:
                    logger.error(f"Error al actualizar la función {funcion.id}: {str(ex)}")
                    continue
            return JsonResponse({
                "message": f"{count} funciones de {funciones.count()} actualizadas correctamente",
            }, status=status.HTTP_200_OK)
    except Exception as ex:
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
        funcion = Funcion.objects.filter(id=funcion_id).first()
        if not funcion:
            raise ValueError("Función no encontrada")
        pelicula = Pelicula.objects.get(id=funcion.pelicula_id)
        if not pelicula:
            raise ValueError("Película de la función no encontrada")
        if pelicula.fecha_lanzamiento > fecha_funcion or fecha_funcion > pelicula.fecha_retiro:
            raise ValueError("La función aun no esta disponible o ya ha finalizado")
        
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
        serializer = ActualizarVentaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        venta = Venta.objects.get(id=id)
        if not venta:
            raise ValueError("Venta no encontrada")
        
        nombre_cliente = venta.nombre_cliente
        email = venta.email
        nit = venta.nit

        if request.data.get('nombre_cliente') is not None:
            nombre_cliente = request.data.get('nombre_cliente')
        if request.data.get('email') is not None:
            email = request.data.get('email')
        if request.data.get('nit') is not None:
            nit = utils.convert_str_to_int(request.data.get('nit'))

        venta.nombre_cliente = nombre_cliente
        venta.email = email
        venta.nit = nit
        
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
    try:
        venta = Venta.objects.get(id=id)
        if not venta:
            raise ValueError("Venta no encontrada")
        venta.delete()
        return JsonResponse({"message": "Venta eliminada correctamente"}, status=status.HTTP_200_OK)
    except Exception as ex:
        logger.error(f"Error al eliminar la venta con id {id}: {str(ex)}")
        return JsonResponse(
            {"error": str(ex)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )