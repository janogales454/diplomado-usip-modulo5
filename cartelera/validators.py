import datetime
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
from . import constants, utils

def validar_nro_sala(value):
    if value is None:
        raise ValidationError("El numero de sala no puede ser nulo.")
    if not isinstance(value, str):
        raise ValidationError("El numero de sala debe ser un string.")
    if not value.startswith('Sala '):
        raise ValidationError(f"{value} no cumple con el formato apropiado.")
    
def validar_fecha(value):
    if value is None:
        raise ValidationError("La fecha no puede ser nula.")
    if isinstance(value, datetime.date):
        if value < timezone.now().date():
            raise ValidationError(f"{value} debe ser una fecha futura.")
    else:
        raise ValidationError(f"{value} no es una variable valida.")

def validar_mayor(value):
    if value <= 0:
        raise ValidationError(f"{value} tiene que ser mayor que 0.")

def validar_vacio(value):
    if str(value).__len__() == 0:
        raise ValidationError(f"No se puede usar valores vacios.")

def validar_espacio_en_blanco(value):
    if value.isspace():
        raise ValidationError(f"No se puede usar espacios vacios.")

def validar_email(value):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValidationError('Email con formato invalido')
