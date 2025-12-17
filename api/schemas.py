from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import date, time, datetime, timedelta
import httpx

from utils import (
    validate_cep,
    validate_cpf,
    validate_cnpj,
    validate_email,
    validate_phone_number,
    validate_uf,
    ValidationError
)

# --- Helper para conectar Utils ao Pydantic ---
def validar_com_utils(func_validacao, valor, nome_campo):
    """
    Executa uma função de validação da lib utils.
    Se a lib levantar ValidationError, converte para ValueError do Pydantic.
    """
    if not valor:
        return valor
    try:
        func_validacao(valor)
    except ValidationError as e:
        raise ValueError(str(e))
    return valor

# Esses Schemas se referem aos aninhamentos internos dos nós

class EnderecoSchema(BaseModel):
    endereco: str = Field(..., max_length=100)
    cep: str = Field(..., max_length=9, description="Formato XXXXX-XXX")
    bairro: str = Field(..., max_length=100)
    cidade: str = Field(..., max_length=100)
    estado: str = Field(..., max_length=2)

    @field_validator('cep')
    def validar_cep(cls, v):
        return validar_com_utils(validate_cep, v, 'cep')

    @field_validator('estado')
    def validar_estado(cls, v):
        return validar_com_utils(validate_uf, v, 'estado')

class RepresentanteSchema(BaseModel):
    nome: str = Field(..., max_length=100)
    cargo: str = Field(..., max_length=100)

class RegistroProfissionalSchema(BaseModel):
    numero: str = Field(..., max_length=20)
    orgao: str = Field(..., max_length=20)

# Esses schemas se referem aos nós principais

class UnidadeConcedenteSchema(BaseModel):
    razao_social: str = Field(..., max_length=100)
    cnpj: Optional[str] = Field(None, max_length=18)
    insc_estadual: str = Field(..., max_length=20)
    cpf: Optional[str] = Field(None, max_length=14)
    telefone: str = Field(..., max_length=15)
    endereco: EnderecoSchema
    representante_legal: RepresentanteSchema

    @field_validator('cnpj')
    def validar_cnpj_campo(cls, v):
        """
        Valida o formato/dígito (Matemática) e a existência na Receita (API).
        """
        if not v:
            return v

        # 1. Validação Matemática (Utils - Rápida)
        try:
            validate_cnpj(v)
        except ValidationError as e:
            raise ValueError(str(e))

        # 2. Validação Externa (BrasilAPI - Lenta)
        cnpj_limpo = v.replace('.', '').replace('/', '').replace('-', '')
        
        try:
            # Cliente síncrono pois validadores do Pydantic são síncronos
            with httpx.Client(timeout=10.0) as client:
                url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
                response = client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'type' in data and data['type'] == 'service_error':
                        raise ValueError(f"CNPJ não encontrado na base da Receita Federal: {v}")
                    
                elif response.status_code == 404:
                    raise ValueError(f"CNPJ não existe na Receita Federal: {v}")
                
                elif response.status_code == 400:
                    raise ValueError("CNPJ inválido ou mal formatado na consulta externa.")
                
                else:
                    # Em caso de erro 500 da API externa, barramos por segurança
                    raise ValueError(f"Erro ao consultar BrasilAPI (Status {response.status_code}). Tente novamente.")

        except httpx.RequestError:
             raise ValueError("Erro de conexão: Não foi possível validar o CNPJ na Receita Federal.")

        return v

    @field_validator('cpf')
    def validar_cpf_campo(cls, v):
        return validar_com_utils(validate_cpf, v, 'cpf')

    @field_validator('telefone')
    def validar_telefone_campo(cls, v):
        return validar_com_utils(validate_phone_number, v, 'telefone')

    @model_validator(mode='after')
    def verificar_documento_obrigatorio(self):
        """Regra: Obrigatório CNPJ se CPF não preenchido e vice-versa."""
        if not self.cnpj and not self.cpf:
            raise ValueError('É obrigatório informar o CNPJ ou o CPF da Unidade Concedente.')
        return self

class SupervisorSchema(BaseModel):
    nome: str = Field(..., max_length=100)
    cpf: str = Field(..., max_length=14)
    cargo: str = Field(..., max_length=100)
    formacao_academica: str = Field(..., max_length=100)
    registro_profissional: RegistroProfissionalSchema
    email: str = Field(..., max_length=100)

    @field_validator('cpf')
    def validar_cpf_campo(cls, v):
        return validar_com_utils(validate_cpf, v, 'cpf')

    @field_validator('email')
    def validar_email_campo(cls, v):
        return validar_com_utils(validate_email, v, 'email')

class EstagiarioSchema(BaseModel):
    nome: str = Field(..., max_length=100)
    curso: str = Field(..., max_length=100)
    periodo: str = Field(..., max_length=20)
    prontuario: str = Field(..., max_length=20)
    rg: str = Field(..., max_length=12)
    cpf: str = Field(..., max_length=14)
    data_nascimento: date
    endereco: EnderecoSchema
    telefone: Optional[str] = Field(None, max_length=15)
    celular: str = Field(..., max_length=15)
    email: str = Field(..., max_length=100)
    estagio_obrigatorio: bool
    portador_de_deficiencia: bool

    @field_validator('cpf')
    def validar_cpf_campo(cls, v):
        return validar_com_utils(validate_cpf, v, 'cpf')

    @field_validator('email')
    def validar_email_campo(cls, v):
        return validar_com_utils(validate_email, v, 'email')

    @field_validator('telefone')
    def validar_telefone_campo(cls, v):
        return validar_com_utils(validate_phone_number, v, 'telefone')

    @field_validator('celular')
    def validar_celular_campo(cls, v):
        return validar_com_utils(validate_phone_number, v, 'celular')

class DadosEstagioSchema(BaseModel):
    data_inicio: date
    data_termino: date
    horario_inicio: time # Formato HH:MM
    horario_termino: time # Formato HH:MM
    horas_semanais: int
    nome_seguradora: str = Field(..., max_length=100)
    numero_apolice_seguro: str = Field(..., max_length=50)
    valor_seguro: float
    valor_bolsa_auxilio: float

    @model_validator(mode='after')
    def validar_regras_negocio_datas(self):
        # Data Término deve ser posterior à Data Início
        if self.data_termino <= self.data_inicio:
            raise ValueError('A data de término deve ser posterior à data de início.')
        return self

    @model_validator(mode='after')
    def validar_regras_negocio_horarios(self):
        # Cálculo da carga horária diária
        dummy_date = date(2000, 1, 1)
        dt_inicio = datetime.combine(dummy_date, self.horario_inicio)
        dt_termino = datetime.combine(dummy_date, self.horario_termino)

        if dt_termino <= dt_inicio:
            raise ValueError('O horário de término deve ser posterior ao horário de início.')

        diferenca = dt_termino - dt_inicio
        horas_diarias = diferenca.total_seconds() / 3600

        # Não ultrapassar 6 horas diárias (padrão)
        if horas_diarias > 6:
            raise ValueError(f'A carga horária diária ({horas_diarias:.1f}h) excede o limite permitido de 6 horas.')

        # Não deve ultrapassar 30 horas semanais
        if self.horas_semanais > 30:
             raise ValueError(f'A carga horária semanal ({self.horas_semanais}h) excede o limite permitido de 30 horas.')
             
        return self

# Schema principal para o JSON que será recebido:

class ValidacaoDocumentoSchema(BaseModel):
    unidade_concedente: UnidadeConcedenteSchema
    supervisor: SupervisorSchema
    estagiario: EstagiarioSchema
    dados_estagio: DadosEstagioSchema

    @model_validator(mode='after')
    def validar_duracao_estagio(self):
        """
        Regra: Período máximo 2 anos (730 dias) exceto para PCD (Portador de Deficiência).
        """
        inicio = self.dados_estagio.data_inicio
        termino = self.dados_estagio.data_termino
        e_pcd = self.estagiario.portador_de_deficiencia
        
        diferenca_dias = abs((termino - inicio).days)
        
        # 2 anos = 730 dias
        if diferenca_dias > 730 and not e_pcd:
            raise ValueError('A duração do estágio não pode exceder 2 anos, exceto para estagiários PCD.')
            
        return self

    @model_validator(mode='after')
    def validar_idade_minima(self):
        """
        Regra: O estagiário deve ter no mínimo 18 anos na data de início do estágio.
        """
        nascimento = self.estagiario.data_nascimento
        inicio = self.dados_estagio.data_inicio
        
        idade = inicio.year - nascimento.year - ((inicio.month, inicio.day) < (nascimento.month, nascimento.day))
        
        if idade < 18:
            raise ValueError(f'O estagiário deve ter no mínimo 18 anos na data de início do estágio. Idade calculada: {idade} anos.')
            
        return self