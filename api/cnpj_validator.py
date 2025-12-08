import httpx
from fastapi import HTTPException

BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1/"

async def validate_cnpj(cnpj: str):

    cnpj_clean = "".join(filter(str.isdigit, cnpj))
    
    if len(cnpj_clean) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve conter 14 dígitos.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BRASIL_API_URL}{cnpj_clean}", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if 'type' in data and data['type'] == 'service_error':
                    raise HTTPException(status_code=404, detail=f"CNPJ não encontrado: {cnpj}")
                return data
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"CNPJ não encontrado: {cnpj}")
            elif response.status_code == 400:
                raise HTTPException(status_code=400, detail="CNPJ inválido ou mal formatado.")
            else:
                raise HTTPException(status_code=500, detail=f"Erro na Brasil API: {response.status_code}")

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Não foi possível conectar à Brasil API.")
    except Exception as e:
        # Capturar qualquer outra exceção não tratad
        raise HTTPException(status_code=500, detail=f"Erro interno ao validar CNPJ: {str(e)}")
