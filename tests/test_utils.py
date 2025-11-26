# Rode com:
# pytest
# (na raiz do projeto)

import pytest
from utils import (
    ValidationError,
    # CEP
    format_cep, is_valid_cep, validate_cep,
    # CPF
    format_cpf, is_valid_cpf, validate_cpf, mask_cpf,
    # CNPJ
    format_cnpj, is_valid_cnpj, validate_cnpj, mask_cnpj,
    # Email
    is_valid_email, validate_email, mask_email,
    # Phone
    format_phone_number, is_valid_phone_number, validate_phone_number,
    # UF
    is_valid_uf, validate_uf,
    # Dados de Estágio
    validate_dados_estagio, is_valid_date_range, is_valid_contract_duration,
    is_valid_daily_hours, is_valid_weekly_hours
)

# --- Testes para CEP ---

def test_format_cep():
    assert format_cep("01001-000") == "01001000"
    assert format_cep(" 01001000 ") == "01001000"

def test_is_valid_cep():
    assert is_valid_cep("01001000") == True
    assert is_valid_cep("01001-000") == True # Deve formatar internamente
    assert is_valid_cep("1234567") == False # Curto
    assert is_valid_cep("123456789") == False # Longo
    assert is_valid_cep("abcdefgh") == False # Letras

def test_validate_cep():
    validate_cep("01001-000") # Deve passar
    with pytest.raises(ValidationError, match="deve conter 8 dígitos"):
        validate_cep("1234567")
    with pytest.raises(ValidationError, match="deve conter apenas números"):
        validate_cep("abc")


# --- Testes para CPF ---

VALID_CPF_NUMBERS = "12136309595"
VALID_CPF_FORMATTED = "121.363.095-95"
INVALID_CPF_ALL_SAME = "11111111111"
INVALID_CPF_WRONG_DIGIT = "05809521001"

def test_format_cpf():
    assert format_cpf(VALID_CPF_FORMATTED) == VALID_CPF_NUMBERS

def test_is_valid_cpf():
    assert is_valid_cpf(VALID_CPF_NUMBERS) == True
    assert is_valid_cpf(VALID_CPF_FORMATTED) == True
    assert is_valid_cpf(INVALID_CPF_ALL_SAME) == False
    assert is_valid_cpf(INVALID_CPF_WRONG_DIGIT) == False
    assert is_valid_cpf("123") == False

def test_validate_cpf():
    validate_cpf(VALID_CPF_NUMBERS) # Deve passar
    with pytest.raises(ValidationError, match="O número do CPF é inválido"):
        validate_cpf(INVALID_CPF_WRONG_DIGIT)
    with pytest.raises(ValidationError, match="O número do CPF é inválido"):
        validate_cpf("abc")

def test_mask_cpf():
    assert mask_cpf(VALID_CPF_NUMBERS) == "121.***.***-95"
    assert mask_cpf(VALID_CPF_FORMATTED) == "121.***.***-95"


# --- Testes para CNPJ ---

VALID_CNPJ_NUMBERS = "80971798000158"
VALID_CNPJ_FORMATTED = "80.971.798/0001-58"
INVALID_CNPJ_ALL_SAME = "22222222222222"
INVALID_CNPJ_WRONG_DIGIT = "14381455000106"

def test_format_cnpj():
    assert format_cnpj(VALID_CNPJ_FORMATTED) == VALID_CNPJ_NUMBERS

def test_is_valid_cnpj():
    assert is_valid_cnpj(VALID_CNPJ_NUMBERS) == True
    assert is_valid_cnpj(VALID_CNPJ_FORMATTED) == True
    assert is_valid_cnpj(INVALID_CNPJ_ALL_SAME) == False
    assert is_valid_cnpj(INVALID_CNPJ_WRONG_DIGIT) == False
    assert is_valid_cnpj("123") == False

def test_validate_cnpj():
    validate_cnpj(VALID_CNPJ_NUMBERS) # Deve passar
    with pytest.raises(ValidationError, match="O número do CNPJ é inválido"):
        validate_cnpj(INVALID_CNPJ_WRONG_DIGIT)
    with pytest.raises(ValidationError, match="O número do CNPJ é inválido"):
        validate_cnpj("abc")

def test_mask_cnpj():
    assert mask_cnpj(VALID_CNPJ_NUMBERS) == "80.***.***/0001-**"
    assert mask_cnpj(VALID_CNPJ_FORMATTED) == "80.***.***/0001-**"


# --- Testes para Email ---

@pytest.mark.parametrize("valid_email", [
    "email@example.com",
    "firstname.lastname@example.com",
    "email@subdomain.example.com",
    "firstname+lastname@example.com",
])
def test_is_valid_email_passes(valid_email):
    assert is_valid_email(valid_email) == True

@pytest.mark.parametrize("invalid_email", [
    "plainaddress",
    "#@%^%#$@#$@#.com",
    "@example.com",
    "email.example.com",
    "email@example@example.com",
    ".email@example.com",
    "email.@example.com",
])
def test_is_valid_email_fails(invalid_email):
    assert is_valid_email(invalid_email) == False

def test_mask_email():
    assert mask_email("gabriel.lourenco@example.com") == "gabr************@example.com"
    assert mask_email("test@example.com") == "test@example.com" # Não mascara se curto
    assert mask_email("invalid-email") == "invalid-email"


# --- Testes para Telefone ---

def test_format_phone_number():
    assert format_phone_number("+55 (11) 98765-4321") == "11987654321"
    assert format_phone_number("11 2345 6789") == "1123456789"

def test_is_valid_phone_number():
    # Válidos
    assert is_valid_phone_number("11987654321") == True # Celular
    assert is_valid_phone_number("1123456789") == True # Fixo
    
    # Inválidos
    assert is_valid_phone_number("0123456789") == False # DDD inválido
    assert is_valid_phone_number("1112345678") == False # Fixo com 1
    assert is_valid_phone_number("12345") == False # Curto

def test_validate_phone_number():
    validate_phone_number("11987654321") # Deve passar
    with pytest.raises(ValidationError, match="O número de telefone é inválido"):
        validate_phone_number("123")


# --- Testes para UF ---

def test_is_valid_uf():
    assert is_valid_uf("SP") == True
    assert is_valid_uf("sp") == True
    assert is_valid_uf("RJ") == True
    assert is_valid_uf("XX") == False
    assert is_valid_uf("Sao Paulo") == False

def test_validate_uf():
    validate_uf("MG") # Deve passar
    with pytest.raises(ValidationError, match="UF inválida"):
        validate_uf("ZZ")