from datetime import datetime, date, time, timedelta
from .exceptions import ValidationError
from api.schemas import DadosEstagioSchema

# --- Funções Auxiliares---
def is_valid_date_range(start_date: date, end_date: date) -> bool:
    """Verifica se a data de término é posterior à data de início."""
    return end_date > start_date

def is_valid_contract_duration(start_date: date, end_date: date, is_pcd: bool) -> bool:
    """
    Verifica se a duração é de no máximo 2 anos.
    Se for PCD (Portador de Deficiência), ignora essa regra.
    """
    if is_pcd:
        return True
    
    try:
        max_end_date = start_date.replace(year=start_date.year + 2)
    except ValueError:
        # Tratamento para ano bissexto (29/02 -> 01/03)
        max_end_date = start_date.replace(year=start_date.year + 2, month=3, day=1)
        
    return end_date <= max_end_date

def is_valid_daily_hours(start_time: time, end_time: time, limit_hours: float = 6.0) -> bool:
    """
    Verifica se a carga horária diária respeita o limite (padrão 6 horas).
    """
    if end_time <= start_time:
        return False
    
    dummy_date = date.min
    dt_start = datetime.combine(dummy_date, start_time)
    dt_end = datetime.combine(dummy_date, end_time)

    diff = dt_end - dt_start
    hours_worked = diff.total_seconds() / 3600

    return hours_worked <= limit_hours

def is_valid_weekly_hours(hours: int, limit: int = 30) -> bool:
    """Verifica limite de horas semanais."""
    return hours <= limit

# --- Função Principal da Validação ---
def validate_dados_estagio(dados: DadosEstagioSchema, is_pcd: bool = False):
    """
    Valida o bloco 'dados_estagio' completo.
    """

    if not is_valid_date_range(dados.data_inicio, dados.data_termino):
        raise ValidationError("Data de Término anterior ou igual à data de Início.")

    if not is_valid_contract_duration(dados.data_inicio, dados.data_termino, is_pcd):
        raise ValidationError("Contrato não pode durar mais do que 2 anos (exceto PCD).")

    if dados.horario_termino <= dados.horario_inicio:
        raise ValidationError("Horário de término deve ser posterior ao horário de início.")
        
    if not is_valid_daily_hours(dados.horario_inicio, dados.horario_termino):
        raise ValidationError("Número de Horas Diárias não deve ser superior a 6 horas.")

    if not is_valid_weekly_hours(dados.horas_semanais):
        raise ValidationError(f"Número de horas semanais ({dados.horas_semanais}h) não deve ultrapassar 30 horas.")