from .schemas import ValidacaoDocumentoSchema, UnidadeConcedenteSchema, SupervisorSchema, EstagiarioSchema
from utils.document_validator import validate_cnpj_api, validate_cpf_business
from typing import Dict, Any

async def validate_document_service(doc: ValidacaoDocumentoSchema) -> Dict[str, Any]:
    """
    Orquestra a validação de todos os documentos (CNPJ e CPFs) presentes no schema.
    """
    observacoes = []
    todas_validas = True

    # 1. Validação do CNPJ da Unidade Concedente
    unidade_concedente: UnidadeConcedenteSchema = doc.unidade_concedente
    cnpj = unidade_concedente.cnpj
    
    if cnpj:
        cnpj_result = await validate_cnpj_api(cnpj)
        if not cnpj_result["validacao"]:
            todas_validas = False
            observacoes.append(f"CNPJ Unidade Concedente: {cnpj_result['obs']}")
        else:
            observacoes.append(f"CNPJ Unidade Concedente: {cnpj_result['obs']}")

    # 2. Validação do CPF do Supervisor
    supervisor: SupervisorSchema = doc.supervisor
    cpf_supervisor = supervisor.cpf
    
    if cpf_supervisor:
        cpf_supervisor_result = await validate_cpf_business(cpf_supervisor)
        if not cpf_supervisor_result["validacao"]:
            todas_validas = False
            observacoes.append(f"CPF Supervisor: {cpf_supervisor_result['obs']}")
        else:
            observacoes.append(f"CPF Supervisor: {cpf_supervisor_result['obs']}")

    # 3. Validação do CPF do Estagiário (Aluno)
    estagiario: EstagiarioSchema = doc.estagiario
    cpf_estagiario = estagiario.cpf
    
    if cpf_estagiario:
        cpf_estagiario_result = await validate_cpf_business(cpf_estagiario)
        if not cpf_estagiario_result["validacao"]:
            todas_validas = False
            observacoes.append(f"CPF Estagiário: {cpf_estagiario_result['obs']}")
        else:
            observacoes.append(f"CPF Estagiário: {cpf_estagiario_result['obs']}")

    # Lógica de retorno final
    if todas_validas:
        return {
            "validacao": True,
            "obs": "Todas as validações de documentos foram bem-sucedidas. " + " | ".join(observacoes)
        }
    else:
        return {
            "validacao": False,
            "obs": "Falha nas validações de documentos: " + " | ".join(observacoes)
        }
