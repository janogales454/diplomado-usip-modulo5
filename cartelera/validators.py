from django.core.exceptions import ValidationError
import re


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
