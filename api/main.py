from fastapi import FastAPI, HTTPException
from .schemas import ValidacaoDocumentoSchema
app = FastAPI(
    title="API de Validação de Estágio",
    description="Valida documentos de estágio conforme regras da Coordenadoria de Extensão.",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    return {"Coordenadoria": "Extensão"}

@app.post("/validacao/", status_code=200)
async def validar_documento_estagio(doc: ValidacaoDocumentoSchema):
    """
    Recebe o JSON completo do documento de estágio.
    
    - Realiza validação de tipos (String, Int, Date).
    - Valida máscaras e formatos (CPF, CNPJ, CEP, Email, Telefone).
    - Aplica regras de negócio (Datas, Horas, PCD, Duração).
    
    Se houver erro, retorna 422 com a lista de erros.
    Se sucesso, retorna 200 com status de sucesso.
    """

    # Já validado pelo schemas.py
    return {
        "status": "sucesso",
        "mensagem": "Documento de estágio validado com sucesso.",
        "dados_processados": {
            "estagiario": doc.estagiario.nome,
            "empresa": doc.unidade_concedente.razao_social,
            "periodo": f"{doc.dados_estagio.data_inicio} a {doc.dados_estagio.data_termino}"
        }
    }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

