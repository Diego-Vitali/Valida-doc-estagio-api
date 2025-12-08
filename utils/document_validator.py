import httpx
from typing import Dict, Any

# Constante para a URL da API de CNPJ
BRASIL_API_CNPJ_URL = "https://brasilapi.com.br/api/cnpj/v1/"

async def validate_cnpj_api(cnpj: str) -> Dict[str, Any]:
    """
    Valida um CNPJ consultando a Brasil API.
    Retorna um dicionário com 'validacao' (bool) e 'obs' (str).
    """
    cnpj_clean = "".join(filter(str.isdigit, cnpj))
    
    if len(cnpj_clean) != 14:
        return {"validacao": False, "obs": "CNPJ deve conter 14 dígitos."}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BRASIL_API_CNPJ_URL}{cnpj_clean}", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if 'type' in data and data['type'] == 'service_error':
                    return {"validacao": False, "obs": f"CNPJ não encontrado na Receita Federal: {cnpj}"}
                
                # CNPJ encontrado e ativo
                razao_social = data.get('razao_social', 'Razão Social não disponível')
                return {"validacao": True, "obs": f"CNPJ Válido. Razão Social: {razao_social}"}
            
            elif response.status_code == 404:
                return {"validacao": False, "obs": f"CNPJ não encontrado: {cnpj}"}
            
            elif response.status_code == 400:
                return {"validacao": False, "obs": "CNPJ inválido ou mal formatado."}
            
            else:
                return {"validacao": False, "obs": f"Erro na Brasil API ao consultar CNPJ: {response.status_code}"}

    except httpx.ConnectError:
        return {"validacao": False, "obs": "Não foi possível conectar à Brasil API para validar CNPJ."}
    except Exception as e:
        return {"validacao": False, "obs": f"Erro interno ao validar CNPJ: {str(e)}"}

def validate_cpf_format(cpf: str) -> Dict[str, Any]:
    """
    Valida o formato básico de um CPF (tamanho e dígitos repetidos).
    Retorna um dicionário com 'validacao' (bool) e 'obs' (str).
    """
    cpf_clean = "".join(filter(str.isdigit, cpf))
    
    if len(cpf_clean) != 11:
        return {"validacao": False, "obs": "CPF deve conter 11 dígitos."}

    
    if cpf_clean == cpf_clean[0] * 11:
        return {"validacao": False, "obs": "CPF inválido (todos os dígitos iguais)."}
    
    return {"validacao": True, "obs": "CPF Válido (formato)." }

async def validate_cpf_business(cpf: str) -> Dict[str, Any]:
    """
    Função de validação de CPF de alto nível (atualmente apenas valida o formato).
    """
    return validate_cpf_format(cpf)
