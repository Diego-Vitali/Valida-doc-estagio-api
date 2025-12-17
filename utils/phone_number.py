import re
from .exceptions import ValidationError

def format_phone_number(phone_number: str) -> str:
    clean_phone = phone_number.replace('+55', '')
    return re.sub(r'[^0-9]', '', clean_phone)

def is_valid_phone_number(phone_number: str) -> bool:
    phone_number = format_phone_number(phone_number)
    
    if not phone_number.isdigit():
        return False
    
    if phone_number.startswith('0') or (len(phone_number) > 1 and phone_number[1] == '0'):
        return False

    length = len(phone_number)
    if length == 11:
        if phone_number[2] != '9' or phone_number[3] == '0':
            return False
    elif length == 10:
        if phone_number[2] in ['0', '1', '9']:
            return False
    else:
        return False
        
    return True

def validate_phone_number(phone_number: str):
    if not is_valid_phone_number(phone_number):
        raise ValidationError("O número de telefone é inválido.")