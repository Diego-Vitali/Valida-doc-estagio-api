import pytest
from datetime import date, time
from utils.exceptions import ValidationError
from utils.estagio import (
    validate_dados_estagio,
    is_valid_date_range,
    is_valid_contract_duration,
    is_valid_daily_hours,
    is_valid_weekly_hours
)
from api.schemas import DadosEstagioSchema

@pytest.fixture
def dados_estagio_validos():
    """Retorna um objeto Schema com dados válidos para usar como base."""
    return DadosEstagioSchema(
        data_inicio=date(2025, 1, 1),
        data_termino=date(2025, 12, 31),
        horario_inicio=time(9, 0),    # 09:00
        horario_termino=time(15, 0),  # 15:00 (6 horas)
        horas_semanais=30,
        nome_seguradora="Seguradora Teste",
        numero_apolice_seguro="12345",
        valor_seguro=100.0,
        valor_bolsa_auxilio=1000.0
    )

# --- Testes Unitários das Funções Auxiliares ---
def test_is_valid_date_range():
    # Sucesso: Fim depois do início
    assert is_valid_date_range(date(2025, 1, 1), date(2025, 1, 2)) is True
    # Falha: Fim igual ao início
    assert is_valid_date_range(date(2025, 1, 1), date(2025, 1, 1)) is False
    # Falha: Fim antes do início
    assert is_valid_date_range(date(2025, 1, 2), date(2025, 1, 1)) is False

def test_is_valid_contract_duration_normal():
    start = date(2024, 1, 1)
    
    # Exatamente 2 anos (Deve passar)
    end_exact = date(2026, 1, 1)
    assert is_valid_contract_duration(start, end_exact, is_pcd=False) is True
    
    # 2 anos e 1 dia (Deve falhar)
    end_over = date(2026, 1, 2)
    assert is_valid_contract_duration(start, end_over, is_pcd=False) is False

def test_is_valid_contract_duration_leap_year():
    """Teste específico para virada de ano bissexto (29/02)."""
    start = date(2024, 2, 29) # 2024 é bissexto
    
    # 2026 não é bissexto. A lógica trata o "aniversário" de 2 anos como 01/03/2026.
    end_valid = date(2026, 3, 1)
    assert is_valid_contract_duration(start, end_valid, is_pcd=False) is True
    
    end_invalid = date(2026, 3, 2)
    assert is_valid_contract_duration(start, end_invalid, is_pcd=False) is False

def test_is_valid_contract_duration_pcd():
    """PCD pode exceder 2 anos."""
    start = date(2024, 1, 1)
    end_long = date(2030, 1, 1) # 6 anos
    
    assert is_valid_contract_duration(start, end_long, is_pcd=True) is True

def test_is_valid_daily_hours():
    start = time(8, 0)
    
    # 6 horas exatas (Passa)
    assert is_valid_daily_hours(start, time(14, 0)) is True
    
    # 4 horas (Passa)
    assert is_valid_daily_hours(start, time(12, 0)) is True
    
    # 6 horas e 1 minuto (Falha)
    assert is_valid_daily_hours(start, time(14, 1)) is False
    
    # Horário invertido (Término antes do início)
    assert is_valid_daily_hours(time(14, 0), time(8, 0)) is False

def test_is_valid_weekly_hours():
    assert is_valid_weekly_hours(30) is True
    assert is_valid_weekly_hours(20) is True
    assert is_valid_weekly_hours(31) is False

# --- Testes de Integração da Função Principal ---

def test_validate_dados_estagio_sucesso(dados_estagio_validos):
    """Teste do caminho feliz."""
    assert validate_dados_estagio(dados_estagio_validos) is None  # Retorna None se sucesso (ou True se alterado)

def test_validate_dados_estagio_erro_cronologico(dados_estagio_validos):
    """Data de término anterior ao início."""
    dados_estagio_validos.data_inicio = date(2025, 12, 31)
    dados_estagio_validos.data_termino = date(2025, 1, 1)
    
    with pytest.raises(ValidationError, match="Data de Término anterior ou igual"):
        validate_dados_estagio(dados_estagio_validos)

def test_validate_dados_estagio_erro_duracao(dados_estagio_validos):
    """Duração maior que 2 anos para não PCD."""
    dados_estagio_validos.data_inicio = date(2024, 1, 1)
    dados_estagio_validos.data_termino = date(2026, 1, 2) # 2 anos e 1 dia
    
    with pytest.raises(ValidationError, match="Contrato não pode durar mais do que 2 anos"):
        validate_dados_estagio(dados_estagio_validos, is_pcd=False)

def test_validate_dados_estagio_sucesso_pcd_longo(dados_estagio_validos):
    """Duração maior que 2 anos PARA PCD (deve passar)."""
    dados_estagio_validos.data_inicio = date(2024, 1, 1)
    dados_estagio_validos.data_termino = date(2028, 1, 1)
    
    # Não deve levantar exceção
    validate_dados_estagio(dados_estagio_validos, is_pcd=True)

def test_validate_dados_estagio_erro_hora_invertida(dados_estagio_validos):
    """Término do expediente antes do início."""
    dados_estagio_validos.horario_inicio = time(18, 0)
    dados_estagio_validos.horario_termino = time(12, 0)
    
    with pytest.raises(ValidationError, match="Horário de término deve ser posterior"):
        validate_dados_estagio(dados_estagio_validos)

def test_validate_dados_estagio_erro_carga_diaria(dados_estagio_validos):
    """Mais de 6 horas por dia."""
    dados_estagio_validos.horario_inicio = time(8, 0)
    dados_estagio_validos.horario_termino = time(15, 0) # 7 horas
    
    with pytest.raises(ValidationError, match="Número de Horas Diárias não deve ser superior"):
        validate_dados_estagio(dados_estagio_validos)

def test_validate_dados_estagio_erro_carga_semanal(dados_estagio_validos):
    """Mais de 30 horas semanais."""
    dados_estagio_validos.horas_semanais = 40
    
    with pytest.raises(ValidationError, match="Número de horas semanais"):
        validate_dados_estagio(dados_estagio_validos)