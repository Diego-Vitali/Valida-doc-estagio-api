from fastapi import FastAPI
from .schemas import ValidacaoDocumentoSchema
from utils.estagio import validate_dados_estagio
from utils.exceptions import ValidationError

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Coordenadoria": "Extensão"}

@app.post("/validacao/")
async def validar_documento_estagio(doc: ValidacaoDocumentoSchema):
    # Aqui a gente adicionar a lógica de validação dos dados e etc...

    ###############################################################
    # Validação dos dados de estágio
    dados_estagio = doc.dados_estagio
    is_pcd = doc.estagiario.portador_de_deficiencia

    try:
        validate_dados_estagio(dados_estagio, is_pcd=is_pcd)
            
    except ValidationError as e:
        return {
            "validacao": False,
            "obs": str(e)
        }
    
    except Exception as e:
        # Erro genérico de sistema
        return {
            "validacao": False,
            "obs": f"Erro interno ao processar validação: {str(e)}"
        }
    ###############################################################

    return {"status": "Documento de estágio validado com sucesso."}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)