from datetime import datetime
from . import constants

def convert_str_to_datetime(date_str, format=constants.DATETIME_FORMAT):
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        raise ValueError(f"El valor '{date_str}' no es una fecha válida. Debe seguir el formato {format}.")

def convert_str_to_int(value_str):
    try:
        return int(value_str)
    except ValueError:
        raise ValueError(f"El valor '{value_str}' no es un entero válido.")

def convert_str_to_float(value_str):
    try:
        return float(value_str)
    except ValueError:
        raise ValueError(f"El valor '{value_str}' no es un número float válido.")

def convert_str_to_bool(value_str):
    try:
        if value_str.lower() in ['true', '1', 'yes']:
            return True
        elif value_str.lower() in ['false', '0', 'no']:
            return False
        else:
            raise ValueError(f"El valor '{value_str}' no es un booleano válido.")
    except ValueError:
        raise ValueError(f"El valor '{value_str}' no es un entero válido.")
